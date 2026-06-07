from rag_redis.text import normalize_text, tokenize


def test_normalize_text_collapses_whitespace_and_lowercases_ascii():
    text = " Redis   SETEX\nAOF   持久化 "

    assert normalize_text(text) == "redis setex aof 持久化"


def test_tokenize_keeps_redis_commands_and_chinese_domain_terms():
    tokens = tokenize("Redis 的 SETEX 和 AOF 持久化如何工作？")

    assert "redis" in tokens
    assert "setex" in tokens
    assert "aof" in tokens
    assert "持久化" in tokens
