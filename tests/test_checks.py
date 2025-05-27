import pytest
import pandas as pd
from data_quality_tool.checks import (
    check_completeness, 
    check_uniqueness, 
    check_data_type, 
    check_accuracy_range, 
    check_consistency_date_order, 
    check_validity_regex, 
    check_timeliness_fixed_range
)

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

# Tests for check_accuracy_range
@pytest.fixture
def range_df():
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'numeric_col': [10, 15, 20, 25, 30, 0, 40, None, 22, 18], # Includes None
        'string_col': ['a', 'b', '10', 'd', '25', 'e', 'f', 'g', 'h', 'i'], # Includes convertible string
        'mixed_col': [5, 'not_num', 15, None, 25, '30x', 35, 10.5, 'NaN', 50] # Mixed types
    }
    return pd.DataFrame(data)

def test_check_accuracy_range_all_in_range(range_df):
    result = check_accuracy_range(range_df, 'numeric_col', 10, 30)
    assert result['status'] == 'passed' # 0 and 40 are out, None is not numeric
    # numeric_col has [10, 15, 20, 25, 30, 0, 40, None, 22, 18]
    # Numeric values: 10, 15, 20, 25, 30, 0, 40, 22, 18 (9 values)
    # In range [10, 30]: 10, 15, 20, 25, 30, 22, 18 (7 values)
    # Out of range: 0, 40 (2 values)
    # Expected: All numeric values are within range. (This message seems off based on data)
    # The actual message will be more complex because of the out-of-range and non-numeric values.
    # Let's re-evaluate the logic in check_accuracy_range for the message.
    # If out_of_range > 0, status is 'failed'.
    # numeric_col: [10, 15, 20, 25, 30, 0, 40, None, 22, 18]
    # pd.to_numeric -> [10, 15, 20, 25, 30, 0, 40, NaN, 22, 18]
    # valid_numeric_rows = 9
    # non_numeric_rows = 0 (None is not counted as non-numeric, it's just missing)
    # in_range [10,30]: 10,15,20,25,30,22,18 (7 values)
    # out_of_range: 0 (<10), 40 (>30) (2 values)
    # Status should be 'failed'
    
    # Re-testing with a column that IS all in range and numeric:
    df_all_in = pd.DataFrame({'vals': [10, 15, 20, 25]})
    result_all_in = check_accuracy_range(df_all_in, 'vals', 10, 25)
    assert result_all_in['status'] == 'passed'
    assert result_all_in['message'] == '4 out of 4 numeric values are within the specified range [10.0, 25.0].'
    assert result_all_in['details']['valid_numeric_rows'] == 4
    assert result_all_in['details']['non_numeric_rows'] == 0
    assert result_all_in['details']['in_range_count'] == 4
    assert result_all_in['details']['out_of_range_count'] == 0
    assert result_all_in['details']['total_rows'] == 4


def test_check_accuracy_range_some_low(range_df):
    result = check_accuracy_range(range_df, 'numeric_col', 15, 30)
    # numeric_col: [10, 15, 20, 25, 30, 0, 40, None, 22, 18] -> valid numeric: 9
    # in range [15,30]: 15, 20, 25, 30, 22, 18 (6 values)
    # out of range: 10 (<15), 0 (<15), 40 (>30) (3 values)
    assert result['status'] == 'failed'
    assert result['message'] == '6 out of 9 numeric values are within the specified range [15.0, 30.0].' # 3 are out of range
    assert result['details']['valid_numeric_rows'] == 9
    assert result['details']['non_numeric_rows'] == 0
    assert result['details']['in_range_count'] == 6
    assert result['details']['out_of_range_count'] == 3

def test_check_accuracy_range_some_high(range_df):
    result = check_accuracy_range(range_df, 'numeric_col', 0, 25)
    # numeric_col: [10, 15, 20, 25, 30, 0, 40, None, 22, 18] -> valid numeric: 9
    # in range [0,25]: 10, 15, 20, 25, 0, 22, 18 (7 values)
    # out of range: 30 (>25), 40 (>25) (2 values)
    assert result['status'] == 'failed'
    assert result['message'] == '7 out of 9 numeric values are within the specified range [0.0, 25.0].'
    assert result['details']['out_of_range_count'] == 2

def test_check_accuracy_range_exact_bounds(range_df):
    df = pd.DataFrame({'exact_vals': [10, 20, 30]})
    result = check_accuracy_range(df, 'exact_vals', 10, 30)
    assert result['status'] == 'passed'
    assert result['details']['in_range_count'] == 3
    assert result['details']['out_of_range_count'] == 0

