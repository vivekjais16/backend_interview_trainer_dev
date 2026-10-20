from typing import List, Dict, Any, Optional

MINDMAP_DATA: List[Dict[str, Any]] = [
    # 1. PYTHON INTERNALS
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
    
    B --> B1["Reference Counting (Immediate Py_DECREF)"]
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
                "code_sample": """from concurrent.futures import ProcessPoolExecutor

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
            }
        ]
    },

    # 2. POSTGRESQL & MYSQL INTERNALS
    {
        "slug": "postgres-mysql-internals",
        "title": "PostgreSQL & MySQL Database Architecture",
        "category": "postgres_mysql",
        "order_index": 2,
        "description": "PostgreSQL MVCC & VACUUM, JSONB GIN indexing, MySQL InnoDB B+ Trees, Next-Key Locks, and ACID Isolation Levels.",
        "mermaid_diagram": """
graph TD
    A["Relational DB Internals"] --> B["PostgreSQL Deep Dive"]
    A --> C["MySQL InnoDB Deep Dive"]
    A --> D["ACID Isolation Levels"]
    
    B --> B1["MVCC & Heap Tuples (xmin, xmax)"]
    B --> B2["VACUUM & Table Bloat / Autovacuum"]
    B --> B3["JSONB & GIN Indexes (Fast Key/Value Lookups)"]
    B --> B4["Partial Indexes & BRIN for Large Time-Series"]
    
    C --> C1["Clustered Index (Primary Key Leaf Pages)"]
    C --> C2["Buffer Pool & Doublewrite Buffer"]
    C --> C3["Next-Key Locks (Record Lock + Gap Lock)"]
    
    D --> D1["Read Committed vs Repeatable Read"]
    D --> D2["Phantom Reads & Serializable Snapshot (SSI)"]
""",
        "nodes": [
            {
                "id": "pg-vacuum",
                "label": "PostgreSQL MVCC, Table Bloat & VACUUM",
                "depth_level": "senior",
                "mnc_importance": "Core database question for high-write microservices at Uber and Stripe.",
                "summary": "Postgres writes a completely new tuple on UPDATE, leaving the old tuple marked dead via xmax. VACUUM reclaims dead tuples so pages can be reused by future inserts.",
                "code_sample": """-- Detect bloat on high-update tables
SELECT relname, n_dead_tup, n_live_tup, 
       round(n_dead_tup * 100 / nullif(n_live_tup + n_dead_tup, 0),2) as dead_ratio
FROM pg_stat_user_tables
ORDER BY dead_ratio DESC;
""",
                "common_traps": [
                    "Running long transactions that prevent autovacuum from truncating dead tuples, causing disk exhaustion.",
                    "Using VACUUM FULL during production peak (it acquires an ACCESS EXCLUSIVE table lock)."
                ],
                "interview_cross_questions": [
                    "What is Transaction ID Wraparound in Postgres, and what happens if autovacuum freeze fails?",
                    "How does HOT (Heap-Only Tuples) optimization reduce index write amplification during updates?"
                ]
            },
            {
                "id": "pg-jsonb",
                "label": "PostgreSQL JSONB vs MySQL JSON & GIN Indexes",
                "depth_level": "mid",
                "mnc_importance": "Vital for building flexible schemas without abandoning ACID guarantees.",
                "summary": "JSONB stores decomposed binary JSON enabling fast index lookups with GIN (Generalized Inverted Index) using `@>` containment operators.",
                "code_sample": """-- Create GIN index on metadata
CREATE INDEX idx_orders_metadata_gin ON orders USING gin (metadata);

-- Fast indexed containment lookup (avoids sequential scan)
SELECT * FROM orders WHERE metadata @> '{"priority": "URGENT"}';
""",
                "common_traps": [
                    "Using plain JSON instead of JSONB (plain JSON re-parses text on every single query).",
                    "Over-indexing large nested JSONB objects, which inflates write amplification."
                ],
                "interview_cross_questions": [
                    "What is the difference between jsonb_ops and jsonb_path_ops in a GIN index?",
                    "When should you normalize data into relational columns versus keeping it inside a JSONB column?"
                ]
            }
        ]
    },

    # 3. MONGODB & NOSQL
    {
        "slug": "mongodb-nosql",
        "title": "MongoDB & Distributed NoSQL Architecture",
        "category": "mongodb_nosql",
        "order_index": 3,
        "description": "Document modeling, WiredTiger engine, Aggregation Pipelines, Sharding, Replica Sets, and the ESR Indexing Rule.",
        "mermaid_diagram": """
graph TD
    A["MongoDB & NoSQL"] --> B["Document Data Modeling"]
    A --> C["WiredTiger Storage Engine"]
    A --> D["High Availability & Sharding"]
    
    B --> B1["Embedding vs Referencing"]
    B --> B2["ESR Indexing Rule (Equality, Sort, Range)"]
    B --> B3["Aggregation Pipeline ($match, $group, $unwind)"]
    
    C --> C1["Document-Level Concurrency & Checkpointing"]
    C --> C2["WiredTiger Cache & Snappy/Zlib Compression"]
    
    D --> D1["Replica Sets & Raft-like Oplog Replication"]
    D --> D2["Write Concerns: w: majority, j: true"]
    D --> D3["Sharding: Range-based vs Hashed Shard Keys"]
""",
        "nodes": [
            {
                "id": "mongo-esr",
                "label": "The ESR Indexing Rule (Equality, Sort, Range)",
                "depth_level": "senior",
                "mnc_importance": "The most asked MongoDB query optimization rule across top tech firms.",
                "summary": "Compound indexes in MongoDB must follow the ESR sequence: First fields queried with exact Equality, next fields used in Sort, and finally fields with Range filters ($gt, $lt, $in).",
                "code_sample": """// Query: Find orders for customer, sorted by date, where total > 100
// Equality: customer_id
// Sort: created_at
// Range: total_amount
db.orders.createIndex({ customer_id: 1, created_at: -1, total_amount: 1 });
""",
                "common_traps": [
                    "Putting the Range field before the Sort field in compound indexes, forcing an in-memory sort.",
                    "Choosing a low-cardinality shard key (like country code), causing jumbo chunk bottlenecks."
                ],
                "interview_cross_questions": [
                    "What happens when write concern is set to `w: 1` vs `w: 'majority'` during a primary node failover?",
                    "How does MongoDB's aggregation pipeline optimize `$match` and `$sort` when placed early in the pipeline?"
                ]
            }
        ]
    },

    # 4. REDIS & HIGH-PERFORMANCE CACHING
    {
        "slug": "redis-caching",
        "title": "Redis Internals, Data Structures & Caching Patterns",
        "category": "redis_caching",
        "order_index": 4,
        "description": "Cache-Aside, Write-Through, Stampede, ZSET sliding-window rate limiters, and Redlock distributed locks.",
        "mermaid_diagram": """
graph TD
    A["Redis & In-Memory Caching"] --> B["Caching Strategies"]
    A --> C["Advanced Data Structures"]
    A --> D["Distributed Locking & Concurrency"]
    
    B --> B1["Cache-Aside (Lazy Loading)"]
    B --> B2["Cache Stampede & Mutex Locking"]
    B --> B3["Cache Avalanche & Jittered Expiration"]
    
    C --> C1["Hashes (HSET/HGET) vs Strings"]
    C --> C2["Sorted Sets (ZSET) for Rate Limiting & Leaderboards"]
    C --> C3["Redis Streams & Pub/Sub"]
    
    D --> D1["Atomic Operations & Lua Scripts"]
    D --> D2["Redlock Multi-Node Distributed Lock"]
    D --> D3["Lock Auto-Renewal (Watchdog pattern)"]
""",
        "nodes": [
            {
                "id": "redis-rate-limiter",
                "label": "Sliding-Window Rate Limiter using Redis ZSET",
                "depth_level": "senior",
                "mnc_importance": "Standard MNC round question for API Gateways and microservice throttling.",
                "summary": "Tracks user request timestamps in a Sorted Set (ZSET). Evicts elements older than `(now - window_size)` with `ZREMRANGEBYSCORE`, counts elements with `ZCARD`, and allows or rejects.",
                "code_sample": """-- Atomic Lua script for sliding window rate limiter:
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local clear_before = now - window

redis.call('ZREMRANGEBYSCORE', key, 0, clear_before)
local count = redis.call('ZCARD', key)
if count < limit then
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, math.ceil(window / 1000))
    return 1 -- Allowed
