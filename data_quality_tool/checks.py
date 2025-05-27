import pandas as pd

def check_completeness(dataframe: pd.DataFrame, column_name: str) -> dict:
    """
    Checks for missing values (NaN or None) in a specified column of a DataFrame.

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check for completeness.

    Returns:
        A dictionary containing the results of the completeness check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "completeness").
        - 'column': (str) The name of the column that was checked.
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        - 'details': (dict) Contains detailed statistics:
            - 'missing_count': (int) Number of missing values found.
            - 'total_processed_rows': (int) Total number of rows in the DataFrame.
    """
    if column_name not in dataframe.columns:
        return {
            "rule_type": "completeness",
            "column": column_name,
            "status": "error",
            "message": f"Column '{column_name}' not found in DataFrame.",
            "details": None,
        }

    missing_count = dataframe[column_name].isnull().sum()
    total_processed_rows = len(dataframe)

    if missing_count == 0:
        status = "passed"
        message = "No missing values found."
    else:
        status = "failed"
        message = f"Found {missing_count} missing values."

    return {
        "rule_type": "completeness",
        "column": column_name,
        "status": status,
        "message": message,
        "details": {"missing_count": int(missing_count), "total_rows": total_processed_rows},
    }

def check_uniqueness(dataframe: pd.DataFrame, column_name: str) -> dict:
    """
    Checks for duplicate values in a specified column of a DataFrame.

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check for uniqueness.

    Returns:
        A dictionary containing the results of the uniqueness check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "uniqueness").
        - 'column': (str) The name of the column that was checked.
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        - 'details': (dict) Contains detailed statistics:
            - 'duplicate_count': (int) Number of duplicate values found.
                                     Note: This counts occurrences beyond the first unique one.
            - 'total_processed_rows': (int) Total number of rows in the DataFrame.
    """
    if column_name not in dataframe.columns:
        return {
            "rule_type": "uniqueness",
            "column": column_name,
            "status": "error",
            "message": f"Column '{column_name}' not found in DataFrame.",
            "details": None,
        }

    duplicate_count = dataframe[column_name].duplicated().sum()
    total_processed_rows = len(dataframe)

    if duplicate_count == 0:
        status = "passed"
        message = "No duplicate values found."
    else:
        status = "failed"
        message = f"Found {duplicate_count} duplicate values."

    return {
        "rule_type": "uniqueness",
        "column": column_name,
        "status": status,
        "message": message,
        "details": {"duplicate_count": int(duplicate_count), "total_rows": total_processed_rows},
    }

def check_data_type(dataframe: pd.DataFrame, column_name: str, expected_type: str) -> dict:
    """
    Checks if the data type of a specified column matches the expected type.

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check.
        expected_type: The expected data type (e.g., 'int64', 'float64').

    Returns:
        A dictionary containing the results of the data type check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "data_type").
        - 'column': (str) The name of the column that was checked.
        - 'expected_type': (str) The expected data type.
        - 'actual_type': (str or None) The actual data type found, or None if column not found.
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        (No 'details' field for this check type by current design).
    """
    if column_name not in dataframe.columns:
        return {
            "rule_type": "data_type",
            "column": column_name,
            "expected_type": expected_type,
            "actual_type": None,
            "status": "error",
            "message": f"Column '{column_name}' not found in DataFrame.",
        }

    actual_type = str(dataframe[column_name].dtype)

    if actual_type == expected_type:
        status = "passed"
        message = "Data type matches expected type."
    else:
        status = "failed"
        message = "Data type mismatch."

    return {
        "rule_type": "data_type",
        "column": column_name,
        "expected_type": expected_type,
        "actual_type": actual_type,
        "status": status,
        "message": message,
    }