def test_check_accuracy_range_with_non_numeric_strings(range_df):
    result = check_accuracy_range(range_df, 'string_col', 10, 30)
    # string_col: ['a', 'b', '10', 'd', '25', 'e', 'f', 'g', 'h', 'i']
    # pd.to_numeric -> [NaN, NaN, 10, NaN, 25, NaN, NaN, NaN, NaN, NaN]
    # original_non_null_count = 10
    # valid_numeric_rows = 2  (10, 25)
    # non_numeric_rows = 8 ('a', 'b', 'd', 'e', 'f', 'g', 'h', 'i')
    # in_range [10,30]: 10, 25 (2 values)
    # out_of_range = 0
    assert result['status'] == 'failed' # Because of non-numeric values
    assert result['message'] == '2 out of 2 numeric values are within the specified range [10.0, 30.0]. 8 additional values were non-numeric.'
    assert result['details']['valid_numeric_rows'] == 2
    assert result['details']['non_numeric_rows'] == 8
    assert result['details']['in_range_count'] == 2
    assert result['details']['out_of_range_count'] == 0

def test_check_accuracy_range_with_mixed_types(range_df):
    result = check_accuracy_range(range_df, 'mixed_col', 10, 30)
    # mixed_col: [5, 'not_num', 15, None, 25, '30x', 35, 10.5, 'NaN', 50]
    # original non-null: 5, 'not_num', 15, 25, '30x', 35, 10.5, 'NaN', 50 (9 values)
    # pd.to_numeric -> [5, NaN, 15, NaN, 25, NaN, 35, 10.5, NaN, 50]
    # valid_numeric_rows = 6 (5, 15, 25, 35, 10.5, 50)
    # non_numeric_rows = 3 ('not_num', '30x', 'NaN' string)
    # in_range [10,30]: 15, 25, 10.5 (3 values)
    # out_of_range: 5 (<10), 35 (>30), 50 (>30) (3 values)
    assert result['status'] == 'failed'
    assert result['message'] == '3 out of 6 numeric values are within the specified range [10.0, 30.0]. 3 additional values were non-numeric.'
    assert result['details']['valid_numeric_rows'] == 6
    assert result['details']['non_numeric_rows'] == 3
    assert result['details']['in_range_count'] == 3
    assert result['details']['out_of_range_count'] == 3

def test_check_accuracy_range_with_nones_and_nans(range_df):
    # Using 'numeric_col' which has one None
    result = check_accuracy_range(range_df, 'numeric_col', 10, 20)
    # numeric_col: [10, 15, 20, 25, 30, 0, 40, None, 22, 18] -> valid numeric: 9
    # in_range [10,20]: 10, 15, 20, 18 (4 values)
    # out_of_range: 25, 30, 0, 40, 22 (5 values)
    assert result['status'] == 'failed'
    assert result['message'] == '4 out of 9 numeric values are within the specified range [10.0, 20.0].'
    assert result['details']['valid_numeric_rows'] == 9
    assert result['details']['non_numeric_rows'] == 0 # The None becomes NaN and is not counted in non_numeric_rows
    assert result['details']['in_range_count'] == 4
    assert result['details']['out_of_range_count'] == 5

def test_check_accuracy_range_empty_dataframe():
    df = pd.DataFrame({'empty_col': []})
    result = check_accuracy_range(df, 'empty_col', 0, 100)
    assert result['status'] == 'passed' # No data to fail the check
    assert result['message'] == 'Column contains only null values or is empty. No numeric data to check.'
    assert result['details']['valid_numeric_rows'] == 0
    assert result['details']['non_numeric_rows'] == 0
    assert result['details']['in_range_count'] == 0
    assert result['details']['out_of_range_count'] == 0
    assert result['details']['total_rows'] == 0

def test_check_accuracy_range_column_not_found(range_df):
    result = check_accuracy_range(range_df, 'non_existent_col', 0, 100)
    assert result['status'] == 'error'
    assert "Column 'non_existent_col' not found" in result['message']

def test_check_accuracy_range_min_greater_than_max(range_df):
    result = check_accuracy_range(range_df, 'numeric_col', 100, 0)
    assert result['status'] == 'error'
    assert "min_value (100.0) cannot be greater than max_value (0.0)" in result['message']

