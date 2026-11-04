"""
iCREATE Automation Engine v2 - Advanced Automation Engine + MCP Standard + Connector Sockets
Standards: MCP 2024-11-05, JSON-RPC 2.0, OpenAPI 3.0 Tool Schema, WebSocket RFC 6455

Install:
pip install pyyaml rich websockets pydantic

Run:
1. Stdio (for Claude Desktop / Cursor): python automation_engine_mcp.py --mcp stdio
2. WebSocket Server: python automation_engine_mcp.py --mcp websocket --port 8765
3. TCP Socket: python automation_engine_mcp.py --mcp socket --port 9000
4. Normal DAG run: python automation_engine_mcp.py --run parallel
"""

from __future__ import annotations
import asyncio
import json
import time
import sys
import socket
import inspect
import logging
import traceback
import threading
import argparse
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import sqlite3

# Optional deps
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
try:
    from rich.logging import RichHandler
    logging.basicConfig(level=logging.INFO, handlers=[RichHandler(rich_tracebacks=True)])
    HAS_RICH = True
except ImportError:
    logging.basicConfig(level=logging.INFO)
    HAS_RICH = False

logger = logging.getLogger("iCREATE Automation Engine-MCP")

# ===================== CORE ENGINE (from v1) =====================
class TaskStatus(Enum):
    PENDING = "pending"; RUNNING = "running"; SUCCESS = "success"
    FAILED = "failed"; SKIPPED = "skipped"; RETRYING = "retrying"

@dataclass
class RetryPolicy:
    max_retries: int = 3; backoff_factor: float = 2.0
    initial_delay: float = 1.0; max_delay: float = 30.0
    retry_on: tuple = (Exception,)

@dataclass
class RateLimit:
    calls: int = 10; period: float = 60.0

@dataclass
class TaskResult:
    task_id: str; status: TaskStatus; output: Any = None
    error: Optional[str] = None; attempts: int = 1
    duration: float = 0.0; timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Task:
    id: str; func: Callable; dependencies: List[str] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    rate_limit: Optional[RateLimit] = None; timeout: float = 300.0
    condition: Optional[Callable[[Dict], bool]] = None; description: str = ""
    is_async: bool = False; metadata: Dict = field(default_factory=dict)
    input_schema: Dict = field(default_factory=dict)  # For MCP/OpenAPI

class EventBus:
    def __init__(self): self._listeners: Dict[str, List[Callable]] = {}
    def on(self, event: str, fn: Callable): self._listeners.setdefault(event, []).append(fn)
    def emit(self, event: str, *args, **kwargs):
        for fn in self._listeners.get(event, []):
            try: fn(*args, **kwargs)
            except Exception as e: logger.error(f"Event error {event}: {e}")

