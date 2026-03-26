"""Agent层 - 推理决策和工具调用"""

from .agent import Agent
from .llm_interface import LLMInterface, OpenAIInterface
from .memory import ConversationMemory, SessionMemory, MemoryManager
from .tools import Tool, ToolRegistry, RetrievalTool, CodeAnalysisTool, SummarizationTool, QuestionDecompositionTool
from .prompt import (
    SYSTEM_PROMPT,
    TOOL_INSTRUCTION,
    CONTEXT_INSTRUCTION,
    REASONING_INSTRUCTION,
    FOLLOW_UP_PROMPT
)

__all__ = [
    # Agent核心
    "Agent",
    # LLM接口
    "LLMInterface",
    "OpenAIInterface",
    # 记忆管理
    "ConversationMemory",
    "SessionMemory",
    "MemoryManager",
    # 工具系统
    "Tool",
    "ToolRegistry",
    "RetrievalTool",
    "CodeAnalysisTool",
    "SummarizationTool",
    "QuestionDecompositionTool",
    # 提示词
    "SYSTEM_PROMPT",
    "TOOL_INSTRUCTION",
    "CONTEXT_INSTRUCTION",
    "REASONING_INSTRUCTION",
    "FOLLOW_UP_PROMPT",
]