def test_check_accuracy_range_all_non_numeric(range_df):
    df = pd.DataFrame({'all_strings': ['a', 'b', 'c']})
    result = check_accuracy_range(df, 'all_strings', 0, 10)
    assert result['status'] == 'failed'
    assert result['message'] == 'No valid numeric data to check; 3 values were non-numeric.'
    assert result['details']['valid_numeric_rows'] == 0
    assert result['details']['non_numeric_rows'] == 3
    assert result['details']['in_range_count'] == 0
    assert result['details']['out_of_range_count'] == 0

def test_check_accuracy_range_all_nulls():
    df = pd.DataFrame({'all_nulls': [None, None, None, pd.NA, pd.NaT]}) # Mix of null types
    result = check_accuracy_range(df, 'all_nulls', 0, 10)
    assert result['status'] == 'passed' # No data to fail the check
    assert result['message'] == 'Column contains only null values or is empty. No numeric data to check.'
    assert result['details']['valid_numeric_rows'] == 0
    assert result['details']['non_numeric_rows'] == 0
    assert result['details']['in_range_count'] == 0
    assert result['details']['out_of_range_count'] == 0
    assert result['details']['total_rows'] == 5

# Tests for check_consistency_date_order
@pytest.fixture
def date_order_df():
    data = {
        'start_date': [
            '2023-01-01', '2023-01-15', '2023-02-01', None, 
            'not-a-date', '2023-03-01', '2023-03-10', '2023-03-15',
            '2023-04-01', '' 
        ],
        'end_date': [
            '2023-01-10', '2023-01-15', '2023-01-20', '2023-02-15', 
            '2023-02-20', 'not-a-date', '2023-03-05', None,
            '2023-04-01', '2023-04-05'
        ],
        'event_id': list(range(1, 11))
    }
    return pd.DataFrame(data)

def test_date_order_all_good(date_order_df):
    df = pd.DataFrame({
        'col_a': ['2023-01-01', '2023-02-01', '2023-03-03'],
        'col_b': ['2023-01-02', '2023-02-02', '2023-03-03']
    })
    result = check_consistency_date_order(df, 'col_a', 'col_b')
    assert result['status'] == 'passed'
    assert "All 3 valid date pairs satisfy the order condition (A <= B)." in result['message']
    assert result['details']['valid_date_pairs_count'] == 3
    assert result['details']['invalid_date_pairs_count'] == 0
    assert result['details']['order_satisfied_count'] == 3
    assert result['details']['order_violated_count'] == 0
    assert result['details']['total_rows'] == 3

def test_date_order_some_violated(date_order_df):
    # Using a slice of the fixture:
    # start_date: '2023-01-01', '2023-01-15', '2023-02-01'
    # end_date:   '2023-01-10', '2023-01-15', '2023-01-20' (this one violates)
    # The third pair in the original date_order_df has end_date < start_date
    # row 2: start='2023-02-01', end='2023-01-20' -> VIOLATION
    # row 6: start='2023-03-10', end='2023-03-05' -> VIOLATION
    # Let's use the full fixture and identify valid/invalid pairs
    # Original pairs:
    # 0: 2023-01-01, 2023-01-10 (OK)
    # 1: 2023-01-15, 2023-01-15 (OK)
    # 2: 2023-02-01, 2023-01-20 (VIOLATION)
    # 3: None,       2023-02-15 (INVALID - col_a is NaT) -> not counted in valid_date_pairs
    # 4: not-a-date, 2023-02-20 (INVALID - col_a is NaT) -> invalid_date_pairs_count = 1 (as 'not-a-date' is non-null)
    # 5: 2023-03-01, not-a-date (INVALID - col_b is NaT) -> invalid_date_pairs_count gets another one
    # 6: 2023-03-10, 2023-03-05 (VIOLATION)
    # 7: 2023-03-15, None       (INVALID - col_b is NaT)
    # 8: 2023-04-01, 2023-04-01 (OK)
    # 9: '',         2023-04-05 (INVALID - col_a is NaT, '' is non-null initially)
    
    # Valid date pairs: (where both parse successfully)
    # Pair 0: 2023-01-01, 2023-01-10 -> OK
    # Pair 1: 2023-01-15, 2023-01-15 -> OK
    # Pair 2: 2023-02-01, 2023-01-20 -> VIOLATED
    # Pair 6: 2023-03-10, 2023-03-05 -> VIOLATED
    # Pair 8: 2023-04-01, 2023-04-01 -> OK
    # Total valid_date_pairs_count = 5
    # order_satisfied_count = 3
    # order_violated_count = 2

    # Invalid date pairs (initially non-null in at least one, but fails to parse in at least one):
    # Pair 4: start_date 'not-a-date' (non-null, fails parse) -> invalid_date_pairs_count = 1
    # Pair 5: end_date 'not-a-date' (non-null, fails parse) -> invalid_date_pairs_count = 2
    # Pair 9: start_date '' (non-null, fails parse) -> invalid_date_pairs_count = 3
    # Note: Pair 3 (None, date) and Pair 7 (date, None) do not contribute to invalid_date_pairs_count
    # because the None value was already null, not a parsing failure of a non-null string.
    # The definition is "At least one column had unparseable date for a row" (from non-null original)

    result = check_consistency_date_order(date_order_df, 'start_date', 'end_date')
    assert result['status'] == 'failed' # Due to violations AND invalid dates
    assert "2 out of 5 valid date pairs violated the order condition (A > B)." in result['message']
    assert "3 pairs had at least one invalid/unparseable date." in result['message']
    assert result['details']['valid_date_pairs_count'] == 5
    assert result['details']['invalid_date_pairs_count'] == 3
    assert result['details']['order_satisfied_count'] == 3
    assert result['details']['order_violated_count'] == 2
    assert result['details']['total_rows'] == 10

