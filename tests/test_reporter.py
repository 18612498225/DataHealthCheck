import pytest
from data_quality_tool.reporter import generate_text_report
import os

@pytest.fixture
def sample_results_good():
    return [
        {
            "rule_type": "completeness", "column": "id", "status": "passed",
            "message": "No missing values found.",
            "details": {"missing_count": 0, "total_rows": 3},
        },
        {
            "rule_type": "uniqueness", "column": "id", "status": "passed",
            "message": "No duplicate values found.",
            "details": {"duplicate_count": 0, "total_rows": 3},
        },
        {
            "rule_type": "data_type", "column": "age", "expected_type": "int64",
            "actual_type": "int64", "status": "passed",
            "message": "Data type matches expected type.",
        },
    ]

@pytest.fixture
def sample_results_mixed():
    return [
        {
            "rule_type": "completeness", "column": "email", "status": "failed",
            "message": "Found 1 missing values.",
            "details": {"missing_count": 1, "total_rows": 4},
        },
        {
            "rule_type": "uniqueness", "column": "name", "status": "failed",
            "message": "Found 1 duplicate values.",
            "details": {"duplicate_count": 1, "total_rows": 4},
        },
        {
            "rule_type": "data_type", "column": "age", "expected_type": "int64",
            "actual_type": "object", "status": "failed",
            "message": "Data type mismatch.",
        },
        {
            "rule_type": "completeness", "column": "id", "status": "passed",
            "message": "No missing values found.",
            "details": {"missing_count": 0, "total_rows": 4},
        },
        {
            "rule_type": "data_type", "column": "non_existent_col", "expected_type": "int64",
            "actual_type": None, "status": "error",
            "message": "Column 'non_existent_col' not found in DataFrame.",
        }
    ]

def test_generate_text_report_console_output_good(capsys, sample_results_good):
    generate_text_report(sample_results_good)
    captured = capsys.readouterr()
    
    assert "Data Quality Report" in captured.out
    assert "Summary:" in captured.out
    assert "Total Checks Run: 3" in captured.out
    assert "Checks Passed: 3" in captured.out
    assert "Checks Failed: 0" in captured.out
    assert "Detailed Results:" in captured.out
    assert "Rule Type: completeness" in captured.out
    assert "Column: id" in captured.out
    assert "Status: passed" in captured.out
    assert "Details: {'missing_count': 0, 'total_rows': 3}" in captured.out # Check one detail

def test_generate_text_report_console_output_mixed(capsys, sample_results_mixed):
    generate_text_report(sample_results_mixed)
    captured = capsys.readouterr()
    
    assert "Data Quality Report" in captured.out
    assert "Summary:" in captured.out
    assert "Total Checks Run: 5" in captured.out
    assert "Checks Passed: 1" in captured.out # Only one explicitly passed
    assert "Checks Failed: 4" in captured.out # 3 failed, 1 error (errors count as not passed for summary)
    
    assert "Rule Type: completeness" in captured.out
    assert "Column: email" in captured.out
    assert "Status: failed" in captured.out
    assert "Details: {'missing_count': 1, 'total_rows': 4}" in captured.out
    
    assert "Rule Type: uniqueness" in captured.out
    assert "Column: name" in captured.out
    assert "Status: failed" in captured.out
    assert "Details: {'duplicate_count': 1, 'total_rows': 4}" in captured.out

    assert "Rule Type: data_type" in captured.out
    assert "Column: age" in captured.out
    assert "Expected Type: int64" in captured.out
    assert "Actual Type: object" in captured.out
    assert "Status: failed" in captured.out
    
    assert "Column: non_existent_col" in captured.out
    assert "Status: error" in captured.out
    assert "Message: Column 'non_existent_col' not found in DataFrame." in captured.out


def test_generate_text_report_file_output(tmp_path, sample_results_mixed):
    report_file = tmp_path / "report.txt"
    generate_text_report(sample_results_mixed, str(report_file))

    assert report_file.exists()
    content = report_file.read_text()

    assert "Data Quality Report" in content
    assert "Summary:" in content
    assert "Total Checks Run: 5" in content
    assert "Checks Passed: 1" in content
    assert "Checks Failed: 4" in content # 3 failed + 1 error
    assert "Rule Type: completeness" in content
    assert "Column: email" in content
    assert "Status: failed" in content

def test_generate_text_report_empty_results(capsys):
    generate_text_report([])
    captured = capsys.readouterr()
    assert "Data Quality Report" in captured.out
    assert "Total Checks Run: 0" in captured.out
    assert "Checks Passed: 0" in captured.out
    assert "Checks Failed: 0" in captured.out
    assert "Detailed Results:" in captured.out
    # Ensure no individual check details are printed
    assert "--- Check Result ---" not in captured.out

def test_generate_text_report_file_output_io_error(capsys, sample_results_good, monkeypatch):
    # Simulate an IOError when writing to file
    def mock_open_raises_io_error(*args, **kwargs):
        raise IOError("Simulated write error")

    monkeypatch.setattr("builtins.open", mock_open_raises_io_error)
    
    # Path that would normally be writable, but open is mocked
    report_file_path = "some_dir/report.txt" 
    
    generate_text_report(sample_results_good, report_file_path)
    
    captured = capsys.readouterr()
    assert f"Error writing report to file {report_file_path}: Simulated write error" in captured.out
    assert "Printing report to console instead:" in captured.out
    # Check if the report content is then printed to console
    assert "Data Quality Report" in captured.out
    assert "Total Checks Run: 3" in captured.out
    assert "Checks Passed: 3" in captured.out
    assert "Checks Failed: 0" in captured.out
