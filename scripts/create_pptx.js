const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pptx.layout = "WIDE";
pptx.author = "Redis RAG Coursework";
pptx.subject = "基于 RAG 的 Redis 垂直领域深度问答系统构建";
pptx.title = "Redis-RAG 垂直领域深度问答系统";
pptx.company = "Coursework";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};

const OUT_PPTX = "slides/redis_rag_presentation.pptx";
const OUT_SCRIPT = "slides/redis_rag_speaker_script.md";
const ASSET_DIR = "slides/assets";
const TOTAL = 15;

const C = {
  redis: "D92D20",
  redisDark: "8A1C14",
  ink: "17212B",
  text: "24313D",
  muted: "64748B",
  bg: "F7F9FC",
  panel: "FFFFFF",
  line: "CBD5E1",
  paleRed: "FDE8E5",
  paleBlue: "EAF2FF",
  paleGreen: "E9F8F4",
  amber: "F59E0B",
  teal: "0F766E",
  blue: "2563EB",
  gray: "E5E7EB",
};

const speaker = [
  "# Redis-RAG 汇报逐页讲稿",
  "",
  "说明：每一页都包含“页面内容”和“讲稿”。讲稿已经覆盖该页主要可见内容，可以在汇报时直接照着念，并根据现场时间删减。",
  "",
];

function font(size, color = C.text, bold = false) {
  return { fontFace: "Microsoft YaHei", fontSize: size, color, bold, margin: 0 };
}

function asset(name) {
  return path.join(ASSET_DIR, name);
}

function addImagePanel(slide, name, x, y, w, h, outline = C.line) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.04,
    fill: { color: "FFFFFF" },
    line: { color: outline, width: 1 },
  });
  slide.addImage({ path: asset(name), x: x + 0.06, y: y + 0.06, w: w - 0.12, h: h - 0.12 });
}

function addNotes(slide, page, title, visibleLines, notes) {
  const visible = visibleLines.join("\n");
  slide.addNotes(`第 ${page} 页：${title}\n\n页面内容：\n${visible}\n\n讲稿：\n${notes}`);
  speaker.push(`## 第 ${page} 页：${title}`);
  speaker.push("");
  speaker.push("### 页面内容");
  speaker.push("");
  visibleLines.forEach((line) => speaker.push(`- ${line}`));
  speaker.push("");
  speaker.push("### 讲稿");
  speaker.push("");
  speaker.push(notes);
  speaker.push("");
}

function addHeader(slide, title, section, page) {
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.38,
    fill: { color: C.redis },
    line: { color: C.redis },
  });
  slide.addText(section, { x: 0.6, y: 0.1, w: 4.4, h: 0.16, ...font(7.5, "FFFFFF", true) });
  slide.addText(title, { x: 0.65, y: 0.62, w: 11.3, h: 0.42, ...font(25, C.ink, true), fit: "shrink" });
  slide.addText(`Redis-RAG 垂直领域问答  |  ${page}/${TOTAL}`, {
    x: 0.65,
    y: 7.14,
    w: 5.8,
    h: 0.18,
    ...font(8.5, C.muted, false),
  });
}

function addCallout(slide, text, x, y, w, h, color = C.redis) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.04,
    fill: { color },
    line: { color },
  });
  slide.addText(text, {
    x: x + 0.2,
    y: y + 0.12,
    w: w - 0.4,
    h: h - 0.24,
    ...font(17, "FFFFFF", true),
    align: "center",
    valign: "mid",
    fit: "shrink",
  });
}

function addCard(slide, x, y, w, h, title, body, accent = C.redis, bodySize = 14.5) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.045,
    fill: { color: C.panel },
    line: { color: C.line, width: 1 },
    shadow: { type: "outer", color: "D7DEE8", opacity: 0.18, blur: 1, angle: 45, distance: 1 },
  });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.1, h, fill: { color: accent }, line: { color: accent } });
  slide.addText(title, { x: x + 0.26, y: y + 0.18, w: w - 0.42, h: 0.28, ...font(16, C.ink, true), fit: "shrink" });
  slide.addText(body, {
    x: x + 0.26,
    y: y + 0.62,
    w: w - 0.42,
    h: h - 0.78,
    ...font(bodySize, C.text, false),
    breakLine: false,
    fit: "shrink",
    valign: "top",
  });
}

function addBullets(slide, items, x, y, w, h, size = 16, color = C.text) {
  slide.addText(
    items.map((item) => ({
      text: item,
      options: { bullet: { indent: 14 }, hanging: 4, breakLine: false },
    })),
    {
      x,
      y,
      w,
      h,
      ...font(size, color, false),
      fit: "shrink",
      breakLine: false,
      valign: "top",
    }
  );
}

function addMetricBar(slide, label, value, x, y, w, color) {
  slide.addText(label, { x, y: y - 0.03, w: 2.6, h: 0.25, ...font(14.5, C.ink, true) });
  slide.addShape(pptx.ShapeType.rect, { x: x + 2.8, y, w, h: 0.26, fill: { color: C.gray }, line: { color: C.gray } });
  slide.addShape(pptx.ShapeType.rect, { x: x + 2.8, y, w: w * value, h: 0.26, fill: { color }, line: { color } });
  slide.addText(value.toFixed(4), { x: x + 2.8 + w + 0.22, y: y - 0.04, w: 0.8, h: 0.24, ...font(13.5, C.ink, true) });
}