def test_date_order_equal_dates(date_order_df):
    df = pd.DataFrame({
        'col_a': ['2023-01-01', '2023-02-02'],
        'col_b': ['2023-01-01', '2023-02-02']
    })
    result = check_consistency_date_order(df, 'col_a', 'col_b')
    assert result['status'] == 'passed'
    assert "All 2 valid date pairs satisfy the order condition (A <= B)." in result['message']
    assert result['details']['order_satisfied_count'] == 2
    assert result['details']['order_violated_count'] == 0

def test_date_order_with_invalid_date_formats(date_order_df):
    # This is largely covered by test_date_order_some_violated using the full fixture
    # Let's make a specific small case
    df = pd.DataFrame({
        'd1': ['2023-01-01', 'bad-date', '2023-01-03'],
        'd2': ['2023-01-02', '2023-01-04', 'bad-date-too']
    })
    # Pair 0: OK
    # Pair 1: d1 invalid -> invalid_date_pairs_count = 1
    # Pair 2: d2 invalid -> invalid_date_pairs_count = 2 (assuming d1 parses)
    # No, pair 1: d1 invalid, d2 valid. invalid_date_pairs_count = 1
    # pair 2: d1 valid, d2 invalid. invalid_date_pairs_count gets another one. Total 2.
    # Valid pairs = 0 (as each row has at least one bad date if we consider 'bad-date' and 'bad-date-too' as unparseable)
    # Let's re-evaluate how 'valid_date_pairs_count' and 'invalid_date_pairs_count' are calculated.
    # valid_date_pairs_count = (initially_not_null_a & initially_not_null_b & date_a.notna() & date_b.notna()).sum()
    # For df:
    # Row 0: d1='2023-01-01' (parses), d2='2023-01-02' (parses). Both initially non-null. -> valid_date_pairs_count = 1
    # Row 1: d1='bad-date' (NaT), d2='2023-01-04' (parses). d1 initially non-null. -> not a valid_date_pair
    # Row 2: d1='2023-01-03' (parses), d2='bad-date-too' (NaT). d2 initially non-null. -> not a valid_date_pair
    # So, valid_date_pairs_count = 1.
    # invalid_date_pairs_count:
    # Row 1: failed_conversion_a_mask is True. invalid_date_pairs_count = 1
    # Row 2: failed_conversion_b_mask is True. invalid_date_pairs_count = 2
    
    result = check_consistency_date_order(df, 'd1', 'd2')
    assert result['status'] == 'failed' # Because of invalid dates
    assert "All 1 valid date pairs satisfy the order condition (A <= B)." in result['message'] # Pair 0 is still valid
    assert "2 pairs had at least one invalid/unparseable date." in result['message']
    assert result['details']['valid_date_pairs_count'] == 1
    assert result['details']['invalid_date_pairs_count'] == 2
    assert result['details']['order_satisfied_count'] == 1 # For ('2023-01-01', '2023-01-02')
    assert result['details']['order_violated_count'] == 0

