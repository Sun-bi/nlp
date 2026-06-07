# Redis RAG Coursework Design

## Goal

Build a complete Redis-domain RAG coursework repository with runnable code, README, evaluation, report, and presentation.

## Scope

The project uses Redis official documentation and cleaned Redis study notes as the private vertical knowledge base. It implements document cleaning, chunking, local embeddings, persistent vector storage, hybrid retrieval, query rewriting, grounded generation, and quantitative evaluation.

## Architecture

Documents are stored as JSONL records. The index builder tokenizes each document with Redis-aware mixed Chinese/English tokenization, creates overlapping chunks, writes chunks, and stores vectors in a JSONL vector database. At inference time, the question is rewritten with Redis domain expansions, searched with vector similarity and BM25, then passed to a grounded generator. If OpenAI-compatible API variables are configured, the generator calls an LLM; otherwise it uses an extractive fallback.

## Evaluation

The evaluation set contains Redis questions with gold document IDs and expected keywords. Metrics are Context Relevance, Faithfulness, and Answer Relevance. Outputs are saved as JSON and CSV under `outputs/`.

## Deliverables

- Code repository with `README.md`, `requirements.txt`, tests, and scripts.
- One-command inference via `python3 infer.py --question "..."`
- Report under `report/`.
- PPTX presentation under `slides/`.
