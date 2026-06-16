import pytest

from rag_redis.embeddings import HashingEmbeddingModel, create_embedding_model
from rag_redis.pipeline import _retrieval_settings
from rag_redis.vector_store import create_vector_store


def test_embedding_factory_defaults_to_hashing():
    embedder = create_embedding_model("hashing", dimensions=64)

    assert isinstance(embedder, HashingEmbeddingModel)
    assert embedder.dimensions == 64


def test_retrieval_modes_configure_weights_and_reranking():
    assert _retrieval_settings("vector", "lightweight") == (1.0, 0.0, False)
    assert _retrieval_settings("bm25", "lightweight") == (0.0, 1.0, False)
    assert _retrieval_settings("hybrid_no_rerank", "lightweight") == (0.45, 0.55, False)
    assert _retrieval_settings("hybrid", "none") == (0.45, 0.55, False)
    assert _retrieval_settings("hybrid", "lightweight") == (0.45, 0.55, True)


def test_unknown_vector_store_is_rejected():
    with pytest.raises(ValueError):
        create_vector_store([], HashingEmbeddingModel(), vector_store="unknown")