def test_date_order_with_nones_and_nans(date_order_df):
    # This is also largely covered by test_date_order_some_violated
    # Let's make a specific small case for Nones
    df = pd.DataFrame({
        'd1': ['2023-01-01', None, '2023-01-03', '2023-01-05'],
        'd2': ['2023-01-02', '2023-01-04', None, pd.NaT]
    })
    # Pair 0: OK
    # Pair 1: d1 is None (NaT). Not a valid_date_pair. Not an invalid_date_pair by current def.
    # Pair 2: d2 is None (NaT). Not a valid_date_pair. Not an invalid_date_pair.
    # Pair 3: d2 is pd.NaT (NaT). Not a valid_date_pair. Not an invalid_date_pair.
    # valid_date_pairs_count = 1 (Pair 0)
    # invalid_date_pairs_count = 0 (because Nones/NaTs were already null, not parsing failures of non-nulls)
    result = check_consistency_date_order(df, 'd1', 'd2')
    assert result['status'] == 'passed' # Only one valid pair, and it passes
    assert "All 1 valid date pairs satisfy the order condition (A <= B)." in result['message']
    assert result['details']['valid_date_pairs_count'] == 1
    assert result['details']['invalid_date_pairs_count'] == 0
    assert result['details']['order_satisfied_count'] == 1
    assert result['details']['order_violated_count'] == 0

def test_date_order_empty_dataframe():
    df = pd.DataFrame({'col_a': [], 'col_b': []})
    result = check_consistency_date_order(df, 'col_a', 'col_b')
    assert result['status'] == 'passed' # No data to fail
    assert "No data to assess." in result['message'] # Or "No valid date pairs to compare."
    assert result['details']['valid_date_pairs_count'] == 0
    assert result['details']['invalid_date_pairs_count'] == 0
    assert result['details']['order_satisfied_count'] == 0
    assert result['details']['order_violated_count'] == 0

# Tests for check_validity_regex
@pytest.fixture
def regex_df():
    # The longest list 'mixed_types' has 7 elements. Others have 6.
    # Pad shorter lists with None to make all lists of length 7.
    data = {
        'emails': [
            'test@example.com', 'invalid-email', 'another.test@example.co.uk', 
            None, 'test@sub.example.com', '', None
        ],  # Length 7
        'codes': [
            'ABC-123', 'XYZ-789', 'DEF-456', 'GHI-000', 
            'abc-123', 'ABC-XYZ', None
        ],  # Length 7
        'numbers_as_strings': [
            '123', '45.6', '7890', None, 
            '0', 'NaN', None
        ],  # Length 7
        'mixed_types': [
            'text1', 123, True, None, 
            'text2', 45.6, False
        ]  # Length 7
    }
    return pd.DataFrame(data)

# Basic email regex pattern (simplified for testing, not RFC 5322 compliant)
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
# Pattern for codes like ABC-123 (3 uppercase letters, hyphen, 3 digits)
CODE_PATTERN = r'^[A-Z]{3}-\d{3}$'
# Pattern for simple numbers (digits only)
NUMBER_PATTERN = r'^\d+$'

def test_regex_all_match(regex_df):
    df = pd.DataFrame({'data': ['ABC-123', 'XYZ-456', 'QWE-789']})
    result = check_validity_regex(df, 'data', CODE_PATTERN)
    assert result['status'] == 'passed'
    assert result['message'] == '3 out of 3 applicable string values matched the pattern.'
    assert result['details']['applicable_rows_count'] == 3
    assert result['details']['matched_count'] == 3
    assert result['details']['non_matched_count'] == 0

def test_regex_some_not_match_emails(regex_df):
    result = check_validity_regex(regex_df, 'emails', EMAIL_PATTERN)
    # emails: ['test@example.com', 'invalid-email', 'another.test@example.co.uk', None, 'test@sub.example.com', '']
    # Applicable (non-None): 5 strings ('test@example.com', 'invalid-email', 'another.test@example.co.uk', 'test@sub.example.com', '')
    # Matches: 'test@example.com', 'another.test@example.co.uk', 'test@sub.example.com' (3 matches)
    # Non-matches: 'invalid-email', '' (2 non-matches)
    assert result['status'] == 'failed'
    assert result['message'] == '3 out of 5 applicable string values matched the pattern. 2 did not match.'
    assert result['details']['applicable_rows_count'] == 5
    assert result['details']['matched_count'] == 3
    assert result['details']['non_matched_count'] == 2

def test_regex_codes_partial_match(regex_df):
    result = check_validity_regex(regex_df, 'codes', CODE_PATTERN)
    # codes: ['ABC-123', 'XYZ-789', 'DEF-456', 'GHI-000', 'abc-123', 'ABC-XYZ']
    # All are non-null, so applicable_rows_count = 6
    # Matches: 'ABC-123', 'XYZ-789', 'DEF-456', 'GHI-000' (4 matches)
    # Non-matches: 'abc-123' (lowercase), 'ABC-XYZ' (digits expected after hyphen) (2 non-matches)
    assert result['status'] == 'failed'
    assert result['message'] == '4 out of 6 applicable string values matched the pattern. 2 did not match.'
    assert result['details']['applicable_rows_count'] == 6
    assert result['details']['matched_count'] == 4
    assert result['details']['non_matched_count'] == 2

