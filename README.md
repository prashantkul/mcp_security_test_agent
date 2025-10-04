# LangGraph MCP Security Testing Agent

A LangGraph-based multi-agent system for testing [Damn Vulnerable MCP Server](https://github.com/harishsg993010/damn-vulnerable-MCP-server) using Gemini 2.5 Flash with intelligent function calling.

## 🎯 Purpose

This repository contains an interactive security testing agent designed specifically for testing the vulnerabilities in the **[Damn Vulnerable MCP Server](https://github.com/harishsg993010/damn-vulnerable-MCP-server)** project. It provides a hands-on learning environment for understanding MCP (Model Context Protocol) security issues through 10 different challenge scenarios.

## ✨ Features

- 🤖 **Multi-Agent Architecture**: Orchestrator + 10 individual challenge agents
- 🔧 **Function Calling Integration**: LLM dynamically calls MCP tools based on user requests
- 💬 **Conversation Persistence**: Full conversation history within threads
- 📊 **LangSmith Tracing**: Complete observability and debugging
- 🎨 **LangGraph Studio UI**: Beautiful chat interface for interactive testing
- 🔐 **Full MCP Support**: Tools, Resources, and Prompts
- 🎯 **Challenge-Specific Configs**: Each agent has customized objectives, resources, and hints
- 🎓 **Educational**: Learn security concepts through hands-on exploration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           LangGraph Studio UI (Port 2024)           │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │   Orchestrator Agent      │
        │   (Guides users)          │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴──────────────────────┐
        │                                    │
    ┌───▼────┐  ┌────────┐  ...  ┌─────────▼┐
    │ C1 (9001)│  │C2 (9002)│       │C10 (9010)│
    └───┬────┘  └───┬────┘         └────┬────┘
        │           │                    │
        ▼           ▼                    ▼
   MCP Server   MCP Server          MCP Server
```

Each challenge agent connects to its respective MCP server running on ports 9001-9010.

## 📁 Project Structure

```
langgraph-security-mcp/
├── orchestrator_agent.py    # Main orchestrator to guide users
├── challenge_agents.py       # 10 challenge-specific agents (C1-C10)
├── challenge_configs.py      # Challenge metadata (name, tools, resources, objectives)
├── mcp_client.py            # MCP client wrapper
├── hint_agent.py            # (Legacy) Interactive hint agent
├── langgraph.json           # LangGraph configuration
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
├── tests/                   # Automated test suite
│   ├── conftest.py          # Test fixtures and MCP server management
│   ├── test_challenge_agents.py  # Main test suite
│   └── README.md            # Testing documentation
├── .env                     # Environment variables (not committed)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🚀 Installation

### 1. Clone this repository

```bash
git clone git@github.com:prashantkul/mcp_security_test_agent.git
cd mcp_security_test_agent
```

### 2. Create conda environment

```bash
conda create -n langgraph_mcp python=3.11
conda activate langgraph_mcp
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
# Gemini Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# LangSmith Configuration (optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=mcp-security-agent
```

**Get API Keys:**
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **LangSmith API**: [LangSmith Settings](https://smith.langchain.com/settings)

## 🧪 Testing

### Automated Tests

This project includes a comprehensive test suite with automatic MCP server spawning:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests (without MCP servers)
pytest tests/ -v -m "not integration"

# Run integration tests (automatically spawns MCP servers)
export DVMCP_SERVER_PATH="$HOME/path/to/damn-vulnerable-MCP-server"
pytest tests/ -v -m integration

# Run all tests
pytest tests/ -v
```

**Test Features:**
- ✅ Automatic MCP server spawning and cleanup
- ✅ Conversation persistence validation
- ✅ Function calling and tool execution tests
- ✅ Challenge-specific vulnerability tests
- ✅ Error handling and edge cases

See [tests/README.md](tests/README.md) for detailed testing documentation.

## 🎮 Usage

### Step 1: Start the Damn Vulnerable MCP Server

First, clone and run the vulnerable MCP server:

```bash
# Clone the vulnerable server repository
git clone https://github.com/harishsg993010/damn-vulnerable-MCP-server.git
cd damn-vulnerable-MCP-server

# Start Challenge 1 (or any challenge you want to test)
cd challenges/easy/challenge1
python server_sse.py  # Runs on port 9001
```

The server will start on the respective port (9001-9010 depending on the challenge).

### Step 2: Start the LangGraph Agent

In a separate terminal:

```bash
conda activate langgraph_mcp
langgraph dev
```

This will:
- Start the LangGraph API server on `http://127.0.0.1:2024`
- Open LangGraph Studio in your browser
- Register all 11 agents (orchestrator + Challenge1-Challenge10)

### Step 3: Interact with the Agent

#### Option A: Use the Orchestrator (Recommended)

The orchestrator provides guidance on how to use the challenge agents:

1. Select **"orchestrator"** from the agent dropdown
2. Ask questions or request guidance
3. Switch to specific challenge agents as instructed

#### Option B: Direct Challenge Testing

For hands-on testing, directly select a challenge agent:

1. Select **"Challenge1"** (or any Challenge2-10) from the dropdown
2. Start testing with commands like:
   - `list resources` - See available MCP resources
   - `list tools` - See available MCP tools
   - `list prompts` - See available MCP prompts
   - `run get_user_info with user=admin` - Execute MCP tool
   - `read resource internal://credentials` - Read MCP resource

The LLM will intelligently interpret your requests and call the appropriate MCP tools!

## 🧪 Example Interaction

```
You: list resources

Agent: 📋 Resources:
[
  {
    "uri": "notes://{user_id}",
    "name": "user_notes",
    "description": "Access user notes"
  },
  {
    "uri": "internal://credentials",
    "name": "credentials",
    "description": "System credentials"
  }
]

You: run get_user_info tool with user=admin

Agent: 🔧 Tool result:
{
  "username": "admin",
  "role": "administrator",
  "email": "admin@example.com"
}
```

## 🎓 Available Challenges

The agent supports all 10 challenges from the Damn Vulnerable MCP Server:

| Challenge | Port | Difficulty | Description |
|-----------|------|------------|-------------|
| Challenge 1 | 9001 | Easy | Basic Prompt Injection |
| Challenge 2 | 9002 | Easy | Tool Poisoning |
| Challenge 3 | 9003 | Easy | Excessive Permission Scope |
| Challenge 4 | 9004 | Medium | Rug Pull Attack |
| Challenge 5 | 9005 | Medium | Tool Shadowing |
| Challenge 6 | 9006 | Medium | Indirect Prompt Injection |
| Challenge 7 | 9007 | Medium | Token Theft |
| Challenge 8 | 9008 | Hard | Malicious Code Execution |
| Challenge 9 | 9009 | Hard | Remote Access Control |
| Challenge 10 | 9010 | Hard | Multi-Vector Attack |

**⚠️ Note**: Challenge-specific configurations are implemented. Each agent has customized system prompts with objectives, resources, and hints. **Testing is pending** to verify all challenges work correctly with the vulnerable MCP servers.

## 🔧 How It Works

### Function Calling Integration

Instead of hardcoded command parsing, the agent uses **LangChain function calling**:

1. **MCP tools are exposed as LangChain tools**:
   - `list_mcp_tools()` - List available tools
   - `list_mcp_resources()` - List available resources
   - `list_mcp_prompts()` - List available prompts
   - `get_user_info(username)` - Get user information
   - `read_mcp_resource(uri)` - Read MCP resource

2. **LLM decides when to call tools**: Gemini 2.5 Flash intelligently interprets natural language requests and calls the appropriate tools

3. **Agent-Tool Loop**: The graph executes tools and feeds results back to the LLM

### Conversation Persistence

Uses the `add_messages` reducer to maintain full conversation history:

```python
class ChallengeState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

This ensures the agent remembers the entire conversation within each thread.

## 📊 LangSmith Observability

When enabled, you get:
- Full trace visualization of agent execution
- Token usage and cost tracking
- Debug information for each LLM call
- Performance metrics and latency analysis

View your traces at: https://smith.langchain.com

## 🛠️ Technical Stack

- **LangGraph**: Multi-agent orchestration and state management
- **LangChain**: LLM integration and tool calling
- **Gemini 2.5 Flash**: Backend LLM with function calling
- **MCP Python SDK**: Official MCP protocol client
- **LangGraph Studio**: Interactive UI for testing
- **LangSmith**: Tracing and observability

## 🤝 Related Projects

- **[Damn Vulnerable MCP Server](https://github.com/harishsg993010/damn-vulnerable-MCP-server)**: The vulnerable MCP server this agent tests against
- **[MCP Protocol](https://modelcontextprotocol.io/)**: Official Model Context Protocol documentation

## 📝 License

This is a security research and educational tool. Use responsibly and only against systems you have permission to test.

## 🙏 Acknowledgments

- Built to test [harishsg993010's Damn Vulnerable MCP Server](https://github.com/harishsg993010/damn-vulnerable-MCP-server)
- Powered by [Anthropic's Model Context Protocol](https://modelcontextprotocol.io/)
- Created with [LangGraph](https://langchain-ai.github.io/langgraph/)

---

**⚠️ Security Warning**: This tool is designed for educational purposes and authorized security testing only. Always ensure you have proper authorization before testing any system.
