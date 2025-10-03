"""
Security Testing Orchestrator Agent
Routes user requests to appropriate challenge agents
"""
import os
from typing import Annotated, Sequence, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

load_dotenv()

# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "mcp-security-agent")

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)


class OrchestratorState(TypedDict):
    """State of the orchestrator agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    selected_challenge: Annotated[str, "Currently selected challenge (Challenge1-Challenge10)"]


SYSTEM_PROMPT = """You are a Security Testing Orchestrator for MCP vulnerability challenges.

**Available Challenges:**
- **Challenge 1**: Basic Prompt Injection (Port 9001) ✅ Ready
- **Challenge 2-10**: Additional challenges (Ports 9002-9010) 🔜 Coming soon

**How to Use:**
Instead of chatting with me, you should directly select and interact with the challenge agents:
1. Go back and select a Challenge agent from the dropdown (e.g., "Challenge1")
2. Each Challenge agent connects to its MCP server and can execute real commands
3. Use commands like:
   - `list tools` - See available MCP tools
   - `list resources` - See available MCP resources
   - `list prompts` - See available MCP prompts
   - `run tool <name> with <args>` - Execute a tool
   - `read resource <uri>` - Read a resource

**Example:**
Switch to "Challenge1" agent and try: `list resources`

I'm just the orchestrator - the real action happens in the Challenge agents! 🎯"""


def create_orchestrator_graph():
    """Create the orchestrator agent graph"""

    async def orchestrator_node(state: OrchestratorState):
        """Process user message and route to appropriate challenge"""
        messages = state["messages"]

        # Always include system prompt at the beginning
        has_system = any(isinstance(m, SystemMessage) for m in messages)
        if not has_system:
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        # Get response from LLM
        response = await llm.ainvoke(messages)

        # Detect which challenge user wants to work on
        last_msg = messages[-1].content.lower() if hasattr(messages[-1], 'content') else ""
        selected_challenge = state.get("selected_challenge", "")

        for i in range(1, 11):
            if f"challenge {i}" in last_msg or f"challenge{i}" in last_msg:
                selected_challenge = f"Challenge{i}"
                break

        return {
            "messages": messages + [response],
            "selected_challenge": selected_challenge
        }

    # Build graph
    workflow = StateGraph(OrchestratorState)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_edge(START, "orchestrator")
    workflow.add_edge("orchestrator", END)

    return workflow.compile()


# Create the graph
graph = create_orchestrator_graph()
