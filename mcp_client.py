"""
MCP Client for interacting with MCP servers
"""
import json
from typing import Dict, Any
from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPClient:
    """Client for interacting with an MCP server"""

    def __init__(self, mcp_url: str):
        """
        Initialize MCP client

        Args:
            mcp_url: SSE endpoint URL (e.g., http://localhost:9001/sse)
        """
        self.mcp_url = mcp_url

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP tool and return results"""
        try:
            streams = sse_client(self.mcp_url)
            read_stream, write_stream = await streams.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            await session.__aexit__(None, None, None)
            await streams.__aexit__(None, None, None)

            content_list = []
            for item in result.content:
                if hasattr(item, 'text'):
                    content_list.append({"type": "text", "text": item.text})
                else:
                    content_list.append(str(item))
            return json.dumps(content_list, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    async def read_resource(self, resource_uri: str) -> str:
        """Read an MCP resource and return contents"""
        try:
            streams = sse_client(self.mcp_url)
            read_stream, write_stream = await streams.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            result = await session.read_resource(resource_uri)
            await session.__aexit__(None, None, None)
            await streams.__aexit__(None, None, None)

            content_list = []
            for item in result.contents:
                if hasattr(item, 'text'):
                    content_dict = {"type": "text", "text": item.text}
                    if hasattr(item, 'uri') and item.uri:
                        content_dict["uri"] = str(item.uri)
                    content_list.append(content_dict)
                else:
                    content_list.append(str(item))
            return json.dumps(content_list, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    async def list_tools(self) -> str:
        """List available MCP tools"""
        try:
            streams = sse_client(self.mcp_url)
            read_stream, write_stream = await streams.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            result = await session.list_tools()
            await session.__aexit__(None, None, None)
            await streams.__aexit__(None, None, None)

            # Extract tools list from result
            tools = result.tools if hasattr(result, 'tools') else (result if isinstance(result, list) else [result])

            tool_list = []
            for t in tools:
                if hasattr(t, 'name'):
                    tool_dict = {"name": t.name}
                    if hasattr(t, 'description') and t.description:
                        tool_dict["description"] = t.description
                    if hasattr(t, 'inputSchema') and t.inputSchema:
                        tool_dict["inputSchema"] = str(t.inputSchema)
                    tool_list.append(tool_dict)
                elif isinstance(t, tuple):
                    tool_list.append({"name": t[0] if len(t) > 0 else None, "description": t[1] if len(t) > 1 else None})
                else:
                    tool_list.append({"info": str(t)})

            return json.dumps(tool_list, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    async def list_resources(self) -> str:
        """List available MCP resources"""
        try:
            streams = sse_client(self.mcp_url)
            read_stream, write_stream = await streams.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            result = await session.list_resources()
            await session.__aexit__(None, None, None)
            await streams.__aexit__(None, None, None)

            resources = result.resources if hasattr(result, 'resources') else (result if isinstance(result, list) else [result])
            resource_list = []
            for r in resources:
                if hasattr(r, 'uri') and hasattr(r, 'name'):
                    res_dict = {"uri": str(r.uri), "name": r.name}
                    if hasattr(r, 'description') and r.description:
                        res_dict["description"] = r.description
                    resource_list.append(res_dict)
            return json.dumps(resource_list, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    async def list_prompts(self) -> str:
        """List available MCP prompts"""
        try:
            streams = sse_client(self.mcp_url)
            read_stream, write_stream = await streams.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            result = await session.list_prompts()
            await session.__aexit__(None, None, None)
            await streams.__aexit__(None, None, None)

            prompts = result.prompts if hasattr(result, 'prompts') else (result if isinstance(result, list) else [result])
            prompt_list = []
            for p in prompts:
                if hasattr(p, 'name'):
                    prompt_dict = {"name": p.name}
                    if hasattr(p, 'description') and p.description:
                        prompt_dict["description"] = p.description
                    if hasattr(p, 'arguments') and p.arguments:
                        prompt_dict["arguments"] = [{"name": arg.name, "description": arg.description if hasattr(arg, 'description') else None, "required": arg.required if hasattr(arg, 'required') else False} for arg in p.arguments]
                    prompt_list.append(prompt_dict)
            return json.dumps(prompt_list, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any] = None) -> str:
        """Get a prompt with optional arguments"""
        try:
            streams = sse_client(self.mcp_url)
            read_stream, write_stream = await streams.__aenter__()
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            result = await session.get_prompt(prompt_name, arguments or {})
            await session.__aexit__(None, None, None)
            await streams.__aexit__(None, None, None)

            # Extract messages from prompt result
            messages_list = []
            if hasattr(result, 'messages'):
                for msg in result.messages:
                    msg_dict = {}
                    if hasattr(msg, 'role'):
                        msg_dict["role"] = msg.role
                    if hasattr(msg, 'content'):
                        if isinstance(msg.content, str):
                            msg_dict["content"] = msg.content
                        elif hasattr(msg.content, 'text'):
                            msg_dict["content"] = msg.content.text
                        else:
                            msg_dict["content"] = str(msg.content)
                    messages_list.append(msg_dict)

            return json.dumps({"messages": messages_list}, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"