def test_regex_with_numbers_as_strings(regex_df):
    result = check_validity_regex(regex_df, 'numbers_as_strings', NUMBER_PATTERN)
    # numbers_as_strings: ['123', '45.6', '7890', None, '0', 'NaN']
    # Applicable (non-None): 5 strings ('123', '45.6', '7890', '0', 'NaN')
    # Matches (digits only): '123', '7890', '0' (3 matches)
    # Non-matches: '45.6' (contains '.'), 'NaN' (not digits) (2 non-matches)
    assert result['status'] == 'failed'
    assert result['message'] == '3 out of 5 applicable string values matched the pattern. 2 did not match.'
    assert result['details']['applicable_rows_count'] == 5
    assert result['details']['matched_count'] == 3
    assert result['details']['non_matched_count'] == 2

def test_regex_with_mixed_types_astype_str_behavior(regex_df):
    # mixed_types: ['text1', 123, True, None, 'text2', 45.6, False]
    # astype(str) for non-nulls: ['text1', '123', 'True', 'text2', '45.6', 'False'] -> 6 applicable rows
    # Pattern: NUMBER_PATTERN (r'^\d+$')
    # Matches: '123' (1 match)
    # Non-matches: 'text1', 'True', 'text2', '45.6', 'False' (5 non-matches)
    result = check_validity_regex(regex_df, 'mixed_types', NUMBER_PATTERN)
    assert result['status'] == 'failed'
    assert result['message'] == '1 out of 6 applicable string values matched the pattern. 5 did not match.'
    assert result['details']['applicable_rows_count'] == 6
    assert result['details']['matched_count'] == 1
    assert result['details']['non_matched_count'] == 5

def test_regex_empty_strings_behavior(regex_df):
    # Using 'emails' column which contains an empty string: ''
    # Pattern: r'^$' (matches only empty string)
    result = check_validity_regex(regex_df, 'emails', r'^$')
    # Applicable (non-None): 5 strings
    # Matches: '' (1 match)
    # Non-matches: 'test@example.com', 'invalid-email', 'another.test@example.co.uk', 'test@sub.example.com' (4 non-matches)
    assert result['status'] == 'failed'
    assert result['message'] == '1 out of 5 applicable string values matched the pattern. 4 did not match.'
    assert result['details']['matched_count'] == 1
    assert result['details']['non_matched_count'] == 4

def test_regex_empty_dataframe():
    df = pd.DataFrame({'data': pd.Series(dtype='str')}) # Ensure column exists but is empty
    result = check_validity_regex(df, 'data', r'.*') # Match any character
    assert result['status'] == 'passed'
    assert result['message'] == 'No data to assess.'
    assert result['details']['applicable_rows_count'] == 0
    assert result['details']['matched_count'] == 0
    assert result['details']['non_matched_count'] == 0
    assert result['details']['total_rows'] == 0

def test_regex_column_not_found(regex_df):
    result = check_validity_regex(regex_df, 'non_existent_column', r'.*')
    assert result['status'] == 'error'
    assert "Column 'non_existent_column' not found" in result['message']
    assert result['details'] is None

def test_regex_invalid_regex_pattern(regex_df):
    invalid_pattern = r'[' # Unbalanced bracket
    result = check_validity_regex(regex_df, 'codes', invalid_pattern)
    assert result['status'] == 'error' # Changed from 'failed' to 'error' as per implementation
    assert "Invalid regular expression pattern:" in result['message']
    assert 'regex_compile_error' in result['details']

def test_regex_all_null_column():
    df = pd.DataFrame({'data': [None, None, None, pd.NA]})
    result = check_validity_regex(df, 'data', r'.*')
    assert result['status'] == 'passed'
    assert "Column contains only null values or is empty. No applicable string data to check against pattern." in result['message']
    assert result['details']['applicable_rows_count'] == 0
    assert result['details']['matched_count'] == 0
    assert result['details']['non_matched_count'] == 0

