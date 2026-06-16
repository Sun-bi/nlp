# Redis-RAG 汇报演讲稿

下面是每页 PPT 对应的演讲者备注。放映时这些内容位于 PowerPoint 备注区，观众在投影画面中看不到。

## 封面

这一页是汇报封面。我的作业选题是 Redis 垂直领域问答系统。核心思路是把 Redis 官方文档和清洗后的技术语料构造成私有知识库，然后通过 RAG 的方式进行检索增强生成。系统不仅包含一键推理脚本，也包含索引构建、量化评估、报告和 PPT。后面我会按照数据、检索、生成、评估和案例分析的顺序展开。 这一页我会顺着画面把这些信息讲清楚：Redis-RAG：基于 RAG 的 Redis 垂直领域深度问答系统；关键词：私有知识库、混合检索、DeepSeek 生成、三维量化评估；交付物：代码仓库、README、依赖文件、一键推理、报告、PPT、讲稿。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 作业要求与本项目交付

这一页说明作业要求和项目交付之间的对应关系。代码仓库里有 README、requirements 和 infer.py，满足一键运行要求；RAG 核心部分包括 Redis 私有知识库、文档分块、embedding、本地向量库、Query Rewriting、BM25/Vector 混合检索、轻量重排序和引用检查；另外我补充了 BGE embedding、FAISS 和 Chroma 的可选适配，加入 20 条评估问题和检索策略消融对比，展示材料也包括可编辑 Word 报告、PPT、演讲者备注和单独讲稿。 这一页我会顺着画面把这些信息讲清楚：本项目交付完整代码仓库；核心 RAG 模块包括知识库、Chunking、Embedding、向量库、混合检索、重排序、引用检查和生成；展示材料包括报告 Word、PPT、演讲者备注和讲稿。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 为什么选 Redis 作为垂直领域

我选择 Redis 是因为它很适合作为垂直领域。第一，Redis 的知识边界清楚，主题从数据结构到持久化和集群都很明确。第二，Redis 问答里有很多精确术语，比如 AOF、RDB、TTL 和 WATCH，这些词非常考验检索系统。第三，官方文档有稳定 URL，可以作为答案引用来源。这个选题能很好地展示 RAG 的核心价值：把答案约束到可追溯的文档上下文中。 这一页我会顺着画面把这些信息讲清楚：Redis 知识边界清晰；Redis 问答包含大量命令名和缩写；官方文档可追溯，适合做引用和忠实度评估；技术文档 RAG 的难点包括术语匹配、概念混淆和答案忠实度。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 私有知识库构建流程

这一页展示私有知识库构建流程。数据可以来自 Redis 官方文档，经过页面抓取和正文清洗后，保存为 JSONL。每条记录都包含 doc_id、title、url 和 text。doc_id 用于评估，url 用于追溯来源。为了保证作业能稳定运行，我保留了一份内置清洗语料，同时也提供脚本重新抓取官方文档。 这一页我会顺着画面把这些信息讲清楚：流程：官方文档、页面抓取、正文清洗、JSONL 语料、索引构建、问答系统；每条文档包含 doc_id、title、url、text；知识主题覆盖 Redis 数据结构、TTL、持久化、高可用、集群和缓存风险。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 知识库主题覆盖

这一页说明知识库覆盖面。Redis 不是只收集几个命令，而是覆盖了数据结构、生命周期、可靠性、高可用、编程能力和缓存工程。这样设计的好处是评估问题可以比较全面，比如既能问 AOF 和 RDB，也能问 Stream 和 Pub/Sub，或者问缓存击穿怎么缓解。覆盖原则是每个问题都应该能从知识库中找到依据，答案也要能回溯到文档来源，而不是让模型凭印象发挥。 这一页我会顺着画面把这些信息讲清楚：基础数据结构：String、Hash、List、Stream、Sorted Set；生命周期：EXPIRE、TTL、PERSIST；可靠性：RDB、AOF、appendfsync；高可用与扩展：Replication、Sentinel、Cluster；编程与消息：事务、Lua、Pub/Sub、Stream；缓存工程：缓存穿透、击穿和雪崩。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## Chunking：让检索单元既可命中又可阅读

这一页解释 Chunking。技术文档分块不能只按普通句子切，因为 Redis 命令名非常关键。我实现了 Redis-aware tokenizer，保留命令名、缩写和中文领域词。默认分块大小是 320，重叠是 40。这样长文档可以切成可检索片段，同时相邻片段之间不会完全断开。每个 chunk 都有来源元数据，所以最后答案可以回到原文档。 这一页我会顺着画面把这些信息讲清楚：Redis-aware tokenizer 保留命令名、缩写和中文领域词；默认 chunk_size=320，overlap=40；每个 chunk 保留来源元数据；AOF/RDB 问题需要保留持久化、persistence、RDB、AOF、snapshot 等关键 token。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## Embedding 与本地向量数据库

