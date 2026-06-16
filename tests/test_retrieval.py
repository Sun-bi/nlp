from rag_redis.chunking import chunk_documents
from rag_redis.corpus import Document
from rag_redis.embeddings import HashingEmbeddingModel
from rag_redis.retriever import HybridRetriever


def test_hybrid_retriever_ranks_exact_redis_terms_above_loose_similarity():
    docs = [
        Document(
            doc_id="redis:persistence",
            title="Redis persistence",
            url="https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/",
            text="Redis persistence uses RDB snapshots and AOF append only files. AOF records write commands and can improve durability.",
        ),
        Document(
            doc_id="redis:streams",
            title="Redis streams",
            url="https://redis.io/docs/latest/develop/data-types/streams/",
            text="Redis streams store append only event logs and support consumer groups for message processing.",
        ),
        Document(
            doc_id="redis:expiration",
            title="Redis key expiration",
            url="https://redis.io/docs/latest/commands/expire/",
            text="Redis keys can have TTL values. EXPIRE sets a timeout and keys are deleted after the timeout.",
        ),
    ]
    chunks = chunk_documents(docs, chunk_size=18, overlap=4)
    retriever = HybridRetriever.from_chunks(
        chunks,
        embedder=HashingEmbeddingModel(dimensions=128),
        vector_weight=0.45,
        bm25_weight=0.55,
    )

    results = retriever.search("AOF 和 RDB 持久化有什么区别", top_k=2)

    assert results[0].chunk.doc_id == "redis:persistence"
    assert results[0].combined_score > results[1].combined_score


def test_reranker_exposes_second_stage_score_for_term_coverage():
    docs = [
        Document(
            doc_id="redis:persistence",
            title="Redis RDB AOF persistence",
            url="https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/",
            text="RDB creates compact snapshots. AOF is an append only file that logs write commands for durability.",
        ),
        Document(
            doc_id="redis:pubsub",
            title="Redis Pub/Sub",
            url="https://redis.io/docs/latest/develop/pubsub/",
            text="Pub/Sub delivers messages to subscribers but does not persist messages for later replay.",
        ),
        Document(
            doc_id="redis:streams",
            title="Redis Streams",
            url="https://redis.io/docs/latest/develop/data-types/streams/",
            text="Streams keep append only event logs and support consumer groups for reliable processing.",
        ),
    ]
    chunks = chunk_documents(docs, chunk_size=28, overlap=4)
    retriever = HybridRetriever.from_chunks(
        chunks,
        embedder=HashingEmbeddingModel(dimensions=128),
    )

    results = retriever.search("AOF 和 RDB 持久化有什么区别", top_k=3)

    assert results[0].chunk.doc_id == "redis:persistence"
    assert results[0].rerank_score > results[0].combined_score
    assert results[0].term_coverage > results[1].term_coverage
