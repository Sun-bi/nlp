# Redis-RAG 项目提交清单

## 必交文件

- `README.md`：项目说明、环境安装、运行方法。
- `requirements.txt`：Python 环境依赖。
- `run_infer.sh`：一键推理脚本。
- `infer.py`：Python 推理入口。
- `build_index.py`：索引构建脚本。
- `evaluate.py`：量化评估脚本。
- `compare_retrieval.py`：检索策略消融脚本。
- `src/rag_redis/`：RAG 系统核心代码。
- `data/raw/redis_official_docs.jsonl`：Redis 官方文档知识库。
- `data/index_official/`：已构建好的官方文档索引。
- `data/eval/eval_questions.jsonl`：评估问题集。
- `report/redis_rag_report.docx`：论文式报告。
- `report/redis_rag_report.md`：报告源码备份。
- `slides/rag.pptx`：汇报 PPT。
- `slides/assets/`：PPT 使用的图表和运行截图。
- `slides/redis_rag_speaker_script.md`：逐页讲稿。
- `frontend/redis_rag_dashboard.html`：前端可视化展示页面。

## 运行检查

```bash
python3 -m pip install -r requirements.txt
./run_infer.sh
PYTHONPATH=src python3 -m pytest tests -q
```

- `.DS_Store`
- `.pytest_cache/`
- `__pycache__/`
- `.env`
- PowerPoint/WPS 临时锁文件
- `outputs/ppt_preview/`
- 任何 API key 或私人账号信息
