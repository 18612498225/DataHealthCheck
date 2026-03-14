# -*- coding: utf-8 -*-
"""
文件名: reporter.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 生成文本格式数据质量报告
"""
import logging
import sys

logger = logging.getLogger(__name__)


def generate_text_report(results: list, output_file_path: str = None):
    """
    Generates a text-based data quality report from assessment results.

    Args:
        results: A list of dictionaries, where each dictionary is a result
                 from AssessmentEngine.
        output_file_path: Optional. Path to save the report. If None,
                          prints to console.
    """
    total_checks = len(results)
    passed_checks = sum(1 for r in results if r.get("status") == "passed")
    failed_checks = total_checks - passed_checks

    report_lines = [
        "======================",
        "Data Quality Report",
        "======================",
        "",
        "Summary:",
        "-------",
        f"Total Checks Run: {total_checks}",
        f"Checks Passed: {passed_checks}",
        f"Checks Failed: {failed_checks}",
        "",
        "Detailed Results:",
        "-----------------",
        "",
    ]

    for result in results:
        report_lines.append("--- Check Result ---")
        report_lines.append(f"Rule Type: {result.get('rule_type')}")
        # consistency_date_order_check 使用 column_a/column_b，优先展示
        if 'column_a' in result and 'column_b' in result:
            report_lines.append(f"Columns: {result.get('column_a')} / {result.get('column_b')}")
        else:
            report_lines.append(f"Column: {result.get('column')}")
        # Handle cases where 'expected_type' or 'actual_type' might be present (for data_type check)
        if 'expected_type' in result:
            report_lines.append(f"Expected Type: {result.get('expected_type')}")
        if 'actual_type' in result:
            report_lines.append(f"Actual Type: {result.get('actual_type')}")
        report_lines.append(f"Status: {result.get('status')}")
        report_lines.append(f"Message: {result.get('message')}")
        if result.get("details"):
            report_lines.append(f"Details: {result.get('details')}")
        report_lines.append("--------------------")
        report_lines.append("")

    report_string = "\n".join(report_lines)

    if output_file_path:
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(report_string)
            logger.info("报告已保存到: %s", output_file_path)
        except IOError as e:
            logger.error("写入报告文件失败 %s: %s", output_file_path, e)
            sys.stdout.write(report_string)
            sys.stdout.write("\n")
    else:
        sys.stdout.write(report_string)
        sys.stdout.write("\n")
