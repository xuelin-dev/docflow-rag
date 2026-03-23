# P1 DocFlow RAG — 开发阶段

> **文档版本：** 1.0
> **日期：** 2026-03-23
> **来源：** 从 p1-architecture-zh.md 第 7 节抽取

---

## 总览

三个阶段，共约 12 周：

- **MVP（第 1–3 周）** — 最小可行 RAG，跑通端到端
- **V1（第 4–9 周）** — Agentic RAG 核心，可 demo 演示
- **V2（第 10–12 周，可选）** — 高级能力，锦上添花

---

## MVP（第 1–3 周） — 最小可行 RAG

**目标：** 跑通 "上传文档 → 提问 → 拿到答案" 的完整链路。

**范围：**
- [ ] 项目脚手架（Monorepo、Docker Compose、CI 基础）
- [ ] 文档上传：PDF + Markdown + TXT 解析
- [ ] 固定大小分块（V1 切换为层级分块）
- [ ] BGE-M3 Embedding + Milvus Dense 向量存储
- [ ] 基础向量检索（仅 Dense，无混合搜索）
- [ ] FastAPI：`/query`（非流式）+ `/documents` CRUD
- [ ] React 对话界面：发送查询 → 展示回答 + 基本来源
- [ ] PostgreSQL：documents + chunks + query_history 表
- [ ] Docker Compose：FastAPI + React + Milvus + PostgreSQL + Redis + Etcd + MinIO

**验收标准：**
1. 上传 PDF → 系统解析、分块、Embedding、存入 Milvus
2. 提问 → 系统检索相关 Chunk → LLM 生成带来源引用的回答
3. `docker compose up` 启动完整技术栈
4. 响应延迟 < 10 秒（暂未优化）

---

## V1（第 4–9 周） — Agentic RAG 核心

**目标：** 实现完整的 Agentic RAG，可现场 demo 演示。

**范围：**
- [ ] 层级分块（替换固定大小）
- [ ] LangGraph 状态机：完整 Agentic RAG 流程
  - [ ] 查询分析 + 路由（simple/complex）
  - [ ] 混合检索（Dense + Sparse，通过 BGE-M3）
  - [ ] RRF 融合
  - [ ] Cross-Encoder 重排序（BGE-reranker）
  - [ ] 文档评分
  - [ ] 查询改写 + 自纠错循环
- [ ] WebSocket 流式对话
- [ ] Redis 语义缓存
- [ ] MCP Server：`rag_query`、`document_add`、`namespace_list`
- [ ] DSPy 评估框架 + 基线基准测试
- [ ] HTML + DOCX 文档支持
- [ ] React：流式对话 + 来源归因面板 + 文档管理
- [ ] Namespace 支持（多文档集合）
- [ ] 对话历史（多轮对话）
- [ ] API Key 认证
- [ ] CI/CD：GitHub Actions（lint + test + Docker 构建）
- [ ] README：架构图 + Quick Start

**验收标准：**
1. Agentic RAG：复杂查询触发分解 → 混合检索 → 评分 → 可选改写 → 回答
2. 自纠错可演示："检索质量差"的查询触发改写循环（在流式状态中可见）
3. DSPy 基准：至少 3 种实验变体并发布指标
4. MCP Server 可被外部客户端调用
5. 缓存命中率可测量（重复查询时 > 0%）
6. 完整 `docker compose up`，所有服务健康
7. 可演示：能用真实文档进行 live demo

---

## V2（第 10–12 周，可选） — 高级能力

**目标：** 差异化高级能力。

**范围：**
- [ ] GraphRAG 增强：实体关系图用于多跳推理 [TBD: 评估 Neo4j 还是内存图]
- [ ] Human-in-the-loop：用户标记"回答不好" → 带反馈重新检索
- [ ] 增量重索引：文档更新时仅对变更的 Chunk 重新 Embedding
- [ ] 多源连接器：Notion API、GitHub README（通过 MCP）
- [ ] DSPy 自动 Prompt 优化 + 对比报告
- [ ] React 评估 Dashboard（图表、对比表格）
- [ ] 限流 + 用量指标

**验收标准：**
1. GraphRAG 在多跳查询上优于基线（有数据证明）
2. 文档更新触发部分重索引，而非全量重建
3. 至少一个外部连接器（Notion 或 GitHub）可用

---

## 里程碑时间线

- **4 月第 1 周：** MVP 完成，`docker compose up` 跑通
- **4 月第 3 周：** V1 第一批功能（LangGraph 状态机 + 混合检索）
- **5 月第 1 周：** V1 完成，可 demo
- **5 月第 2 周：** P1 收尾，开始 P3 CodeReviewer
- **6-7 月：** V2 可选功能按需推进

---

*05-development-phases.md · DocFlow RAG · 2026-03-23*
