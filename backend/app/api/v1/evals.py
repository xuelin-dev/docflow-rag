"""Evaluation endpoints."""

from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, DbSession

router = APIRouter()


class EvalRunRequest(BaseModel):
    """Trigger an evaluation run."""
    name: str = Field(..., min_length=1, max_length=255)
    dataset_name: str = Field(default="benchmark_v1")
    config: dict = Field(default_factory=dict, description="ExperimentConfig overrides")


class EvalMetrics(BaseModel):
    """Evaluation metrics."""
    faithfulness: float = 0.0
    relevance_precision: float = 0.0
    retrieval_recall: float = 0.0
    answer_quality: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0


class EvalRunResponse(BaseModel):
    """Evaluation run result."""
    id: UUID
    name: str
    status: str = "running"
    dataset_name: str | None = None
    sample_count: int = 0
    metrics: EvalMetrics | None = None
    created_at: str | None = None
    completed_at: str | None = None


class EvalListResponse(BaseModel):
    """List of evaluation runs."""
    runs: list[EvalRunResponse]
    total: int


@router.post("/run", response_model=EvalRunResponse, status_code=201)
async def trigger_eval_run(request: EvalRunRequest, db: DbSession, user: CurrentUser) -> EvalRunResponse:
    """Trigger a new evaluation run against the benchmark dataset.

    Runs the RAG pipeline with the specified configuration against
    evaluation samples and computes faithfulness, relevance, and quality metrics.
    """
    # TODO: Enqueue eval run
    return EvalRunResponse(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        name=request.name,
        status="queued",
        dataset_name=request.dataset_name,
    )


@router.get("/results", response_model=EvalListResponse)
async def list_eval_results(db: DbSession, user: CurrentUser) -> EvalListResponse:
    """List all evaluation runs with their metrics."""
    # TODO: Query from database
    return EvalListResponse(runs=[], total=0)


@router.get("/results/{run_id}", response_model=EvalRunResponse)
async def get_eval_result(run_id: UUID, db: DbSession, user: CurrentUser) -> EvalRunResponse:
    """Get detailed results for a specific evaluation run."""
    # TODO: Fetch from database
    return EvalRunResponse(
        id=run_id,
        name="placeholder",
        status="completed",
    )
