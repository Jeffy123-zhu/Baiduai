"""
DocuMind Demo - CAMEL-AI Multi-Agent System Usage Examples

This script demonstrates:
1. Document processing pipeline (OCR -> Analysis -> Summary)
2. Intelligent question answering
3. CAMEL RolePlaying deep analysis
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import DocuMindWorkforce, AgentRole


async def demo_document_processing():
    """Demonstrate document processing pipeline."""
    print("\n" + "="*60)
    print("Demo 1: Document Processing Pipeline")
    print("="*60)
    
    workforce = DocuMindWorkforce()
    workforce.initialize()
    
    print(f"\nInitialized {len(workforce.coordinator.agents)} agents:")
    for role, agent in workforce.coordinator.agents.items():
        print(f"   - {agent.name} ({role})")
    
    sample_document = """
    # Annual Report 2024
    
    ## Overview
    This year the company achieved significant breakthroughs in artificial intelligence,
    successfully launching the DocuMind intelligent document analysis system.
    
    ## Key Achievements
    1. Completed CAMEL-AI framework integration
    2. Implemented PaddleOCR-VL document recognition
    3. Deployed ERNIE large model service
    
    ## Financial Data
    - Annual Revenue: $10 million
    - R&D Investment: $3 million
    - Net Profit: $2 million
    
    ## Team
    Team members: John Smith (Tech Lead), Jane Doe (Product Manager), Bob Wilson (AI Engineer)
    
    ## Next Steps
    In 2025, we will continue to deepen AI technology R&D with an expected investment of $5 million.
    """
    
    print("\nAnalyzing document content...")
    
    result = await workforce.analyze(sample_document)
    
    if "agent_outputs" in result:
        print("\nAnalysis Results:")
        if "analysis" in result["agent_outputs"]:
            analysis = result["agent_outputs"]["analysis"]["data"]
            if isinstance(analysis, dict):
                print(f"   Document Type: {analysis.get('document_type', 'N/A')}")
                print(f"   Sentiment: {analysis.get('sentiment', 'N/A')}")
                if "key_entities" in analysis:
                    entities = analysis["key_entities"]
                    print(f"   Persons: {entities.get('persons', [])}")
                    print(f"   Amounts: {entities.get('amounts', [])}")
        
        if "summary" in result["agent_outputs"]:
            summary = result["agent_outputs"]["summary"]["data"]
            print(f"\nSummary: {summary[:200]}...")


async def demo_qa():
    """Demonstrate intelligent question answering."""
    print("\n" + "="*60)
    print("Demo 2: Intelligent Question Answering")
    print("="*60)
    
    workforce = DocuMindWorkforce()
    
    document = """
    DocuMind is an intelligent document analysis system built on the CAMEL-AI framework.
    Main features include: OCR text recognition, document analysis, summary generation, intelligent QA.
    Technology stack: ERNIE large model, PaddleOCR-VL, CAMEL-AI, FastAPI.
    The development team is based in Beijing, established in 2024.
    """
    
    questions = [
        "What AI framework does DocuMind use?",
        "What are the main features of the system?",
        "Where is the development team located?"
    ]
    
    print("\nSetting document context...")
    
    for q in questions:
        print(f"\nQuestion: {q}")
        answer = await workforce.ask(q, document if q == questions[0] else None)
        print(f"Answer: {answer[:300]}...")


async def demo_role_playing():
    """Demonstrate CAMEL RolePlaying deep analysis."""
    print("\n" + "="*60)
    print("Demo 3: CAMEL RolePlaying Deep Analysis")
    print("="*60)
    
    workforce = DocuMindWorkforce()
    workforce.initialize()
    
    document = """
    Project Risk Assessment Report
    
    1. Technical Risk: Steep learning curve for new technology stack may impact development progress
    2. Market Risk: Numerous competitors, intense market share competition
    3. Financial Risk: High R&D investment, long payback period
    4. Talent Risk: AI talent shortage, recruitment difficulties
    """
    
    print("\nStarting RolePlaying analysis...")
    print("   Analyst Agent and Reviewer Agent will collaborate on document analysis\n")
    
    result = await workforce.deep_analysis(
        content=document,
        task="Identify the most critical risks and propose mitigation measures"
    )
    
    if "analyst_output" in result:
        print("Analyst Output:")
        print(f"   {result['analyst_output'][:400]}...")
        
    if "reviewer_feedback" in result:
        print("\nReviewer Feedback:")
        print(f"   {result['reviewer_feedback'][:400]}...")


async def demo_agent_info():
    """Display agent system information."""
    print("\n" + "="*60)
    print("DocuMind Multi-Agent System Information")
    print("="*60)
    
    workforce = DocuMindWorkforce()
    workforce.initialize()
    
    print("\nAgent List:")
    print("-" * 40)
    
    for role, agent in workforce.coordinator.agents.items():
        print(f"\n* {agent.name}")
        print(f"   Role: {role}")
        print(f"   Description: {agent.description}")
        print(f"   System Prompt: {agent.system_prompt[:100]}...")


async def main():
    """Main entry point."""
    print("\n" + " DocuMind CAMEL-AI Multi-Agent Demo ".center(60, "="))
    print("Intelligent Document Analysis System")
    print("Built on CAMEL-AI + ERNIE + PaddleOCR-VL")
    print("="*60)
    
    await demo_agent_info()
    
    # Run full demos with ERNIE API
    await demo_document_processing()
    await demo_qa()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