else
    return 0 -- Rate limited
end
""",
                "common_traps": [
                    "Using Fixed-Window counters, which allow 2x burst traffic at boundary transitions.",
                    "Running multiple consecutive Redis commands from Python without a Lua script or pipeline, creating race conditions."
                ],
                "interview_cross_questions": [
                    "What is the memory footprint of storing millions of user request timestamps in ZSETs, and how would you optimize it?",
                    "How does Martin Kleppmann critique the Redlock algorithm regarding clock drift and GC pauses?"
                ]
            }
        ]
    },

    # 5. KAFKA & EVENT-DRIVEN MESSAGING
    {
        "slug": "kafka-messaging",
        "title": "Apache Kafka & Event-Driven Architecture",
        "category": "kafka_messaging",
        "order_index": 5,
        "description": "Partitions, Consumer Groups, Offset commits, Rebalancing, Idempotent Producers, and Log Compaction.",
        "mermaid_diagram": """
graph TD
    A["Apache Kafka Architecture"] --> B["Storage & Topic Topology"]
    A --> C["Consumer Groups & Scalability"]
    A --> D["Delivery Guarantees"]
    
    B --> B1["Partitioning & Sequential Disk I/O (PageCache)"]
    B --> B2["Zero-Copy Network Transfer (sendfile syscall)"]
    B --> B3["Log Compaction & Retention Policies"]
    
    C --> C1["Consumer Rebalance (Eager vs Cooperative Sticky)"]
    C --> C2["Manual Offset Commits vs Auto Commit"]
    C --> C3["Partition Skew & Hotspot Keys"]
    
    D --> D1["At-Least-Once vs Exactly-Once (EOS)"]
    D --> D2["Idempotent Producers (PID & Sequence Numbers)"]
    D --> D3["Transactional Outbox Integration"]
