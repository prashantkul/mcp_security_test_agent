"""
Test SSE client using MCP Python SDK
Based on: https://github.com/modelcontextprotocol/python-sdk
"""
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_sse_connection():
    """Test SSE connection to Challenge1 MCP server"""
    sse_url = "http://localhost:9001/sse"

    print(f"Connecting to MCP server at {sse_url}...")

    try:
        # Create SSE client using the MCP SDK
        async with sse_client(sse_url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                print("✅ Connected and initialized!")

                # List available resources
                print("\n📁 Listing resources...")
                resources = await session.list_resources()
                print(f"Found {len(resources.resources)} resources:")
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")

                # List available tools
                print("\n🛠️  Listing tools...")
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Read a resource
                if len(resources.resources) > 0:
                    print("\n📄 Reading first resource...")
                    first_resource = resources.resources[0]
                    result = await session.read_resource(first_resource.uri)
                    print(f"Content: {result.contents[0].text[:200]}...")

                # Call a tool if available
                if len(tools.tools) > 0:
                    print("\n⚙️  Testing tool call...")
                    first_tool = tools.tools[0]
                    if first_tool.name == "get_user_info":
                        result = await session.call_tool(first_tool.name, {"username": "admin"})
                        print(f"Tool result: {result.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sse_connection())
