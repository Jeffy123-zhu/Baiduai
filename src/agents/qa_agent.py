"""
QA Agent

Answers questions about documents. Keeps context in memory
so you can ask follow-up questions.
"""
from typing import Any, Dict, List, Optional

# CAMEL-AI import (optional)
try:
    from camel.messages import BaseMessage
except ImportError:
    BaseMessage = None

from .base_agent import BaseDocuMindAgent, AgentRole, AgentResult
from core.ernie_client import ernie_client


class QAAgent(BaseDocuMindAgent):
    """
    QA Agent for document-based question answering.
    
    Capabilities:
    1. Answer questions based on document content
    2. Multi-turn conversation support
    3. Citation support for answers
    """
    
    SYSTEM_MESSAGE = """You are a professional document QA assistant agent. Your tasks include:
1. Accurately answering user questions based on provided document content
2. Citing relevant content from the document when the answer is found
3. Clearly informing users when information is not found in the document
4. Keeping answers concise, accurate, and helpful

You are part of the DocuMind multi-agent system, responsible for the QA stage.
Important: Only answer based on document content, do not fabricate information."""

    def __init__(self):
        super().__init__(
            name="QA-Agent",
            role=AgentRole.QA,
            system_message=self.SYSTEM_MESSAGE,
            description="Document QA expert for answering questions based on document content"
        )
        self.ernie = ernie_client
        self.conversation_history: List[Dict[str, str]] = []
        self.document_context: str = ""

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute a QA task.
        
        Args:
            task: Task specification containing:
                - action: "ask" | "set_context" | "clear" | "multi_turn"
                - question: Question string (required for ask)
                - document: Document content (required for set_context)
                - with_citation: Whether to include citations
                
        Returns:
            AgentResult with QA outcome
        """
        try:
            action = task.get("action", "ask")
            
            if action == "set_context":
                document = task.get("document", "")
                self.document_context = document
                self.conversation_history = []  # reset history when new doc
                return AgentResult(
                    success=True,
                    data={"message": "Document context set successfully"},
                    metadata={"document_length": len(document), "agent": self.name}
                )
            
            elif action == "clear":
                self.document_context = ""
                self.conversation_history = []
                self.reset()
                return AgentResult(
                    success=True,
                    data={"message": "Context cleared"}
                )
            
            elif action == "ask":
                question = task.get("question", "")
                with_citation = task.get("with_citation", True)
                
                if not question:
                    return AgentResult(
                        success=False,
                        data=None,
                        error="No question provided"
                    )
                
                if not self.document_context:
                    return AgentResult(
                        success=False,
                        data=None,
                        error="Please set document context first"
                    )
                
                answer = await self._answer_question(question, with_citation)
                
                self.conversation_history.append({"role": "user", "content": question})
                self.conversation_history.append({"role": "assistant", "content": answer})
                
                return AgentResult(
                    success=True,
                    data={"answer": answer, "question": question},
                    metadata={"with_citation": with_citation, "agent": self.name}
                )
            
            elif action == "multi_turn":
                questions = task.get("questions", [])
                answers = []
                
                for q in questions:
                    answer = await self._answer_question(q, with_citation=True)
                    self.conversation_history.append({"role": "user", "content": q})
                    self.conversation_history.append({"role": "assistant", "content": answer})
                    answers.append({"question": q, "answer": answer})
                
                return AgentResult(
                    success=True,
                    data={"qa_pairs": answers},
                    metadata={"total_turns": len(questions), "agent": self.name}
                )
            
            return AgentResult(
                success=False,
                data=None,
                error=f"Unknown action: {action}"
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _answer_question(self, question: str, with_citation: bool = True) -> str:
        """Answer a question based on document context."""
        citation_instruction = ""
        if with_citation:
            citation_instruction = "\nIf the answer comes from the document, mark [Citation] and provide the relevant excerpt."
        
        prompt = f"""Answer the question based on the following document content:

[Document Content]
{self.document_context[:6000]}

[Question]
{question}

Please answer accurately.{citation_instruction}
If the information is not found in the document, clearly state "Information not found in document"."""

        messages = []
        
        recent_history = self.conversation_history[-8:] if len(self.conversation_history) > 8 else self.conversation_history
        messages.extend(recent_history)
        
        messages.append({"role": "user", "content": prompt})
        
        return await self.ernie.chat(messages, system=self.system_prompt, temperature=0.3)
    
    async def ask(self, question: str, document: Optional[str] = None) -> str:
        """
        Convenience method for direct questioning.
        
        Args:
            question: The question to ask
            document: Optional document content to set as context
            
        Returns:
            Answer string
        """
        if document:
            await self.execute({"action": "set_context", "document": document})
        
        result = await self.execute({"action": "ask", "question": question})
        
        if result.success:
            return result.data["answer"]
        else:
            return f"Error: {result.error}"
