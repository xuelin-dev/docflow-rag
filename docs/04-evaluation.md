# P1 DocFlow RAG — 评估方案

> **文档版本：** 1.0
> **日期：** 2026-03-23
> **作者：** Dojo

---

## 1. 评估目标

### 要证明什么

P1 的评估体系需要回答三个核心问题：

1. **Agentic RAG 比 Pipeline RAG 好多少？** — 量化 self-correction 带来的检索质量提升
2. **每个工程决策的 ROI 是什么？** — 混合检索 vs 纯向量、有 reranker vs 无 reranker、分层 chunking vs 固定 chunking
3. **每个评估维度有什么数据？** — 每个维度都要有可引用的具体数字

### 评估原则

- 所有实验可复现：配置参数版本化，数据集固定
- 对比公平：每次只变一个变量，其他条件不变
- 数据真实：用公开 benchmark + 自建数据集，不用人造简单 case
- 结果可视化：Arize Phoenix 追踪 + 自建 Dashboard

---

## 2. 公开 Benchmark 数据集

### 2.1 BEIR（Benchmarking Information Retrieval）

BEIR 是信息检索领域的 de facto 标准 benchmark，包含 18 个子数据集，覆盖 9 类检索任务。

**为什么用 BEIR：**
- 零样本评估（zero-shot），不允许在目标数据集上微调，测试泛化能力
- 学术界和工业界广泛采用，结果有公信力
- 主要指标：nDCG@10、Recall@K、MAP

**选用子数据集（4 个，平衡覆盖面和工作量）：**

**NQ（Natural Questions）**
- 来源：Google 搜索真实问题 + Wikipedia 答案段落
- 数据量：约 3,452 queries / 2.68M passages
- 为什么选：最接近 P1 的"文档问答"场景，query 是真实用户搜索问题
- 适用场景：测试基础检索质量

**HotpotQA**
- 来源：多跳推理问答，需要跨多个 Wikipedia 段落综合答案
- 数据量：约 7,405 queries / 5.23M passages
- 为什么选：P1 的 query 分解 + 复杂路由就是为了解决多跳问题，这个数据集直接验证核心卖点
- 适用场景：测试 Agentic RAG 的 query 分解和多文档综合能力

**TREC-COVID**
- 来源：COVID-19 学术文献检索
- 数据量：约 50 queries / 171K passages
- 为什么选：垂直领域专业文档检索，测试 P1 在技术文档场景下的表现
- 适用场景：测试专业文档检索的精度

**FiQA（Financial Opinion Mining and Question Answering）**
- 来源：金融领域问答
- 数据量：约 648 queries / 57K passages
- 为什么选：短文本 + 专业术语密集，考验 embedding 模型和 chunking 策略的鲁棒性
- 适用场景：测试领域迁移能力

### 2.2 RAGAS Benchmark

RAGAS 是 RAG 评估的 de facto 标准框架，P1 使用 RAGAS 的指标体系而非其数据集。

**核心 RAGAS 指标（详见第 4 节）：**
- Context Precision — 检索的信噪比
- Context Recall — 检索的完整性
- Faithfulness — 答案是否忠于检索内容
- Answer Relevancy — 答案是否切题

**为什么选 RAGAS 指标而非自建指标：**
- 行业标准，广泛认可
- Reference-free 评估（除 Context Recall 外不需要人工标注 ground truth）
- 成本可控：GPT-4o-mini 做 judge，约 $0.001-0.003/样本
- 与 DSPy、LangChain 生态集成良好

### 2.3 RGB（Retrieval-augmented Generation Benchmark）

RGB 是评估 RAG 系统鲁棒性的 benchmark，由清华等团队提出（arXiv 2309.01431）。

**四个核心能力维度：**
- **Noise Robustness** — 检索结果含噪声（不相关文档）时，LLM 能否正确提取信息
- **Negative Rejection** — 检索结果完全不相关时，LLM 能否拒绝回答而非编造
- **Information Integration** — 答案需要跨多个文档综合时，LLM 的推理能力
- **Counterfactual Robustness** — 检索结果含错误信息时，LLM 能否识别并抵抗

**为什么用 RGB：**
- P1 的 self-correction 机制直接对标 Noise Robustness（检索到不相关文档 → 评分 → 改写 → 重检索）
- Negative Rejection 验证 P1 的 fallback 机制（检索失败时明确告知用户"找不到相关信息"）
- 数据量小（约 200 条/语言），评估成本低
- 覆盖中英文双语，匹配 P1 的 BGE-M3 多语言 embedding

