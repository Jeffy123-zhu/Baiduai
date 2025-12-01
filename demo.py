"""
DocuMind Demo Script

Run this to see the system in action.
Usage: python demo.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.agents import DocuMindWorkforce


# Sample contract for demo
SAMPLE_CONTRACT = """
SERVICE AGREEMENT

This Agreement is entered into on January 15, 2025 between:

Party A: TechCorp Inc., located at 123 Innovation Drive, San Francisco, CA
Party B: DataServices LLC, located at 456 Cloud Street, Seattle, WA

1. SERVICES
Party B agrees to provide data processing and analytics services to Party A
for a period of 12 months starting February 1, 2025.

2. PAYMENT
Party A shall pay Party B a monthly fee of $15,000 USD, due on the 1st of each month.
Late payments will incur a 2% penalty per month.

3. CONFIDENTIALITY
Both parties agree to keep all shared information confidential for 3 years
after termination of this agreement.

4. TERMINATION
Either party may terminate with 30 days written notice. Early termination
by Party A requires payment of 3 months fees as penalty.

5. LIABILITY
Party B's total liability shall not exceed the fees paid in the last 12 months.

Signed:
John Smith, CEO - TechCorp Inc.
Jane Doe, President - DataServices LLC
"""


async def main():
    print("=" * 50)
    print("DocuMind - Document Analysis Demo")
    print("=" * 50)

    # init
    print("\nStarting agents...")
    workforce = DocuMindWorkforce()
    workforce.initialize()
    print(f"Ready. {len(workforce.coordinator.agents)} agents loaded.\n")

    # show sample
    print("-" * 50)
    print("SAMPLE DOCUMENT (Contract)")
    print("-" * 50)
    print(SAMPLE_CONTRACT[:500] + "...\n")

    # analyze
    print("-" * 50)
    print("ANALYSIS")
    print("-" * 50)

    print("\n[1] Generating summary...")
    summary = await workforce.coordinator.agents["summary"].execute({
        "action": "brief",
        "content": SAMPLE_CONTRACT
    })
    print(f"Summary: {summary.data}\n")

    print("[2] Asking a question...")
    answer = await workforce.ask(
        "What is the monthly payment amount?",
        SAMPLE_CONTRACT
    )
    print(f"Q: What is the monthly payment amount?")
    print(f"A: {answer}\n")

    print("[3] Another question...")
    answer2 = await workforce.ask(
        "What happens if Party A terminates early?",
        None  # uses previous context
    )
    print(f"Q: What happens if Party A terminates early?")
    print(f"A: {answer2}\n")

    print("-" * 50)
    print("Demo complete!")
    print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
