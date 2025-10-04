"""
Pytest configuration and fixtures for automated testing
Manages MCP server lifecycle and test environment setup
"""
import asyncio
import os
import subprocess
import time
import pytest
from pathlib import Path
from langgraph_sdk import get_client


# Configuration
LANGGRAPH_URL = "http://127.0.0.1:2024"
DVMCP_SERVER_PATH = os.getenv(
    "DVMCP_SERVER_PATH",
    str(Path.home() / "Documents/source-code/vulnerable_mcp/damn-vulnerable-MCP-server")
)

# Challenge server configurations
CHALLENGE_SERVERS = {
    1: {"port": 9001, "path": "challenges/easy/challenge1/server_sse.py"},
    2: {"port": 9002, "path": "challenges/easy/challenge2/server_sse.py"},
    3: {"port": 9003, "path": "challenges/easy/challenge3/server_sse.py"},
    4: {"port": 9004, "path": "challenges/medium/challenge4/server_sse.py"},
    5: {"port": 9005, "path": "challenges/medium/challenge5/server_sse.py"},
    6: {"port": 9006, "path": "challenges/medium/challenge6/server_sse.py"},
    7: {"port": 9007, "path": "challenges/medium/challenge7/server_sse.py"},
    8: {"port": 9008, "path": "challenges/hard/challenge8/server_sse.py"},
    9: {"port": 9009, "path": "challenges/hard/challenge9/server_sse.py"},
    10: {"port": 9010, "path": "challenges/hard/challenge10/server_sse.py"},
}


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires MCP servers)"
    )
    config.addinivalue_line(
        "markers", "challenge(num): mark test to run specific challenge server"
    )


class MCPServerManager:
    """Manages MCP server processes for testing"""

    def __init__(self, dvmcp_path: str):
        self.dvmcp_path = Path(dvmcp_path)
        self.processes = {}

    def start_server(self, challenge_num: int) -> subprocess.Popen:
        """Start an MCP challenge server"""
        import httpx

        config = CHALLENGE_SERVERS[challenge_num]
        server_script = self.dvmcp_path / config["path"]

        if not server_script.exists():
            raise FileNotFoundError(
                f"MCP server script not found: {server_script}\n"
                f"Set DVMCP_SERVER_PATH environment variable to the correct path."
            )

        # Determine which Python to use
        # First check if there's a conda env for DVMCP
        dvmcp_conda_env = os.getenv("DVMCP_CONDA_ENV", "vul_mcp")

        # Try to use conda environment if available
        conda_python = subprocess.run(
            ["conda", "run", "-n", dvmcp_conda_env, "which", "python"],
            capture_output=True,
            text=True
        )

        if conda_python.returncode == 0:
            # Use conda run to execute in the proper environment
            cmd = ["conda", "run", "-n", dvmcp_conda_env, "python", str(server_script)]
            print(f"  Using conda environment: {dvmcp_conda_env}")
        else:
            # Fall back to system python
            cmd = ["python", str(server_script)]
            print(f"  Warning: conda env '{dvmcp_conda_env}' not found, using system python")

        # Start the server process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=server_script.parent,
        )

        # Wait for server to start and verify it's responding
        port = config["port"]
        max_retries = 10
        retry_delay = 0.5

        for i in range(max_retries):
            time.sleep(retry_delay)

            # Check if process crashed
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise RuntimeError(
                    f"Challenge {challenge_num} server failed to start\n"
                    f"stdout: {stdout.decode()}\n"
                    f"stderr: {stderr.decode()}"
                )

            # Try to connect to the SSE endpoint
            try:
                # Just check if we can connect - SSE will hang/stream so use short timeout
                with httpx.Client(timeout=0.5) as client:
                    try:
                        response = client.get(f"http://localhost:{port}/sse")
                        # If we get here without exception, server is responding
                        print(f"✓ Challenge {challenge_num} server ready on port {port}")
                        self.processes[challenge_num] = process
                        return process
                    except httpx.ReadTimeout:
                        # SSE endpoints will timeout while streaming - this is actually good!
                        # It means the server is running and responding
                        print(f"✓ Challenge {challenge_num} server ready on port {port}")
                        self.processes[challenge_num] = process
                        return process
            except httpx.ConnectError:
                # Server not ready yet, continue waiting
                continue

        # If we get here, server didn't start in time
        process.terminate()
        raise RuntimeError(
            f"Challenge {challenge_num} server did not respond on port {port} "
            f"after {max_retries * retry_delay} seconds"
        )

    def stop_server(self, challenge_num: int):
        """Stop an MCP challenge server"""
        if challenge_num in self.processes:
            process = self.processes[challenge_num]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.processes[challenge_num]
            print(f"✓ Stopped Challenge {challenge_num} server")

    def stop_all(self):
        """Stop all running MCP servers"""
        for challenge_num in list(self.processes.keys()):
            self.stop_server(challenge_num)

    def is_running(self, challenge_num: int) -> bool:
        """Check if a server is running"""
        if challenge_num in self.processes:
            return self.processes[challenge_num].poll() is None
        return False


@pytest.fixture(scope="session")
def mcp_server_manager():
    """Create MCP server manager for the test session"""
    manager = MCPServerManager(DVMCP_SERVER_PATH)
    yield manager
    # Cleanup: stop all servers after tests
    manager.stop_all()


@pytest.fixture
def challenge_server(request, mcp_server_manager):
    """
    Start a specific challenge server for a test.
    Use with: @pytest.mark.challenge(1)
    """
    # Get challenge number from marker
    marker = request.node.get_closest_marker("challenge")
    if marker is None:
        pytest.skip("Test requires @pytest.mark.challenge(num) marker")

    challenge_num = marker.args[0]

    # Start server if not already running
    if not mcp_server_manager.is_running(challenge_num):
        mcp_server_manager.start_server(challenge_num)

    yield challenge_num

    # Note: We don't stop servers here to allow reuse across tests
    # They'll be stopped at session end by mcp_server_manager fixture


@pytest.fixture(scope="session")
async def langgraph_client():
    """Create LangGraph SDK client (session-scoped for reuse)"""
    return get_client(url=LANGGRAPH_URL)


@pytest.fixture
async def client():
    """Create LangGraph SDK client (function-scoped)"""
    return get_client(url=LANGGRAPH_URL)


@pytest.fixture
async def thread(client):
    """Create a new thread for each test and cleanup after"""
    thread = await client.threads.create()
    yield thread
    # Cleanup after test
    try:
        await client.threads.delete(thread["thread_id"])
    except Exception as e:
        print(f"Warning: Failed to delete thread {thread['thread_id']}: {e}")


@pytest.fixture
def wait_for_run():
    """Helper to wait for a run to complete"""
    async def _wait(client, thread_id, run_id, timeout=30):
        """Wait for run to complete with timeout"""
        start = time.time()
        while time.time() - start < timeout:
            run_state = await client.runs.get(thread_id, run_id)
            if run_state["status"] in ["success", "error", "interrupted"]:
                return run_state
            await asyncio.sleep(0.5)
        raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")
    return _wait


# Pytest hooks for better output
def pytest_collection_modifyitems(config, items):
    """Add markers based on test location and name"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower() or "test_mcp" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)


def pytest_report_header(config):
    """Add custom header to test output"""
    return [
        f"LangGraph URL: {LANGGRAPH_URL}",
        f"DVMCP Server Path: {DVMCP_SERVER_PATH}",
        f"Python: {subprocess.check_output(['python', '--version']).decode().strip()}",
    ]
