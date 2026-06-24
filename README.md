# Redis 垂直领域 RAG 问答系统

本仓库是“基于 RAG 的垂直领域深度问答系统构建”课程作业的完整提交版本。项目围绕 Redis 官方文档构建私有知识库，实现文档清洗、技术词分块、哈希嵌入、本地向量索引、关键词和语义混合检索、二阶段重排序、带引用答案生成、引用检查和量化评估。

## 1. 提交材料

| 老师要求 | 本仓库对应文件 |
|---|---|
| 完整代码仓库 | `src/rag_redis/`、`infer.py`、`build_index.py`、`evaluate.py`、`compare_retrieval.py`、`scripts/` |
| 清晰的 `README.md` | 当前文件 |
| 环境依赖 `requirements.txt` | `requirements.txt` |
| 一键运行推理脚本 | `run_infer.sh` 和 `infer.py` |
| 私有知识库 | `data/raw/redis_official_docs.jsonl` |
| 已构建索引 | `data/index_official/chunks.jsonl`、`data/index_official/vectors.jsonl` |
| 论文/报告 | `report/redis_rag_report.docx`、`report/redis_rag_report.md` |
| 汇报 PPT | `slides/rag.pptx` |
| 讲稿备份 | `slides/redis_rag_speaker_script.md` |
| 前端可视化展示 | `frontend/redis_rag_dashboard.html`，PPT 最后一页已放展示效果 |

## 2. 项目结构

```text
.
├── README.md
├── requirements.txt
├── run_infer.sh                    # 一键推理脚本，默认使用官方文档知识库
├── infer.py                        # 命令行推理入口
├── build_index.py                  # 构建知识库索引
├── evaluate.py                     # 三维量化评估
├── compare_retrieval.py            # 检索策略消融对比
├── src/rag_redis/                  # RAG 核心实现
├── data/
│   ├── raw/redis_official_docs.jsonl
│   ├── raw/redis_seed_docs.jsonl
│   ├── index_official/
│   ├── index/
│   └── eval/eval_questions.jsonl
├── report/
│   ├── redis_rag_report.docx
│   └── redis_rag_report.md
├── slides/
│   ├── rag.pptx
│   ├── redis_rag_speaker_script.md
│   └── assets/
├── frontend/redis_rag_dashboard.html
├── scripts/
└── tests/
```

## 3. 环境安装

推荐使用 Python 3.9 及以上版本。

```bash
cd /Users/sun/deeplearning/nlp
python3 -m pip install -r requirements.txt
```

默认推理链路不需要下载大模型，也不需要 GPU。系统默认使用本地哈希嵌入和本地索引文件，方便在课堂或验收电脑上复现。

可选增强依赖已经写在 `requirements.txt` 注释中。如果要运行神经嵌入、FAISS 或 Chroma，可以手动安装：

```bash
python3 -m pip install sentence-transformers faiss-cpu chromadb
```

## 4. 一键运行推理

最简单方式：

```bash
./run_infer.sh
```

传入自己的问题：

```bash
./run_infer.sh "Redis 的 AOF 和 RDB 持久化有什么区别？"
```

等价的 Python 命令：

```bash
python3 infer.py \
  --corpus data/raw/redis_official_docs.jsonl \
  --index-dir data/index_official \
  --question "Redis 的 AOF 和 RDB 持久化有什么区别？"
```

如果想输出机器可读的 JSON：

```bash
python3 infer.py \
  --corpus data/raw/redis_official_docs.jsonl \
  --index-dir data/index_official \
  --question "Redis Stream 和 Pub/Sub 有什么区别？" \
  --json
```

输出会包含：

- 问题和答案
- 来源引用
- 检索到的文档片段
- 综合分数、向量分数、关键词分数、重排序分数
- 引用检查结果

## 5. 重新构建索引

仓库中已经包含官方文档索引，一般不需要重新构建。如果需要重新构建：

