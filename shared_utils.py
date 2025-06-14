# shared_utils.py — central DB reference with quoting helper
import sqlite3
import pathlib

# Always reference DB path relative to this file
DB_PATH = str(pathlib.Path(__file__).parent / "universal_data.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def quote_table(table_name):
    return f'"{table_name}"'  # safely quote table names for SQLite
