import argparse
import json
import sys # Import sys for exiting
import pandas as pd # Though not directly used, good for consistency

# Project specific imports
from data_quality_tool.data_loader import load_csv_data
from data_quality_tool.assessment_engine import AssessmentEngine
from data_quality_tool.reporter import generate_text_report

def main():
    parser = argparse.ArgumentParser(description="Data Quality Assessment Tool")
    parser.add_argument("data_file", help="Path to the input CSV data file.")
    parser.add_argument("rules_file", help="Path to the JSON file containing assessment rules.")
    parser.add_argument(
        "--output_report_file",
        "-o",
        help="Optional path to save the text report. Prints to console if not provided.",
        default=None,
    )

    args = parser.parse_args()

    # Load rules
    try:
        with open(args.rules_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
    except FileNotFoundError:
        print(f"Error: Rules file not found at {args.rules_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from rules file {args.rules_file}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while loading rules: {e}")
        sys.exit(1)
        
    if not isinstance(rules, list):
        print(f"Error: Rules file {args.rules_file} must contain a JSON list of rules.")
        sys.exit(1)

    # Load data
    dataframe = load_csv_data(args.data_file)
    if dataframe is None:
        # Error message is printed by load_csv_data
        sys.exit(1)

    # Perform assessment
    engine = AssessmentEngine(dataframe)
    results = engine.run_checks(rules)

    # Generate report
    generate_text_report(results, args.output_report_file)

if __name__ == "__main__":
    main()
