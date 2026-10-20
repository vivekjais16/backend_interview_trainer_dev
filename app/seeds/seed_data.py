from app.models.question import QuestionCategory, QuestionDifficulty

SEED_QUESTIONS = [
    # =========================================================================
    # JUNIOR LEVEL (0 - 2 Years)
    # =========================================================================
    {
        "title": "The Mutable Default Argument Trap in Python",
        "slug": "python-mutable-default-argument",
        "category": QuestionCategory.PYTHON_INTERNALS,
        "difficulty": QuestionDifficulty.BASIC,
        "min_exp_years": 0,
        "max_exp_years": 2,
        "company_tags": ["Amazon", "Microsoft", "TCS", "Infosys"],
        "frequency_score": 98,
        "mindmap_topic": "python-internals",
        "mindmap_node": "py-gil",
        "scenario_text": """
A junior engineer pushed code to a microservice that appends items to a user's shopping basket. 
Under load, users started seeing items belonging to completely different users in their baskets!
Investigate why Python evaluates default arguments only once at function definition time, and fix the function.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of a default argument like a **communal whiteboard in an office conference room**. When Python first defines the function, it sets up that single whiteboard. If everyone who calls the function without bringing their own notebook writes on that communal whiteboard, they all see each other's notes!

### ⚙️ Under The Hood (Why It Happens)
Python functions are objects created at **definition time** (when the code is imported or read), not when the function is called.
Default values are stored in the function's `__defaults__` tuple once. If the default is a mutable object (like a `list` or `dict`), every call that omits the parameter points to the exact same memory address (`id(cart)`).

### 🚀 Step-by-Step Production Fix
1. **Never** put `[]` or `{}` as a default parameter.
2. Use `None` as a safe placeholder: `def add_to_cart(item: str, cart: list | None = None)`.
3. Inside the function, create a brand new list if `cart is None`:
   ```python
   if cart is None:
       cart = []
   cart.append(item)
   ```

### 🎯 30-Second MNC Interview Punchline
*"Never use mutable objects as default arguments in Python because defaults are evaluated once at definition time, not runtime. Always use None as the sentinel value."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# BUGGY IMPLEMENTATION:
def add_to_cart(item: str, cart: list = []) -> list:
    cart.append(item)
    return cart

# Test the behavior:
user1_cart = add_to_cart("MacBook Pro")
print("User 1 Cart:", user1_cart)

user2_cart = add_to_cart("AirPods")
print("User 2 Cart (Notice the bug!):", user2_cart)
""",
        "solution_code": """def add_to_cart(item: str, cart: list | None = None) -> list:
    if cart is None:
        cart = []
    cart.append(item)
    return cart

user1_cart = add_to_cart("MacBook Pro")
print("User 1 Cart:", user1_cart)

user2_cart = add_to_cart("AirPods")
print("User 2 Cart (Fixed):", user2_cart)
""",
        "has_sql_sandbox": False,
        "cross_questions": [
            "Why doesn't this bug happen with immutable types like integers or strings?",
            "How can you inspect default arguments at runtime using `__defaults__` or `inspect` module?",
            "What happens if you use a dataclass with `field(default_factory=list)` instead?"
        ],
        "common_traps": [
            "Thinking `cart = []` creates a new list on every function call.",
            "Using `if not cart:` which causes a bug if an empty list was legitimately passed as an argument."
        ],
        "best_practices": [
            "Always use `None` as default for mutable arguments.",
            "Use typing annotations `list | None = None`."
        ]
    },
    {
        "title": "SQL: Finding the N-th Highest Salary in Department",
        "slug": "sql-nth-highest-salary",
        "category": QuestionCategory.POSTGRES_MYSQL,
        "difficulty": QuestionDifficulty.BASIC,
        "min_exp_years": 0,
        "max_exp_years": 3,
        "company_tags": ["Amazon", "Google", "Oracle", "Goldman Sachs"],
        "frequency_score": 95,
        "mindmap_topic": "postgres-mysql-internals",
        "mindmap_node": "pg-vacuum",
        "scenario_text": """
The HR analytics team needs to find the 2nd highest salary in each department. 
If multiple employees earn the exact same highest salary, they share rank #1, and the next unique salary must be ranked #2.
Write an optimal SQL query using window functions (`DENSE_RANK()`) over the `hr_tech` schema.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of an Olympic medal podium:
- If two runners tie for 1st place (Gold), `DENSE_RANK()` awards the next runner 2nd place (Silver).
- But regular `RANK()` skips 2nd place and jumps straight to 3rd place (Bronze)!
So if an interviewer asks for the 2nd highest salary, `DENSE_RANK()` is mathematically the only correct choice.

### ⚙️ Under The Hood (Why It Happens)
- `ROW_NUMBER()`: Assigns sequential numbers (1, 2, 3...) regardless of ties.
- `RANK()`: Leaves gaps when ties happen (1, 1, 3...).
- `DENSE_RANK()`: Never leaves gaps (1, 1, 2, 3...).
By combining `DENSE_RANK()` with `PARTITION BY department_id`, we compute ranks per department in a single query scan.

### 🚀 Step-by-Step Production Fix
1. Wrap the ranking calculation in a Common Table Expression (CTE) `WITH RankedSalaries AS (...)`.
2. Apply `DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC)`.
3. Filter in the outer query: `WHERE salary_rank = 2`.
4. Create an index on `(department_id, salary DESC)` to avoid full table filesorts.

### 🎯 30-Second MNC Interview Punchline
*"Use DENSE_RANK() instead of RANK() or LIMIT/OFFSET because DENSE_RANK handles ties gracefully without skipping rank numbers, and partitioning guarantees per-department calculation."*
        """,
        "has_python_sandbox": False,
        "has_sql_sandbox": True,
        "sql_schema": "hr_tech",
        "starter_sql": """-- Query the second highest salary using DENSE_RANK()
SELECT 
    name, 
    department_id, 
    salary
FROM employees;
""",
        "solution_sql": """WITH RankedSalaries AS (
    SELECT 
        e.id,
        e.name,
        d.dept_name,
        e.salary,
        DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) as salary_rank
    FROM employees e
    JOIN departments d ON e.department_id = d.id
)
SELECT 
    dept_name,
    name,
    salary,
    salary_rank
FROM RankedSalaries
WHERE salary_rank = 2;
""",
        "cross_questions": [
            "What is the difference in performance between `DENSE_RANK()` vs `LIMIT 1 OFFSET 1`?",
            "What composite index on `employees` would eliminate the need for a full table filesort?",
            "How does MySQL handle NULL values in `ORDER BY salary DESC`?"
        ],
        "common_traps": [
            "Using `LIMIT 1 OFFSET 1` without partitioning, which only gets the second highest salary across the entire company, not per department.",
            "Using `RANK()` instead of `DENSE_RANK()`, causing rank 2 to be skipped if there are two employees tied at rank 1."
        ],
        "best_practices": [
            "Use Common Table Expressions (CTEs) for readable multi-step queries.",
            "Ensure an index exists on `(department_id, salary DESC)`."
        ]
    },

    # =========================================================================
    # MID LEVEL (3 - 5 Years)
    # =========================================================================
    {
        "title": "Fixing Event Loop Starvation in FastAPI Async Endpoints",
        "slug": "fastapi-async-event-loop-starvation",
        "category": QuestionCategory.ASYNC_CONCURRENCY,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["Uber", "Stripe", "DoorDash", "Razorpay"],
        "frequency_score": 96,
        "mindmap_topic": "python-internals",
        "mindmap_node": "py-gil",
        "scenario_text": """
During a promotional campaign, your FastAPI backend suddenly showed 100% CPU on a single core, 
and incoming health-check probes failed with 504 Gateway Timeout.
Upon inspecting the codebase, you discovered an `async def` endpoint calling a blocking third-party SDK.
Simulate the issue in the Python interpreter and fix it using `asyncio.to_thread` / `run_in_executor`.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of the FastAPI event loop like a **fast-food cashier**. 
If the cashier leaves the counter and goes into the kitchen to cook the burger for 5 seconds (blocking synchronous I/O), the entire line of 100 waiting customers freezes!
If the cashier hands the ticket to a kitchen helper in the back (`asyncio.to_thread`), the cashier keeps taking orders without any pause.

### ⚙️ Under The Hood (Why It Happens)
FastAPI runs `async def` routes directly on the single-threaded event loop. If synchronous blocking code (like `time.sleep()`, `requests.get()`, or legacy DB drivers) runs inside `async def`, the entire thread is frozen. No other coroutine can run until that blocking call returns.

### 🚀 Step-by-Step Production Fix
1. If using synchronous I/O inside `async def`, wrap it with `await asyncio.to_thread(func, *args)`.
2. Or use regular `def route()` instead of `async def` (FastAPI automatically runs regular `def` in an external thread pool).
3. Best practice: Switch to native async libraries like `httpx.AsyncClient` or `asyncpg`.

### 🎯 30-Second MNC Interview Punchline
*"Never execute synchronous blocking I/O directly inside async def routes; offload them to a thread pool with asyncio.to_thread or use native non-blocking async libraries."*
        """,
        "has_python_sandbox": True,
        "starter_code": """import asyncio
import time

def legacy_sync_payment_verification(order_id: str) -> bool:
    time.sleep(1) # Simulates blocking synchronous I/O
    return True

async def handle_request_correct(order_id: str):
    # Offload blocking synchronous I/O to thread pool
    return await asyncio.to_thread(legacy_sync_payment_verification, order_id)

async def main():
    start = time.perf_counter()
    print("Testing concurrent execution...")
    results = await asyncio.gather(
        handle_request_correct("ORD-101"),
        handle_request_correct("ORD-102"),
        handle_request_correct("ORD-103")
    )
    print(f"Finished {len(results)} requests in {time.perf_counter() - start:.2f}s (Concurrent!)")

asyncio.run(main())
""",
        "solution_code": """import asyncio
import time

def legacy_sync_payment_verification(order_id: str) -> bool:
    time.sleep(1) # Simulates blocking call
    return True

async def handle_request_correct(order_id: str):
    return await asyncio.to_thread(legacy_sync_payment_verification, order_id)

async def main():
    start = time.perf_counter()
    print("Running 3 requests concurrently...")
    results = await asyncio.gather(
        handle_request_correct("ORD-101"),
        handle_request_correct("ORD-102"),
        handle_request_correct("ORD-103")
    )
    total_time = time.perf_counter() - start
    print(f"Completed {len(results)} orders in {total_time:.2f}s (Concurrent!)")

asyncio.run(main())
""",
        "has_sql_sandbox": False,
        "cross_questions": [
            "What is the default thread pool size for `asyncio.to_thread` in FastAPI?",
            "What happens when the threadpool is completely saturated under 10,000 req/sec?",
            "Why doesn't `asyncio.to_thread` speed up CPU-bound mathematical calculations in Python?"
        ],
        "common_traps": [
            "Assuming making a function `async def` automatically makes all operations inside it non-blocking.",
            "Creating a new `ThreadPoolExecutor` inside each request rather than reusing the global event loop pool."
        ],
        "best_practices": [
            "Use native async libraries (`httpx` instead of `requests`, `asyncpg` instead of `psycopg2`).",
            "Use `asyncio.to_thread` for legacy synchronous blocking I/O."
        ]
    },
    {
        "title": "Redis Caching: Cache Stampede & Sliding Window Rate Limiting",
        "slug": "redis-cache-stampede-rate-limiter",
        "category": QuestionCategory.REDIS_CACHING,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["Uber", "Stripe", "Swiggy", "Zomato"],
        "frequency_score": 97,
        "mindmap_topic": "redis-caching",
        "mindmap_node": "redis-rate-limiter",
        "scenario_text": """
At 12:00 PM, a viral product's cache expires in Redis.
Within 1 second, 50,000 requests hit the server, find the cache empty, and simultaneously query the primary database.
This 'Cache Stampede' crashes the database.
Test Redis caching commands and implement sliding-window rate limiting using Redis Sorted Sets (ZSET).
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of a store's morning coffee special. At 9:00 AM, the coffee pot runs out. If 1,000 customers all notice at the exact same second and all 1,000 run into the kitchen to brew coffee, the kitchen collapses! 
A **Redis Mutex Lock** lets only the first person into the kitchen to brew coffee while everyone else waits outside for the fresh pot.

### ⚙️ Under The Hood (Why It Happens)
When a high-traffic cache key expires, thousands of concurrent requests get a cache miss simultaneously and hammer the primary database at the same instant (Cache Stampede / Thundering Herd).

### 🚀 Step-by-Step Production Fix
1. **Cache Mutex**: The first worker acquires a lock (`SET lock_key uuid NX EX 5`) and queries the DB; other requests wait or return slightly stale data.
2. **Add TTL Jitter**: Set expiration with random variation (e.g. `3600 + random(0, 300)`) so keys don't all expire at the exact same second.
3. **Sliding-Window Rate Limiting**: Use Redis Sorted Sets (ZSET) to evict expired timestamps with `ZREMRANGEBYSCORE` and count with `ZCARD`.

### 🎯 30-Second MNC Interview Punchline
*"Mitigate cache stampedes using distributed mutex locks or early background refresh, and always add random TTL jitter so keys never expire simultaneously."*
        """,
        "has_python_sandbox": True,
        "has_redis_sandbox": True,
        "starter_redis": """-- Redis CLI commands for sliding window rate limiter:
-- 1. Remove old timestamps older than 60 seconds ago
ZREMRANGEBYSCORE user:101:ratelimit 0 1710000000

-- 2. Count requests in current window
ZCARD user:101:ratelimit

-- 3. Record new request timestamp
ZADD user:101:ratelimit 1710000050 "req-uuid-1"

-- 4. Inspect keys and TTL
KEYS user:*
""",
        "solution_redis": """-- Full rate limiter sequence:
ZREMRANGEBYSCORE user:101:ratelimit 0 1710000000
ZADD user:101:ratelimit 1710000050 "req-uuid-1"
EXPIRE user:101:ratelimit 60
ZCARD user:101:ratelimit
""",
        "starter_code": """# Python simulation of Cache Mutex Lock:
import time

cache = {}
locks = set()

def fetch_product_safe(product_id: str):
    if product_id in cache:
        return cache[product_id]
    
    # Mutex lock check: Only 1 worker queries DB
    if product_id not in locks:
        locks.add(product_id)
        print(f"[DB QUERY] Refreshing cache for {product_id}...")
        time.sleep(0.05) # DB latency
        cache[product_id] = {"id": product_id, "name": "iPhone 16 Pro", "price": 1099}
        locks.remove(product_id)
        return cache[product_id]
    else:
        print(f"[WAIT] Another request is already refreshing {product_id}...")
        return {"status": "refreshing, please retry"}

print(fetch_product_safe("SKU-01"))
print(fetch_product_safe("SKU-01")) # Cache hit!
""",
        "solution_code": """# Safe Cache-Aside with Lock
import time

cache = {"SKU-01": {"id": "SKU-01", "name": "iPhone 16 Pro", "price": 1099}}

def get_product(pid: str):
    return cache.get(pid)

print(get_product("SKU-01"))
""",
        "cross_questions": [
            "What is the difference between Cache-Aside, Write-Through, and Write-Behind?",
            "How do you prevent Cache Avalanche when thousands of keys are configured with the exact same 3600s TTL?",
            "How does a Bloom filter help prevent Cache Penetration for non-existent IDs?"
        ],
        "common_traps": [
            "Setting static cache expiration times without adding random jitter.",
            "Holding database locks while waiting on Redis network responses."
        ],
        "best_practices": [
            "Add random jitter (+/- 10%) to cache expiration times.",
            "Use Redis Lua scripts for atomic rate limiting."
        ]
    },
    {
        "title": "MongoDB Aggregation Pipeline & The ESR Indexing Rule",
        "slug": "mongodb-aggregation-esr-rule",
        "category": QuestionCategory.MONGODB_NOSQL,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["Uber", "PayPay", "DoorDash", "Coinbase"],
        "frequency_score": 93,
        "mindmap_topic": "mongodb-nosql",
        "mindmap_node": "mongo-esr",
        "scenario_text": """
An e-commerce order management service queries MongoDB to calculate total revenue per customer tier for delivered orders.
Write a MongoDB aggregation pipeline using `$match`, `$unwind`, and `$group`.
Explain the ESR (Equality, Sort, Range) rule to design the ideal compound index for this query.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of searching in a physical library:
1. First, walk to the right department: Fiction (**Equality**).
2. Next, walk to the shelf already sorted alphabetically by Author (**Sort**).
3. Finally, pick only books published after 2020 (**Range**).
If you put Range before Sort, the librarian has to pull 10,000 books off the shelf and sort them on the floor in memory!

### ⚙️ Under The Hood (Why It Happens)
MongoDB evaluates compound indexes left-to-right.
- **E (Equality)**: Filters out non-matching documents immediately.
- **S (Sort)**: Lets MongoDB read in B-Tree index order, avoiding an in-memory blocking sort.
- **R (Range)**: Filters values (`$gt`, `$lt`) at the end of the scan.

### 🚀 Step-by-Step Production Fix
1. Put `$match` as the very first stage in the aggregation pipeline.
2. Build compound indexes in strict **Equality -> Sort -> Range** order:
   `db.orders.createIndex({ "status": 1, "created_at": -1, "total_amount": 1 })`.
3. Never put `$unwind` before `$match`.

### 🎯 30-Second MNC Interview Punchline
*"Always design compound indexes following the ESR rule (Equality, Sort, Range) to guarantee efficient index scans and eliminate in-memory sorting bottlenecks."*
        """,
        "has_nosql_sandbox": True,
        "starter_nosql": """db.orders.aggregate([
  { "$match": { "status": "DELIVERED" } },
  { "$group": { 
      "_id": "$customer.tier", 
      "total_revenue": { "$sum": "$total_amount" } 
    } 
  },
  { "$sort": { "total_revenue": -1 } }
])""",
        "solution_nosql": """db.orders.aggregate([
  { "$match": { "status": "DELIVERED" } },
  { "$group": { 
      "_id": "$customer.tier", 
      "total_revenue": { "$sum": "$total_amount" } 
    } 
  },
  { "$sort": { "total_revenue": -1 } }
])""",
        "has_python_sandbox": False,
        "has_sql_sandbox": False,
        "cross_questions": [
            "What happens if you place `$unwind` before `$match` in a large MongoDB collection?",
            "What is the maximum BSON document size limit in MongoDB, and how does it influence embedding vs referencing?",
            "What is the difference between `w: 1` and `w: 'majority'` write concern during network partitions?"
        ],
        "common_traps": [
            "Embedding unbounded arrays (e.g. infinite comments or transaction logs inside a single user document).",
            "Violating the ESR rule by placing range filters before sort filters."
        ],
        "best_practices": [
            "Always filter early with `$match` before `$unwind` or `$group`.",
            "Index compound keys in strict Equality -> Sort -> Range order."
        ]
    },
    {
        "title": "Celery Worker Concurrency, Chords & RabbitMQ DLX",
        "slug": "celery-worker-concurrency-rabbitmq-dlx",
        "category": QuestionCategory.CELERY_RABBITMQ,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["Instagram", "Pinterest", "Robinhood", "Instacart"],
        "frequency_score": 94,
        "mindmap_topic": "celery-rabbitmq",
        "mindmap_node": "celery-chord",
        "scenario_text": """
Your background Celery worker processes high-volume image transformations and webhook dispatches.
Under load, workers suffer memory leaks and eventually die with Out-Of-Memory (OOM).
Additionally, third-party webhook failures crash workers repeatedly.
Demonstrate how to configure Celery task concurrency (`prefork` vs `gevent`), recycle leaky workers (`max_tasks_per_child`), 
and implement exponential backoff retries with RabbitMQ Dead Letter Exchanges (DLX).
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of a package delivery driver. If a customer's gate is locked, the driver shouldn't honk the horn 100 times in 1 second (which causes a traffic jam and crashes the system). 
Instead, the driver waits 2 minutes, then 4 minutes, then 8 minutes (**Exponential Backoff with Jitter**). If delivery still fails after 5 tries, they place the package in the return warehouse (**Dead Letter Queue**) for manual audit.

### ⚙️ Under The Hood (Why It Happens)
Immediate retries flood failing third-party APIs. Without backoff and jitter, all retrying workers hit the target at identical intervals, causing thundering-herd downtime. Additionally, long-running Python workers leak memory over time.

### 🚀 Step-by-Step Production Fix
1. Configure Celery tasks with `autoretry_for=(ConnectionError,)`, `retry_backoff=True`, and `retry_jitter=True`.
2. Set `acks_late=True` so tasks are acknowledged only after finishing.
3. Set `worker_max_tasks_per_child = 500` to automatically restart worker processes and reclaim leaked RAM.

### 🎯 30-Second MNC Interview Punchline
*"Use exponential backoff with jitter and Dead Letter Exchanges to prevent retry storms, and set worker_max_tasks_per_child to eliminate memory leaks."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Celery Task simulation with Exponential Backoff
import time
import random

class MockTask:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def execute_with_retry(self, payload: dict, attempt: int = 1):
        try:
            print(f"[Attempt {attempt}] Processing webhook for order {payload['order_id']}...")
            # Simulate transient network failure on first 2 attempts
            if attempt < 3:
                raise ConnectionError("503 Service Unavailable from downstream webhook")
            print("Webhook delivered successfully!")
            return True
        except ConnectionError as exc:
            if attempt < self.max_retries:
                delay = 2 ** attempt + random.uniform(0.1, 0.5) # Exponential backoff + jitter
                print(f"Failed. Retrying in {delay:.2f}s...")
                return self.execute_with_retry(payload, attempt + 1)
            else:
                print("[DLX] Max retries exceeded. Routing to Dead Letter Queue for manual audit.")
                return False

task = MockTask()
task.execute_with_retry({"order_id": "ORD-777", "amount": 250})
""",
        "solution_code": """# Production Celery task decorator pattern:
# @celery_app.task(
#     bind=True,
#     autoretry_for=(ConnectionError,),
#     retry_backoff=True,
#     retry_backoff_max=600,
#     retry_jitter=True,
#     max_retries=5,
#     acks_late=True
# )
print("Celery exponential backoff with jitter and acks_late configured.")
""",
        "cross_questions": [
            "Why must `acks_late=True` be set when implementing idempotent tasks?",
            "What is the difference between RabbitMQ Direct, Topic, and Fanout exchanges?",
            "What is Prefetch Count (QoS) in RabbitMQ, and why does a default prefetch of 4 starve other Celery workers?"
        ],
        "common_traps": [
            "Passing large Django/SQLAlchemy ORM instances into task parameters (causes serialization bloat and stale data).",
            "Retrying immediately without exponential backoff and jitter (causes thundering herd DDoS on downstream APIs)."
        ],
        "best_practices": [
            "Pass only entity IDs (`user_id`, `order_id`) to Celery tasks.",
            "Set `worker_max_tasks_per_child` to guard against memory leaks."
        ]
    },

    # =========================================================================
    # SENIOR LEVEL (6 - 9 Years)
    # =========================================================================
    {
        "title": "Apache Kafka: Consumer Lag, Partition Skew & Rebalancing",
        "slug": "kafka-consumer-lag-rebalancing",
        "category": QuestionCategory.KAFKA_MESSAGING,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["LinkedIn", "Uber", "Netflix", "PayPal"],
        "frequency_score": 98,
        "mindmap_topic": "kafka-messaging",
        "mindmap_node": "kafka-rebalance",
        "scenario_text": """
A critical payment settlement topic in Kafka has 12 partitions and 12 consumers in a consumer group.
Suddenly, one consumer's processing time spikes, exceeding `max.poll.interval.ms`.
Kafka detects a dead consumer and triggers a group rebalance, halting message consumption across all 12 partitions.
Explain how Cooperative Sticky Rebalancing solves this, how to diagnose partition skew (hot keys), and how to commit offsets safely.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of 12 cashiers at an airport check-in desk.
In older Kafka (**Eager Rebalance**), if one cashier drops their pen, the manager blows a whistle and **all 12 cashiers stop serving passengers** for 30 seconds!
In modern Kafka (**Cooperative Sticky Rebalance**), the other 11 cashiers keep checking in passengers without stopping, while only the 1 affected line is adjusted.

### ⚙️ Under The Hood (Why It Happens)
Eager rebalancing halts message consumption across all partitions ('Stop-the-World'). Cooperative Sticky Rebalancing revokes only the specific partitions being moved, allowing unaffected consumers to continue streaming messages without delay.

### 🚀 Step-by-Step Production Fix
1. Set `partition.assignment.strategy` to `CooperativeStickyAssignor`.
2. Avoid partition skew (hot keys) by salting keys (e.g. `f"{merchant_id}:{order_id}"`) so traffic distributes evenly across all 12 partitions.
3. Tune `max.poll.interval.ms` so slow batch processing doesn't falsely trigger consumer eviction.

### 🎯 30-Second MNC Interview Punchline
*"Cooperative Sticky Rebalancing eliminates stop-the-world pauses in consumer groups, and balanced partition keys prevent hot-partition lag."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Simulating Kafka Partition Key Hashing:
import hashlib

def get_partition(key: str, total_partitions: int = 12) -> int:
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % total_partitions

# Test partition distribution:
merchants = ["Merchant-A", "Merchant-B", "Merchant-C", "Merchant-D", "Merchant-E"]
distribution = {i: 0 for i in range(12)}

for m in merchants:
    for _ in range(1000):
        p = get_partition(m)
        distribution[p] += 1

print("Partition message counts:")
for p, count in distribution.items():
    if count > 0:
        print(f"Partition {p}: {count} messages")
""",
        "solution_code": """# Solution: Add salt or compound key (merchant_id + order_uuid) to avoid partition hotspotting
import hashlib

def get_balanced_partition(merchant_id: str, order_id: str, total_partitions: int = 12) -> int:
    compound = f"{merchant_id}:{order_id}"
    return int(hashlib.md5(compound.encode()).hexdigest(), 16) % total_partitions

print("Balanced partition selection demonstrated.")
""",
        "cross_questions": [
            "How does Kafka achieve high write performance through sequential disk I/O and OS PageCache?",
            "What happens if `enable.auto.commit` is True and the consumer crashes midway through processing a batch?",
            "What is the difference between `acks=0`, `acks=1`, and `acks=all` (`-1`) in Kafka producers?"
        ],
        "common_traps": [
            "Performing slow external REST API calls directly inside the Kafka consumer poll loop.",
            "Setting more consumers than partitions in a group (excess consumers will sit permanently idle)."
        ],
        "best_practices": [
            "Use Cooperative Sticky Rebalancing (`cooperative-sticky`).",
            "Commit offsets manually after business transaction completes."
        ]
    },
    {
        "title": "Docker: Multi-Stage Build & Container Security Hardening",
        "slug": "docker-multistage-security-hardening",
        "category": QuestionCategory.DOCKER_CONTAINERS,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["Google", "Amazon", "Palantir", "Cloudflare"],
        "frequency_score": 95,
        "mindmap_topic": "docker-containers",
        "mindmap_node": "docker-multistage",
        "scenario_text": """
A company's Python backend Docker image is 1.4 GB in size and contains 45 HIGH and CRITICAL vulnerabilities according to Trivy.
The container runs as root, has GCC compilers in production, and builds take 10 minutes because Docker layer caching is broken.
Write an optimized, secure multi-stage Dockerfile that:
1. Slashes image size below 100 MB.
2. Runs as a non-privileged user (`USER appuser`).
3. Maximizes Docker layer caching for fast CI/CD builds.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of building a house. You need heavy bulldozers, cement mixers, and scaffolding during construction (**the builder stage**). But when moving into the finished house, you don't leave bulldozers and scaffolding in your living room! 
Multi-stage Docker builds use heavy compilers to build the application, then copy only the clean compiled files into a tiny, secure final container.

### ⚙️ Under The Hood (Why It Happens)
Single-stage Docker images include build tools (`gcc`, `make`, `git`, package caches), inflating image size to 1.5GB+ and introducing dozens of OS vulnerabilities. Multi-stage builds leave the build tools behind and run as an unprivileged user (`USER appuser`).

### 🚀 Step-by-Step Production Fix
1. **Stage 1 (Builder)**: Install dependencies into `/root/.local` using `python:3.12-slim AS builder`.
2. **Stage 2 (Runtime)**: Copy only `.local` from builder into a fresh slim container.
3. **Security**: Create a non-root user (`useradd -u 1001 appuser`) and set `USER appuser`.

### 🎯 30-Second MNC Interview Punchline
*"Multi-stage builds slash container attack surfaces and image size by discarding build tools, and running as non-root prevents container breakout exploits."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Inspecting Docker layer caching logic:
dockerfile_bad = '''
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
'''

dockerfile_good = '''
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd -m -u 1001 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

print("Comparing Dockerfile patterns...")
print("Good Dockerfile separates builder stage, caches requirements, and drops root privileges.")
""",
        "solution_code": """print("Multi-stage Dockerfile with non-root security verified.")""",
        "cross_questions": [
            "Why is PID 1 special inside a Docker container, and what happens when SIGTERM is sent?",
            "What is a Distroless container, and how do you debug a container that lacks a shell (/bin/sh)?",
            "How does `.dockerignore` prevent leaking `.env` files and `__pycache__` into the image layer history?"
        ],
        "common_traps": [
            "Using `COPY . .` before `RUN pip install`, invalidating layer caches on every commit.",
            "Leaving credentials, SSH keys, or `.git` directories inside intermediate Docker layers."
        ],
        "best_practices": [
            "Use Multi-stage builds with Python `-slim` or Distroless images.",
            "Run as non-root user (`USER 1001`)."
        ]
    },
    {
        "title": "Kubernetes: Zero-Downtime Rolling Updates & Probe Architecture",
        "slug": "kubernetes-zero-downtime-probes",
        "category": QuestionCategory.KUBERNETES_DEVOPS,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["Uber", "Google", "Microsoft", "Stripe"],
        "frequency_score": 96,
        "mindmap_topic": "kubernetes-devops",
        "mindmap_node": "k8s-graceful-shutdown",
        "scenario_text": """
During automated CI/CD deployments to a Kubernetes cluster, users experience intermittent 502 Bad Gateway errors for 15 seconds.
Investigation reveals that when old Pods are terminated, Kubelet sends `SIGTERM` immediately while the Ingress controller is still routing live traffic to the terminating Pod.
Configure a Kubernetes deployment with `preStop` hooks, proper `terminationGracePeriodSeconds`, and separate Liveness/Readiness/Startup probes to achieve true zero-downtime rolling updates.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
When a restaurant waiter's shift ends, they don't abruptly throw the plates on the floor! 
A `preStop` hook gives the Kubernetes Ingress router 15 seconds to stop sending new diners to the waiter, while the waiter finishes serving the food currently in their hands.

### ⚙️ Under The Hood (Why It Happens)
When a Pod is terminated, removing its IP from Ingress/kube-proxy takes 2-5 seconds. Kubelet sends `SIGTERM` concurrently. If the app stops immediately, in-flight HTTP requests receive connection refused (`502 Bad Gateway`). A `preStop: sleep 15` delays SIGTERM until Ingress traffic has stopped.

### 🚀 Step-by-Step Production Fix
1. Add `lifecycle: preStop: exec: command: ['/bin/sh', '-c', 'sleep 15']` in the Pod spec.
2. Set `terminationGracePeriodSeconds: 45`.
3. In Python, handle `SIGTERM` to drain active DB connections before exiting.
4. Keep Liveness probes strictly local (don't ping external databases in liveness probes).

### 🎯 30-Second MNC Interview Punchline
*"Pair a preStop sleep hook with graceful SIGTERM connection draining to eliminate Ingress 502 race conditions during rolling deployments."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Simulating Graceful Shutdown in Python FastAPI / Uvicorn:
import signal
import time

is_shutting_down = False

def handle_sigterm(signum, frame):
    global is_shutting_down
    print("[SIGTERM] Received termination signal from Kubernetes!")
    print("[DRAIN] Draining in-flight database transactions...")
    is_shutting_down = True
    time.sleep(1) # Simulates flushing active requests
    print("[EXIT] Clean shutdown completed. Zero dropped connections.")

# Register signal handler
signal.signal(signal.SIGTERM, handle_sigterm)
print("Server running. Ready to handle graceful termination.")
""",
        "solution_code": """print("Graceful SIGTERM handler and Kubernetes preStop lifecycle pattern verified.")""",
        "cross_questions": [
            "What is the danger of having Liveness Probe check downstream database connectivity?",
            "What is the difference between CPU throttling (CFS quota) and Memory OOMKilled (Exit code 137)?",
            "How do `maxUnavailable` and `maxSurge` parameters control the speed and safety of rolling updates?"
        ],
        "common_traps": [
            "Having Liveness probe ping external services; if external service flaps, K8s kills all pods in an unrecoverable restart loop.",
            "Setting `terminationGracePeriodSeconds` lower than your slowest batch transaction time."
        ],
        "best_practices": [
            "Use a `preStop` sleep hook (10-15s) in production deployments.",
            "Keep Liveness probes strictly local (checking process health, not third-party dependencies)."
        ]
    },

    # =========================================================================
    # LEAD / ARCHITECT LEVEL (10+ Years)
    # =========================================================================
    {
        "title": "Dual-Write Problem: MySQL & Kafka Consistency (Transactional Outbox)",
        "slug": "dual-write-kafka-transactional-outbox",
        "category": QuestionCategory.SYSTEM_DESIGN_MNC,
        "difficulty": QuestionDifficulty.ARCHITECT,
        "min_exp_years": 10,
        "max_exp_years": 20,
        "company_tags": ["Netflix", "Uber", "Amazon", "Confluent"],
        "frequency_score": 98,
        "mindmap_topic": "system-design-troubleshooting",
        "mindmap_node": "system-flash-sale",
        "scenario_text": """
In an event-driven architecture, when a customer places an order, your service must:
1. Insert the order into MySQL database.
2. Publish an `OrderCreated` event to Apache Kafka for downstream billing and shipping.
If you commit to MySQL and Kafka publish fails, events are lost.
If you publish to Kafka first and MySQL commit fails/rolls back, ghost events are published.
Architect guaranteed at-least-once delivery using the Transactional Outbox Pattern and Debezium / CDC without distributed 2PC locks.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
If you try to write in two different notebooks in two different buildings at the exact same second, one building might catch fire and your records won't match. 
Instead, write both records into your single local notebook (**MySQL ACID transaction**), and have an assistant reliably copy the records to the second building (**Kafka CDC**).

### ⚙️ Under The Hood (Why It Happens)
Writing to MySQL and then publishing to Kafka cannot be atomic without slow 2PC locks. If Kafka is down, the order is saved but the event is lost. If Kafka succeeds and MySQL rolls back, ghost events are published. The **Transactional Outbox Pattern** saves the business entity and the event in the same local ACID transaction.

### 🚀 Step-by-Step Production Fix
1. Create an `outbox_events` table in MySQL.
2. In a single local transaction: insert the order and insert the event into `outbox_events`.
3. An asynchronous CDC tool (Debezium reading the MySQL binlog) streams events from the outbox table to Kafka with guaranteed at-least-once delivery.

### 🎯 30-Second MNC Interview Punchline
*"Solve dual-write inconsistencies with the Transactional Outbox Pattern: commit the entity and event in a single local ACID transaction, then use log-based CDC to stream to Kafka."*
        """,
        "has_python_sandbox": True,
        "starter_code": """class MockDBTransaction:
    def __init__(self):
        self.orders = []
        self.outbox_events = []
    
    def create_order_with_outbox(self, order_id: str, amount: float):
        # ATOMIC LOCAL TRANSACTION:
        self.orders.append({"id": order_id, "amount": amount})
        self.outbox_events.append({
            "event_id": f"EVT-{order_id}",
            "topic": "orders.v1.created",
            "payload": {"order_id": order_id, "amount": amount},
            "status": "PENDING"
        })
        print(f"Committed order {order_id} and outbox event atomically.")

db = MockDBTransaction()
db.create_order_with_outbox("ORD-8888", 299.99)
print("Orders:", db.orders)
print("Outbox:", db.outbox_events)
""",
        "solution_code": """class OutboxPublisher:
    def __init__(self, db):
        self.db = db
        self.kafka_cluster = []

    def poll_and_publish(self):
        for event in list(self.db.outbox_events):
            if event["status"] == "PENDING":
                self.kafka_cluster.append(event)
                event["status"] = "PUBLISHED"
                print(f"[CDC Worker] Published event {event['event_id']} to Kafka.")

db = MockDBTransaction()
db.create_order_with_outbox("ORD-9999", 450.00)
publisher = OutboxPublisher(db)
publisher.poll_and_publish()
print("Kafka Events:", publisher.kafka_cluster)
""",
        "has_sql_sandbox": True,
        "sql_schema": "fintech",
        "starter_sql": """-- Schema definition for Transactional Outbox in MySQL:
CREATE TABLE IF NOT EXISTS outbox_events (
    id VARCHAR(64) PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL
);
""",
        "solution_sql": """SELECT 
    id, 
    aggregate_type, 
    aggregate_id, 
    event_type, 
    created_at 
FROM outbox_events 
ORDER BY created_at ASC;
""",
        "cross_questions": [
            "How does Debezium tail the MySQL binary log (binlog) without imposing locking overhead on the InnoDB buffer pool?",
            "How do downstream consumers handle duplicate events when Kafka guarantees at-least-once delivery?",
            "What are the operational trade-offs of polling the outbox table (`SELECT ... FOR UPDATE SKIP LOCKED`) vs log-based CDC?"
        ],
        "common_traps": [
            "Assuming distributed transactions (XA / 2PC) are feasible across microservices.",
            "Forgetting to clean up or partition old outbox table records, resulting in an unmanageably huge table."
        ],
        "best_practices": [
            "Use Log-based CDC (Debezium + Kafka Connect) reading MySQL binlog.",
            "Make all Kafka consumers idempotent using transaction logs or deduplication filters."
        ]
    },
    {
        "title": "CI/CD & Zero-Downtime Blue-Green Schema Migrations",
        "slug": "cicd-zerodowntime-schema-migrations",
        "category": QuestionCategory.CICD_PIPELINES,
        "difficulty": QuestionDifficulty.ARCHITECT,
        "min_exp_years": 10,
        "max_exp_years": 20,
        "company_tags": ["Stripe", "Amazon", "GitHub", "Shopify"],
        "frequency_score": 99,
        "mindmap_topic": "cicd-production",
        "mindmap_node": "cicd-canary",
        "scenario_text": """
A microservice database table has 200 million rows.
A new feature requires renaming column `phone_number` to `contact_number` and changing its type.
Running `ALTER TABLE` directly will lock the table for 45 minutes, causing a catastrophic global outage.
Architect the 4-phase Expand-and-Contract (Parallel Run) migration pattern in your CI/CD pipeline to ensure zero downtime.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of replacing an old bridge. You don't blow up the old bridge while cars are driving on it!
1. Build the new lane right alongside the old one (**Expand**).
2. Allow cars to use both lanes (**Dual-Write**).
3. Move all traffic onto the new lane.
4. Safely demolish the old lane (**Contract**).

### ⚙️ Under The Hood (Why It Happens)
Running `ALTER TABLE` to rename columns locks tables for hours on 200M row databases. The **Expand-and-Contract** pattern decouples schema evolution from application deployments across non-breaking phases.

### 🚀 Step-by-Step Production Fix
1. **Phase 1 (Expand)**: Add `new_column` as nullable via non-blocking migration.
2. **Phase 2 (Dual Write)**: App writes to both `old_column` and `new_column`.
3. **Phase 3 (Backfill)**: Run an async script in small indexed batches to copy historic rows.
4. **Phase 4 (Contract)**: Switch reads to `new_column` and drop `old_column` in a future deploy.

### 🎯 30-Second MNC Interview Punchline
*"Never rename columns in a single deploy; use the 4-phase Expand-and-Contract pattern to ensure non-breaking zero-downtime database evolution."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Simulating Dual-Write Expand and Contract Migration:
class UserRecordService:
    def __init__(self):
        self.db = [{"id": 1, "phone_number": "123-456-7890", "contact_number": None}]

    def update_phone_phase2_dual_write(self, user_id: int, new_number: str):
        for user in self.db:
            if user["id"] == user_id:
                # DUAL WRITE: Write to both legacy and new column
                user["phone_number"] = new_number
                user["contact_number"] = new_number
                print(f"[DUAL WRITE] Updated user {user_id} in both columns safely.")

service = UserRecordService()
service.update_phone_phase2_dual_write(1, "987-654-3210")
print(service.db)
""",
        "solution_code": """print("Expand and Contract dual-write migration pattern verified.")""",
        "has_sql_sandbox": False,
        "cross_questions": [
            "Why is `ALTER TABLE` dangerous on large MySQL InnoDB tables, and how do tools like `gh-ost` and `pt-online-schema-change` work using binlog triggers?",
            "How do you handle rollbacks if Phase 3 backfill detects inconsistent data formats?",
            "How does Argo Rollouts automate Canary analysis using Prometheus metric queries before promoting a version to 100%?"
        ],
        "common_traps": [
            "Renaming or dropping columns in a single deploy step while old instances of the backend are still running.",
            "Running bulk UPDATE scripts without batching, locking the entire table and filling up the undo log."
        ],
        "best_practices": [
            "Always use the Expand-and-Contract pattern for database schema evolution.",
            "Run table backfills in small indexed batches during off-peak hours."
        ]
    },

    # =========================================================================
    # ADDITIONAL PYTHON & BACKEND ROADMAP QUESTIONS
    # =========================================================================
    {
        "title": "Python Object Lifecycle: __new__ vs __init__ & Thread-Safe Singleton",
        "slug": "python-new-vs-init-singleton",
        "category": QuestionCategory.PYTHON_INTERNALS,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["Google", "Microsoft", "Bloomberg", "Amazon"],
        "frequency_score": 96,
        "mindmap_topic": "python-internals",
        "mindmap_node": "py-gil",
        "scenario_text": """
You are implementing a centralized Database Connection Pool manager in Python that must be a strict Singleton across all threads.
A junior developer tried implementing `__init__`, but noticed `__init__` is invoked on every single instantiation call, re-initializing the connections!
Explain the difference between `__new__` (object allocator) and `__init__` (object initializer), and implement a thread-safe Singleton using `threading.Lock`.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
`__new__` is the construction company that buys the land and builds the house.
`__init__` is the interior decorator who paints the walls.
To ensure there is only **ONE house in the entire world (Singleton)**, you must stop the construction company in `__new__` before a second house is built!

### ⚙️ Under The Hood (Why It Happens)
`__new__(cls)` is the static method that allocates the object in memory. `__init__(self)` initializes attributes on that existing instance. If you attempt to implement a singleton inside `__init__`, Python has already allocated a new memory address. Overriding `__new__` with double-checked locking guarantees only one instance is ever created.

### 🚀 Step-by-Step Production Fix
1. In `__new__`, check `if cls._instance is None:`.
2. Acquire `threading.Lock()` to prevent race conditions.
3. Double-check: `if cls._instance is None: cls._instance = super().__new__(cls)`.
4. Return `cls._instance`.

### 🎯 30-Second MNC Interview Punchline
*"__new__ allocates the instance in memory while __init__ initializes it. Intercept __new__ with double-checked locking to enforce a thread-safe singleton."*
        """,
        "has_python_sandbox": True,
        "starter_code": """import threading

class DatabaseConnectionPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Double-checked locking pattern:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("[ALLOCATING] Creating singleton instance in memory...")
                    cls._instance = super().__new__(cls)
                    cls._instance.connections = 10
        return cls._instance

# Test Singleton:
pool1 = DatabaseConnectionPool()
pool2 = DatabaseConnectionPool()

print("pool1 is pool2?", pool1 is pool2)
print("pool1 ID:", id(pool1))
print("pool2 ID:", id(pool2))
""",
        "solution_code": """import threading

class DatabaseConnectionPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.pool_size = 20
        return cls._instance

p1 = DatabaseConnectionPool()
p2 = DatabaseConnectionPool()
assert p1 is p2
print("Thread-safe Singleton verified.")
""",
        "has_sql_sandbox": False,
        "cross_questions": [
            "Why is double-checked locking needed in multi-threaded environments?",
            "How can a Singleton be implemented using a Python metaclass (`__call__`) instead of `__new__`?",
            "What happens if a Singleton is unpickled with `pickle.loads()`?"
        ],
        "common_traps": [
            "Initializing connection state inside `__init__` in a singleton class, causing re-initialization on every `Pool()` call.",
            "Forgetting thread synchronization with `threading.Lock`."
        ],
        "best_practices": [
            "Use module-level singletons (Python modules are cached in `sys.modules` by default) where possible.",
            "Use metaclasses or double-checked locking in `__new__` when dynamic classes are required."
        ]
    },
    {
        "title": "Python Generators & Processing 10GB Data with O(1) Memory",
        "slug": "python-generators-memory-efficiency",
        "category": QuestionCategory.PYTHON_INTERNALS,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 2,
        "max_exp_years": 5,
        "company_tags": ["Amazon", "Meta", "Uber", "Spotify"],
        "frequency_score": 94,
        "mindmap_topic": "python-internals",
        "mindmap_node": "py-gil",
        "scenario_text": """
A production batch job reads a 10 GB server access log file into a Python list: `lines = file.readlines()`.
The container immediately crashes with `MemoryError` (OOMKilled) because the 10 GB string data exhausts RAM.
Refactor the code into a memory-efficient Generator Pipeline using `yield` that streams lines, parses status codes, and filters errors in $O(1)$ constant memory.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Loading a 10 GB file with `file.readlines()` is like trying to drink an entire swimming pool in one gulp (chokes RAM).
A generator is a **drinking water fountain**: it gives you one sip (`yield line`) at a time, keeping your memory usage at almost zero bytes!

### ⚙️ Under The Hood (Why It Happens)
Lists load all elements into RAM upfront ($O(N)$ memory). Generators use **lazy evaluation**: they compute values on demand and pause execution between iterations using `yield`, consuming only $O(1)$ constant memory regardless of data size.

### 🚀 Step-by-Step Production Fix
1. Replace list comprehensions `[...]` with generator expressions `(...)`.
2. Use `yield` inside loops instead of appending to in-memory lists.
3. Chain generator functions: `read_lines -> filter_5xx -> parse_json`.

### 🎯 30-Second MNC Interview Punchline
*"Generators provide lazy on-demand evaluation, reducing memory footprint from O(N) to O(1) for massive data pipelines."*
        """,
        "has_python_sandbox": True,
        "starter_code": """import sys

# MOCK STREAM OF 100,000 LOG ENTRIES:
def generate_mock_logs(count=50000):
    for i in range(count):
        status = 500 if i % 100 == 0 else 200
        yield f"2026-03-01 12:00:00 GET /api/v1/orders HTTP/1.1 {status} - response_time=12ms"

# Generator pipeline:
def filter_5xx_errors(log_stream):
    for line in log_stream:
        if " 500 " in line:
            yield line

# Memory-efficient consumer:
stream = generate_mock_logs(5000)
error_stream = filter_5xx_errors(stream)

first_5_errors = [next(error_stream) for _ in range(5)]
print("Parsed Errors without loading file into memory:")
for err in first_5_errors:
    print(">", err)
print("Memory footprint: Constant O(1) bytes!")
""",
        "solution_code": """def stream_errors(generator):
    for line in generator:
        if " 500 " in line:
            yield line
print("Generator streaming verified.")
""",
        "has_sql_sandbox": False,
        "cross_questions": [
            "What is the difference between `yield` and `yield from` in Python 3.3+?",
            "How does a generator differ from an iterator in terms of state storage?",
            "How can you send data back into a running generator using `.send()`?"
        ],
        "common_traps": [
            "Converting a generator into a list (`list(gen)`) which immediately loads all data into memory.",
            "Iterating over a generator a second time (generators are one-time exhaustible streams)."
        ],
        "best_practices": [
            "Compose generator pipelines (`gen1 -> gen2 -> gen3`) for streaming large data sets.",
            "Use `itertools.islice` to safely paginate generator outputs."
        ]
    },
    {
        "title": "SQLAlchemy ORM: Diagnosing and Eliminating the N+1 Query Problem",
        "slug": "sqlalchemy-n-plus-1-query-optimization",
        "category": QuestionCategory.POSTGRES_MYSQL,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["DoorDash", "Instacart", "Airbnb", "Shopify"],
        "frequency_score": 97,
        "mindmap_topic": "postgres-mysql-internals",
        "mindmap_node": "pg-vacuum",
        "scenario_text": """
A customer dashboard displays 50 orders along with the list of items inside each order.
Under load, database monitoring shows 51 separate SQL queries executed for a single HTTP request!
Query 1: `SELECT * FROM orders LIMIT 50;`
Queries 2-51: `SELECT * FROM order_items WHERE order_id = ?;` (executed 50 times in a loop!).
Explain the N+1 query problem, simulate the issue, and solve it using eager loading (`joinedload` vs `selectinload`).
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Imagine going to the grocery store **51 separate times to buy 51 individual eggs** instead of buying one carton with all 50 eggs inside! 
The N+1 query problem happens when your code fetches 50 orders, and then runs 50 separate SQL queries in a loop to get the items for each order.

### ⚙️ Under The Hood (Why It Happens)
Lazy loading issues 1 query for parents, plus $N$ additional queries for child relationships as you iterate over them. `selectinload` executes exactly 2 queries: Query 1 loads all parent orders; Query 2 loads all child items using an `IN (1, 2, 3...)` clause.

### 🚀 Step-by-Step Production Fix
1. For 1-to-many relationships in SQLAlchemy: use `.options(selectinload(Order.items))`.
2. For 1-to-1 relationships: use `.options(joinedload(Order.customer))`.
3. Add unit test assertions on query count to prevent N+1 regressions.

### 🎯 30-Second MNC Interview Punchline
*"Eliminate N+1 queries using selectinload for 1-to-many collections to fetch child records in a single batch IN-clause query."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Simulating N+1 vs Eager Loading in Python:
orders_db = [{"id": i, "total": 100 + i} for i in range(1, 6)]
items_db = [{"order_id": o["id"], "item": f"Product-{o['id']}-{j}"} for o in orders_db for j in range(2)]

# NAIVE N+1 APPROACH (Simulating 1 + N SQL queries):
queries_executed = 0

queries_executed += 1 # 1 query for orders
loaded_orders = orders_db

for order in loaded_orders:
    queries_executed += 1 # N queries inside loop!
    order["items"] = [it for it in items_db if it["order_id"] == order["id"]]

print(f"Total SQL queries issued: {queries_executed} (Massive N+1 bottleneck!)")

# EAGER SELECTINLOAD OPTIMIZATION (Exactly 2 queries):
optimized_queries = 0
optimized_queries += 1 # Query 1: SELECT * FROM orders
order_ids = [o["id"] for o in orders_db]

optimized_queries += 1 # Query 2: SELECT * FROM items WHERE order_id IN (1, 2, 3, 4, 5)
batch_items = [it for it in items_db if it["order_id"] in order_ids]

print(f"Optimized Eager Load queries: {optimized_queries} (Regardless of whether N=5 or N=5000!)")
""",
        "solution_code": """print("Eager loading with selectinload verified.")""",
        "has_sql_sandbox": True,
        "sql_schema": "ecommerce",
        "starter_sql": """-- Query parent orders and join child items in single query
SELECT 
    o.id as order_id, 
    o.total_amount, 
    i.product_id, 
    i.quantity, 
    i.unit_price
FROM orders o
JOIN order_items i ON o.id = i.order_id
WHERE o.customer_id = 1;
""",
        "solution_sql": """SELECT 
    o.id as order_id, 
    o.total_amount, 
    i.product_id, 
    i.quantity, 
    i.unit_price
FROM orders o
JOIN order_items i ON o.id = i.order_id
WHERE o.customer_id = 1;
""",
        "cross_questions": [
            "Why can `joinedload` cause Cartesian product issues when loading multiple 1-to-many relationships simultaneously?",
            "What is the difference between `lazy='dynamic'`, `lazy='selectin'`, and `lazy='subquery'` in SQLAlchemy 2.0?",
            "How do you configure SQLAlchemy query logging in production without impacting P99 latency?"
        ],
        "common_traps": [
            "Accessing child relationships inside a Jinja template or Pydantic serializer without eager loading.",
            "Using `joinedload` with `.limit()`, which causes SQLAlchemy to load all rows into memory to paginate client-side."
        ],
        "best_practices": [
            "Use `selectinload` as the default for 1-to-many collections in SQLAlchemy.",
            "Write integration tests with query counter assertions to prevent N+1 regressions."
        ]
    },
    {
        "title": "MySQL Deadlock Analysis: Next-Key Locks & Gap Locking",
        "slug": "mysql-deadlock-next-key-gap-locks",
        "category": QuestionCategory.POSTGRES_MYSQL,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["Amazon", "Uber", "Flipkart", "Stripe"],
        "frequency_score": 98,
        "mindmap_topic": "postgres-mysql-internals",
        "mindmap_node": "pg-vacuum",
        "scenario_text": """
A financial ledger service runs in MySQL Repeatable Read isolation level.
Transaction 1 executes: `SELECT * FROM accounts WHERE id = 15 FOR UPDATE;`
Transaction 2 executes: `SELECT * FROM accounts WHERE id = 25 FOR UPDATE;`
Next, Transaction 1 tries to insert an account with ID 20, and Transaction 2 tries to insert an account with ID 18.
Both transactions block each other, and MySQL aborts one with:
`ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction`.
Analyze why Gap Locks caused this deadlock and how to prevent it.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
In MySQL's default Repeatable Read mode, when you lock a house on a street, MySQL also locks the **empty lawns on both sides of the house (Gap Locks)**. 
If two neighbors both lock the same empty lawn and both try to build a shed in it, both block each other forever -> DEADLOCK!

### ⚙️ Under The Hood (Why It Happens)
InnoDB acquires Next-Key Locks (Record Lock + Gap Lock) to prevent Phantom Reads. If two transactions both hold shared gap locks on the interval `(15, 25)` and both attempt to insert, neither can proceed because both wait for the other's gap lock to release.

### 🚀 Step-by-Step Production Fix
1. Switch transaction isolation to **Read Committed** (disables gap locks for standard statements).
2. Ensure all transactions acquire locks in strict identical ordering across the codebase.
3. Catch MySQL Error 1213 and retry with exponential backoff.

### 🎯 30-Second MNC Interview Punchline
*"Prevent InnoDB deadlocks by switching to Read Committed to eliminate gap locks, and enforce consistent table/row lock ordering across the application."*
        """,
        "has_python_sandbox": True,
        "starter_code": """# Simulating Deadlock Detection & Exponential Backoff Retry in Python:
import time
import random

class DeadlockException(Exception): pass

def execute_with_deadlock_retry(operation, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            # Simulate operation that might hit deadlock
            if attempt < 2:
                raise DeadlockException("Deadlock found when trying to get lock (MySQL Error 1213)")
            return operation()
        except DeadlockException as e:
            if attempt == max_retries:
                raise e
            backoff = (2 ** attempt) * 0.05 + random.uniform(0.01, 0.05)
            print(f"[RETRY {attempt}] Deadlock detected. Retrying after {backoff*1000:.1f}ms jitter...")
            time.sleep(backoff)

def transfer_money():
    print("Money transfer transaction succeeded!")
    return True

execute_with_deadlock_retry(transfer_money)
""",
        "solution_code": """print("Deadlock retry pattern with exponential jitter verified.")""",
        "has_sql_sandbox": True,
        "sql_schema": "fintech",
        "starter_sql": """-- Inspect active transactions and locks in MySQL:
SELECT * FROM accounts WHERE id IN (1, 2);
""",
        "solution_sql": """SELECT * FROM accounts WHERE id IN (1, 2);""",
        "cross_questions": [
            "Why does switching from Repeatable Read to Read Committed eliminate most gap lock deadlocks?",
            "What is the output of `SHOW ENGINE INNODB STATUS` and how do you find the 'LATEST DETECTED DEADLOCK' section?",
            "What is the difference between an Intention Exclusive (IX) lock and a Record Exclusive (X) lock?"
        ],
        "common_traps": [
            "Assuming transactions with row-level locks never deadlock.",
            "Holding database locks while making synchronous HTTP calls to third-party payment gateways."
        ],
        "best_practices": [
            "Keep transactions as short as possible.",
            "Acquire row locks in consistent global order (e.g. `ORDER BY id ASC`)."
        ]
    },
    {
        "title": "Redis Distributed Lock with Auto-Renewal (Watchdog Pattern)",
        "slug": "redis-distributed-lock-watchdog-lua",
        "category": QuestionCategory.REDIS_CACHING,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["Uber", "Stripe", "Amazon", "Grab"],
        "frequency_score": 99,
        "mindmap_topic": "redis-caching",
        "mindmap_node": "redis-rate-limiter",
        "scenario_text": """
A microservice acquires a Redis lock with a 5-second TTL: `SET lock:order:101 <random_uuid> NX EX 5`.
Under a sudden garbage collection pause or network blip, the business processing takes 7 seconds.
The Redis lock expires at second 5. A second worker acquires the lock and processes the order concurrently!
At second 7, the first worker finishes and blindly deletes the lock (`DEL lock:order:101`), which deletes the second worker's active lock!
Solve both problems:
1. Implement atomic lock release using a Lua script to ensure a worker only deletes its OWN lock.
2. Implement a background Watchdog thread to automatically renew lock TTL while the worker is actively running.
""",
        "theory_explanation": """
### 💡 In Simple Words (The Intuition)
Think of renting a conference room with a keycard that expires in 10 minutes. 
If your meeting runs longer, your assistant automatically extends the timer (**Watchdog renewal**) so no one kicks you out mid-meeting. 
When your meeting ends, you return your specific keycard (**Lua script verifies ownership** before unlocking).

### ⚙️ Under The Hood (Why It Happens)
Simple locks fail in production if a task runs longer than the TTL: the lock expires, another worker acquires it, and the first worker accidentally unlocks the second worker's lock! 
A production distributed lock requires atomic acquisition with NX/EX, an auto-renewing watchdog thread, and an atomic Lua release script.

### 🚀 Step-by-Step Production Fix
1. Acquire lock atomically: `SET lock_key unique_token NX EX 10`.
2. Start a background heartbeat thread every 3 seconds to extend TTL with `EXPIRE lock_key 10`.
3. Release lock atomically using Lua script to verify token ownership before calling `DEL`.

### 🎯 30-Second MNC Interview Punchline
*"A production Redis distributed lock requires atomic acquisition with NX/EX, a background watchdog for TTL renewal, and an atomic Lua script to prevent releasing another worker's lock."*
        """,
        "has_python_sandbox": True,
        "has_redis_sandbox": True,
        "starter_redis": """-- Step 1: Acquire lock with NX and EX 30s
SET lock:resource:999 "worker-uuid-abc" EX 30

-- Step 2: Check remaining TTL
TTL lock:resource:999

-- Step 3: Inspect active lock value
GET lock:resource:999
""",
        "solution_redis": """SET lock:resource:999 "worker-uuid-abc" EX 30
TTL lock:resource:999
""",
        "starter_code": """# Python simulation of Safe Distributed Lock with Lua release:
import uuid

mock_redis = {}

def acquire_lock(lock_key: str, token: str):
    if lock_key not in mock_redis:
        mock_redis[lock_key] = token
        return True
    return False

# Safe release: Only deletes if the token matches!
def release_lock_lua(lock_key: str, token: str):
    if mock_redis.get(lock_key) == token:
        del mock_redis[lock_key]
        return True # Lock safely released
    return False # Refused: Lock belongs to another worker!

token1 = str(uuid.uuid4())
token2 = str(uuid.uuid4())

print("Worker 1 acquires lock:", acquire_lock("order:101", token1))
print("Worker 2 tries to delete Worker 1's lock:", release_lock_lua("order:101", token2))
print("Worker 1 safely releases its own lock:", release_lock_lua("order:101", token1))
""",
        "solution_code": """print("Safe Redis distributed lock release verified.")""",
        "cross_questions": [
            "How does the Redisson Java framework implement its Netty-based Watchdog timer?",
            "What happens to a Redis lock if the master node crashes before replicating the key to the replica node?",
            "What is a Fencing Token, and why does Martin Kleppmann recommend monotonic fencing tokens for distributed storage safety?"
        ],
        "common_traps": [
            "Using `DEL lock_key` without checking if the lock value matches the worker's token.",
            "Setting lock TTL too short without an auto-renewal watchdog mechanism."
        ],
        "best_practices": [
            "Always release Redis locks with atomic Lua script token validation.",
            "Use Fencing Tokens at the database layer to reject outdated distributed lock holders."
        ]
    }
]

