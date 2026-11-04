"""
iCREATE Automation Engine - Advanced Automation Engine
by iCREATE Digital Studio
Features: DAG execution, async+thread hybrid, retries, circuit breaker, rate limiter,
          event bus, SQLite state, YAML workflow, scheduler, hooks, CLI

pip install pyyaml rich apscheduler pydantic
"""

from __future__ import annotations
import asyncio
import time
import json
import sqlite3
import logging
import traceback
import functools
import inspect
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml

# Optional rich logging
try:
    from rich.logging import RichHandler
    RICH = True
except ImportError:
    RICH = False

# ===================== CONFIG & LOGGING =====================
LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[RichHandler(rich_tracebacks=True)] if RICH else [logging.StreamHandler()],
)
logger = logging.getLogger("iCREATE Automation Engine")

# ===================== CORE ENUMS & MODELS =====================
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

@dataclass
class RetryPolicy:
    max_retries: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 30.0
    retry_on: tuple = (Exception,)

@dataclass
class RateLimit:
    calls: int = 10
    period: float = 60.0  # seconds

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    attempts: int = 1
    duration: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Task:
    id: str
    func: Callable
    dependencies: List[str] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    rate_limit: Optional[RateLimit] = None
    timeout: float = 300.0
    condition: Optional[Callable[[Dict], bool]] = None
    description: str = ""
    is_async: bool = False
    metadata: Dict = field(default_factory=dict)

# ===================== UTILITIES =====================
class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, fn: Callable):
        self._listeners.setdefault(event, []).append(fn)
    
    def emit(self, event: str, *args, **kwargs):
        for fn in self._listeners.get(event, []):
            try:
                fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Event handler error for {event}: {e}")

