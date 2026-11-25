# JobPal – AI-Powered Job Recommendation System

JobPal is an AI-powered conversational job discovery application that helps users find relevant job opportunities through natural-language queries. It combines Google Gemini, LLM function calling, semantic search, and SQLite to provide an interactive job-search experience.

> **Note:** The current application uses fictional sample job listings for demonstration purposes. It does not fetch live vacancies.

## Features

- **Conversational AI:** Uses Google Gemini 3.5 Flash-Lite to understand natural-language job-search requests.
- **LLM Function Calling:** Enables the AI agent to select and execute predefined application tools.
- **Semantic Job Search:** Uses Sentence Transformers embeddings to rank jobs based on query similarity.
- **TF-IDF Fallback:** Provides an alternative text-retrieval method when the embedding model is unavailable.
- **Job Details:** Retrieves detailed information about selected job listings.
- **Job Shortlisting:** Allows users to save jobs and view their saved list.
- **Conversation Memory:** Maintains message history during an agent session.
- **Web Interface:** Provides a Flask-based interface alongside a command-line interface.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| LLM | Google Gemini 3.5 Flash-Lite |
| LLM Integration | Google GenAI SDK |
| Backend | Flask |
| Semantic Search | Sentence Transformers |
| Retrieval Fallback | Scikit-learn TF-IDF |
| Database | SQLite |
| Environment Management | Python dotenv |

## Architecture

```text
              User Query
                  |
                  v
          Flask / CLI Interface
                  |
                  v
             Gemini Agent
                  |
          LLM Function Calling
                  |
       +----------+----------+
       |          |          |
       v          v          v
   Search Jobs  Job Details  Save / List Jobs
       |
       v
   SQL Filtering
       |
       v
  Semantic Ranking
       |
   +---+---+
   |       |
   v       v
Sentence  TF-IDF
Transformers Fallback
   |       |
   +---+---+
       |
       v
 Relevant Job Results
       |
       v
 Gemini Generates Response
       |
       v
    User Response
```

## Project Structure

```text
JobPal/
│
├── app.py                # Flask web application
├── agent.py              # Gemini agent and function calling
├── cli.py                # Command-line interface
├── db.py                 # Database operations
├── search.py             # Hybrid job retrieval
├── setup_db.py           # Database initialization
├── seed_jobs.py          # Sample job listings
├── eval_agent.py         # Agent evaluation
├── eval_retrieval.py     # Retrieval evaluation
├── test_gemini.py        # Gemini connection test
├── requirements.txt      # Python dependencies
├── .env                  # API configuration (not committed)
└── .gitignore            # Excluded files
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/xoxosuna1728/JobPal-AI-Job-Recommendation.git
cd JobPal-AI-Job-Recommendation
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
JOBPAL_MODEL=gemini-3.5-flash-lite
```

Get an API key through [Google AI Studio](https://aistudio.google.com/).

**Security:** Never commit your `.env` file or expose your API key publicly.

### 5. Initialize the database

```bash
python setup_db.py
python seed_jobs.py
```

### 6. Run the application

For the web application:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

For the command-line interface:

```bash
python cli.py
```

## Example Queries

Try asking JobPal:

- Find an AI internship in Bengaluru.
- Show me Python backend internships in Coimbatore.
- Find remote machine learning opportunities.
- Show the full details of job #2.
- Save job #2.
- Show my saved jobs.

## Evaluation

JobPal includes two evaluation scripts:

**Retrieval evaluation**

```bash
python eval_retrieval.py
```

Evaluates whether relevant job listings appear within the top three search results using Recall@3.

**Agent evaluation**

```bash
python eval_agent.py
```

Checks agent behaviour, including whether recommendations are supported by retrieved job records.

Record the actual results after running the evaluation scripts. Do not assume that earlier test results apply to every environment or dataset.

## Current Scope and Future Improvements

The current version focuses on conversational job discovery over structured SQLite job records. It uses semantic retrieval and LLM-generated responses.

Potential future improvements:

- Integrate real-time job listing sources.
- Add document and resume ingestion for personalised recommendations.
- Explore a dedicated vector database.
- Improve retrieval ranking and evaluation coverage.
- Add user authentication and persistent user profiles.
- Deploy the application online.

## Author

**Sunandita B**

GitHub: https://github.com/xoxosuna1728

Project Repository: https://github.com/xoxosuna1728/JobPal-AI-Job-Recommendation
