# Redis-RAG 汇报逐页讲稿

说明：每一页都包含“页面内容”和“讲稿”。讲稿已经覆盖该页主要可见内容，可以在汇报时直接照着念，并根据现场时间删减。

## 第 1 页：封面

### 页面内容

- Redis-RAG：基于 RAG 的 Redis 垂直领域深度问答系统
- 关键词：私有知识库、混合检索、DeepSeek 生成、三维量化评估
- 交付物：代码仓库、README、依赖文件、一键推理、报告、PPT、讲稿

### 讲稿

这一页是汇报封面。我的作业选题是 Redis 垂直领域问答系统。核心思路是把 Redis 官方文档和清洗后的技术语料构造成私有知识库，然后通过 RAG 的方式进行检索增强生成。系统不仅包含一键推理脚本，也包含索引构建、量化评估、报告和 PPT。后面我会按照数据、检索、生成、评估和案例分析的顺序展开。

## 第 2 页：作业要求与本项目交付

### 页面内容

- 本项目交付完整代码仓库
- 核心 RAG 模块包括知识库、Chunking、Embedding、向量库、混合检索和生成
- 展示材料包括报告、PPT 和逐页讲稿

### 讲稿

这一页说明作业要求和项目交付之间的对应关系。代码仓库里有 README、requirements 和 infer.py，满足一键运行要求。RAG 核心部分包括 Redis 私有知识库、文档分块、embedding、本地向量库、Query Rewriting 和混合检索。展示材料方面，我补充了论文式报告、PDF、15页PPT和逐页讲稿，所以这个项目既可以运行，也可以完整展示。

## 第 3 页：为什么选 Redis 作为垂直领域

### 页面内容

- Redis 知识边界清晰
- Redis 问答包含大量命令名和缩写
- 官方文档可追溯，适合做引用和忠实度评估
- 技术文档 RAG 的难点包括术语匹配、概念混淆和答案忠实度

### 讲稿

我选择 Redis 是因为它很适合作为垂直领域。第一，Redis 的知识边界清楚，主题从数据结构到持久化和集群都很明确。第二，Redis 问答里有很多精确术语，比如 AOF、RDB、TTL 和 WATCH，这些词非常考验检索系统。第三，官方文档有稳定 URL，可以作为答案引用来源。这个选题能很好地展示 RAG 的核心价值：把答案约束到可追溯的文档上下文中。

## 第 4 页：私有知识库构建流程

### 页面内容

- 流程：官方文档、页面抓取、正文清洗、JSONL 语料、索引构建、问答系统
- 每条文档包含 doc_id、title、url、text
- 知识主题覆盖 Redis 数据结构、TTL、持久化、高可用、集群和缓存风险

### 讲稿

这一页展示私有知识库构建流程。数据可以来自 Redis 官方文档，经过页面抓取和正文清洗后，保存为 JSONL。每条记录都包含 doc_id、title、url 和 text。doc_id 用于评估，url 用于追溯来源。为了保证作业能稳定运行，我保留了一份内置清洗语料，同时也提供脚本重新抓取官方文档。

## 第 5 页：知识库主题覆盖

### 页面内容

- 基础数据结构：String、Hash、List、Stream、Sorted Set
- 生命周期：EXPIRE、TTL、PERSIST
- 可靠性：RDB、AOF、appendfsync
- 高可用与扩展：Replication、Sentinel、Cluster
- 编程与消息：事务、Lua、Pub/Sub、Stream
- 缓存工程：缓存穿透、击穿和雪崩

### 讲稿

这一页说明知识库覆盖面。Redis 不是只收集几个命令，而是覆盖了数据结构、生命周期、可靠性、高可用、编程能力和缓存工程。这样设计的好处是评估问题可以比较全面，比如既能问 AOF 和 RDB，也能问 Stream 和 Pub/Sub，或者问缓存击穿怎么缓解。覆盖原则是每个问题都应该能从知识库中找到依据。

## 第 6 页：Chunking：让检索单元既可命中又可阅读

### 页面内容

- Redis-aware tokenizer 保留命令名、缩写和中文领域词
- 默认 chunk_size=320，overlap=40
- 每个 chunk 保留来源元数据
- AOF/RDB 问题需要保留持久化、persistence、RDB、AOF、snapshot 等关键 token

### 讲稿

这一页解释 Chunking。技术文档分块不能只按普通句子切，因为 Redis 命令名非常关键。我实现了 Redis-aware tokenizer，保留命令名、缩写和中文领域词。默认分块大小是 320，重叠是 40。这样长文档可以切成可检索片段，同时相邻片段之间不会完全断开。每个 chunk 都有来源元数据，所以最后答案可以回到原文档。

## 第 7 页：Embedding 与本地向量数据库

### 页面内容

- 默认使用 HashingEmbeddingModel，维度 256
- 向量库保存 chunk 和 vector，文件是 data/index/vectors.jsonl
- 优点是可复现、无需下载模型、便于解释
- 后续可升级为 BGE、E5、SentenceTransformer、FAISS 或 Chroma

### 讲稿

这一页说明 embedding 和向量库。为了保证作业在没有 GPU、没有外部模型下载的环境中也能跑，我默认使用 hashing embedding。它不如 BGE 这类模型强，但非常适合课程复现。向量库用 JSONL 保存，每条记录包含 chunk 和 vector，结构完全透明。后续如果要做真实系统，可以把这一层替换成 BGE embedding 和 FAISS 或 Chroma。

## 第 8 页：Query Rewriting：连接中文问题与英文术语

### 页面内容