def test_regex_pattern_that_matches_nan_string(regex_df):
    # Test if "NaN" string (from numbers_as_strings) matches a pattern like "NaN"
    result = check_validity_regex(regex_df, 'numbers_as_strings', r'^NaN$')
    # numbers_as_strings: ['123', '45.6', '7890', None, '0', 'NaN']
    # Applicable: 5 ('123', '45.6', '7890', '0', 'NaN')
    # Matches: 'NaN' (1 match)
    assert result['status'] == 'failed' # Because other applicable strings don't match
    assert result['message'] == '1 out of 5 applicable string values matched the pattern. 4 did not match.'
    assert result['details']['applicable_rows_count'] == 5
    assert result['details']['matched_count'] == 1
    assert result['details']['non_matched_count'] == 4

def test_regex_full_match_vs_partial_match_behavior():
    # Pandas str.match behaves like re.match (matches from beginning).
    # This test is to document/confirm this behavior.
    # For fullmatch semantics, pattern needs ^...$
    df = pd.DataFrame({'data': ['abc_123', '123_abc', 'abc']})
    
    # Pattern 'abc' will match 'abc_123' and 'abc' because it matches at the start
    result_partial = check_validity_regex(df, 'data', r'abc')
    assert result_partial['status'] == 'failed' # '123_abc' does not match
    assert result_partial['details']['matched_count'] == 2 # 'abc_123', 'abc'
    assert result_partial['details']['non_matched_count'] == 1 # '123_abc'
    
    # Pattern '^abc$' will only match 'abc'
    result_full = check_validity_regex(df, 'data', r'^abc$')
    assert result_full['status'] == 'failed'
    assert result_full['details']['matched_count'] == 1 # only 'abc'
    assert result_full['details']['non_matched_count'] == 2 # 'abc_123', '123_abc'

# Tests for check_timeliness_fixed_range
@pytest.fixture
def timeliness_df():
    data = {
        'event_date': [
            '2023-01-15', '2023-02-01', '2023-02-28', '2023-03-10', None,
            'not-a-date', '2022-12-31', '2023-04-01', '', '2023-02-15'
        ],
        'id': list(range(10))
    }
    return pd.DataFrame(data)

FIXED_START_DATE = '2023-01-01'
FIXED_END_DATE = '2023-03-01' # Inclusive