class StateStore:
    def __init__(self, db_path: str = "automation.db"):
        self.db_path = db_path; self._lock = threading.Lock(); self._init_db()
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, task_id TEXT,
                status TEXT, output TEXT, error TEXT, duration REAL, timestamp TEXT)""")
    def save(self, run_id: str, result: TaskResult):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO runs (run_id, task_id, status, output, error, duration, timestamp) VALUES (?,?,?,?,?,?,?)",
                    (run_id, result.task_id, result.status.value, json.dumps(str(result.output))[:5000], result.error, result.duration, result.timestamp))

class AutomationEngine:
    def __init__(self, name="iCREATE Automation Engine-MCP", max_workers=10, db_path="automation.db"):
        self.name = name; self.tasks: Dict[str, Task] = {}; self.results: Dict[str, TaskResult] = {}
        self.event_bus = EventBus(); self.state_store = StateStore(db_path)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S"); self.global_context: Dict[str, Any] = {}
        logger.info(f"Engine [{self.name}] ready | run_id={self.run_id}")

    def task(self, task_id=None, dependencies=None, retry=None, rate_limit=None, timeout=300, condition=None, description=""):
        def decorator(fn: Callable):
            tid = task_id or fn.__name__
            # Auto-generate OpenAPI schema from signature
            sig = inspect.signature(fn)
            props = {}
            for pname, param in sig.parameters.items():
                if pname == 'ctx': continue
                props[pname] = {"type": "string", "description": f"param {pname}"}
            schema = {"type": "object", "properties": props, "required": []}
            t = Task(id=tid, func=fn, dependencies=dependencies or [], retry_policy=retry or RetryPolicy(),
                     rate_limit=rate_limit, timeout=timeout, condition=condition, description=description,
                     is_async=inspect.iscoroutinefunction(fn), input_schema=schema)
            self.tasks[tid] = t
            return fn
        return decorator

    def _topological_sort(self) -> List[str]:
        visited, temp, order = set(), set(), []
        def visit(node):
            if node in temp: raise ValueError(f"Circular dep at {node}")
            if node not in visited:
                temp.add(node)
                for dep in self.tasks[node].dependencies:
                    if dep not in self.tasks: raise ValueError(f"Unknown dep {dep}")
                    visit(dep)
                temp.remove(node); visited.add(node); order.append(node)
        for tid in self.tasks:
            if tid not in visited: visit(tid)
        return order

    def _execute_single(self, task: Task, extra_args: Dict = None) -> TaskResult:
        start = time.time(); attempts = 0; last_error = None
        ctx = {**self.global_context, **(extra_args or {})}
        if task.condition and not task.condition(ctx):
            return TaskResult(task.id, TaskStatus.SKIPPED)
        while attempts <= task.retry_policy.max_retries:
            attempts += 1
            try:
                self.event_bus.emit("task_start", task.id)
                if task.is_async:
                    output = asyncio.run(task.func(ctx))
                else:
                    output = task.func(ctx)
                duration = time.time() - start
                result = TaskResult(task.id, TaskStatus.SUCCESS, output=output, attempts=attempts, duration=duration)
                self.global_context[task.id] = output
                self.event_bus.emit("task_success", task.id, output)
                return result
            except Exception as e:
                last_error = traceback.format_exc()
                if attempts <= task.retry_policy.max_retries:
                    delay = min(task.retry_policy.initial_delay * (task.retry_policy.backoff_factor ** (attempts-1)), task.retry_policy.max_delay)
                    time.sleep(delay)
                else: break
        return TaskResult(task.id, TaskStatus.FAILED, error=last_error, attempts=attempts, duration=time.time()-start)

    def run_parallel(self, inputs: Dict[str, Dict] = None):
        # Simple parallel DAG
        order = self._topological_sort()
        for tid in order:
            extra = (inputs or {}).get(tid, {})
            res = self._execute_single(self.tasks[tid], extra)
            self.results[tid] = res
            self.state_store.save(self.run_id, res)
        return self.results

# ===================== MCP STANDARD PROTOCOL =====================
class MCPProtocol:
    """Implements MCP 2024-11-05 + JSON-RPC 2.0 standard"""
    PROTOCOL_VERSION = "2024-11-05"
    
    @staticmethod
    def make_response(id: Any, result: Any):
        return {"jsonrpc": "2.0", "id": id, "result": result}
    
    @staticmethod
    def make_error(id: Any, code: int, message: str, data: Any = None):
        err = {"code": code, "message": message}
        if data: err["data"] = data
        return {"jsonrpc": "2.0", "id": id, "error": err}

    @staticmethod
    def make_notification(method: str, params: Any = None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None: msg["params"] = params
        return msg

class MCPServer:
    """Exposes AutomationEngine tasks as MCP Tools"""
    def __init__(self, engine: AutomationEngine):
        self.engine = engine
        self.initialized = False

    def get_capabilities(self):
        return {
            "protocolVersion": MCPProtocol.PROTOCOL_VERSION,
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
                "logging": {}
            },
            "serverInfo": {"name": self.engine.name, "version": "2.0.0"}
        }

    def list_tools(self):
        tools = []
        for tid, task in self.engine.tasks.items():
            tools.append({
                "name": tid,
                "description": task.description or f"Automation task {tid}",
                "inputSchema": task.input_schema or {"type": "object", "properties": {}, "required": []},
                "metadata": {"dependencies": task.dependencies, "timeout": task.timeout}
            })
        # Add engine control tools
        tools.extend([
            {"name": "engine_run_all", "description": "Run all tasks in DAG order", "inputSchema": {"type": "object", "properties": {}, "required": []}},
            {"name": "engine_status", "description": "Get engine status and last results", "inputSchema": {"type": "object", "properties": {}, "required": []}},
            {"name": "engine_list_tasks", "description": "List all registered automation tasks", "inputSchema": {"type": "object", "properties": {}, "required": []}},
        ])
        return {"tools": tools}

    def list_resources(self):
        return {"resources": [
            {"uri": "automation://state/last_run", "name": "Last Run Report", "mimeType": "application/json", "description": "Last automation run results"},
            {"uri": "automation://db/history", "name": "Run History DB", "mimeType": "application/json", "description": "SQLite history"},
        ]}

    def list_prompts(self):
        return {"prompts": [
            {"name": "create_automation", "description": "Create a new automation workflow", "arguments": [{"name": "goal", "description": "Automation goal", "required": True}]},
            {"name": "debug_task", "description": "Debug a failed task", "arguments": [{"name": "task_id", "description": "Task ID to debug", "required": True}]},
        ]}

    def handle_request(self, req: Dict) -> Dict:
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        try:
            if method == "initialize":
                self.initialized = True
                return MCPProtocol.make_response(req_id, self.get_capabilities())

            if not self.initialized and method not in ["ping"]:
                return MCPProtocol.make_error(req_id, -32002, "Server not initialized")

            if method == "ping":
                return MCPProtocol.make_response(req_id, {})

            if method == "tools/list":
                return MCPProtocol.make_response(req_id, self.list_tools())

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                return self.call_tool(req_id, tool_name, arguments)

            if method == "resources/list":
                return MCPProtocol.make_response(req_id, self.list_resources())

            if method == "resources/read":
                uri = params.get("uri")
                return MCPProtocol.make_response(req_id, {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(self.engine.results, default=str)}]})

            if method == "prompts/list":
                return MCPProtocol.make_response(req_id, self.list_prompts())

            if method == "prompts/get":
                name = params.get("name")
                return MCPProtocol.make_response(req_id, {"description": f"Prompt {name}", "messages": [{"role": "user", "content": {"type": "text", "text": f"Execute prompt {name} with args {params.get('arguments')}"}}]})

            return MCPProtocol.make_error(req_id, -32601, f"Method not found: {method}")

        except Exception as e:
            logger.exception(f"MCP handle error: {e}")
            return MCPProtocol.make_error(req_id, -32603, "Internal error", str(e))

    def call_tool(self, req_id, tool_name: str, arguments: Dict):
        try:
            if tool_name == "engine_run_all":
                results = self.engine.run_parallel()
                return MCPProtocol.make_response(req_id, {"content": [{"type": "text", "text": json.dumps({k: v.status.value for k,v in results.items()}, indent=2)}], "isError": False})

            if tool_name == "engine_status":
                return MCPProtocol.make_response(req_id, {"content": [{"type": "text", "text": json.dumps({"run_id": self.engine.run_id, "tasks": list(self.engine.tasks.keys()), "results": {k: {"status": v.status.value, "duration": v.duration} for k,v in self.engine.results.items()}}, indent=2)}], "isError": False})

            if tool_name == "engine_list_tasks":
                return MCPProtocol.make_response(req_id, {"content": [{"type": "text", "text": json.dumps(self.list_tools(), indent=2)}], "isError": False})

            if tool_name in self.engine.tasks:
                task = self.engine.tasks[tool_name]
                result = self.engine._execute_single(task, extra_args=arguments)
                self.engine.results[tool_name] = result
                if result.status == TaskStatus.SUCCESS:
                    return MCPProtocol.make_response(req_id, {"content": [{"type": "text", "text": f"Task {tool_name} success: {json.dumps(result.output, indent=2, default=str)[:4000]}"}], "isError": False})
                else:
                    return MCPProtocol.make_response(req_id, {"content": [{"type": "text", "text": f"Task {tool_name} failed: {result.error[:2000]}"}], "isError": True})

            return MCPProtocol.make_error(req_id, -32602, f"Unknown tool: {tool_name}")

        except Exception as e:
            return MCPProtocol.make_error(req_id, -32603, f"Tool call failed: {e}", traceback.format_exc())

# ===================== CONNECTOR SOCKETS (STANDARDS) =====================
class BaseConnector:
    """Base for all transport connectors"""
    def __init__(self, mcp_server: MCPServer): self.mcp_server = mcp_server

class StdioConnector(BaseConnector):
    """MCP Standard: Stdio transport - for Claude Desktop, Cursor, Windsurf"""
    def run(self):
        logger.info("STDIO Connector started - waiting for JSON-RPC on stdin")
        for line in sys.stdin:
            line=line.strip()
            if not line: continue
            try:
                req = json.loads(line)
                # Handle batch or single
                if isinstance(req, list):
                    responses = [self.mcp_server.handle_request(r) for r in req]
                    print(json.dumps(responses), flush=True)
                else:
                    resp = self.mcp_server.handle_request(req)
                    print(json.dumps(resp), flush=True)
            except Exception as e:
                err = MCPProtocol.make_error(None, -32700, "Parse error", str(e))
                print(json.dumps(err), flush=True)

class SocketConnector(BaseConnector):
    """Advanced: Raw TCP Socket with JSON-RPC framing (newline delimited) + Auth + Heartbeat"""
    def __init__(self, mcp_server, host="0.0.0.0", port=9000, auth_token=None):
        super().__init__(mcp_server)
        self.host = host; self.port = port; self.auth_token = auth_token

    def handle_client(self, conn, addr):
        logger.info(f"Socket client connected: {addr}")
        conn.settimeout(300) # 5min heartbeat
        try:
            # Auth handshake (optional)
            if self.auth_token:
                conn.sendall((json.dumps({"method": "auth_required"})+"\n").encode())
                data = conn.recv(4096).decode().strip()
                auth = json.loads(data)
                if auth.get("token") != self.auth_token:
                    conn.sendall((json.dumps(MCPProtocol.make_error(None, -32001, "Unauthorized"))+"\n").encode())
                    conn.close(); return
            # Main loop
            buffer = ""
            while True:
                data = conn.recv(4096).decode()
                if not data: break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip(): continue
                    req = json.loads(line)
                    resp = self.mcp_server.handle_request(req)
                    conn.sendall((json.dumps(resp)+"\n").encode())
        except Exception as e:
            logger.error(f"Socket client error {addr}: {e}")
        finally:
            conn.close(); logger.info(f"Socket client disconnected: {addr}")

    def run(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port)); srv.listen(100)
        logger.info(f"TCP Socket Connector listening on {self.host}:{self.port} (JSON-RPC newline)")
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

class WebSocketConnector(BaseConnector):
    """Advanced: WebSocket Connector (RFC 6455) - for web clients, n8n, Make, custom dashboards"""
    def __init__(self, mcp_server, host="0.0.0.0", port=8765, auth_token=None):
        super().__init__(mcp_server)
        self.host = host; self.port = port; self.auth_token = auth_token

    async def ws_handler(self, websocket):
        client = websocket.remote_address
        logger.info(f"WS client connected: {client}")
        try:
            # Optional auth via first message
            if self.auth_token:
                await websocket.send(json.dumps({"method": "auth_required", "params": {"type": "bearer"}}))
                msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                auth = json.loads(msg)
                if auth.get("token") != self.auth_token:
                    await websocket.send(json.dumps(MCPProtocol.make_error(None, -32001, "Unauthorized")))
                    return
            async for message in websocket:
                try:
                    req = json.loads(message)
                    if isinstance(req, list):
                        responses = [self.mcp_server.handle_request(r) for r in req]
                        await websocket.send(json.dumps(responses))
                    else:
                        # Heartbeat
                        if req.get("method") == "ping":
                            await websocket.send(json.dumps(MCPProtocol.make_response(req.get("id"), {"pong": True, "ts": time.time()})))
                            continue
                        resp = self.mcp_server.handle_request(req)
                        await websocket.send(json.dumps(resp))
                except Exception as e:
                    await websocket.send(json.dumps(MCPProtocol.make_error(None, -32700, "Parse error", str(e))))
        except Exception as e:
            logger.error(f"WS error {client}: {e}")
        finally:
            logger.info(f"WS disconnected: {client}")

    def run(self):
        if not HAS_WEBSOCKETS:
            logger.error("websockets lib not installed. pip install websockets")
            return
        async def start():
            async with websockets.serve(self.ws_handler, self.host, self.port, ping_interval=20, ping_timeout=10, max_size=10*1024*1024):
                logger.info(f"WebSocket Connector listening on ws://{self.host}:{self.port}")
                await asyncio.Future()
        asyncio.run(start())

# ===================== EXAMPLE TASKS (iCREATE) =====================
def build_engine():
    engine = AutomationEngine(name="iCREATE-MCP-Engine", max_workers=10)

    @engine.task(task_id="scrape_trends", description="Scrape trending topics for content ideas - returns 3 trends", retry=RetryPolicy(max_retries=2))
    def scrape_trends(ctx):
        time.sleep(0.5)
        return {"trends": ["AI Automation 2025", "MCP Protocol", "No-code Tools"], "source": "mock"}

    @engine.task(task_id="generate_content", dependencies=["scrape_trends"], description="Generate content draft from trends")
    def generate_content(ctx):
        trends = ctx.get("scrape_trends", {}).get("trends", [])
        draft = f"Top trend today: {trends[0] if trends else 'AI'} - Here's why it matters..."
        return {"draft": draft, "length": len(draft)}

    @engine.task(task_id="publish_draft", dependencies=["generate_content"], description="Publish draft to output folder and return file path")
    def publish_draft(ctx):
        content = ctx.get("generate_content")
        Path("output").mkdir(exist_ok=True)
        out_path = Path("output/draft.json")
        out_path.write_text(json.dumps(content, indent=2))
        return {"published": True, "path": str(out_path)}

    @engine.task(task_id="webhook_notify", dependencies=["publish_draft"], description="Send webhook notification (requires url param)")
    def webhook_notify(ctx):
        import urllib.request
        url = ctx.get("url", "")
        payload = json.dumps({"event": "automation_done", "run_id": engine.run_id}).encode()
        if url:
            try:
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
                return {"notified": True, "url": url}
            except Exception as e:
                return {"notified": False, "error": str(e)}
        return {"notified": False, "reason": "no url provided"}

    return engine

# ===================== MAIN CLI =====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iCREATE Automation Engine MCP Engine")
    parser.add_argument("--mcp", choices=["stdio", "socket", "websocket", "none"], default="none", help="MCP transport")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--auth", default=None, help="Auth token for socket/ws")
    parser.add_argument("--run", choices=["parallel", "sequential"], default=None, help="Run DAG directly")
    args = parser.parse_args()

    engine = build_engine()
    mcp_server = MCPServer(engine)

    if args.run:
        print(f"Running {args.run} mode...")
        engine.run_parallel()
        print(json.dumps({k: v.status.value for k,v in engine.results.items()}, indent=2))
    elif args.mcp == "stdio":
        connector = StdioConnector(mcp_server)
        connector.run()
    elif args.mcp == "socket":
        connector = SocketConnector(mcp_server, host=args.host, port=args.port, auth_token=args.auth)
        connector.run()
    elif args.mcp == "websocket":
        connector = WebSocketConnector(mcp_server, host=args.host, port=args.port, auth_token=args.auth)
        connector.run()
    else:
        # Show help and example client config
        print("""
iCREATE Automation Engine v2 Ready.

Example Claude Desktop config (claude_desktop_config.json):
{
  "mcpServers": {
    "icreate-automation": {
      "command": "python",
      "args": ["PATH_TO/automation_engine_mcp.py", "--mcp", "stdio"],
      "env": {}
    }
  }
}

WebSocket client test:
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        await ws.send(json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}))
        print(await ws.recv())
        await ws.send(json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list"}))
        print(await ws.recv())
asyncio.run(test())

TCP Socket test:
import socket, json
s=socket.socket(); s.connect(('localhost',9000))
s.sendall((json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/list"})+"\\n").encode())
print(s.recv(8192).decode())
        """)
        # Default run for demo
        engine.run_parallel()
        print("Demo run done:", engine.results)
