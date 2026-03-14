"""Profiling service: load data and run profiling."""
from app.services.data_loader import load_data


def run_profiling(datasource_type: str, config: dict, sample_size: int = 10000) -> dict | None:
    """
    Run profiling on a datasource.
    Returns {columns: [...]} or None on error.
    """
    df = load_data(datasource_type, config)
    if df is None:
        return None

    from data_quality_tool.profiling import profile_dataframe
    columns = profile_dataframe(df, sample_size=sample_size)
    return {"columns": columns, "row_count": len(df)}
