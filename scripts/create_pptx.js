const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Redis RAG Coursework";
pptx.subject = "基于 RAG 的 Redis 垂直领域深度问答系统构建";
pptx.title = "Redis-RAG 垂直领域深度问答系统";
pptx.company = "Coursework";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  lang: "zh-CN",
};
pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pptx.layout = "WIDE";

const C = {
  red: "DC382D",
  dark: "1F2933",
  text: "263238",
  muted: "64748B",
  light: "F8FAFC",
  panel: "FFFFFF",
  line: "CBD5E1",
  amber: "F59E0B",
  teal: "0F766E",
};

function addTopBar(slide, title, kicker = "Redis RAG") {
  slide.background = { color: C.light };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.42, fill: { color: C.red }, line: { color: C.red } });
  slide.addText(kicker, { x: 0.55, y: 0.10, w: 2.2, h: 0.2, fontFace: "Arial", fontSize: 7.5, bold: true, color: "FFFFFF", margin: 0 });
  slide.addText(title, { x: 0.55, y: 0.62, w: 10.5, h: 0.42, fontFace: "Arial", fontSize: 21, bold: true, color: C.dark, margin: 0 });
}

function addFooter(slide, page) {
  slide.addText(`Redis-RAG 作业汇报  |  ${page}`, { x: 0.55, y: 7.13, w: 12.2, h: 0.18, fontFace: "Arial", fontSize: 7.5, color: C.muted, margin: 0 });
}

function bullet(slide, items, x, y, w, h, size = 13) {
  slide.addText(items.map((t) => ({ text: t, options: { bullet: { indent: 13 }, hanging: 3 } })), {
    x, y, w, h,
    fontFace: "Arial",
    fontSize: size,
    color: C.text,
    breakLine: false,
    fit: "shrink",
    valign: "mid",
  });
}

function card(slide, x, y, w, h, title, body, accent = C.red) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: C.panel }, line: { color: C.line, width: 1 } });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color: accent }, line: { color: accent } });
  slide.addText(title, { x: x + 0.22, y: y + 0.18, w: w - 0.35, h: 0.25, fontFace: "Arial", fontSize: 12.5, bold: true, color: C.dark, margin: 0 });
  slide.addText(body, { x: x + 0.22, y: y + 0.58, w: w - 0.35, h: h - 0.72, fontFace: "Arial", fontSize: 10.5, color: C.text, fit: "shrink", breakLine: false, valign: "top", margin: 0 });
}

function box(slide, x, y, w, h, text, fill = "FFFFFF", line = C.red) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { color: line, width: 1.2 } });
  slide.addText(text, { x: x + 0.08, y: y + 0.12, w: w - 0.16, h: h - 0.2, fontFace: "Arial", fontSize: 11.2, bold: true, color: C.dark, align: "center", valign: "mid", fit: "shrink", margin: 0 });
}

function arrow(slide, x1, y1, x2, y2) {
  slide.addShape(pptx.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: C.red, width: 1.4, beginArrowType: "none", endArrowType: "triangle" } });
}

