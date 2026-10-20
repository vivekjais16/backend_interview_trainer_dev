"""
Centralized Concept Hub (Inspired by InterviewBit, GeeksforGeeks, and Top Tech Interview Standards).
Contains structured, categorized concepts, complexity formulas, under-the-hood breakdowns, and 30-second punchlines.
"""

from typing import List, Dict, Any

CENTRALIZED_CONCEPTS: List[Dict[str, Any]] = [
    # ------------------ PYTHON INTERNALS & DATA TYPES ------------------
    {
        "id": "py-memory-model",
        "category": "python",
        "category_name": "Python Mastery",
        "title": "Python Memory Model, Object Headers & Reference Counting",
        "badge": "MNC Favorite",
        "difficulty": "Intermediate",
        "summary": "Every object in CPython is represented by a C struct (PyObject) with a reference count and type pointer. Memory is managed via reference counting for immediate cleanup plus a 3-generation cyclic garbage collector for circular references.",
        "key_mechanisms": [
            "PyObject Header contains ob_refcnt (8 bytes) and ob_type pointer (8 bytes).",
            "Small Integer Cache: Integers from -5 to 256 are pre-allocated singletons in memory at startup.",
            "String Interning: Python automatically interns compile-time constant identifiers and strings via sys.intern().",
            "Cyclic Garbage Collector: Handles circular references across 3 generations (Gen 0, 1, 2) using doubly linked lists."
        ],
        "complexity": "Allocation: O(1) from pymalloc arena pool; Deallocation: Immediate O(1) when ob_refcnt == 0.",
        "interview_punchline": "CPython uses deterministic reference counting for immediate reclamation and a generational cyclic GC (Gen 0, 1, 2) to break reference cycles.",
        "code_snippet": "import sys\na = 256\nb = 256\nprint(a is b)  # True (interned small integer pool)\n\nx = [1, 2]\ny = x          # sys.getrefcount(x) increases",
        "related_slugs": ["python-shallow-deep-copy-memory", "python-new-vs-init-singleton"]
    },
    {
        "id": "py-dict-internals",
        "category": "python",
        "category_name": "Python Mastery",
        "title": "Python Dictionaries: Compact Hash Table & SipHash",
        "badge": "High Frequency",
        "difficulty": "Intermediate",
        "summary": "Since Python 3.6 (PEP 468), dicts preserve insertion order while reducing memory by 30-95% using a split design: a sparse hash index table mapping to a dense entries array of (hash, key, value).",
        "key_mechanisms": [
            "Sparse index array stores indices pointing into a compact dense array containing actual key-value objects.",
            "Collision resolution: Uses open addressing with a pseudorandom perturbation formula: j = ((5*j) + 1 + perturb) & mask.",
            "Security: Key hashes use SipHash with a randomized per-process seed to defend against HashDoS algorithmic complexity attacks.",
            "Resizing: When load factor exceeds 2/3 (66%), the table reallocates to a larger power of 2 and repopulates dense entries."
        ],
        "complexity": "Lookup / Insert / Delete: Average O(1), Worst-case O(N) during extreme hash collisions.",
        "interview_punchline": "Python dicts achieve order-preservation and memory compaction by separating a sparse hash index array from a dense entries array, resolved via open addressing.",
        "code_snippet": "# Compact table layout:\n# indices = [-1, 0, -1, 1, -1, 2]\n# entries = [\n#   [hash('a'), 'a', 10],\n#   [hash('b'), 'b', 20],\n# ]",
        "related_slugs": ["python-mutable-default-argument"]
    },
    {
        "id": "py-gil-concurrency",
        "category": "python",
        "category_name": "Python Mastery",
        "title": "CPython GIL (Global Interpreter Lock) & Concurrency Matrix",
        "badge": "Must Know",
        "difficulty": "Advanced",
        "summary": "The GIL is a mutual-exclusion lock preventing multiple native OS threads from executing CPython bytecodes simultaneously. It protects memory management (ob_refcnt) from race conditions.",
        "key_mechanisms": [
            "CPU-bound tasks: Threading causes high latency due to OS context switching and GIL contention without speedup. Use multiprocessing.",
            "I/O-bound tasks: Threads and AsyncIO release the GIL during network and file system system calls (read, write, sleep).",
            "PEP 703 (Free-threaded Python 3.13+): Introduces experimental build disabling GIL using mimalloc and biased reference counting.",
            "AsyncIO: Single-threaded cooperative multitasking using an event loop (epoll/kqueue) avoiding thread overhead entirely."
        ],
        "complexity": "Context switch overhead: ~1-2 microseconds per thread switch under GIL contention.",
        "interview_punchline": "The GIL protects CPython memory refcounts by serializing bytecode execution; use AsyncIO or threading for I/O-bound workloads, and multiprocessing or C-extensions for CPU-bound computation.",
        "code_snippet": "import asyncio\n\n# Non-blocking async cooperative task\nasync def fetch_user(uid: int):\n    await asyncio.sleep(0.01) # GIL released during I/O\n    return {'uid': uid}",
        "related_slugs": ["fastapi-async-event-loop-starvation"]
    },
    {
        "id": "py-generators-memory",
        "category": "python",
        "category_name": "Python Mastery",
        "title": "Generators, Iterators & O(1) Constant Memory Pipelines",
        "badge": "Must Know",
        "difficulty": "Basic",
        "summary": "Generators implement the Iterator Protocol (__iter__, __next__) lazily evaluating one element at a time on demand. This allows streaming gigabytes of data through pipelines with O(1) constant auxiliary memory.",
        "key_mechanisms": [
            "Generator execution freezes local state (frame object, instruction pointer f_lasti) upon yield and resumes on next().",
            "Iterator Protocol: Objects defining __iter__() returning an iterator, and __next__() raising StopIteration when exhausted.",
            "yield from: Delegates subgenerator iteration and bi-directional value/exception passing seamlessly.",
            "Memory benchmark: [x for x in range(10_000_000)] takes ~800MB RAM, while (x for x in range(10_000_000)) takes ~104 bytes."
        ],
        "complexity": "Memory: O(1) constant auxiliary memory; Time: O(1) per yielded element.",
        "interview_punchline": "Generators produce items lazily on demand, decoupling computational pipelines while maintaining strict O(1) memory footprint regardless of dataset size.",
        "code_snippet": "def read_huge_file(filepath):\n    with open(filepath, 'r') as f:\n        for line in f:\n            yield line.strip()  # O(1) memory streaming",
        "related_slugs": ["python-generators-memory-efficiency"]
    },

    # ------------------ SQL & DATABASE INTERNALS ------------------
    {
        "id": "sql-btree-indexing",
        "category": "sql",
        "category_name": "SQL & Database Internals",
        "title": "B-Tree Index Internals & The Leftmost Prefix Rule",
        "badge": "Top MNC Question",
        "difficulty": "Intermediate",
        "summary": "Relational databases (MySQL InnoDB, PostgreSQL) use balanced B+ Trees for primary and secondary indexing. Leaf nodes form a doubly linked list enabling rapid point lookups and range scans.",
        "key_mechanisms": [
            "Clustered Index: In MySQL InnoDB, the primary key B+ Tree leaf nodes store actual table rows. Non-leaf nodes store keys and child page pointers.",
            "Secondary Index: Leaf nodes store the secondary index columns plus the primary key reference (requiring double lookup / table lookup unless covering).",
            "Leftmost Prefix Rule: A composite index ON (a, b, c) can satisfy queries on (a), (a, b), and (a, b, c), but NOT on (b) or (c) alone.",
            "Range Predicate Trap: In ON (a, b, c), if WHERE a = 1 AND b > 10 AND c = 'ACTIVE', column c cannot use the index for filtering because b is a range."
        ],
        "complexity": "Lookup / Insert: O(log_B N) where B is fanout (~100-500 keys per 16KB page, tree height is typically 3-4 levels for millions of rows).",
        "interview_punchline": "B+ Trees organize data in balanced 16KB pages with leaf-level doubly linked lists; composite indexes must follow the leftmost prefix rule, ordering equality filters before ranges.",
        "code_snippet": "-- Optimal composite index for WHERE user_id = ? AND created_at > ?\nCREATE INDEX idx_user_created ON orders (user_id, created_at);",
        "related_slugs": ["sql-joins-null-handling-optimization", "sql-nth-highest-salary"]
    },
    {
        "id": "sql-acid-isolation",
        "category": "sql",
        "category_name": "SQL & Database Internals",
        "title": "ACID Properties & Transaction Isolation Levels",
        "badge": "MNC Favorite",
        "difficulty": "Advanced",
        "summary": "ACID guarantees database reliability. Isolation levels define how transactions see concurrent mutations, trading concurrency performance against consistency anomalies.",
        "key_mechanisms": [
            "Read Uncommitted: Allows Dirty Reads (reading uncommitted changes from other concurrent transactions).",
            "Read Committed (Postgres default): Read sees only committed data. Non-repeatable reads possible (rereading same row yields different values).",
            "Repeatable Read (MySQL InnoDB default): Snapshot isolation using MVCC undo log. Eliminates non-repeatable reads; prevents phantoms in InnoDB via Next-Key locks.",
            "Serializable: Full serializability via strict two-phase locking (2PL) or Serializable Snapshot Isolation (SSI).",
            "MVCC (Multi-Version Concurrency Control): Readers do not block writers and writers do not block readers."
        ],
        "complexity": "Concurrency: Read Committed (Highest throughput) -> Serializable (Lowest throughput, highest abort rate).",
        "interview_punchline": "MVCC provides non-blocking reads using undo log version snapshots; Repeatable Read in InnoDB uses Next-Key locks to eliminate phantom rows.",
        "code_snippet": "-- Inspect and set isolation level\nSET TRANSACTION ISOLATION LEVEL REPEATABLE READ;\nSTART TRANSACTION;\nSELECT * FROM accounts WHERE id = 101 FOR UPDATE; -- pessimistic lock",
        "related_slugs": ["mysql-deadlock-next-key-gap-locks", "sqlalchemy-n-plus-1-query-optimization"]
    },

    # ------------------ REDIS & CACHING ------------------
    {
        "id": "redis-cache-patterns",
        "category": "redis",
        "category_name": "Redis & In-Memory Caching",
        "title": "Caching Strategies & The Three Cache Catastrophes",
        "badge": "Must Know",
        "difficulty": "Intermediate",
        "summary": "Caching reduces database load by keeping frequently accessed items in memory. Production systems must defend against Cache Penetration, Cache Avalanche, and Cache Stampede.",
        "key_mechanisms": [
            "Cache-Aside (Lazy Loading): App checks Redis first; on miss, loads from DB and writes back to Redis with TTL. Most common pattern.",
            "Cache Penetration: Requests for non-existent IDs bypass cache and hammer database. Fix: Bloom filters or cache null values with short TTL.",
            "Cache Avalanche: Thousands of keys expire simultaneously under high traffic. Fix: Add random TTL jitter (e.g. 3600s + rand(0, 300s)).",
            "Cache Stampede (Thundering Herd): High-concurrency read on an expensive key that just expired. Fix: Distributed lock with mutex or probabilistic early expiration (XFetch)."
        ],
        "complexity": "Redis in-memory read: O(1) with sub-millisecond P99 latency.",
        "interview_punchline": "Protect cache architectures from avalanche with randomized TTL jitter, from penetration with Bloom filters, and from stampede using distributed mutex locks.",
        "code_snippet": "# Atomic acquisition with NX and expiration EX\nSET lock:resource:123 token_uuid NX EX 30\n\n# Safe Lua unlock script\nif redis.call('get', KEYS[1]) == ARGV[1] then\n    return redis.call('del', KEYS[1])\nelse\n    return 0\nend",
        "related_slugs": ["redis-cache-stampede-rate-limiter", "redis-distributed-lock-watchdog-lua"]
    },

    # ------------------ DOCKER & KUBERNETES ------------------
    {
        "id": "docker-k8s-production",
        "category": "devops",
        "category_name": "Docker & Kubernetes Architecture",
        "title": "Container Hardening, Multi-Stage Builds & Zero-Downtime Probes",
        "badge": "Top MNC Question",
        "difficulty": "Advanced",
        "summary": "Production containers require minimal image attack surface, clean signal propagation (PID 1), and Kubernetes probes to guarantee zero 502 Bad Gateway errors during rolling updates.",
        "key_mechanisms": [
            "Multi-Stage Builds: Discard build toolchains and compilers; copy only runtime artifacts to Distroless or Debian-slim base.",
            "PID 1 & Signals: Linux init processes reap zombies and propagate SIGTERM. Wrap Python in tini or dumb-init; avoid shell form in CMD.",
            "Readiness Probe: Validates pod can accept traffic. Failing readiness removes pod from Service endpoints without restarting it.",
            "Liveness Probe: Detects deadlocks and restarts frozen containers. Do NOT check external databases in liveness probes.",
            "Graceful Shutdown: Kubernetes sends SIGTERM while removing endpoints. Use a preStop sleep hook (sleep 5) to allow iptables propagation before app exits."
        ],
        "complexity": "Rolling update: maxUnavailable=0 ensures 100% capacity retention during container deployments.",
        "interview_punchline": "Combine multi-stage distroless builds, tini signal reaping, and a preStop sleep hook with readiness probes to guarantee zero-downtime rolling deploys.",
        "code_snippet": "# Kubernetes zero-downtime deployment spec\nlifecycle:\n  preStop:\n    exec:\n      command: [\"/bin/sh\", \"-c\", \"sleep 5\"]\nreadinessProbe:\n  httpGet:\n    path: /health/readiness\n    port: 8000\n  periodSeconds: 5",
        "related_slugs": ["docker-cmd-entrypoint-caching-basics", "docker-multistage-security-hardening", "kubernetes-zero-downtime-probes"]
    },

    # ------------------ SYSTEM DESIGN & MICROSERVICES ------------------
    {
        "id": "sys-transactional-outbox",
        "category": "system_design",
        "category_name": "System Design & Microservices",
        "title": "Dual-Write Problem & The Transactional Outbox Pattern",
        "badge": "Staff / Architect",
        "difficulty": "Architect",
        "summary": "In microservices, writing to a relational database and publishing to Kafka cannot be wrapped in a single distributed transaction without brittle 2PC. The Transactional Outbox pattern guarantees eventual consistency.",
        "key_mechanisms": [
            "The Dual-Write Hazard: If DB commits but Kafka publish fails (or vice versa), the system suffers permanent data inconsistency.",
            "Transactional Outbox: In the same local ACID transaction that updates business tables, write event payloads into an 'outbox' table.",
            "Change Data Capture (CDC): An asynchronous worker or Debezium tailing the DB binary log (WAL) reads outbox rows and publishes them to Kafka.",
            "Idempotent Consumers: Consumers store processed message IDs to handle duplicate at-least-once deliveries safely."
        ],
        "complexity": "Latency: Asynchronous replication with sub-second eventual consistency; Zero distributed locks.",
        "interview_punchline": "Solve dual-write consistency by writing events to a local outbox table inside the business transaction, published asynchronously via Change Data Capture.",
        "code_snippet": "-- Atomic local transaction\nSTART TRANSACTION;\nUPDATE accounts SET balance = balance - 500 WHERE id = 101;\nINSERT INTO outbox_events (event_type, payload) VALUES ('PAYMENT_PROCESSED', '{\"account\": 101, \"amount\": 500}');\nCOMMIT;",
        "related_slugs": ["dual-write-kafka-transactional-outbox", "kafka-consumer-lag-rebalancing"]
    },
    {
        "id": "sys-rate-limiting",
        "category": "system_design",
        "category_name": "System Design & Microservices",
        "title": "Distributed Rate Limiting: Token Bucket vs Sliding Window",
        "badge": "High Frequency",
        "difficulty": "Intermediate",
        "summary": "Rate limiting protects microservices and payment gateways from denial-of-service and noisy neighbors by throttling requests per IP, user, or API key.",
        "key_mechanisms": [
            "Fixed Window Counter: Memory efficient, but allows 2x traffic bursts at window boundaries (e.g. 100 req at 00:59 and 100 at 01:00).",
            "Token Bucket: Tokens refill at constant rate; burst capacity up to bucket size. Highly efficient.",
            "Sliding Window Log: Stores timestamps in Redis Sorted Set (ZSET); removes elements older than window size. Accurate but higher memory.",
            "Sliding Window Counter: Combines current window and previous window counts weighted by elapsed time. Memory efficient and prevents boundary spikes."
        ],
        "complexity": "Sliding Window Counter: O(1) time complexity, minimal memory (2 Redis keys per client).",
        "interview_punchline": "Use Sliding Window Counter with Redis atomic Lua scripts to achieve accurate distributed rate limiting without boundary burst hazards.",
        "code_snippet": "# Redis Sliding Window Lua script\n# Removes timestamps older than (now - window)\nZREMRANGEBYSCORE key 0 (now - window)\nlocal count = ZCARD key\nif count < limit then\n    ZADD key now now\n    return 1\nelse\n    return 0\nend",
        "related_slugs": ["redis-cache-stampede-rate-limiter"]
    }
]

def get_concepts_catalog() -> List[Dict[str, Any]]:
    """Returns the centralized concept reference bank."""
    return CENTRALIZED_CONCEPTS