function addFlowBox(slide, text, x, y, w, h, fill, line = C.redis) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.035,
    fill: { color: fill },
    line: { color: line, width: 1.2 },
  });
  slide.addText(text, { x: x + 0.08, y: y + 0.1, w: w - 0.16, h: h - 0.2, ...font(13.5, C.ink, true), align: "center", valign: "mid", fit: "shrink" });
}

function addArrow(slide, x1, y1, x2, y2, color = C.redis) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1,
    y: y1,
    w: x2 - x1,
    h: y2 - y1,
    line: { color, width: 1.4, beginArrowType: "none", endArrowType: "triangle" },
  });
}

function addTableLike(slide, rows, x, y, w, h, headerFill = C.paleRed) {
  const rowH = h / rows.length;
  const colW = [w * 0.33, w * 0.67];
  rows.forEach((row, i) => {
    const fill = i === 0 ? headerFill : "FFFFFF";
    slide.addShape(pptx.ShapeType.rect, { x, y: y + i * rowH, w: colW[0], h: rowH, fill: { color: fill }, line: { color: C.line, width: 0.7 } });
    slide.addShape(pptx.ShapeType.rect, { x: x + colW[0], y: y + i * rowH, w: colW[1], h: rowH, fill: { color: fill }, line: { color: C.line, width: 0.7 } });
    slide.addText(row[0], { x: x + 0.12, y: y + i * rowH + 0.09, w: colW[0] - 0.2, h: rowH - 0.16, ...font(i === 0 ? 13 : 12.2, C.ink, i === 0), fit: "shrink", valign: "mid" });
    slide.addText(row[1], { x: x + colW[0] + 0.12, y: y + i * rowH + 0.09, w: colW[1] - 0.2, h: rowH - 0.16, ...font(i === 0 ? 13 : 12.2, C.text, i === 0), fit: "shrink", valign: "mid" });
  });
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: C.ink };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: C.redis }, line: { color: C.redis } });
  slide.addShape(pptx.ShapeType.rect, { x: 9.1, y: 0, w: 4.23, h: 7.5, fill: { color: C.redisDark, transparency: 10 }, line: { color: C.redisDark } });
  slide.addText("Redis-RAG", { x: 0.9, y: 1.18, w: 6.4, h: 0.62, ...font(42, "FFFFFF", true) });
  slide.addText("基于 RAG 的垂直领域深度问答系统构建", { x: 0.92, y: 2.08, w: 7.3, h: 0.42, ...font(22, "F8FAFC", false), fit: "shrink" });
  slide.addText("私有知识库 · 混合检索 · DeepSeek 生成 · 三维量化评估", { x: 0.95, y: 3.05, w: 7.1, h: 0.34, ...font(17, "DDE7F3", true), fit: "shrink" });
  slide.addText("课程作业完整交付：代码仓库 / README / requirements / infer.py / 报告 / PPT / 逐页讲稿", { x: 0.95, y: 3.68, w: 7.9, h: 0.36, ...font(14.5, "CBD5E1", false), fit: "shrink" });
  slide.addShape(pptx.ShapeType.roundRect, { x: 9.85, y: 1.55, w: 2.35, h: 2.35, rectRadius: 0.08, fill: { color: C.redis }, line: { color: C.redis } });
  slide.addText("RAG", { x: 10.15, y: 2.1, w: 1.72, h: 0.42, ...font(31, "FFFFFF", true), align: "center" });
  slide.addText("Redis Docs\nQA System", { x: 10.18, y: 2.82, w: 1.66, h: 0.52, ...font(13, "FFFFFF", true), align: "center", fit: "shrink" });
  slide.addImage({ path: asset("hero_redis_rag.png"), x: 8.75, y: 4.15, w: 4.1, h: 2.3 });
  slide.addText("2026.06", { x: 0.95, y: 6.78, w: 1.6, h: 0.18, ...font(9.5, "CBD5E1", false) });
  addNotes(slide, 1, "封面", [
    "Redis-RAG：基于 RAG 的 Redis 垂直领域深度问答系统",
    "关键词：私有知识库、混合检索、DeepSeek 生成、三维量化评估",
    "交付物：代码仓库、README、依赖文件、一键推理、报告、PPT、讲稿",
  ], "这一页是汇报封面。我的作业选题是 Redis 垂直领域问答系统。核心思路是把 Redis 官方文档和清洗后的技术语料构造成私有知识库，然后通过 RAG 的方式进行检索增强生成。系统不仅包含一键推理脚本，也包含索引构建、量化评估、报告和 PPT。后面我会按照数据、检索、生成、评估和案例分析的顺序展开。");
}