def check_accuracy_range(dataframe: pd.DataFrame, column_name: str, min_value: float, max_value: float) -> dict:
    """
    Checks if numeric values in a specified column fall within a given range [min_value, max_value].

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check.
        min_value: The minimum allowed value (inclusive).
        max_value: The maximum allowed value (inclusive).

    Returns:
        A dictionary containing the results of the accuracy range check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "accuracy_range_check").
        - 'column': (str) The name of the column that was checked.
        - 'min_value': (float) The specified minimum value for the range.
        - 'max_value': (float) The specified maximum value for the range.
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        - 'details': (dict or None) Contains detailed statistics if successful, else None:
            - 'total_processed_rows': (int) Total rows in the input DataFrame.
            - 'valid_numeric_rows': (int) Count of rows with valid numeric data in the column.
            - 'non_numeric_rows': (int) Count of original non-null rows that couldn't be converted to numeric.
            - 'in_range_count': (int) Count of numeric values within the specified range.
            - 'out_of_range_count': (int) Count of numeric values outside the specified range.
    """
    if column_name not in dataframe.columns:
        return {
            "rule_type": "accuracy_range_check",
            "column": column_name,
            "min_value": min_value,
            "max_value": max_value,
            "status": "error",
            "message": f"Column '{column_name}' not found in DataFrame.",
            "details": None,
        }

    if min_value > max_value:
        return {
            "rule_type": "accuracy_range_check",
            "column": column_name,
            "min_value": min_value,
            "max_value": max_value,
            "status": "error",
            "message": f"min_value ({min_value}) cannot be greater than max_value ({max_value}).",
            "details": None,
        }
        
    original_non_null_count = dataframe[column_name].count() # Counts non-NaN/None values
    
    # Attempt to convert to numeric, coercing errors to NaN
    numeric_column = pd.to_numeric(dataframe[column_name], errors='coerce')
    
    valid_numeric_rows = numeric_column.count() # Count of successfully converted numeric values
    non_numeric_rows = original_non_null_count - valid_numeric_rows # Original non-nulls that failed conversion

    # Rows that were originally NaN/None before conversion attempt
    # These are not counted in non_numeric_rows as they were not conversion failures
    # but rather pre-existing missing data.
    # total_rows = len(dataframe)
    # initially_null_or_nan = total_rows - original_non_null_count
    
    in_range_count = numeric_column[(numeric_column >= min_value) & (numeric_column <= max_value)].count()
    out_of_range_count = valid_numeric_rows - in_range_count
    
    status = "passed"
    message_parts = []

    if out_of_range_count > 0:
        status = "failed"
        message_parts.append(f"{out_of_range_count} values out of range.")
    else:
        message_parts.append("All numeric values are within range.")

    if non_numeric_rows > 0:
        status = "failed" # If non-numeric values are present, it's a failure for accuracy.
        message_parts.append(f"{non_numeric_rows} values were non-numeric.")
    
    if valid_numeric_rows == 0 and non_numeric_rows == 0 and original_non_null_count == 0 : # All values were initially null
         message = "Column contains only null values or is empty. No numeric data to check."
         # status can remain "passed" if no out-of-range or non-numeric values were found,
         # or be "failed" if the presence of only nulls is considered a failure for this check.
         # For now, let's assume if there's nothing to check against the range, it's not a 'fail' in terms of range.
         # However, non_numeric_rows > 0 would have already set it to failed.
         # If the column is entirely empty (original_non_null_count == 0), it means no data to check.
    elif valid_numeric_rows == 0 and non_numeric_rows > 0:
        message = f"No valid numeric data to check; {non_numeric_rows} values were non-numeric."
        status = "failed"
    elif valid_numeric_rows > 0 :
        message = f"{in_range_count} out of {valid_numeric_rows} numeric values are within the specified range [{min_value}, {max_value}]."
        if non_numeric_rows > 0:
            message += f" {non_numeric_rows} additional values were non-numeric."
        if out_of_range_count > 0: # This implies status is 'failed'
            pass # message already includes in_range and total numeric.
    else: # Only non-numeric or empty, handled by above.
        message = "No numeric data to assess against the range."
        if non_numeric_rows > 0:
            message = f"{non_numeric_rows} values were non-numeric and could not be assessed."
            status = "failed"


    return {
        'rule_type': 'accuracy_range_check',
        'column': column_name,
        'min_value': min_value,
        'max_value': max_value,
        'status': status,
        'message': message,
        'details': {
            'total_rows': len(dataframe), # Total rows in the input slice/dataframe
            'valid_numeric_rows': int(valid_numeric_rows),
            'non_numeric_rows': int(non_numeric_rows), # Values that were not NaN but couldn't be converted
            'in_range_count': int(in_range_count),
            'out_of_range_count': int(out_of_range_count),
        }
    }

