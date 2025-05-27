import pytest
import pandas as pd
from data_quality_tool.checks import check_completeness, check_uniqueness, check_data_type

# Sample DataFrames for testing
@pytest.fixture
def good_df():
    data = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [30, 24, 35],
        'score': [85.5, 90.0, 78.5]
    }
    return pd.DataFrame(data)

@pytest.fixture
def nulls_df():
    data = {'id': [1, 2, 3], 'name': ['A', None, 'C'], 'value': [100, 200, None]}
    return pd.DataFrame(data)

@pytest.fixture
def duplicates_df():
    data = {'id': [1, 2, 2, 3], 'category': ['X', 'Y', 'Y', 'Z']}
    return pd.DataFrame(data)

# Tests for check_completeness
def test_check_completeness_no_nulls(good_df):
    result = check_completeness(good_df, 'name')
    assert result['status'] == 'passed'
    assert result['message'] == 'No missing values found.'
    assert result['details']['missing_count'] == 0
    assert result['details']['total_rows'] == 3

def test_check_completeness_with_nulls(nulls_df):
    result = check_completeness(nulls_df, 'name')
    assert result['status'] == 'failed'
    assert "Found 1 missing values." in result['message'] # Allow for slight variations
    assert result['details']['missing_count'] == 1
    assert result['details']['total_rows'] == 3

def test_check_completeness_all_nulls(nulls_df):
    # Create a column with all nulls for testing
    all_nulls_df = pd.DataFrame({'all_null_col': [None, None, None]})
    result = check_completeness(all_nulls_df, 'all_null_col')
    assert result['status'] == 'failed'
    assert "Found 3 missing values." in result['message']
    assert result['details']['missing_count'] == 3
    assert result['details']['total_rows'] == 3


def test_check_completeness_column_not_found(good_df):
    result = check_completeness(good_df, 'non_existent_column')
    assert result['status'] == 'error'
    assert "Column 'non_existent_column' not found" in result['message']

# Tests for check_uniqueness
def test_check_uniqueness_no_duplicates(good_df):
    result = check_uniqueness(good_df, 'id')
    assert result['status'] == 'passed'
    assert result['message'] == 'No duplicate values found.'
    assert result['details']['duplicate_count'] == 0
    assert result['details']['total_rows'] == 3

def test_check_uniqueness_with_duplicates(duplicates_df):
    result = check_uniqueness(duplicates_df, 'id') # 'id' column in duplicates_df has a duplicate '2'
    assert result['status'] == 'failed'
    assert "Found 1 duplicate values." in result['message'] # pandas .duplicated() marks the second occurrence as duplicate
    assert result['details']['duplicate_count'] == 1 # Corrected based on how duplicated() works
    assert result['details']['total_rows'] == 4

def test_check_uniqueness_column_not_found(good_df):
    result = check_uniqueness(good_df, 'non_existent_column')
    assert result['status'] == 'error'
    assert "Column 'non_existent_column' not found" in result['message']

# Tests for check_data_type
def test_check_data_type_match_int(good_df):
    result = check_data_type(good_df, 'age', 'int64')
    assert result['status'] == 'passed'
    assert result['message'] == 'Data type matches expected type.'
    assert result['actual_type'] == 'int64'

def test_check_data_type_match_float(good_df):
    result = check_data_type(good_df, 'score', 'float64')
    assert result['status'] == 'passed'
    assert result['actual_type'] == 'float64'

def test_check_data_type_match_object_string(good_df):
    # Pandas often uses 'object' for strings
    result = check_data_type(good_df, 'name', 'object')
    assert result['status'] == 'passed'
    assert result['actual_type'] == 'object'

def test_check_data_type_mismatch(good_df):
    result = check_data_type(good_df, 'age', 'float64') # Expect float, but it's int
    assert result['status'] == 'failed'
    assert result['message'] == 'Data type mismatch.'
    assert result['actual_type'] == 'int64'
    assert result['expected_type'] == 'float64'

def test_check_data_type_column_not_found(good_df):
    result = check_data_type(good_df, 'non_existent_column', 'int64')
    assert result['status'] == 'error'
    assert "Column 'non_existent_column' not found" in result['message']

def test_check_data_type_with_nulls(nulls_df):
    # Test data type check on a column that contains nulls
    # The presence of nulls shouldn't prevent type checking of the column itself
    # For 'value' column, if it had non-nulls, they might be float or object depending on pd.read_csv.
    # Let's assume it's read as float64 due to the NaN.
    # If we load data_with_nulls.csv, 'value' column will be float64 because of NaN
    loaded_nulls_df = pd.read_csv("tests/sample_data/data_with_nulls.csv")

    result = check_data_type(loaded_nulls_df, 'value', 'float64')
    assert result['status'] == 'passed'
    assert result['actual_type'] == 'float64'

    result_mismatch = check_data_type(loaded_nulls_df, 'value', 'int64')
    assert result_mismatch['status'] == 'failed'
    assert result_mismatch['actual_type'] == 'float64'
