# -*- coding: utf-8 -*-
"""
文件名: profiling.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据剖析模块，列级统计与规则推荐
"""
from typing import Optional
import pandas as pd


def profile_dataframe(df: pd.DataFrame, sample_size: Optional[int] = None) -> list[dict]:
    """
    Profile a DataFrame: compute column-level statistics and suggest rules.

    Args:
        df: Input DataFrame
        sample_size: If set, profile only first N rows (for large datasets)

    Returns:
        List of column stats: {name, dtype, non_null_count, null_count, unique_count, suggested_rules, ...}
    """
    if df.empty:
        return []

    if sample_size and len(df) > sample_size:
        df = df.head(sample_size)

    results = []
    for col in df.columns:
        series = df[col]
        non_null = series.notna().sum()
        null_count = series.isna().sum()
        unique_count = int(series.nunique())

        info: dict = {
            "name": col,
            "dtype": str(series.dtype),
            "non_null_count": int(non_null),
            "null_count": int(null_count),
            "unique_count": unique_count,
            "suggested_rules": _suggest_rules(series, col, non_null, null_count, unique_count, len(df)),
        }

        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            if len(valid) > 0:
                info["min"] = float(valid.min())
                info["max"] = float(valid.max())
                info["mean"] = float(valid.mean())

        if pd.api.types.is_datetime64_any_dtype(series):
            valid = series.dropna()
            if len(valid) > 0:
                info["min_date"] = str(valid.min())
                info["max_date"] = str(valid.max())

        results.append(info)

    return results


def _suggest_rules(
    series: pd.Series, col: str,
    non_null: int, null_count: int, unique_count: int, total: int
) -> list[str]:
    """Suggest quality rules based on column statistics."""
    suggestions: list[str] = []

    if null_count > 0:
        suggestions.append("completeness")

    if unique_count == total and total > 0:
        suggestions.append("uniqueness")

    if pd.api.types.is_numeric_dtype(series):
        suggestions.append("data_type")
        suggestions.append("accuracy_range_check")

    if pd.api.types.is_datetime64_any_dtype(series):
        suggestions.append("data_type")
        suggestions.append("timeliness_fixed_range_check")

    if series.dtype == object or str(series.dtype) == "string":
        sample = series.dropna().head(10)
        if len(sample) > 0 and any(isinstance(v, str) and "@" in str(v) for v in sample):
            suggestions.append("validity_regex_match_check")

    return list(dict.fromkeys(suggestions))
