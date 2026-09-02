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
from ai.schemas.report import Report


class ResearchPipeline:

    def __init__(
        self,
        planner=None,
        researcher=None,
        extractor=None,
        validator=None,
        reporter=None,
        citation_builder=None,
        report_linker=None
    ):
        self.planner = planner or PlannerAgent()
        self.researcher = researcher or ResearchAgent()
        self.extractor = extractor or ExtractionAgent()
        self.validator = validator or ValidationAgent()
        self.reporter = reporter or ReportAgent()
        self.citation_builder = citation_builder or CitationBuilder()
        self.report_linker = report_linker or ReportLinker()

    def run(self, query: str) -> ResearchResult:

        # Step 1: Planning
        tasks: list[ResearchTask] = self.planner.create_plan(query)

        if not tasks:
            raise ValueError("Planner returned no research tasks")

        print(f"\nPlanner generated {len(tasks)} research tasks.")

        # Step 2: Research
        sources: list[Source] = []

        for task in tasks:
            task_sources = self.researcher.research(task)
            sources.extend(task_sources)

        if not sources:
            raise ValueError("Research agent returned no sources")

        print(f"Research found {len(sources)} sources.")

        # Step 3: Extraction
        evidences: list[Evidence] = []

        for source in sources:
            source_evidence = self.extractor.extract(source)
            evidences.extend(source_evidence)

        if not evidences:
            raise ValueError("Extraction agent returned no evidence")

        print(f"Extraction produced {len(evidences)} evidence items.")

        # Step 4: Validation
        validations: list[ValidationResult] = self.validator.validate(
            evidences=evidences,
            sources=sources
        )

        if not validations:
            raise ValueError(
                "Validation agent returned no validation results"
            )

        print(f"Validation produced {len(validations)} results.")

        # Step 5: Citation Building
        citations = self.citation_builder.build(sources)

        if not citations:
            raise ValueError("Citation builder returned no citations")

        print(f"Generated {len(citations)} citations.")

        # Step 6: Report Generation
        report = self.reporter.generate_report(
        tasks=tasks,
        evidences=evidences,
        validations=validations,
        citations=citations
        )

        if not report:
            raise ValueError("Report agent returned no report")


        # Step 7: Link Report to Sources
        linked_report = self.report_linker.link_report(
        report=report,
        evidences=evidences,
        citations=citations
        )

        if not linked_report:
            raise ValueError(
            "Report linker returned no linked report"
        )

        print("Report generated successfully.")
        print(
            f"Linked {len(linked_report.key_findings)} key findings."
        )

        return ResearchResult(
        report=report,
        linked_report=linked_report,
        tasks=tasks,
        sources=sources,
        evidences=evidences,
        validations=validations,
        )