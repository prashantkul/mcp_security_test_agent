# Automated Tests for LangGraph MCP Security Agent

Comprehensive test suite for testing the LangGraph agents, MCP integration, and challenge servers.

## 🎯 Test Categories

### 1. **Conversation Persistence Tests**
- Verify agents remember conversation history
- Test message accumulation with `add_messages` reducer
- Validate context retention across multiple interactions

### 2. **Tool Calling Tests**
- Ensure LLM correctly interprets natural language requests
- Verify function calling integration with MCP tools
- Test parameter extraction and tool execution

### 3. **MCP Integration Tests** (requires MCP servers)
- Automatically spawn challenge MCP servers
- Test real MCP protocol communication
- Validate tool/resource/prompt listing
- Test challenge-specific vulnerabilities

### 4. **Challenge Configuration Tests**
- Verify challenge-specific metadata loads correctly
- Test system prompts include objectives and hints
- Validate all 10 challenge agents are configured

### 5. **Error Handling Tests**
- Test graceful handling of invalid requests
- Verify robustness against edge cases
- Test error recovery mechanisms

## 🚀 Quick Start

### Prerequisites

1. **Install test dependencies**:
```bash
pip install pytest pytest-asyncio
```

2. **Set environment variable** for DVMCP server location:
```bash
export DVMCP_SERVER_PATH="$HOME/Documents/source-code/vulnerable_mcp/damn-vulnerable-MCP-server"
```

3. **Ensure LangGraph is running**:
```bash
langgraph dev  # Should be running on http://127.0.0.1:2024
```

### Run All Tests (without MCP servers)

```bash
pytest tests/ -v -m "not integration"
```

This runs basic tests for conversation persistence, tool calling, and configuration without requiring MCP servers.

### Run Integration Tests (with MCP servers)

```bash
pytest tests/ -v -m integration
```

This automatically:
1. Spawns required MCP challenge servers
2. Runs tests against live servers
3. Cleans up servers after tests

### Run Specific Challenge Tests

```bash
# Test only Challenge 1
pytest tests/ -v -m "challenge(1)"

# Test Challenges 1, 2, and 3
pytest tests/test_challenge_agents.py::TestMCPIntegration -v
```

### Run All Tests (including integration)

```bash
pytest tests/ -v
```

## 📊 Test Output

### Successful Test Run
```
tests/test_challenge_agents.py::TestConversationPersistence::test_orchestrator_persistence PASSED
tests/test_challenge_agents.py::TestToolCalling::test_list_tools_execution PASSED
tests/test_challenge_agents.py::TestMCPIntegration::test_challenge1_list_tools PASSED
✓ Started Challenge 1 server on port 9001
✓ Stopped Challenge 1 server

==================== 15 passed in 45.23s ====================
```

### Test with Verbose Logging
```bash
pytest tests/ -v --log-cli-level=DEBUG
```

## 🔧 Test Configuration

### Environment Variables

- `DVMCP_SERVER_PATH`: Path to the Damn Vulnerable MCP Server repository
  - Default: `~/Documents/source-code/vulnerable_mcp/damn-vulnerable-MCP-server`

### Pytest Markers

- `@pytest.mark.integration`: Marks test as requiring MCP servers
- `@pytest.mark.challenge(num)`: Specifies which challenge server to spawn
- `@pytest.mark.slow`: Marks test as slow (for filtering)

### Example Test with Challenge Server

```python
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.challenge(1)
async def test_my_challenge(client, thread, challenge_server):
    """Test with Challenge 1 server automatically spawned"""
    thread_id = thread["thread_id"]

    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id="Challenge1",
        input={"messages": [{"role": "human", "content": "list tools"}]}
    )

    await client.runs.join(thread_id, run["run_id"])
    # Test assertions...
```

