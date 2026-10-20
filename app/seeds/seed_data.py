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
In Python, default parameter expressions are evaluated once when the `def` statement executes, not when the function is invoked.
If the default argument is a mutable object (such as a `list` or `dict`), every invocation of the function that does not supply an argument shares the exact same instance in memory (`id(target)` remains identical).
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
In SQL, ranking functions behave differently:
- `ROW_NUMBER()` assigns sequential integers regardless of ties.
- `RANK()` leaves gaps in ranking when ties occur (e.g., 1, 1, 3).
- `DENSE_RANK()` does not leave gaps (e.g., 1, 1, 2). For N-th highest distinct value, `DENSE_RANK()` is mathematically correct.
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
FastAPI runs `async def` routes directly on the main event loop thread. 
If an `async def` endpoint executes synchronous blocking I/O (like `time.sleep`, `requests.get()`, or legacy DB drivers), 
it monopolizes the thread. No other coroutine can yield or run until that blocking call returns.
In contrast, standard `def` routes in FastAPI are automatically offloaded to an `anyio` threadpool worker.
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
Cache Stampede (Thundering Herd) occurs when high-concurrency requests all experience a cache miss at the exact same moment.
Mitigation strategies:
1. **Mutex Lock**: Only the first request acquires a lock to query the DB and refresh cache; others wait or return stale data.
2. **Probabilistic Early Expiration (XFetch)**.
3. **Sliding-Window Rate Limiting with ZSET**: Evict timestamps older than window using `ZREMRANGEBYSCORE`, check `ZCARD`, add timestamp with `ZADD`.
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
MongoDB aggregation processes documents in an optimized pipeline.
The ESR rule dictates:
1. **E (Equality)**: Put exact match fields first (e.g. `status: "DELIVERED"`).
2. **S (Sort)**: Put sort fields second (e.g. `created_at: -1`).
3. **R (Range)**: Put range/inequality filters last (e.g. `total_amount: { $gt: 100 }`).
Following ESR ensures MongoDB avoids an in-memory blocking sort.
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
Celery uses distinct execution pools:
- `prefork`: Multiprocessing, ideal for CPU-bound or blocking C-extensions.
- `gevent` / `eventlet`: Greenlets, ideal for thousands of concurrent network I/O tasks.
For worker memory leaks (common with C libraries and pandas), set `worker_max_tasks_per_child = 500` to automatically recycle the process.
For retries, use Celery's `autoretry_for=(Exception,)` with `retry_backoff=True` and exponential jitter.
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
In older Eager Rebalancing, Kafka revokes ALL partition assignments across all consumers in the group during rebalance ('Stop the World').
In Cooperative Sticky Rebalancing (introduced in Kafka 2.4+):
1. Only the affected partition is reassigned.
2. Unaffected consumers continue streaming messages uninterrupted.
Partition Skew occurs when messages use a low-cardinality key (e.g. all orders for a merchant ID hash to partition #3), overloading one consumer while 11 consumers sit idle.
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
Production Container Best Practices:
1. **Multi-Stage Build**: Build dependencies in a heavy builder stage; copy only the compiled wheels to a minimal slim runtime.
2. **Order of Layers**: Copy `requirements.txt` and install before copying application code. Code changes will no longer trigger re-installation of dependencies.
3. **Non-Root User**: Never run as root. A compromised container process with root privileges can exploit Linux kernel vulnerabilities to break out to the host.
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
When a Pod enters termination:
1. Endpoints controller removes the Pod IP from the Service endpoints list, propagating to `kube-proxy` and Ingress (takes 2-5 seconds).
2. Kubelet sends `SIGTERM` to container processes concurrently.
If your app shuts down immediately upon receiving SIGTERM, incoming requests already in flight receive connection refused (HTTP 502).
Adding a `preStop: exec: command: ["/bin/sh", "-c", "sleep 15"]` ensures the pod stops taking new requests before the application starts closing DB connections and server listeners.
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
The Dual-Write problem cannot be safely solved with consecutive application-level writes because network partitions or crashes can occur between step 1 and step 2.
**The Transactional Outbox Pattern**:
1. Within the same local ACID transaction as the order creation, insert an event record into an `outbox_events` table in MySQL.
2. Since both writes share the same local DB transaction, atomicity is guaranteed.
3. An asynchronous CDC process (such as Debezium reading the MySQL binlog) streams events from `outbox_events` to Kafka with guaranteed at-least-once delivery.
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
The Expand and Contract Pattern (Parallel Run):
1. **Phase 1 (Expand)**: Add the new column `contact_number` as nullable without touching the old column.
2. **Phase 2 (Dual Write)**: Deploy code that reads from old column but writes to BOTH old and new columns.
3. **Phase 3 (Backfill)**: Run an asynchronous background script in small batches (`WHERE id BETWEEN x AND y`) to copy old data to new column.
4. **Phase 4 (Contract)**: Switch reading to the new column, verify, remove old column in a subsequent release.
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
    }
]
