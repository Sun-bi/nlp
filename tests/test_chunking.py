from rag_redis.corpus import Document
from rag_redis.chunking import chunk_document


def test_chunk_document_preserves_metadata_and_overlap():
    doc = Document(
        doc_id="redis:persistence",
        title="Redis persistence",
        url="https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/",
        text="Redis AOF persistence records write operations. RDB snapshots store compact point in time copies for recovery.",
    )

    chunks = chunk_document(doc, chunk_size=8, overlap=2)

    assert len(chunks) == 3
    assert chunks[0].doc_id == "redis:persistence"
    assert chunks[0].chunk_id == "redis:persistence#0"
    assert chunks[1].tokens[:2] == chunks[0].tokens[-2:]
    assert chunks[0].source_title == "Redis persistence"
