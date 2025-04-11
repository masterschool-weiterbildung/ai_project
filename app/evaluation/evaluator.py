import os

from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from langsmith import Client
from langsmith import wrappers
from openai import OpenAI

from app.utility.env import get_env_key, get_open_ai_model
from app.utility.rag_qa import generate_user_message

os.environ["LANGSMITH_TRACING"] = "true"
os.environ[
    "LANGSMITH_API_KEY"] = get_env_key("LANGSMITH_API_KEY")
os.environ[
    "OPENAI_API_KEY"] = get_env_key("OPEN_AI_KEY")

openai_client = wrappers.wrap_openai(OpenAI())
client = Client()

def target(inputs: dict) -> dict:
    """
        response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer the following question accurately"},
            {"role": "user", "content": inputs["question"]},
        ],
    )
    """

    return {"answer": generate_user_message(inputs["question"], "test_chatbot_1")}


dataset = client.create_dataset(
    dataset_name="Nursing Assistant", description="Dataset for Agentic RAG chatbot"
)

answer_from_rag = """
Inflammatory medicines, particularly those classified as anti-inflammatory and antipruritic, include:

1. **Betamethasone**: A potent corticosteroid used in cream or ointment form (0.1% as valerate).
2. **Hydrocortisone**: A weaker corticosteroid available in cream or ointment form (1% acetate).
3. **Calamine**: Often used in lotion form for its soothing properties.

These medications are commonly used to reduce inflammation and alleviate itching associated with various skin conditions.
"""
# Create examples
examples = [
    {
        "inputs": {"question": "What are the inflammatory medicines?"},
        "outputs": {"answer": f"{answer_from_rag}"},
    }
]

client.create_examples(dataset_id=dataset.id, examples=examples)


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        model=get_open_ai_model(),
        feedback_key="correctness",
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs
    )
    return eval_result


def main():
    experiment_results = client.evaluate(
        target,
        data="Nursing Assistant",
        evaluators=[
            correctness_evaluator,
        ],
        experiment_prefix="nursing-assistant-test",
        max_concurrency=2,
    )

    print(experiment_results)


if __name__ == '__main__':
    main()
