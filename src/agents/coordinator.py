"""
Coordinator Agent - the brain of the system

Manages all the other agents. Based on CAMEL-AI patterns but simplified
because the full framework was overkill for this project.
"""
from typing import Any, Dict, List, Optional
import asyncio

# CAMEL-AI imports (optional, with fallback)
try:
    from camel.agents import ChatAgent
    from camel.societies import RolePlaying
    from camel.messages import BaseMessage
    from camel.types import TaskType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False

from .base_agent import BaseDocuMindAgent, AgentRole, AgentResult
from core.ernie_client import ernie_client


class CoordinatorAgent(BaseDocuMindAgent):
    """
    Coordinator Agent for multi-agent orchestration.
    
    Implements CAMEL-AI patterns for:
    1. Task decomposition and planning
    2. Agent scheduling and collaboration
    3. RolePlaying-based deep analysis
    4. Result aggregation
    """
    
    SYSTEM_MESSAGE = """You are the coordinator agent of the DocuMind system. Your responsibilities include:
1. Analyzing document processing requirements from users
2. Decomposing complex tasks into subtasks
3. Coordinating OCR, analysis, summary, and QA agents
4. Aggregating outputs from all agents into final results

Based on task type, determine which agents to invoke and in what sequence.
For document processing, the typical flow is: OCR extraction -> Content analysis -> Summary generation -> QA preparation"""

    def __init__(self):
        super().__init__(
            name="Coordinator-Agent",
            role=AgentRole.COORDINATOR,
            system_message=self.SYSTEM_MESSAGE,
            description="Multi-agent system coordinator for task planning and scheduling"
        )
        self.ernie = ernie_client
        self.agents: Dict[str, BaseDocuMindAgent] = {}
        
    def register_agent(self, agent: BaseDocuMindAgent):
        """Register an agent with the coordinator."""
        self.agents[agent.role.value] = agent
        # TODO: maybe add validation here later
        
    def get_agent(self, role: AgentRole) -> Optional[BaseDocuMindAgent]:
        """Retrieve an agent by its role."""
        return self.agents.get(role.value)  # returns None if not found
    
    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute a coordination task.
        
        Args:
            task: Task specification containing:
                - action: "process_document" | "analyze" | "qa" | "role_play"
                - file_path: str (for process_document)
                - content: str (for analyze)
                - question: str (for qa)
                
        Returns:
            AgentResult with execution outcome
        """
        try:
            action = task.get("action", "process_document")
            
            if action == "process_document":
                return await self._process_document(task.get("file_path"))
            elif action == "analyze":
                return await self._analyze_content(task.get("content"))
            elif action == "qa":
                return await self._handle_qa(task.get("question"), task.get("document"))
            elif action == "role_play":
                return await self._role_play_analysis(task.get("content"), task.get("task_prompt"))
            else:
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
    
    async def _process_document(self, file_path: str) -> AgentResult:
        """
        Execute full document processing pipeline.
        
        Pipeline: OCR -> Analysis -> Summary
        """
        results = {
            "file_path": file_path,
            "stages": {},
            "agent_interactions": []
        }
        
        # Stage 1: OCR extraction
        ocr_agent = self.get_agent(AgentRole.OCR)
        if ocr_agent:
            results["agent_interactions"].append({
                "from": self.name,
                "to": ocr_agent.name,
                "task": "extract_text_from_document"
            })
            
            ocr_result = await ocr_agent.execute({
                "action": "to_markdown",
                "file_path": file_path
            })
            results["stages"]["ocr"] = {
                "success": ocr_result.success,
                "data": ocr_result.data
            }
            
            if not ocr_result.success:
                return AgentResult(
                    success=False,
                    data=results,
                    error=f"OCR failed: {ocr_result.error}"
                )
            
            content = ocr_result.data.get("markdown", "")
        else:
            return AgentResult(
                success=False,
                data=None,
                error="OCR Agent not registered"
            )
        
        # Stage 2: Document analysis
        analysis_agent = self.get_agent(AgentRole.ANALYSIS)
        if analysis_agent:
            results["agent_interactions"].append({
                "from": self.name,
                "to": analysis_agent.name,
                "task": "analyze_document_content"
            })
            
            analysis_result = await analysis_agent.execute({
                "action": "analyze",
                "content": content
            })
            results["stages"]["analysis"] = {
                "success": analysis_result.success,
                "data": analysis_result.data
            }
        
        # Stage 3: Summary generation
        summary_agent = self.get_agent(AgentRole.SUMMARY)
        if summary_agent:
            results["agent_interactions"].append({
                "from": self.name,
                "to": summary_agent.name,
                "task": "generate_summary"
            })
            
            summary_result = await summary_agent.execute({
                "action": "key_points",
                "content": content
            })
            results["stages"]["summary"] = {
                "success": summary_result.success,
                "data": summary_result.data
            }
        
        # Stage 4: Prepare QA context
        qa_agent = self.get_agent(AgentRole.QA)
        if qa_agent:
            await qa_agent.execute({
                "action": "set_context",
                "document": content
            })
            results["qa_ready"] = True
        
        results["content"] = content
        
        return AgentResult(
            success=True,
            data=results,
            metadata={
                "stages_completed": list(results["stages"].keys()),
                "total_interactions": len(results["agent_interactions"])
            }
        )
    
    async def _analyze_content(self, content: str) -> AgentResult:
        """Execute parallel analysis with multiple agents."""
        results = {"agent_outputs": {}}
        
        analysis_agent = self.get_agent(AgentRole.ANALYSIS)
        summary_agent = self.get_agent(AgentRole.SUMMARY)
        
        tasks = []
        if analysis_agent:
            tasks.append(("analysis", analysis_agent.execute({
                "action": "analyze",
                "content": content
            })))
        if summary_agent:
            tasks.append(("summary", summary_agent.execute({
                "action": "brief",
                "content": content
            })))
        
        for name, task in tasks:
            result = await task
            results["agent_outputs"][name] = {
                "success": result.success,
                "data": result.data
            }
        
        return AgentResult(
            success=True,
            data=results
        )
    
    async def _handle_qa(self, question: str, document: Optional[str] = None) -> AgentResult:
        """Handle question-answering requests."""
        qa_agent = self.get_agent(AgentRole.QA)
        if not qa_agent:
            return AgentResult(
                success=False,
                data=None,
                error="QA Agent not registered"
            )
        
        if document:
            await qa_agent.execute({
                "action": "set_context",
                "document": document
            })
        
        return await qa_agent.execute({
            "action": "ask",
            "question": question
        })
    
    async def _role_play_analysis(self, content: str, task_prompt: str) -> AgentResult:
        """
        Perform deep analysis using CAMEL RolePlaying pattern.
        
        Two agents collaborate: an analyst and a reviewer.
        """
        analyst_prompt = f"""You are a professional document analyst.
