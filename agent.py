
"""The LLM agent: Gemini tool-calling loop with conversation memory."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from db import execute, query

load_dotenv()

MODEL = os.getenv("JOBPAL_MODEL", "gemini-3.5-flash-lite")
MAX_STEPS = 6

SYSTEM = """You are JobPal, a friendly career assistant that helps people find jobs.
Rules:
- Use the tools to look up jobs. Never invent jobs, companies, pay or other details.
- If the request is too vague to search, ask one short clarifying question.
- Refer to every job you recommend as [#ID] followed by its title and company, using only IDs returned by the tools.
- Keep answers short: at most 3 recommendations, each with one line on why it fits.
- If the user wants to keep a job, call save_job."""

TOOLS = [
    {
        "name": "search_jobs",
        "description": "Semantic search over the jobs database, with optional filters. Use for any request to find jobs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "location": {"type": "string"},
                "job_type": {
                    "type": "string",
                    "enum": ["internship", "full-time"]
                },
                "work_mode": {
                    "type": "string",
                    "enum": ["onsite", "remote", "hybrid"]
                },
                "min_pay": {"type": "integer"},
                "top_k": {"type": "integer"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_job_details",
        "description": "Get the full description of one job by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {"job_id": {"type": "integer"}},
            "required": ["job_id"]
        }
    },
    {
        "name": "save_job",
        "description": "Save a job to the user's shortlist.",
        "input_schema": {
            "type": "object",
            "properties": {"job_id": {"type": "integer"}},
            "required": ["job_id"]
        }
    },
    {
        "name": "list_saved_jobs",
        "description": "List the jobs the user has saved so far.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

# Convert existing tool definitions into Gemini format
GEMINI_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters_json_schema=tool["input_schema"]
        )
        for tool in TOOLS
    ]
)


class Agent:

    def __init__(self, index, session_id="default", client=None):
        self.index = index
        self.session_id = session_id

        api_key = os.getenv("GEMINI_API_KEY")

        if client is None and not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        self.client = client or genai.Client(api_key=api_key)

        self.messages = []
        self.seen_ids = set()
        self.tool_log = []

    def _run_tool(self, name, args):
        try:

            if name == "search_jobs":
                results = self.index.search(
                    args["query"],
                    top_k=min(int(args.get("top_k", 5)), 5),
                    location=args.get("location"),
                    job_type=args.get("job_type"),
                    work_mode=args.get("work_mode"),
                    min_pay=args.get("min_pay")
                )

                self.seen_ids.update(r["id"] for r in results)

                return {"results": results}

            if name == "get_job_details":
                rows = query(
                    "SELECT * FROM jobs WHERE id = ?",
                    (int(args["job_id"]),)
                )

                if not rows:
                    return {"error": "No job with that ID."}

                self.seen_ids.add(rows[0]["id"])

                return dict(rows[0])

            if name == "save_job":

                if not query(
                    "SELECT 1 FROM jobs WHERE id = ?",
                    (int(args["job_id"]),)
                ):
                    return {"error": "No job with that ID."}

                execute(
                    """INSERT OR IGNORE INTO saved_jobs
                    (session_id, job_id) VALUES (?, ?)""",
                    (self.session_id, int(args["job_id"]))
                )

                return {"saved": int(args["job_id"])}

            if name == "list_saved_jobs":
                rows = query(
                    """SELECT j.id, j.title, j.company
                    FROM saved_jobs s
                    JOIN jobs j ON j.id = s.job_id
                    WHERE s.session_id = ?
                    ORDER BY s.saved_at""",
                    (self.session_id,)
                )

                return {"saved": [dict(row) for row in rows]}

            return {"error": f"Unknown tool {name}"}

        except Exception as exc:
            return {"error": str(exc)}

    def chat(self, user_text):

        # Store user message in conversation memory
        self.messages.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)]
            )
        )

        for _ in range(MAX_STEPS):

            response = self.client.models.generate_content(
                model=MODEL,
                contents=self.messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM,
                    tools=[GEMINI_TOOL],
                    max_output_tokens=1024
                )
            )

            if not response.candidates:
                return "Sorry, I couldn't generate a response. Please try again."

            model_content = response.candidates[0].content

            if model_content is None:
                return "Sorry, I couldn't generate a response. Please try again."

            # Store Gemini response in conversation memory
            self.messages.append(model_content)

            # Check whether Gemini requested any tools
            function_calls = [
                part.function_call
                for part in model_content.parts
                if part.function_call is not None
            ]

            # If no tools are needed, return the answer
            if not function_calls:
                return response.text or "Sorry, I couldn't generate a response."

            # Execute requested tools
            function_responses = []

            for call in function_calls:

                name = call.name
                args = dict(call.args or {})

                result = self._run_tool(name, args)

                self.tool_log.append((name, args))

                function_responses.append(
                    types.Part.from_function_response(
                        name=name,
                        response=result
                    )
                )

            # Send tool results back to Gemini
            self.messages.append(
                types.Content(
                    role="user",
                    parts=function_responses
                )
            )

        return "Sorry, I couldn't finish that. Could you rephrase?"
