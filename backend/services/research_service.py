import time
import logging

from google.genai.errors import ServerError, ClientError

from ai.pipeline.research_pipeline import ResearchPipeline
from ai.schemas.research_result import ResearchResult

from backend.repositories.planner_task_repository import PlannerTaskRepository
from backend.repositories.source_repository import SourceRepository
from backend.repositories.evidence_repository import EvidenceRepository
from backend.repositories.validation_repository import ValidationRepository
from backend.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


class ResearchService:
    def __init__(
        self,
        pipeline=None,
        planner_task_repository=None,
        source_repository=None,
        evidence_repository=None,
        validation_repository=None,
        report_repository=None,
    ):
        self.pipeline = pipeline or ResearchPipeline()

        self.planner_task_repository = (
            planner_task_repository
            or PlannerTaskRepository()
        )

        self.source_repository = (
            source_repository
            or SourceRepository()
        )

        self.evidence_repository = (
            evidence_repository
            or EvidenceRepository()
        )

        self.validation_repository = (
            validation_repository
            or ValidationRepository()
        )

        self.report_repository = (
            report_repository
            or ReportRepository()
        )

    def run_research(
        self,
        query: str,
        job_id: str,
    ) -> ResearchResult:
        """
        Runs the complete AI research pipeline and persists results.
        """

        if not query or not query.strip():
            raise ValueError("Research query cannot be empty.")

        query = query.strip()

        logger.info("=" * 60)
        logger.info(f"Starting research job: {job_id}")
        logger.info(f"Research query: {query}")
        logger.info("=" * 60)

        service_start = time.time()

        try:
            # -------------------------------------------------------
            # Run AI Pipeline
            # -------------------------------------------------------
            pipeline_start = time.time()

            result = self.pipeline.run(query)

            logger.info(
                f"Research pipeline completed in "
                f"{time.time() - pipeline_start:.2f}s."
            )

            # -------------------------------------------------------
            # Save Planner Tasks
            # -------------------------------------------------------
            task_start = time.time()

            task_count = 0

            for task in result.tasks:
                self.planner_task_repository.create_task(
                    job_id=job_id,
                    task_type=task.purpose,
                    query=task.query,
                )
                task_count += 1

            logger.info(
                f"Saved {task_count} planner tasks "
                f"in {time.time() - task_start:.2f}s."
            )

            # -------------------------------------------------------
            # Save Sources
            # -------------------------------------------------------
            source_start = time.time()

            source_map = {}

            for source in result.sources:
                db_source = self.source_repository.create_source(
                    job_id=job_id,
                    url=source.url,
                    title=source.title,
                )

                source_map[source.source_id] = db_source

            logger.info(
                f"Saved {len(source_map)} sources "
                f"in {time.time() - source_start:.2f}s."
            )

            # -------------------------------------------------------
            # Save Evidence
            # -------------------------------------------------------
            evidence_start = time.time()

            evidence_map = {}

            for evidence in result.evidences:

                db_source = source_map.get(evidence.source_id)

                if not db_source:
                    logger.warning(
                        f"Skipping evidence "
                        f"{evidence.evidence_id}: source not found."
                    )
                    continue

                db_evidence = self.evidence_repository.create_evidence(
                    job_id=job_id,
                    source_id=db_source["id"],
                    claim=evidence.claim,
                    quote=evidence.excerpt,
                    confidence=evidence.relevance_score,
                )

                evidence_map[evidence.evidence_id] = db_evidence

            logger.info(
                f"Saved {len(evidence_map)} evidence items "
                f"in {time.time() - evidence_start:.2f}s."
            )

            # -------------------------------------------------------
            # Save Validation Results
            # -------------------------------------------------------
            validation_start = time.time()

            validation_count = 0

            for validation in result.validations:

                db_evidence = evidence_map.get(validation.evidence_id)

                if not db_evidence:
                    logger.warning(
                        f"Skipping validation for "
                        f"{validation.evidence_id}: evidence not found."
                    )
                    continue

                self.validation_repository.create_validation(
                    evidence_id=db_evidence["id"],
                    is_valid=validation.is_valid,
                    credibility_score=validation.credibility_score,
                    recency_score=validation.recency_score,
                    is_duplicate=validation.is_duplicate,
                    has_conflict=validation.has_conflict,
                    reason=validation.reason,
                )

                validation_count += 1

            logger.info(
                f"Saved {validation_count} validations "
                f"in {time.time() - validation_start:.2f}s."
            )

            # -------------------------------------------------------
            # Save Report
            # -------------------------------------------------------
            report_start = time.time()

            report_data = result.report.model_dump()

            self.report_repository.create_report(
                job_id=job_id,
                report=report_data,
            )

            logger.info(
                f"Saved research report "
                f"in {time.time() - report_start:.2f}s."
            )

            logger.info(
                "=" * 60
            )
            logger.info(
                f"Research job {job_id} completed successfully "
                f"in {time.time() - service_start:.2f}s."
            )
            logger.info("=" * 60)

            return result

        # -------------------------------------------------------
        # Gemini temporary failures (503 / 429 / 500)
        # -------------------------------------------------------
        except (ServerError, ClientError) as e:
            logger.error(
                f"Gemini temporary failure while processing "
                f"job {job_id}: {e}"
            )

            raise RuntimeError(
                "Gemini is temporarily unavailable. Please retry shortly."
            ) from e

        # -------------------------------------------------------
        # Pipeline / Database failures
        # -------------------------------------------------------
        except Exception as e:
            logger.exception(
                f"Research job {job_id} failed after "
                f"{time.time() - service_start:.2f}s."
            )

            raise