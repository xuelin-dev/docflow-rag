# DocFlow RAG

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![React](https://img.shields.io/badge/react-18-blue)

Production-grade Agentic RAG engine that turns private documents into a conversational, traceable knowledge base with self-correction capabilities.

## Key Features

- **Agentic RAG with LangGraph state machine** — Multi-step reasoning with query planning, retrieval, and answer generation
- **Hybrid retrieval (dense + sparse) with RRF fusion** — Combines semantic and keyword search for better recall
- **Cross-encoder reranking** — Re-scores retrieved chunks for higher precision
- **Self-correction loop** — Automatic query rewrite and re-retrieval when answers are insufficient
- **Source attribution with chunk-level provenance** — Every answer cites exact document chunks
- **MCP Server for Agent interoperability** — Expose RAG as a tool for other agents
- **Semantic caching (Redis)** — Cache embeddings and results for faster repeated queries
- **DSPy evaluation framework** — Systematic benchmarking of retrieval and generation quality
- **React/TS frontend with streaming chat** — Real-time streaming responses with source highlights

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  React 18 + TypeScript Frontend                        │    │
│  │  - Streaming chat UI                                   │    │
│  │  - Source attribution display                          │    │
│  │  - Document upload & management                        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           API Layer                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  FastAPI + Uvicorn                                     │    │
│  │  - REST endpoints (/query, /ingest, /health)          │    │
│  │  - SSE streaming for chat                             │    │
│  │  - MCP server integration                             │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Engine Layer                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  LangGraph State Machine                               │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│  │  │  Query   │→ │ Retrieve │→ │ Generate │            │    │
│  │  │ Planning │  │ & Rerank │  │ Answer   │            │    │
│  │  └──────────┘  └──────────┘  └──────────┘            │    │
│  │       ↑              ↓              ↓                  │    │
│  │       └──────── Self-Correction ────┘                 │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Retrieval Pipeline                                    │    │
│  │  - BGE-M3 embeddings (dense)                           │    │
│  │  - BM25 (sparse)                                       │    │
│  │  - RRF fusion                                          │    │
│  │  - Cross-encoder reranking                             │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Storage Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Milvus     │  │    Redis     │  │  PostgreSQL  │         │
│  │  (vectors)   │  │  (cache)     │  │  (metadata)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component          | Choice                | Version  |
|--------------------|-----------------------|----------|
| Backend Framework  | FastAPI               | 0.115+   |
| LLM Orchestration  | LangGraph             | 0.2+     |
| Vector Store       | Milvus                | 2.4+     |
| Embedding Model    | BGE-M3                | BAAI     |
| Reranker           | bge-reranker-v2-m3    | BAAI     |
| Cache              | Redis                 | 7.2+     |
| Database           | PostgreSQL            | 16+      |
| Frontend           | React + TypeScript    | 18+      |
| Evaluation         | DSPy                  | 2.5+     |
| LLM Provider       | Ollama / OpenAI-compatible | -    |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/XueLin25/docflow-rag.git
cd docflow-rag

# Configure environment
cp .env.example .env
# Edit .env with your settings (LLM endpoint, model names, etc.)

# Start all services
docker compose up -d

# Open the frontend
open http://localhost:3000
```

The application will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend dev server will proxy API requests to http://localhost:8000.

## Project Structure

```
docflow-rag/
├── backend/
│   ├── app/
│   │   ├── api/              # REST endpoints
│   │   ├── core/             # Config, logging
│   │   ├── graph/            # LangGraph state machine
│   │   ├── models/           # Pydantic models
│   │   ├── services/         # Business logic (retrieval, LLM, cache)
│   │   └── main.py           # FastAPI app entry
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── architecture.md
│   ├── prd.md
│   └── evaluation.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Reference

### Core Endpoints

- `POST /api/v1/query` — Submit a query and get streaming response
  - Request: `{ "query": "string", "session_id": "optional" }`
  - Response: SSE stream with chunks and sources

- `POST /api/v1/ingest` — Upload and process documents
  - Request: multipart/form-data with files
  - Response: `{ "task_id": "uuid", "status": "processing" }`

- `GET /api/v1/documents` — List ingested documents
  - Response: `[{ "id": "uuid", "name": "string", "status": "ready" }]`

- `GET /health` — Health check
  - Response: `{ "status": "ok", "services": {...} }`

### MCP Server

The MCP server exposes a `rag_query` tool for agent interoperability. See `docs/mcp-integration.md` for details.

## Evaluation

Run DSPy evaluation benchmarks:

```bash
cd backend
python -m app.evaluation.run_eval \
  --dataset data/eval/test_set.jsonl \
  --output results/eval_$(date +%Y%m%d).json
```

Metrics tracked:
- Retrieval: Precision@k, Recall@k, MRR
- Generation: ROUGE-L, BERTScore, Human ratings
- End-to-end: Answer accuracy, Source correctness

See `docs/evaluation.md` for detailed methodology.

## Roadmap

### MVP (Current)
- ✅ Core RAG pipeline (ingest, retrieve, generate)
- ✅ Hybrid retrieval with RRF
- ✅ Basic web UI
- ✅ Docker Compose deployment

### V1 (Q2 2026)
- [ ] Self-correction loop (query rewrite + re-retrieve)
- [ ] Cross-encoder reranking
- [ ] Semantic caching
- [ ] MCP server integration
- [ ] DSPy evaluation framework

### V2 (Q3 2026)
- [ ] Multi-hop reasoning
- [ ] Structured data extraction
- [ ] Multi-lingual support
- [ ] Fine-tuned reranker on domain data
- [ ] Observability dashboard (Arize Phoenix integration)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows project style (Black for Python, Prettier for TypeScript)
- Tests pass (`pytest` for backend, `npm test` for frontend)
- New features include tests and documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) — State machine orchestration
- [Milvus](https://milvus.io/) — Vector database
- [DSPy](https://github.com/stanfordnlp/dspy) — LLM evaluation framework
- [BGE-M3](https://huggingface.co/BAAI/bge-m3) — Embedding model by BAAI

Built with ❤️ by [Alex](https://github.com/XueLin25)
