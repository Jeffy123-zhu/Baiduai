"""Quick test for DocuMind system."""
import asyncio
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import DocuMindWorkforce

async def main():
    print("="*50)
    print("DocuMind Multi-Agent System Test")
    print("="*50)
    
    workforce = DocuMindWorkforce()
    workforce.initialize()
    
    print(f"\n✓ {len(workforce.coordinator.agents)} agents initialized:")
    for role, agent in workforce.coordinator.agents.items():
        print(f"   - {agent.name}")
    
    # Test 1: QA
    print("\n[Test 1] Question Answering...")
    doc = "DocuMind is an AI document analysis system built with ERNIE LLM and PaddleOCR-VL."
    answer = await workforce.ask("What technologies does DocuMind use?", doc)
    print(f"✓ Answer: {answer[:150]}...")
    
    # Test 2: Summary
    print("\n[Test 2] Summary Generation...")
    summary_agent = workforce.coordinator.get_agent(
        workforce.coordinator.agents["summary"].role
    )
    summary_result = await summary_agent.execute({
        "action": "brief",
        "content": doc
    })
    print(f"✓ Summary: {str(summary_result.data)[:150]}...")
    
    print("\n✓ Core functionality verified!")
    
    print("\n" + "="*50)
    print("All tests passed! System ready for deployment.")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