## 📁 Test Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest fixtures and MCP server management
├── test_challenge_agents.py     # Main test suite
└── __init__.py                  # Makes tests a package
```

## 🧪 Writing New Tests

### Example: Test Conversation Persistence

```python
@pytest.mark.asyncio
async def test_agent_remembers_name(client, thread):
    thread_id = thread["thread_id"]

    # First message
    run1 = await client.runs.create(
        thread_id=thread_id,
        assistant_id="Challenge1",
        input={"messages": [{"role": "human", "content": "My name is Alice"}]}
    )
    await client.runs.join(thread_id, run1["run_id"])

    # Second message
    run2 = await client.runs.create(
        thread_id=thread_id,
        assistant_id="Challenge1",
        input={"messages": [{"role": "human", "content": "What is my name?"}]}
    )
    await client.runs.join(thread_id, run2["run_id"])

    # Verify
    state = await client.threads.get_state(thread_id)
    assert len(state["values"]["messages"]) >= 4
```

### Example: Test with MCP Server

```python
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.challenge(2)
async def test_challenge2_tool_poisoning(client, thread, challenge_server):
    """Test automatically spawns Challenge 2 server on port 9002"""
    thread_id = thread["thread_id"]

    run = await client.runs.create(
        thread_id=thread_id,
        assistant_id="Challenge2",
        input={"messages": [{"role": "human", "content": "list tools"}]}
    )

    await client.runs.join(thread_id, run["run_id"])

    state = await client.threads.get_state(thread_id)
    messages = state["values"]["messages"]

    # Verify tool was called
    tool_messages = [m for m in messages if hasattr(m, "type") and m.type == "tool"]
    assert len(tool_messages) > 0
```

## 🐛 Troubleshooting

### Issue: "MCP server script not found"
**Solution**: Set the correct `DVMCP_SERVER_PATH`:
```bash
export DVMCP_SERVER_PATH="/path/to/damn-vulnerable-MCP-server"
```

### Issue: "LangGraph API not responding"
**Solution**: Ensure `langgraph dev` is running:
```bash
langgraph dev  # In a separate terminal
```

### Issue: "Challenge server failed to start"
**Solution**: Check if the port is already in use:
```bash
lsof -i :9001  # Check if port 9001 is in use
kill -9 <PID>  # Kill the process if needed
```

### Issue: Tests timing out
**Solution**: Increase timeout or check server logs:
```bash
pytest tests/ -v --timeout=60
```

## 📊 Continuous Integration

### GitHub Actions Example

```yaml
name: Test LangGraph Agents

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Clone DVMCP Server
        run: |
          git clone https://github.com/harishsg993010/damn-vulnerable-MCP-server.git
          echo "DVMCP_SERVER_PATH=$(pwd)/damn-vulnerable-MCP-server" >> $GITHUB_ENV

      - name: Start LangGraph
        run: langgraph dev &

      - name: Run Tests
        run: pytest tests/ -v --tb=short
```

## 📝 Best Practices

1. **Always use fixtures**: Use `client` and `thread` fixtures for cleanup
2. **Mark integration tests**: Use `@pytest.mark.integration` for tests requiring servers
3. **Specify challenge servers**: Use `@pytest.mark.challenge(num)` to auto-spawn servers
4. **Test in isolation**: Each test gets its own thread for independence
5. **Clean up resources**: Fixtures handle cleanup automatically
6. **Use descriptive names**: Test function names should describe what they test

## 🔍 Test Coverage

Current test coverage:
- ✅ Conversation persistence
- ✅ Function calling / tool execution
- ✅ MCP server integration (Challenges 1-3)
- ✅ Challenge configuration loading
- ✅ Error handling
- ✅ Multi-agent testing
- 🔜 All 10 challenge vulnerabilities (in progress)
- 🔜 Performance/load testing
- 🔜 Security validation tests

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [LangGraph SDK](https://langchain-ai.github.io/langgraph/)
- [Damn Vulnerable MCP Server](https://github.com/harishsg993010/damn-vulnerable-MCP-server)