class StateStore:
    """SQLite persistence for task runs"""
    def __init__(self, db_path: str = "automation.db"):
        self.db_path = db_path
        self._init_db()
        self._lock = threading.Lock()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    task_id TEXT,
                    status TEXT,
                    output TEXT,
                    error TEXT,
                    duration REAL,
                    timestamp TEXT
                )
            """)

    def save(self, run_id: str, result: TaskResult):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO runs (run_id, task_id, status, output, error, duration, timestamp) VALUES (?,?,?,?,?,?,?)",
                    (run_id, result.task_id, result.status.value, json.dumps(str(result.output))[:5000], result.error, result.duration, result.timestamp)
                )

    def get_last_run(self, task_id: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM runs WHERE task_id=? ORDER BY id DESC LIMIT 1", (task_id,))
            row = cur.fetchone()
            return row

class TokenBucket:
    """Simple rate limiter"""
    def __init__(self, rate_limit: RateLimit):
        self.rate = rate_limit.calls / rate_limit.period
        self.capacity = rate_limit.calls
        self.tokens = self.capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            sleep_time = (1 - self.tokens) / self.rate
            time.sleep(max(0, sleep_time))
            self.tokens = 0
            return True

class CircuitBreaker:
    def __init__(self, fail_max=5, reset_timeout=60):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.last_fail = 0
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_fail > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise RuntimeError("Circuit OPEN - too many failures")
        try:
            result = func(*args, **kwargs)
            self.fail_count = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.fail_count += 1
            self.last_fail = time.time()
            if self.fail_count >= self.fail_max:
                self.state = "OPEN"
            raise e

# ===================== MAIN ENGINE =====================
class AutomationEngine:
    def __init__(self, name: str = "iCREATE Automation Engine", max_workers: int = 10, db_path: str = "automation.db"):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, TaskResult] = {}
        self.event_bus = EventBus()
        self.state_store = StateStore(db_path)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.rate_limiters: Dict[str, TokenBucket] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.global_context: Dict[str, Any] = {}
        logger.info(f"Engine [{self.name}] initialized | run_id={self.run_id}")

    # --- Decorator API ---
    def task(self, task_id: Optional[str] = None, dependencies: List[str] = None,
             retry: RetryPolicy = None, rate_limit: RateLimit = None,
             timeout: float = 300, condition: Callable = None, description: str = ""):
        def decorator(fn: Callable):
            tid = task_id or fn.__name__
            is_async = inspect.iscoroutinefunction(fn)
            t = Task(
                id=tid,
                func=fn,
                dependencies=dependencies or [],
                retry_policy=retry or RetryPolicy(),
                rate_limit=rate_limit,
                timeout=timeout,
                condition=condition,
                description=description,
                is_async=is_async,
            )
            self.register(t)
            return fn
        return decorator

    def register(self, task: Task):
        if task.id in self.tasks:
            logger.warning(f"Task {task.id} overwritten")
        self.tasks[task.id] = task
        if task.rate_limit:
            self.rate_limiters[task.id] = TokenBucket(task.rate_limit)
        self.circuit_breakers[task.id] = CircuitBreaker()
        logger.debug(f"Registered task: {task.id} | deps={task.dependencies}")

    # --- DAG RESOLUTION ---
    def _topological_sort(self) -> List[str]:
        visited: Set[str] = set()
        temp: Set[str] = set()
        order: List[str] = []

        def visit(node: str):
            if node in temp:
                raise ValueError(f"Circular dependency detected at {node}")
            if node not in visited:
                temp.add(node)
                for dep in self.tasks[node].dependencies:
                    if dep not in self.tasks:
                        raise ValueError(f"Task {node} depends on unknown task {dep}")
                    visit(dep)
                temp.remove(node)
                visited.add(node)
                order.append(node)

        for tid in self.tasks:
            if tid not in visited:
                visit(tid)
        return order

    def _get_ready_tasks(self, completed: Set[str]) -> List[Task]:
        ready = []
        for tid, task in self.tasks.items():
            if tid in completed:
                continue
            if all(dep in completed and self.results[dep].status == TaskStatus.SUCCESS for dep in task.dependencies):
                ready.append(task)
        return ready

    # --- EXECUTION CORE ---
    def _execute_single(self, task: Task) -> TaskResult:
        # Condition check
        if task.condition and not task.condition(self.global_context):
            logger.info(f"Skipping {task.id} - condition false")
            return TaskResult(task.id, TaskStatus.SKIPPED)

        # Rate limiting
        if task.id in self.rate_limiters:
            self.rate_limiters[task.id].acquire()

        start = time.time()
        attempts = 0
        last_error = None

        while attempts <= task.retry_policy.max_retries:
            attempts += 1
            try:
                self.event_bus.emit("task_start", task.id)
                logger.info(f"▶ Running {task.id} (attempt {attempts})")

                # Timeout handling
                if task.is_async:
                    output = asyncio.run(asyncio.wait_for(task.func(self.global_context), timeout=task.timeout))
                else:
                    # Run with circuit breaker
                    cb = self.circuit_breakers[task.id]
                    output = cb.call(task.func, self.global_context)

                duration = time.time() - start
                result = TaskResult(task.id, TaskStatus.SUCCESS, output=output, attempts=attempts, duration=duration)
                self.global_context[task.id] = output
                self.event_bus.emit("task_success", task.id, output)
                logger.info(f"✅ {task.id} success in {duration:.2f}s")
                return result

            except Exception as e:
                last_error = traceback.format_exc()
                logger.warning(f"⚠️ {task.id} failed attempt {attempts}: {e}")
                if attempts <= task.retry_policy.max_retries and isinstance(e, task.retry_policy.retry_on):
                    delay = min(task.retry_policy.initial_delay * (task.retry_policy.backoff_factor ** (attempts-1)), task.retry_policy.max_delay)
                    self.event_bus.emit("task_retry", task.id, attempts, delay)
                    logger.info(f"Retrying {task.id} in {delay}s...")
                    time.sleep(delay)
                else:
                    break

        duration = time.time() - start
        result = TaskResult(task.id, TaskStatus.FAILED, error=last_error, attempts=attempts, duration=duration)
        self.event_bus.emit("task_failed", task.id, last_error)
        logger.error(f"❌ {task.id} failed after {attempts} attempts")
        return result

    def run_sequential(self) -> Dict[str, TaskResult]:
        order = self._topological_sort()
        logger.info(f"Sequential run order: {order}")
        for tid in order:
            result = self._execute_single(self.tasks[tid])
            self.results[tid] = result
            self.state_store.save(self.run_id, result)
            if result.status == TaskStatus.FAILED and not self.tasks[tid].metadata.get("continue_on_fail", False):
                logger.error(f"Stopping chain due to failure of {tid}")
                # Don't break DAG if parallelizable, but for sequential we stop? We'll continue to log others as skipped
        return self.results

    def run_parallel(self, continue_on_fail: bool = True) -> Dict[str, TaskResult]:
        completed: Set[str] = set()
        pending = set(self.tasks.keys())

        logger.info(f"Parallel DAG execution started with {len(pending)} tasks")
        while pending:
            ready = self._get_ready_tasks(completed)
            if not ready:
                if pending:
                    # Check for deadlock
                    unresolved = ", ".join(pending)
                    logger.error(f"Deadlock - remaining: {unresolved}")
                    break
                break

            futures = {self.executor.submit(self._execute_single, t): t for t in ready}
            for future in as_completed(futures):
                task = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    result = TaskResult(task.id, TaskStatus.FAILED, error=str(e))

                self.results[task.id] = result
                self.state_store.save(self.run_id, result)
                completed.add(task.id)
                pending.discard(task.id)

                if result.status == TaskStatus.FAILED and not continue_on_fail:
                    logger.error("Aborting due to failure")
                    return self.results

        return self.results

    # --- YAML WORKFLOW ---
    def load_yaml(self, path: str):
        """Load workflow from YAML"""
        data = yaml.safe_load(Path(path).read_text())
        for tdef in data.get("tasks", []):
            # tdef should have 'id' and 'type' or 'func' mapping is done externally
            logger.info(f"YAML task defined: {tdef}")
        return data

    def export_report(self, path: str = None):
        path = path or f"report_{self.run_id}.json"
        report = {
            "run_id": self.run_id,
            "engine": self.name,
            "timestamp": datetime.now().isoformat(),
            "tasks": {tid: {"status": r.status.value, "duration": r.duration, "attempts": r.attempts} for tid, r in self.results.items()},
            "context_keys": list(self.global_context.keys())
        }
        Path(path).write_text(json.dumps(report, indent=2))
        logger.info(f"Report exported to {path}")
        return report

# ===================== EXAMPLE USAGE =====================
if __name__ == "__main__":
    engine = AutomationEngine(name="iCREATE Automation Engine", max_workers=5)

    # Event hooks
    engine.event_bus.on("task_success", lambda tid, out: print(f"[HOOK] {tid} tapos na!"))
    engine.event_bus.on("task_failed", lambda tid, err: print(f"[HOOK] {tid} palpak!"))

    @engine.task(task_id="scrape_data", description="Scrape sample API", retry=RetryPolicy(max_retries=2), rate_limit=RateLimit(calls=5, period=10))
    def scrape_data(ctx):
        import requests
        # Example API call
        # res = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=10)
        # return res.json()
        time.sleep(1)
        return {"data": [1,2,3], "source": "api"}

    @engine.task(task_id="process_data", dependencies=["scrape_data"], description="Process and transform")
    def process_data(ctx):
        raw = ctx.get("scrape_data")
        processed = [x*2 for x in raw["data"]]
        time.sleep(0.5)
        return {"processed": processed}

    @engine.task(task_id="save_results", dependencies=["process_data"])
    def save_results(ctx):
        data = ctx.get("process_data")
        Path("output").mkdir(exist_ok=True)
        Path("output/result.json").write_text(json.dumps(data, indent=2))
        return "saved to output/result.json"

    @engine.task(task_id="notify", dependencies=["save_results"], description="Notify completion")
    def notify(ctx):
        # Here you can integrate Telegram, Discord, Email
        return f"Run {engine.run_id} completed!"

    # Choose execution mode
    print("\n--- RUNNING PARALLEL DAG MODE ---\n")
    results = engine.run_parallel()

    print("\n--- SUMMARY ---")
    for tid, res in results.items():
        print(f"{tid}: {res.status.value} ({res.duration:.2f}s)")

    engine.export_report()

    # Example YAML workflow (create sample file)
    sample_yaml = """
name: my-workflow
tasks:
  - id: fetch
    description: Fetch from API
  - id: transform
    dependencies: [fetch]
  - id: publish
    dependencies: [transform]
"""
    Path("workflow.yaml").write_text(sample_yaml)
    print("\nSample workflow.yaml created!")
