from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "cleaned"
REJECT_DIR = BASE_DIR / "data" / "rejects"

DB_PATH = BASE_DIR / "netflix.db"

SQL_DIR = BASE_DIR / "sql"
CREATE_TABLES_SQL = SQL_DIR / "01_create_tables.sql"
