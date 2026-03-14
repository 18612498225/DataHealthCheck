import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

# Add project root for data_quality_tool import (shared with CLI)
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from data_quality_tool.data_loader import load_csv_data

try:
    import pandas as pd
    from sqlalchemy import create_engine
except ImportError:
    pd = None
    create_engine = None


_backend_dir = Path(__file__).resolve().parent.parent.parent


def get_data_dir() -> Path:
    """Return backend/data directory for relative paths."""
    return _backend_dir / "data"


def load_csv(path: str):
    """Load CSV file."""
    return load_csv_data(path)


def load_excel(path: str, sheet: str | int = 0):
    """Load Excel file. sheet: sheet name or 0-based index."""
    if pd is None:
        return None
    try:
        return pd.read_excel(path, sheet_name=sheet)
    except Exception:
        return None


def _load_db(
    dialect: str,
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    table: str | None = None,
    query: str | None = None,
) -> "pd.DataFrame | None":
    """Load data from database via SQLAlchemy and pandas."""
    if pd is None or create_engine is None:
        return None
    pass_enc = quote_plus(str(password)) if password else ""
    url = f"{dialect}://{user}:{pass_enc}@{host}:{port}/{database}"
    try:
        engine = create_engine(url)
        sql = query if query else f"SELECT * FROM {table}"
        return pd.read_sql(sql, engine)
    except Exception:
        return None


def load_data(source_type: str, config: dict) -> "pd.DataFrame | None":
    """
    Load data based on source_type and config.
    csv: config {"path": "good_data.csv"} - path relative to backend/data
    excel: config {"path": "data.xlsx", "sheet": 0} - optional sheet
    postgresql: config {"host", "port", "database", "user", "password", "table" or "query"}
    mysql: config same as postgresql
    """
    if pd is None:
        return None

    if source_type == "csv":
        path = config.get("path")
        if not path:
            return None
        data_dir = get_data_dir()
        full_path = data_dir / path if not os.path.isabs(path) else Path(path)
        return load_csv_data(str(full_path))

    if source_type == "excel":
        path = config.get("path")
        if not path:
            return None
        data_dir = get_data_dir()
        full_path = data_dir / path if not os.path.isabs(path) else Path(path)
        sheet = config.get("sheet", 0)
        return load_excel(str(full_path), sheet)

    if source_type == "postgresql":
        return _load_db(
            dialect="postgresql",
            host=config.get("host", "localhost"),
            port=int(config.get("port", 5432)),
            database=config.get("database", ""),
            user=config.get("user", ""),
            password=config.get("password", ""),
            table=config.get("table"),
            query=config.get("query"),
        )

    if source_type == "mysql":
        return _load_db(
            dialect="mysql+pymysql",
            host=config.get("host", "localhost"),
            port=int(config.get("port", 3306)),
            database=config.get("database", ""),
            user=config.get("user", ""),
            password=config.get("password", ""),
            table=config.get("table"),
            query=config.get("query"),
        )

    return None