def check_consistency_date_order(dataframe: pd.DataFrame, column_a_name: str, column_b_name: str) -> dict:
    """
    Checks if dates in column_a are before or the same as dates in column_b.

    Args:
        dataframe: The pandas DataFrame to check.
        column_a_name: The name of the first date column.
        column_b_name: The name of the second date column.

    Returns:
        A dictionary containing the results of the date order check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "consistency_date_order_check").
        - 'column_a': (str) The name of the first date column (start date).
        - 'column_b': (str) The name of the second date column (end date).
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        - 'details': (dict or None) Contains detailed statistics if successful, else None:
            - 'total_processed_rows': (int) Total rows in the input DataFrame.
            - 'valid_date_pairs_count': (int) Number of rows where both columns had parseable dates.
            - 'invalid_date_pairs_count': (int) Number of rows where at least one original non-null value
                                            failed to parse as a date.
            - 'order_satisfied_count': (int) Number of valid date pairs where date_a <= date_b.
            - 'order_violated_count': (int) Number of valid date pairs where date_a > date_b.
    """
    if column_a_name not in dataframe.columns or column_b_name not in dataframe.columns:
        missing_cols = []
        if column_a_name not in dataframe.columns:
            missing_cols.append(column_a_name)
        if column_b_name not in dataframe.columns:
            missing_cols.append(column_b_name)
        return {
            'rule_type': 'consistency_date_order_check',
            'column_a': column_a_name,
            'column_b': column_b_name,
            'status': 'error',
            'message': f"Column(s) '{', '.join(missing_cols)}' not found in DataFrame.",
            'details': None,
        }

    # Convert to datetime, coercing errors to NaT
    date_a = pd.to_datetime(dataframe[column_a_name], errors='coerce')
    date_b = pd.to_datetime(dataframe[column_b_name], errors='coerce')

    # Identify rows where both original values were not null/empty
    # This is tricky because pd.to_datetime will convert empty strings to NaT as well.
    # We are interested in pairs that *could* have been dates.
    # Let's consider rows where both series `date_a` and `date_b` are not NaT as valid pairs for comparison.
    # Rows that were originally something but failed parsing are NaT. Rows that were originally NaN/None are also NaT.
    
    # Valid date pairs are those where both date_a and date_b are not NaT after conversion
    valid_mask = date_a.notna() & date_b.notna()
    valid_date_pairs_count = valid_mask.sum()

    # Invalid date pairs: at least one was NaT after conversion, considering only rows that had *some* value initially.
    # This means we need to know if the original value was non-empty.
    # If original dataframe[column_a_name] or dataframe[column_b_name] was None or NaN, to_datetime makes it NaT.
    # If it was a non-parseable string, it also becomes NaT.
    # We're interested in rows where at least one conversion failed for a non-null original value.
    # The problem asks for "invalid_date_pairs_count: At least one column had unparseable date for a row"
    # This implies looking at rows that were not originally null in both spots.
    
    # Let's count rows where at least one date is NaT AFTER conversion
    initially_not_null_a = dataframe[column_a_name].notna()
    initially_not_null_b = dataframe[column_b_name].notna()
    
    # A pair is considered for validity if both had some initial non-null value.
    # Or, more simply, total_processed_rows - valid_date_pairs_count = rows with at least one NaT
    # total_rows = len(dataframe)
    # invalid_date_pairs_count = total_rows - valid_date_pairs_count
    # This is not quite right, as it includes rows that were initially null in one or both.
    # The problem asks for "invalid_date_pairs_count: At least one column had unparseable date for a row"
    # This usually means a non-null value that couldn't be parsed.
    
    # Rows where original data was present in both columns
    # original_pairs_present_mask = dataframe[column_a_name].notna() & dataframe[column_b_name].notna()
    # original_pairs_present_count = original_pairs_present_mask.sum()

    # Rows where conversion failed for at least one column (became NaT)
    # given that the original was not null.
    failed_conversion_a_mask = dataframe[column_a_name].notna() & date_a.isna()
    failed_conversion_b_mask = dataframe[column_b_name].notna() & date_b.isna()
    invalid_date_pairs_mask = failed_conversion_a_mask | failed_conversion_b_mask
    invalid_date_pairs_count = invalid_date_pairs_mask.sum()
    
    # Re-calculate valid_date_pairs_count based on initial non-nulls that successfully parsed
    # A pair is valid if both initial values were not null AND both parsed correctly.
    valid_date_pairs_count = (initially_not_null_a & initially_not_null_b & date_a.notna() & date_b.notna()).sum()
    
    # Adjust invalid_date_pairs_count to only count pairs where at least one was an unparseable non-null value,
    # and the other was either also an unparseable non-null value OR a parseable value.
    # This is essentially what invalid_date_pairs_mask.sum() calculated.

    order_satisfied_count = 0
    order_violated_count = 0

    if valid_date_pairs_count > 0:
        order_satisfied_count = (date_a[valid_mask] <= date_b[valid_mask]).sum()
        order_violated_count = valid_date_pairs_count - order_satisfied_count
    
    status = "passed"
    message_parts = []

    if order_violated_count > 0:
        status = "failed"
        message_parts.append(f"{order_violated_count} out of {valid_date_pairs_count} valid date pairs violated the order condition (A > B).")
    else:
        if valid_date_pairs_count > 0:
            message_parts.append(f"All {valid_date_pairs_count} valid date pairs satisfy the order condition (A <= B).")
        else:
            message_parts.append("No valid date pairs to compare.")

    if invalid_date_pairs_count > 0:
        status = "failed" # If there are unparseable dates, it's a failure for consistency.
        message_parts.append(f"{invalid_date_pairs_count} pairs had at least one invalid/unparseable date.")
    
    if not message_parts: # e.g. empty dataframe
        message = "No data to assess."
    else:
        message = " ".join(message_parts)


    return {
        'rule_type': 'consistency_date_order_check',
        'column_a': column_a_name,
        'column_b': column_b_name,
        'status': status,
        'message': message,
        'details': {
            'total_rows': len(dataframe),
            'valid_date_pairs_count': int(valid_date_pairs_count),
            'invalid_date_pairs_count': int(invalid_date_pairs_count),
            'order_satisfied_count': int(order_satisfied_count),
            'order_violated_count': int(order_violated_count),
        }
    }

