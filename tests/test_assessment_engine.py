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
    assert "Missing 'column' in completeness rule" in result['message']

    rules_dt = [{"type": "data_type", "expected_type": "int64"}] # Missing "column"
    results_dt = engine.run_checks(rules_dt)
    assert len(results_dt) == 1
    result_dt = results_dt[0]
    assert result_dt['status'] == 'error'
    assert "Missing 'column' in data_type rule" in result_dt['message']


def test_run_checks_missing_expected_type_in_rule(sample_df, capsys):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "data_type", "column": "age"}] # Missing "expected_type"
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error'
    assert "Missing 'expected_type' in data_type rule" in result['message']

def test_run_checks_column_not_in_dataframe(sample_df):
    engine = AssessmentEngine(sample_df)
    rules = [{"type": "completeness", "column": "non_existent_column"}]
    results = engine.run_checks(rules)
    assert len(results) == 1
    result = results[0]
    assert result['status'] == 'error'
    assert "Column 'non_existent_column' not found" in result['message']