- 持久化扩展为 persistence、RDB、AOF、snapshot
- 高可用扩展为 replication、sentinel、failover、cluster
- 过期扩展为 expire、TTL、timeout
- 队列扩展为 list、stream、consumer group、XREADGROUP
- Query Rewriting 主要提升召回率

### 讲稿

这一页是高级 RAG 优化的第一部分：Query Rewriting。Redis 官方文档很多术语是英文，但用户可能用中文问，比如“持久化”“高可用”“过期”。如果不扩展，检索可能找不到相关英文术语。所以我维护了一个领域词表，把中文问题扩展成 Redis 常用英文概念。这个策略主要提升召回率。

## 第 9 页：Hybrid Retrieval：BM25 与向量检索互补

### 页面内容

- 融合公式：score = 0.45 × vector + 0.55 × BM25
- 向量检索擅长语义相似
- BM25 擅长 AOF、RDB、TTL、WATCH 等精确术语
- Redis 问答需要语义理解和精确术语命中结合

### 讲稿

这一页解释混合检索。向量检索能处理语义相似，但是对命令名未必足够敏感。BM25 对精确词非常有效，但不能很好处理同义表达。所以我把二者融合。公式里向量权重是 0.45，BM25 权重是 0.55，因为 Redis 问答中命令名非常关键。这个策略比单纯向量检索更适合 Redis 技术文档。

## 第 10 页：端到端系统架构

### 页面内容

- 文档 JSONL 经过 Chunking 后进入 Embedding 和 BM25
- 用户问题经过 Query Rewriting 后进入 Hybrid Retriever
- Top-k 上下文传入 DeepSeek 或抽取式生成器
- 输出带引用答案和检索分数

### 讲稿

这一页展示端到端架构。左边是文档处理和索引构建，文档先变成 chunk，再进入 embedding 和 BM25。右边是在线问答流程，用户问题先经过 Query Rewriting，然后由 Hybrid Retriever 找到 Top-k 上下文，最后传给 DeepSeek 或抽取式生成器。系统还会输出检索分数，便于分析为什么选中某个文档。

## 第 11 页：生成模块：DeepSeek 优先，离线可回退

### 页面内容

- 设置 DEEPSEEK_API_KEY 后默认使用 deepseek-v4-pro
- 没有 API key 时使用抽取式生成器
- 提示词要求只能基于上下文回答，并带来源引用
- API key 不写入仓库

### 讲稿

这一页说明生成模块。项目支持 DeepSeek，只要设置 DEEPSEEK_API_KEY，默认模型就是 deepseek-v4-pro。同时我保留了抽取式回退，保证没有 API key 也能运行。为了降低幻觉，系统提示要求模型只能依据检索上下文回答，并带引用。如果上下文不足，就要说明无法确认。这里也强调，API key 不会写入仓库，只通过环境变量传入。

## 第 12 页：量化评估：三个维度衡量 RAG 能力

### 页面内容

- Context Relevance 衡量检索上下文是否相关
- Faithfulness 衡量答案是否忠实于上下文
- Answer Relevance 衡量答案是否回答问题
- 评估集包含 10 条 Redis 技术问题

### 讲稿

这一页介绍评估方案。Context Relevance 主要评价检索是否找到了相关文档。Faithfulness 评价答案是否被上下文支持，也就是是否有幻觉风险。Answer Relevance 评价答案是否覆盖问题的关键点。评估集包含 10 条 Redis 技术问题，输出结果会保存成 JSON 和 CSV，方便报告引用。

## 第 13 页：实验结果与解释

### 页面内容

- Context Relevance = 1.0000
- Faithfulness = 0.8116
- Answer Relevance = 0.8750
- 检索效果较稳，答案忠实度较好，部分关键词覆盖仍可提升

### 讲稿

这一页展示实验结果。Context Relevance 是 1.0000，说明在当前评估集里，检索能覆盖相关文档。Faithfulness 是 0.8116，说明答案大多数内容都能被上下文支持。Answer Relevance 是 0.8750，说明答案基本覆盖问题要点，但还有提升空间。主要问题是抽取式生成有时表达比较硬，可能没有覆盖所有期望关键词。

## 第 14 页：案例分析：AOF 与 RDB 持久化问答

### 页面内容

- 问题是 Redis 的 AOF 和 RDB 持久化有什么区别
- 系统命中文档 redis:persistence
- 答案包含 RDB 快照、AOF 追加日志、备份恢复和数据安全性
- 命中原因是 Query Rewriting 和 BM25 精确术语匹配

### 讲稿

这一页用 AOF 和 RDB 问题做案例。系统最终命中了 redis:persistence 文档，combined_score 是 1.0000。答案能解释 RDB 是快照，适合备份和快速恢复；AOF 是追加日志，通常数据安全性更好。这个案例能说明 Query Rewriting 和 BM25 的价值：中文问题会扩展到 persistence、snapshot 和 append only file，同时 AOF 和 RDB 被精确命中。

## 第 15 页：Bad Case、改进方向与总结

### 页面内容

- Bad Case：AOF/RDB 问题早期召回 Pub/Sub 弱相关文档
- 已做改进：Query Rewriting、混合检索、上下文过滤
- 后续优化：BGE embedding、reranker、更大评估集、citation checking
- 复现实验命令：infer.py 和 evaluate.py

### 讲稿

最后一页总结问题和改进。一个典型 bad case 是 AOF/RDB 问题早期会召回 Pub/Sub，因为它也出现了持久化相关词。为了解决这个问题，我加入了 Query Rewriting、混合检索和生成阶段上下文过滤。后续可以进一步替换 BGE embedding、增加 reranker、扩大评估集，并对 LLM 输出做引用一致性检查。总体来说，这个项目完成了从知识库到检索、生成、评估和展示的完整闭环。