import re # Import the 're' module for regular expressions

def check_validity_regex(dataframe: pd.DataFrame, column_name: str, pattern: str) -> dict:
    """
    Checks if string values in a specified column match a given regular expression.

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check.
        pattern: The regular expression pattern to match against.

    Returns:
        A dictionary containing the results of the regex match check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "validity_regex_match_check").
        - 'column': (str) The name of the column that was checked.
        - 'pattern': (str) The regex pattern used.
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        - 'details': (dict or None) Contains detailed statistics if successful, else None.
                     If regex compilation fails, 'details' contains {'regex_compile_error': str(e)}.
                     Otherwise, it contains:
                     - 'total_processed_rows': (int) Total rows in the input DataFrame.
                     - 'applicable_rows_count': (int) Count of original non-null values in the column.
                     - 'matched_count': (int) Count of applicable rows that matched the pattern.
                     - 'non_matched_count': (int) Count of applicable rows that did not match.
    """
    if column_name not in dataframe.columns:
        return {
            'rule_type': 'validity_regex_match_check',
            'column': column_name,
            'pattern': pattern,
            'status': 'error',
            'message': f"Column '{column_name}' not found in DataFrame.",
            'details': None,
        }

    try:
        compiled_regex = re.compile(pattern)
    except re.error as e:
        return {
            'rule_type': 'validity_regex_match_check',
            'column': column_name,
            'pattern': pattern,
            'status': 'error', # Changed from 'failed' to 'error' for invalid regex pattern itself
            'message': f"Invalid regular expression pattern: {e}",
            'details': {'regex_compile_error': str(e)},
        }

    # Keep track of original non-null values before converting to string
    # This is 'applicable_rows_count' - rows that are not NaN/None initially.
    original_non_null_mask = dataframe[column_name].notna()
    applicable_rows_count = original_non_null_mask.sum()
    
    # Convert the column to string type for regex operations.
    # Apply regex only to originally non-null values.
    # .astype(str) on a series containing None will convert None to 'None'.
    # We want to apply regex to string representations of original non-null values.
    
    # Create a series of strings from the original non-null values
    # If the column is already string type, this doesn't change much for valid strings.
    # If it's numeric/boolean, it converts them to their string representations.
    # If it contains actual NaN/None, these are filtered out by original_non_null_mask
    
    string_series_to_check = dataframe.loc[original_non_null_mask, column_name].astype(str)

    matched_count = 0
    if not string_series_to_check.empty: # Only proceed if there are non-null values to check
        # Using str.match requires the pattern to match at the beginning of the string.
        # For full string match, the pattern should be anchored, e.g., ^pattern$
        # Or use series.apply(lambda x: bool(compiled_regex.fullmatch(x)))
        # series.str.match by default checks if the *beginning* of the string matches.
        # For a "validity" check, we usually want the whole string to match.
        # So, the regex pattern itself should ensure this (e.g. using ^ and $).
        # Here, we will use str.match as requested, assuming the pattern is crafted accordingly.
        matched_count = string_series_to_check.str.match(compiled_regex).sum()
    
    non_matched_count = applicable_rows_count - matched_count

    status = "passed"
    message = f"{matched_count} out of {applicable_rows_count} applicable string values matched the pattern."

    if non_matched_count > 0:
        status = "failed"
        message = f"{matched_count} out of {applicable_rows_count} applicable string values matched the pattern. {non_matched_count} did not match."
    
    if applicable_rows_count == 0 and len(dataframe) > 0 : # All values were null/NaN
        message = "Column contains only null values or is empty. No applicable string data to check against pattern."
        status = "passed" # Or 'skipped' or 'n/a'. For now, passed if no non-matches.
    elif applicable_rows_count == 0 and len(dataframe) == 0: # Empty dataframe
        message = "No data to assess."
        status = "passed"

    return {
        'rule_type': 'validity_regex_match_check',
        'column': column_name,
        'pattern': pattern,
        'status': status,
        'message': message,
        'details': {
            'total_rows': len(dataframe),
            'applicable_rows_count': int(applicable_rows_count), # Count of original non-null values
            'matched_count': int(matched_count),
            'non_matched_count': int(non_matched_count),
        }
    }

