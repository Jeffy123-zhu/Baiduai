"""
Base Agent

All agents inherit from this. Tried to follow CAMEL-AI patterns
but had to simplify some things to get it working.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# Try to import CAMEL-AI, fallback to mock if not available
try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.types import RoleType, ModelType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    ChatAgent = None
    BaseMessage = None


class AgentRole(Enum):
    """Enumeration of agent roles in the DocuMind system."""
    COORDINATOR = "coordinator"
    OCR = "ocr"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    QA = "qa"


@dataclass
class AgentResult:
    """Data class representing the result of an agent execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MockBaseMessage:
    """Mock BaseMessage for when CAMEL-AI is not available."""
    
    def __init__(self, role_name: str, content: str):
        self.role_name = role_name
        self.content = content
    
    @classmethod
    def make_user_message(cls, role_name: str, content: str):
        return cls(role_name, content)
    
    @classmethod
    def make_assistant_message(cls, role_name: str, content: str):
        return cls(role_name, content)


class MockChatAgent:
    """Mock ChatAgent for when CAMEL-AI is not available."""
    
    def __init__(self, system_message=None, model_type=None):
        self.system_message = system_message
    
    def reset(self):
        pass


class BaseDocuMindAgent(ABC):
    """
    Base class for DocuMind agents built on CAMEL-AI framework.
    
    Each agent wraps a CAMEL ChatAgent and provides:
    1. Role-based system prompts
    2. ERNIE-powered conversation capabilities
    3. Inter-agent communication support
    
    Attributes:
        name: The agent's identifier
        role: The agent's role in the system
        description: Brief description of the agent's capabilities
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        system_message: str,
        description: str = ""
    ):
        self.name = name
        self.role = role
        self.description = description
        self._system_message = system_message
        self._context: Dict[str, Any] = {}
        
        self._chat_agent = self._create_chat_agent(system_message)
    
    def _create_chat_agent(self, system_message: str):
        """
        Create a CAMEL ChatAgent instance.
        
        Args:
            system_message: The system prompt for the agent
            
        Returns:
            Configured ChatAgent instance or mock
        """
        if CAMEL_AVAILABLE:
            sys_msg = BaseMessage.make_assistant_message(
                role_name=self.name,
                content=system_message
            )
            agent = ChatAgent(
                system_message=sys_msg,
                model_type=ModelType.GPT_4O_MINI,
            )
            return agent
        else:
            sys_msg = MockBaseMessage.make_assistant_message(
                role_name=self.name,
                content=system_message
            )
            return MockChatAgent(system_message=sys_msg)
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return self._system_message
    
    def create_user_message(self, content: str):
        """Create a user message for CAMEL framework."""
        if CAMEL_AVAILABLE:
            return BaseMessage.make_user_message(
                role_name="User",
                content=content
            )
        return MockBaseMessage.make_user_message("User", content)
    
    def create_assistant_message(self, content: str):
        """Create an assistant message for CAMEL framework."""
        if CAMEL_AVAILABLE:
            return BaseMessage.make_assistant_message(
                role_name=self.name,
                content=content
            )
        return MockBaseMessage.make_assistant_message(self.name, content)
    
    @abstractmethod
    async def execute(self, task: Any) -> AgentResult:
        """
        Execute a task. Must be implemented by subclasses.
        
        Args:
            task: The task specification
            
        Returns:
            AgentResult containing execution outcome
        """
        pass
    
    def update_context(self, key: str, value: Any):
        """Update the agent's context with a key-value pair."""
        self._context[key] = value
        
    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the agent's context."""
        return self._context.get(key, default)
    
    def reset(self):
        """Reset the agent state."""
        self._context.clear()
        if self._chat_agent:
            self._chat_agent.reset()
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, role={self.role.value})>"
