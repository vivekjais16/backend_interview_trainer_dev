from typing import List, Dict, Any, Optional

MINDMAP_DATA: List[Dict[str, Any]] = [
    {
        "slug": "python-internals",
        "title": "Python Internals, GIL & Memory Management",
        "category": "python_internals",
        "order_index": 1,
        "description": "Deep CPython memory architecture, garbage collector cycles, GIL nuances, and performance tuning.",
        "mermaid_diagram": """
graph TD
    A["Python Internals"] --> B["Memory Management"]
    A --> C["Global Interpreter Lock (GIL)"]
    A --> D["Object Model & MRO"]
    
    B --> B1["Reference Counting (Immediate Deallocation)"]
    B --> B2["Generational GC (Gen 0, 1, 2 for Cyclic Refs)"]
    B --> B3["PyMalloc Allocator (Arenas, Pools, Blocks)"]
    
    C --> C1["Thread Synchronization in CPython"]
    C --> C2["I/O Bound (Releases GIL)"]
    C --> C3["CPU Bound (GIL Contention & Free-Threading in 3.13)"]
    
    D --> D1["__new__ vs __init__ Lifecycle"]
    D --> D2["Descriptors & Metaclasses"]
    D --> D3["C3 Linearization Algorithm"]
""",
        "nodes": [
            {
                "id": "py-gil",
                "label": "Global Interpreter Lock (GIL)",
                "depth_level": "mid",
                "mnc_importance": "Asked in 90% of Google, Uber, and High-Frequency Trading Python interviews.",
                "summary": "CPython's mutex preventing multiple native OS threads from executing Python bytecodes simultaneously. I/O syscalls release the GIL, while CPU-intensive tasks thrash thread switches.",
                "code_sample": """# CPU-bound tasks do not speed up with standard threading due to the GIL
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def compute(n):
    return sum(i * i for i in range(n))

# For CPU-bound: Use ProcessPoolExecutor to spawn separate OS processes with distinct GILs
with ProcessPoolExecutor() as executor:
    results = list(executor.map(compute, [10**7, 10**7]))
""",
                "common_traps": [
                    "Assuming threading speeds up mathematical computation in Python.",
                    "Failing to understand that native C-extensions (like NumPy) release the GIL during calculations."
                ],
                "interview_cross_questions": [
                    "Why did Guido van Rossum choose reference counting + GIL instead of fine-grained locks?",
                    "How does Python 3.13's experimental `--disable-gil` (free-threading) change multi-threaded performance?"
                ]
            },
            {
                "id": "py-gc",
                "label": "Generational Garbage Collection",
                "depth_level": "senior",
                "mnc_importance": "Critical for diagnosing memory leaks and long-running FastAPI microservices.",
                "summary": "Primary deallocation happens immediately when reference count drops to zero (`Py_DECREF`). For circular references (`a.b = b; b.a = a`), Python uses a 3-generation cyclic garbage collector with thresholds.",
                "code_sample": """import gc
import sys

class Node:
    def __init__(self, name):
        self.name = name
        self.neighbor = None

a = Node("A")
b = Node("B")
a.neighbor = b
b.neighbor = a # Cyclic reference created!

del a
del b
# Ref counts are not zero! They will only be cleaned up by gc.collect()
print(f"Unreachable collected: {gc.collect()}")
""",
                "common_traps": [
                    "Believing `del x` immediately frees memory. It only decrements the reference count.",
                    "Memory fragmentation in long-running processes where memory is released to pymalloc but not returned to the OS."
                ],
                "interview_cross_questions": [
                    "What are the heuristic thresholds for Gen 0, Gen 1, and Gen 2 collections?",
                    "How would you profile a memory leak in a production FastAPI container using `tracemalloc` and `objgraph`?"
                ]
            }
        ]
    },
    {
        "slug": "async-concurrency",
        "title": "High-Throughput Asyncio & Concurrency",
        "category": "async_concurrency",
        "order_index": 2,
        "description": "Event loops, coroutines, non-blocking I/O, TaskGroup, and thread pool offloading.",
        "mermaid_diagram": """
graph TD
    A["Asyncio Architecture"] --> B["Event Loop (epoll / kqueue)"]
    A --> C["Concurrency Primitives"]
    A --> D["Offloading Strategies"]
    
    B --> B1["Single-Threaded Cooperative Multitasking"]
    B --> B2["Coroutines (async def / yield from)"]
    B --> B3["Tasks & Futures"]
    
    C --> C1["asyncio.gather vs asyncio.TaskGroup"]
    C --> C2["asyncio.Semaphore (Concurrency Throttling)"]
    C --> C3["asyncio.Queue (Producer-Consumer)"]
    
    D --> D1["run_in_executor (ThreadPool for Blocking I/O)"]
    D --> D2["ProcessPoolExecutor (CPU-bound offload)"]
""",
        "nodes": [
            {
                "id": "async-event-loop",
                "label": "Event Loop & Blocking Gotchas",
                "depth_level": "mid",
                "mnc_importance": "The #1 reason FastAPI services suffer catastrophic P99 latency spikes.",
                "summary": "Asyncio runs on a single thread using OS notification mechanisms (`epoll` on Linux, `kqueue` on macOS). If any function calls synchronous blocking code (`time.sleep` or synchronous DB driver), the entire event loop halts for all concurrent users.",
                "code_sample": """import asyncio
import time

# WRONG in production: Blocks the entire server event loop!
# async def bad_route():
#     time.sleep(2) # STALLS all other requests!

# CORRECT: Use non-blocking async primitives or run in worker thread
async def good_route():
    await asyncio.sleep(2) # Yields control to event loop

# For legacy synchronous libraries:
async def safe_sync_call():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, time.sleep, 2)
""",
                "common_traps": [
                    "Using `requests.get()` inside `async def` instead of `httpx.AsyncClient()`.",
                    "Using synchronous SQLAlchemy without async driver in an async route."
                ],
                "interview_cross_questions": [
                    "What happens when you declare `def route()` instead of `async def route()` in FastAPI?",
                    "How does `asyncio.TaskGroup` in Python 3.11+ handle exception propagation compared to `asyncio.gather(..., return_exceptions=False)`?"
                ]
            }
        ]
    },
    {
        "slug": "fastapi-architecture",
        "title": "FastAPI, Pydantic V2 & Production Microservices",
        "category": "fastapi_architecture",
        "order_index": 3,
        "description": "Dependency injection graph, middleware pipeline, Pydantic V2 Rust core, and ASGI lifecycle.",
        "mermaid_diagram": """
graph TD
    A["FastAPI Architecture"] --> B["Dependency Injection (Depends)"]
    A --> C["Data Validation (Pydantic V2)"]
    A --> D["ASGI Lifecycle & Middlewares"]
    
    B --> B1["Hierarchical Sub-dependencies"]
    B --> B2["Yield Dependencies (DB Session cleanup)"]
    B --> B3["Security & Auth Scopes"]
    
    C --> C1["Rust-powered Serialization (pydantic-core)"]
    C --> C2["model_validate & Field constraints"]
    C --> C3["Zero-copy parsing"]
    
    D --> D1["Lifespan Context Manager (Startup/Shutdown)"]
    D --> D2["CORS, Rate Limiter & Auth Middlewares"]
    D --> D3["Exception Handlers & Custom Error Schemas"]
""",
        "nodes": [
            {
                "id": "fastapi-di",
                "label": "Dependency Injection System",
                "depth_level": "senior",
                "mnc_importance": "Core architecture design question in modern Python backend interviews.",
                "summary": "FastAPI resolves dependencies as a Directed Acyclic Graph (DAG). `yield` dependencies run teardown logic (like closing DB sessions or releasing locks) guaranteed even if an exception occurs.",
                "code_sample": """from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db # Injected into route
    finally:
        db.close() # Guaranteed teardown

@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
""",
                "common_traps": [
                    "Creating a new DB engine inside every request rather than sharing a singleton pool.",
                    "Failing to handle database rollback inside teardown blocks."
                ],
                "interview_cross_questions": [
                    "How does FastAPI cache dependency results when `use_cache=True`?",
                    "How would you implement hierarchical tenant isolation using FastAPI dependencies?"
                ]
            }
        ]
    },
    {
        "slug": "mysql-database-internals",
        "title": "MySQL InnoDB Internals, Indexing & Transactions",
        "category": "sql_database_internals",
        "order_index": 4,
        "description": "B+ Trees, Clustered Indexes, MVCC, Isolation levels, Deadlock mitigation, and EXPLAIN plans.",
        "mermaid_diagram": """
graph TD
    A["MySQL InnoDB Internals"] --> B["Storage Architecture"]
    A --> C["Indexing Strategy"]
    A --> D["Transactions & Concurrency (ACID)"]
    
    B --> B1["Buffer Pool (LRU Cache)"]
    B --> B2["Redo Log (WAL - Write Ahead Logging)"]
    B --> B3["Undo Log (MVCC & Rollback)"]
    
    C --> C1["Clustered Index (Primary Key on Leaf Page)"]
    C --> C2["Secondary Index (Points to PK)"]
    C --> C3["Covering Index (Zero Table Lookup)"]
    C --> C4["Leftmost Prefix Matching"]
    
    D --> D1["MVCC (Multi-Version Concurrency Control)"]
    D --> D2["Isolation Levels: RC vs RR (Next-Key Lock)"]
    D --> D3["Deadlock Detection & Resolution"]
""",
        "nodes": [
            {
                "id": "mysql-btree",
                "label": "B+ Tree Indexing & Leftmost Prefix Rule",
                "depth_level": "senior",
                "mnc_importance": "Asked in nearly all database rounds across FAANG and FinTech.",
                "summary": "InnoDB organizes data in B+ Trees where leaf nodes contain actual row data (Clustered Index) linked as a doubly-linked list. Composite indexes `(A, B, C)` can only be used by queries filtering on `A`, or `(A, B)`, or `(A, B, C)` due to the leftmost prefix rule.",
                "code_sample": """-- Composite Index:
CREATE INDEX idx_user_status_date ON orders(customer_id, status, order_date);

-- USES INDEX effectively:
SELECT * FROM orders WHERE customer_id = 42 AND status = 'COMPLETED';

-- CANNOT USE idx_user_status_date effectively (causes full table scan):
SELECT * FROM orders WHERE status = 'COMPLETED';
""",
                "common_traps": [
                    "Over-indexing tables, causing severe write/insert slowdowns and buffer pool churn.",
                    "Using functions on indexed columns (`WHERE YEAR(created_at) = 2026`), which invalidates B-Tree index lookups."
                ],
                "interview_cross_questions": [
                    "Why does InnoDB use B+ Trees instead of B-Trees or Binary Search Trees?",
                    "Explain the difference between Next-Key Lock, Gap Lock, and Record Lock in MySQL Repeatable Read."
                ]
            }
        ]
    },
    {
        "slug": "system-design-troubleshooting",
        "title": "MNC Production Troubleshooting & System Design",
        "category": "system_design_mnc",
        "order_index": 5,
        "description": "Flash sales, distributed locks, idempotency, rate limiting, and live incident post-mortems.",
        "mermaid_diagram": """
graph TD
    A["Production MNC Scenarios"] --> B["High Concurrency Patterns"]
    A --> C["Resiliency & Fault Tolerance"]
    A --> D["Live Incident Debugging"]
    
    B --> B1["Flash Sale Inventory Reservation"]
    B --> B2["Distributed Locking (Redis Redlock / Lua)"]
    B --> B3["Idempotent API Design (Idempotency Keys)"]
    
    C --> C1["Rate Limiter (Token Bucket / Sliding Window)"]
    C --> C2["Circuit Breakers (Fail-fast fallback)"]
    C --> C3["Connection Pool Starvation Prevention"]
    
    D --> D1["P99 Latency Spikes Troubleshooting"]
    D --> D2["Database Deadlocks in High-Write Tables"]
    D --> D3["Memory Leaks in Containerized Pods"]
""",
        "nodes": [
            {
                "id": "system-flash-sale",
                "label": "Flash-Sale Inventory Reservation & Race Conditions",
                "depth_level": "architect",
                "mnc_importance": "The ultimate test of real-time backend concurrency for Senior/Lead roles.",
                "summary": "Preventing overselling under 100,000 simultaneous checkouts without locking the entire database table. Combines Redis atomic decrement with Lua scripts and optimistic DB updates.",
                "code_sample": """-- Atomic SQL decrement with non-negative guard:
UPDATE inventory
SET stock = stock - 1
WHERE product_id = :pid AND stock >= 1;
-- If affected rows == 0 -> Out of Stock!
""",
                "common_traps": [
                    "Reading stock in Python (`SELECT stock`), checking `if stock > 0:`, and then updating (`UPDATE`). That is a massive race condition!",
                    "Holding a long DB transaction open while calling external payment gateways."
                ],
                "interview_cross_questions": [
                    "How would you ensure zero duplicate charges if an order times out midway through payment capture?",
                    "How do you design a sliding-window rate limiter in Redis using sorted sets (ZSET)?"
                ]
            }
        ]
    }
]

def get_all_mindmaps() -> List[Dict[str, Any]]:
    return MINDMAP_DATA

def get_mindmap_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    for m in MINDMAP_DATA:
        if m["slug"] == slug:
            return m
    return None