```bash
python3 build_index.py \
  --corpus data/raw/redis_official_docs.jsonl \
  --index-dir data/index_official
```

当前官方文档知识库包含：

- `data/raw/redis_official_docs.jsonl`：14 篇 Redis 官方文档主题
- `data/index_official/chunks.jsonl`：196 个检索片段
- `data/index_official/vectors.jsonl`：196 条本地向量记录

## 6. 系统方案

最终方案采用：

```text
官方文档知识库 + 技术词分块 + 哈希嵌入 + 本地索引文件
+ 关键词/语义混合检索 + 二阶段重排序 + 引用检查
```

核心模块位置：

| 模块 | 文件 | 说明 |
|---|---|---|
| 文档读取 | `src/rag_redis/corpus.py` | 读取 JSONL 知识库 |
| 文本处理 | `src/rag_redis/text.py` | 归一化和 Redis 技术词分词 |
| 文档分块 | `src/rag_redis/chunking.py` | 重叠分块，保留上下文 |
| 哈希嵌入 | `src/rag_redis/embeddings.py` | 本地生成向量，不依赖外部模型 |
| 本地索引 | `src/rag_redis/vector_store.py` | 保存片段、来源和向量 |
| 查询改写 | `src/rag_redis/query.py` | 扩展中文问题中的 Redis 术语 |
| 混合检索 | `src/rag_redis/retriever.py` | 关键词检索和向量检索融合 |
| 答案生成 | `src/rag_redis/generator.py` | 支持 DeepSeek，也支持本地抽取式回退 |
| 引用检查 | `src/rag_redis/citations.py` | 检查答案来源编号是否有效 |
| 量化评估 | `src/rag_redis/evaluation.py` | 上下文相关性、忠实度、答案相关性 |

## 7. DeepSeek 生成模式

没有 API key 时，系统会自动使用本地抽取式生成器，保证离线可运行。

如果要使用 DeepSeek：

```bash
export DEEPSEEK_API_KEY="你的 API Key"
export OPENAI_MODEL="deepseek-v4-pro"
./run_infer.sh "Redis Sentinel 主要解决什么问题？"
```

不要把 API key 写进代码、报告、PPT 或提交记录。

## 8. 评估与消融实验

运行三维量化评估：

```bash
python3 evaluate.py \
  --corpus data/raw/redis_official_docs.jsonl \
  --index-dir data/index_official
```

运行检索策略消融对比：

```bash
python3 compare_retrieval.py \
  --corpus data/raw/redis_official_docs.jsonl \
  --index-dir data/index_official
```

评估结果文件：

```text
outputs/eval_results.json
outputs/eval_results.csv
outputs/retrieval_comparison.json
outputs/retrieval_comparison.csv
```

## 9. 测试

```bash
PYTHONPATH=src python3 -m pytest tests -q
```

测试覆盖文本处理、分块、检索、可选后端参数、生成、引用检查和评估指标。

## 10. 报告和 PPT

论文式报告：

```text
report/redis_rag_report.docx
report/redis_rag_report.md
```

汇报 PPT：

```text
slides/rag.pptx
```

PPT 已经包含最终方案页、中文系统架构页、评估结果、前端可视化展示页和讲稿备注。讲稿备份在：

```text
slides/redis_rag_speaker_script.md
```

前端可视化页面：

```text
frontend/redis_rag_dashboard.html
```

## 11. 提交建议

提交时建议保留以下内容：

- 根目录所有 Python 脚本和 `src/`
- `README.md`
- `requirements.txt`
- `run_infer.sh`
- `data/raw/redis_official_docs.jsonl`
- `data/index_official/`
- `data/eval/`
- `report/`
- `slides/rag.pptx`
- `slides/assets/`
- `frontend/`
- `tests/`

不需要提交的内容：

- `.DS_Store`
- `.pytest_cache/`
- `__pycache__/`
- PowerPoint/WPS 临时锁文件
- `outputs/ppt_preview/`
