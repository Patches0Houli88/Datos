# shared_utils.py — central DB reference for full app sync
import sqlite3
import pathlib

# Always reference DB path relative to this file, ensuring consistent access across pages and cloud deployments
DB_PATH = str(pathlib.Path(__file__).parent / "universal_data.db")

def get_connection():
    return sqlite3.connect(DB_PATH)
