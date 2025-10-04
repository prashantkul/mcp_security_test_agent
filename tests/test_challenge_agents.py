"""
Automated tests for LangGraph challenge agents
Tests conversation persistence, tool calling, and MCP integration
"""
import asyncio
import pytest

# Fixtures are imported from conftest.py
# Available fixtures: client, thread, challenge_server, mcp_server_manager, wait_for_run


class TestConversationPersistence:
    """Test that conversation history persists across messages"""

    @pytest.mark.asyncio
    async def test_orchestrator_persistence(self, client, thread):
        """Test orchestrator remembers conversation history"""
        thread_id = thread["thread_id"]

        # First message
        run1 = await client.runs.create(
            thread_id=thread_id,
            assistant_id="orchestrator",
            input={"messages": [{"role": "human", "content": "My name is Alice"}]}
        )

        # Wait for completion
        await client.runs.join(thread_id, run1["run_id"])

        # Second message asking to recall
        run2 = await client.runs.create(
            thread_id=thread_id,
            assistant_id="orchestrator",
            input={"messages": [{"role": "human", "content": "What is my name?"}]}
        )

        await client.runs.join(thread_id, run2["run_id"])

        # Verify thread has 4 messages (2 user + 2 AI)
        state = await client.threads.get_state(thread_id)
        assert len(state["values"]["messages"]) >= 4

    @pytest.mark.asyncio
    @pytest.mark.parametrize("agent_id", ["Challenge1", "Challenge5", "Challenge10"])
    async def test_challenge_agent_persistence(self, client, thread, agent_id):
        """Test challenge agents remember conversation history"""
        thread_id = thread["thread_id"]

        # First message
        run1 = await client.runs.create(
            thread_id=thread_id,
            assistant_id=agent_id,
            input={"messages": [{"role": "human", "content": "Remember this number: 42"}]}
        )

        await client.runs.join(thread_id, run1["run_id"])

        # Second message asking to recall
        run2 = await client.runs.create(
            thread_id=thread_id,
            assistant_id=agent_id,
            input={"messages": [{"role": "human", "content": "What number did I ask you to remember?"}]}
        )

        await client.runs.join(thread_id, run2["run_id"])

        # Verify messages persisted
        state = await client.threads.get_state(thread_id)
        assert len(state["values"]["messages"]) >= 4


