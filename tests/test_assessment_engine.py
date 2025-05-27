import pytest
import pandas as pd
from data_quality_tool.assessment_engine import AssessmentEngine

@pytest.fixture
def sample_df():
    data = {
        'id': [1, 2, 2, 3, None], # Includes duplicate and null
        'name': ['Alice', 'Bob', 'Bob', 'Charlie', 'David'], # Includes duplicate
        'age': [30, 24, 24, 35, 40], # All int
        'score': [85.5, 90.0, 90.0, 78.5, None] # Includes duplicate and null, float
    }
    return pd.DataFrame(data)

def test_assessment_engine_init(sample_df):
    engine = AssessmentEngine(sample_df)
    assert engine.dataframe is sample_df

def test_run_checks_empty_rules(sample_df):
    engine = AssessmentEngine(sample_df)
    results = engine.run_checks([])
    assert results == []

def test_run_checks_completeness(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "completeness", "column": "id"}]
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['rule_type'] == 'completeness'
    assert result['column'] == 'id'
    assert result['status'] == 'failed' # Due to one None
    assert result['details']['missing_count'] == 1
    assert result['details']['total_rows'] == 5

    rules_no_nulls = [{"type": "completeness", "column": "age"}]
    results_no_nulls = engine.run_checks(rules_no_nulls)
    assert results_no_nulls[0]['status'] == 'passed'


def test_run_checks_uniqueness(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "uniqueness", "column": "name"}]
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['rule_type'] == 'uniqueness'
    assert result['column'] == 'name'
    assert result['status'] == 'failed' # 'Bob' is duplicated
    assert result['details']['duplicate_count'] == 1 # Counts the second 'Bob' as a duplicate
    assert result['details']['total_rows'] == 5

    rules_no_duplicates = [{"type": "uniqueness", "column": "id"}] # Note: id has null, but uniqueness checks for duplicate non-nulls. Pandas duplicated() behavior needs to be kept in mind.
                                                                   # '2' is duplicated.
    results_no_duplicates = engine.run_checks(rules_no_duplicates)
    assert results_no_duplicates[0]['status'] == 'failed'
    assert results_no_duplicates[0]['details']['duplicate_count'] == 1


def test_run_checks_data_type(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "data_type", "column": "age", "expected_type": "int64"}]
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['rule_type'] == 'data_type'
    assert result['column'] == 'age'
    assert result['status'] == 'passed'
    assert result['actual_type'] == 'int64'

    rules_mismatch = [{"type": "data_type", "column": "age", "expected_type": "float64"}]
    results_mismatch = engine.run_checks(rules_mismatch)
    assert results_mismatch[0]['status'] == 'failed'
    assert results_mismatch[0]['actual_type'] == 'int64'

def test_run_checks_multiple_rules(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [
        {"type": "completeness", "column": "score"},
        {"type": "uniqueness", "column": "age"}, # age has duplicate 24
        {"type": "data_type", "column": "name", "expected_type": "object"}
    ]
    results = engine.run_checks(rules)
    assert len(results) == 3
    assert results[0]['rule_type'] == 'completeness'
    assert results[0]['column'] == 'score'
    assert results[0]['status'] == 'failed' # Has one None

    assert results[1]['rule_type'] == 'uniqueness'
    assert results[1]['column'] == 'age'
    assert results[1]['status'] == 'failed' # 24 is duplicated
    assert results[1]['details']['duplicate_count'] == 1

    assert results[2]['rule_type'] == 'data_type'
    assert results[2]['column'] == 'name'
    assert results[2]['status'] == 'passed'
    assert results[2]['actual_type'] == 'object'

def test_run_checks_missing_column_in_rule(sample_df, capsys):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "completeness"}] # Missing "column"
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error'
    assert "Missing 'column' in completeness rule." in result['message'] # Adjusted assertion

    rules_dt = [{"type": "data_type", "expected_type": "int64"}] # Missing "column"
    results_dt = engine.run_checks(rules_dt)
    assert len(results_dt) == 1
    result_dt = results_dt[0]
    assert result_dt['status'] == 'error'
    assert "Missing 'column' in data_type rule." in result_dt['message'] # Adjusted assertion


