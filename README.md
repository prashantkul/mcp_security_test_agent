# LangGraph Security Agent for MCP Server Testing

A LangGraph-based security researcher agent that tests MCP (Model Context Protocol) servers for vulnerabilities using Gemini 2.5 Flash as the backend LLM.

## Features

- ✅ **Proper SSE Connection**: Uses MCP Python SDK's `sse_client` for reliable SSE connections
- ✅ **Gemini 2.5 Flash Integration**: Powered by Google's Gemini model for AI-driven security analysis
- ✅ **Full MCP Protocol Support**: Discovers and uses Tools, Prompts, and Resources from MCP servers
- ✅ **LangGraph State Management**: Tracks analysis state and findings
- ✅ **LangSmith Tracing**: Full observability and debugging with LangSmith
- ✅ **Challenge 1 Integration**: Successfully tests Basic Prompt Injection vulnerabilities

## Project Structure

```
langgraph-security-mcp/
├── hint_agent.py                # Interactive hint agent (LangGraph Chat UI)
├── security_agent_final.py      # Full analysis agent with LangSmith integration
├── test_sse_client.py           # Simple SSE connection test
├── langgraph.json               # LangGraph configuration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

## Installation

1. **Create conda environment** (already done):
```bash
conda activate langgraph_mcp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with:

```env
# Gemini Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
CONDA_ENV_NAME=langgraph_mcp

# LangSmith Configuration (optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=mcp-security-agent
```

### Get Your API Keys:
- **Gemini API**: [Get key from Google AI Studio](https://makersuite.google.com/app/apikey)
- **LangSmith API**: [Get key from LangSmith](https://smith.langchain.com/settings)

## Usage

### Start the Challenge 1 MCP Server

First, make sure the Challenge1 MCP server is running on port 9001:

```bash
# In another terminal, run the vulnerable MCP server
cd /Users/pskulkarni/Documents/source-code/vulnerable_mcp/damn-vulnerable-MCP-server/challenges/easy/challenge1
python server_sse.py
```

### Option 1: Interactive Hint Agent (LangGraph Chat UI) ⭐ RECOMMENDED

The hint agent provides interactive guidance and hints for solving security challenges:

```bash
conda activate langgraph_mcp
langgraph dev
```

This will:
- Start the LangGraph API server on `http://127.0.0.1:2024`
- Open LangGraph Studio in your browser
- Provide a chat interface to interact with the hint agent

**Chat Interface URL**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### Option 2: Full Security Analysis Agent

For a complete automated security analysis:

```bash
conda activate langgraph_mcp
python security_agent_final.py
```

### Test SSE Connection Only

To verify the SSE connection without running the full agent:

```bash
python test_sse_client.py
```

## How the Hint Agent Works

The hint agent is an interactive chat-based assistant that helps you learn about MCP security vulnerabilities:

### Progressive Hint System

1. **Gentle Hints**: Points you in the right direction without spoiling the solution
2. **Specific Hints**: Provides more details about what to look for
3. **Technical Hints**: Explains the vulnerability mechanism
4. **Example Payloads**: Shows working examples only when you're really stuck

### Example Conversation

```
You: I'm stuck on Challenge 1, can you give me a hint?

Agent: Great question! For Challenge 1, think about what happens when you put
your own text into the {user_id} part of the notes:// URI. What if that text
contained special instructions instead of just a user ID? 🤔

You: I tried notes://admin but nothing happened

Agent: Good start! You're on the right track with the notes:// resource.
But 'admin' is just a regular user ID. Think bigger - what if you could
make the LLM do something completely different than just fetch notes?
What would you want it to do? 🎯
```

### Features
- 😊 Friendly and encouraging tone
- 🎯 Progressive learning approach
- 💡 Explains the "why" behind concepts
- 🔐 Teaches security through discovery

## How the Analysis Agent Works

### 1. SSE Connection
The agent uses the official MCP Python SDK to establish an SSE connection:

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client(sse_url) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # ... interact with MCP server
```

### 2. Capability Discovery
The agent discovers available MCP resources and tools:

```python
# List resources
resources = await session.list_resources()

# List tools
tools = await session.list_tools()

# Read resources
result = await session.read_resource("internal://credentials")

# Call tools
result = await session.call_tool("get_user_info", {"username": "admin"})
```

### 3. LangGraph Agent
The security analysis is powered by a LangGraph agent:

```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    mcp_tools: list
    mcp_resources: list
    resource_contents: dict
    tool_results: dict
    iteration: int

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
graph = workflow.compile()
```

### 4. Gemini 2.5 Flash Analysis
The LLM analyzes the discovered vulnerabilities and generates:
- Vulnerability identification
- Exploitation strategies
- Proof-of-concept payloads
- Impact assessment
- Remediation recommendations

## Example Output

```
🔐 SECURITY ANALYSIS: Challenge 1 - Basic Prompt Injection
================================================================================
✅ MCP session initialized

🔍 Discovering MCP capabilities...
📁 Found 1 resources:
  - internal://credentials: get_credentials
🛠️  Found 1 tools:
  - get_user_info: Get information about a user

📄 Reading resources...
  ✓ internal://credentials: 300 chars

⚙️  Testing tools...
  ✓ get_user_info: Success

[SECURITY ANALYSIS]:
...provides comprehensive analysis with 5 injection payloads...
```

## Key Implementation Details

### SSE Connection (The LangGraph Way)

Unlike Google ADK which uses `MCPToolset`, LangGraph projects should use the MCP Python SDK directly:

```python
# ✅ Correct for LangGraph
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client(url) as (read, write):
    async with ClientSession(read, write) as session:
        # Use session

# ❌ Wrong - This is Google ADK approach
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
toolset = MCPToolset(connection_params=SseConnectionParams(url))
```

### MCP Protocol Integration

The agent properly implements all three MCP primitives:

1. **Resources**: Read-only data sources (e.g., `internal://credentials`)
2. **Tools**: Executable functions (e.g., `get_user_info`)
3. **Prompts**: Reusable prompt templates (discovered but not used in Challenge1)

## Tested Against

- **Challenge 1**: Basic Prompt Injection (Port 9001) ✅
  - Successfully discovers the `internal://credentials` resource
  - Identifies the `notes://{user_id}` vulnerability vector
  - Generates 5 working prompt injection payloads
  - Provides detailed security analysis and remediation

## Next Steps

To extend this for other challenges:

1. Add challenge-specific analysis prompts
2. Implement automated payload testing
3. Add reporting/logging capabilities
4. Support multiple concurrent challenge analysis

## LangSmith Observability

When LangSmith is enabled, you get:
- 📊 **Full trace visualization** of agent execution
- 🔍 **Token usage and cost tracking**
- 🐛 **Debug information** for each LLM call
- 📈 **Performance metrics** and latency analysis
- 🏷️ **Tagged runs** for easy filtering (tags: `security-analysis`, `mcp-testing`, `prompt-injection`)

View your traces at: https://smith.langchain.com

## Dependencies

- `langgraph` - Graph-based agent framework
- `langchain` - LLM integration framework
- `langchain-google-genai` - Gemini integration
- `langsmith` - LangSmith tracing and observability
- `mcp` - Official MCP Python SDK
- `httpx` - HTTP client
- `httpx-sse` - SSE support
- `python-dotenv` - Environment management

## License

This is a security research tool for educational purposes only.