**局限性：**
- 数据集规模小，结果方差可能较大
- 部分评估标签较粗糙
- 需要与 BEIR 结合使用，不能单独作为主 benchmark

---

## 3. 自建评估集

### 3.1 为什么需要自建

公开 benchmark 是通用领域的（Wikipedia、学术论文），P1 的核心场景是"技术团队内部文档问答"。需要构建贴近实际场景的评估集：

- 技术文档（API 文档、设计文档、README）
- 中英混合内容
- 代码相关问题（报错排查、API 用法）
- 多文档综合问题（跨多个文档的关联查询）

### 3.2 Synthetic QA Generation 流程

```
Step 1: 准备文档集
  └── 收集 10-15 份真实技术文档（开源项目 README、API docs、设计文档）
  └── 确保覆盖多种格式：PDF、Markdown、HTML

Step 2: LLM 自动生成 QA 对
  └── Prompt: "根据以下文档内容，生成 5 个不同难度的问题和对应答案"
  └── 控制难度分布：
      - Simple（40%）：答案在单一段落中，直接检索可回答
      - Complex（40%）：需要理解上下文或跨段落综合
      - Multi-hop（20%）：需要跨多个文档关联推理
  └── 同时生成 ground truth：标注答案来自哪些文档/段落

Step 3: 人工校验
  └── Alex 逐条审核，标准：
      - 问题是否自然（不是从答案反推的人造问题）
      - 答案是否准确完整
      - 难度标注是否合理
      - 相关文档标注是否正确
  └── 预计审核 pass rate: 60-70%（丢弃不合格的）

Step 4: 标注元数据
  └── 每条 QA 标注：
      - query（问题）
      - expected_answer（参考答案）
      - relevant_doc_ids（ground truth 相关文档列表）
      - difficulty（simple / complex / multi-hop）
      - domain（api-docs / design-docs / readme / troubleshooting）
```

### 3.3 目标数量

- **MVP 阶段：** 50 条（足够跑通评估流程，生成初步数据点）
- **V1 阶段：** 100 条（覆盖足够多的变量组合，结果统计上更可靠）
- **分布目标：** Simple 40 条 / Complex 40 条 / Multi-hop 20 条

### 3.4 数据集版本化

- 评估集存储为 JSON 文件，放在 `backend/app/evaluation/datasets/` 目录
- 每次修改评估集都打版本号（benchmark_v1.json → benchmark_v2.json）
- 实验结果必须标注使用的数据集版本，确保可对比

---

## 4. 评估维度

### 4.1 Retrieval Recall@K

**衡量什么：** 检索阶段是否找到了正确的文档。在 top-K 个检索结果中，ground truth 相关文档被命中的比例。

**计算方法：**
```
Recall@K = |检索到的相关文档 ∩ 所有相关文档| / |所有相关文档|
```

**K 值选择：**
- Recall@5 — 严格标准，核心指标
- Recall@10 — 宽松标准，展示上限

**工具：**
- 自建计算（基于 ground truth 标注）
- BEIR 提供标准化评估脚本

**核心意义：** Recall@10 衡量检索阶段有没有把正确文档放进候选池。这是 RAG 的地基——检索不到，后面再好的 LLM 也救不了。

### 4.2 Faithfulness

**衡量什么：** 生成的答案是否忠实于检索到的文档内容，有没有幻觉。

**计算方法（RAGAS 标准）：**
1. 从生成答案中提取所有 claims（声明/事实断言）
2. 逐条检查每个 claim 是否能从检索到的文档中找到支撑
3. Faithfulness = 有支撑的 claims 数 / 总 claims 数

**工具：**
- RAGAS `faithfulness` 指标
- DSPy LLM-as-judge 自定义 metric
- Arize Phoenix 追踪每次评估的具体判断过程

**核心意义：** Faithfulness 衡量答案有没有编造。预期 Agentic RAG 的 Faithfulness 高于 Pipeline RAG，因为 self-correction 过滤掉了不相关的文档，LLM 输入质量更好。

### 4.3 Answer Relevance

**衡量什么：** 生成的答案是否切题、完整、有用。

**计算方法（RAGAS 标准）：**
1. 从答案中反向生成 N 个可能的原始问题
2. 计算这些生成问题与原始 query 的语义相似度
3. Answer Relevance = 平均相似度
4. 惩罚机制：答案过于冗长或包含无关信息会降低得分

