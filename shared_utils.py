import sqlite3

# Global DB file path
DB_FILE = "universal_data.db"

# Simple connection function
def get_connection():
    return sqlite3.connect(DB_FILE)

# Clean table quoting for dynamic queries
def quote_table(table_name):
    return f'"{table_name}"'
