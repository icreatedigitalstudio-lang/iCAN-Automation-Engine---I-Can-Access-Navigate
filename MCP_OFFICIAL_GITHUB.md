# iCREATE - Official Claude MCP Libraries from GitHub

Kinuha from GitHub: https://github.com/modelcontextprotocol

## Official Organization: modelcontextprotocol

Main repos:
- **modelcontextprotocol/servers** - Reference implementations (7 official + 13 archived) - 82k+ stars【1226890218594320551†L2-L8】
- **modelcontextprotocol/python-sdk** - Python SDK - PyPI: mcp - pip install mcp【1501260572147886394†L6-L17】
- **modelcontextprotocol/typescript-sdk** - TypeScript SDK - npm: @modelcontextprotocol/sdk - npm install @modelcontextprotocol/sdk【5179192244951180265†L8-L19】
- **modelcontextprotocol/go-sdk, java-sdk, kotlin-sdk, csharp-sdk, swift-sdk, rust-sdk, ruby-sdk, php-sdk**
- **modelcontextprotocol/modelcontextprotocol** - Spec + docs
- **modelcontextprotocol/inspector** - MCP Inspector dev tool
- **anthropics/claude-ai-mcp** - Communication hub for Claude.ai MCP integration【4843164869935776215†L53-L56】

## Reference Servers (official, maintained by steering group)

From https://github.com/modelcontextprotocol/servers README:

**Current reference (7):**
- **Everything** - Reference/test server with prompts, resources, tools - supports stdio + Streamable HTTP【1226890218594320551†L45-L46】
- **Fetch** - Web content fetching and conversion【1226890218594320551†L47-L48】
- **Filesystem** - Secure file operations with configurable access controls【1226890218594320551†L49-L50】
- **Git** - Tools to read, search, manipulate Git repositories【1226890218594320551†L51-L52】
- **Memory** - Knowledge graph-based persistent memory system【1226890218594320551†L53-L54】
- **Sequential Thinking** - Dynamic and reflective problem-solving【1226890218594320551†L55-L56】
- **Time** - Time and timezone conversion【1226890218594320551†L57-L58】

**Archived (moved to servers-archived):**
- AWS KB Retrieval, Brave Search, EverArt, GitHub, GitLab, Google Drive, Google Maps, PostgreSQL, Puppeteer, Redis, Sentry, Slack (now Zencoder), SQLite【1226890218594320551†L60-L87】

## Official SDKs

| SDK | Repo | Install | Docs |
|-----|------|---------|------|
| Python | modelcontextprotocol/python-sdk | pip install mcp / uv add mcp | https://py.sdk.modelcontextprotocol.io/ |
| TypeScript | modelcontextprotocol/typescript-sdk | npm install @modelcontextprotocol/sdk | https://modelcontextprotocol.io |
| Go | modelcontextprotocol/go-sdk | go get | - |
| Java | modelcontextprotocol/java-sdk | maven | - |
| Others | kotlin, csharp, swift, rust, ruby, php | - | - |

Python SDK Quick Start (from official README):

```python
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

server = Server("example-server")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [types.Prompt(name="example-prompt", description="An example", arguments=[types.PromptArgument(name="arg1", description="Example", required=True)])]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    return types.GetPromptResult(description="Example", messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text="Example text"))])

async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream, InitializationOptions(server_name="example", server_version="0.1.0", capabilities=server.get_capabilities(notification_options=NotificationOptions(), experimental_capabilities={})))
```

Client:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command="path/to/server", args=[], env=None)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        resources = await session.list_resources()
        tools = await session.list_tools()
        result = await session.call_tool("tool-name", arguments={"arg1": "value"})
```

## Transports

From spec:
- **stdio**: client launches server as subprocess, talks via stdin/stdout, no port. Every reference server serves stdio, only Everything also serves Streamable HTTP【1226890218594320551†L219-L226】
- **Streamable HTTP**: server runs as HTTP service, many clients, URL like http://localhost:3001/mcp【1226890218594320551†L222-L223】

## iCREATE Integration

We have both:
1. **Custom MCP** (`mcp/server.py`) - our full: stdio + websocket :8765 + tcp :8766 + sse :8767 + 22 tools
2. **Official SDK MCP** (`mcp/official_server.py`) - uses pip install mcp, native Claude Desktop compatible, stdio + sse via Starlette

Config for Claude Desktop combining both + official reference servers:

```json
{
  "mcpServers": {
    "icreate": {
      "command": "python",
      "args": ["-m", "pyautoforge.mcp.official_server"],
      "env": {"OLLAMA_BASE_URL": "http://localhost:11434"}
    },
    "icreate-custom": {
      "command": "python",
      "args": ["-m", "pyautoforge.mcp.server"],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "/tmp/test.db"]
    }
  }
}
```

For Windows wrap npx with cmd /c: "command": "cmd", "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"]【1226890218594320551†L148-L168】

Testing without client - use Inspector:
```
npx @modelcontextprotocol/inspector uvx mcp-server-git
npx @modelcontextprotocol/server-everything streamableHttp
npx @modelcontextprotocol/inspector --transport http --server-url http://localhost:3001/mcp
```

## Installation for iCREATE

```bash
# Official SDK
pip install mcp[cli]
# or
uv add "mcp[cli]"

# TypeScript SDK (if building Node servers)
npm install @modelcontextprotocol/sdk

# Reference servers
npx -y @modelcontextprotocol/server-memory
uvx mcp-server-git
npx @modelcontextprotocol/inspector

# For SSE transport
pip install starlette uvicorn
```

## Files in iCREATE now

- src/pyautoforge/mcp/protocol.py - MCP 2024-11-05 protocol
- src/pyautoforge/mcp/server.py - Custom full server (22 tools, 8 resources, 5 prompts)
- src/pyautoforge/mcp/official_server.py - Official SDK server (Claude native)
- src/pyautoforge/mcp/github_servers.py - List of all official reference servers + SDKs
- src/pyautoforge/mcp/client.py - Custom client
- src/pyautoforge/connectors/* - 4 transports (stdio, websocket, tcp, sse) + ConnectorManager
- src/pyautoforge/core/connections.py - ConnectionManager singleton

All downloaded from GitHub org modelcontextprotocol.
