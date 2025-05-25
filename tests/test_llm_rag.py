import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langsmith import traceable

from app.utility.env import get_env_key, get_open_ai_model
from app.utility.rag_qa import rag_evaluation

from langsmith import Client

from typing_extensions import Annotated, TypedDict

from tests.prompt import correctness_instructions, relevance_instructions, grounded_instructions, \
    retrieval_relevance_instructions

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = get_env_key("LANGSMITH_API_KEY")
os.environ["OPENAI_API_KEY"] = get_env_key("OPEN_AI_KEY")

llm = ChatOpenAI(
    model=get_open_ai_model(),
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)


@traceable()
def rag_bot(question: str) -> dict:
    retriever = rag_evaluation()
    docs = retriever.invoke(question)
    print("******************************")
    print(docs)
    docs_string = "".join([doc.page_content + str(doc.metadata) for doc in docs])
    instructions = f"""
        You are a helpful assistant who is good at analyzing source information and answering questions.

        Use the following source documents to answer the user's questions.

        If you don't know the answer, just say that you don't know.

        Use three sentences maximum and keep the answer concise.

        Documents: {docs_string}"""

    # langchain ChatModel will be automatically traced
    ai_msg = llm.invoke([
        {"role": "system", "content": instructions},
        {"role": "user", "content": question},
    ],
    )

    return {"answer": ai_msg.content, "documents": docs}


answer_from_rag = """
The anti-inflammatory medicines listed include sulfasalazine, mesalazine, hydrocortisone, and prednisolone. They are available in various forms such as retention enemas, suppositories, and tablets. Additionally, betamethasone and calamine are also mentioned as anti-inflammatory and antipruritic medicines.
"""

examples = [
    {
        "inputs": {"question": "What are the inflammatory medicines?"},
        "outputs": {"answer": f"{answer_from_rag}"},
    }
]

client = Client()

# Create the dataset and examples in LangSmith
dataset_name = "Nurse Assistant Dataset - " + str(datetime.now())
dataset = client.create_dataset(dataset_name=dataset_name)
client.create_examples(
    dataset_id=dataset.id,
    examples=examples
)


# Grade output schema
class CorrectnessGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    correct: Annotated[bool, ..., "True if the answer is correct, False otherwise."]


# Grader LLM
grader_llm = (ChatOpenAI(model=get_open_ai_model(), temperature=0)
              .with_structured_output(CorrectnessGrade,
                                      method="json_schema",
                                      strict=True))


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    """An evaluator for RAG answer accuracy"""
    answers = f"""
                    QUESTION: {inputs['question']}
                    GROUND TRUTH ANSWER: {reference_outputs['answer']}
                    STUDENT ANSWER: {outputs['answer']}
               """
    # Run evaluator
    grade = grader_llm.invoke([
        {"role": "system", "content": correctness_instructions},
        {"role": "user", "content": answers}
    ])
    return grade["correct"]


# Grade output schema
class RelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "Provide the score on whether the answer addresses the question"]


# Grader LLM
relevance_llm = (ChatOpenAI(model=get_open_ai_model(), temperature=0)
                 .with_structured_output(RelevanceGrade,
                                         method="json_schema",
                                         strict=True))


# Evaluator
def relevance(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer helpfulness."""
    answer = f"QUESTION: {inputs['question']}\nSTUDENT ANSWER: {outputs['answer']}"

    grade = relevance_llm.invoke([
        {"role": "system", "content": relevance_instructions},
        {"role": "user", "content": answer}
    ])
    return grade["relevant"]


# Grade output schema
class GroundedGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    grounded: Annotated[bool, ..., "Provide the score on if the answer hallucinates from the documents"]


# Grader LLM
grounded_llm = (ChatOpenAI(model=get_open_ai_model(), temperature=0)
                .with_structured_output(GroundedGrade,
                                        method="json_schema",
                                        strict=True))


# Evaluator
def groundedness(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer groundedness."""
    doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
    answer = f"FACTS: {doc_string}\nSTUDENT ANSWER: {outputs['answer']}"
    grade = grounded_llm.invoke(
        [{"role": "system", "content": grounded_instructions}, {"role": "user", "content": answer}])
    return grade["grounded"]


# Grade output schema
class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "True if the retrieved documents are relevant to the question, False otherwise"]


# Grader LLM
retrieval_relevance_llm = (ChatOpenAI(model=get_open_ai_model(), temperature=0)
                           .with_structured_output(RetrievalRelevanceGrade,
                                                   method="json_schema",
                                                   strict=True))


def retrieval_relevance(inputs: dict, outputs: dict) -> bool:
    """An evaluator for document relevance"""
    doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
    answer = f"FACTS: {doc_string}\nQUESTION: {inputs['question']}"

    # Run evaluator
    grade = retrieval_relevance_llm.invoke([
        {"role": "system", "content": retrieval_relevance_instructions},
        {"role": "user", "content": answer}
    ])
    return grade["relevant"]


def target(inputs: dict) -> dict:
    return rag_bot(inputs["question"])


class TestLLMRAG:
    def test_length_score(self) -> None:
        """Test that the length score is at least 80%."""
        experiment_results = client.evaluate(
            target,
            data=dataset_name,
            evaluators=[correctness, groundedness, relevance, retrieval_relevance],
            experiment_prefix="rag-doc-relevance",
            metadata={"version": "Nurse Assistant context, gpt-4o-mini"},
        )
