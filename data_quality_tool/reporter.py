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
            print(f"Report successfully saved to {output_file_path}")
        except IOError as e:
            print(f"Error writing report to file {output_file_path}: {e}")
            print("Printing report to console instead:")
            print(report_string)
    else:
        print(report_string)
