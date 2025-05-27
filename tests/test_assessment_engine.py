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

def test_run_checks_consistency_date_order(sample_df): # Using existing sample_df, will add date columns
    # Add date columns to the sample_df for this test
    sample_df['start_date'] = pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-05', '2023-01-01'])
    sample_df['end_date'] = pd.to_datetime(['2023-01-02', '2023-01-02', '2022-12-31', '2023-01-04', '2023-01-03']) # One violation, one earlier end
    
    engine = AssessmentEngine(sample_df)
    rules = [{
        "type": "consistency_date_order_check", 
        "column_a": "start_date", 
        "column_b": "end_date"
    }]
    results = engine.run_checks(rules)
    
    assert len(results) == 1
    result = results[0]
    
    assert result['rule_type'] == 'consistency_date_order_check'
    # Verify the new 'column' format
    expected_column_name = f"{rules[0]['column_a']} & {rules[0]['column_b']}"
    assert result['column'] == expected_column_name
    
    # Check that the "Missing 'column' parameter" error is NOT present
    if 'message' in result and result['message'] is not None: # Check if message key exists and is not None
     assert "Missing 'column' parameter" not in result['message']

    # Based on the data:
    # Pair 0: 2023-01-01 <= 2023-01-02 (OK)
    # Pair 1: 2023-01-01 <= 2023-01-02 (OK)
    # Pair 2: 2023-01-01 > 2022-12-31 (VIOLATION)
    # Pair 3: 2023-01-05 > 2023-01-04 (VIOLATION)
    # Pair 4: 2023-01-01 <= 2023-01-03 (OK)
    # valid_date_pairs_count = 5
    # order_satisfied_count = 3
    # order_violated_count = 2
    assert result['status'] == 'failed' # Because there are violations
    assert result['details']['valid_date_pairs_count'] == 5
    assert result['details']['order_violated_count'] == 2
    assert result['details']['order_satisfied_count'] == 3
    
    # Test with missing column_a in rule definition
    rules_missing_col_a = [{"type": "consistency_date_order_check", "column_b": "end_date"}]
    results_missing_col_a = engine.run_checks(rules_missing_col_a)
    assert len(results_missing_col_a) == 1
    result_missing_col_a = results_missing_col_a[0]
    assert result_missing_col_a['status'] == 'error'
    assert "Missing ''column_a'' in consistency_date_order_check rule." in result_missing_col_a['message']
    # The 'column' field in case of error might be tricky, let's see what the engine does.
    # The engine currently sets 'column_a' and 'column_b' fields in the error dict.
    # The special formatting of 'column' is only for successful calls to the check function.
    # So, 'column' might be None or not present if the rule definition itself is bad.
    # Let's check the current engine behavior for the error case:
    # It appends: {"rule_type": rule_type, "column_a": column_a_name, "column_b": column_b_name, "status": "error", ...}
    # The reporter will then try to access 'column', which might be None.
    # This is acceptable, as the error is about the rule definition, not the column data.
    # The test should ensure 'column' is not the combined name for this error case.
    assert result_missing_col_a.get('column') != f"None & end_date"


    # Test with one of the date columns not existing in DataFrame (handled by check function)
    rules_col_not_in_df = [{
        "type": "consistency_date_order_check", 
        "column_a": "start_date_typo", 
        "column_b": "end_date"
    }]
    results_col_not_in_df = engine.run_checks(rules_col_not_in_df)
    assert len(results_col_not_in_df) == 1
    result_col_not_in_df = results_col_not_in_df[0]
    assert result_col_not_in_df['status'] == 'error'
    assert "Column(s) 'start_date_typo' not found in DataFrame." in result_col_not_in_df['message']
    # Check the 'column' field in this specific error case (coming from the check function directly)
    # The engine adds the f-string column if the check function was successfully called and returned.
    # If the check function returns an error status (like column not found), it might not have 'column_a'/'column_b'
    # or the engine still formats 'column'.
    # Current implementation: check_function returns the error, engine formats 'column'.
    expected_error_column_name = f"start_date_typo & end_date"
    assert result_col_not_in_df['column'] == expected_error_column_name
