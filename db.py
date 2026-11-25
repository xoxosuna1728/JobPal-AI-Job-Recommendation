"""SQLite helpers: schema, queries and seeding."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobpal.db"

SCHEMA = """
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS saved_jobs;

CREATE TABLE jobs (
    id             INTEGER PRIMARY KEY,
    title          TEXT NOT NULL,
    company        TEXT NOT NULL,
    location       TEXT NOT NULL,
    work_mode      TEXT NOT NULL CHECK (work_mode IN ('onsite', 'remote', 'hybrid')),
    job_type       TEXT NOT NULL CHECK (job_type IN ('internship', 'full-time')),
    pay_per_month  INTEGER NOT NULL,
    skills         TEXT NOT NULL,
    description    TEXT NOT NULL
);

CREATE TABLE saved_jobs (
    session_id TEXT NOT NULL,
    job_id     INTEGER NOT NULL REFERENCES jobs(id),
    saved_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, job_id)
);

CREATE INDEX idx_jobs_type_mode ON jobs(job_type, work_mode);
"""


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, params=()):
    """Run a SELECT and return a list of dicts."""
    conn = _conn()
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def execute(sql, params=()):
    """Run an INSERT/UPDATE/DELETE and return the affected row count."""
    conn = _conn()
    try:
        with conn:
            cur = conn.execute(sql, params)
        return cur.rowcount
    finally:
        conn.close()


def init_db(jobs):
    """Create the tables and load the given list of job dicts."""
    conn = _conn()
    try:
        with conn:
            conn.executescript(SCHEMA)
            conn.executemany(
                """INSERT INTO jobs (title, company, location, work_mode, job_type,
                                     pay_per_month, skills, description)
                   VALUES (:title, :company, :location, :work_mode, :job_type,
                           :pay_per_month, :skills, :description)""",
                jobs,
            )
    finally:
        conn.close()