def test_run_checks_missing_expected_type_in_rule(sample_df): # Removed capsys, not used
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "data_type", "column": "age"}] # Missing "expected_type"
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error'
    assert "Missing 'expected_type' in data_type rule for column 'age'." in result['message'] # Adjusted assertion

def test_run_checks_column_not_in_dataframe(sample_df):
    engine = AssessmentEngine(sample_df)
    # This will be caught by the check function itself, not the engine's pre-validation
    rules = [{"type": "completeness", "column": "non_existent_column"}]
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error' # This is correct as check_completeness returns error
    assert "Column 'non_existent_column' not found in DataFrame." in result['message'] # Adjusted assertion

def test_run_checks_unsupported_rule_type(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "non_existent_rule", "column": "id"}]
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error'
    assert result['rule_type'] == 'non_existent_rule'
    assert "Unsupported rule type: 'non_existent_rule'." in result['message']

def test_run_checks_missing_rule_type(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [{"column": "id"}] # Missing "type"
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error'
    assert result['rule_type'] is None
    assert "Missing 'type' in rule definition." in result['message']


def test_run_checks_accuracy_range(sample_df):
    engine = AssessmentEngine(sample_df)

    # Passed scenario
    rules_passed = [{"type": "accuracy_range_check", "column": "age", "min_value": 20, "max_value": 40}]
    results_passed = engine.run_checks(rules_passed)
    assert len(results_passed) == 1
    result_passed = results_passed[0]
    assert result_passed['rule_type'] == 'accuracy_range_check'
    assert result_passed['column'] == 'age'
    assert result_passed['status'] == 'passed'
    assert result_passed['details']['valid_numeric_rows'] == 5 # All 5 are numeric
    assert result_passed['details']['non_numeric_rows'] == 0
    assert result_passed['details']['in_range_count'] == 5
    assert result_passed['details']['out_of_range_count'] == 0
    assert result_passed['details']['total_rows'] == 5

    # Failed scenario
    rules_failed = [{"type": "accuracy_range_check", "column": "age", "min_value": 30, "max_value": 35}]
    results_failed = engine.run_checks(rules_failed)
    assert len(results_failed) == 1
    result_failed = results_failed[0]
    assert result_failed['rule_type'] == 'accuracy_range_check'
    assert result_failed['column'] == 'age'
    assert result_failed['status'] == 'failed'
    # age: [30, 24, 24, 35, 40] -> all 5 are numeric
    # range [30, 35]:
    # In range: 30, 35 (2 values: Alice, Charlie)
    # Out of range: 24, 24, 40 (3 values: Bob, Bob, David)
    assert result_failed['details']['valid_numeric_rows'] == 5
    assert result_failed['details']['non_numeric_rows'] == 0
    assert result_failed['details']['in_range_count'] == 2 
    assert result_failed['details']['out_of_range_count'] == 3 
    assert result_failed['details']['total_rows'] == 5


    # Error scenario: Missing min_value
    rules_error_min = [{"type": "accuracy_range_check", "column": "age", "max_value": 35}]
    results_error_min = engine.run_checks(rules_error_min)
    assert len(results_error_min) == 1
    result_error_min = results_error_min[0]
    assert result_error_min['rule_type'] == 'accuracy_range_check'
    assert result_error_min['status'] == 'error'
    assert "Missing 'min_value' in accuracy_range_check rule for column 'age'." in result_error_min['message']

    # Error scenario: Missing max_value
    rules_error_max = [{"type": "accuracy_range_check", "column": "age", "min_value": 30}]
    results_error_max = engine.run_checks(rules_error_max)
    assert len(results_error_max) == 1
    result_error_max = results_error_max[0]
    assert result_error_max['rule_type'] == 'accuracy_range_check'
    assert result_error_max['status'] == 'error'
    assert "Missing 'max_value' in accuracy_range_check rule for column 'age'." in result_error_max['message']


@pytest.fixture
def date_order_df():
    data = {
        'id': [1, 2, 3, 4],
        'start_date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
        'end_date': pd.to_datetime(['2023-01-15', '2023-02-10', '2023-02-20', '2023-04-05']) # Third row has end_date < start_date
    }
    return pd.DataFrame(data)

def test_run_checks_consistency_date_order(date_order_df):
    engine = AssessmentEngine(date_order_df)

    # Passed scenario
    rules_passed = [{"type": "consistency_date_order_check", "column_a": "start_date", "column_b": "end_date"}]
    # Correcting the dataframe for a truly passed scenario for the first test
    passed_df_data = {
        'id': [1, 2, 3, 4],
        'start_date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
        'end_date': pd.to_datetime(['2023-01-15', '2023-02-10', '2023-03-15', '2023-04-05'])
    }
    passed_engine = AssessmentEngine(pd.DataFrame(passed_df_data))
    results_passed = passed_engine.run_checks(rules_passed)
    assert len(results_passed) == 1
    result_passed = results_passed[0]
    assert result_passed['rule_type'] == 'consistency_date_order_check'
    assert result_passed['column_a'] == 'start_date'
    assert result_passed['column_b'] == 'end_date'
    assert result_passed['status'] == 'passed'
    assert result_passed['details']['valid_date_pairs_count'] == 4
    assert result_passed['details']['invalid_date_pairs_count'] == 0
    assert result_passed['details']['order_satisfied_count'] == 4
    assert result_passed['details']['order_violated_count'] == 0
    assert result_passed['details']['total_rows'] == 4

    # Failed scenario (using original date_order_df which has one invalid order)
    results_failed = engine.run_checks(rules_passed) # Re-use rules_passed, but on original df
    assert len(results_failed) == 1
    result_failed = results_failed[0]
    assert result_failed['rule_type'] == 'consistency_date_order_check'
    assert result_failed['column_a'] == 'start_date'
    assert result_failed['column_b'] == 'end_date'
    assert result_failed['status'] == 'failed'
    # date_order_df:
    # 0: 2023-01-01, 2023-01-15 (OK)
    # 1: 2023-02-01, 2023-02-10 (OK)
    # 2: 2023-03-01, 2023-02-20 (VIOLATION)
    # 3: 2023-04-01, 2023-04-05 (OK)
    # All pairs are valid dates.
    assert result_failed['details']['valid_date_pairs_count'] == 4
    assert result_failed['details']['invalid_date_pairs_count'] == 0
    assert result_failed['details']['order_satisfied_count'] == 3
    assert result_failed['details']['order_violated_count'] == 1 # The third row
    assert result_failed['details']['total_rows'] == 4

    # Error scenario: Missing column_a
    rules_error_col_a = [{"type": "consistency_date_order_check", "column_b": "end_date"}]
    results_error_col_a = engine.run_checks(rules_error_col_a)
    assert len(results_error_col_a) == 1
    result_error_col_a = results_error_col_a[0]
    assert result_error_col_a['rule_type'] == 'consistency_date_order_check'
    assert result_error_col_a['status'] == 'error'
    assert "Missing 'column_a' in consistency_date_order_check rule." in result_error_col_a['message']

    # Error scenario: Missing column_b
    rules_error_col_b = [{"type": "consistency_date_order_check", "column_a": "start_date"}]
    results_error_col_b = engine.run_checks(rules_error_col_b)
    assert len(results_error_col_b) == 1
    result_error_col_b = results_error_col_b[0]
    assert result_error_col_b['rule_type'] == 'consistency_date_order_check'
    assert result_error_col_b['status'] == 'error'
    assert "Missing 'column_b' in consistency_date_order_check rule." in result_error_col_b['message']


def test_run_checks_validity_regex_match(sample_df):
    engine = AssessmentEngine(sample_df)

    # Passed scenario: All names start with an uppercase letter
    rules_passed = [{"type": "validity_regex_match_check", "column": "name", "pattern": r"^[A-Z][a-z]*$"}]
    results_passed = engine.run_checks(rules_passed)
    assert len(results_passed) == 1
    result_passed = results_passed[0]
    assert result_passed['rule_type'] == 'validity_regex_match_check'
    assert result_passed['column'] == 'name'
    assert result_passed['status'] == 'passed'
    # sample_df 'name': ['Alice', 'Bob', 'Bob', 'Charlie', 'David'] -> 5 applicable rows
    assert result_passed['details']['applicable_rows_count'] == 5
    assert result_passed['details']['matched_count'] == 5
    assert result_passed['details']['non_matched_count'] == 0
    assert result_passed['details']['total_rows'] == 5

    # Failed scenario: Only names starting with 'A'
    rules_failed = [{"type": "validity_regex_match_check", "column": "name", "pattern": r"^A"}]
    results_failed = engine.run_checks(rules_failed)
    assert len(results_failed) == 1
    result_failed = results_failed[0]
    assert result_failed['rule_type'] == 'validity_regex_match_check'
    assert result_failed['column'] == 'name'
    assert result_failed['status'] == 'failed'
    assert result_failed['details']['applicable_rows_count'] == 5
    assert result_failed['details']['matched_count'] == 1  # Alice
    assert result_failed['details']['non_matched_count'] == 4 # Bob, Bob, Charlie, David
    assert result_failed['details']['total_rows'] == 5

    # Error scenario: Missing pattern
    rules_error = [{"type": "validity_regex_match_check", "column": "name"}]
    results_error = engine.run_checks(rules_error)
    assert len(results_error) == 1
    result_error = results_error[0]
    assert result_error['rule_type'] == 'validity_regex_match_check'
    assert result_error['status'] == 'error'
    assert "Missing 'pattern' in validity_regex_match_check rule for column 'name'." in result_error['message']


@pytest.fixture
def timeliness_df():
    data = {
        'id': [1, 2, 3, 4],
        'event_date': pd.to_datetime(['2023-01-10', '2023-01-20', '2023-02-05', '2023-02-15'])
    }
    return pd.DataFrame(data)

def test_run_checks_timeliness_fixed_range(timeliness_df):
    engine = AssessmentEngine(timeliness_df)

    # Passed scenario
    rules_passed = [{
        "type": "timeliness_fixed_range_check",
        "column": "event_date",
        "start_date": "2023-01-01",
        "end_date": "2023-02-28"
    }]
    results_passed = engine.run_checks(rules_passed)
    assert len(results_passed) == 1
    result_passed = results_passed[0]
    assert result_passed['rule_type'] == 'timeliness_fixed_range_check'
    assert result_passed['column'] == 'event_date'
    assert result_passed['status'] == 'passed'
    assert result_passed['details']['parseable_column_dates_count'] == 4
    assert result_passed['details']['unparseable_column_dates_count'] == 0
    assert result_passed['details']['in_range_count'] == 4
    assert result_passed['details']['out_of_range_count'] == 0
    assert result_passed['details']['total_rows'] == 4

    # Failed scenario
    rules_failed = [{
        "type": "timeliness_fixed_range_check",
        "column": "event_date",
        "start_date": "2023-01-15", # This will make the first date (Jan 10) out of range
        "end_date": "2023-02-10"  # This will make the last date (Feb 15) out of range
    }]
    results_failed = engine.run_checks(rules_failed)
    assert len(results_failed) == 1
    result_failed = results_failed[0]
    assert result_failed['rule_type'] == 'timeliness_fixed_range_check'
    assert result_failed['column'] == 'event_date'
    assert result_failed['status'] == 'failed'
    assert result_failed['details']['parseable_column_dates_count'] == 4
    assert result_failed['details']['unparseable_column_dates_count'] == 0
    assert result_failed['details']['in_range_count'] == 2 # Jan 20, Feb 05
    assert result_failed['details']['out_of_range_count'] == 2 # Jan 10, Feb 15
    assert result_failed['details']['total_rows'] == 4

    # Error scenario: Missing start_date
    rules_error_start = [{
        "type": "timeliness_fixed_range_check",
        "column": "event_date",
        "end_date": "2023-02-28"
    }]
    results_error_start = engine.run_checks(rules_error_start)
    assert len(results_error_start) == 1
    result_error_start = results_error_start[0]
    assert result_error_start['rule_type'] == 'timeliness_fixed_range_check'
    assert result_error_start['status'] == 'error'
    assert "Missing 'start_date' in timeliness_fixed_range_check rule for column 'event_date'." in result_error_start['message']

    # Error scenario: Missing end_date
    rules_error_end = [{
        "type": "timeliness_fixed_range_check",
        "column": "event_date",
        "start_date": "2023-01-01"
    }]
    results_error_end = engine.run_checks(rules_error_end)
    assert len(results_error_end) == 1
    result_error_end = results_error_end[0]
    assert result_error_end['rule_type'] == 'timeliness_fixed_range_check'
    assert result_error_end['status'] == 'error'
    assert "Missing 'end_date' in timeliness_fixed_range_check rule for column 'event_date'." in result_error_end['message']