// Slide 2
{
  const slide = pptx.addSlide();
  addHeader(slide, "作业要求与本项目交付", "01 任务映射", 2);
  addCallout(slide, "目标：不是只演示概念，而是交付可运行、可解释、可评估的 RAG 仓库", 0.75, 1.25, 11.85, 0.62, C.redis);
  addCard(slide, 0.75, 2.25, 3.65, 2.05, "代码仓库", "README.md\nrequirements.txt\ninfer.py 一键推理\nbuild_index.py / evaluate.py", C.redis, 14.5);
  addCard(slide, 4.85, 2.25, 3.65, 2.05, "RAG 核心", "Redis 私有知识库\nChunking + Embedding\n本地向量库\nQuery Rewriting + Hybrid Retrieval", C.teal, 14.5);
  addCard(slide, 8.95, 2.25, 3.65, 2.05, "展示材料", "论文式报告 MD/PDF\n15 页汇报 PPT\nPPT speaker notes\n逐页讲稿 Markdown", C.amber, 14.5);
  addBullets(slide, [
    "知识库、检索、生成、评估四个环节均可单独运行和检查",
    "无 API key 时可复现；配置 DeepSeek 后可调用 deepseek-v4-pro",
    "评估输出保存为 JSON 和 CSV，方便报告引用"
  ], 1.05, 5.05, 11.1, 0.95, 15.5);
  addNotes(slide, 2, "作业要求与本项目交付", [
    "本项目交付完整代码仓库",
    "核心 RAG 模块包括知识库、Chunking、Embedding、向量库、混合检索和生成",
    "展示材料包括报告、PPT 和逐页讲稿",
  ], "这一页说明作业要求和项目交付之间的对应关系。代码仓库里有 README、requirements 和 infer.py，满足一键运行要求。RAG 核心部分包括 Redis 私有知识库、文档分块、embedding、本地向量库、Query Rewriting 和混合检索。展示材料方面，我补充了论文式报告、PDF、15页PPT和逐页讲稿，所以这个项目既可以运行，也可以完整展示。");
}

// Slide 3
{
  const slide = pptx.addSlide();
  addHeader(slide, "为什么选 Redis 作为垂直领域", "02 选题动机", 3);
  addCard(slide, 0.8, 1.35, 3.75, 2.0, "边界清晰", "Redis 文档围绕数据结构、命令、持久化、高可用、集群和缓存工程展开，知识范围明确，适合构建私有知识库。", C.redis, 14.2);
  addCard(slide, 4.8, 1.35, 3.75, 2.0, "术语密集", "AOF、RDB、TTL、XREADGROUP、WATCH、EXEC 等精确术语决定答案质量，适合展示检索策略差异。", C.teal, 14.2);
  addCard(slide, 8.8, 1.35, 3.75, 2.0, "可追溯", "Redis 官方文档页面稳定，每条知识记录保留 URL，答案可带来源引用，便于分析 Faithfulness。", C.amber, 14.2);
  slide.addText("技术文档 RAG 的三个难点", { x: 0.85, y: 4.08, w: 4.1, h: 0.3, ...font(18, C.ink, true) });
  addBullets(slide, [
    "中文问题与英文官方术语存在表达差异",
    "相似概念容易误召回，例如 Pub/Sub 与 Stream、RDB 与 AOF",
    "答案必须忠实于上下文，不能凭模型记忆补充未检索到的内容"
  ], 1.05, 4.65, 10.8, 1.1, 16);
  addNotes(slide, 3, "为什么选 Redis 作为垂直领域", [
    "Redis 知识边界清晰",
    "Redis 问答包含大量命令名和缩写",
    "官方文档可追溯，适合做引用和忠实度评估",
    "技术文档 RAG 的难点包括术语匹配、概念混淆和答案忠实度",
  ], "我选择 Redis 是因为它很适合作为垂直领域。第一，Redis 的知识边界清楚，主题从数据结构到持久化和集群都很明确。第二，Redis 问答里有很多精确术语，比如 AOF、RDB、TTL 和 WATCH，这些词非常考验检索系统。第三，官方文档有稳定 URL，可以作为答案引用来源。这个选题能很好地展示 RAG 的核心价值：把答案约束到可追溯的文档上下文中。");
}

// Slide 4
{
  const slide = pptx.addSlide();
  addHeader(slide, "私有知识库构建流程", "03 数据构建", 4);
  addFlowBox(slide, "Redis 官方文档", 0.8, 1.35, 1.95, 0.72, "FFFFFF");
  addArrow(slide, 2.85, 1.71, 3.25, 1.71);
  addFlowBox(slide, "页面抓取", 3.25, 1.35, 1.55, 0.72, C.paleRed);
  addArrow(slide, 4.9, 1.71, 5.3, 1.71);
  addFlowBox(slide, "清洗正文", 5.3, 1.35, 1.55, 0.72, C.paleBlue, C.blue);
  addArrow(slide, 6.95, 1.71, 7.35, 1.71);
  addFlowBox(slide, "JSONL 语料", 7.35, 1.35, 1.7, 0.72, C.paleGreen, C.teal);
  addArrow(slide, 9.15, 1.71, 9.55, 1.71);
  addFlowBox(slide, "索引构建", 9.55, 1.35, 1.55, 0.72, C.paleRed);
  addArrow(slide, 11.2, 1.71, 11.6, 1.71);
  addFlowBox(slide, "问答系统", 11.6, 1.35, 1.25, 0.72, "FFFFFF");
  addCard(slide, 0.85, 2.85, 5.65, 2.2, "文档字段", "doc_id：评估和引用使用\ntitle：展示标题\nurl：官方来源追溯\ntext：清洗后的正文内容", C.redis, 15);
  addCard(slide, 6.9, 2.85, 5.65, 2.2, "覆盖主题", "数据结构、TTL、内存淘汰、RDB/AOF、Replication、Sentinel、Cluster、事务、Lua、Pub/Sub、缓存风险", C.teal, 15);
  slide.addText("关键取舍：内置语料保证离线可复现，采集脚本体现真实私有知识库构建流程。", { x: 0.9, y: 5.75, w: 11.4, h: 0.32, ...font(16.5, C.ink, true), fit: "shrink" });
  addNotes(slide, 4, "私有知识库构建流程", [
    "流程：官方文档、页面抓取、正文清洗、JSONL 语料、索引构建、问答系统",
    "每条文档包含 doc_id、title、url、text",
    "知识主题覆盖 Redis 数据结构、TTL、持久化、高可用、集群和缓存风险",
  ], "这一页展示私有知识库构建流程。数据可以来自 Redis 官方文档，经过页面抓取和正文清洗后，保存为 JSONL。每条记录都包含 doc_id、title、url 和 text。doc_id 用于评估，url 用于追溯来源。为了保证作业能稳定运行，我保留了一份内置清洗语料，同时也提供脚本重新抓取官方文档。");
}