这一页说明 embedding 和向量库的升级。为了保证老师本地一定能跑，默认仍使用 hashing embedding 和 JSONL 本地向量库；为了回应后续扩展要求，我已经加入 SentenceTransformerEmbeddingModel，可以使用 BGE 小模型，也加入 FAISS 和 Chroma 的可选适配器。这样项目不是只停留在 demo，而是保留了课程可复现路径和真实部署升级路径。 这一页我会顺着画面把这些信息讲清楚：默认使用 HashingEmbeddingModel，维度 256；可选使用 BGE/SentenceTransformer embedding；向量库支持本地 JSONL、FAISS adapter 和 Chroma adapter；默认不强制下载模型，保证作业能稳定复现。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 已完成的增强扩展

这一页专门回应之前写在后续工作的扩展项。现在 BGE embedding 已经不是一句展望，而是做成了 SentenceTransformerEmbeddingModel；FAISS 和 Chroma 也做成了可选 vector store adapter；reranker 除了默认轻量版本，还预留了 cross-encoder 入口；评估集从 10 条扩展到 20 条，并新增 compare_retrieval.py 做 pure vector、BM25、hybrid 和 hybrid rerank 的消融对比；最后，生成后会自动输出 citation_check，用来检查引用编号是否有效。 这一页我会顺着画面把这些信息讲清楚：BGE embedding 作为可选 SentenceTransformer 适配器；FAISS 和 Chroma 作为可选向量库 adapter；cross-encoder reranker 作为可选升级路径；评估集扩充到 20 条并加入检索消融；生成后输出 citation_check。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## Query Rewriting：连接中文问题与英文术语

这一页是高级 RAG 优化的第一部分：Query Rewriting。Redis 官方文档很多术语是英文，但用户可能用中文问，比如“持久化”“高可用”“过期”。如果不扩展，检索可能找不到相关英文术语。所以我维护了一个领域词表，把中文问题扩展成 Redis 常用英文概念。这个策略主要提升召回率。 这一页我会顺着画面把这些信息讲清楚：持久化扩展为 persistence、RDB、AOF、snapshot；高可用扩展为 replication、sentinel、failover、cluster；过期扩展为 expire、TTL、timeout；队列扩展为 list、stream、consumer group、XREADGROUP；Query Rewriting 主要提升召回率。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## Hybrid Retrieval：BM25 与向量检索互补

这一页解释混合检索。向量检索能处理语义相似，但是对命令名未必足够敏感。BM25 对精确词非常有效，但不能很好处理同义表达。所以我把二者融合。公式里向量权重是 0.45，BM25 权重是 0.55，因为 Redis 问答中命令名非常关键。这个策略比单纯向量检索更适合 Redis 技术文档。 这一页我会顺着画面把这些信息讲清楚：融合公式：score = 0.45 × vector + 0.55 × BM25；向量检索擅长语义相似；BM25 擅长 AOF、RDB、TTL、WATCH 等精确术语；Redis 问答需要语义理解和精确术语命中结合。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 端到端系统架构

这一页展示端到端架构。左边是文档处理和索引构建，文档先变成 chunk，再进入 embedding 和 BM25。右边是在线问答流程，用户问题先经过 Query Rewriting，然后由 Hybrid Retriever 找到候选上下文，再经过轻量 reranker 根据术语覆盖率和标题覆盖率做二次排序。最后系统把高质量上下文传给 DeepSeek 或抽取式生成器，并输出带引用答案。这样设计的重点是可观测、可替换和可复现：检索分数能看到，embedding 和向量库能替换，没有 API key 时也能跑完整流程。 这一页我会顺着画面把这些信息讲清楚：文档 JSONL 经过 Chunking 后进入 Embedding 和 BM25；用户问题经过 Query Rewriting 后进入 Hybrid Retriever；Top-k 候选经过轻量 reranker 二次排序；最终上下文传入 DeepSeek 或抽取式生成器；输出带引用答案和可解释检索分数。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 生成模块：DeepSeek 优先，离线可回退

这一页说明生成模块。项目支持 DeepSeek，只要设置 DEEPSEEK_API_KEY，默认模型就是 deepseek-v4-pro。同时我保留了抽取式回退，保证没有 API key 也能运行。为了降低幻觉，系统提示要求模型只能依据检索上下文回答，并带引用。如果上下文不足，就要说明无法确认。这里也强调，API key 不会写入仓库，只通过环境变量传入。 这一页我会顺着画面把这些信息讲清楚：设置 DEEPSEEK_API_KEY 后默认使用 deepseek-v4-pro；没有 API key 时使用抽取式生成器；提示词要求只能基于上下文回答，并带来源引用；API key 不写入仓库。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 量化评估：三个维度衡量 RAG 能力

