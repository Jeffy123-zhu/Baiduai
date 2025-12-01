"""
Analysis Agent

Does the heavy lifting for document understanding.
Entity extraction is kinda slow but it works.
"""
from typing import Any, Dict, List, Optional
import json

# CAMEL-AI import (optional)
try:
    from camel.messages import BaseMessage
except ImportError:
    BaseMessage = None

from .base_agent import BaseDocuMindAgent, AgentRole, AgentResult
from core.ernie_client import ernie_client


class AnalysisAgent(BaseDocuMindAgent):
    """
    Analysis Agent for document understanding and entity extraction.
    
    Capabilities:
    1. Document structure analysis
    2. Key entity extraction (dates, amounts, names, organizations)
    3. Document classification
    4. Sentiment analysis
    """
    
    SYSTEM_MESSAGE = """You are a professional document analysis agent. Your tasks include:
1. Analyzing document structure and type
2. Extracting key entities (names, organizations, dates, amounts, locations)
3. Identifying important clauses and information
4. Outputting analysis results in structured JSON format

You are part of the DocuMind multi-agent system, responsible for the document analysis stage.
Ensure your analysis is accurate, comprehensive, and clearly formatted."""

    def __init__(self):
        super().__init__(
            name="Analysis-Agent",
            role=AgentRole.ANALYSIS,
            system_message=self.SYSTEM_MESSAGE,
            description="Document analysis expert for extracting and analyzing key information"
        )
        self.ernie = ernie_client

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute an analysis task.
        
        Args:
            task: Task specification containing:
                - action: "analyze" | "extract_entities" | "classify"
                - content: Document content string
                - options: Optional configuration dict
                
        Returns:
            AgentResult with analysis outcome
        """
        try:
            action = task.get("action", "analyze")
            content = task.get("content", "")
            
            if not content:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No document content provided"
                )
            
            user_msg = self.create_user_message(f"Analysis task: {action}")
            
            if action == "analyze":
                result = await self._full_analysis(content)
            elif action == "extract_entities":
                result = await self._extract_entities(content)
            elif action == "classify":
                result = await self._classify_document(content)
            else:
                # default to full analysis if action not recognized
                result = await self._full_analysis(content)
            
            return AgentResult(
                success=True,
                data=result,
                metadata={"action": action, "agent": self.name}
            )
            
        except Exception as e:
            # TODO: better error handling
            return AgentResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _full_analysis(self, content: str) -> Dict[str, Any]:
        """Perform comprehensive document analysis."""
        prompt = f"""Please analyze the following document comprehensively and return results in JSON format:

Document content:
{content[:4000]}

Return the following JSON structure:
{{
    "document_type": "Document type (e.g., contract, report, letter)",
    "language": "Document language",
    "structure": {{
        "has_title": true/false,
        "has_sections": true/false,
        "section_count": number
    }},
    "key_entities": {{
        "persons": ["list of names"],
        "organizations": ["list of organizations"],
        "dates": ["list of dates"],
        "amounts": ["list of monetary amounts"],
        "locations": ["list of locations"]
    }},
    "key_points": ["list of key points"],
    "sentiment": "Document sentiment (positive/neutral/negative)",
    "summary": "One-sentence summary"
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, system=self.system_prompt, temperature=0.3)
        
        return self._parse_json_response(response)
    
    async def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract named entities from document."""
        prompt = f"""Extract all key entities from the following document and return in JSON format:

Document content:
{content[:4000]}

Return the following format:
{{
    "persons": ["names"],
    "organizations": ["organization names"],
    "dates": ["dates"],
    "amounts": ["monetary amounts"],
    "locations": ["locations"],
    "products": ["product/service names"],
    "other": ["other important entities"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, temperature=0.2)
        
        return self._parse_json_response(response)
    
    async def _classify_document(self, content: str) -> Dict[str, Any]:
        """Classify document type and category."""
        prompt = f"""Classify the following document and return in JSON format:

Document content:
{content[:2000]}

Return:
{{
    "primary_category": "Primary category",
    "secondary_category": "Secondary category",
    "confidence": 0.0-1.0,
    "tags": ["relevant tags"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, temperature=0.2)
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from model response."""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass
        
        return {"raw_analysis": response}
