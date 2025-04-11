import pytest
from langsmith import evaluate

from app.evaluation.evaluator import target
from app.evaluation.evaluator_rag import dataset_name, correctness, groundedness, relevance, retrieval_relevance, client


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

        # This will be cleaned up in the next release:
        feedback = client.list_feedback(
            run_ids=[r.id for r in client.list_runs(project_name=experiment_results.experiment_name)],
            feedback_key="concision"
        )
        scores = [f.score for f in feedback]
        assert sum(scores) / len(scores) >= 0.8, "Aggregate score should be at least .8"
