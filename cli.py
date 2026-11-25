"""Chat with JobPal in the terminal. Run: python cli.py"""
from agent import Agent
from search import JobIndex

if __name__ == "__main__":
    agent = Agent(JobIndex(), "cli")
    print("JobPal: Hi! Tell me what kind of job you want. (Ctrl+C to quit)\n")
    while True:
        try:
            text = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if text:
            print("\nJobPal:", agent.chat(text), "\n")
