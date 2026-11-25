# JobPal: a conversational job search agent

JobPal is a small LLM agent that helps people find jobs by chatting. It combines tool calling, conversation memory, a SQL database and semantic search, and it ships with two evals.

All companies and jobs in `seed_jobs.py` are fictional sample data.

## How it works

```
user message
   |
   v
Agent (agent.py)  <-- conversation memory (message history)
   |  LLM decides which tool to call (tool calling)
   v
Tools: search_jobs | get_job_details | save_job | list_saved_jobs
   |
   v
SQLite (db.py): jobs table + saved_jobs table
   |
   v
search.py: SQL filters (location, type, mode, pay) -> embedding similarity ranking
```

- **Tool use and structured outputs:** the model calls typed JSON tools instead of guessing.
- **Memory:** the full message history is kept per session, and saved jobs persist in SQL.
- **Hybrid retrieval:** SQL narrows candidates, then sentence-transformer embeddings rank them.
- **Guardrails:** the system prompt forbids inventing jobs; every recommendation must cite a `[#ID]` returned by a tool.

## Setup

```bash
pip install -r requirements.txt
python setup_db.py                      # creates jobpal.db with 20 sample jobs
export ANTHROPIC_API_KEY=your_key       # Windows PowerShell: $env:ANTHROPIC_API_KEY="your_key"
```

The first run downloads the embedding model (about 90 MB). If it can't, search falls back to TF-IDF and prints a notice.

## Run

```bash
python cli.py     # chat in the terminal
python app.py     # web chat at http://127.0.0.1:5000 and POST /chat
```

Try: "I want an AI internship in Bengaluru", then "save the first one", then "what have I saved?".

Optional: set `JOBPAL_MODEL` to use a different Claude model (default `claude-haiku-5-5`).

## Evals

```bash
python eval_retrieval.py   # recall@3 of the search, no API key needed
python eval_agent.py       # checks the agent searched and never mentions a job it did not retrieve
```

Run both and write the real numbers in the table below.

| Eval | Result |
|---|---|
| Retrieval recall@3 (embeddings) | _fill in_ |
| Agent grounded and tool-backed | _fill in_ |

## Ideas to extend

1. Deploy it (Docker + Render or Railway) so it has a live link.
2. Load real job listings from a CSV instead of the sample data.
3. Store embeddings in a vector database such as FAISS or pgvector.
4. Add a rerank step and a "why this fits" explanation using the user's resume.
5. Add more eval cases and track them over time.

## Files

| File | Purpose |
|---|---|
| `db.py`, `setup_db.py`, `seed_jobs.py` | schema, helpers, sample data |
| `search.py` | hybrid SQL + embedding search |
| `agent.py` | tool-calling loop, memory, system prompt |
| `cli.py`, `app.py` | terminal and Flask interfaces |
| `eval_retrieval.py`, `eval_agent.py` | evals |
