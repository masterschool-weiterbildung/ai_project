import glob
import hashlib
import time
import os

from pathlib import Path

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_openai import ChatOpenAI
from langsmith import utils

from app.utility.constant import MAX_MESSAGES, INDEX_NAME, NAMESPACE
from app.utility.env import get_env_key, get_open_ai_model
from app.utility.logger import get_logger
from app.utility.others import get_database_configuration

from pinecone import Pinecone, ServerlessSpec

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.schema import HumanMessage, SystemMessage
from langchain_pinecone import PineconeEmbeddings
from langchain_pinecone import PineconeRerank
from langchain_core.tools import tool

from langgraph.graph import StateGraph
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver

from psycopg_pool import ConnectionPool

from app.utility.prompt import rag_system_prompt_generate

os.environ[
    "OPENAI_API_KEY"] = get_env_key("OPEN_AI_KEY")

llm = ChatOpenAI(
    model=get_open_ai_model(),
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

graph_builder = StateGraph(MessagesState)

logger = get_logger()

# Set environment for Langsmith
os.environ[
    "LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ[
    "LANGSMITH_API_KEY"] = get_env_key("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = "chatbot"

def set_pinecone_open_ai_environment():
    # Set environment key for pinecone and openai
    os.environ[
        "PINECONE_API_KEY"] = get_env_key("PINECONE_API_KEY")

"""
    RAG 1st component : 
        (1) Indexing: a pipeline for ingesting data from a source and indexing it.
"""

"""
    1. Load: First we need to load our data. This is done with Document Loaders.
"""


def load_pdf_files():
    # Load the pdf file
    pdf_path = Path(
        __file__).parent.parent.parent / "public" / "Who Essential Medicine.pdf"
    pdf_paths = glob.glob(str(pdf_path))
    # Loop through the directories and load the pdf files
    documents = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        documents.extend(docs)
    return documents

""""
    2. Split: Text splitters break large Documents into smaller chunks. 
    This is useful both for indexing data and passing it into a model, 
    as large chunks are harder to search over and won't fit in a model's finite context window.
    Chunk Optimization — Recursive Structure Aware, A hybrid method combining fixed-size sliding window 
    and structure-aware splitting. 
"""


def split_documents_chunks(documents):
    # Create a text splitter instance
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200)
    # Split the loaded documents into smaller chunks
    split_documents = text_splitter.split_documents(documents)
    return split_documents


""""
    3. Store: We need somewhere to store and index our splits,
    so that they can be searched over later. This is often done using a VectorStore and Embeddings model.
"""


def init_embeddings():
    # Initialize embeddings
    model_name = 'multilingual-e5-large'
    embeddings = PineconeEmbeddings(model=model_name)
    return embeddings

"""
    Generating content based ids has the following advantages:
    1. If the same content appears in multiple chunks, they will share the same ID
    2. Hash-based IDs allow quick comparisons between chunks without needing to compare the full text.
    3. IDs can serve as keys to associate chunks with their embeddings or metadata
    4. If a chunk’s content changes, its ID will change
"""

def generate_content_based_ids(split_documents):
    # Generate content-based IDs for each chunk
    ids = [hashlib.md5(doc.page_content.encode()).hexdigest() for doc in
           split_documents]
    return ids


def init_pinecone_set_serverless_spec(embeddings):
    # Init pinecone
    pc = Pinecone()
    # Set cloud and region for serverless spec
    cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
    region = os.environ.get('PINECONE_REGION') or 'us-east-1'
    spec = ServerlessSpec(cloud=cloud, region=region)
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=embeddings.dimension,
            metric="cosine",
            spec=spec
        )
        # Wait for index to be ready
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)
    return INDEX_NAME, NAMESPACE


def upload_documents_with_ids_to_pinecone(embeddings, ids, index_name, namespace, split_documents):
    # Upload documents with content-based IDs to Pinecone
    docsearch = PineconeVectorStore.from_documents(
        documents=split_documents,
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace,
        ids=ids
    )
    return docsearch


