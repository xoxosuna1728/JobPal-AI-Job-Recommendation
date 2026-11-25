"""LLM output eval: is every job the agent recommends grounded in tool results?

For each prompt we check that (1) the agent called a search tool, and (2) every [#ID]
it mentions was actually returned by a tool, i.e. no invented jobs.
Needs ANTHROPIC_API_KEY. Run: python eval_agent.py
"""
import re

from agent import Agent
from search import JobIndex

PROMPTS = [
    "Find me an AI internship in Bengaluru",
    "Any remote internships that pay at least 40000?",
    "I like Flask and SQL. What backend jobs fit me?",
    "Show me computer vision roles",
    "I want to work on search and recommendations",
]


def main():
    index = JobIndex()
    passed = 0
    for prompt in PROMPTS:
        agent = Agent(index, "eval")
        reply = agent.chat(prompt)
        mentioned = {int(i) for i in re.findall(r"\[#(\d+)\]", reply)}
        used_search = any(name == "search_jobs" for name, _ in agent.tool_log)
        grounded = mentioned <= agent.seen_ids
        ok = used_search and grounded
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {prompt!r}  searched={used_search} mentioned={sorted(mentioned)}")
    print(f"\nGrounded and tool-backed: {passed}/{len(PROMPTS)}")


if __name__ == "__main__":
    main()
