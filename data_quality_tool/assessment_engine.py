import pandas as pd

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
            if rule.get("type") == "completeness":
                column_name = rule.get("column")
                if column_name:
                    # Assuming check_completeness is imported
                    # from .checks import check_completeness
                    # For now, let's define it here or ensure it's available
                    # For simplicity in this step, let's assume it's globally available
                    # or we will import it.
                    # To make it runnable, I will import it from the checks module
                    from .checks import check_completeness, check_uniqueness, check_data_type # Updated import
                    result = check_completeness(self.dataframe, column_name)
                    results.append(result)
                else:
                    results.append({
                        "rule_type": "completeness",
                        "column": None,
                        "status": "error",
                        "message": "Missing 'column' in completeness rule.",
                        "details": None,
                    })
            elif rule.get("type") == "uniqueness":
                column_name = rule.get("column")
                if column_name:
                    result = check_uniqueness(self.dataframe, column_name)
                    results.append(result)
                else:
                    results.append({
                        "rule_type": "uniqueness",
                        "column": None,
                        "status": "error",
                        "message": "Missing 'column' in uniqueness rule.",
                        "details": None,
                    })
            elif rule.get("type") == "data_type":
                column_name = rule.get("column")
                expected_type = rule.get("expected_type")
                if column_name and expected_type:
                    result = check_data_type(self.dataframe, column_name, expected_type)
                    results.append(result)
                elif not column_name:
                    results.append({
                        "rule_type": "data_type",
                        "column": None,
                        "expected_type": expected_type,
                        "status": "error",
                        "message": "Missing 'column' in data_type rule.",
                        "details": None,
                    })
                else: # Missing expected_type
                    results.append({
                        "rule_type": "data_type",
                        "column": column_name,
                        "expected_type": None,
                        "status": "error",
                        "message": "Missing 'expected_type' in data_type rule.",
                        "details": None,
                    })
            # Placeholder for other rule types
        return results