"""
    RAG 2nd component : 
        (2) Retrieval and generation: the actual RAG chain, which takes the
        user query at run time and retrieves the relevant data from the index,
        then passes that to the model.
"""
"""
    4. Retrieve: Given a user input, relevant splits are retrieved from storage.
"""


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""

    # Setup up the environments
    set_pinecone_open_ai_environment()

    pc = Pinecone()

    embeddings = init_embeddings()

    generate_hypothetical_document_embeddings(embeddings, query)

    if INDEX_NAME not in pc.list_indexes().names():

        # Indexing
        documents = load_pdf_files()

        split_documents = split_documents_chunks(documents)

        ids = generate_content_based_ids(split_documents)

        index_name, namespace = init_pinecone_set_serverless_spec(embeddings)

        vector_store = upload_documents_with_ids_to_pinecone(embeddings, ids,
                                                             index_name, namespace,
                                                             split_documents)
    else:

        vector_store = PineconeVectorStore.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings,
            namespace=NAMESPACE
        )

    reranker = PineconeRerank(model="bge-reranker-v2-m3", top_n=5)

    retrieved_docs = vector_store.similarity_search(query, k=10)

    reranked_docs = reranker.compress_documents(retrieved_docs, query)

    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in reranked_docs
    )
    return serialized, retrieved_docs


"""
    In HyDE (Hypothetical Document Embeddings) we let the LLM create an answer to the
    user’s query without context first, and use the answer to search for relevant 
    information within our vector database.
"""

def generate_hypothetical_document_embeddings(embeddings, query):
    messages = [
        SystemMessage(content="Answer the following question. Give the rational before answering"),
        HumanMessage(content=query)
    ]
    hypothetical_answer = llm.invoke(messages)
    embeddings.embed_query(hypothetical_answer.content)

def rag_evaluation():
    # Setup up the environments
    set_pinecone_open_ai_environment()

    # Indexing
    documents = load_pdf_files()

    split_documents = split_documents_chunks(documents)

    ids = generate_content_based_ids(split_documents)

    embeddings = init_embeddings()


    index_name, namespace = init_pinecone_set_serverless_spec(embeddings)

    vector_store = upload_documents_with_ids_to_pinecone(embeddings, ids,
                                                         index_name, namespace,
                                                         split_documents)
    retriever = vector_store.as_retriever(k=10)

    model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
    compressor = CrossEncoderReranker(model=model, top_n=5)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )

    return compression_retriever

def trim_messages(messages):
    if len(messages) > MAX_MESSAGES:
        return messages[-MAX_MESSAGES:]  # Keep only the last MAX_MESSAGES
    return messages


def generate_user_message(input_message, thread_id):
    # Setup database connection and checkpointer
    db_path = Path(__file__).parent.parent.parent / "config.json"
    connection_kwargs = {"autocommit": True, "prepare_threshold": 0, }
    with ConnectionPool(conninfo=get_database_configuration("database_dev_chatbot", "url", db_path), max_size=20,
                        kwargs=connection_kwargs, ) as pool:
        checkpointer = PostgresSaver(pool)

        checkpointer.setup()

        # Retrieve the checkpoint
        config = {"configurable": {"thread_id": thread_id}}
        checkpoint = checkpointer.get(config)

        # Load and trim the state
        if checkpoint is None:
            initial_messages = []
        else:
            # Extract messages from the checkpoint (assumes 'messages' key exists)
            initial_messages = checkpoint.get("channel_values", []).get("messages", [])

            # Trim to the last MAX_MESSAGES
            initial_messages = trim_messages(initial_messages)

        print("================================")
        print(initial_messages)
        print("================================")

        # Create agent with checkpointer
        agent_executor = create_react_agent(llm, [retrieve], checkpointer=checkpointer, prompt=rag_system_prompt_generate)

        # Prepare the input with trimmed context
        input_state = {"messages": initial_messages + [{"role": "user", "content": input_message}]}

        print("++++++++++++++++++++++++++++++++++++")
        print(input_state)
        print("++++++++++++++++++++++++++++++++++++")

        # Step 4: Process the new message
        response_stream = agent_executor.stream(
            input_state,
            stream_mode="values",
            config=config,
        )

        # Generate and send response
        response = []
        for event in response_stream:
            response.append(event["messages"][-1].content)

        return response[-1]


def main():
    input_message = (
        "What are the inflammatory medicines?"
        # "What are the medicines you suggested before?"
        # "What is Calamine?"
        # "What is my first question?"
    )
    # print(generate_user_message("Hello", "j300"))
    print(generate_user_message(input_message, "patient_11"))

    print(utils.tracing_is_enabled())

if __name__ == '__main__':
    main()