这一页介绍评估方案。Context Relevance 主要评价检索是否找到了相关文档，Faithfulness 评价答案是否被上下文支持，也就是是否有幻觉风险，Answer Relevance 评价答案是否覆盖问题的关键点；这次评估集已经从 10 条扩充到 20 条，覆盖 String、Hash、List、Stream、持久化、高可用、Cluster、Lua、缓存风险等主题，输出结果会保存成 JSON 和 CSV，方便报告引用。 这一页我会顺着画面把这些信息讲清楚：Context Relevance 衡量检索上下文是否相关；Faithfulness 衡量答案是否忠实于上下文；Answer Relevance 衡量答案是否回答问题；评估集包含 20 条 Redis 技术问题。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 实验结果与解释

这一页展示实验结果。图里的数值不是手工写的，而是实际运行 evaluate.py --rebuild 后从 outputs/eval_results.json 中读取并生成的；20 条评估问题下，Context Relevance 是 0.9750，说明检索整体覆盖稳定但多文档问题仍有少量漏召回，Faithfulness 是 0.8319，说明答案大多数内容能被上下文支持，Answer Relevance 是 0.9375，说明答案基本覆盖问题要点；这个结果比只跑 10 条问题更有说服力。 这一页我会顺着画面把这些信息讲清楚：Context Relevance = 0.9750；Faithfulness = 0.8319；Answer Relevance = 0.9375；检索效果较稳，答案忠实度较好，部分关键词覆盖仍可提升。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 检索策略消融：Vector、BM25、Hybrid 对比

这一页是新增的检索消融实验。compare_retrieval.py 会在同一批 20 条问题上对比 pure vector、BM25、hybrid 和 hybrid rerank，可以看到 pure vector 的 Context Relevance、Top-1 Hit 和 MRR 都明显低一些，说明只靠语义向量不够适合 Redis 这种命令名密集的技术文档；BM25 和 hybrid 表现更稳，hybrid rerank 的主要价值是保留最终排序和术语覆盖等可解释字段，方便做 bad case 分析。 这一页我会顺着画面把这些信息讲清楚：pure vector 的 Context Relevance、Top-1 Hit 和 MRR 都低于 BM25 和 hybrid；BM25 在 Redis 这种命令密集型知识库里非常强；hybrid 和 hybrid_rerank 保持 Top-1 与 MRR 稳定，同时提供更完整的可解释字段。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## 案例分析：AOF 与 RDB 持久化问答

这一页用 AOF 和 RDB 问题做案例。这里放的是脚本真实运行输出，不是后期编造的截图。系统最终命中了 redis:persistence 文档，最终 score 是 1.0819，其中 hybrid combined_score 是 1.0000，reranker 又根据 AOF、RDB、persistence 等术语覆盖给了额外奖励。答案解释了 RDB 是快照，适合备份和快速恢复；AOF 是追加日志，通常数据安全性更好。这个案例能说明 Query Rewriting、BM25 精确术语匹配和轻量重排序的价值：中文问题会扩展到 persistence、snapshot 和 append only file，同时 AOF 和 RDB 被精确命中。 这一页我会顺着画面把这些信息讲清楚：问题是 Redis 的 AOF 和 RDB 持久化有什么区别；系统命中文档 redis:persistence；最终 score = 1.0819，说明 rerank 在 hybrid score 基础上加入术语覆盖奖励；答案包含 RDB 快照、AOF 追加日志、备份恢复和数据安全性；命中原因是 Query Rewriting、BM25 精确术语匹配和轻量重排序共同作用。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。

## Bad Case、改进方向与总结

最后一页总结问题和改进。表格来自 infer.py --json 的真实输出，可以看到 redis:persistence 排名第一，score 和 rerank_score 都是 1.0819，term_coverage 明显高于其他候选；一个典型 bad case 是 AOF/RDB 问题仍会召回 Pub/Sub，因为 Pub/Sub 文档也出现了“不会持久化”这类词；为了解决这个问题，我加入了 Query Rewriting、BM25/Vector 混合检索、轻量重排序和生成阶段上下文过滤，并且已经完成 BGE embedding、FAISS/Chroma adapter、20 条评估集、检索消融对比和 citation checking 等扩展，整体项目已经形成从知识库、检索、生成、评估到展示材料的完整闭环。 这一页我会顺着画面把这些信息讲清楚：真实 JSON 输出展示 score、combined_score、rerank_score 和 term_coverage；Bad Case：AOF/RDB 问题仍会召回 Pub/Sub 弱相关文档；已做改进：Query Rewriting、混合检索、轻量重排序和上下文过滤；已完成扩展：BGE/FAISS 可选适配、20 条评估集、检索消融和 citation checking。讲的时候我会把它们串成“为什么这样设计、系统如何实现、结果说明什么”这条线索，整页讲完后自然过渡到下一页。
