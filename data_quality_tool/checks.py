import pandas as pd

def check_completeness(dataframe: pd.DataFrame, column_name: str) -> dict:
    """
    Checks for missing values (NaN or None) in a specified column of a DataFrame.

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check for completeness.

    Returns:
        A dictionary containing the results of the completeness check.
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
    total_rows = len(dataframe)

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
        "details": {"missing_count": int(missing_count), "total_rows": total_rows},
    }

def check_uniqueness(dataframe: pd.DataFrame, column_name: str) -> dict:
    """
    Checks for duplicate values in a specified column of a DataFrame.

    Args:
        dataframe: The pandas DataFrame to check.
        column_name: The name of the column to check for uniqueness.

    Returns:
        A dictionary containing the results of the uniqueness check.
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
    total_rows = len(dataframe)

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
        "details": {"duplicate_count": int(duplicate_count), "total_rows": total_rows},
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
