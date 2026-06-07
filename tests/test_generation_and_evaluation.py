from rag_redis.chunking import Chunk
from rag_redis.evaluation import evaluate_single
from rag_redis.generator import ExtractiveGenerator, OpenAICompatibleGenerator
from rag_redis.retriever import RetrievalResult


def _result(doc_id, title, text, score=1.0):
    return RetrievalResult(
        chunk=Chunk(
            chunk_id=f"{doc_id}#0",
            doc_id=doc_id,
            source_title=title,
            url=f"https://example.test/{doc_id}",
            text=text,
            tokens=text.lower().split(),
            start_token=0,
            end_token=len(text.split()),
        ),
        vector_score=score,
        bm25_score=score,
        combined_score=score,
    )


def test_extractive_generator_cites_sources_and_uses_retrieved_context():
    contexts = [
        _result(
            "redis:persistence",
            "Redis persistence",
            "AOF records write operations in an append-only log. RDB creates point-in-time snapshots.",
        )
    ]

    answer = ExtractiveGenerator().generate("AOF 和 RDB 有什么区别？", contexts)

    assert "AOF" in answer.answer
    assert "RDB" in answer.answer
    assert "[1]" in answer.answer
    assert answer.sources[0].doc_id == "redis:persistence"


def test_evaluate_single_scores_context_faithfulness_and_answer_relevance():
    contexts = [
        _result(
            "redis:persistence",
            "Redis persistence",
            "AOF records write operations. RDB creates snapshots. Both are Redis persistence options.",
        )
    ]
    answer = "AOF records write operations, while RDB creates snapshots. [1]"
    sample = {
        "question": "AOF 和 RDB 的区别是什么？",
        "gold_doc_ids": ["redis:persistence"],
        "expected_keywords": ["AOF", "RDB", "write operations", "snapshots"],
    }

    metrics = evaluate_single(sample, answer, contexts)

    assert metrics["context_relevance"] == 1.0
    assert metrics["faithfulness"] > 0.5
    assert metrics["answer_relevance"] >= 0.75


def test_deepseek_environment_defaults_are_openai_compatible(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    generator = OpenAICompatibleGenerator()

    assert generator.base_url == "https://api.deepseek.com"
    assert generator.model == "deepseek-v4-pro"
