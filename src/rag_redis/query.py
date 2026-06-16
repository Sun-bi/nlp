"""Query rewriting rules for Redis domain terminology."""

from __future__ import annotations


EXPANSIONS = {
    "持久化": "persistence rdb aof snapshot append only file durability",
    "高可用": "replication replica sentinel failover cluster",
    "主从": "replication replica primary replica",
    "主从复制": "replication replica primary replica",
    "哨兵": "sentinel failover monitor quorum",
    "集群": "cluster sharding hash slot reshard failover",
    "过期": "expire ttl timeout key expiration",
    "过期时间": "expire ttl timeout key expiration",
    "淘汰": "eviction maxmemory lru lfu volatile allkeys",
    "淘汰策略": "eviction maxmemory policy allkeys volatile lru lfu",
    "互斥锁": "mutex lock set nx ex px",
    "字段级过期": "hash field expiration ttl",
    "字段过期": "hash field expiration ttl",
    "同步过程": "replication full synchronization incremental offset backlog",
    "事务": "multi exec watch transaction optimistic locking",
    "发布订阅": "pubsub publish subscribe channel",
    "队列": "list stream consumer group xadd xread",
    "消费者组": "stream consumer group xreadgroup ack pending",
    "lua": "eval script scripting atomic",
    "缓存穿透": "cache penetration null cache bloom filter",
    "缓存击穿": "hot key mutex logical expiration",
    "缓存雪崩": "cache avalanche random ttl rate limit",
}


def rewrite_query(question: str) -> str:
    additions = []
    lowered = question.lower()
    for keyword, expansion in EXPANSIONS.items():
        if keyword in lowered:
            additions.append(expansion)
    if not additions:
        return question
    return f"{question} {' '.join(additions)}"
