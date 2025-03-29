import glob
import hashlib
import time
import os

from pathlib import Path
from app.utility.env import get_env_key, get_open_ai_model
from app.utility.logger import get_logger

logger = get_logger()

from pinecone import Pinecone, ServerlessSpec

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain


def generate_draft_message_to_patient(query: str) -> tuple:
    set_pinecone_open_ai_environment()

    set_langsmith_environment()

    documents = load_pdf_files()

    split_documents = split_documents_chunks(documents)

    ids = generate_content_based_ids(split_documents)

    embeddings = init_embeddings()

    index_name, namespace = init_pinecone_set_serverless_spec(embeddings)

    docsearch = upload_documents_with_ids_to_pinecone(embeddings, ids,
                                                      index_name, namespace,
                                                      split_documents)

    retrieval_chain = set_up_retrieval_chain(docsearch)

    answer_with_knowledge = retrieval_chain.invoke({"input": query})

    answer = answer_with_knowledge['answer']
    context = answer_with_knowledge['context']

    logger.info(answer)

    return answer, context


def set_up_retrieval_chain(docsearch):
    # Set up retrieval chain
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    retriever = docsearch.as_retriever()
    llm = ChatOpenAI(model_name=get_open_ai_model(), temperature=0.0)
    combine_docs_chain = create_stuff_documents_chain(
        llm, retrieval_qa_chat_prompt
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    return retrieval_chain


def upload_documents_with_ids_to_pinecone(embeddings, ids, index_name,
                                          namespace, split_documents):
    # Upload documents with content-based IDs to Pinecone
    docsearch = PineconeVectorStore.from_documents(
        documents=split_documents,
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace,
        ids=ids
    )
    return docsearch


def init_pinecone_set_serverless_spec(embeddings):
    # Init pinecone
    pc = Pinecone()
    # Set cloud and region for serverless spec
    cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
    region = os.environ.get('PINECONE_REGION') or 'us-east-1'
    spec = ServerlessSpec(cloud=cloud, region=region)
    index_name = "nursingassistant"
    namespace = "nursing"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=embeddings.dimension,
            metric="cosine",
            spec=spec
        )
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    return index_name, namespace


def init_embeddings():
    # Initialize embeddings
    model_name = 'multilingual-e5-large'
    embeddings = PineconeEmbeddings(model=model_name)
    return embeddings


def generate_content_based_ids(split_documents):
    # Generate content-based IDs for each chunk
    ids = [hashlib.md5(doc.page_content.encode()).hexdigest() for doc in
           split_documents]
    return ids


def split_documents_chunks(documents):
    # Create a text splitter instance
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200)
    # Split the loaded documents into smaller chunks
    split_documents = text_splitter.split_documents(documents)
    return split_documents


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


def set_pinecone_open_ai_environment():
    # Set environment key for pinecone and openai
    os.environ[
        "PINECONE_API_KEY"] = get_env_key("PINECONE_API_KEY")
    os.environ[
        "OPENAI_API_KEY"] = get_env_key("OPEN_AI_KEY")


def set_langsmith_environment():
    # Set environment for Langsmith
    os.environ[
        "LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ[
        "LANGSMITH_API_KEY"] = get_env_key("LANGSMITH_API_KEY")
    os.environ["LANGSMITH_PROJECT"] = "nursingassistant"


def main():
    generate_draft_message_to_patient("pentamidine is the medicine for what?")


if __name__ == '__main__':
    main()
