import time
import logging
import re

from google.genai.errors import ServerError, ClientError

from ai.planner.planner_agent import PlannerAgent
from ai.research.research_agent import ResearchAgent
from ai.extraction.extraction_agent import ExtractionAgent
from ai.validation.validation_agent import ValidationAgent
from ai.report.report_agent import ReportAgent
from ai.report.citation_builder import CitationBuilder
from ai.report.report_linker import ReportLinker

from ai.schemas.research_result import ResearchResult
from ai.schemas.research_task import ResearchTask
from ai.schemas.source import Source
from ai.schemas.evidence import Evidence
from ai.schemas.validation import ValidationResult

logger = logging.getLogger(__name__)

# ==========================================================
# Retry Configuration
# ==========================================================

MAX_GEMINI_RETRIES = 5
INITIAL_BACKOFF = 2
REQUEST_DELAY = 0.5


class ResearchPipeline:
    def __init__(
        self,
        planner=None,
        researcher=None,
        extractor=None,
        validator=None,
        reporter=None,
        citation_builder=None,
        report_linker=None,
    ):
        self.planner = planner or PlannerAgent()
        self.researcher = researcher or ResearchAgent()
        self.extractor = extractor or ExtractionAgent()
        self.validator = validator or ValidationAgent()
        self.reporter = reporter or ReportAgent()
        self.citation_builder = citation_builder or CitationBuilder()
        self.report_linker = report_linker or ReportLinker()

    # ==========================================================
    # Extract Retry Delay from Gemini Error
    # ==========================================================

    @staticmethod
    def _extract_retry_delay(error: Exception) -> int | None:
        """
        Extract retry delay from Gemini RetryInfo.

        Example message:
        retryDelay: '12s'
        """

        text = str(error)

        match = re.search(r"retryDelay['\"]?:\\s*['\"]?(\\d+)s", text)

        if match:
            return int(match.group(1))

        return None

    # ==========================================================
    # Generic Retry Wrapper
    # ==========================================================

    def _run_with_retry(self, func, stage_name: str, item_name: str):
        """
        Retry Gemini operations on retryable HTTP errors.
        """

        retryable_codes = ["429", "500", "502", "503", "504"]

        for attempt in range(1, MAX_GEMINI_RETRIES + 1):

            try:
                logger.info(
                    "%s: Processing %s (Attempt %s/%s)",
                    stage_name,
                    item_name,
                    attempt,
                    MAX_GEMINI_RETRIES,
                )

                return func()

            except (ServerError, ClientError, RuntimeError) as e:

                error_text = str(e)

                retryable = any(code in error_text for code in retryable_codes)

                if not retryable:
                    logger.exception(
                        "%s: Non-retryable Gemini error while processing %s",
                        stage_name,
                        item_name,
                    )
                    raise

                if attempt == MAX_GEMINI_RETRIES:
                    logger.error(
                        "%s: Failed after %s retries for %s",
                        stage_name,
                        MAX_GEMINI_RETRIES,
                        item_name,
                    )
                    raise RuntimeError(
                        "Gemini is temporarily unavailable after multiple retries. Please retry in a few minutes."
                    ) from e

                retry_delay = self._extract_retry_delay(e)

                if retry_delay:
                    wait_time = retry_delay
                else:
                    wait_time = INITIAL_BACKOFF * (2 ** (attempt - 1))

                logger.warning(
                    "%s: Retryable Gemini error while processing %s. "
                    "Waiting %ss before retry (%s/%s). Error: %s",
                    stage_name,
                    item_name,
                    wait_time,
                    attempt,
                    MAX_GEMINI_RETRIES,
                    error_text,
                )

                time.sleep(wait_time)

    # ==========================================================
    # Main Pipeline
    # ==========================================================

    def run(self, query: str) -> ResearchResult:

        pipeline_start = time.time()

        try:

            # ------------------------------------------------------
            # STEP 1 — Planner
            # ------------------------------------------------------

            logger.info("========== PLANNER STAGE ==========")

            start = time.time()

            tasks: list[ResearchTask] = self._run_with_retry(
                lambda: self.planner.create_plan(query),
                stage_name="Planner",
                item_name="Research Plan",
            )

            if not tasks:
                raise ValueError("Planner returned no research tasks.")

            logger.info(
                "Planner generated %s research tasks in %.2fs.",
                len(tasks),
                time.time() - start,
            )

            # ------------------------------------------------------
            # STEP 2 — Research
            # ------------------------------------------------------

            logger.info("========== RESEARCH STAGE ==========")

            start = time.time()

            sources: list[Source] = []

            for task in tasks:
                sources.extend(self.researcher.research(task))

            if not sources:
                raise ValueError("Research agent returned no sources.")

            logger.info(
                "Research found %s sources in %.2fs.",
                len(sources),
                time.time() - start,
            )

            # ------------------------------------------------------
            # STEP 3 — Extraction
            # ------------------------------------------------------

            logger.info("========== EXTRACTION STAGE ==========")

            start = time.time()

            evidences: list[Evidence] = []

            for index, source in enumerate(sources, start=1):

                source_evidence = self._run_with_retry(
                    lambda s=source: self.extractor.extract(s),
                    stage_name="Extraction",
                    item_name=f"Source {index}/{len(sources)}",
                )

                evidences.extend(source_evidence)

                if index < len(sources):
                    time.sleep(REQUEST_DELAY)

            if not evidences:
                raise ValueError("Extraction agent returned no evidence.")

            logger.info(
                "Extraction produced %s evidence items in %.2fs.",
                len(evidences),
                time.time() - start,
            )

            # ------------------------------------------------------
            # STEP 4 — Validation
            # ------------------------------------------------------

            logger.info("========== VALIDATION STAGE ==========")

            start = time.time()

            time.sleep(2)

            validations: list[ValidationResult] = self._run_with_retry(
                lambda: self.validator.validate(
                    evidences=evidences,
                    sources=sources,
                ),
                stage_name="Validation",
                item_name="Evidence Batch",
            )

            if not validations:
                raise ValueError("Validation agent returned no validation results.")

            logger.info(
                "Validation produced %s results in %.2fs.",
                len(validations),
                time.time() - start,
            )

            # ------------------------------------------------------
            # STEP 5 — Citation Builder
            # ------------------------------------------------------

            logger.info("========== CITATION STAGE ==========")

            start = time.time()

            citations = self.citation_builder.build(sources)

            if not citations:
                raise ValueError("Citation builder returned no citations.")

            logger.info(
                "Generated %s citations in %.2fs.",
                len(citations),
                time.time() - start,
            )

            # ------------------------------------------------------
            # STEP 6 — Report Generation
            # ------------------------------------------------------

            logger.info("========== REPORT STAGE ==========")

            start = time.time()

            time.sleep(2)

            if len(evidences) > 20:
                try:
                    top_evidence = sorted(
                        evidences,
                        key=lambda x: getattr(x, "relevance_score", 0),
                        reverse=True,
                    )[:20]
                except Exception:
                    top_evidence = evidences[:20]
            else:
                top_evidence = evidences

            report = self._run_with_retry(
                lambda: self.reporter.generate_report(
                    tasks=tasks,
                    evidences=top_evidence,
                    validations=validations,
                    citations=citations,
                ),
                stage_name="Report",
                item_name="Final Report",
            )

            if not report:
                raise ValueError("Report agent returned no report.")

            logger.info(
                "Report generated in %.2fs.",
                time.time() - start,
            )

            # ------------------------------------------------------
            # STEP 7 — Report Linking
            # ------------------------------------------------------

            logger.info("========== REPORT LINKER STAGE ==========")

            start = time.time()

            linked_report = self.report_linker.link_report(
                report=report,
                evidences=evidences,
                citations=citations,
            )

            if not linked_report:
                raise ValueError("Report linker returned no linked report.")

            logger.info(
                "Linked %s key findings in %.2fs.",
                len(linked_report.key_findings),
                time.time() - start,
            )

            logger.info(
                "Pipeline completed successfully in %.2fs.",
                time.time() - pipeline_start,
            )

            return ResearchResult(
                report=report,
                linked_report=linked_report,
                tasks=tasks,
                sources=sources,
                evidences=evidences,
                validations=validations,
            )

        # ------------------------------------------------------
        # Final Gemini Failure
        # ------------------------------------------------------

        except RuntimeError:
            logger.exception("Pipeline stopped because Gemini remained unavailable.")
            raise

        except (ServerError, ClientError) as e:
            logger.exception("Unhandled Gemini API error.")
            raise RuntimeError(
                "Gemini is temporarily unavailable. Please retry."
            ) from e

        except Exception:
            logger.exception(
                "Research pipeline failed after %.2fs.",
                time.time() - pipeline_start,
            )
            raise
