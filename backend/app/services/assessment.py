import sys
from pathlib import Path

# Use project root so data_quality_tool resolves to root package
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from data_quality_tool.assessment_engine import AssessmentEngine
from app.services.data_loader import load_data


def run_assessment(
    source_type: str,
    config: dict,
    rules: list,
    column_mapping: dict | None = None,
) -> tuple[list, str | None]:
    """
    Run assessment and return (results, error_message).
    column_mapping: {"actual_col": "rule_col"} to map data columns to rule-expected names.
    """
    df = load_data(source_type, config)
    if df is None:
        return [], "Failed to load data (file not found or invalid)"
    if column_mapping:
        df = df.rename(columns=column_mapping)
    engine = AssessmentEngine(df)
    results = engine.run_checks(rules)
    return results, None
