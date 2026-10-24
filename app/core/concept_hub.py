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
    },

    # ------------------ GEN AI & LLM INFERENCE ------------------
    {
        "id": "genai-paged-attention",
        "category": "gen_ai",
        "category_name": "Gen AI & LLM Inference",
        "title": "KV-Cache Management & PagedAttention Architecture",
        "badge": "Staff Must Know",
        "difficulty": "Advanced",
        "summary": "In generative transformer serving, the autoregressive generation loop requires caching previous token Key and Value tensors. Naive contiguous allocation causes 60-80% VRAM waste. PagedAttention solves this via virtual memory block tables.",
        "key_mechanisms": [
            "Autoregressive generation: Each generated token attends to all previous tokens; caching K and V avoids quadratic recomputations.",
            "Memory waste hazard: Dynamic output lengths force naive servers to pre-allocate maximum context size, fragmenting GPU high-bandwidth memory (HBM).",
            "PagedAttention Virtual Pages: Partitions the KV cache into fixed-size physical blocks (e.g., 16 tokens), indexed via logical-to-physical block tables.",
            "Copy-on-Write (COW): Enables parallel sampling and beam search to share common prompt prefix blocks without memory duplication."
        ],
        "complexity": "KV Cache size per token: 2 * 2 * n_layers * n_heads * d_head bytes. Memory waste drops from ~70% to < 4%.",
        "interview_punchline": "PagedAttention eliminates GPU memory fragmentation by dividing the transformer KV-cache into discrete non-contiguous physical blocks mapped via virtual block tables.",
        "code_snippet": "# vLLM / PagedAttention concept:\n# logical_blocks = [0, 1, 2]\n# physical_gpu_pages = [page_102, page_45, page_88]\n# Tokens are fetched non-contiguously by custom CUDA attention kernels.",
        "related_slugs": ["genai-pagedattention-kvcache-vllm-serving"]
    },

    # ------------------ RAG & VECTOR SEARCH ------------------
    {
        "id": "rag-hybrid-retrieval",
        "category": "rag_systems",
        "category_name": "RAG & Vector Retrieval",
        "title": "Enterprise RAG: Dense HNSW Search + Sparse BM25 + Reciprocal Rank Fusion",
        "badge": "MNC Favorite",
        "difficulty": "Advanced",
        "summary": "Pure vector search struggles on exact keywords, codes, or domain terms. Enterprise RAG combines dense semantic embeddings with sparse lexical indexing (BM25), merged via Reciprocal Rank Fusion and cross-encoder re-ranking.",
        "key_mechanisms": [
            "Dense Semantic Search: Generates embeddings via models (e.g. text-embedding-3-large); queries using HNSW graph index for semantic understanding.",
            "Sparse Keyword Search: Inverted indexes with BM25 scoring for exact identifiers, product SKUs, and proper nouns.",
            "Reciprocal Rank Fusion (RRF): Formula RRF(d) = sum(1 / (k + rank_i(d))) combines heterogeneous score distributions without manual score calibration.",
            "Re-Ranking: Top 50 candidates are evaluated with a cross-encoder transformer model for deep contextual relevance before passing to LLM context."
        ],
        "complexity": "Dense HNSW search: O(log N); Sparse BM25: O(1) posting list lookup; Re-ranker: O(M * L^2) where M is top-K candidate count.",
        "interview_punchline": "Enterprise RAG achieves high recall and precision by fusing dense HNSW vector search with sparse BM25 inverted indexes using Reciprocal Rank Fusion.",
        "code_snippet": "def reciprocal_rank_fusion(dense_ranks, sparse_ranks, k=60):\n    scores = {}\n    for doc, r in dense_ranks.items(): scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + r)\n    for doc, r in sparse_ranks.items(): scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + r)\n    return sorted(scores.items(), key=lambda x: x[1], reverse=True)",
        "related_slugs": ["rag-hnsw-vs-ivfflat-vector-search-embeddings"]
    },

    # ------------------ VECTOR DATABASES ------------------
    {
        "id": "vector-hnsw-indexing",
        "category": "vector_databases",
        "category_name": "Vector Databases & Indexing",
        "title": "HNSW (Hierarchical Navigable Small World) Graph Architecture",
        "badge": "Top MNC Question",
        "difficulty": "Staff",
        "summary": "HNSW is the gold-standard algorithm powering vector databases (Milvus, Pinecone, Qdrant). It solves the high-dimensional Approximate Nearest Neighbor (ANN) problem by building multi-layer proximity graphs.",
        "key_mechanisms": [
            "Skip-List Hierarchy: Top layers have long-range links for fast macroscopic navigation; bottom layer 0 contains dense local neighbor links.",
            "Greedy Traversal: Search starts at top layer entry point, moving to the neighbor closest to query vector until a local minimum is reached, then drops to the next layer.",
            "Bounded Degree M: Controls memory and connectivity; heuristics prune redundant edges while preserving cluster connectedness.",
            "Distance Metrics: Cosine similarity (1 - (u·v)/(||u||*||v||)), Dot Product (for normalized vectors), and Euclidean (L2) distance."
        ],
        "complexity": "Query time: O(log N) average; Build time: O(N log N); Storage: Higher RAM footprint due to bi-directional link graphs.",
        "interview_punchline": "HNSW achieves sub-10ms Approximate Nearest Neighbor search on millions of vectors by traversing multi-layer proximity skip-graphs in O(log N) time.",
        "code_snippet": "# HNSW layer traversal:\n# Layer 2: [Start Node] -------------> [Cluster Center]\n# Layer 1: [Cluster Center] ----> [Sub-Cluster]\n# Layer 0: [Sub-Cluster] -> [Exact Nearest Neighbors (k=10)]",
        "related_slugs": ["rag-hnsw-vs-ivfflat-vector-search-embeddings"]
    },

    # ------------------ MACHINE LEARNING & MLOPS ------------------
    {
        "id": "ml-lora-peft",
        "category": "machine_learning",
        "category_name": "Machine Learning & MLOps",
        "title": "Parameter-Efficient Fine-Tuning (PEFT) & LoRA Decomposition",
        "badge": "Staff Must Know",
        "difficulty": "Advanced",
        "summary": "Fine-tuning multi-billion parameter foundation models requires massive compute and risks catastrophic forgetting. Low-Rank Adaptation (LoRA) freezes the base model and trains low-rank decomposition matrices.",
        "key_mechanisms": [
            "Intrinsic Rank Hypothesis: Weight updates ΔW during domain adaptation live in a much lower dimensional subspace than original weight matrix W0.",
            "Decomposition: Represents update as ΔW = B * A, where B is (d x r) and A is (r x k) with rank r << min(d, k) (typically r=8 or 16).",
            "Zero Initialization: A is initialized with Gaussian noise and B is initialized to zeros, ensuring ΔW = 0 at the start of training.",
            "Multi-Tenant Serving: A single GPU serves multiple tenant adapters by dynamically swapping only small A and B matrices during inference."
        ],
        "complexity": "Trainable parameters: Reduced by >99.9%; Optimizer state memory: Vanishes, enabling 70B parameter tuning on consumer GPUs.",
        "interview_punchline": "LoRA freezes foundation model weights and decomposes updates into low-rank matrices ΔW = B * A, slashing training memory by 99% while enabling multi-tenant adapter hot-swapping.",
        "code_snippet": "# LoRA forward pass:\n# output = W0(x) + (alpha / r) * (B(A(x)))\n# W0 is frozen; only B and A accumulate gradients.",
        "related_slugs": ["mlops-lora-peft-parameter-efficient-fine-tuning"]
    },

    # ------------------ DATA SCIENCE & FEATURE PIPELINES ------------------
    {
        "id": "ds-feature-stores",
        "category": "data_science",
        "category_name": "Data Science & Feature Engineering",
        "title": "Feature Stores: Point-in-Time Correctness & Training-Serving Skew",
        "badge": "MNC Favorite",
        "difficulty": "Advanced",
        "summary": "Production ML systems suffer when offline training features leak future event data or differ from real-time production features. Feature Stores (Feast, Hopsworks) guarantee point-in-time correctness.",
        "key_mechanisms": [
            "Training-Serving Skew: Discrepancy between feature engineering logic in offline batch pipelines (Spark/SQL) versus real-time online inference (Python/Go).",
            "Target / Data Leakage: Joining training examples with future feature state (e.g. including fraud signals timestamped after the transaction occurred).",
            "ASOF Point-in-Time Join: Automatically projects backward in time, joining each observation with the most recent feature value that existed prior to event timestamp.",
            "Dual-Storage Architecture: Low-latency online store (Redis/DynamoDB) for sub-10ms lookup + analytical offline store (Snowflake/BigQuery) for training."
        ],
        "complexity": "Online read: O(1) Redis key lookup; Offline join: O(N log N) distributed temporal sort/merge join.",
        "interview_punchline": "Feature Stores eliminate training-serving skew and data leakage by unifying feature definitions and executing point-in-time ASOF joins on historical datasets.",
        "code_snippet": "-- ASOF Temporal Join:\nSELECT event.user_id, event.timestamp, f.user_rolling_fraud_score\nFROM transaction_events event\nASOF JOIN user_features f\nON event.user_id = f.user_id AND event.timestamp >= f.feature_timestamp",
        "related_slugs": ["datascience-feature-stores-point-in-time-leakage"]
    },

    # ------------------ NOSQL & DISTRIBUTED DATA STORES ------------------
    {
        "id": "nosql-tunable-consistency",
        "category": "nosql_distributed",
        "category_name": "NoSQL & Distributed Stores",
        "title": "NoSQL Tunable Consistency & Cassandra Ring Architecture",
        "badge": "Staff Must Know",
        "difficulty": "Staff",
        "summary": "Distributed leaderless NoSQL systems (Apache Cassandra, Amazon DynamoDB) distribute data using consistent hashing and allow tuning trade-offs between consistency, availability, and latency on every read/write operation.",
        "key_mechanisms": [
            "Quorum Equation: Strong consistency is guaranteed when R + W > N (Read nodes + Write nodes exceed Replication Factor N).",
            "Local Quorum: Restricts quorum validation to nodes inside the local datacenter ((N_local / 2) + 1), avoiding high-latency cross-region WAN roundtrips.",
            "LSM-Tree Storage: Writes append to CommitLog (WAL) and Memtable in RAM; flushed sequentially to immutable SSTables on disk, avoiding random I/O.",
            "Read Repair & Anti-Entropy: Mismatched read responses trigger background read repairs; periodic anti-entropy repairs use Merkle trees to reconcile cold data."
        ],
        "complexity": "Write: O(1) append-only sequential disk write; Read: O(log N) SSTable Bloom filter + B-Tree index lookup.",
        "interview_punchline": "Leaderless NoSQL databases achieve high write throughput via append-only LSM-trees and allow fine-grained CAP trade-offs via tunable read/write quorums.",
        "code_snippet": "// Strong consistency without WAN latency:\nstatement.setConsistencyLevel(ConsistencyLevel.LOCAL_QUORUM);",
        "related_slugs": ["sys-idempotency-tracing-15-idempotency-keys,-exactly-once"]
    }
]

def get_concepts_catalog() -> List[Dict[str, Any]]:
    """Returns the centralized concept reference bank."""
    return CENTRALIZED_CONCEPTS
