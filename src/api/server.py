"""FastAPI Server for Learning Assistant Agent"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent import Agent, ToolRegistry, RetrievalTool, OpenAIInterface
from src.agent import ConversationMemory, CodeAnalysisTool, SummarizationTool, QuestionDecompositionTool
from src.rag.rag import RAG


# ─── Global State ───────────────────────────────────────────────────────────

_app_state = {
    "rag": None,
    "agent": None,
    "memory": None,
    "llm": None,
    "tool_registry": None,
    "initialized": False,
}


# ─── Lifespan Event Handler ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown event handler.
    Initializes RAG + Agent on startup, cleans up on shutdown.
    """
    # Startup: Initialize RAG and Agent
    print("Initializing RAG system...", file=sys.stderr)
    try:
        config_path = project_root / "config" / "rag.yaml"
        _app_state["rag"] = RAG(str(config_path))
        print("RAG initialized.", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing RAG: {str(e)}", file=sys.stderr)
        raise

    print("Initializing LLM interface...", file=sys.stderr)
    try:
        _app_state["llm"] = OpenAIInterface()
        print("LLM interface initialized.", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}", file=sys.stderr)
        raise

    print("Initializing conversation memory...", file=sys.stderr)
    _app_state["memory"] = ConversationMemory(max_history=20, max_tokens=4000)

    print("Initializing tool registry...", file=sys.stderr)
    _app_state["tool_registry"] = ToolRegistry()

    # Register retrieval tool
    retrieval_tool = RetrievalTool(_app_state["rag"].hybrid_retriever)
    _app_state["tool_registry"].register(retrieval_tool)

    # Register other tools
    _app_state["tool_registry"].register(CodeAnalysisTool())
    _app_state["tool_registry"].register(SummarizationTool(_app_state["llm"]))
    _app_state["tool_registry"].register(QuestionDecompositionTool(_app_state["llm"]))

    print("Initializing Agent...", file=sys.stderr)
    _app_state["agent"] = Agent(
        tool_registry=_app_state["tool_registry"],
        llm_interface=_app_state["llm"],
        memory=_app_state["memory"],
        max_iterations=3
    )

    _app_state["initialized"] = True
    print("All systems ready.", file=sys.stderr)

    yield  # Server is running

    # Shutdown: Cleanup
    print("Shutting down...", file=sys.stderr)
    _app_state["initialized"] = False


# ─── FastAPI App ────────────────────────────────────────────────────────────

app = FastAPI(
    title="Learning Assistant Agent API",
    description="REST API for the Learning Assistant Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "127.0.0.1", "http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic Models ────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str  # "ready" | "initializing"


class ChatRequest(BaseModel):
    query: str
    use_tools: bool = True


class ChatResponse(BaseModel):
    response: str
    stats: Dict[str, Any]


class ResetResponse(BaseModel):
    success: bool


class HistoryMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class HistoryResponse(BaseModel):
    messages: List[HistoryMessage]


# ─── API Routes ─────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    """Check if the server and RAG system are ready."""
    if _app_state["initialized"]:
        return HealthResponse(status="ready")
    else:
        return HealthResponse(status="initializing")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the Agent and get a response."""
    if not _app_state["initialized"]:
        raise HTTPException(status_code=503, detail="System is still initializing")

    try:
        response = _app_state["agent"].run(request.query, use_tools=request.use_tools)
        stats = _app_state["agent"].get_memory_stats()
        return ChatResponse(response=response, stats=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/reset", response_model=ResetResponse)
async def reset():
    """Reset the conversation memory."""
    if not _app_state["initialized"]:
        raise HTTPException(status_code=503, detail="System is still initializing")

    try:
        _app_state["agent"].reset_memory()
        return ResetResponse(success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting memory: {str(e)}")


@app.get("/history", response_model=HistoryResponse)
async def history():
    """Get the conversation history."""
    if not _app_state["initialized"]:
        raise HTTPException(status_code=503, detail="System is still initializing")

    try:
        messages = _app_state["agent"].get_conversation_history()
        history_messages = [
            HistoryMessage(role=msg["role"], content=msg["content"], timestamp=msg["timestamp"])
            for msg in messages
        ]
        return HistoryResponse(messages=history_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


# ─── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8765"))
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False
    )
