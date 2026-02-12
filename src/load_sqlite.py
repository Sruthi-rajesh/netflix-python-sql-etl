import sqlite3
import pandas as pd
from pathlib import Path
from config import CLEAN_DIR

DB_PATH = Path("netflix.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def load_csv(con, filename: str, table: str):
    df = pd.read_csv(CLEAN_DIR / filename)
    df.to_sql(table, con, if_exists="append", index=False)
    print(f"Loaded {len(df):,} rows into {table}")

def main():
    if not (CLEAN_DIR / "users_clean.csv").exists():
        print("Missing cleaned CSVs. Run: python src/etl.py after generating raw data.")
        return

    con = connect()
    cur = con.cursor()

    # Recreate tables using your schema file (sql/01_create_tables.sql)
    schema_sql = Path("sql/01_create_tables.sql").read_text(encoding="utf-8")
    cur.executescript(schema_sql)

    # Load dimension tables first, then fact table
    load_csv(con, "users_clean.csv", "users")
    load_csv(con, "titles_clean.csv", "titles")
    load_csv(con, "views_clean.csv", "views")

    con.commit()
    con.close()
    print(f"✅ SQLite DB ready: {DB_PATH.resolve()}")

if __name__ == "__main__":
    main()
