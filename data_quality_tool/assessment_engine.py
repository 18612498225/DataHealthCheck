import pandas as pd
from .checks import (
    check_completeness,
    check_uniqueness,
    check_data_type,
    check_accuracy_range,
    check_consistency_date_order,
    check_validity_regex,
    check_timeliness_fixed_range # Added new import
)

class AssessmentEngine:
    """
    A class to perform data quality assessments on a pandas DataFrame.
    """
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initializes the AssessmentEngine with a pandas DataFrame.

        Args:
            dataframe: The pandas DataFrame to be assessed.
        """
        self.dataframe = dataframe
        self.check_functions = {
            "completeness": check_completeness,
            "uniqueness": check_uniqueness,
            "data_type": check_data_type,
            "accuracy_range_check": check_accuracy_range,
            "consistency_date_order_check": check_consistency_date_order,
            "validity_regex_match_check": check_validity_regex,
            "timeliness_fixed_range_check": check_timeliness_fixed_range, # Added new check
        }

    def run_checks(self, rules: list) -> list:
        """
        Runs a series of data quality checks based on the provided rules.

        Args:
            rules: A list of rules (dictionaries) defining the checks to perform.

        Returns:
            A list of dictionaries, where each dictionary represents the result
            of a data quality check.
        """
        results = []
        for rule in rules:
            rule_type = rule.get("type")
            column_name = rule.get("column")
            
            check_function = self.check_functions.get(rule_type)

            if not rule_type:
                results.append({
                    "rule_type": None,
                    "column": column_name,
                    "status": "error",
                    "message": "Missing 'type' in rule definition.",
                    "details": None,
                })
                continue

            if not check_function:
                results.append({
                    "rule_type": rule_type,
                    "column": column_name,
                    "status": "error",
                    "message": f"Unsupported rule type: '{rule_type}'.",
                    "details": None,
                })
                continue
            
            # General 'column' validation, skipped for rules that don't use a single 'column' parameter.
            # consistency_date_order_check uses column_a and column_b.
            if rule_type not in ["consistency_date_order_check"]: # Add other multi-column rules here in future
                if not column_name: # column_name is rule.get("column")
                    results.append({
                        "rule_type": rule_type,
                        "column": None,
                        "status": "error",
                        "message": f"Missing 'column' parameter in {rule_type} rule definition.",
                        "details": None,
                    })
                    continue

            # Specific argument handling for different check types
            if rule_type == "data_type":
                expected_type = rule.get("expected_type")
                if not expected_type:
                    results.append({
                        "rule_type": rule_type,
                        "column": column_name,
                        "expected_type": None,
                        "status": "error",
                        "message": f"Missing 'expected_type' in {rule_type} rule for column '{column_name}'.",
                        "details": None,
                    })
                    continue
                result = check_function(self.dataframe, column_name, expected_type)
            elif rule_type == "accuracy_range_check":
                min_value = rule.get("min_value")
                max_value = rule.get("max_value")
                
                if min_value is None or max_value is None: # Check if either is None
                    missing_params = []
                    if min_value is None:
                        missing_params.append("'min_value'")
                    if max_value is None:
                        missing_params.append("'max_value'")
                    
                    results.append({
                        "rule_type": rule_type,
                        "column": column_name,
                        "min_value": min_value,
                        "max_value": max_value,
                        "status": "error",
                        "message": f"Missing {', '.join(missing_params)} in {rule_type} rule for column '{column_name}'.",
                        "details": None,
                    })
                    continue
                # Attempt to convert to float, in case they are provided as strings in JSON
                try:
                    min_value = float(min_value)
                    max_value = float(max_value)
                except ValueError:
                    results.append({
                        "rule_type": rule_type,
                        "column": column_name,
                        "min_value": rule.get("min_value"), # Show original values
                        "max_value": rule.get("max_value"),
                        "status": "error",
                        "message": f"'min_value' and 'max_value' must be numbers for {rule_type} rule on column '{column_name}'.",
                        "details": None,
                    })
                    continue
                result = check_function(self.dataframe, column_name, min_value, max_value)
            elif rule_type == "consistency_date_order_check":
                column_a_name = rule.get("column_a") # Or a more generic name like 'first_column'
                column_b_name = rule.get("column_b") # Or 'second_column'

                if not column_a_name or not column_b_name:
                    missing_params = []
                    if not column_a_name:
                        missing_params.append("'column_a'")
                    if not column_b_name:
                        missing_params.append("'column_b'")
                    results.append({
                        "rule_type": rule_type,
                        "column_a": column_a_name,
                        "column_b": column_b_name,
                        "status": "error",
                        "message": f"Missing {', '.join(missing_params)} in {rule_type} rule.",
                        "details": None,
                    })
                    continue
                raw_result = check_function(self.dataframe, column_a_name, column_b_name)
                # Modify the result for reporting: Add a 'column' field with combined names.
                result = {
                    **raw_result, # Spread the original results from the check function
                    'column': f"{column_a_name} & {column_b_name}" 
                }
            elif rule_type == "validity_regex_match_check":
                pattern = rule.get("pattern")
                if not pattern: # pattern can be an empty string, but None or missing is an error
                    results.append({
                        "rule_type": rule_type,
                        "column": column_name, # column_name is already validated to exist by this point
                        "pattern": None,
                        "status": "error",
                        "message": f"Missing 'pattern' in {rule_type} rule for column '{column_name}'.",
                        "details": None,
                    })
                    continue
                result = check_function(self.dataframe, column_name, pattern)
            elif rule_type == "timeliness_fixed_range_check":
                start_date_str = rule.get("start_date")
                end_date_str = rule.get("end_date")
                
                if not start_date_str or not end_date_str:
                    missing_params = []
                    if not start_date_str:
                        missing_params.append("'start_date'")
                    if not end_date_str:
                        missing_params.append("'end_date'")
                    results.append({
                        "rule_type": rule_type,
                        "column": column_name,
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        "status": "error",
                        "message": f"Missing {', '.join(missing_params)} in {rule_type} rule for column '{column_name}'.",
                        "details": None,
                    })
                    continue
                result = check_function(self.dataframe, column_name, start_date_str, end_date_str)
            else: # For completeness, uniqueness, and other single-column checks
                # These checks are expected to return a dict that already includes 'column': column_name
                result = check_function(self.dataframe, column_name)
            
            results.append(result)
        return results