def check_timeliness_fixed_range(dataframe: pd.DataFrame, column_name: str, start_date_str: str, end_date_str: str) -> dict:
    """
    Checks if dates in a specified column fall within a fixed date range [start_date, end_date].

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column containing dates to check.
        start_date_str: The start date of the allowed range (inclusive), as a string.
        end_date_str: The end date of the allowed range (inclusive), as a string.

    Returns:
        A dictionary containing the results of the timeliness check.
        The dictionary includes:
        - 'rule_type': (str) The type of check (e.g., "timeliness_fixed_range_check").
        - 'column': (str) The name of the column that was checked.
        - 'start_date': (str) The specified start date string for the range.
        - 'end_date': (str) The specified end date string for the range.
        - 'status': (str) "passed", "failed", or "error".
        - 'message': (str) A human-readable message describing the result.
        - 'details': (dict or None) Contains detailed statistics if successful, else None:
            - 'total_processed_rows': (int) Total rows in the input DataFrame.
            - 'parseable_column_dates_count': (int) Count of values in the column successfully parsed as dates.
            - 'unparseable_column_dates_count': (int) Count of original non-null values in the column
                                                that failed to parse as dates.
            - 'in_range_count': (int) Count of parseable dates within the specified range.
            - 'out_of_range_count': (int) Count of parseable dates outside the specified range.
    """
    if column_name not in dataframe.columns:
        return {
            'rule_type': 'timeliness_fixed_range_check',
            'column': column_name,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'status': 'error',
            'message': f"Column '{column_name}' not found in DataFrame.",
            'details': None,
        }

    try:
        start_date = pd.to_datetime(start_date_str)
        end_date = pd.to_datetime(end_date_str)
    except ValueError:
        return {
            'rule_type': 'timeliness_fixed_range_check',
            'column': column_name,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'status': 'error',
            'message': "Invalid start_date or end_date parameter format. Dates must be parseable.",
            'details': None,
        }

    if start_date > end_date:
        return {
            'rule_type': 'timeliness_fixed_range_check',
            'column': column_name,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'status': 'error',
            'message': "Start date cannot be after end date.",
            'details': None,
        }

    # Convert the target column to datetime, coercing errors to NaT
    column_dates = pd.to_datetime(dataframe[column_name], errors='coerce')

    parseable_column_dates_count = column_dates.notna().sum()
    unparseable_column_dates_count = dataframe[column_name].notna().sum() - parseable_column_dates_count
    # The above unparseable count is for non-null original values that failed parsing.
    # If we want total NaT after conversion, that's len(column_dates) - parseable_column_dates_count,
    # but the prompt implies unparseable from original non-nulls.

    in_range_count = 0
    out_of_range_count = 0

    if parseable_column_dates_count > 0:
        in_range_mask = (column_dates >= start_date) & (column_dates <= end_date)
        in_range_count = in_range_mask.sum()
        out_of_range_count = parseable_column_dates_count - in_range_count
    
    status = "passed"
    message_parts = []

    if out_of_range_count > 0:
        status = "failed"
        message_parts.append(f"{out_of_range_count} parseable dates were out of the specified range [{start_date.date()}-{end_date.date()}].")
    
    if unparseable_column_dates_count > 0:
        status = "failed"
        message_parts.append(f"{unparseable_column_dates_count} values in the column could not be parsed as dates.")

    if status == "passed" and parseable_column_dates_count > 0:
        message_parts.append(f"All {parseable_column_dates_count} parseable dates are within the specified range.")
    elif status == "passed" and parseable_column_dates_count == 0 and unparseable_column_dates_count == 0:
         message_parts.append("No parseable dates found in the column to check against the range.")
    
    if not message_parts:
        if len(dataframe) == 0:
            message = "No data to assess."
        elif parseable_column_dates_count == 0 and unparseable_column_dates_count == 0: # All original values were None/NaN
            message = "Column contains only null values or is empty. No dates to check."
        else: # Should be covered by other conditions
            message = "Assessment complete."
    else:
        message = " ".join(message_parts)


    return {
        'rule_type': 'timeliness_fixed_range_check',
        'column': column_name,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'status': status,
        'message': message,
        'details': {
            'total_rows': len(dataframe),
            'parseable_column_dates_count': int(parseable_column_dates_count),
            'unparseable_column_dates_count': int(unparseable_column_dates_count),
            'in_range_count': int(in_range_count),
            'out_of_range_count': int(out_of_range_count),
        }
    }
