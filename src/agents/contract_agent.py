"""
Contract Analysis Agent

Specialized agent for analyzing contracts and legal documents.
Extracts key terms, identifies risks, and highlights important clauses.
"""
from typing import Any, Dict
from .base_agent import BaseDocuMindAgent, AgentRole, AgentResult
from core.ernie_client import ernie_client


class ContractAgent(BaseDocuMindAgent):
    """Analyzes contracts and identifies key terms and risks."""

    SYSTEM_MESSAGE = """You are a contract analysis assistant. Your job is to:
1. Extract key terms (parties, dates, amounts, obligations)
2. Identify potential risks or unusual clauses
3. Summarize the main points of the agreement
Be concise and practical."""

    def __init__(self):
        super().__init__(
            name="Contract-Agent",
            role=AgentRole.ANALYSIS,  # reuse analysis role
            system_message=self.SYSTEM_MESSAGE,
            description="Contract analysis specialist"
        )
        self.ernie = ernie_client

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """Analyze a contract document."""
        try:
            content = task.get("content", "")
            if not content:
                return AgentResult(success=False, data=None, error="No content")

            action = task.get("action", "full")

            if action == "risks":
                result = await self._find_risks(content)
            elif action == "terms":
                result = await self._extract_terms(content)
            else:
                result = await self._full_analysis(content)

            return AgentResult(success=True, data=result)

        except Exception as e:
            return AgentResult(success=False, data=None, error=str(e))

    async def _full_analysis(self, content: str) -> Dict[str, Any]:
        """Full contract analysis."""
        prompt = f"""Analyze this contract and return JSON:

{content[:3000]}

Return:
{{
    "parties": ["list of parties involved"],
    "effective_date": "date or null",
    "termination_date": "date or null", 
    "key_obligations": ["main obligations"],
    "payment_terms": "payment info or null",
    "risks": ["potential issues to watch"],
    "summary": "2-3 sentence summary"
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, temperature=0.2)

        # try to parse json
        import json
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return {"raw": response}

    async def _find_risks(self, content: str) -> Dict[str, Any]:
        """Find potential risks in contract."""
        prompt = f"""Review this contract for risks:

{content[:3000]}

List potential issues, unusual terms, or things to watch out for."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, temperature=0.3)
        return {"risks": response}

    async def _extract_terms(self, content: str) -> Dict[str, Any]:
        """Extract key terms from contract."""
        prompt = f"""Extract key terms from this contract:

{content[:3000]}

List: parties, dates, amounts, deadlines, obligations."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, temperature=0.2)
        return {"terms": response}