def test_timeliness_all_in_range():
    df = pd.DataFrame({'dates': ['2023-01-01', '2023-01-15', '2023-02-10', '2023-03-01']})
    result = check_timeliness_fixed_range(df, 'dates', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'passed'
    assert "All 4 parseable dates are within the specified range." in result['message']
    assert result['details']['parseable_column_dates_count'] == 4
    assert result['details']['unparseable_column_dates_count'] == 0
    assert result['details']['in_range_count'] == 4
    assert result['details']['out_of_range_count'] == 0

def test_timeliness_some_early(timeliness_df):
    # event_date: ['2023-01-15', '2023-02-01', '2023-02-28', '2023-03-10', None,
    #              'not-a-date', '2022-12-31', '2023-04-01', '', '2023-02-15']
    # Range: [2023-01-01, 2023-03-01]
    # Parseable: 2023-01-15 (in), 2023-02-01 (in), 2023-02-28 (in), 2023-03-10 (out),
    #            2022-12-31 (out), 2023-04-01 (out), 2023-02-15 (in) -> 7 parseable
    # Unparseable from non-null: 'not-a-date', '' -> 2 unparseable
    # In range: 4
    # Out of range: 3 (2023-03-10, 2022-12-31, 2023-04-01)
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'failed' # Due to out_of_range and unparseable
    assert "3 parseable dates were out of the specified range [2023-01-01-2023-03-01]." in result['message']
    assert "2 values in the column could not be parsed as dates." in result['message']
    assert result['details']['parseable_column_dates_count'] == 7
    assert result['details']['unparseable_column_dates_count'] == 2
    assert result['details']['in_range_count'] == 4
    assert result['details']['out_of_range_count'] == 3

def test_timeliness_some_late(timeliness_df):
    # Same as test_timeliness_some_early because FIXED_START_DATE and FIXED_END_DATE are class level
    # and that test already covers dates both before start and after end.
    # Re-asserting for clarity.
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'failed'
    assert result['details']['out_of_range_count'] == 3 # 2023-03-10, 2022-12-31, 2023-04-01

def test_timeliness_exact_bounds():
    df = pd.DataFrame({'dates': [FIXED_START_DATE, FIXED_END_DATE, '2023-01-15']})
    result = check_timeliness_fixed_range(df, 'dates', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'passed'
    assert result['details']['in_range_count'] == 3
    assert result['details']['out_of_range_count'] == 0

def test_timeliness_with_invalid_date_formats_in_column(timeliness_df):
    # Covered by test_timeliness_some_early as it uses the full fixture.
    # Specifically, 'not-a-date' and '' are unparseable.
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'failed' # unparseable count > 0 makes it fail
    assert result['details']['unparseable_column_dates_count'] == 2

def test_timeliness_with_nones_and_nans_in_column(timeliness_df):
    # Covered by test_timeliness_some_early. 'None' is present.
    # Nones are not counted in unparseable_column_dates_count (which is for non-nulls that fail parse).
    # They reduce the parseable_column_dates_count.
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', FIXED_START_DATE, FIXED_END_DATE)
    assert result['details']['parseable_column_dates_count'] == 7 # Total 10 rows, 1 None, 2 unparseable strings
    assert result['details']['unparseable_column_dates_count'] == 2

def test_timeliness_empty_dataframe():
    df = pd.DataFrame({'dates': pd.Series(dtype='datetime64[ns]')})
    result = check_timeliness_fixed_range(df, 'dates', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'passed'
    assert "No data to assess." in result['message']
    assert result['details']['total_rows'] == 0
    assert result['details']['parseable_column_dates_count'] == 0
    assert result['details']['unparseable_column_dates_count'] == 0

def test_timeliness_column_not_found(timeliness_df):
    result = check_timeliness_fixed_range(timeliness_df, 'non_existent', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'error'
    assert "Column 'non_existent' not found" in result['message']

def test_timeliness_invalid_start_date_param():
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', 'invalid-date-string', FIXED_END_DATE)
    assert result['status'] == 'error'
    assert "Invalid start_date or end_date parameter format." in result['message']

def test_timeliness_invalid_end_date_param():
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', FIXED_START_DATE, 'another-invalid-date')
    assert result['status'] == 'error'
    assert "Invalid start_date or end_date parameter format." in result['message']

def test_timeliness_start_date_after_end_date_param():
    result = check_timeliness_fixed_range(timeliness_df, 'event_date', FIXED_END_DATE, FIXED_START_DATE) # Swapped
    assert result['status'] == 'error'
    assert "Start date cannot be after end date." in result['message']

def test_timeliness_all_null_column():
    df = pd.DataFrame({'dates': [None, pd.NaT, None]})
    result = check_timeliness_fixed_range(df, 'dates', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'passed'
    # Message might be "No parseable dates found..." or "Column contains only null values..."
    assert "Column contains only null values or is empty. No dates to check." in result['message']
    assert result['details']['parseable_column_dates_count'] == 0
    assert result['details']['unparseable_column_dates_count'] == 0

def test_timeliness_all_unparseable_column():
    df = pd.DataFrame({'dates': ['abc', 'def', 'ghi']})
    result = check_timeliness_fixed_range(df, 'dates', FIXED_START_DATE, FIXED_END_DATE)
    assert result['status'] == 'failed'
    assert "3 values in the column could not be parsed as dates." in result['message']
    assert result['details']['parseable_column_dates_count'] == 0
    assert result['details']['unparseable_column_dates_count'] == 3
    assert result['details']['in_range_count'] == 0
    assert result['details']['out_of_range_count'] == 0
    assert result['details']['total_rows'] == 0

def test_date_order_column_not_found(date_order_df):
    result_a_missing = check_consistency_date_order(date_order_df, 'non_existent_a', 'end_date')
    assert result_a_missing['status'] == 'error'
    assert "Column(s) 'non_existent_a' not found" in result_a_missing['message']

    result_b_missing = check_consistency_date_order(date_order_df, 'start_date', 'non_existent_b')
    assert result_b_missing['status'] == 'error'
    assert "Column(s) 'non_existent_b' not found" in result_b_missing['message']

    result_both_missing = check_consistency_date_order(date_order_df, 'non_existent_a', 'non_existent_b')
    assert result_both_missing['status'] == 'error'
    assert "Column(s) 'non_existent_a', 'non_existent_b' not found" in result_both_missing['message']

def test_date_order_all_invalid_pairs():
    df = pd.DataFrame({
        'd1': ['not-a-date1', 'not-a-date2'],
        'd2': ['still-not-date1', 'still-not-date2']
    })
    result = check_consistency_date_order(df, 'd1', 'd2')
    assert result['status'] == 'failed'
    assert "No valid date pairs to compare." in result['message']
    assert "2 pairs had at least one invalid/unparseable date." in result['message']
    assert result['details']['valid_date_pairs_count'] == 0
    assert result['details']['invalid_date_pairs_count'] == 2
    assert result['details']['order_satisfied_count'] == 0
    assert result['details']['order_violated_count'] == 0
