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
        "category": QuestionCategory.SQL_DATABASE_INTERNALS,
        "difficulty": QuestionDifficulty.BASIC,
        "min_exp_years": 0,
        "max_exp_years": 3,
        "company_tags": ["Amazon", "Google", "Oracle", "Goldman Sachs"],
        "frequency_score": 95,
        "mindmap_topic": "mysql-database-internals",
        "mindmap_node": "mysql-btree",
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
        "mindmap_topic": "async-concurrency",
        "mindmap_node": "async-event-loop",
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

# BLOCKING SYNCHRONOUS FUNCTION (e.g. legacy payment SDK or heavy file write)
def legacy_sync_payment_verification(order_id: str) -> bool:
    print(f"Starting payment verification for {order_id}...")
    time.sleep(1) # Simulates blocking synchronous I/O
    print(f"Verification done for {order_id}")
    return True

# INSECURE ASYNC CALL: Calling sync blocking code in async loop stalls everything
async def handle_request_wrong(order_id: str):
    return legacy_sync_payment_verification(order_id)

# TODO: Refactor using asyncio.to_thread or run_in_executor
async def handle_request_correct(order_id: str):
    # Your optimized non-blocking implementation here
    pass

async def main():
    start = time.perf_counter()
    # Simulate 3 concurrent incoming requests
    # With non-blocking offload, 3 tasks should complete in ~1 second, not 3 seconds!
    print("Testing concurrent execution...")
    # Add your test run here

asyncio.run(main())
""",
        "solution_code": """import asyncio
import time

def legacy_sync_payment_verification(order_id: str) -> bool:
    time.sleep(1) # Simulates blocking call
    return True

