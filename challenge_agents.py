"""
Challenge-specific agents (Challenge1-Challenge10)
Each agent connects to its respective MCP server
"""
import os
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from mcp_client import MCPClient
from challenge_configs import get_challenge_config

load_dotenv()

# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "mcp-security-agent")

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.8,
)


class ChallengeState(TypedDict):
    """State of a challenge agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]


def create_challenge_agent(challenge_num: int, port: int):
    """Create a challenge-specific agent"""
    mcp_client = MCPClient(f"http://localhost:{port}/sse")
    config = get_challenge_config(challenge_num)

    # Create MCP tools as LangChain tools
    @tool
    async def list_mcp_tools() -> str:
        """List all available MCP tools from the server"""
        return await mcp_client.list_tools()

    @tool
    async def list_mcp_resources() -> str:
        """List all available MCP resources from the server"""
        return await mcp_client.list_resources()

    @tool
    async def list_mcp_prompts() -> str:
        """List all available MCP prompts from the server"""
        return await mcp_client.list_prompts()

    @tool
    async def get_user_info(username: str) -> str:
        """Get user information from the MCP server.

        Args:
            username: The username to look up
        """
        return await mcp_client.execute_tool("get_user_info", {"username": username})

    @tool
    async def read_mcp_resource(uri: str) -> str:
        """Read a resource from the MCP server.

        Args:
            uri: The resource URI (e.g., 'internal://credentials' or 'notes://user123')
        """
        return await mcp_client.read_resource(uri)

    # Bind tools to LLM
    tools = [list_mcp_tools, list_mcp_resources, list_mcp_prompts, get_user_info, read_mcp_resource]
    llm_with_tools = llm.bind_tools(tools)

    async def challenge_node(state: ChallengeState):
        """Process user message and interact with MCP server"""
        messages = state["messages"]

        # Build challenge-specific system message
        challenge_info = f"""**Challenge {challenge_num}: {config.get('name', 'Unknown')}**
Difficulty: {config.get('difficulty', 'Unknown')} | Port: {port}

{config.get('description', '')}

**Available Tools/Resources:**
""" + "\n".join([f"- {tool}" for tool in config.get('resources', [])]) + """

**Your Objectives:**
""" + "\n".join([f"{i+1}. {obj}" for i, obj in enumerate(config.get('objectives', []))]) if config else ""

        system_msg = f"""You are an MCP (Model Context Protocol) security testing assistant for Challenge {challenge_num}.

{challenge_info}

**Your Role:**
- Help users explore and test this MCP server for vulnerabilities
- Use the available MCP tools to execute user requests
- Provide clear explanations of what you discover
- Format JSON results with markdown code blocks for better readability

**Available MCP Operations:**
- list_mcp_tools() - Show available MCP tools from the server
- list_mcp_resources() - Show available MCP resources
- list_mcp_prompts() - Show available MCP prompts
- get_user_info(username) - Get user information
- read_mcp_resource(uri) - Read MCP resources (e.g., 'internal://credentials', 'notes://user123')

**Important:**
- Be proactive in calling tools when users make requests
- Execute actual MCP operations rather than just explaining them
- Help users understand the security implications of what they discover
- Present findings in a clear, educational manner

Ready to help you explore Challenge {challenge_num}!"""

        # Only add system message on first turn
        if len(messages) <= 1 and not any(hasattr(m, 'type') and m.type == 'system' for m in messages):
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content=system_msg)] + list(messages)

        # Call LLM with tools
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    async def tool_node(state: ChallengeState):
        """Execute tools that the LLM requested"""
        messages = state["messages"]
        last_message = messages[-1]

        # Execute all tool calls
        tool_responses = []
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the tool
                for t in tools:
                    if t.name == tool_name:
                        result = await t.ainvoke(tool_args)
                        tool_responses.append(
                            ToolMessage(
                                content=result,
                                tool_call_id=tool_call["id"]
                            )
                        )
                        break

        return {"messages": tool_responses}

    def should_continue(state: ChallengeState):
        """Decide whether to continue to tools or end"""
        messages = state["messages"]
        last_message = messages[-1]

        # If LLM called tools, execute them
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        # Otherwise, end
        return END

    # Build graph
    workflow = StateGraph(ChallengeState)
    workflow.add_node("agent", challenge_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Create all challenge agents
Challenge1 = create_challenge_agent(1, 9001)
Challenge2 = create_challenge_agent(2, 9002)
Challenge3 = create_challenge_agent(3, 9003)
Challenge4 = create_challenge_agent(4, 9004)
Challenge5 = create_challenge_agent(5, 9005)
Challenge6 = create_challenge_agent(6, 9006)
Challenge7 = create_challenge_agent(7, 9007)
Challenge8 = create_challenge_agent(8, 9008)
Challenge9 = create_challenge_agent(9, 9009)
Challenge10 = create_challenge_agent(10, 9010)
