"""Create the SQLite database and load the sample jobs. Run once: python setup_db.py"""
from db import init_db, query
from seed_jobs import JOBS

if __name__ == "__main__":
    init_db(JOBS)
    print(f"Loaded {query('SELECT COUNT(*) AS n FROM jobs')[0]['n']} jobs into jobpal.db")