""",
        "nodes": [
            {
                "id": "kafka-rebalance",
                "label": "Consumer Group Rebalance & Offset Commit Strategies",
                "depth_level": "senior",
                "mnc_importance": "Core question for high-throughput streaming systems at Uber, Netflix, and LinkedIn.",
                "summary": "When a consumer dies or new nodes are added, Kafka reassigns partitions across the consumer group. Cooperative Sticky Rebalancing avoids the 'stop-the-world' pauses of older eager rebalances.",
                "code_sample": """# Safe manual synchronous offset commit in Python kafka-python / confluent-kafka:
from confluent_kafka import Consumer

c = Consumer({'bootstrap.servers': 'localhost:9092', 'group.id': 'orders-group', 'enable.auto.commit': False})
c.subscribe(['orders.v1'])

while True:
    msg = c.poll(1.0)
    if msg is None: continue
    if msg.error(): continue
    
    # Process message business logic
    process_order(msg.value())
    
    # Commit offset only AFTER successful processing
    c.commit(msg, asynchronous=False)
""",
                "common_traps": [
                    "Using `enable.auto.commit: True` when processing takes longer than the commit interval, leading to message loss on crashes.",
                    "Executing long blocking tasks in the consumer poll loop, exceeding `max.poll.interval.ms` and causing endless rebalancing loops."
                ],
                "interview_cross_questions": [
                    "How does Kafka achieve multi-gigabyte throughput on commodity hard drives using OS PageCache and `sendfile`?",
                    "What happens if all messages in a topic have the same partition key?"
                ]
            }
        ]
    },

    # 6. CELERY & RABBITMQ
    {
        "slug": "celery-rabbitmq",
        "title": "Celery & RabbitMQ Asynchronous Task Queues",
        "category": "celery_rabbitmq",
        "order_index": 6,
        "description": "AMQP Exchanges, Celery Canvas primitives (Groups, Chords, Chains), Prefork vs Gevent, and Dead-Letter Exchanges.",
        "mermaid_diagram": """
graph TD
    A["Celery & RabbitMQ"] --> B["RabbitMQ AMQP Architecture"]
    A --> C["Celery Worker Concurrency"]
    A --> D["Resiliency & Dead Letters"]
    
    B --> B1["Exchanges: Direct, Fanout, Topic, Headers"]
    B --> B2["Bindings, Routing Keys & Virtual Hosts"]
    B --> B3["Prefetch Count (QoS) & Fair Dispatch"]
    
    C --> C1["Concurrency Pools: Prefork vs Gevent/Eventlet vs Solo"]
    C --> C2["Celery Canvas: Chords, Chains, Groups"]
    C --> C3["Worker Memory Leaks: max_tasks_per_child"]
    
    D --> D1["Dead-Letter Exchanges (DLX) & Retry Queues"]
    D --> D2["Exponential Backoff with Jitter"]
    D --> D3["Idempotent Task Execution"]