// Slide 5
{
  const slide = pptx.addSlide();
  addHeader(slide, "知识库主题覆盖", "03 数据构建", 5);
  const topics = [
    ["基础数据结构", "String / Hash / List / Stream / Sorted Set"],
    ["生命周期", "EXPIRE / TTL / PERSIST / 惰性删除 / 周期删除"],
    ["可靠性", "RDB / AOF / appendfsync / 备份恢复"],
    ["高可用与扩展", "Replication / Sentinel / Cluster / hash slot"],
    ["编程与消息", "MULTI / EXEC / WATCH / Lua / Pub/Sub / Stream"],
    ["缓存工程", "缓存穿透 / 缓存击穿 / 缓存雪崩 / 随机 TTL"],
  ];
  topics.forEach((t, i) => {
    const x = 0.85 + (i % 2) * 6.05;
    const y = 1.3 + Math.floor(i / 2) * 1.55;
    addCard(slide, x, y, 5.45, 1.16, t[0], t[1], i % 2 === 0 ? C.redis : C.teal, 14.2);
  });
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.95, y: 6.1, w: 11.4, h: 0.52, rectRadius: 0.04, fill: { color: C.paleRed }, line: { color: "F8C5BD" } });
  slide.addText("覆盖原则：问题要能从知识库中找到依据，答案要能回溯到文档，而不是依赖模型记忆。", { x: 1.2, y: 6.25, w: 10.9, h: 0.2, ...font(14.8, C.redisDark, true), fit: "shrink" });
  addImagePanel(slide, "knowledge_base_overview.png", 0.72, 1.16, 11.95, 5.82, C.line);
  addNotes(slide, 5, "知识库主题覆盖", [
    "基础数据结构：String、Hash、List、Stream、Sorted Set",
    "生命周期：EXPIRE、TTL、PERSIST",
    "可靠性：RDB、AOF、appendfsync",
    "高可用与扩展：Replication、Sentinel、Cluster",
    "编程与消息：事务、Lua、Pub/Sub、Stream",
    "缓存工程：缓存穿透、击穿和雪崩",
  ], "这一页说明知识库覆盖面。Redis 不是只收集几个命令，而是覆盖了数据结构、生命周期、可靠性、高可用、编程能力和缓存工程。这样设计的好处是评估问题可以比较全面，比如既能问 AOF 和 RDB，也能问 Stream 和 Pub/Sub，或者问缓存击穿怎么缓解。覆盖原则是每个问题都应该能从知识库中找到依据。");
}

// Slide 6
{
  const slide = pptx.addSlide();
  addHeader(slide, "Chunking：让检索单元既可命中又可阅读", "04 文档处理", 6);
  addCard(slide, 0.85, 1.25, 3.75, 2.0, "Redis-aware tokenizer", "保留 AOF、RDB、TTL、EXPIRE、XREADGROUP、WATCH 等命令名和缩写，也识别“持久化”“消费者组”等中文领域词。", C.redis, 14.2);
  addCard(slide, 4.85, 1.25, 3.75, 2.0, "重叠分块", "默认 chunk_size=320，overlap=40。长文档切分后相邻 chunk 保留上下文连接，避免答案依据被切断。", C.teal, 14.2);
  addCard(slide, 8.85, 1.25, 3.75, 2.0, "可解释元数据", "每个 chunk 保存 chunk_id、doc_id、source_title、url、start_token、end_token，便于引用和调试。", C.amber, 14.2);
  slide.addText("示例：AOF/RDB 问题的关键 token", { x: 0.9, y: 4.1, w: 4.2, h: 0.26, ...font(17, C.ink, true) });
  addCallout(slide, "持久化", 0.95, 4.65, 1.25, 0.5, C.redis);
  addCallout(slide, "persistence", 2.35, 4.65, 1.55, 0.5, C.teal);
  addCallout(slide, "RDB", 4.05, 4.65, 1.0, 0.5, C.redis);
  addCallout(slide, "AOF", 5.2, 4.65, 1.0, 0.5, C.redis);
  addCallout(slide, "snapshot", 6.35, 4.65, 1.4, 0.5, C.blue);
  addCallout(slide, "append only file", 7.9, 4.65, 2.1, 0.5, C.teal);
  slide.addText("如果这些 token 被切掉或弱化，检索会更容易偏到其他包含“持久化”字样的文档。", { x: 1.0, y: 5.65, w: 10.9, h: 0.26, ...font(15.5, C.text, false), fit: "shrink" });
  addNotes(slide, 6, "Chunking：让检索单元既可命中又可阅读", [
    "Redis-aware tokenizer 保留命令名、缩写和中文领域词",
    "默认 chunk_size=320，overlap=40",
    "每个 chunk 保留来源元数据",
    "AOF/RDB 问题需要保留持久化、persistence、RDB、AOF、snapshot 等关键 token",
  ], "这一页解释 Chunking。技术文档分块不能只按普通句子切，因为 Redis 命令名非常关键。我实现了 Redis-aware tokenizer，保留命令名、缩写和中文领域词。默认分块大小是 320，重叠是 40。这样长文档可以切成可检索片段，同时相邻片段之间不会完全断开。每个 chunk 都有来源元数据，所以最后答案可以回到原文档。");
}