**工具：**
- RAGAS `answer_relevancy` 指标
- 需要 embedding 模型计算语义相似度

**核心意义：** Answer Relevance 确保答案不跑题。高 Faithfulness 但低 Relevance 意味着答案引用了正确文档但没回答用户的问题。

### 4.4 Context Precision

**衡量什么：** 检索到的文档中，有用信息的密度（信噪比）。

**计算方法（RAGAS 标准）：**
1. 评估检索到的每个 context chunk 是否对回答问题有用
2. 有用的 chunk 排在前面得分更高（考虑排序质量）
3. Context Precision = 加权精度

**工具：**
- RAGAS `context_precision` 指标
- 不需要 ground truth（LLM-as-judge 判断）

**核心意义：** Context Precision 衡量检索结果的信噪比。Reranking 的核心价值就体现在这里——rerank 后排在前面的文档更相关，Context Precision 会显著提升。

### 4.5 Latency P95

**衡量什么：** 端到端响应延迟的第 95 百分位数。

**计算方法：**
1. 记录每次 query 从接收到返回完整答案的耗时（毫秒）
2. 排序取 P95 值
3. 同时记录各节点的耗时分解（analyze → retrieve → rerank → grade → generate）

**关键分解：**
- Embedding 耗时：~50ms/query（CPU）/ ~5ms（GPU）
- Milvus 检索耗时：~20-50ms
- Reranking 耗时：~150ms（10 个文档，GPU）
- LLM 生成耗时：~1000-3000ms（取决于模型和答案长度）
- Self-correction 额外耗时：~500-1500ms/次（含重检索 + 重评分）

**工具：**
- Python `time.perf_counter()` 精确计时
- Arize Phoenix span-level 追踪
- 自建 latency 统计聚合

**核心意义：** P95 延迟是关键工程指标。预期 baseline P95 约 2.5s，加 self-correction 后最差情况 P95 约 5s，但 Recall 提升显著。这是一个明确的 latency-quality trade-off——在复杂 query 上牺牲延迟换质量。

---

## 5. 实验对比框架

### 5.1 变量列表

每次实验只变一个变量，其他条件固定：

**变量 1：Chunking 策略**
- 固定大小 256 tokens（baseline）
- 固定大小 512 tokens
- 语义切分（基于段落/标题边界）
- 分层切分（child 256 + parent 1024）— P1 最终方案

**变量 2：Embedding 模型**
- BGE-M3（P1 选择）— 多语言，dense + sparse
- BGE-Large-EN — 英文专用
- text-embedding-3-small（OpenAI）— API 方案

**变量 3：检索策略**
- Dense only（纯向量检索）
- Sparse only（纯 BM25）
- Hybrid（Dense + Sparse + RRF 融合）— P1 最终方案

**变量 4：Top-K**
- K=3
- K=5（P1 默认）
- K=10
- K=20

**变量 5：Reranker**
- 无 reranker（baseline）
- BGE-reranker-v2-m3（P1 选择）

**变量 6：Self-Correction**
- 无 self-correction（Pipeline RAG baseline）
- 有 self-correction，max_retries=1
- 有 self-correction，max_retries=2（P1 默认）

### 5.2 实验记录模板

采用 TSV 格式记录，便于版本控制和数据分析：

```
experiment_id	timestamp	dataset	dataset_version	chunking	embedding	retrieval	top_k	reranker	self_correction	max_retries	llm_model	recall_at_5	recall_at_10	faithfulness	answer_relevance	context_precision	latency_p50_ms	latency_p95_ms	cost_per_query_usd	notes
exp-001	2026-04-15T10:00:00	benchmark_v1	1.0	fixed_256	bge-m3	dense_only	5	none	false	0	qwen2.5-7b	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	baseline
exp-002	2026-04-15T11:00:00	benchmark_v1	1.0	fixed_256	bge-m3	hybrid	5	none	false	0	qwen2.5-7b	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	+hybrid
exp-003	2026-04-15T12:00:00	benchmark_v1	1.0	fixed_256	bge-m3	hybrid	5	bge-reranker	false	0	qwen2.5-7b	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	+rerank
exp-004	2026-04-15T13:00:00	benchmark_v1	1.0	hierarchical	bge-m3	hybrid	5	bge-reranker	true	2	qwen2.5-7b	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	full agentic
exp-005	2026-04-15T14:00:00	benchmark_v1	1.0	hierarchical	bge-m3	hybrid	5	bge-reranker	true	2	gpt-4o	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	[TBD]	agentic+gpt4o
```