// 1
{
  const slide = pptx.addSlide();
  slide.background = { color: C.dark };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: C.dark }, line: { color: C.dark } });
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.22, h: 7.5, fill: { color: C.red }, line: { color: C.red } });
  slide.addText("Redis-RAG", { x: 0.8, y: 1.15, w: 7.4, h: 0.55, fontFace: "Arial", fontSize: 34, bold: true, color: "FFFFFF", margin: 0 });
  slide.addText("基于 RAG 的垂直领域深度问答系统构建", { x: 0.8, y: 1.9, w: 8.6, h: 0.45, fontFace: "Arial", fontSize: 21, color: "F8FAFC", margin: 0 });
  slide.addText("知识库：Redis 官方文档与清洗技术语料\n优化策略：Query Rewriting + BM25/Vector Hybrid Retrieval\n交付：代码仓库、README、一键推理、量化评估、报告、PPT", { x: 0.85, y: 3.0, w: 7.7, h: 1.1, fontFace: "Arial", fontSize: 14, color: "E2E8F0", breakLine: false, fit: "shrink", margin: 0 });
  slide.addShape(pptx.ShapeType.roundRect, { x: 9.25, y: 1.25, w: 2.75, h: 2.75, rectRadius: 0.08, fill: { color: C.red }, line: { color: C.red } });
  slide.addText("RAG", { x: 9.55, y: 2.0, w: 2.15, h: 0.5, fontFace: "Arial", fontSize: 34, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  slide.addText("Redis Docs\nQA System", { x: 9.55, y: 2.75, w: 2.15, h: 0.55, fontFace: "Arial", fontSize: 13, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  slide.addText("2026.06", { x: 0.85, y: 6.8, w: 1.8, h: 0.2, fontFace: "Arial", fontSize: 9, color: "CBD5E1", margin: 0 });
}

// 2
{
  const slide = pptx.addSlide();
  addTopBar(slide, "作业目标与系统选题");
  card(slide, 0.7, 1.35, 3.8, 4.6, "为什么选 Redis", "Redis 是典型垂直技术领域，包含数据结构、命令、持久化、高可用和缓存风险等主题。问题中常出现 AOF、RDB、TTL、XREADGROUP 等精确术语，适合展示 RAG 检索优化。", C.red);
  card(slide, 4.8, 1.35, 3.8, 4.6, "课程要求映射", "私有知识库：Redis 文档语料\nChunking：Redis-aware tokenizer + overlap\nEmbedding：hashing embedding\n向量库：JSONL local vector DB\n生成：DeepSeek/OpenAI-compatible + fallback\n评估：三维量化指标", C.teal);
  card(slide, 8.9, 1.35, 3.8, 4.6, "交付物", "README.md\nrequirements.txt\ninfer.py 一键推理\nbuild_index.py / evaluate.py\nreport/redis_rag_report.md + PDF\nslides/redis_rag_presentation.pptx", C.amber);
  addFooter(slide, 2);
}

// 3
{
  const slide = pptx.addSlide();
  addTopBar(slide, "私有知识库构建");
  bullet(slide, [
    "内置清洗语料：data/raw/redis_seed_docs.jsonl，保证离线可复现",
    "官方文档采集：scripts/collect_redis_docs.py 抓取 Redis 文档页面",
    "知识主题覆盖：String、Hash、List、Stream、Sorted Set、TTL、淘汰、RDB/AOF、Replication、Sentinel、Cluster、Lua、Pub/Sub、缓存风险",
    "每条文档包含 doc_id、title、url、text，便于引用和评估"
  ], 0.8, 1.35, 6.15, 3.1, 13);
  slide.addShape(pptx.ShapeType.roundRect, { x: 7.25, y: 1.35, w: 5.2, h: 3.8, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("JSONL 示例", { x: 7.55, y: 1.65, w: 1.8, h: 0.25, fontFace: "Arial", fontSize: 12, bold: true, color: C.red, margin: 0 });
  slide.addText('{ "doc_id": "redis:persistence",\n  "title": "Redis persistence with RDB and AOF",\n  "url": "https://redis.io/docs/...",\n  "text": "Redis 提供 RDB 和 AOF 两类持久化机制..." }', { x: 7.55, y: 2.12, w: 4.55, h: 1.8, fontFace: "Courier New", fontSize: 10.5, color: C.dark, fit: "shrink", breakLine: false, margin: 0 });
  slide.addText("设计重点：语料必须可追溯、可重建、可离线运行。", { x: 7.55, y: 4.45, w: 4.4, h: 0.36, fontFace: "Arial", fontSize: 12.2, color: C.text, bold: true, margin: 0 });
  addFooter(slide, 3);
}

// 4
{
  const slide = pptx.addSlide();
  addTopBar(slide, "系统架构与数据流");
  box(slide, 0.65, 1.45, 1.55, 0.78, "Redis 文档", "FFFFFF");
  box(slide, 2.65, 1.45, 1.65, 0.78, "清洗 JSONL", "FFFFFF");
  box(slide, 4.75, 1.45, 1.7, 0.78, "Chunking", "FFFFFF");
  box(slide, 7.0, 0.95, 1.75, 0.78, "Embedding", "FFFFFF", C.teal);
  box(slide, 7.0, 2.05, 1.75, 0.78, "BM25", "FFFFFF", C.amber);
  box(slide, 9.3, 1.45, 1.7, 0.78, "Hybrid\nRetriever", "FFFFFF");
  box(slide, 11.45, 1.45, 1.45, 0.78, "答案生成", "FFFFFF");
  arrow(slide, 2.2, 1.84, 2.65, 1.84);
  arrow(slide, 4.3, 1.84, 4.75, 1.84);
  arrow(slide, 6.45, 1.84, 7.0, 1.34);
  arrow(slide, 6.45, 1.84, 7.0, 2.44);
  arrow(slide, 8.75, 1.34, 9.3, 1.75);
  arrow(slide, 8.75, 2.44, 9.3, 1.94);
  arrow(slide, 11.0, 1.84, 11.45, 1.84);
  card(slide, 0.85, 3.65, 3.65, 1.55, "Query Rewriting", "中文领域问题扩展为 Redis 英文术语，例如“持久化”扩展到 persistence、RDB、AOF、snapshot。", C.red);
  card(slide, 4.85, 3.65, 3.65, 1.55, "Vector DB", "将 chunk 和向量持久化到 data/index/vectors.jsonl，可重复加载，不依赖外部数据库。", C.teal);
  card(slide, 8.85, 3.65, 3.65, 1.55, "Grounded Answer", "生成器只基于检索上下文回答，并在答案中保留 [1] 形式来源引用。", C.amber);
  addFooter(slide, 4);
}

// 5
{
  const slide = pptx.addSlide();
  addTopBar(slide, "高级 RAG 优化：Query Rewriting + 混合检索");
  slide.addText("融合分数", { x: 0.8, y: 1.28, w: 1.8, h: 0.28, fontFace: "Arial", fontSize: 13, bold: true, color: C.red, margin: 0 });
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.8, y: 1.72, w: 5.3, h: 0.78, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("score = 0.45 × vector_score + 0.55 × bm25_score", { x: 1.05, y: 1.96, w: 4.8, h: 0.25, fontFace: "Courier New", fontSize: 13, bold: true, color: C.dark, margin: 0 });
  bullet(slide, [
    "向量检索：捕捉语义相似表达",
    "BM25：保留命令名、缩写和精确概念",
    "Query Rewriting：打通中文提问与英文官方术语"
  ], 0.95, 3.0, 5.1, 1.35, 12.5);
  const rows = [
    ["用户词", "扩展词"],
    ["持久化", "persistence, RDB, AOF, snapshot"],
    ["高可用", "replication, sentinel, failover"],
    ["过期", "expire, TTL, timeout"],
    ["队列", "list, stream, consumer group"]
  ];
  slide.addTable(rows, {
    x: 6.8, y: 1.35, w: 5.65, h: 3.45,
    border: { type: "solid", color: C.line, pt: 0.8 },
    fontFace: "Arial",
    fontSize: 10.5,
    color: C.text,
    fill: "FFFFFF",
    margin: 0.08,
    autoFit: false,
    valign: "mid",
  });
  slide.addText("为什么适合 Redis：技术问答里 AOF、RDB、TTL 等术语必须精确命中，纯语义检索容易漏掉或混入弱相关片段。", { x: 0.9, y: 5.4, w: 11.5, h: 0.55, fontFace: "Arial", fontSize: 13.5, bold: true, color: C.dark, margin: 0, fit: "shrink" });
  addFooter(slide, 5);
}

// 6
{
  const slide = pptx.addSlide();
  addTopBar(slide, "生成模块：DeepSeek 优先，抽取式回退");
  card(slide, 0.75, 1.25, 5.55, 1.45, "DeepSeek/OpenAI-compatible LLM", "设置 DEEPSEEK_API_KEY 后，系统默认调用 deepseek-v4-pro；也兼容 OPENAI_API_KEY、OPENAI_BASE_URL、OPENAI_MODEL。", C.red);
  card(slide, 0.75, 3.05, 5.55, 1.45, "无 Key 可复现", "没有 API key 时自动使用抽取式生成器，只从检索上下文中选句，保证作业演示不被外部服务阻塞。", C.teal);
  card(slide, 0.75, 4.85, 5.55, 1.45, "防幻觉约束", "系统提示要求只能依据上下文回答；生成阶段还会过滤弱相关上下文，减少答案污染。", C.amber);
  slide.addShape(pptx.ShapeType.roundRect, { x: 7.0, y: 1.25, w: 5.45, h: 4.85, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("一键推理", { x: 7.35, y: 1.55, w: 1.4, h: 0.28, fontFace: "Arial", fontSize: 13, bold: true, color: C.red, margin: 0 });
  slide.addText("python3 infer.py \\\n  --question \"Redis Sentinel 主要解决什么问题？\"", { x: 7.35, y: 2.15, w: 4.65, h: 0.7, fontFace: "Courier New", fontSize: 11, color: C.dark, margin: 0 });
  slide.addText("可选环境变量", { x: 7.35, y: 3.28, w: 1.6, h: 0.25, fontFace: "Arial", fontSize: 12, bold: true, color: C.dark, margin: 0 });
  slide.addText("DEEPSEEK_API_KEY\nOPENAI_MODEL=deepseek-v4-pro", { x: 7.35, y: 3.72, w: 4.8, h: 0.68, fontFace: "Courier New", fontSize: 11, color: C.text, margin: 0 });
  slide.addText("API key 不写入代码仓库。", { x: 7.35, y: 5.18, w: 4.5, h: 0.25, fontFace: "Arial", fontSize: 11.5, bold: true, color: C.red, margin: 0 });
  addFooter(slide, 6);
}

// 7
{
  const slide = pptx.addSlide();
  addTopBar(slide, "量化评估设计");
  const rows = [
    ["维度", "定义", "实现方式"],
    ["Context Relevance", "检索上下文是否覆盖标注相关文档", "Top-k doc_id 与 gold_doc_ids 的覆盖率"],
    ["Faithfulness", "答案是否被上下文支持", "答案 token 在上下文 token 中的支持比例"],
    ["Answer Relevance", "答案是否回应问题要点", "期望关键词覆盖率"]
  ];
  slide.addTable(rows, {
    x: 0.75, y: 1.35, w: 11.85, h: 2.35,
    border: { type: "solid", color: C.line, pt: 0.7 },
    fontFace: "Arial",
    fontSize: 10.5,
    color: C.text,
    fill: "FFFFFF",
    margin: 0.08,
    valign: "mid",
  });
  card(slide, 0.75, 4.3, 3.75, 1.3, "评估集", "10 条 Redis 技术问题，覆盖持久化、过期、Stream、Sentinel、Cluster、事务、Lua、缓存风险等主题。", C.red);
  card(slide, 4.8, 4.3, 3.75, 1.3, "输出文件", "outputs/eval_results.json\noutputs/eval_results.csv", C.teal);
  card(slide, 8.85, 4.3, 3.75, 1.3, "运行命令", "python3 evaluate.py --rebuild", C.amber);
  addFooter(slide, 7);
}

// 8
{
  const slide = pptx.addSlide();
  addTopBar(slide, "实验结果");
  const metrics = [
    ["Context Relevance", 1.0, C.red],
    ["Faithfulness", 0.8116, C.teal],
    ["Answer Relevance", 0.875, C.amber],
  ];
  metrics.forEach((m, i) => {
    const y = 1.45 + i * 1.35;
    slide.addText(m[0], { x: 0.9, y, w: 2.7, h: 0.26, fontFace: "Arial", fontSize: 12.5, bold: true, color: C.dark, margin: 0 });
    slide.addShape(pptx.ShapeType.rect, { x: 3.85, y: y + 0.02, w: 6.2, h: 0.28, fill: { color: "E5E7EB" }, line: { color: "E5E7EB" } });
    slide.addShape(pptx.ShapeType.rect, { x: 3.85, y: y + 0.02, w: 6.2 * m[1], h: 0.28, fill: { color: m[2] }, line: { color: m[2] } });
    slide.addText(m[1].toFixed(4), { x: 10.35, y: y - 0.02, w: 1.1, h: 0.28, fontFace: "Arial", fontSize: 12.5, bold: true, color: C.dark, margin: 0 });
  });
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.9, y: 5.55, w: 11.45, h: 0.7, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("结论：系统能稳定检索到相关文档；答案基本由检索上下文支持；部分 Answer Relevance 损失来自抽取句与期望关键词表述不完全一致。", { x: 1.2, y: 5.78, w: 10.85, h: 0.25, fontFace: "Arial", fontSize: 12.2, bold: true, color: C.dark, margin: 0, fit: "shrink" });
  addFooter(slide, 8);
}

// 9
{
  const slide = pptx.addSlide();
  addTopBar(slide, "Bad Case 与局限");
  card(slide, 0.75, 1.25, 5.75, 1.55, "Bad Case：持久化问题混入 Pub/Sub", "早期检索中 Pub/Sub 文档因为出现“不会持久化”等词，被排到较前位置。说明技术文档中共现词可能造成弱相关上下文污染。", C.red);
  card(slide, 6.85, 1.25, 5.75, 1.55, "修正：生成阶段上下文过滤", "生成器只使用与最高分足够接近的上下文。最终 AOF/RDB 问题只引用 persistence 文档，答案更聚焦。", C.teal);
  card(slide, 0.75, 3.45, 3.75, 1.45, "局限 1", "默认 hashing embedding 可复现，但语义能力弱于 BGE/SentenceTransformer。", C.amber);
  card(slide, 4.8, 3.45, 3.75, 1.45, "局限 2", "内置评估集规模较小，适合课程演示，真实系统需要更多人工标注问题。", C.amber);
  card(slide, 8.85, 3.45, 3.75, 1.45, "局限 3", "接入 LLM 后表达更自然，但仍需持续监控 Faithfulness 防止幻觉。", C.amber);
  addFooter(slide, 9);
}

// 10
{
  const slide = pptx.addSlide();
  addTopBar(slide, "总结");
  bullet(slide, [
    "完成 Redis 私有知识库、Chunking、Embedding、向量库、检索、生成和评估闭环",
    "实现 Query Rewriting + BM25/Vector Hybrid Retrieval，贴合 Redis 命令密集型问答",
    "支持 DeepSeek deepseek-v4-pro，同时保留无 Key 抽取式回退",
    "交付完整仓库：README、requirements、一键推理、报告和 PPT"
  ], 0.9, 1.35, 7.0, 2.7, 14);
  slide.addShape(pptx.ShapeType.roundRect, { x: 8.55, y: 1.35, w: 3.8, h: 3.25, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("推荐演示命令", { x: 8.85, y: 1.72, w: 1.8, h: 0.24, fontFace: "Arial", fontSize: 12.5, bold: true, color: C.red, margin: 0 });
  slide.addText("python3 infer.py --question \\\n\"Redis 的 AOF 和 RDB 持久化有什么区别？\"\n\npython3 evaluate.py --rebuild", { x: 8.85, y: 2.2, w: 3.15, h: 1.35, fontFace: "Courier New", fontSize: 9.7, color: C.dark, fit: "shrink", breakLine: false, margin: 0 });
  slide.addText("谢谢", { x: 0.95, y: 5.85, w: 2.2, h: 0.45, fontFace: "Arial", fontSize: 26, bold: true, color: C.red, margin: 0 });
  addFooter(slide, 10);
}

async function main() {
  await pptx.writeFile({ fileName: "slides/redis_rag_presentation.pptx" });
  console.log("slides/redis_rag_presentation.pptx");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
