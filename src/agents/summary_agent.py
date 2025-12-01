"""
Summary Agent

Generates summaries. Nothing fancy, just prompts ERNIE
with different instructions based on what you need.
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


class SummaryAgent(BaseDocuMindAgent):
    """
    Summary Agent for document summarization.
    
    Capabilities:
    1. Brief summary generation
    2. Detailed summary generation
    3. Key points extraction
    4. Structured outline generation
    """
    
    SYSTEM_MESSAGE = """You are a professional document summarization agent. Your tasks include:
1. Accurately understanding the core content of documents
2. Extracting key information and main points
3. Generating concise and accurate summaries
4. Preserving important information without loss

You are part of the DocuMind multi-agent system, responsible for the summarization stage.
Ensure summaries are clear, well-organized, and help readers quickly understand document content."""

    def __init__(self):
        super().__init__(
            name="Summary-Agent",
            role=AgentRole.SUMMARY,
            system_message=self.SYSTEM_MESSAGE,
            description="Document summarization expert for extracting core content"
        )
        self.ernie = ernie_client

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute a summarization task.
        
        Args:
            task: Task specification containing:
                - action: "brief" | "detailed" | "key_points" | "outline"
                - content: Document content string
                - max_length: Optional maximum length for summary
                
        Returns:
            AgentResult with summarization outcome
        """
        try:
            action = task.get("action", "brief")
            content = task.get("content", "")
            max_length = task.get("max_length", 500)
            
            if not content:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No document content provided"
                )
            
            user_msg = self.create_user_message(f"Summary task: {action}")
            
            if action == "brief":
                result = await self._brief_summary(content, max_length)
            elif action == "detailed":
                result = await self._detailed_summary(content)
            elif action == "key_points":
                result = await self._extract_key_points(content)
            elif action == "outline":
                result = await self._generate_outline(content)
            else:
                result = await self._brief_summary(content, max_length)
            
            return AgentResult(
                success=True,
                data=result,
                metadata={"action": action, "agent": self.name}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _brief_summary(self, content: str, max_length: int = 500) -> str:
        """Generate a brief summary."""
        prompt = f"""Generate a brief summary of the following document, no more than {max_length} characters:

Document content:
{content[:6000]}

Requirements:
1. Summarize the main content of the document
2. Highlight the most important information
3. Use concise and clear language"""

        messages = [{"role": "user", "content": prompt}]
        return await self.ernie.chat(messages, system=self.system_prompt, temperature=0.3)
    
    async def _detailed_summary(self, content: str) -> str:
        """Generate a detailed summary."""
        prompt = f"""Generate a detailed summary of the following document:

Document content:
{content[:6000]}

Requirements:
1. Summarize each section's content in paragraphs
2. Preserve important details
3. Use clear structure to organize the summary
4. Include background, main content, and conclusions"""

        messages = [{"role": "user", "content": prompt}]
        return await self.ernie.chat(messages, system=self.system_prompt, temperature=0.4)
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from document."""
        prompt = f"""Extract 5-10 key points from the following document:

Document content:
{content[:6000]}

Return as a list, one point per line:
1. Point one
2. Point two
..."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, system=self.system_prompt, temperature=0.3)
        
        points = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                point = line.lstrip('0123456789.-*) ').strip()
                if point:
                    points.append(point)
        
        return points if points else [response]
    
    async def _generate_outline(self, content: str) -> Dict[str, Any]:
        """Generate a structured document outline."""
        prompt = f"""Generate a structured outline for the following document in JSON format:

Document content:
{content[:6000]}

Return the following format:
{{
    "title": "Document title",
    "sections": [
        {{
            "heading": "Section heading",
            "summary": "Section summary",
            "subsections": ["Subsection 1", "Subsection 2"]
        }}
    ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self.ernie.chat(messages, temperature=0.3)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except json.JSONDecodeError:
            pass
        
        return {"raw_outline": response}