### 5.3 基线定义

**Baseline（exp-001）：**
- 固定大小 256 token chunking
- BGE-M3 embedding
- 纯向量检索（Dense only）
- Top-K = 5
- 无 reranker
- 无 self-correction
- Qwen2.5-7B（本地模型）

**这是最简单的 RAG Pipeline 配置，后续所有实验都与它对比。**

每次加一个组件（混合检索 → reranker → self-correction → 分层 chunking），量化每个组件的增量贡献。

---

## 6. 预期 Benchmark 数据点

### 6.1 目标范围（基于文献和行业数据，待实测验证）

**Retrieval Recall@10：**
- Baseline（Dense only）：[TBD] 目标范围 65-75%
- + Hybrid（Dense + Sparse + RRF）：[TBD] 目标范围 +10-15%（75-85%）
- + Reranker：[TBD] 目标范围 +5-8%（80-90%）
- + Self-Correction：[TBD] 目标范围 +3-5%（复杂 query 上更明显）

**Faithfulness：**
- Baseline：[TBD] 目标范围 0.70-0.80
- Full Agentic：[TBD] 目标范围 0.85-0.95

**Context Precision：**
- 无 Reranker：[TBD] 目标范围 0.55-0.65
- 有 Reranker：[TBD] 目标范围 0.75-0.85

**Latency P95：**
- Baseline（无 rerank、无 self-correction）：[TBD] 目标范围 1500-2500ms
- Full Agentic（含 rerank + self-correction）：[TBD] 目标范围 3000-5500ms

**Semantic Cache Hit Rate：**
- 知识库 Q&A 场景：[TBD] 目标范围 30-40%

### 6.2 对标竞品公开数据

**BEIR Leaderboard 参考（nDCG@10）：**
- Voyage-Large-2：54.8%
- Cohere Embed v4：53.7%
- BGE-Large-EN：52.3%
- BM25 baseline：通常 40-45%

**行业经验值：**
- 混合检索 + Reranking 对比纯向量：通常 +15-25% Recall
- Self-correction 对复杂 query：通常 +5-10% Recall（简单 query 几乎无变化）
- 语义缓存命中率：知识库 Q&A 场景通常 30-40%

**RAGFlow 公开信息：**
- RAGFlow 对比 Dify 在 QA 准确率上有 20% 提升（Dify 官方博客数据）
- 但 RAGFlow 没有公开标准 BEIR benchmark 数据

**RGB Benchmark 参考：**
- ChatGPT 在 Noise Ratio=0 时准确率 96.33%，Noise Ratio=0.8 时降至 76%
- 小模型（7B）在高噪声场景表现急剧下降

---

## 7. FAQ

**Q: 为什么不用 RAGAS 做全部评估，要自己搭 DSPy？**

RAGAS 擅长指标计算，但 DSPy 的优势在于 programmatic prompt optimization。本项目采用 RAGAS 的指标体系（Faithfulness、Answer Relevance 等），同时用 DSPy 的 optimizer 自动调优 grading prompt 和 generation prompt。DSPy 还能和 LangChain Pipeline 无缝集成。

**Q: 100 条自建数据集够吗？**

100 条覆盖 3 个难度级别、4 个领域，足以产生有意义的对比数据。更重要的是评估流程的可复现性——任何人拉取 repo 跑同样的脚本都能得到相同结果。生产环境建议扩展到 500-1000 条并引入人工评估。

**Q: Self-correction 增加延迟，怎么缓解？**

两个策略：一是 query 路由——简单 query 跳过 self-correction 直接生成，只有复杂 query 走完整 Agentic 流程。二是 streaming——流式输出让用户在 self-correction 过程中看到中间状态（"正在验证检索结果..."），感知延迟远小于实际延迟。

**Q: 有对标竞品的评估吗？**

没有直接跑竞品代码做对比（不公平且工作量大），但对标了 BEIR 公开 leaderboard 数据和 RGB benchmark 公开结果。Baseline 相当于标准 RAG Pipeline，full agentic 配置的提升幅度符合学术文献中报告的范围。

---

*04-evaluation.md · P1 DocFlow RAG · v1.0 · 2026-03-23*