// Slide 7
{
  const slide = pptx.addSlide();
  addHeader(slide, "Embedding 与本地向量数据库", "05 向量索引", 7);
  addCard(slide, 0.85, 1.35, 3.85, 2.25, "默认选择", "HashingEmbeddingModel\n维度：256\n优点：无需下载模型、无需 GPU、结果稳定、适合作业复现。", C.redis, 14.4);
  addCard(slide, 4.95, 1.35, 3.85, 2.25, "向量库设计", "LocalVectorStore\n保存 chunk + vector\n文件：data/index/vectors.jsonl\n结构透明，方便检查。", C.teal, 14.4);
  addCard(slide, 9.05, 1.35, 3.15, 2.25, "可升级方向", "BGE\nE5\nSentenceTransformer\nFAISS / Chroma", C.amber, 14.4);
  slide.addShape(pptx.ShapeType.roundRect, { x: 1.0, y: 4.35, w: 11.3, h: 1.35, rectRadius: 0.04, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText('"chunk": { "doc_id": "redis:persistence", "title": "...", "text": "..." }\n"vector": [0.0, 0.12, -0.04, ...]', { x: 1.3, y: 4.72, w: 10.7, h: 0.55, ...font(13, C.ink, false), fontFace: "Courier New", fit: "shrink" });
  slide.addText("课程取舍：默认方案重在可复现和可解释；真实部署时可替换为神经 embedding + 专业向量库。", { x: 1.0, y: 6.12, w: 11.1, h: 0.26, ...font(15.5, C.ink, true), fit: "shrink" });
  addNotes(slide, 7, "Embedding 与本地向量数据库", [
    "默认使用 HashingEmbeddingModel，维度 256",
    "向量库保存 chunk 和 vector，文件是 data/index/vectors.jsonl",
    "优点是可复现、无需下载模型、便于解释",
    "后续可升级为 BGE、E5、SentenceTransformer、FAISS 或 Chroma",
  ], "这一页说明 embedding 和向量库。为了保证作业在没有 GPU、没有外部模型下载的环境中也能跑，我默认使用 hashing embedding。它不如 BGE 这类模型强，但非常适合课程复现。向量库用 JSONL 保存，每条记录包含 chunk 和 vector，结构完全透明。后续如果要做真实系统，可以把这一层替换成 BGE embedding 和 FAISS 或 Chroma。");
}

// Slide 8
{
  const slide = pptx.addSlide();
  addHeader(slide, "Query Rewriting：连接中文问题与英文术语", "06 高级 RAG 优化", 8);
  addTableLike(slide, [
    ["用户表达", "扩展后的检索术语"],
    ["持久化", "persistence, RDB, AOF, snapshot, append only file, durability"],
    ["高可用", "replication, sentinel, failover, cluster"],
    ["过期", "expire, TTL, timeout, key expiration"],
    ["队列", "list, stream, consumer group, XREADGROUP"],
    ["Lua", "eval, script, scripting, atomic"],
  ], 0.9, 1.25, 11.55, 3.85, C.paleRed);
  addCallout(slide, "作用：提升召回率，减少“中文提问找不到英文文档术语”的问题", 1.05, 5.65, 11.2, 0.62, C.teal);
  addNotes(slide, 8, "Query Rewriting：连接中文问题与英文术语", [
    "持久化扩展为 persistence、RDB、AOF、snapshot",
    "高可用扩展为 replication、sentinel、failover、cluster",
    "过期扩展为 expire、TTL、timeout",
    "队列扩展为 list、stream、consumer group、XREADGROUP",
    "Query Rewriting 主要提升召回率",
  ], "这一页是高级 RAG 优化的第一部分：Query Rewriting。Redis 官方文档很多术语是英文，但用户可能用中文问，比如“持久化”“高可用”“过期”。如果不扩展，检索可能找不到相关英文术语。所以我维护了一个领域词表，把中文问题扩展成 Redis 常用英文概念。这个策略主要提升召回率。");
}

// Slide 9
{
  const slide = pptx.addSlide();
  addHeader(slide, "Hybrid Retrieval：BM25 与向量检索互补", "06 高级 RAG 优化", 9);
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.9, y: 1.2, w: 5.4, h: 1.0, rectRadius: 0.04, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("score = 0.45 × vector + 0.55 × BM25", { x: 1.15, y: 1.54, w: 4.9, h: 0.26, ...font(16, C.ink, true), fontFace: "Courier New", fit: "shrink" });
  addCard(slide, 0.9, 2.7, 3.65, 2.05, "向量检索", "擅长语义相似：例如“高可用”与“failover”之间不完全字面匹配，但语义相关。", C.blue, 14.3);
  addCard(slide, 4.85, 2.7, 3.65, 2.05, "BM25", "擅长精确匹配：AOF、RDB、TTL、WATCH 等命令名必须被强命中。", C.redis, 14.3);
  addCard(slide, 8.8, 2.7, 3.65, 2.05, "融合排序", "先归一化两个分数，再线性加权。Redis 场景中 BM25 权重略高。", C.teal, 14.3);
  slide.addText("核心判断：Redis 问答不是纯语义任务，而是“语义理解 + 精确术语命中”的组合任务。", { x: 0.95, y: 5.7, w: 11.4, h: 0.3, ...font(16.5, C.ink, true), fit: "shrink" });
  addNotes(slide, 9, "Hybrid Retrieval：BM25 与向量检索互补", [
    "融合公式：score = 0.45 × vector + 0.55 × BM25",
    "向量检索擅长语义相似",
    "BM25 擅长 AOF、RDB、TTL、WATCH 等精确术语",
    "Redis 问答需要语义理解和精确术语命中结合",
  ], "这一页解释混合检索。向量检索能处理语义相似，但是对命令名未必足够敏感。BM25 对精确词非常有效，但不能很好处理同义表达。所以我把二者融合。公式里向量权重是 0.45，BM25 权重是 0.55，因为 Redis 问答中命令名非常关键。这个策略比单纯向量检索更适合 Redis 技术文档。");
}

// Slide 10
{
  const slide = pptx.addSlide();
  addHeader(slide, "端到端系统架构", "07 系统流程", 10);
  addFlowBox(slide, "文档\nJSONL", 0.55, 1.35, 1.35, 0.78, "FFFFFF");
  addArrow(slide, 1.95, 1.74, 2.3, 1.74);
  addFlowBox(slide, "Chunking", 2.3, 1.35, 1.45, 0.78, C.paleRed);
  addArrow(slide, 3.8, 1.74, 4.15, 1.28);
  addArrow(slide, 3.8, 1.74, 4.15, 2.18);
  addFlowBox(slide, "Embedding", 4.15, 0.88, 1.45, 0.72, C.paleBlue, C.blue);
  addFlowBox(slide, "BM25", 4.15, 1.8, 1.45, 0.72, C.paleGreen, C.teal);
  addArrow(slide, 5.65, 1.24, 6.2, 1.62);
  addArrow(slide, 5.65, 2.16, 6.2, 1.9);
  addFlowBox(slide, "Hybrid\nRetriever", 6.2, 1.35, 1.65, 0.78, "FFFFFF");
  addArrow(slide, 7.9, 1.74, 8.25, 1.74);
  addFlowBox(slide, "Top-k\nContexts", 8.25, 1.35, 1.45, 0.78, C.paleRed);
  addArrow(slide, 9.75, 1.74, 10.1, 1.74);
  addFlowBox(slide, "DeepSeek /\nFallback", 10.1, 1.35, 1.65, 0.78, C.paleBlue, C.blue);
  addArrow(slide, 11.8, 1.74, 12.15, 1.74);
  addFlowBox(slide, "带引用\n答案", 12.15, 1.35, 0.9, 0.78, "FFFFFF");
  addCard(slide, 0.85, 3.45, 3.7, 1.55, "可观测", "输出 retrieved_contexts，展示 doc_id、title、combined_score、vector_score 和 bm25_score。", C.redis, 13.8);
  addCard(slide, 4.85, 3.45, 3.7, 1.55, "可替换", "Embedding、向量库、生成模型都以模块封装，后续可替换为 BGE、FAISS、reranker。", C.teal, 13.8);
  addCard(slide, 8.85, 3.45, 3.7, 1.55, "可复现", "无 API key 自动回退抽取式生成，保证老师本地也能运行完整流程。", C.amber, 13.8);
  addImagePanel(slide, "architecture_flow.png", 0.62, 1.14, 12.08, 5.58, C.line);
  addNotes(slide, 10, "端到端系统架构", [
    "文档 JSONL 经过 Chunking 后进入 Embedding 和 BM25",
    "用户问题经过 Query Rewriting 后进入 Hybrid Retriever",
    "Top-k 上下文传入 DeepSeek 或抽取式生成器",
    "输出带引用答案和检索分数",
  ], "这一页展示端到端架构。左边是文档处理和索引构建，文档先变成 chunk，再进入 embedding 和 BM25。右边是在线问答流程，用户问题先经过 Query Rewriting，然后由 Hybrid Retriever 找到 Top-k 上下文，最后传给 DeepSeek 或抽取式生成器。系统还会输出检索分数，便于分析为什么选中某个文档。");
}

// Slide 11
{
  const slide = pptx.addSlide();
  addHeader(slide, "生成模块：DeepSeek 优先，离线可回退", "08 生成策略", 11);
  addCard(slide, 0.85, 1.25, 3.75, 2.0, "DeepSeek 模式", "设置 DEEPSEEK_API_KEY 后，默认模型为 deepseek-v4-pro。提示词要求只基于检索上下文回答。", C.redis, 14.2);
  addCard(slide, 4.85, 1.25, 3.75, 2.0, "抽取式回退", "没有 API key 时，从 Top-k 片段中抽取与问题最相关的句子，保证结果可复现。", C.teal, 14.2);
  addCard(slide, 8.85, 1.25, 3.75, 2.0, "防幻觉机制", "如果上下文不足，要求模型说明无法确认；答案必须带 [1] 形式来源引用。", C.amber, 14.2);
  slide.addShape(pptx.ShapeType.roundRect, { x: 1.0, y: 4.15, w: 11.2, h: 1.35, rectRadius: 0.04, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("export DEEPSEEK_API_KEY=\"...\"\nexport OPENAI_MODEL=\"deepseek-v4-pro\"\npython3 infer.py --question \"Redis Sentinel 主要解决什么问题？\"", { x: 1.3, y: 4.48, w: 10.5, h: 0.62, ...font(13, C.ink, false), fontFace: "Courier New", fit: "shrink" });
  slide.addText("API key 不写入仓库；README 只说明环境变量用法。", { x: 1.0, y: 5.95, w: 10.7, h: 0.25, ...font(15.5, C.redisDark, true), fit: "shrink" });
  addNotes(slide, 11, "生成模块：DeepSeek 优先，离线可回退", [
    "设置 DEEPSEEK_API_KEY 后默认使用 deepseek-v4-pro",
    "没有 API key 时使用抽取式生成器",
    "提示词要求只能基于上下文回答，并带来源引用",
    "API key 不写入仓库",
  ], "这一页说明生成模块。项目支持 DeepSeek，只要设置 DEEPSEEK_API_KEY，默认模型就是 deepseek-v4-pro。同时我保留了抽取式回退，保证没有 API key 也能运行。为了降低幻觉，系统提示要求模型只能依据检索上下文回答，并带引用。如果上下文不足，就要说明无法确认。这里也强调，API key 不会写入仓库，只通过环境变量传入。");
}

// Slide 12
{
  const slide = pptx.addSlide();
  addHeader(slide, "量化评估：三个维度衡量 RAG 能力", "09 评估方案", 12);
  addCard(slide, 0.8, 1.35, 3.75, 2.2, "Context Relevance", "检索结果是否覆盖标注相关文档。\n\n|retrieved ∩ gold| / |gold|", C.redis, 14.2);
  addCard(slide, 4.8, 1.35, 3.75, 2.2, "Faithfulness", "答案内容是否被检索上下文支持。\n\nsupported_answer_tokens / answer_tokens", C.teal, 14.2);
  addCard(slide, 8.8, 1.35, 3.75, 2.2, "Answer Relevance", "答案是否覆盖问题所需关键词。\n\ncovered_keywords / expected_keywords", C.amber, 14.2);
  addCard(slide, 0.9, 4.35, 11.55, 1.3, "评估集", "10 条 Redis 技术问题，覆盖持久化、过期、Stream/PubSub、Sorted Set、Sentinel、Cluster、事务、Lua、内存淘汰和缓存风险。输出保存为 outputs/eval_results.json 与 outputs/eval_results.csv。", C.blue, 14.2);
  addNotes(slide, 12, "量化评估：三个维度衡量 RAG 能力", [
    "Context Relevance 衡量检索上下文是否相关",
    "Faithfulness 衡量答案是否忠实于上下文",
    "Answer Relevance 衡量答案是否回答问题",
    "评估集包含 10 条 Redis 技术问题",
  ], "这一页介绍评估方案。Context Relevance 主要评价检索是否找到了相关文档。Faithfulness 评价答案是否被上下文支持，也就是是否有幻觉风险。Answer Relevance 评价答案是否覆盖问题的关键点。评估集包含 10 条 Redis 技术问题，输出结果会保存成 JSON 和 CSV，方便报告引用。");
}

// Slide 13
{
  const slide = pptx.addSlide();
  addHeader(slide, "实验结果与解释", "09 评估方案", 13);
  addMetricBar(slide, "Context Relevance", 1.0, 0.9, 1.55, 6.0, C.redis);
  addMetricBar(slide, "Faithfulness", 0.8116, 0.9, 2.75, 6.0, C.teal);
  addMetricBar(slide, "Answer Relevance", 0.875, 0.9, 3.95, 6.0, C.amber);
  addCard(slide, 8.95, 1.25, 3.45, 1.35, "检索表现", "相关文档覆盖率达到 1.0000，说明混合检索能稳定召回正确文档。", C.redis, 13.5);
  addCard(slide, 8.95, 2.95, 3.45, 1.35, "生成表现", "Faithfulness 为 0.8116，答案多数内容可由上下文支持。", C.teal, 13.5);
  addCard(slide, 8.95, 4.65, 3.45, 1.35, "剩余问题", "部分关键词未完全覆盖，主要来自抽取式答案表达不够自然。", C.amber, 13.5);
  addImagePanel(slide, "evaluation_results.png", 0.55, 1.12, 7.8, 5.45, C.line);
  addNotes(slide, 13, "实验结果与解释", [
    "Context Relevance = 1.0000",
    "Faithfulness = 0.8116",
    "Answer Relevance = 0.8750",
    "检索效果较稳，答案忠实度较好，部分关键词覆盖仍可提升",
  ], "这一页展示实验结果。Context Relevance 是 1.0000，说明在当前评估集里，检索能覆盖相关文档。Faithfulness 是 0.8116，说明答案大多数内容都能被上下文支持。Answer Relevance 是 0.8750，说明答案基本覆盖问题要点，但还有提升空间。主要问题是抽取式生成有时表达比较硬，可能没有覆盖所有期望关键词。");
}

// Slide 14
{
  const slide = pptx.addSlide();
  addHeader(slide, "案例分析：AOF 与 RDB 持久化问答", "10 案例与反思", 14);
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.85, y: 1.25, w: 11.65, h: 0.65, rectRadius: 0.04, fill: { color: C.paleRed }, line: { color: "F8C5BD" } });
  slide.addText("问题：Redis 的 AOF 和 RDB 持久化有什么区别？", { x: 1.15, y: 1.45, w: 10.9, h: 0.22, ...font(16, C.redisDark, true), fit: "shrink" });
  addCard(slide, 0.9, 2.35, 3.65, 2.2, "命中文档", "redis:persistence\nRedis persistence with RDB and AOF\ncombined_score = 1.0000", C.redis, 14);
  addCard(slide, 4.85, 2.35, 3.65, 2.2, "答案要点", "RDB 是快照，文件紧凑，适合备份和快速恢复；AOF 是追加日志，记录写命令，数据安全性更好。", C.teal, 14);
  addCard(slide, 8.8, 2.35, 3.65, 2.2, "为什么能命中", "Query Rewriting 扩展 persistence、snapshot、append only file；BM25 强命中 AOF/RDB。", C.amber, 14);
  slide.addText("这个案例体现：Redis 问答需要同时处理中文表达、英文术语和精确命令名。", { x: 0.95, y: 5.45, w: 11.2, h: 0.28, ...font(16.2, C.ink, true), fit: "shrink" });
  addImagePanel(slide, "inference_result.png", 0.72, 2.08, 12.0, 4.78, C.line);
  addNotes(slide, 14, "案例分析：AOF 与 RDB 持久化问答", [
    "问题是 Redis 的 AOF 和 RDB 持久化有什么区别",
    "系统命中文档 redis:persistence",
    "答案包含 RDB 快照、AOF 追加日志、备份恢复和数据安全性",
    "命中原因是 Query Rewriting 和 BM25 精确术语匹配",
  ], "这一页用 AOF 和 RDB 问题做案例。系统最终命中了 redis:persistence 文档，combined_score 是 1.0000。答案能解释 RDB 是快照，适合备份和快速恢复；AOF 是追加日志，通常数据安全性更好。这个案例能说明 Query Rewriting 和 BM25 的价值：中文问题会扩展到 persistence、snapshot 和 append only file，同时 AOF 和 RDB 被精确命中。");
}

// Slide 15
{
  const slide = pptx.addSlide();
  addHeader(slide, "Bad Case、改进方向与总结", "11 总结", 15);
  addCard(slide, 0.75, 1.25, 3.75, 2.0, "Bad Case", "AOF/RDB 问题早期会召回 Pub/Sub，因为 Pub/Sub 文档中也出现“不会持久化”。说明共现词会造成弱相关上下文污染。", C.redis, 13.5);
  addCard(slide, 4.8, 1.25, 3.75, 2.0, "已做改进", "加入 Query Rewriting、BM25/Vector 融合，以及生成阶段上下文分数过滤，减少弱相关片段进入答案。", C.teal, 13.5);
  addCard(slide, 8.85, 1.25, 3.75, 2.0, "后续优化", "替换 BGE embedding；加入 reranker；扩展评估集；增加 LLM 生成后的 citation checking。", C.amber, 13.5);
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.9, y: 4.05, w: 11.55, h: 1.35, rectRadius: 0.04, fill: { color: "FFFFFF" }, line: { color: C.line } });
  slide.addText("复现实验命令", { x: 1.2, y: 4.35, w: 2.2, h: 0.25, ...font(15, C.redisDark, true) });
  slide.addText("python3 infer.py --question \"Redis 的 AOF 和 RDB 持久化有什么区别？\"\npython3 evaluate.py --rebuild", { x: 1.2, y: 4.82, w: 9.8, h: 0.48, ...font(12.5, C.ink, false), fontFace: "Courier New", fit: "shrink" });
  addImagePanel(slide, "retrieval_scores.png", 0.74, 3.56, 11.9, 2.65, C.line);
  slide.addText("总结：本项目完成了 Redis 私有知识库、检索增强生成、DeepSeek 接入、三维评估和完整展示材料。", { x: 0.95, y: 6.32, w: 11.5, h: 0.3, ...font(15.2, C.ink, true), fit: "shrink" });
  addNotes(slide, 15, "Bad Case、改进方向与总结", [
    "Bad Case：AOF/RDB 问题早期召回 Pub/Sub 弱相关文档",
    "已做改进：Query Rewriting、混合检索、上下文过滤",
    "后续优化：BGE embedding、reranker、更大评估集、citation checking",
    "复现实验命令：infer.py 和 evaluate.py",
  ], "最后一页总结问题和改进。一个典型 bad case 是 AOF/RDB 问题早期会召回 Pub/Sub，因为它也出现了持久化相关词。为了解决这个问题，我加入了 Query Rewriting、混合检索和生成阶段上下文过滤。后续可以进一步替换 BGE embedding、增加 reranker、扩大评估集，并对 LLM 输出做引用一致性检查。总体来说，这个项目完成了从知识库到检索、生成、评估和展示的完整闭环。");
}

async function main() {
  fs.mkdirSync(path.dirname(OUT_PPTX), { recursive: true });
  await pptx.writeFile({ fileName: OUT_PPTX });
  fs.writeFileSync(OUT_SCRIPT, speaker.join("\n"), "utf-8");
  console.log(OUT_PPTX);
  console.log(OUT_SCRIPT);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
