import pytest
import pandas as pd
from data_quality_tool.data_loader import load_csv_data

# Define paths to test data files
GOOD_DATA_PATH = "tests/sample_data/good_data.csv"
EMPTY_DATA_PATH = "tests/sample_data/empty_data.csv"
MALFORMED_DATA_PATH = "tests/sample_data/malformed_data.csv"
NON_EXISTENT_PATH = "tests/sample_data/non_existent.csv"

def test_load_csv_data_success():
    """Test loading a valid CSV file."""
    df = load_csv_data(GOOD_DATA_PATH)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["id", "name", "age", "email"]
    assert len(df) == 3

def test_load_csv_data_file_not_found(capsys):
    """Test loading a non-existent CSV file."""
    df = load_csv_data(NON_EXISTENT_PATH)
    assert df is None
    captured = capsys.readouterr()
    assert f"Error: File not found at path: {NON_EXISTENT_PATH}" in captured.out

def test_load_csv_data_empty_file(capsys):
    """Test loading an empty CSV file."""
    df = load_csv_data(EMPTY_DATA_PATH)
    assert df is None # pandas.errors.EmptyDataError makes read_csv return None in our wrapper
    captured = capsys.readouterr()
    assert f"Error: File is empty at path: {EMPTY_DATA_PATH}" in captured.out


def test_load_csv_data_malformed_file(capsys):
    """Test loading a malformed CSV file."""
    df = load_csv_data(MALFORMED_DATA_PATH)
    assert df is None # pandas.errors.ParserError makes read_csv return None in our wrapper
    captured = capsys.readouterr()
    assert f"Error: Could not parse CSV file at path: {MALFORMED_DATA_PATH}" in captured.out
