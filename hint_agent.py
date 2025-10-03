"""
MCP Security Challenge Hint Agent
Interactive agent that provides hints for testing MCP security challenges
AND can execute MCP tools/resources when asked
"""
import os
import json
from typing import Annotated, Sequence, Dict, Any
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()

# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "mcp-security-agent")

# MCP Server URL
MCP_SERVER_URL = "http://localhost:9001/sse"

# Initialize Gemini 2.5 Flash
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.8,
)


class AgentState(TypedDict):
    """State of the hint agent"""
    messages: Annotated[Sequence[BaseMessage], "The conversation messages"]
    mcp_session: Annotated[Any, "MCP session for tool execution"]


# System prompt for the hint agent
SYSTEM_PROMPT = """You are a friendly and helpful MCP Security Training Assistant. Your role is to guide users through hands-on security testing of vulnerable MCP servers by providing hints, explanations, and encouragement.

## Your Mission
Help users learn about MCP security vulnerabilities through interactive exploration. Provide hints when they're stuck, explain concepts when asked, but let them discover vulnerabilities themselves.

## Available Challenges

### Challenge 1: Basic Prompt Injection (Port 9001)
**MCP Server**: http://localhost:9001/sse
**Vulnerability**: Prompt injection in user input handling
**Key Resources**:
- `notes://{user_id}` - Accepts user input (VULNERABLE - reflects user_id without sanitization)
- `internal://credentials` - Hidden credentials resource (not listed, but accessible)
**Tools**:
- `get_user_info(username: str)` - Returns user information

## How to Interact

**When users ask for hints**, provide them in this order:
1. **Gentle Hint**: Point them in the right direction without giving away the answer
2. **Specific Hint**: Give more details about what to look for
3. **Technical Hint**: Explain the vulnerability mechanism
4. **Example Payload**: Only if they're really stuck, show a working example

**When users ask you to execute MCP tools or read resources**:
- You MUST call the appropriate function: execute_mcp_tool() or read_mcp_resource()
- Examples: "run tool get_user_info with user=admin" → execute_mcp_tool("get_user_info", {"username": "admin"})
- Examples: "read resource internal://credentials" → read_mcp_resource("internal://credentials")
- NEVER make up results - always execute the actual tool/resource

**When users share their attempts**, analyze them and provide feedback:
- If close, encourage and suggest refinements
- If wrong direction, gently redirect
- If successful, congratulate and explain why it worked

**When users ask about concepts**, explain clearly:
- What is prompt injection?
- How does MCP resource URI templating work?
- Why is input sanitization important?

## Your Style
- Be encouraging and positive 😊
- Use emojis to make it friendly 🎯
- Provide progressive hints, not full solutions
- Celebrate discoveries and learning moments 🎉
- Explain the "why" behind security concepts 🔐
- ALWAYS execute real MCP tools/resources when asked, never fake results

Remember: Your goal is to teach, not solve. Help users learn by discovery!
"""


# Helper functions for MCP operations
async def get_mcp_session():
    """Get or create MCP session"""
    read_stream, write_stream = await sse_client(MCP_SERVER_URL).__aenter__()
    session = ClientSession(read_stream, write_stream)
    await session.__aenter__()
    await session.initialize()
    return session


