"""Test different questions"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import DocuMindWorkforce

DOC = """
DocuMind Annual Report 2024

Revenue: $12.5 million (up 45%)
Team: John Smith (CEO), Jane Doe (CTO)
Clients: 50+ enterprises
Technology: ERNIE LLM, PaddleOCR-VL, CAMEL-AI
"""

async def main():
    workforce = DocuMindWorkforce()
    workforce.initialize()
    
    questions = [
        "What is the revenue?",
        "Who is the CEO?",
        "What technology does it use?",
        "How many clients?"
    ]
    
    print("Testing different questions:\n")
    
    for i, q in enumerate(questions):
        doc = DOC if i == 0 else None  # only pass doc on first question
        answer = await workforce.ask(q, doc)
        print(f"Q: {q}")
        print(f"A: {answer}\n")

if __name__ == "__main__":
    asyncio.run(main())
