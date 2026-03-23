# P1 DocFlow RAG — 立项背景

> **文档版本：** 1.0
> **日期：** 2026-03-23
> **作者：** Dojo

---

## 1. 项目定位

**一句话：** 生产级 Agentic RAG 引擎，让私有文档变成可对话、可溯源、能自我纠正的知识库。

不是又一个 RAG demo，是面向真实生产环境的、具备自我纠正能力的知识检索系统，同时暴露 MCP Server 接口供其他 Agent 调用。

---

## 2. 市场现状分析

当前 RAG 项目生态可分为四类，每类有不同的定位和局限：

### 2.1 平台型（Low-Code RAG Platform）

**代表项目：** Dify（134K⭐）、FastGPT（27K⭐）、RAGFlow（75K⭐）

**特征：**
- 提供可视化界面，拖拽配置 RAG Pipeline
- 开箱即用，非技术用户也能上手
- 商业化路线，面向企业知识库场景

**局限：**
- 底层 RAG 逻辑封装在平台内部，开发者难以深度定制
- 检索策略固定或配置项有限，无法做精细的 Agentic 控制
- 对开发者而言是"黑箱"——难以深入理解和定制底层技术决策

### 2.2 框架型（RAG Framework / SDK）

**代表项目：** LangChain（125K⭐）、LlamaIndex（46.5K⭐）、Haystack（24.6K⭐）

**特征：**
- 提供 RAG 的基础组件（loader、splitter、retriever、generator）
- 开发者用代码组装 Pipeline
- 生态丰富，集成选项多

**局限：**
- 提供的是"积木"，不是"成品"——开发者需要自己完成大量工程化工作
- RAG 模板（如 LangChain RAG templates）只展示 happy path，不处理生产级问题
- 缺少内置的评估框架、缓存策略、自我纠正机制

### 2.3 Demo 型（Tutorial / Prototype RAG）

**代表项目：** 各种 LangChain RAG 教程、Streamlit RAG demo、ChatPDF 类工具

**特征：**
- Notebook 或简单脚本实现 retrieve → generate
- 用于学习和概念验证
- 通常基于 Chroma + OpenAI API

**局限：**
- 固定大小 chunking 破坏语义完整性
- 无混合检索、无重排序、无自我纠正
- 无法处理生产环境的复杂问题（多文档来源、权限、缓存、监控）
- 同质化严重，无差异化

### 2.4 工程化深度型（Production-Grade Agentic RAG）

**代表项目：** 极少。这正是 P1 的定位空间。

**特征：**
- 完整的 Agentic RAG 状态机（query 分析 → 路由 → 检索 → 评分 → 纠正 → 生成）
- 混合检索 + Cross-Encoder Reranking
- 可量化的评估框架
- MCP 标准接口，可被其他 Agent 调用
- 生产级基础设施（缓存、异步队列、监控）

**局限：**
- 开发成本高，需要同时具备 AI 知识和工程化能力
- 目前市场上真正做到这一层的开源项目很少

---

## 3. 痛点定义

### 3.1 P1 解决什么问题

**痛点一：传统 RAG 的"一次检索"天花板**
- 传统 RAG 是 Pipeline 模式：retrieve → generate，一次完成
- 当 query 模糊、多义或复杂（如"为什么 API 在 auth 重构后返回 502"），一次检索很可能返回错误文档
- 检索失败 → LLM 基于错误文档生成答案 → 幻觉
- **P1 的解决方案：** LangGraph 状态机控制的 Agentic RAG，包含文档相关性评分 + query 改写 + 自我纠正循环

**痛点二：知识碎片化**
- 技术团队的知识散落在 Confluence、Notion、GitHub README、PDF 规范文档中
- 没有统一的 Q&A 入口
- **P1 的解决方案：** 多格式文档支持（PDF/MD/HTML/TXT）+ Namespace 隔离 + 统一检索接口

**痛点三：答案不可信**
- 普通 RAG 不展示答案来自哪个文档、哪一段、什么时候更新的
- 工程师不敢依赖没有溯源的 AI 答案
- **P1 的解决方案：** 每个答案都附带来源文档段落、相关性分数、原始 URL

### 3.2 目标用户

- **主要用户：** 中小技术团队（5-50人），有大量内部文档但没有统一知识管理工具
- **次要用户：** 个人开发者，管理学习笔记、代码注释、技术文档
- **场景通用性：** 任何技术团队都能理解场景，支持 live demo 展示

---

## 4. 差异化定位

### P1 vs 市面方案的本质区别

**vs 平台型（Dify/FastGPT/RAGFlow）：**
- P1 不做平台，做引擎。暴露 MCP Server 接口，可被任何 Agent 调用
- P1 的 RAG 逻辑完全开放、可定制，每个技术决策都可追溯和讨论
- P1 的评估框架是一等公民（DSPy），不是附加功能

**vs 框架型（LangChain/LlamaIndex/Haystack）：**
- 框架提供积木，P1 是完整的生产级应用
- P1 在框架（LangChain + LangGraph）之上构建了 Agentic RAG 状态机、语义缓存、评估系统
- P1 有前端界面（React/TS）和 Docker Compose 一键部署

**vs Demo 型：**
- P1 的每个模块都有 trade-off 分析和实验数据支撑
- 分层 Chunking、混合检索、Cross-Encoder Reranking、自我纠正——Demo 型项目一个都没做
- P1 有 benchmark 数据支撑，不是"跑通就行"

### P1 的核心差异化标签

1. **Agentic > Pipeline** — 不是一次性 retrieve-generate，是有自我评估和纠正能力的 Agent
2. **MCP Server** — 标准工具接口，P3 CodeReviewer 直接调用，展示跨项目组合能力
3. **可量化** — DSPy 评估框架，5 组实验变量，有 benchmark 数据支撑
4. **全栈交付** — Python 后端 + React 前端 + Docker Compose，不是 Notebook demo

---

## 5. 项目风险

### 已知风险 + 应对策略

**风险 1：Milvus 配置复杂度**
- 风险等级：低
- Milvus 需要 etcd + MinIO 作为依赖，初始配置繁琐
- 应对：Docker Compose 已覆盖全部依赖；训练营课程包含 Milvus 模块
- 备选方案：如果 Milvus 出现不可解决的问题，可降级为 pgvector（牺牲部分功能）

**风险 2：DSPy 评估框架学习成本**
- 风险等级：低
- DSPy 文档质量一般，API 变化频繁
- 应对：1-2 天快速上手核心功能即可；备选用 RAGAS 框架做评估

**风险 3：LLM API 成本**
- 风险等级：中
- 开发阶段频繁调用 LLM（评估、自我纠正）会产生 API 费用
- 应对：开发阶段用 Ollama + Qwen2.5-7B（免费本地模型）；Redis 语义缓存降低重复调用

**风险 4：与训练营时间冲突**
- 风险等级：中
- 4 月起训练营全日制，项目开发只能用课余时间
- 应对：CC（Claude Code）做编码执行，Alex 做架构决策和 review；MVP 控制在 2-3 周

**风险 5：竞品迭代速度**
- 风险等级：低
- RAGFlow 等竞品快速迭代，功能不断增加
- 应对：P1 的定位与竞品不同——SDK + MCP Server 路线 vs 平台路线。竞品越成熟，反而说明方向正确

**风险 6：GraphRAG V2 的数据质量**
- 风险等级：中
- GraphRAG 需要高质量的实体关系图谱，构建成本高
- 应对：V2 是可选功能，可参考 LightRAG 的方案；如果时间不够直接跳过

---

*01-proposal.md · P1 DocFlow RAG · v1.0 · 2026-03-23*