""",
        "nodes": [
            {
                "id": "celery-chord",
                "label": "Celery Canvas (Chords & Chains) and Memory Leak Mitigation",
                "depth_level": "mid",
                "mnc_importance": "Fundamental knowledge for scaling Python background jobs in production.",
                "summary": "Celery Chords execute a group of tasks in parallel and trigger a callback task once all parallel tasks finish. Worker memory leaks are controlled using `worker_max_tasks_per_child` to recycle processes.",
                "code_sample": """from celery import chord, group
from myapp.tasks import fetch_user_data, summarize_reports

# Parallel fetch with unified callback
def generate_annual_report(user_ids):
    parallel_jobs = group(fetch_user_data.s(uid) for uid in user_ids)
    workflow = chord(parallel_jobs)(summarize_reports.s())
    return workflow.id
""",
                "common_traps": [
                    "Passing large database objects / ORM instances into Celery task arguments instead of passing the integer ID.",
                    "Failing to set `acks_late=True` for critical tasks that must be retried if a worker is killed mid-execution."
                ],
                "interview_cross_questions": [
                    "Why does Celery with Gevent/Eventlet pool fail when calling synchronous C-extensions or the GIL?",
                    "How do you design a Dead-Letter Queue (DLQ) in RabbitMQ with TTL to automatically retry failed jobs 3 times with exponential delays?"
                ]
            }
        ]
    },

    # 7. DOCKER & CONTAINER SECURITY
    {
        "slug": "docker-containers",
        "title": "Docker, Containerization & Production Image Security",
        "category": "docker_containers",
        "order_index": 7,
        "description": "Multi-stage builds, non-root users, distroless images, layer caching, and SIGTERM signal handling.",
        "mermaid_diagram": """
graph TD
    A["Docker & Containers"] --> B["Image Optimization"]
    A --> C["Security Hardening"]
    A --> D["Runtime & Lifecycle"]
    
    B --> B1["Multi-Stage Builds (Build tools vs Runtime)"]
    B --> B2["Layer Caching: Order of COPY & RUN"]
    B --> B3[".dockerignore & Minimal Base (Alpine/Distroless)"]
    
    C --> C1["Non-Root User (USER appuser)"]
    C --> C2["Read-Only Root Filesystems"]
    C --> C3["Vulnerability Scanning (Trivy / Grype)"]
    
    D --> D1["PID 1 Problem & Tini (Init process)"]
    D --> D2["SIGTERM vs SIGKILL Graceful Exit"]
    D --> D3["Container Resource Constraints (--memory, --cpus)"]
""",
        "nodes": [
            {
                "id": "docker-multistage",
                "label": "Multi-Stage Dockerfile for Python FastAPI",
                "depth_level": "mid",
                "mnc_importance": "Asked in DevOps/Platform rounds to ensure minimal CVE attack surfaces.",
                "summary": "Multi-stage builds use a heavy build environment with compilers (gcc, git) to compile wheels, then copy only the compiled artifacts into a lightweight slim/distroless runtime image without compilers.",
                "code_sample": """# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final Minimal & Secure Runtime