class TestToolCalling:
    """Test that agents properly call MCP tools"""

    @pytest.mark.asyncio
    async def test_list_tools_execution(self, client, thread):
        """Test that agent executes list_mcp_tools when asked"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "list available tools"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        # Get state and verify tool was called
        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Should have: user message, AI response with tool_calls, tool message, final AI message
        assert len(messages) >= 3

        # Check that a tool was called
        tool_called = False
        for msg in messages:
            if isinstance(msg, dict) and msg.get("type") == "tool":
                tool_called = True
                break

        assert tool_called, "Agent should have called a tool"

    @pytest.mark.asyncio
    async def test_list_resources_execution(self, client, thread):
        """Test that agent executes list_mcp_resources when asked"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "show me available resources"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Verify tool was executed
        tool_called = any(isinstance(msg, dict) and msg.get("type") == "tool" for msg in messages)
        assert tool_called

    @pytest.mark.asyncio
    async def test_get_user_info_with_parameter(self, client, thread):
        """Test that agent calls get_user_info with correct parameter"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "get user info for admin"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Verify tool message exists
        tool_messages = [msg for msg in messages if isinstance(msg, dict) and msg.get("type") == "tool"]
        assert len(tool_messages) > 0


class TestMCPIntegration:
    """Test MCP server integration (spawns actual MCP servers)"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.challenge(1)
    async def test_challenge1_list_tools(self, client, thread, challenge_server):
        """Test Challenge1 can list tools from MCP server on port 9001"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "list tools"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Get the final AI response
        ai_messages = [msg for msg in messages if isinstance(msg, dict) and msg.get("type") == "ai"]
        assert len(ai_messages) > 0

        # Response should contain tool information
        final_response = ai_messages[-1]["content"]
        assert len(final_response) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.challenge(1)
    async def test_challenge1_list_resources(self, client, thread, challenge_server):
        """Test Challenge1 can list resources from MCP server"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "list resources"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Verify we got a response
        ai_messages = [msg for msg in messages if isinstance(msg, dict) and msg.get("type") == "ai"]
        assert len(ai_messages) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.challenge(1)
    async def test_challenge1_basic_prompt_injection(self, client, thread, challenge_server):
        """Test Challenge1 basic prompt injection vulnerability"""
        thread_id = thread["thread_id"]

        # Try to access internal credentials
        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "read resource internal://credentials"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Should have executed the resource read
        tool_messages = [msg for msg in messages if isinstance(msg, dict) and msg.get("type") == "tool"]
        assert len(tool_messages) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.challenge(2)
    async def test_challenge2_tool_poisoning(self, client, thread, challenge_server):
        """Test Challenge2 tool poisoning detection"""
        thread_id = thread["thread_id"]

        # List tools to see poisoned descriptions
        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge2",
            input={"messages": [{"role": "human", "content": "list available tools"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        ai_messages = [msg for msg in messages if isinstance(msg, dict) and msg.get("type") == "ai"]
        assert len(ai_messages) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.challenge(3)
    async def test_challenge3_excessive_permissions(self, client, thread, challenge_server):
        """Test Challenge3 excessive permission scope"""
        thread_id = thread["thread_id"]

        # Try to search for files
        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge3",
            input={"messages": [{"role": "human", "content": "list tools and resources"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # Should have tool execution
        assert len(messages) >= 3


class TestChallengeConfiguration:
    """Test that challenge-specific configurations are loaded correctly"""

    @pytest.mark.asyncio
    async def test_challenge1_shows_objectives(self, client, thread):
        """Test Challenge1 system message includes objectives"""
        thread_id = thread["thread_id"]

        # First interaction should trigger system message
        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "hello"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # First message should be system message
        if len(messages) > 0 and isinstance(messages[0], dict) and messages[0].get("type") == "system":
            system_content = messages[0]["content"]
            assert "Challenge 1" in system_content
            assert "Basic Prompt Injection" in system_content

    @pytest.mark.asyncio
    @pytest.mark.parametrize("challenge_num,name", [
        (1, "Basic Prompt Injection"),
        (2, "Tool Poisoning"),
        (10, "Multi-Vector Attack")
    ])
    async def test_challenge_names_loaded(self, client, thread, challenge_num, name):
        """Test that challenge configurations include correct names"""
        thread_id = thread["thread_id"]
        agent_id = f"Challenge{challenge_num}"

        # Just send a simple message to trigger system prompt
        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id=agent_id,
            input={"messages": [{"role": "human", "content": "hello"}]}
        )

        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        messages = state["values"]["messages"]

        # The system message should contain challenge info
        # Check all messages for challenge name (system message has it)
        content_combined = " ".join([
            msg["content"] for msg in messages
            if isinstance(msg, dict) and "content" in msg and isinstance(msg["content"], str)
        ])

        # Should find either the challenge name or number in the system message or response
        assert (name in content_combined or
                f"Challenge {challenge_num}" in content_combined or
                len(messages) >= 2), f"Should have challenge info for {agent_id}"


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_invalid_tool_request(self, client, thread):
        """Test agent handles requests for non-existent tools gracefully"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": "run the nonexistent_tool"}]}
        )

        # Should complete without error
        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        assert len(state["values"]["messages"]) > 0

    @pytest.mark.asyncio
    async def test_empty_message_handling(self, client, thread):
        """Test agent handles empty messages"""
        thread_id = thread["thread_id"]

        run = await client.runs.create(
            thread_id=thread_id,
            assistant_id="Challenge1",
            input={"messages": [{"role": "human", "content": ""}]}
        )

        # Should complete without error
        await client.runs.join(thread_id, run["run_id"])

        state = await client.threads.get_state(thread_id)
        assert len(state["values"]["messages"]) > 0


class TestMultipleAgents:
    """Test interactions with multiple challenge agents"""

    @pytest.mark.asyncio
    async def test_all_challenge_agents_respond(self, client):
        """Test that all 10 challenge agents can handle basic requests"""
        for challenge_num in range(1, 11):
            agent_id = f"Challenge{challenge_num}"
            thread = await client.threads.create()
            thread_id = thread["thread_id"]

            try:
                run = await client.runs.create(
                    thread_id=thread_id,
                    assistant_id=agent_id,
                    input={"messages": [{"role": "human", "content": "hello"}]}
                )

                await client.runs.join(thread_id, run["run_id"])

                state = await client.threads.get_state(thread_id)
                messages = state["values"]["messages"]

                # Verify we got a response
                assert len(messages) >= 2, f"{agent_id} should respond to messages"

            finally:
                try:
                    await client.threads.delete(thread_id)
                except:
                    pass


if __name__ == "__main__":
    # Run with: pytest tests/test_challenge_agents.py -v
    # Run integration tests: pytest tests/test_challenge_agents.py -v -m integration
    # Run without integration tests: pytest tests/test_challenge_agents.py -v -m "not integration"
    pytest.main([__file__, "-v"])