async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute an MCP tool and return results"""
    read_stream = None
    write_stream = None
    try:
        streams = sse_client(MCP_SERVER_URL)
        read_stream, write_stream = await streams.__aenter__()

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()

        await session.initialize()
        result = await session.call_tool(tool_name, arguments)

        await session.__aexit__(None, None, None)
        await streams.__aexit__(None, None, None)

        # Extract text from TextContent objects
        content_list = []
        for item in result.content:
            if hasattr(item, 'text'):
                content_list.append({"type": "text", "text": item.text})
            else:
                content_list.append(str(item))

        return json.dumps(content_list, indent=2)
    except Exception as e:
        import traceback
        return f"Error executing tool {tool_name}: {str(e)}\n{traceback.format_exc()}"


async def read_mcp_resource(resource_uri: str) -> str:
    """Read an MCP resource and return contents"""
    read_stream = None
    write_stream = None
    try:
        streams = sse_client(MCP_SERVER_URL)
        read_stream, write_stream = await streams.__aenter__()

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()

        await session.initialize()
        result = await session.read_resource(resource_uri)

        await session.__aexit__(None, None, None)
        await streams.__aexit__(None, None, None)

        # Extract text from content objects
        content_list = []
        for item in result.contents:
            if hasattr(item, 'text'):
                content_dict = {"type": "text", "text": item.text}
                if hasattr(item, 'uri') and item.uri:
                    content_dict["uri"] = str(item.uri)  # Convert AnyUrl to string
                content_list.append(content_dict)
            else:
                content_list.append(str(item))

        return json.dumps(content_list, indent=2)
    except Exception as e:
        import traceback
        return f"Error reading resource {resource_uri}: {str(e)}\n{traceback.format_exc()}"


async def list_mcp_tools() -> str:
    """List available MCP tools"""
    read_stream = None
    write_stream = None
    try:
        streams = sse_client(MCP_SERVER_URL)
        read_stream, write_stream = await streams.__aenter__()

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()

        await session.initialize()
        tools = await session.list_tools()

        await session.__aexit__(None, None, None)
        await streams.__aexit__(None, None, None)

        return json.dumps([{"name": t.name, "description": t.description} for t in tools], indent=2)
    except Exception as e:
        import traceback
        return f"Error listing tools: {str(e)}\n{traceback.format_exc()}"


async def list_mcp_resources() -> str:
    """List available MCP resources"""
    read_stream = None
    write_stream = None
    try:
        streams = sse_client(MCP_SERVER_URL)
        read_stream, write_stream = await streams.__aenter__()

        session = ClientSession(read_stream, write_stream)
        await session.__aenter__()

        await session.initialize()
        result = await session.list_resources()

        await session.__aexit__(None, None, None)
        await streams.__aexit__(None, None, None)

        # Extract resources list from the result
        resources = []
        if hasattr(result, 'resources'):
            resources = result.resources
        elif isinstance(result, list):
            resources = result
        else:
            resources = [result]

        # Handle different resource formats
        resource_list = []
        for r in resources:
            if hasattr(r, 'uri') and hasattr(r, 'name'):
                res_dict = {"uri": str(r.uri), "name": r.name}
                if hasattr(r, 'description') and r.description:
                    res_dict["description"] = r.description
                if hasattr(r, 'mimeType') and r.mimeType:
                    res_dict["mimeType"] = r.mimeType
                resource_list.append(res_dict)
            elif isinstance(r, tuple):
                # If it's a tuple, assume (uri, name) format
                resource_list.append({"uri": str(r[0]) if r[0] else None, "name": r[1] if len(r) > 1 else None})
            else:
                resource_list.append({"info": str(r)})

        return json.dumps(resource_list, indent=2)
    except Exception as e:
        import traceback
        return f"Error listing resources: {str(e)}\n{traceback.format_exc()}"


def create_hint_graph():
    """Create the hint agent graph"""

    async def hint_node(state: AgentState):
        """Process user message and provide hint"""
        messages = state["messages"]

        # Get the last user message content safely
        last_msg = ""
        if messages:
            last_message = messages[-1]
            content = None

            if hasattr(last_message, 'content'):
                content = last_message.content
            elif isinstance(last_message, dict) and 'content' in last_message:
                content = last_message['content']

            # Convert content to string
            if isinstance(content, str):
                last_msg = content.lower()
            elif isinstance(content, list):
                # If content is a list (multimodal), extract text
                last_msg = " ".join([str(item.get('text', '')) if isinstance(item, dict) else str(item) for item in content]).lower()
            elif content:
                last_msg = str(content).lower()

        # Add system prompt if this is the first message
        if len(messages) == 1:
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        # Check if user wants to execute MCP operations
        mcp_result = None

        # List tools
        if "list tools" in last_msg or "show tools" in last_msg or "available tools" in last_msg:
            mcp_result = await list_mcp_tools()
            messages.append(AIMessage(content=f"📋 Available MCP Tools:\n```json\n{mcp_result}\n```"))

        # List resources
        elif "list resources" in last_msg or "show resources" in last_msg or "available resources" in last_msg:
            mcp_result = await list_mcp_resources()
            messages.append(AIMessage(content=f"📋 Available MCP Resources:\n```json\n{mcp_result}\n```"))

        # Execute tool (detect patterns like "run tool", "execute tool", "call tool")
        elif any(x in last_msg for x in ["run tool", "execute tool", "call tool", "use tool"]):
            # Try to parse tool name and arguments
            if "get_user_info" in last_msg:
                # Extract username
                import re
                username_match = re.search(r'(?:user|username)[\s=:]+(\w+)', last_msg)
                if username_match:
                    username = username_match.group(1)
                    mcp_result = await execute_mcp_tool("get_user_info", {"username": username})
                    messages.append(AIMessage(content=f"🔧 Executed tool `get_user_info(username='{username}')`:\n```json\n{mcp_result}\n```"))

        # Read resource (detect patterns like "read resource", "access resource")
        elif any(x in last_msg for x in ["read resource", "access resource", "get resource", "fetch resource"]):
            # Try to parse resource URI
            import re
            # Get original content (not lowercased) for URI matching
            original_content = ""
            last_message = messages[-1]

            if hasattr(last_message, 'content'):
                original_content = last_message.content
            elif isinstance(last_message, dict) and 'content' in last_message:
                original_content = last_message['content']

            # Convert to string if it's a list
            if isinstance(original_content, list):
                original_content = " ".join([str(item.get('text', '')) if isinstance(item, dict) else str(item) for item in original_content])
            elif not isinstance(original_content, str):
                original_content = str(original_content)

            # Match URIs like internal://credentials or notes://something
            uri_match = re.search(r'(\w+://[\w/\-]+)', original_content)
            if uri_match:
                resource_uri = uri_match.group(1)
                mcp_result = await read_mcp_resource(resource_uri)
                messages.append(AIMessage(content=f"📄 Read resource `{resource_uri}`:\n```json\n{mcp_result}\n```"))

        # If we didn't execute MCP operation, get normal LLM response
        if not mcp_result:
            response = await llm.ainvoke(messages)
            return {"messages": messages + [response]}
        else:
            # Return messages with MCP result already added
            return {"messages": messages}

    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("hint", hint_node)
    workflow.add_edge(START, "hint")
    workflow.add_edge("hint", END)

    # LangGraph Platform handles persistence automatically
    return workflow.compile()


# Create the graph
graph = create_hint_graph()


async def chat(message: str, thread_id: str = "default") -> str:
    """
    Send a message and get a response

    Args:
        message: User message
        thread_id: Conversation thread ID

    Returns:
        Assistant response
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "metadata": {
            "user_message": message,
            "challenge": "interactive"
        },
        "tags": ["hint-agent", "interactive-chat", "mcp-security"]
    }

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    return result["messages"][-1].content


# For testing
if __name__ == "__main__":
    import asyncio

    async def test():
        print("🔐 MCP Security Hint Agent - Interactive Test\n")

        # Test conversation
        messages = [
            "Hi! I want to learn about Challenge 1",
            "Can you give me a hint for the prompt injection?",
            "I tried notes://admin but it didn't work",
        ]

        for msg in messages:
            print(f"User: {msg}")
            response = await chat(msg, thread_id="test-1")
            print(f"Assistant: {response}\n")

    asyncio.run(test())