async def handle_request_correct(order_id: str):
    # Offload blocking synchronous I/O to thread pool
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
            "What is the default thread pool size for `asyncio.to_thread` / `anyio` in FastAPI, and what happens when it is saturated?",
            "What is the overhead of thread context switching in high-throughput microservices?",
            "Why doesn't `asyncio.to_thread` bypass the GIL for pure CPU-bound mathematical operations?"
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
        "title": "MySQL Composite Index Optimization & Leftmost Prefix Rule",
        "slug": "mysql-composite-index-leftmost-prefix",
        "category": QuestionCategory.SQL_DATABASE_INTERNALS,
        "difficulty": QuestionDifficulty.INTERMEDIATE,
        "min_exp_years": 3,
        "max_exp_years": 6,
        "company_tags": ["Amazon", "Flipkart", "LinkedIn", "PayPal"],
        "frequency_score": 92,
        "mindmap_topic": "mysql-database-internals",
        "mindmap_node": "mysql-btree",
        "scenario_text": """
An e-commerce customer order history page is experiencing severe query latency.
The table has a composite index `(customer_id, order_date, status)`.
Run query plan analysis using `EXPLAIN QUERY PLAN` on different WHERE clause combinations, 
and determine which queries fully leverage the index B+ Tree vs which cause full table scans.
""",
        "theory_explanation": """
In B+ Tree composite indexes `(colA, colB, colC)`, the data is sorted primarily by `colA`, then by `colB` within the same `colA`, and finally by `colC`.
If a query skips `colA` and filters only by `colB` or `colC`, the database cannot jump to the index leaf nodes directly and must perform a full scan.
Furthermore, as soon as a range condition (`>`, `<`, `BETWEEN`) is used on `colB`, the index cannot use `colC` for filtering.
""",
        "has_python_sandbox": False,
        "has_sql_sandbox": True,
        "sql_schema": "ecommerce",
        "starter_sql": """-- Query 1: Fully utilizes leftmost prefix
SELECT id, total_amount, status 
FROM orders 
WHERE customer_id = 1 AND order_date >= '2026-01-01'
ORDER BY order_date DESC;

-- Examine the EXPLAIN QUERY PLAN output below!
""",
        "solution_sql": """-- Optimal query leveraging idx_orders_customer
SELECT 
    o.id, 
    c.name as customer_name,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.customer_id = 4 
  AND o.order_date >= '2026-01-01'
ORDER BY o.order_date DESC;
""",
        "cross_questions": [
            "What is a 'Covering Index' (Index-Only Scan), and how does it avoid the secondary index bookmark lookup?",
            "What happens if you apply a function like `DATE(order_date)` in the WHERE clause?",
            "How does MySQL InnoDB handle index condition pushdown (ICP)?"
        ],
        "common_traps": [
            "Placing low-cardinality columns (e.g. `status` with 3 values) at the front of composite indexes ahead of high-cardinality columns (`customer_id`).",
            "Assuming having 3 individual indexes is better than 1 well-designed composite index."
        ],
        "best_practices": [
            "Order composite index columns: `(Equality columns, Sort columns, Range columns)`.",
            "Always verify execution plan with `EXPLAIN`."
        ]
    },

    # =========================================================================
    # SENIOR LEVEL (6 - 9 Years)
    # =========================================================================
    {
        "title": "Flash Sale Concurrency: Race Conditions & Atomic Stock Decrement",
        "slug": "flash-sale-race-condition-inventory",
        "category": QuestionCategory.SYSTEM_DESIGN_MNC,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["Amazon", "Uber", "Flipkart", "Stripe"],
        "frequency_score": 97,
        "mindmap_topic": "system-design-troubleshooting",
        "mindmap_node": "system-flash-sale",
        "scenario_text": """
During a Black Friday flash sale, only 10 units of an iPhone are in stock.
500 concurrent buyer requests arrive within a 200ms window.
A naive implementation reads stock from DB (`SELECT stock`), checks in Python `if stock > 0:`, and executes `UPDATE stock = stock - 1`.
This causes massive overselling (stock ends up at negative numbers).
Demonstrate the race condition and implement the atomic SQL guard and concurrency lock.
""",
        "theory_explanation": """
The 'Read-Modify-Write' pattern without concurrency control creates classic race conditions.
Solutions include:
1. **Atomic SQL Decrement**: `UPDATE products SET stock = stock - 1 WHERE id = :id AND stock >= 1;` (affected rows = 1 indicates success; 0 indicates sold out).
2. **Pessimistic Locking**: `SELECT stock FROM products WHERE id = :id FOR UPDATE;` (locks row until transaction commits, but can cause contention/deadlocks).
3. **Optimistic Locking**: Using a `version` column: `UPDATE products SET stock = stock - 1, version = version + 1 WHERE id = :id AND version = :current_version;`
""",
        "has_python_sandbox": True,
        "starter_code": """import threading
import time

# SIMULATED DATABASE RECORD
product_stock = 10
successful_orders = 0
lock = threading.Lock()

# NAIVE IMPLEMENTATION WITH MASSIVE RACE CONDITION:
def naive_purchase(buyer_id: int):
    global product_stock, successful_orders
    # 1. Read current stock
    current = product_stock
    time.sleep(0.001) # Simulates network/DB latency
    
    # 2. Check stock in application layer
    if current > 0:
        # 3. Write decremented stock
        product_stock = current - 1
        successful_orders += 1

threads = [threading.Thread(target=naive_purchase, args=(i,)) for i in range(50)]
for t in threads: t.start()
for t in threads: t.join()

print(f"Final Stock: {product_stock} (Expected 0, but notice negative or wrong!)")
print(f"Successful Orders: {successful_orders} (Expected 10, but notice oversold!)")
""",
        "solution_code": """import threading
import time

product_stock = 10
successful_orders = 0
stock_lock = threading.Lock()

def atomic_purchase(buyer_id: int):
    global product_stock, successful_orders
    # Atomic reservation pattern (Simulating atomic DB: UPDATE ... WHERE stock >= 1)
    with stock_lock:
        if product_stock >= 1:
            product_stock -= 1
            successful_orders += 1
            return True
        return False

threads = [threading.Thread(target=atomic_purchase, args=(i,)) for i in range(50)]
for t in threads: t.start()
for t in threads: t.join()

print(f"Final Stock: {product_stock} (Guaranteed exact 0)")
print(f"Successful Orders: {successful_orders} (Guaranteed exact 10, zero overselling!)")
""",
        "has_sql_sandbox": True,
        "sql_schema": "ecommerce",
        "starter_sql": """-- ATOMIC SQL DECREMENT WITH ZERO OVERSELLING:
UPDATE products
SET stock_quantity = stock_quantity - 1
WHERE id = 1 AND stock_quantity >= 1;

-- Check remaining stock
SELECT id, sku, name, stock_quantity FROM products WHERE id = 1;
""",
        "solution_sql": """-- Single atomic statement: Row-level lock acquired and released instantly
UPDATE products
SET stock_quantity = stock_quantity - 1
WHERE id = 1 AND stock_quantity >= 1;

-- Query affected row count in your application (if rows_affected == 0 -> OUT_OF_STOCK)
SELECT id, name, stock_quantity FROM products WHERE id = 1;
""",
        "cross_questions": [
            "Why is an atomic SQL `UPDATE ... WHERE stock >= 1` superior to `SELECT ... FOR UPDATE` under high concurrency?",
            "How would you handle Redis distributed inventory caching with Lua scripts to prevent the database from even receiving the 500,000 requests?",
            "What is the difference between reservation expiry (holding an item in cart for 10 minutes) vs immediate payment capture?"
        ],
        "common_traps": [
            "Doing stock checks in Python memory without distributed locking or DB constraints.",
            "Using MySQL Serializable isolation level, which causes frequent deadlock errors and aborts under high concurrency."
        ],
        "best_practices": [
            "Use atomic conditional updates at the DB layer.",
            "Use Redis Lua scripts for fast pre-validation before hitting relational databases."
        ]
    },
    {
        "title": "Idempotent Payment API Design with State Machines",
        "slug": "idempotent-payment-api-design",
        "category": QuestionCategory.SYSTEM_DESIGN_MNC,
        "difficulty": QuestionDifficulty.ADVANCED,
        "min_exp_years": 6,
        "max_exp_years": 9,
        "company_tags": ["Stripe", "PayPal", "Square", "Uber"],
        "frequency_score": 99,
        "mindmap_topic": "system-design-troubleshooting",
        "mindmap_node": "system-flash-sale",
        "scenario_text": """
A mobile client sends a charge request to your payment API.
The payment gateway processes the $500 charge successfully, but a cellular network drop prevents the HTTP 200 response from reaching the app.
The mobile app automatically retries the request 3 times.
How do you design the backend API using `Idempotency-Key` headers, distributed locks, and state transitions so the customer is charged exactly once?
""",
        "theory_explanation": """
An idempotent HTTP operation produces the same server state regardless of whether it is executed 1 time or 10 times.
MNC Standard Implementation:
1. Client generates a unique UUID `Idempotency-Key` header.
2. Server acquires a distributed lock on `idempotency_key` (with TTL).
3. Server queries DB for an existing record with that key:
   - If found and status is `SUCCESS`, immediately return the cached response payload.
   - If found and status is `PROCESSING`, return HTTP 409 Conflict or poll.
   - If not found, insert record with status `PENDING`, execute payment, update to `SUCCESS`, save response payload, and release lock.
""",
        "has_python_sandbox": True,
        "starter_code": """# Simulate an Idempotent Payment Processor
import uuid
import time

db_transactions = {}

def process_payment(idempotency_key: str, amount: float, account_id: str) -> dict:
    # TODO: Implement idempotency check
    # If key already processed, return existing result without re-charging
    transaction_id = f"TXN-{uuid.uuid4().hex[:8]}"
    result = {"transaction_id": transaction_id, "amount": amount, "status": "SUCCESS"}
    db_transactions[idempotency_key] = result
    return result

# Test duplicate requests with the same idempotency key:
key = "req-idemp-999"
res1 = process_payment(key, 500.0, "ACC-01")
res2 = process_payment(key, 500.0, "ACC-01")

print("Call 1:", res1)
print("Call 2:", res2)
print("Are they identical transactions?", res1["transaction_id"] == res2["transaction_id"])
""",
        "solution_code": """import uuid

db_transactions = {}

def process_payment(idempotency_key: str, amount: float, account_id: str) -> dict:
    # Check if this idempotency key was already processed
    if idempotency_key in db_transactions:
        print(f"[IDEMPOTENT HIT] Returning cached response for key: {idempotency_key}")
        return db_transactions[idempotency_key]

    # Process new charge
    transaction_id = f"TXN-{uuid.uuid4().hex[:8]}"
    result = {
        "transaction_id": transaction_id, 
        "amount": amount, 
        "status": "SUCCESS", 
        "idempotency_key": idempotency_key
    }
    db_transactions[idempotency_key] = result
    return result

key = "req-idemp-999"
res1 = process_payment(key, 500.0, "ACC-01")
res2 = process_payment(key, 500.0, "ACC-01")

print("Call 1:", res1)
print("Call 2:", res2)
print("Duplicate prevented?", res1["transaction_id"] == res2["transaction_id"])
""",
        "has_sql_sandbox": True,
        "sql_schema": "fintech",
        "starter_sql": """-- Query existing transaction by unique idempotency_key
SELECT id, sender_account_id, receiver_account_id, amount, status, idempotency_key 
FROM transactions
WHERE idempotency_key = 'tx-idemp-001';
""",
        "solution_sql": """-- Inspect ledger and verify unique constraint on idempotency_key
SELECT 
    t.id,
    t.idempotency_key,
    s.user_name as sender,
    r.user_name as receiver,
    t.amount,
    t.status,
    t.created_at
FROM transactions t
JOIN accounts s ON t.sender_account_id = s.id
JOIN accounts r ON t.receiver_account_id = r.id
WHERE t.idempotency_key = 'tx-idemp-001';
""",
        "cross_questions": [
            "What happens if two concurrent requests with the SAME idempotency key arrive at two different FastAPI instances within 1 millisecond?",
            "How long should idempotency keys be retained in Redis/Database (TTL)?",
            "What happens if the client sends the same Idempotency-Key but with a different payload (e.g. $1000 instead of $500)?"
        ],
        "common_traps": [
            "Using client-generated timestamps instead of a client-generated UUID for idempotency keys.",
            "Not storing the response body, forcing downstream services to re-calculate state."
        ],
        "best_practices": [
            "Enforce a UNIQUE constraint in the database on `idempotency_key`.",
            "Reject requests with a 422 Unprocessable Entity if the same idempotency key is reused with mismatched parameters (payload hash validation)."
        ]
    },

    # =========================================================================
    # LEAD / ARCHITECT LEVEL (10+ Years)
    # =========================================================================
    {
        "title": "Dual-Write Problem: Database & Kafka Consistency (Transactional Outbox)",
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
In a microservices architecture, when a customer places an order, your service must:
1. Insert the order into MySQL database.
2. Publish an `OrderCreated` event to Apache Kafka for notifications and inventory.
If you commit to MySQL and Kafka publish fails, events are lost.
If you publish to Kafka first and MySQL commit fails/rolls back, ghost events are published.
How do you architect guaranteed at-least-once delivery using the Transactional Outbox Pattern and Debezium / CDC?
""",
        "theory_explanation": """
The Dual-Write problem cannot be safely solved with naive application-level consecutive writes because network partitions and process crashes can occur between step 1 and step 2.
2-Phase Commit (2PC) is rarely used in high-throughput cloud environments due to coordinator blocking and latency.
**The Transactional Outbox Pattern**:
1. Within the same local ACID transaction as the order creation, insert an event record into an `outbox_events` table in MySQL.
2. Since both writes share the same local DB transaction, atomicity is guaranteed.
3. An asynchronous CDC process (such as Debezium reading the MySQL binlog) or a dedicated poller reads the `outbox_events` table and streams events to Kafka with guaranteed at-least-once semantics.
""",
        "has_python_sandbox": True,
        "starter_code": """# Python representation of Transactional Outbox Pattern
class MockDBTransaction:
    def __init__(self):
        self.orders = []
        self.outbox_events = []
    
    def create_order_with_outbox(self, order_id: str, amount: float):
        # ATOMIC LOCAL TRANSACTION:
        # Step 1: Insert business entity
        self.orders.append({"id": order_id, "amount": amount})
        # Step 2: Insert outbox event in the SAME transaction
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
        "solution_code": """# Complete Transactional Outbox & CDC Poller simulation
class OutboxPublisher:
    def __init__(self, db):
        self.db = db
        self.kafka_cluster = []

    def poll_and_publish(self):
        # Simulates CDC / Debezium streaming from Outbox to Kafka
        for event in list(self.db.outbox_events):
            if event["status"] == "PENDING":
                self.kafka_cluster.append(event)
                event["status"] = "PUBLISHED"
                print(f"[CDC Worker] Published event {event['event_id']} to Kafka.")

# Usage:
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
    }
]