Analyze the following document content and discuss your findings with the reviewer:

{content[:3000]}

Task: {task_prompt}"""

        reviewer_prompt = """You are a rigorous reviewer.
Review the analyst's findings, raise questions, and suggest improvements.
Ensure the analysis is accurate, comprehensive, and valuable."""

        messages = [
            {"role": "user", "content": f"[Analyst Role]\n{analyst_prompt}"}
        ]
        
        analyst_response = await self.ernie.chat(messages, temperature=0.7)
        
        messages.append({"role": "assistant", "content": analyst_response})
        messages.append({"role": "user", "content": f"[Reviewer Role]\n{reviewer_prompt}\n\nPlease review the above analysis."})
        
        reviewer_response = await self.ernie.chat(messages, temperature=0.5)
        
        return AgentResult(
            success=True,
            data={
                "analyst_output": analyst_response,
                "reviewer_feedback": reviewer_response,
                "role_play_rounds": 2
            },
            metadata={"method": "camel_role_playing"}
        )


class DocuMindWorkforce:
    """
    DocuMind Workforce - Agent management and orchestration.
    
    Manages the lifecycle of all agents and provides high-level
    APIs for document processing tasks.
    """
    
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        self._initialized = False
        
    def initialize(self):
        """Initialize all agents in the workforce."""
        if self._initialized:
            return
            
        from .ocr_agent import OCRAgent
        from .analysis_agent import AnalysisAgent
        from .summary_agent import SummaryAgent
        from .qa_agent import QAAgent
        
        self.coordinator.register_agent(OCRAgent())
        self.coordinator.register_agent(AnalysisAgent())
        self.coordinator.register_agent(SummaryAgent())
        self.coordinator.register_agent(QAAgent())
        
        self._initialized = True
        
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document through the full agent pipeline."""
        self.initialize()
        result = await self.coordinator.execute({
            "action": "process_document",
            "file_path": file_path
        })
        return result.data if result.success else {"error": result.error}
    
    async def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content using parallel agent processing."""
        self.initialize()
        result = await self.coordinator.execute({
            "action": "analyze",
            "content": content
        })
        return result.data if result.success else {"error": result.error}
    
    async def ask(self, question: str, document: Optional[str] = None) -> str:
        """Answer a question based on document content."""
        self.initialize()
        result = await self.coordinator.execute({
            "action": "qa",
            "question": question,
            "document": document
        })
        if result.success:
            return result.data.get("answer", "")
        return f"Error: {result.error}"
    
    async def deep_analysis(self, content: str, task: str) -> Dict[str, Any]:
        """Perform deep analysis using CAMEL RolePlaying."""
        self.initialize()
        result = await self.coordinator.execute({
            "action": "role_play",
            "content": content,
            "task_prompt": task
        })
        return result.data if result.success else {"error": result.error}


# Backward compatibility alias
AgentOrchestrator = DocuMindWorkforce