FROM python:3.12-slim
WORKDIR /app
# Create non-root user
RUN useradd -m -u 1001 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
                "common_traps": [
                    "Running containers as `root`, giving attackers a privilege escalation vector to the host kernel.",
                    "Copying application source code before `requirements.txt`, which busts the Docker layer cache on every code commit."
                ],
                "interview_cross_questions": [
                    "Why is PID 1 special in Linux containers, and what happens when your Python app doesn't reap zombie processes?",
                    "How do you implement health checks in Docker without installing curl in a distroless container?"
                ]
            }
        ]
    },

    # 8. KUBERNETES & CLOUD-NATIVE BACKEND
    {
        "slug": "kubernetes-devops",
        "title": "Kubernetes (K8s) & Cloud-Native Production Backend",
        "category": "kubernetes_devops",
        "order_index": 8,
        "description": "Deployments, Probes (Liveness/Readiness/Startup), HPA, Zero-downtime rolling updates, and preStop hooks.",
        "mermaid_diagram": """
graph TD
    A["Kubernetes Architecture"] --> B["Workloads & Controller"]
    A --> C["Probes & Health Checks"]
    A --> D["Autoscaling & Resiliency"]
    
    B --> B1["Deployments & ReplicaSets"]
    B --> B2["StatefulSets for Distributed Databases"]
    B --> B3["ConfigMaps & Sealed Secrets"]
    
    C --> C1["Startup Probe (Slow app boot protection)"]
    C --> C2["Readiness Probe (Remove from Service endpoints)"]
    C --> C3["Liveness Probe (Restart deadlocked containers)"]
    
    D --> D1["Zero-Downtime RollingUpdate (maxUnavailable, maxSurge)"]
    D --> D2["preStop Hook + SIGTERM Graceful Shutdown"]
    D --> D3["Horizontal Pod Autoscaler (HPA with KEDA)"]
""",
        "nodes": [
            {
                "id": "k8s-graceful-shutdown",
                "label": "Zero-Downtime Rolling Update & Graceful Shutdown (preStop)",
                "depth_level": "senior",
                "mnc_importance": "The #1 reason microservices drop in-flight user requests during deployments.",
                "summary": "When a pod is deleted, Kubelet sends a SIGTERM simultaneously as kube-proxy updates iptables. Adding a `preStop` sleep hook allows existing in-flight connections to drain before the process shuts down.",
                "code_sample": """lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"] # Allows ingress/iptables to unregister pod
terminationGracePeriodSeconds: 45
""",
                "common_traps": [
                    "Making Liveness and Readiness probes point to the exact same database query. If the DB fluctuates, K8s restarts all pods simultaneously (cascading death spiral).",
                    "Setting CPU limits too tight, triggering Linux CFS quota throttling and increasing P99 latency."
                ],
                "interview_cross_questions": [
                    "What is the difference between CPU throttling and Memory OOMKill (Exit code 137) in Kubernetes?",
                    "How does KEDA (Kubernetes Event-driven Autoscaling) scale pods based on Kafka consumer lag or RabbitMQ queue length?"
                ]
            }
        ]
    },

    # 9. CI/CD & PRODUCTION SRE
    {
        "slug": "cicd-production",
        "title": "CI/CD Pipelines, SRE & Observability",
        "category": "cicd_pipelines",
        "order_index": 9,
        "description": "GitHub Actions pipelines, Trivy security scanning, Canary deployments, and OpenTelemetry distributed tracing.",
        "mermaid_diagram": """
graph TD
    A["CI/CD & SRE Observability"] --> B["Continuous Integration (CI)"]
    A --> C["Continuous Delivery (CD)"]
    A --> D["Observability & SRE"]
    
    B --> B1["Linters (Ruff, Flake8, Black)"]
    B --> B2["Pytest Matrix & Coverage Thresholds"]
    B --> B3["Security: Trivy Vulnerability & Bandit SAST"]
    
    C --> C1["Canary Deployments (Argo Rollouts)"]
    C --> C2["Blue-Green Deployments"]
    C --> C3["GitOps with ArgoCD / Flux"]
    
    D --> D1["Metrics (Prometheus & RED method)"]
    D --> D2["Distributed Tracing (OpenTelemetry + Jaeger)"]
    D --> D3["SLI, SLO & Error Budget Alerting"]
""",
        "nodes": [
            {
                "id": "cicd-canary",
                "label": "Canary Releases & OpenTelemetry Distributed Tracing",
                "depth_level": "architect",
                "mnc_importance": "Standard evaluation for Lead/Staff engineers overseeing tier-1 production systems.",
                "summary": "Canary releases route 5% of production traffic to a new version, automatically rolling back if HTTP 5xx error rates spike or P99 latency exceeds the SLO.",
                "code_sample": """# GitHub Actions step for automated Trivy container scan:
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:${{ github.sha }}'
    format: 'table'
    exit-code: '1'
    ignore-unfixed: true
    severity: 'CRITICAL,HIGH'
""",
                "common_traps": [
                    "Deploying schema migrations in the same step as code changes without backward compatibility (breaks rolling updates).",
                    "Logging sensitive PII or credentials in unmasked application logs."
                ],
                "interview_cross_questions": [
                    "How do you design backward and forward compatible database migrations for Blue-Green deployments?",
                    "How does distributed trace context propagation work over HTTP headers (`traceparent`, W3C standard) and Kafka message headers?"
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
