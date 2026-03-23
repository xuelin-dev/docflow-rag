"""Evaluation repository — async CRUD for eval runs and samples."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EvalRun, EvalSample


class EvaluationRepository:
    """Async CRUD operations for evaluation runs and samples."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        name: str,
        config: dict,
        dataset_name: str | None = None,
        sample_count: int | None = None,
    ) -> EvalRun:
        """Create a new evaluation run."""
        run = EvalRun(
            name=name,
            config=config,
            dataset_name=dataset_name,
            sample_count=sample_count,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def complete_run(
        self,
        run_id: uuid.UUID,
        results: dict,
        status: str = "completed",
    ) -> None:
        """Mark an evaluation run as completed with results."""
        run = await self.session.get(EvalRun, run_id)
        if run:
            run.status = status
            run.results = results
            run.completed_at = datetime.now(timezone.utc)
            await self.session.flush()

    async def add_sample(
        self,
        run_id: uuid.UUID,
        query: str,
        expected: str | None = None,
        actual: str | None = None,
        scores: dict | None = None,
        latency_ms: int | None = None,
    ) -> EvalSample:
        """Add a sample result to an evaluation run."""
        sample = EvalSample(
            run_id=run_id,
            query=query,
            expected=expected,
            actual=actual,
            scores=scores,
            latency_ms=latency_ms,
        )
        self.session.add(sample)
        await self.session.flush()
        return sample

    async def list_runs(self, limit: int = 20, offset: int = 0) -> list[EvalRun]:
        """List evaluation runs ordered by creation date."""
        query = select(EvalRun).order_by(EvalRun.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_run(self, run_id: uuid.UUID) -> EvalRun | None:
        """Get an evaluation run by ID."""
        return await self.session.get(EvalRun, run_id)
