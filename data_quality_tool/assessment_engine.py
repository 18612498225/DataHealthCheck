import pandas as pd
from .checks import check_completeness, check_uniqueness, check_data_type

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

            if not column_name:
                results.append({
                    "rule_type": rule_type,
                    "column": None,
                    "status": "error",
                    "message": f"Missing 'column' in {rule_type} rule.",
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
            else: # For completeness and uniqueness
                result = check_function(self.dataframe, column_name)
            
            results.append(result)
        return results
