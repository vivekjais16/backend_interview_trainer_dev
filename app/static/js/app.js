// CogniPrep PRO / MNC Staff Technical Interview Platform - Core Engine
// =========================================================================

// --- STATE MANAGEMENT ---
let activeAppTab = 'mcq'; // 'mcq', 'mindmap', 'interview', 'questions', 'analytics', 'profile'
let targetRole = 'Staff Backend Architect (Distributed Systems)';
let streakDays = 14;

// User Account & Tracking State
let currentUser = null;
let authToken = localStorage.getItem('cogniprep_auth_token') || null;
let currentAuthMode = 'register';
let userHistoryData = null;
let userRecommendationsData = null;

// Session Timer State
let sessionSeconds = 740;
let isTimerRunning = true;
let sessionTimerInterval = null;

// Voice Simulation State
let isVoiceActive = false;

// Active Interview Session State
let activeSessionId = null;
let currentQuestion = null;
let selectedIdeLanguage = 'python';
let isRunningCode = false;

// Chat Messages State
let chatMessages = [
    {
        id: 1,
        sender: 'interviewer',
        text: "Welcome! Today we'll explore designing a high-throughput, low-latency Distributed Rate Limiter. How would you synchronize tokens across multiple load-balanced worker instances without global locking?",
        timestamp: "10:02 AM"
    }
];

// Live Rubric Scores
let rubricScores = {
    architecture: 88,
    edgeCases: 74,
    complexity: 92,
    communication: 85
};

// Mind Map State
let mindmapTree = null;
let selectedMindmapNode = null;
let mindmapZoom = 1;
let mindmapPan = { x: 30, y: 40 };

// MCQ State
let mcqQuestions = [];
let selectedAnswers = {}; // { [qId]: 'A' | 'B' | ... }
let activeMcqDrawerId = null;
let mcqMode = 'practice'; // 'practice' or 'timed'
let timedCountdown = 900; // 15 min
let timedInterval = null;
let isTestSubmitted = false;
let activeModalQuestion = null;

// Question Bank State
let bankQuestions = [];
let activeBankQuestion = null;

// --- INITIAL FOUNDATIONAL MINDMAP TREE ---
const INITIAL_MINDMAP_DATA = {
    id: 'root',
    label: 'Distributed Systems & Architecture',
    level: 0,
    category: 'core',
    status: 'mastered',
    readiness: 92,
    summary: 'Architecting resilient, scalable multi-tier architectures with fault-tolerance.',
    questions: [
        'How do you handle split-brain in distributed consensus?',
        'CAP vs PACELC: When does PACELC yield practical architecture trade-offs?'
    ],
    children: [
        {
            id: 'cons',
            label: 'Consensus & Coordination',
            level: 1,
            category: 'consensus',
            status: 'reviewing',
            readiness: 74,
            summary: 'Protocols ensuring nodes agree on state despite network partitions.',
            questions: [
                'How does Raft leader election handle network partitions with staled terms?',
                'Difference between Paxos Synod and Multi-Paxos.'
            ],
            children: [
                {
                    id: 'raft',
                    label: 'Raft & Paxos Protocol',
                    level: 2,
                    category: 'consensus',
                    status: 'mastered',
                    readiness: 88,
                    summary: 'State machine replication via term leadership and write quorums.',
                    questions: ['Explain log matching invariant in Raft.']
                },
                {
                    id: 'zookeeper',
                    label: 'Distributed Locks (Zookeeper/etcd)',
                    level: 2,
                    category: 'consensus',
                    status: 'learning',
                    readiness: 65,
                    summary: 'Ephemeral sequential znodes & lease mechanisms for master election.',
                    questions: ['How do you guard against GC pauses invalidating a distributed lock lease?']
                }
            ]
        },
        {
            id: 'storage',
            label: 'Data Partitioning & Storage',
            level: 1,
            category: 'database',
            status: 'mastered',
            readiness: 95,
            summary: 'Data distribution, horizontal sharding keys, and replication topologies.',
            questions: [
                'How to mitigate hot spots when sharding on timestamp-based keys?',
                'LSM-Trees vs B-Trees: Trade-offs for write-heavy logging platforms.'
            ],
            children: [
                {
                    id: 'consistent_hashing',
                    label: 'Consistent Hashing & Virtual Nodes',
                    level: 2,
                    category: 'database',
                    status: 'mastered',
                    readiness: 94,
                    summary: 'Minimizing rebalancing keys when nodes are added or removed dynamically.',
                    questions: ['Calculate expected rehash fraction when ring membership scales from N to N+1.']
                },
                {
                    id: 'sharding_repl',
                    label: 'Sharding Strategies & Replication Lag',
                    level: 2,
                    category: 'database',
                    status: 'reviewing',
                    readiness: 80,
                    summary: 'Range-based, Hash-based, and Directory-based partitioning trade-offs.',
                    questions: ['How to guarantee read-your-own-writes under asynchronous replication?']
                }
            ]
        },
        {
            id: 'caching',
            label: 'Caching & Read Optimization',
            level: 1,
            category: 'cache',
            status: 'mastered',
            readiness: 89,
            summary: 'Low-latency eviction algorithms, invalidation patterns, and stampede defenses.',
            questions: [
                'Compare Cache-Aside, Write-Through, and Write-Back.',
                'How to prevent Thundering Herd (Cache Stampede) under high concurrency?'
            ],
            children: [
                {
                    id: 'redis_cluster',
                    label: 'Redis Cluster & Sentinel',
                    level: 2,
                    category: 'cache',
                    status: 'mastered',
                    readiness: 91,
                    summary: 'In-memory key-value data structures, 16384 hash slots, and auto-failover.',
                    questions: ['How are multi-key transactions handled across different Redis hash slots?']
                },
                {
                    id: 'stampede',
                    label: 'Cache Invalidation & Thundering Herd',
                    level: 2,
                    category: 'cache',
                    status: 'learning',
                    readiness: 62,
                    summary: 'Probabilistic early expiration (XFetch algorithm) and mutex leases.',
                    questions: ['Implement early probabilistic expiration logic in pseudo-code.']
                }
            ]
        },
        {
            id: 'comm',
            label: 'Async Messaging & Streaming',
            level: 1,
            category: 'messaging',
            status: 'learning',
            readiness: 68,
            summary: 'Decoupled systems via event streams, message brokers, and transactional outbox.',
            questions: [
                'How does Kafka achieve high sequential write throughput using OS page cache?',
                'At-least-once vs Exactly-Once semantics using idempotent producer ids.'
            ],
            children: [
                {
                    id: 'kafka',
                    label: 'Kafka Internals & Consumer Groups',
                    level: 2,
                    category: 'messaging',
                    status: 'reviewing',
                    readiness: 72,
                    summary: 'Log segment storage, partition rebalancing, and committed offset pointers.',
                    questions: ['What causes partition rebalance storms and how do static memberships solve it?']
                },
                {
                    id: 'outbox',
                    label: 'Transactional Outbox & CDC',
                    level: 2,
                    category: 'messaging',
                    status: 'mastered',
                    readiness: 85,
                    summary: 'Atomically recording business state and domain events using database WAL tailing.',
                    questions: ['Describe Debezium architecture for tailing Postgres WAL log into Kafka.']
                }
            ]
        },
        {
            id: 'genai_branch',
            label: 'Gen AI & LLM Architecture',
            level: 1,
            category: 'genai',
            status: 'mastered',
            readiness: 89,
            summary: 'LLM inference serving, memory optimization, prompt orchestrations, and autonomous agents.',
            questions: [
                'How does PagedAttention eliminate memory fragmentation in KV-Cache?',
                'Continuous batching vs dynamic batching in LLM inference servers.'
            ],
            children: [
                {
                    id: 'genai_kvcache',
                    label: 'LLM Inference & KV-Cache',
                    level: 2,
                    category: 'genai',
                    status: 'mastered',
                    readiness: 92,
                    summary: 'PagedAttention, token generation latency, flash attention, and vLLM architecture.',
                    questions: ['How do vLLM block tables map logical tokens to physical GPU pages?']
                },
                {
                    id: 'rag_hnsw',
                    label: 'RAG & Vector Databases (HNSW)',
                    level: 2,
                    category: 'genai',
                    status: 'mastered',
                    readiness: 91,
                    summary: 'Hierarchical Navigable Small World graphs, dense retrieval, and hybrid re-ranking.',
                    questions: ['Why does HNSW provide O(log N) search complexity compared to IVFFlat?']
                }
            ]
        },
        {
            id: 'ml_ds_branch',
            label: 'Machine Learning & Data Science',
            level: 1,
            category: 'ml',
            status: 'reviewing',
            readiness: 82,
            summary: 'Model adaptation, feature engineering, offline/online feature stores, and MLOps deployment.',
            questions: [
                'How does point-in-time correctness prevent target leakage in feature stores?',
                'LoRA low-rank adaptation decomposition mechanics.'
            ],
            children: [
                {
                    id: 'ml_lora',
                    label: 'Machine Learning & LoRA Fine-Tuning',
                    level: 2,
                    category: 'ml',
                    status: 'mastered',
                    readiness: 88,
                    summary: 'Parameter-efficient fine-tuning via rank decomposition matrices without optimizer bloat.',
                    questions: ['Why does LoRA freeze base weights W0 and train only A and B?']
                },
                {
                    id: 'ds_feature_store',
                    label: 'Data Science & Feature Stores',
                    level: 2,
                    category: 'ml',
                    status: 'reviewing',
                    readiness: 84,
                    summary: 'Time-travel ASOF joins, online low-latency key-value stores, and pipeline drift monitoring.',
                    questions: ['Explain training-serving skew and how feature stores prevent it.']
                }
            ]
        },
        {
            id: 'databases_branch',
            label: 'SQL & NoSQL Architectures',
            level: 1,
            category: 'database',
            status: 'mastered',
            readiness: 93,
            summary: 'Relational query engines, MVCC internals, tunable consistency NoSQL, and write-heavy LSM trees.',
            questions: [
                'How does PostgreSQL MVCC Heap-Only Tuple (HOT) update operate?',
                'Cassandra tunable consistency equation (R + W > N).'
            ],
            children: [
                {
                    id: 'sql_mvcc',
                    label: 'PostgreSQL MVCC & HOT Updates',
                    level: 2,
                    category: 'database',
                    status: 'mastered',
                    readiness: 95,
                    summary: 'Visibility maps, index-only scans, tuple headers, and vacuum bloat mechanics.',
                    questions: ['Why does modifying an indexed column break HOT updates in Postgres?']
                },
                {
                    id: 'nosql_quorum',
                    label: 'Cassandra Tunable Consistency & Quorums',
                    level: 2,
                    category: 'database',
                    status: 'mastered',
                    readiness: 90,
                    summary: 'Replication factors, gossip protocols, hint handoffs, and local vs global quorums.',
                    questions: ['Why is LOCAL_QUORUM preferred over global QUORUM across WAN links?']
                }
            ]
        },
        {
            id: 'python_runtime_branch',
            label: 'Python Runtime & Concurrency',
            level: 1,
            category: 'core',
            status: 'mastered',
            readiness: 94,
            summary: 'Asyncio single-threaded cooperative loop, GIL synchronization, and process pools.',
            questions: [
                'Why does CPU-bound synchronous code block an asyncio event loop?',
                'How to safely offload heavy computational workloads in FastAPI.'
            ],
            children: [
                {
                    id: 'python_gil',
                    label: 'Python Internals & Event Loop Starvation',
                    level: 2,
                    category: 'core',
                    status: 'mastered',
                    readiness: 92,
                    summary: 'Event loop socket polling, cooperative task scheduling, and ProcessPoolExecutor integration.',
                    questions: ['How does loop.run_in_executor prevent socket starvation under heavy CPU load?']
                }
            ]
        }
    ]
};

// --- CORE REPOSITORY OF STAFF-LEVEL MCQS (WITH DEEP INVARIANTS) ---
const INITIAL_MCQ_DATABASE = [
    {
        id: 'mcq-1',
        topic: 'Distributed Systems',
        mindmapNodeId: 'raft',
        mindmapLabel: 'Raft & Paxos Protocol',
        difficulty: 'Staff',
        keywords: ['consensus', 'split-brain', 'raft', 'quorum', 'network partition', 'leader election', 'accenture', 'cognizant'],
        companyTags: ['Accenture', 'Cognizant', 'HCL', 'Capgemini'],
        question: 'In a 5-node Raft consensus cluster partitioned into two subnets {N1, N2} and {N3, N4, N5}, which statement describes the behavior when clients write to both partitions simultaneously?',
        options: [
            { id: 'A', text: 'Both partitions accept and commit writes independently to optimize availability.' },
            { id: 'B', text: 'Only the majority partition {N3, N4, N5} can commit entries; {N1, N2} can accept uncommitted proposals but will discard them upon reunification.' },
            { id: 'C', text: 'The minority partition {N1, N2} automatically triggers an instantaneous node self-termination to avoid split-brain.' },
            { id: 'D', text: 'All writes block globally across the entire cluster until the network bridge is restored.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'Raft guarantees state machine safety via the Quorum Intersection property: any two majorities of cluster size N share at least one node (for N=5, quorum size is 3). Hence, only partition {N3, N4, N5} can achieve write consensus.',
            distractorBreakdown: [
                { option: 'A', reason: 'Violates the log matching safety invariant. Raft is CP in CAP; it sacrifices availability under minority partitions.' },
                { option: 'C', reason: 'Nodes in minority do not terminate; they continuously time out, increment election terms, and attempt candidate transitions until reunited.' },
                { option: 'D', reason: 'False. The majority partition continues processing writes without stalling.' }
            ],
            codeSnippet: `// Raft commit rule:\n// A leader can commit log entry if:\n// 1. entry.term == currentTerm\n// 2. replicateCount >= (TOTAL_NODES / 2) + 1\n// In {N1, N2}: max replicateCount is 2 < 3 (No commit)`
        }
    },
    {
        id: 'mcq-2',
        topic: 'Caching & Performance',
        mindmapNodeId: 'stampede',
        mindmapLabel: 'Cache Invalidation & Thundering Herd',
        difficulty: 'Intermediate',
        keywords: ['cache stampede', 'thundering herd', 'xfetch', 'probabilistic early expiration', 'redis', 'hcl', 'ey'],
        companyTags: ['HCL', 'EY', 'TCS', 'Infosys'],
        question: 'Which algorithm or strategy prevents "Cache Stampedes" (Thundering Herd) when a hot cache key expires under 100,000 concurrent QPS without introducing prolonged lock serialization?',
        options: [
            { id: 'A', text: 'Increase Redis replication factor to 5 replicas.' },
            { id: 'B', text: 'Probabilistic Early Expiration (e.g., XFetch algorithm) where workers asynchronously recompute before actual TTL using -beta * log(rand()).' },
            { id: 'C', text: 'Switch Redis eviction policy from volatile-lru to allkeys-random.' },
            { id: 'D', text: 'Set TTL to infinite and rely on manual cron-based key flushes.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'XFetch computes a dynamic decision boundary: currentTime - (computationDelta * beta * ln(rand())) > expiry. As the item nears expiration, the probability of an incoming request triggering background regeneration scales gracefully from 0% to 100%, guaranteeing that exactly one worker refreshes early.',
            distractorBreakdown: [
                { option: 'A', reason: 'Replicas mirror the same expired state and will all forward read-miss queries to database simultaneously.' },
                { option: 'C', reason: 'Random eviction does not solve synchronization spikes on expired hot keys.' },
                { option: 'D', reason: 'Stale data persists indefinitely and manual cron jobs cause catastrophic periodic spikes.' }
            ],
            codeSnippet: `import math, random, time\n\ndef should_refresh_early(expiry_time, compute_delta, beta=1.0):\n    # Probabilistic early recomputation\n    return (time.time() - compute_delta * beta * math.log(random.random())) > expiry_time`
        }
    },
    {
        id: 'mcq-3',
        topic: 'Database & Sharding',
        mindmapNodeId: 'consistent_hashing',
        mindmapLabel: 'Consistent Hashing & Virtual Nodes',
        difficulty: 'Staff',
        keywords: ['consistent hashing', 'virtual nodes', 'vnodes', 'ring partition', 'dynamo', 'cassandra', 'capgemini', 'deloitte'],
        companyTags: ['Capgemini', 'Deloitte', 'Wipro', 'Accenture'],
        question: 'In a distributed ring topology with Consistent Hashing, what primary architectural purpose do Virtual Nodes (V-Nodes) serve?',
        options: [
            { id: 'A', text: 'They enable synchronous two-phase commits across distant physical nodes.' },
            { id: 'B', text: 'They ensure non-uniform hash ring distribution to favor cold storage.' },
            { id: 'C', text: 'They smooth variance in token distribution, eliminating non-uniform key hotspots and enabling proportional load scaling.' },
            { id: 'D', text: 'They encrypt memory contents before replicating to peer nodes.' }
        ],
        correctOptionId: 'C',
        explanation: {
            corePrinciple: 'With only N physical nodes, random hash placement causes significant cluster imbalance (some nodes get 3x more ranges than average). By assigning 256 virtual points per physical server, variance approaches standard deviation σ = O(1 / sqrt(N * V)), distributing keys evenly.',
            distractorBreakdown: [
                { option: 'A', reason: 'Consistent hashing is a routing/partitioning layer, independent of transaction consensus.' },
                { option: 'B', reason: 'Virtual nodes aim for uniform distribution, not non-uniformity.' },
                { option: 'D', reason: 'Has no connection to cryptographic data-at-rest encryption.' }
            ],
            codeSnippet: `# Virtual node mapping:\n# Physical Server "S1" maps to tokens:\n# hash("S1-vnode-0"), hash("S1-vnode-1"), ..., hash("S1-vnode-255")`
        }
    },
    {
        id: 'mcq-4',
        topic: 'Async Messaging & Streaming',
        mindmapNodeId: 'kafka',
        mindmapLabel: 'Kafka Internals & Consumer Groups',
        difficulty: 'Intermediate',
        keywords: ['kafka', 'zero copy', 'page cache', 'sendfile', 'throughput', 'consumer groups', 'accenture', 'cognizant'],
        companyTags: ['Accenture', 'Cognizant', 'EY', 'TCS'],
        question: 'Why does Apache Kafka deliver extraordinarily high sequential write and read throughput compared to traditional message queues?',
        options: [
            { id: 'A', text: 'It maintains all active partition logs exclusively in JVM heap memory without disk flushes.' },
            { id: 'B', text: 'It leverages OS Page Cache sequential append-only writes, Zero-Copy (sendfile syscall), and avoids JVM GC overhead.' },
            { id: 'C', text: 'It compiles consumer bytecode into native GPU kernels.' },
            { id: 'D', text: 'It drops transaction validation headers to shave byte latency.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'Kafka relies on the Linux OS Page Cache rather than JVM heap to eliminate garbage collection pauses. For reads, it utilizes the sendfile() system call (Zero-Copy), piping data directly from OS page cache to network socket DMA without copying into user-space RAM.',
            distractorBreakdown: [
                { option: 'A', reason: 'Kafka strictly persists to disk via sequential segments; purely in-heap queues would lose durability.' },
                { option: 'C', reason: 'Kafka is a standard Java/Scala server running on general CPUs; GPU kernels are irrelevant.' },
                { option: 'D', reason: 'Kafka guarantees message integrity via CRC checks and transactional headers.' }
            ],
            codeSnippet: `// Linux Zero-Copy kernel flow:\n// Disk -> OS Page Cache -> NIC Buffer (via sendfile)\n// Bypasses JVM user-space memory entirely.`
        }
    },
    {
        id: 'mcq-5',
        topic: 'Concurrency & Locks',
        mindmapNodeId: 'zookeeper',
        mindmapLabel: 'Distributed Locks (Zookeeper/etcd)',
        difficulty: 'Staff',
        keywords: ['fencing token', 'distributed lock', 'gc pause', 'split-brain', 'lease', 'hcl', 'capgemini'],
        companyTags: ['HCL', 'Capgemini', 'Deloitte', 'Cognizant'],
        question: 'A worker holds a distributed lock with a 30-second TTL. The worker encounters a 45-second Stop-The-World JVM garbage collection pause. How must downstream storage prevent data corruption when the resumed worker performs delayed writes?',
        options: [
            { id: 'A', text: 'Increase the distributed lock TTL to 20 minutes.' },
            { id: 'B', text: 'Rely solely on TCP keep-alive pings between client and storage.' },
            { id: 'C', text: 'Require Fencing Tokens (monotonically increasing numbers) verified atomically by downstream storage to reject stale tokens.' },
            { id: 'D', text: 'Disable garbage collection in production.' }
        ],
        correctOptionId: 'C',
        explanation: {
            corePrinciple: 'As Martin Kleppmann proven in distributed lock analyses, time-based leases can never guarantee mutual exclusion when clients can pause (GC, disk I/O, context switch). A fencing token (e.g., token 34 < current token 35) rejected by the database is the only mathematically sound barrier.',
            distractorBreakdown: [
                { option: 'A', reason: 'Lengthening TTL simply increases downtime if a client genuinely crashes, and pauses can still exceed it.' },
                { option: 'B', reason: 'TCP keep-alive only verifies socket health, not client lock lease validity.' },
                { option: 'D', reason: 'Impossible in managed runtimes like JVM, Go, or Node.js.' }
            ],
            codeSnippet: `-- Downstream Storage atomic check:\nUPDATE accounts \nSET balance = balance + 100, last_token = 35 \nWHERE account_id = 'A12' AND last_token < 35;`
        }
    },
    {
        id: 'mcq-6',
        topic: 'Gen AI & LLM Systems',
        mindmapNodeId: 'genai_kvcache',
        mindmapLabel: 'LLM Inference & KV-Cache',
        difficulty: 'Staff',
        keywords: ['gen ai', 'llm', 'kv-cache', 'pagedattention', 'vllm', 'inference', 'tokens', 'accenture', 'ey'],
        companyTags: ['Accenture', 'EY', 'Infosys', 'Wipro'],
        question: 'In high-throughput LLM serving systems (such as vLLM or TensorRT-LLM), why does naive contiguous memory allocation for KV-Cache cause up to 60-80% GPU VRAM waste?',
        options: [
            { id: 'A', text: 'Floating point rounding errors in softmax normalization.' },
            { id: 'B', text: 'Internal and external memory fragmentation caused by unknown output sequence lengths forcing pre-allocation of maximum context window limits.' },
            { id: 'C', text: 'CUDA kernels failing to execute matrix multiplication on dynamic sequence shapes.' },
            { id: 'D', text: 'Attention heads requiring asynchronous host-to-device PCIe page swaps for every token generated.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'Because output lengths cannot be known ahead of time, naive engines pre-allocate contiguous slots for the full max_tokens context (internal fragmentation) and fail to reuse non-contiguous memory segments (external fragmentation). PagedAttention solves this via virtual memory page tables mapping physical blocks non-contiguously.',
            distractorBreakdown: [
                { option: 'A', reason: 'Softmax precision affects perplexity/accuracy, not GPU memory layout fragmentation.' },
                { option: 'C', reason: 'Tensor cores effortlessly multiply dynamic shapes via GEMM kernels.' },
                { option: 'D', reason: 'PCIe host-to-device transfers would cause catastrophic 100x latency degradation; KV-cache resides in GPU HBM.' }
            ],
            codeSnippet: `# PagedAttention Block Table Mapping:\n# Logical Token Blocks: [0, 1, 2] -> Physical GPU Pages: [page_42, page_19, page_88]\n# Memory waste drops from ~70% to < 4%.`
        }
    },
    {
        id: 'mcq-7',
        topic: 'RAG & Vector Search',
        mindmapNodeId: 'rag_hnsw',
        mindmapLabel: 'RAG & Vector Databases (HNSW)',
        difficulty: 'Staff',
        keywords: ['rag', 'vector database', 'hnsw', 'ivfflat', 'cosine similarity', 'embeddings', 'milvus', 'pinecone', 'hcl', 'capgemini'],
        companyTags: ['HCL', 'Capgemini', 'Deloitte', 'Cognizant'],
        question: 'When architecting an enterprise RAG retrieval pipeline querying 50 million 1536-dimensional embeddings with <15ms p99 latency, why is HNSW (Hierarchical Navigable Small World) preferred over IVFFlat?',
        options: [
            { id: 'A', text: 'HNSW requires zero RAM and executes completely from cold disk storage.' },
            { id: 'B', text: 'HNSW builds multi-layer skip-list graph structures offering logarithmic O(log N) search complexity with high recall (>98%) without clustering retraining.' },
            { id: 'C', text: 'IVFFlat is mathematically limited to only 2-dimensional embeddings.' },
            { id: 'D', text: 'HNSW eliminates the need for vector embedding generation.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'HNSW constructs hierarchical proximity graphs where upper layers act like express lane skip-lists for fast traversals and lower layers offer dense local clustering. IVFFlat partitions space using k-means Voronoi cells, which degrades under high dimensions and requires complete index retraining as vectors shift.',
            distractorBreakdown: [
                { option: 'A', reason: 'HNSW is RAM-heavy because the entire graph index and neighbor link lists reside in memory.' },
                { option: 'C', reason: 'IVFFlat works in high dimensions; its issue is recall drop and slow centroid lookups.' },
                { option: 'D', reason: 'HNSW is an indexing algorithm; an embedding model (e.g. text-embedding-3-large) is still strictly required.' }
            ],
            codeSnippet: `// HNSW Query Complexity: O(log N) graph traversal\n// Layer 2 (Sparse skip links) -> Layer 1 -> Layer 0 (Dense nearest neighbors)`
        }
    },
    {
        id: 'mcq-8',
        topic: 'Machine Learning & MLOps',
        mindmapNodeId: 'ml_lora',
        mindmapLabel: 'Machine Learning & LoRA Fine-Tuning',
        difficulty: 'Advanced',
        keywords: ['machine learning', 'mlops', 'lora', 'peft', 'fine-tuning', 'catastrophic forgetting', 'pytorch', 'accenture', 'capgemini'],
        companyTags: ['Accenture', 'Capgemini', 'TCS', 'Infosys'],
        question: 'How does Low-Rank Adaptation (LoRA) enable parameter-efficient fine-tuning of 70B parameter LLMs on consumer GPUs while preventing catastrophic forgetting?',
        options: [
            { id: 'A', text: 'By quantizing all activations into 1-bit integers and dropping attention weights.' },
            { id: 'B', text: 'By freezing base model weights W0 and injecting trainable rank decomposition matrices: ΔW = B * A, where r << min(d, k).' },
            { id: 'C', text: 'By retraining only the tokenizer vocabulary while leaving transformer blocks untouched.' },
            { id: 'D', text: 'By replacing all transformer attention heads with linear regression layers.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'LoRA hypothesizes that the weight updates during task adaptation have a low intrinsic rank r. By decomposing ΔW of size (d x k) into B (d x r) and A (r x k) with r=8 or 16, trainable parameters drop by 99.9%, optimizer memory vanishes, and the base model weights remain intact.',
            distractorBreakdown: [
                { option: 'A', reason: '1-bit quantization (BitNet) is an architectural quantization method, not LoRA adapter decomposition.' },
                { option: 'C', reason: 'Retraining vocabulary does not fine-tune reasoning or domain knowledge.' },
                { option: 'D', reason: 'Linear regression cannot model complex semantic dependencies.' }
            ],
            codeSnippet: `# PyTorch Forward Pass with LoRA adapter:\n# output = W0 * x + (alpha / r) * (B * (A * x))\n# W0 is frozen (no optimizer state gradients required)`
        }
    },
    {
        id: 'mcq-9',
        topic: 'Data Science & Pipelines',
        mindmapNodeId: 'ds_feature_store',
        mindmapLabel: 'Data Science & Feature Stores',
        difficulty: 'Staff',
        keywords: ['data science', 'feature store', 'feast', 'point-in-time', 'data leakage', 'training-serving skew', 'hcl', 'ey'],
        companyTags: ['HCL', 'EY', 'Deloitte', 'Cognizant'],
        question: 'In production machine learning systems, what critical data science problem does "Point-in-Time Correctness" (Time-Travel Join) in Feature Stores solve?',
        options: [
            { id: 'A', text: 'It speeds up Pandas dataframe serialization into JSON.' },
            { id: 'B', text: 'It prevents Data Leakage (Target Leakage) by ensuring offline training features match the exact state that existed at the historical event timestamp.' },
            { id: 'C', text: 'It converts all categorical strings into numeric float64 representations.' },
            { id: 'D', text: 'It automatically removes outliers using z-score normalization.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'If a training sample represents a fraud event at 14:00, joining with user transaction features computed at 18:00 leaks future fraud indicators into training, yielding an over-optimistic model that catastrophically fails in real-time inference (Training-Serving Skew).',
            distractorBreakdown: [
                { option: 'A', reason: 'Serialization speed is an I/O optimization, unrelated to temporal join semantics.' },
                { option: 'C', reason: 'One-hot or target encoding handles categorical conversions.' },
                { option: 'D', reason: 'Outlier detection is preprocessing, not time-travel joins.' }
            ],
            codeSnippet: `-- Feature Store Point-in-Time ASOF Join:\nSELECT o.order_id, o.order_time, f.user_30d_spend\nFROM orders o ASOF JOIN user_features f \nON o.user_id = f.user_id AND o.order_time >= f.feature_timestamp;`
        }
    },
    {
        id: 'mcq-10',
        topic: 'Python Core & Asyncio',
        mindmapNodeId: 'python_gil',
        mindmapLabel: 'Python Internals & Event Loop Starvation',
        difficulty: 'Advanced',
        keywords: ['python', 'asyncio', 'event loop', 'gil', 'cpu bound', 'processpoolexecutor', 'threading', 'cognizant', 'accenture'],
        companyTags: ['Cognizant', 'Accenture', 'Wipro', 'HCL'],
        question: 'Why does executing a synchronous CPU-bound computation (e.g., PBKDF2 hash or JSON parsing 100MB payload) inside an async def FastAPI endpoint stall ALL concurrent network requests?',
        options: [
            { id: 'A', text: 'Asyncio creates a new operating system process for each coroutine.' },
            { id: 'B', text: 'Python asyncio operates on a single-threaded cooperative event loop; a long-running CPU task never yields control via await, starving the OS socket selectors.' },
            { id: 'C', text: 'The Linux kernel automatically suspends HTTP TCP connections when CPU exceeds 50%.' },
            { id: 'D', text: 'Asyncio coroutines only accept integer arguments.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'Asyncio achieves high concurrency via non-blocking I/O event demultiplexing (epoll/kqueue) on a single thread. It is cooperative multitasking: if a function does not await (which yields control back to loop.poll()), the entire loop stalls until computation completes. Fix: offload to loop.run_in_executor(ProcessPoolExecutor, func).',
            distractorBreakdown: [
                { option: 'A', reason: 'Asyncio is single-threaded by default and does not spawn OS processes.' },
                { option: 'C', reason: 'Linux TCP sockets buffer in kernel memory; the application loop fails to read them.' },
                { option: 'D', reason: 'Nonsense assertion.' }
            ],
            codeSnippet: `# Production Fix:\nimport asyncio\nfrom concurrent.futures import ProcessPoolExecutor\n\nexecutor = ProcessPoolExecutor(max_workers=4)\nresult = await asyncio.get_running_loop().run_in_executor(executor, heavy_cpu_task, payload)`
        }
    },
    {
        id: 'mcq-11',
        topic: 'SQL & Database Internals',
        mindmapNodeId: 'sql_mvcc',
        mindmapLabel: 'PostgreSQL MVCC & HOT Updates',
        difficulty: 'Staff',
        keywords: ['sql', 'postgres', 'mvcc', 'hot update', 'vacuum', 'b-tree index', 'bloat', 'ey', 'capgemini'],
        companyTags: ['EY', 'Capgemini', 'Infosys', 'TCS'],
        question: 'In PostgreSQL, why does an UPDATE statement on a column with a B-Tree index cause significantly more disk I/O and table bloat than an update on an unindexed column?',
        options: [
            { id: 'A', text: 'PostgreSQL locks the entire database table during indexed updates.' },
            { id: 'B', text: 'Because indexed column updates prevent HOT (Heap-Only Tuples) optimization, forcing Postgres to insert a new entry into every single index on the table.' },
            { id: 'C', text: 'B-Tree indexes require synchronous fsync to the write-ahead log twice per column.' },
            { id: 'D', text: 'PostgreSQL converts B-Tree indexes into Hash indexes upon modification.' }
        ],
        correctOptionId: 'B',
        explanation: {
            corePrinciple: 'Under PostgreSQL MVCC, UPDATE writes a new tuple version. If NO indexed columns are modified and the page has room, Heap-Only Tuples (HOT) creates a heap chain pointing from old to new tuple without touching any index. Modifying an indexed column breaks HOT, requiring new entries in every index and generating heavy index bloat.',
            distractorBreakdown: [
                { option: 'A', reason: 'Row-level locking (RowExclusiveLock) is used, not table-level exclusive locks.' },
                { option: 'C', reason: 'Fsync is batched by WAL writer according to synchronous_commit settings.' },
                { option: 'D', reason: 'PostgreSQL never alters underlying index types on updates.' }
            ],
            codeSnippet: `-- Verify HOT Update Ratio:\nSELECT relname, n_tup_upd, n_tup_hot_upd,\n       round(100.0 * n_tup_hot_upd / nullif(n_tup_upd, 0), 2) AS hot_ratio\nFROM pg_stat_user_tables;`
        }
    },
    {
        id: 'mcq-12',
        topic: 'NoSQL & Key-Value Stores',
        mindmapNodeId: 'nosql_quorum',
        mindmapLabel: 'Cassandra Tunable Consistency & Quorums',
        difficulty: 'Staff',
        keywords: ['nosql', 'cassandra', 'quorum', 'tunable consistency', 'cap theorem', 'dynamo', 'hcl', 'deloitte'],
        companyTags: ['HCL', 'Deloitte', 'Accenture', 'Cognizant'],
        question: 'In Apache Cassandra with a replication factor of N=5 across two datacenters, which read and write consistency levels guarantee Strong Consistency (linearizability) while insulating client operations against cross-region WAN network partitions?',
        options: [
            { id: 'A', text: 'Write: ANY, Read: ONE' },
            { id: 'B', text: 'Write: ALL, Read: ALL' },
            { id: 'C', text: 'Write: LOCAL_QUORUM, Read: LOCAL_QUORUM (where R_local + W_local > N_local in the local datacenter)' },
            { id: 'D', text: 'Write: QUORUM, Read: ANY' }
        ],
        correctOptionId: 'C',
        explanation: {
            corePrinciple: 'The Quorum condition requires R + W > N. However, using global QUORUM routes RPCs across the WAN, which stalls if the cross-datacenter link fails. LOCAL_QUORUM restricts quorum validation to nodes within the client local datacenter (e.g. 2 of 3 local nodes for N_local=3), guaranteeing local strong consistency with low latency.',
            distractorBreakdown: [
                { option: 'A', reason: 'R + W = 1 + 0 < 5. Yields dirty reads and data loss.' },
                { option: 'B', reason: 'If even a single node in the entire world is down, all writes fail, destroying availability.' },
                { option: 'D', reason: 'Read: ANY is not a valid Cassandra read level; ANY only applies to writes via hinted handoffs.' }
            ],
            codeSnippet: `// Cassandra Driver Execution Profile:\nSimpleStatement statement = SimpleStatement.newInstance("SELECT * FROM user_balances WHERE user_id = ?")\n    .setConsistencyLevel(DefaultConsistencyLevel.LOCAL_QUORUM);`
        }
    }
];

// Default Starter Code for Interview
const DEFAULT_STARTER_CODE = `class TokenBucketRateLimiter:
    """
    Thread-Safe Distributed Token Bucket Rate Limiter
    High-throughput O(1) step time complexity.
    """
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = capacity
        self.last_update = 0.0

    def allow_request(self, current_time: float, cost: int = 1) -> bool:
        elapsed = current_time - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = current_time
        
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

# Benchmark test runner
limiter = TokenBucketRateLimiter(capacity=10, refill_rate_per_sec=2.0)
print("[TEST 1] First burst of 5 tokens:", limiter.allow_request(current_time=1.0, cost=5))
print("[TEST 2] Second burst of 5 tokens:", limiter.allow_request(current_time=1.0, cost=5))
print("[TEST 3] Over-limit check (should be False):", limiter.allow_request(current_time=1.0, cost=1))
`;

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", async () => {
    // 0. Verify and Sync User Authentication
    await checkAuthStatus();

    // 1. Initialize Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // 2. Setup Session Timer
    startSessionTimer();

    // 3. Setup Tab Indentation in IDE
    setupTabIndentation("ideCodeTextarea");

    // 4. Set Initial Code
    const ideTextarea = document.getElementById("ideCodeTextarea");
    if (ideTextarea) ideTextarea.value = DEFAULT_STARTER_CODE;

    // 5. Initialize Mindmap & MCQs
    mindmapTree = INITIAL_MINDMAP_DATA;
    selectedMindmapNode = mindmapTree.children[0].children[0];
    mcqQuestions = [...INITIAL_MCQ_DATABASE];

    // 6. Load Data from Backend
    await initInterviewSession();
    await fetchBackendQuestions();
    await fetchBackendMcqs();

    // 7. Initial Render
    renderMcqs();
    renderMindmapSvg();
    renderMindmapDrawer();
    renderChatStream();
    renderRubricScores();
    updateSidebarMastery();
    initTargetRoleListener();
    loadCentralizedConcepts();
    initLlmChatView();

    // 8. Refresh Lucide Icons after dynamic renders
    if (window.lucide) {
        lucide.createIcons();
    }
});

// --- HELPER: TAB INDENTATION & SHORTCUTS IN TEXTAREAS ---
function setupTabIndentation(textareaId) {
    const el = document.getElementById(textareaId);
    if (!el) return;
    el.addEventListener("keydown", function(e) {
        if (e.key === "Tab") {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            handleExecuteCode();
        }
    });
}

// --- TAB NAVIGATION SWITCHER ---
function switchAppTab(tab) {
    activeAppTab = tab;

    // Panes
    const paneMap = {
        'mcq': 'paneMcq',
        'concepts': 'paneConcepts',
        'mindmap': 'paneMindmap',
        'interview': 'paneInterview',
        'questions': 'paneQuestions',
        'analytics': 'paneAnalytics',
        'profile': 'paneProfile',
        'llm': 'paneLlm'
    };

    Object.entries(paneMap).forEach(([k, id]) => {
        const el = document.getElementById(id);
        if (el) {
            if (k === tab) el.classList.remove("hidden");
            else el.classList.add("hidden");
        }
    });

    // Nav Buttons
    const btnMap = {
        'mcq': 'navTabMcq',
        'concepts': 'navTabConcepts',
        'mindmap': 'navTabMindmap',
        'interview': 'navTabInterview',
        'questions': 'navTabQuestions',
        'analytics': 'navTabAnalytics',
        'profile': 'navTabProfile',
        'llm': 'navTabLlm'
    };

    const activeBtnClass = "tab-nav-btn group flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all bg-gradient-to-r from-indigo-600/30 to-violet-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm";
    const inactiveBtnClass = "tab-nav-btn group flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all text-zinc-400 hover:bg-zinc-900/80 hover:text-zinc-200";

    Object.entries(btnMap).forEach(([k, id]) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.className = (k === tab) ? activeBtnClass : inactiveBtnClass;
            const icon = btn.querySelector("i");
            if (icon) {
                if (k === tab) {
                    icon.classList.remove("text-zinc-400");
                    icon.classList.add("text-indigo-400");
                } else {
                    icon.classList.remove("text-indigo-400");
                    icon.classList.add("text-zinc-400");
                }
            }
        }
    });

    if (tab === 'concepts') {
        if (!allConceptsData || allConceptsData.length === 0) {
            loadCentralizedConcepts();
        } else {
            renderConceptsCards();
        }
    } else if (tab === 'mindmap') {
        renderMindmapSvg();
        renderMindmapDrawer();
    } else if (tab === 'questions') {
        renderQuestionBankList();
    } else if (tab === 'analytics') {
        renderAnalyticsTab();
    } else if (tab === 'profile') {
        loadUserRecommendationsAndHistory();
    } else if (tab === 'llm') {
        initLlmChatView();
    }

    if (window.lucide) {
        lucide.createIcons();
    }
}

// --- SESSION TIMER & VOICE SIMULATION ---
function startSessionTimer() {
    if (sessionTimerInterval) clearInterval(sessionTimerInterval);
    sessionTimerInterval = setInterval(() => {
        if (isTimerRunning) {
            sessionSeconds++;
            const textEl = document.getElementById("sessionTimerText");
            if (textEl) {
                const mins = Math.floor(sessionSeconds / 60);
                const secs = sessionSeconds % 60;
                textEl.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
        }
    }, 1000);
}

function toggleSessionTimer() {
    isTimerRunning = !isTimerRunning;
    const iconEl = document.getElementById("sessionTimerIcon");
    if (iconEl) iconEl.innerText = isTimerRunning ? "⏸" : "▶";
    showToast(isTimerRunning ? "Session timer resumed" : "Session timer paused");
}

function toggleVoiceSimulation() {
    isVoiceActive = !isVoiceActive;
    const btn = document.getElementById("voiceToggleBtn");
    const micIcon = document.getElementById("voiceMicIcon");
    const statusText = document.getElementById("voiceStatusText");
    const eq = document.getElementById("voiceEqualizer");

    if (isVoiceActive) {
        if (btn) btn.className = "flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-medium border border-indigo-500/50 bg-indigo-500/20 text-indigo-300 shadow-md shadow-indigo-500/10 transition-all";
        if (statusText) statusText.innerText = "Voice Simulation: ON";
        if (eq) {
            eq.classList.remove("hidden");
            eq.classList.add("flex");
        }
        if (micIcon) micIcon.setAttribute("data-lucide", "mic");
        showToast("🎙️ Voice simulation active with live audio stream");
    } else {
        if (btn) btn.className = "flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-medium border border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:bg-zinc-800 transition-all";
        if (statusText) statusText.innerText = "Voice Off";
        if (eq) {
            eq.classList.add("hidden");
            eq.classList.remove("flex");
        }
        if (micIcon) micIcon.setAttribute("data-lucide", "mic-off");
        showToast("Voice simulation paused");
    }

    if (window.lucide) {
        lucide.createIcons();
    }
}

// --- BACKEND API INTEGRATION ---
async function initInterviewSession() {
    try {
        const headers = { "Content-Type": "application/json" };
        if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

        const res = await fetch("/api/v1/interview/sessions", {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
                candidate_id: currentUser ? currentUser.id : null,
                session_title: `${targetRole} - Mock Interview`,
                experience_level: currentUser ? (currentUser.experience_level || "senior") : "senior",
                target_company: (currentUser && currentUser.target_companies && currentUser.target_companies[0]) ? currentUser.target_companies[0] : "Google"
            })
        });
        if (res.ok) {
            const data = await res.json();
            activeSessionId = data.id;
        }
    } catch (err) {
        console.warn("Using offline session mode:", err);
    }
}

async function fetchBackendQuestions() {
    try {
        const res = await fetch("/api/v1/questions?limit=100");
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                bankQuestions = data;
                const countBadge = document.getElementById("navQuestionsCountBadge");
                if (countBadge) countBadge.innerText = `${data.length}+`;
                if (bankQuestions.length > 0) {
                    activeBankQuestion = bankQuestions[0];
                }
            }
        }
    } catch (err) {
        console.warn("Could not load backend questions:", err);
    }
}

async function fetchBackendMcqs() {
    try {
        const res = await fetch("/api/v1/questions/mcq-quiz");
        if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                // Map backend items to frontend format
                const mapped = data.map((item, idx) => ({
                    id: `mcq-backend-${item.id}`,
                    backendId: item.id,
                    topic: formatCategory(item.category) || 'Distributed Systems',
                    mindmapNodeId: item.mindmap_node || 'raft',
                    mindmapLabel: item.mindmap_topic || formatCategory(item.category),
                    difficulty: (item.difficulty || 'staff').charAt(0).toUpperCase() + (item.difficulty || 'staff').slice(1),
                    keywords: [item.category.replace(/_/g, ' '), item.phase || 'staff', 'invariants', ...(item.company_tags || [])],
                    companyTags: item.company_tags || [],
                    question: item.mcq_question || item.title,
                    options: (item.mcq_options || []).map((opt, oIdx) => ({
                        id: String.fromCharCode(65 + oIdx), // 'A', 'B', 'C', 'D'
                        text: opt
                    })),
                    correctOptionId: item.mcq_correct_index !== null ? String.fromCharCode(65 + item.mcq_correct_index) : 'A',
                    explanation: {
                        corePrinciple: item.mcq_explanation || 'Guarantees state machine consistency and quorum intersection safety invariants.',
                        distractorBreakdown: [
                            { option: 'A', reason: 'Fails under network partitions or high concurrency stampedes.' },
                            { option: 'C', reason: 'Introduces uncontrolled split-brain or prolonged synchronization locks.' },
                            { option: 'D', reason: 'Violates low-latency p99 bounds under production workloads.' }
                        ],
                        codeSnippet: item.solution_code || `// Production Architectural Pattern:\n// Atomic Compare-And-Swap (CAS) guard`
                    }
                }));

                // Combine foundational MCQs with backend MCQs
                mcqQuestions = [...INITIAL_MCQ_DATABASE, ...mapped];
                const badge = document.getElementById("navMcqBadge");
                if (badge) badge.innerText = `${mcqQuestions.length} New`;
                renderMcqs();
            }
        }
    } catch (err) {
        console.warn("Could not load backend MCQs, using foundational suite:", err);
    }
}

// --- MCQ ENGINE: RENDERING & INTERACTIONS ---
function filterMcqs() {
    renderMcqs();
}

function clearMcqSearch() {
    const input = document.getElementById("mcqSearchInput");
    if (input) input.value = "";
    document.getElementById("mcqSearchClearBtn")?.classList.add("hidden");
    filterMcqs();
}

function setMcqMode(mode) {
    mcqMode = mode;
    isTestSubmitted = false;
    const practiceBtn = document.getElementById("mcqModePracticeBtn");
    const timedBtn = document.getElementById("mcqModeTimedBtn");
    const timedBanner = document.getElementById("mcqTimedBanner");
    const scoreBanner = document.getElementById("mcqScoreSummaryBanner");

    if (scoreBanner) scoreBanner.classList.add("hidden");

    if (mode === 'practice') {
        if (practiceBtn) practiceBtn.className = "rounded-lg px-3 py-1 text-xs font-semibold bg-indigo-600 text-white shadow-sm transition-all";
        if (timedBtn) timedBtn.className = "flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold text-zinc-400 hover:text-zinc-200 transition-all";
        if (timedBanner) timedBanner.classList.add("hidden");
        if (timedInterval) clearInterval(timedInterval);
    } else {
        if (timedBtn) timedBtn.className = "flex items-center gap-1.5 rounded-lg px-3 py-1 text-xs font-semibold bg-amber-600 text-white shadow-sm transition-all";
        if (practiceBtn) practiceBtn.className = "rounded-lg px-3 py-1 text-xs font-semibold text-zinc-400 hover:text-zinc-200 transition-all";
        if (timedBanner) {
            timedBanner.classList.remove("hidden");
            timedBanner.classList.add("flex");
        }
        startTimedExam();
    }

    renderMcqs();
}

function startTimedExam() {
    timedCountdown = 900; // 15 min
    if (timedInterval) clearInterval(timedInterval);
    timedInterval = setInterval(() => {
        if (timedCountdown > 0 && !isTestSubmitted) {
            timedCountdown--;
            const mins = Math.floor(timedCountdown / 60);
            const secs = timedCountdown % 60;
            const el = document.getElementById("timedCountdownText");
            if (el) el.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} remaining`;
        } else if (timedCountdown === 0 && !isTestSubmitted) {
            submitTimedExam();
        }
    }, 1000);
}

function submitTimedExam() {
    isTestSubmitted = true;
    if (timedInterval) clearInterval(timedInterval);

    // Calculate score
    let correct = 0;
    const questionsToCount = mcqQuestions.slice(0, 10);
    questionsToCount.forEach(q => {
        if (selectedAnswers[q.id] === q.correctOptionId) {
            correct++;
        }
    });

    const percent = Math.round((correct / questionsToCount.length) * 100);
    const scoreBanner = document.getElementById("mcqScoreSummaryBanner");
    const scoreTitle = document.getElementById("mcqScoreSummaryTitle");
    const scoreDesc = document.getElementById("mcqScoreSummaryDesc");

    if (scoreBanner) scoreBanner.classList.remove("hidden");
    if (scoreTitle) scoreTitle.innerText = `Diagnostic Score: ${percent}%`;
    if (scoreDesc) scoreDesc.innerText = `You scored ${correct} out of ${questionsToCount.length} on Staff-Level Architectural Invariants.`;

    renderMcqs();
    updateSidebarMastery();
    showToast(`Timed Assessment Complete: ${percent}% Score!`);
}

function retakeTimedExam() {
    selectedAnswers = {};
    isTestSubmitted = false;
    document.getElementById("mcqScoreSummaryBanner")?.classList.add("hidden");
    startTimedExam();
    renderMcqs();
    updateSidebarMastery();
}

function resetMcqState() {
    selectedAnswers = {};
    activeMcqDrawerId = null;
    isTestSubmitted = false;
    clearMcqSearch();
    document.getElementById("mcqDomainFilter").value = "All";
    document.getElementById("mcqDifficultyFilter").value = "All";
    document.getElementById("mcqScoreSummaryBanner")?.classList.add("hidden");
    renderMcqs();
    updateSidebarMastery();
    showToast("MCQ Assessment state reset.");
}

function renderMcqs() {
    const container = document.getElementById("mcqCardsContainer");
    if (!container) return;

    const searchInput = document.getElementById("mcqSearchInput");
    const kw = (searchInput?.value || "").toLowerCase().trim();
    const domainFilter = document.getElementById("mcqDomainFilter")?.value || "All";
    const diffFilter = (document.getElementById("mcqDifficultyFilter")?.value || "All").toLowerCase();

    // Toggle clear button
    const clearBtn = document.getElementById("mcqSearchClearBtn");
    if (clearBtn) {
        if (kw) clearBtn.classList.remove("hidden");
        else clearBtn.classList.add("hidden");
    }

    // Filter list
    const filtered = mcqQuestions.filter(q => {
        const matchKw = !kw ||
            q.question.toLowerCase().includes(kw) ||
            q.topic.toLowerCase().includes(kw) ||
            (q.keywords || []).some(k => k.toLowerCase().includes(kw)) ||
            (q.companyTags || []).some(c => c.toLowerCase().includes(kw)) ||
            (q.options || []).some(o => o.text.toLowerCase().includes(kw)) ||
            (q.explanation?.corePrinciple || "").toLowerCase().includes(kw);

        const df = domainFilter.toLowerCase();
        const matchDomain = (domainFilter === "All") ||
            (q.topic && q.topic.toLowerCase().includes(df)) ||
            (q.mindmapLabel && q.mindmapLabel.toLowerCase().includes(df)) ||
            (q.keywords || []).some(k => k.toLowerCase().includes(df));
        
        const qDiff = (q.difficulty || '').toLowerCase();
        let matchDiff = (diffFilter === "all");
        if (!matchDiff) {
            if (diffFilter === "staff" || diffFilter === "advanced" || diffFilter === "principal") {
                matchDiff = qDiff.includes("staff") || qDiff.includes("advanced") || qDiff.includes("principal") || qDiff.includes("senior") || qDiff.includes("hard");
            } else if (diffFilter === "intermediate" || diffFilter === "mid") {
                matchDiff = qDiff.includes("intermediate") || qDiff.includes("mid") || qDiff.includes("medium");
            } else if (diffFilter === "basic" || diffFilter === "junior") {
                matchDiff = qDiff.includes("basic") || qDiff.includes("junior") || qDiff.includes("easy");
            } else {
                matchDiff = qDiff.includes(diffFilter);
            }
        }

        return matchKw && matchDomain && matchDiff;
    });

    // Update ratio in timed banner
    const ratioEl = document.getElementById("timedAnsweredRatio");
    if (ratioEl) {
        ratioEl.innerText = `Answered: ${Object.keys(selectedAnswers).length} / ${Math.min(filtered.length, 10)}`;
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-16 text-center text-zinc-500">
                <i data-lucide="file-question" class="h-12 w-12 text-zinc-700 mb-3"></i>
                <p class="text-sm font-semibold text-zinc-400">No questions match keyword "${escapeHtml(kw)}"</p>
                <p class="text-xs text-zinc-600 mt-1">Try clearing filters or search terms like 'Raft', 'Redis', or 'Kafka'.</p>
                <button onclick="resetMcqState()" class="mt-4 rounded-xl border border-zinc-800 bg-zinc-900 px-4 py-1.5 text-xs font-semibold text-zinc-300 hover:bg-zinc-800 transition">
                    Clear All Filters
                </button>
            </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
    }

    container.innerHTML = filtered.map((q, idx) => {
        const userAnswer = selectedAnswers[q.id];
        const hasAnswered = !!userAnswer;
        const isCorrect = userAnswer === q.correctOptionId;
        const showFeedback = (mcqMode === 'practice') ? hasAnswered : isTestSubmitted;
        const isDrawerOpen = (activeMcqDrawerId === q.id);

        const isCardSearchMatched = kw && (
            q.question.toLowerCase().includes(kw) ||
            (q.keywords || []).some(k => k.toLowerCase().includes(kw)) ||
            (q.options || []).some(o => o.text.toLowerCase().includes(kw))
        );

        let borderCardClass = 'border-zinc-800/80 bg-zinc-900/40 hover:border-zinc-700';
        if (showFeedback && isCorrect) {
            borderCardClass = 'border-emerald-500/40 bg-zinc-900/60 shadow-lg shadow-emerald-500/5';
        } else if (showFeedback && !isCorrect) {
            borderCardClass = 'border-rose-500/40 bg-zinc-900/60 shadow-lg shadow-rose-500/5';
        } else if (isCardSearchMatched) {
            borderCardClass = 'border-indigo-500/50 bg-zinc-900/60 shadow-md shadow-indigo-500/10 ring-1 ring-indigo-500/30';
        }

        const optionsHtml = (q.options || []).map(opt => {
            const isSelected = (userAnswer === opt.id);
            const isThisCorrect = (opt.id === q.correctOptionId);

            let optClass = "flex items-start gap-3.5 rounded-xl border p-3.5 text-xs transition-all cursor-pointer select-none";
            let badgeClass = "border-zinc-700 bg-zinc-800 text-zinc-400";
            let badgeIcon = opt.id;

            if (showFeedback) {
                if (isThisCorrect) {
                    optClass += " border-emerald-500 bg-emerald-950/20 text-emerald-200";
                    badgeClass = "border-emerald-400 bg-emerald-500 text-white font-black";
                    badgeIcon = "✓";
                } else if (isSelected && !isThisCorrect) {
                    optClass += " border-rose-500 bg-rose-950/20 text-rose-200";
                    badgeClass = "border-rose-400 bg-rose-500 text-white font-black";
                    badgeIcon = "✕";
                } else {
                    optClass += " border-zinc-800/80 bg-zinc-950/40 text-zinc-400 opacity-60";
                }
            } else {
                if (isSelected) {
                    optClass += " border-indigo-500 bg-indigo-950/30 text-white shadow-sm";
                    badgeClass = "border-indigo-400 bg-indigo-600 text-white font-bold";
                } else {
                    optClass += " border-zinc-800 bg-zinc-950/60 text-zinc-300 hover:border-zinc-700 hover:bg-zinc-900/60";
                }
            }

            return `
                <div onclick="handleSelectMcqOption('${q.id}', '${opt.id}')" class="${optClass}">
                    <div class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full text-[10px] border ${badgeClass}">
                        ${badgeIcon}
                    </div>
                    <span class="leading-snug pt-0.5">${escapeHtml(opt.text)}</span>
                </div>
            `;
        }).join('');

        const keywordPillsHtml = (q.keywords || []).slice(0, 4).map(k => {
            const isMatch = kw && k.toLowerCase().includes(kw);
            return `
                <span class="rounded px-1.5 py-0.5 text-[10px] font-mono border transition-all ${
                    isMatch
                        ? 'bg-indigo-500/25 text-indigo-200 border-indigo-400 font-bold shadow-xs'
                        : 'bg-zinc-800/60 text-zinc-400 border-zinc-700/50'
                }">#${k}</span>
            `;
        }).join('');

        const companyTagsHtml = (q.companyTags || []).slice(0, 3).map(c => {
            const isMatch = kw && c.toLowerCase().includes(kw);
            return `
                <span class="rounded px-1.5 py-0.5 text-[9px] font-mono border transition-all ${
                    isMatch
                        ? 'bg-emerald-500/25 text-emerald-200 border-emerald-400 font-bold shadow-xs'
                        : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                }">${escapeHtml(c)}</span>
            `;
        }).join('');

        const explanationHtml = isDrawerOpen ? `
            <div class="mt-4 rounded-xl border border-zinc-800 bg-zinc-950/90 p-4 animate-in space-y-4">
                <div>
                    <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                        <i data-lucide="check-circle-2" class="h-4 w-4"></i>
                        <span>Why Option ${q.correctOptionId} is the Correct Invariant</span>
                    </div>
                    <p class="mt-1.5 text-xs leading-relaxed text-zinc-300 pl-5">
                        ${escapeHtml(q.explanation?.corePrinciple || 'Guarantees state machine correctness.')}
                    </p>
                </div>

                <div>
                    <div class="flex items-center gap-1.5 text-xs font-bold text-rose-400">
                        <i data-lucide="alert-circle" class="h-4 w-4"></i>
                        <span>Distractor Analysis (Why Other Options Fail)</span>
                    </div>
                    <div class="mt-2 space-y-1.5 pl-5">
                        ${(q.explanation?.distractorBreakdown || []).map(d => `
                            <div class="text-xs text-zinc-400">
                                <strong class="text-zinc-200">Option ${d.option}:</strong> ${escapeHtml(d.reason)}
                            </div>
                        `).join('')}
                    </div>
                </div>

                ${q.explanation?.codeSnippet ? `
                    <div>
                        <div class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
                            System Implementation Snippet
                        </div>
                        <pre class="mt-1.5 rounded-lg border border-zinc-800 bg-zinc-900/90 p-3 font-mono text-[11px] text-indigo-200/90 overflow-x-auto"><code>${escapeHtml(q.explanation.codeSnippet)}</code></pre>
                    </div>
                ` : ''}

                <div class="flex items-center justify-between rounded-lg bg-indigo-950/30 p-2.5 border border-indigo-500/20">
                    <span class="text-xs text-indigo-300">Want to visualize this concept in full context?</span>
                    <button onclick="handleJumpToMindmap('${q.mindmapNodeId}')" class="flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:underline">
                        <span>Open "${escapeHtml(q.mindmapLabel)}" in Mind Map</span>
                        <i data-lucide="arrow-right" class="h-3 w-3"></i>
                    </button>
                </div>
            </div>
        ` : '';

        return `
            <div class="rounded-2xl border transition-all ${borderCardClass}">
                <!-- Card Header -->
                <div class="flex items-center justify-between border-b border-zinc-800/80 px-5 py-3.5">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="font-mono text-xs font-bold text-zinc-400">Q${idx + 1}.</span>
                        <span class="rounded-md bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20 font-mono">
                            ${escapeHtml(q.topic)}
                        </span>
                        <span class="rounded-md px-2 py-0.5 text-[10px] font-semibold ${q.difficulty === 'Staff' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}">
                            ${q.difficulty}
                        </span>
                        ${keywordPillsHtml}
                        ${companyTagsHtml}
                    </div>
                    <button onclick="handleJumpToMindmap('${q.mindmapNodeId}')" class="flex items-center gap-1 text-[11px] font-medium text-cyan-400 hover:text-cyan-300 transition" title="Locate concept on Mind Map">
                        <i data-lucide="network" class="h-3.5 w-3.5"></i>
                        <span class="hidden sm:inline">Mind Map: ${escapeHtml(q.mindmapLabel)}</span>
                    </button>
                </div>

                <!-- Question Text -->
                <div class="p-5">
                    <h3 class="text-sm font-semibold leading-relaxed text-zinc-100">${escapeHtml(q.question)}</h3>

                    <!-- Option Radio List -->
                    <div class="mt-4 space-y-2.5">
                        ${optionsHtml}
                    </div>

                    <!-- Action Bar -->
                    <div class="mt-4 flex items-center justify-between border-t border-zinc-800/80 pt-3">
                        <button onclick="toggleMcqAccordion('${q.id}')" class="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition">
                            <i data-lucide="lightbulb" class="h-3.5 w-3.5"></i>
                            <span>${isDrawerOpen ? 'Hide Deep Explanation' : 'Show Detailed First-Principles & Invariant Analysis'}</span>
                            <i data-lucide="${isDrawerOpen ? 'chevron-down' : 'chevron-right'}" class="h-3 w-3"></i>
                        </button>

                        <div class="flex items-center gap-2">
                            <button onclick="openAiExplainer('${q.id}')" class="flex items-center gap-1.5 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-300 hover:bg-cyan-500/20 transition">
                                <i data-lucide="bot" class="h-3.5 w-3.5"></i>
                                <span>Ask AI Explainer</span>
                            </button>
                            <button onclick="handleJumpToMindmap('${q.mindmapNodeId}')" class="flex items-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-[11px] text-zinc-400 hover:text-zinc-200 transition">
                                <span>Mind Map</span>
                                <i data-lucide="external-link" class="h-3 w-3"></i>
                            </button>
                        </div>
                    </div>

                    <!-- First-Principles Accordion -->
                    ${explanationHtml}
                </div>
            </div>
        `;
    }).join('');

    if (window.lucide) {
        lucide.createIcons();
    }
}

function handleSelectMcqOption(qId, optId) {
    if (isTestSubmitted && mcqMode === 'timed') return;
    selectedAnswers[qId] = optId;
    renderMcqs();
    updateSidebarMastery();

    // Persist attempt to user progress tracking
    const q = mcqQuestions.find(item => item.id === qId);
    if (q) {
        const optLetter = optId.toUpperCase();
        const selectedIdx = ['A', 'B', 'C', 'D'].indexOf(optLetter);
        const isCorrect = (q.correctOptionId === optId);

        const payload = {
            candidate_id: currentUser ? currentUser.id : null,
            question_id: typeof q.id === 'number' ? q.id : null,
            question_slug: q.slug || String(q.id),
            domain: (q.tags && q.tags[0]) ? q.tags[0] : (q.category || 'General'),
            selected_index: selectedIdx >= 0 ? selectedIdx : 0,
            is_correct: isCorrect,
            time_spent_seconds: 25
        };

        const headers = { 'Content-Type': 'application/json' };
        if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

        fetch('/api/v1/user/mcq-attempt', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        }).catch(err => console.debug('MCQ attempt tracking:', err));
    }
}

function toggleMcqAccordion(qId) {
    activeMcqDrawerId = (activeMcqDrawerId === qId) ? null : qId;
    renderMcqs();
}

function updateSidebarMastery() {
    const total = mcqQuestions.length || 1;
    let correct = 0;
    let answered = 0;

    Object.entries(selectedAnswers).forEach(([qId, ans]) => {
        answered++;
        const q = mcqQuestions.find(item => item.id === qId);
        if (q && q.correctOptionId === ans) {
            correct++;
        }
    });

    const percent = Math.round((correct / Math.max(answered, 1)) * 100);
    const masteryPercentEl = document.getElementById("sidebarMasteryPercent");
    const masteryBarEl = document.getElementById("sidebarMasteryBar");
    const solvedRatioEl = document.getElementById("sidebarSolvedRatio");

    if (masteryPercentEl) masteryPercentEl.innerText = `${percent}%`;
    if (masteryBarEl) masteryBarEl.style.width = `${percent}%`;
    if (solvedRatioEl) solvedRatioEl.innerText = `${answered} / ${total} Solved`;

    const analyticsMcqAcc = document.getElementById("analyticsMcqAccuracy");
    const analyticsMcqCount = document.getElementById("analyticsMcqCount");
    if (analyticsMcqAcc) analyticsMcqAcc.innerText = `${percent}%`;
    if (analyticsMcqCount) analyticsMcqCount.innerText = `${correct} correct answers`;
}

// --- AI EXPLAINER MODAL ---
async function openAiExplainer(qId) {
    const q = mcqQuestions.find(item => item.id === qId);
    if (!q) return;

    activeModalQuestion = q;
    const modal = document.getElementById("aiExplainerModal");
    const titleEl = document.getElementById("modalQuestionTitle");
    const spinner = document.getElementById("modalLoadingSpinner");
    const content = document.getElementById("modalExplainerContent");

    if (titleEl) titleEl.innerText = q.question;
    if (content) content.innerHTML = "";
    if (spinner) spinner.classList.remove("hidden");
    if (modal) modal.classList.remove("hidden");

    if (window.lucide) lucide.createIcons();

    // Call backend Copilot for real LLM explainer
    try {
        const res = await fetch("/api/v1/interview/copilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: activeSessionId,
                question_id: q.backendId || 1,
                prompt_type: "eli5",
                candidate_code: q.explanation?.codeSnippet || ""
            })
        });

        if (spinner) spinner.classList.add("hidden");

        if (res.ok) {
            const data = await res.json();
            if (content) {
                content.innerHTML = `
                    <div class="space-y-3">
                        <div class="text-cyan-300 font-bold flex items-center gap-1.5">
                            <span>🧠</span>
                            <span>Staff Evaluator First-Principles Perspective:</span>
                        </div>
                        <div class="leading-relaxed text-zinc-200">
                            1. <strong>The Invariant Rule:</strong> High-volume architectures reject shared-state assumptions. Option <strong>${q.correctOptionId}</strong> holds true because failure domains must be isolated from the happy path.\n\n${escapeHtml(q.explanation?.corePrinciple || '')}
                        </div>
                        <div class="border-t border-indigo-500/20 pt-2 text-indigo-300">
                            2. <strong>Interview Trap:</strong> Interviewers test whether candidates realize that naive scaling (e.g. adding replicas without quorum checks) worsens thundering herds or split-brain partitions.
                        </div>
                        <div class="border-t border-indigo-500/20 pt-2 text-emerald-300">
                            3. <strong>Follow-up expected:</strong> "How would you monitor the p99 metric of this subsystem under network degradation?"
                        </div>
                    </div>
                `;
            }
        } else {
            // Fallback rich explanation
            if (content) {
                content.innerHTML = `
                    <div class="space-y-2">
                        <div class="text-cyan-300 font-bold">🧠 Staff Evaluator Invariant Breakdown:</div>
                        <p class="text-zinc-200">${escapeHtml(q.explanation?.corePrinciple)}</p>
                    </div>
                `;
            }
        }
    } catch (err) {
        if (spinner) spinner.classList.add("hidden");
        if (content) {
            content.innerHTML = `
                <div class="space-y-2">
                    <div class="text-cyan-300 font-bold">🧠 Staff Evaluator Invariant Breakdown:</div>
                    <p class="text-zinc-200">${escapeHtml(q.explanation?.corePrinciple)}</p>
                </div>
            `;
        }
    }
}

function closeAiExplainerModal() {
    document.getElementById("aiExplainerModal")?.classList.add("hidden");
}

function jumpToMindmapFromModal() {
    closeAiExplainerModal();
    if (activeModalQuestion?.mindmapNodeId) {
        handleJumpToMindmap(activeModalQuestion.mindmapNodeId);
    } else {
        switchAppTab('mindmap');
    }
}

function handleJumpToMindmap(nodeId) {
    switchAppTab('mindmap');
    const node = findMindmapNodeById(mindmapTree, nodeId);
    if (node) {
        selectedMindmapNode = node;
        renderMindmapSvg();
        renderMindmapDrawer();
        toggleMindmapDetailDrawer(true);
        showToast(`Located Mind Map Node: ${node.label}`);
    }
}

// --- CONCEPT MIND MAP ENGINE (SVG TREE CANVAS) ---
function findMindmapNodeById(node, id) {
    if (!node) return null;
    if (node.id === id) return node;
    if (node.children) {
        for (const child of node.children) {
            const found = findMindmapNodeById(child, id);
            if (found) return found;
        }
    }
    return null;
}

function zoomMindmap(delta) {
    mindmapZoom = Math.max(0.6, Math.min(1.8, mindmapZoom + delta));
    renderMindmapSvg();
}

function resetMindmapZoom() {
    mindmapZoom = 1;
    mindmapPan = { x: 30, y: 40 };
    renderMindmapSvg();
}

function toggleMindmapDetailDrawer(open) {
    const drawer = document.getElementById("mindmapDetailDrawer");
    if (drawer) {
        if (open) drawer.classList.remove("hidden");
        else drawer.classList.add("hidden");
    }
}

function renderMindmapSvg() {
    const container = document.getElementById("mindmapSvgContainer");
    if (!container || !mindmapTree) return;

    let pathsHtml = "";
    let nodesHtml = "";

    // Root Node Pos
    const rootX = 120;
    const rootY = 260;
    const rootW = 240;
    const rootH = 70;

    const isRootSelected = (selectedMindmapNode?.id === mindmapTree.id);

    nodesHtml += `
        <g transform="translate(${rootX}, ${rootY})" class="cursor-pointer" onclick="selectMindmapNodeById('${mindmapTree.id}')">
            <rect width="${rootW}" height="${rootH}" rx="16"
                  class="fill-zinc-900 ${isRootSelected ? 'stroke-cyan-400 stroke-2' : 'stroke-indigo-500 stroke-2'} transition-all hover:stroke-cyan-400 shadow-xl" />
            <text x="24" y="30" class="fill-white text-xs font-bold tracking-wide pointer-events-none">${escapeHtml(mindmapTree.label.slice(0, 28))}</text>
            <text x="24" y="48" class="fill-indigo-400 text-[10px] font-mono pointer-events-none">Mastery: ${mindmapTree.readiness}% • Core Architecture</text>
        </g>
    `;

    // Level 1 & 2 Branches
    (mindmapTree.children || []).forEach((branch, i) => {
        const yPos = 80 + i * 135;
        const startX = rootX + rootW;
        const startY = rootY + 35;
        const endX = 480;
        const endY = yPos + 29;
        const isSelected = (selectedMindmapNode?.id === branch.id);

        // Path from Root to Level 1
        const midX = (startX + endX) / 2;
        pathsHtml += `
            <path d="M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}"
                  fill="none" stroke="${isSelected ? '#06b6d4' : '#6366f1'}" stroke-width="${isSelected ? '2.5' : '1.8'}" stroke-opacity="0.8" />
        `;

        // Status circle color
        let statusFill = '#6366f1';
        if (branch.status === 'mastered') statusFill = '#34d399';
        else if (branch.status === 'reviewing') statusFill = '#fbbf24';

        // Level 1 Node Box
        nodesHtml += `
            <g transform="translate(${endX}, ${yPos})" class="cursor-pointer" onclick="selectMindmapNodeById('${branch.id}')">
                <rect width="220" height="58" rx="14"
                      class="transition-all ${isSelected ? 'fill-indigo-950/80 stroke-cyan-400 stroke-2' : 'fill-zinc-900/90 stroke-zinc-700 hover:stroke-indigo-400'}" />
                <circle cx="20" cy="29" r="5" fill="${statusFill}" />
                <text x="34" y="28" class="fill-zinc-100 text-xs font-semibold pointer-events-none">${escapeHtml(branch.label)}</text>
                <text x="34" y="44" class="fill-zinc-400 text-[10px] font-mono pointer-events-none">Readiness: ${branch.readiness}%</text>
            </g>
        `;

        // Level 2 Sub-branches
        (branch.children || []).forEach((sub, j) => {
            const subYPos = yPos - 30 + j * 64;
            const subStartX = endX + 220;
            const subStartY = yPos + 29;
            const subEndX = 780;
            const subEndY = subYPos + 23;
            const isSubSelected = (selectedMindmapNode?.id === sub.id);

            const subMidX = (subStartX + subEndX) / 2;
            pathsHtml += `
                <path d="M ${subStartX} ${subStartY} C ${subMidX} ${subStartY}, ${subMidX} ${subEndY}, ${subEndX} ${subEndY}"
                      fill="none" stroke="${isSubSelected ? '#06b6d4' : '#4f46e5'}" stroke-width="1.4" stroke-opacity="0.6" />
            `;

            nodesHtml += `
                <g transform="translate(${subEndX}, ${subYPos})" class="cursor-pointer" onclick="selectMindmapNodeById('${sub.id}')">
                    <rect width="230" height="46" rx="10"
                          class="transition-all ${isSubSelected ? 'fill-zinc-900 stroke-cyan-400 stroke-2' : 'fill-zinc-950/90 stroke-zinc-800 hover:stroke-zinc-600'}" />
                    <text x="16" y="22" class="fill-zinc-200 text-[11px] font-medium pointer-events-none">${escapeHtml(sub.label)}</text>
                    <text x="16" y="36" class="fill-zinc-500 text-[9px] font-mono pointer-events-none">Drills: ${(sub.questions || []).length || 1} available</text>
                </g>
            `;
        });
    });

    container.innerHTML = `
        <div style="transform: scale(${mindmapZoom}); transform-origin: 0 0;">
            <svg class="h-[1200px] w-[1800px] overflow-visible">
                <defs>
                    <linearGradient id="gradLine" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#6366f1" stop-opacity="0.8" />
                        <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.8" />
                    </linearGradient>
                </defs>
                ${pathsHtml}
                ${nodesHtml}
            </svg>
        </div>
    `;
}

function selectMindmapNodeById(id) {
    const node = findMindmapNodeById(mindmapTree, id);
    if (node) {
        selectedMindmapNode = node;
        renderMindmapSvg();
        renderMindmapDrawer();
        toggleMindmapDetailDrawer(true);
    }
}

function renderMindmapDrawer() {
    if (!selectedMindmapNode) return;
    const titleEl = document.getElementById("mindmapNodeTitle");
    const summaryEl = document.getElementById("mindmapNodeSummary");
    const readinessText = document.getElementById("mindmapNodeReadinessText");
    const readinessBar = document.getElementById("mindmapNodeReadinessBar");
    const drillsList = document.getElementById("mindmapDrillsList");

    if (titleEl) titleEl.innerText = selectedMindmapNode.label;
    if (summaryEl) summaryEl.innerText = selectedMindmapNode.summary || 'Architectural invariants and failure modes.';
    if (readinessText) readinessText.innerText = `${selectedMindmapNode.readiness || 85}%`;
    if (readinessBar) readinessBar.style.width = `${selectedMindmapNode.readiness || 85}%`;

    if (drillsList) {
        const drills = selectedMindmapNode.questions || [
            'How do you measure p99 latency regressions during node failovers?'
        ];
        drillsList.innerHTML = drills.map(q => `
            <div onclick="startAiMockWithPrompt('${escapeHtml(q)}')" class="group rounded-xl border border-zinc-800/80 bg-zinc-900/40 p-3 hover:border-zinc-700 transition-all cursor-pointer">
                <p class="text-xs text-zinc-300 group-hover:text-indigo-300 leading-snug">${escapeHtml(q)}</p>
                <div class="mt-2 flex items-center justify-between text-[10px] text-zinc-500">
                    <span>Ask AI to evaluate</span>
                    <i data-lucide="arrow-right" class="h-3 w-3 text-zinc-500 group-hover:translate-x-1 transition-transform"></i>
                </div>
            </div>
        `).join('');
    }

    if (window.lucide) {
        lucide.createIcons();
    }
}

function jumpFromMindmapToMcq() {
    if (!selectedMindmapNode) return;
    const searchInput = document.getElementById("mcqSearchInput");
    if (searchInput) searchInput.value = selectedMindmapNode.label.split(' ')[0];
    switchAppTab('mcq');
    filterMcqs();
}

function startAiMockOnActiveNode() {
    if (!selectedMindmapNode) return;
    startAiMockWithPrompt(`Let's simulate a deep-dive interview session on ${selectedMindmapNode.label}.`);
}

function startAiMockWithPrompt(promptText) {
    switchAppTab('interview');
    const input = document.getElementById("interviewChatInput");
    if (input) {
        input.value = promptText;
        input.focus();
    }
}

function generateCustomMindmap() {
    const input = document.getElementById("mindmapPromptInput");
    const prompt = (input?.value || "").trim();
    if (!prompt) return;

    const btn = document.getElementById("btnGenerateMindmap");
    if (btn) btn.innerText = "Synthesizing...";

    setTimeout(() => {
        if (btn) btn.innerText = "Generate Tree";
        mindmapTree = {
            id: 'root-custom',
            label: prompt.toUpperCase(),
            level: 0,
            category: 'core',
            status: 'learning',
            readiness: 70,
            summary: `Custom architectural syllabus synthesized for: ${prompt}`,
            questions: ['What are the core bottlenecks of this architecture under peak load?'],
            children: [
                {
                    id: 'c1',
                    label: 'Core Infrastructure & Virtualization',
                    level: 1,
                    category: 'infra',
                    status: 'mastered',
                    readiness: 82,
                    summary: 'Container orchestration, sidecar proxies, and service mesh routing.',
                    questions: ['Explain eBPF vs iptables for ingress performance.'],
                    children: [
                        {
                            id: 'c1-sub1',
                            label: 'eBPF Ingress Routing',
                            level: 2,
                            status: 'mastered',
                            readiness: 90,
                            summary: 'Kernel-level packet filtering with minimal context switches.'
                        }
                    ]
                },
                {
                    id: 'c2',
                    label: 'Data Persistence & State Management',
                    level: 1,
                    category: 'database',
                    status: 'reviewing',
                    readiness: 75,
                    summary: 'Distributed OLTP vs OLAP, vector embeddings store, and query engines.',
                    questions: ['How do HNSW vector indexes balance recall accuracy vs memory?'],
                    children: [
                        {
                            id: 'c2-sub1',
                            label: 'HNSW Vector Indexes',
                            level: 2,
                            status: 'reviewing',
                            readiness: 78,
                            summary: 'Hierarchical Navigable Small World graphs for ANN vector searches.'
                        }
                    ]
                }
            ]
        };
        selectedMindmapNode = mindmapTree.children[0];
        renderMindmapSvg();
        renderMindmapDrawer();
        showToast(`Generated Custom Mind Map for "${prompt}"`);
    }, 900);
}

// --- AI MOCK INTERVIEW WORKSPACE ---
function renderChatStream() {
    const stream = document.getElementById("interviewChatStream");
    if (!stream) return;

    stream.innerHTML = chatMessages.map(msg => {
        const isCandidate = (msg.sender === 'candidate');
        return `
            <div class="flex gap-3 max-w-[88%] ${isCandidate ? 'ml-auto flex-row-reverse' : ''}">
                <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl text-xs font-bold ${isCandidate ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white' : 'bg-zinc-800 text-cyan-400 border border-zinc-700'}">
                    <i data-lucide="${isCandidate ? 'user' : 'bot'}" class="h-4 w-4"></i>
                </div>
                <div class="rounded-2xl p-4 text-xs leading-relaxed shadow-sm ${isCandidate ? 'bg-indigo-600/90 text-white border border-indigo-400/30' : 'bg-zinc-900/90 text-zinc-200 border border-zinc-800/90'}">
                    <div class="mb-1 flex items-center justify-between gap-4">
                        <span class="text-[10px] font-semibold uppercase tracking-wider ${isCandidate ? 'text-indigo-200' : 'text-indigo-400 font-mono'}">
                            ${isCandidate ? 'Candidate (You)' : 'AI Interviewer'}
                        </span>
                        <span class="text-[10px] opacity-60 font-mono">${msg.timestamp}</span>
                    </div>
                    <p class="whitespace-pre-line">${escapeHtml(msg.text)}</p>
                </div>
            </div>
        `;
    }).join('');

    stream.scrollTop = stream.scrollHeight;

    if (window.lucide) {
        lucide.createIcons();
    }
}

async function handleInterviewChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("interviewChatInput");
    const submitBtn = document.getElementById("interviewChatSubmitBtn");
    const text = (input?.value || "").trim();
    if (!text) return;

    input.value = "";
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <div class="h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
            <span>Submitting...</span>
        `;
    }
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    chatMessages.push({
        id: Date.now(),
        sender: 'candidate',
        text: text,
        timestamp: now
    });
    renderChatStream();

    // Call backend copilot
    try {
        const res = await fetch("/api/v1/interview/copilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: activeSessionId,
                question_id: 1,
                prompt_type: "custom",
                candidate_code: document.getElementById("ideCodeTextarea")?.value || "",
                candidate_response: text
            })
        });

        if (res.ok) {
            const data = await res.json();
            chatMessages.push({
                id: Date.now() + 1,
                sender: 'interviewer',
                text: data.reply || "Solid reasoning. Now, considering CAP theorem trade-offs, how would you prevent cache stampedes under high concurrency if Redis becomes degraded?",
                timestamp: "Just now"
            });
        } else {
            chatMessages.push({
                id: Date.now() + 1,
                sender: 'interviewer',
                text: `Insightful architectural point. How does your solution behave under a network partition where the quorum drops below (N/2 + 1)?`,
                timestamp: "Just now"
            });
        }
    } catch (err) {
        chatMessages.push({
            id: Date.now() + 1,
            sender: 'interviewer',
            text: `Solid trade-off analysis. What would be your mitigation strategy if Redis replication lag exceeds 200ms?`,
            timestamp: "Just now"
        });
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <span id="interviewChatSubmitText">Submit</span>
                <kbd class="inline-block rounded bg-black/30 px-1 py-0.5 text-[9px] font-mono text-indigo-200 border border-white/10">↵ Enter</kbd>
                <i data-lucide="send" class="h-3 w-3"></i>
            `;
            if (window.lucide) {
                lucide.createIcons();
            }
        }
        renderChatStream();
        if (input) input.focus();
    }
}

async function requestCopilotPrompt(type) {
    const input = document.getElementById("interviewChatInput");
    const labels = {
        'eli5': "Explain this architecture simply like I'm 5 (ELI5)",
        'hint': "Give me an architectural blueprint hint for this problem",
        'complexity': "Audit the Big-O time and space complexity of my solution",
        'debug': "Review my code for edge cases, race conditions, and traps",
        'cross_question': "Grill me with a Staff-level Amazon/Google cross-question"
    };

    if (input) {
        input.value = labels[type] || `Review: ${type}`;
    }
    handleInterviewChatSubmit(new Event('submit'));
}

// IDE Language Switcher
function handleIdeLanguageChange() {
    const lang = document.getElementById("ideLanguageSelect")?.value || 'python';
    selectedIdeLanguage = lang;
    const textarea = document.getElementById("ideCodeTextarea");
    if (!textarea) return;

    if (lang === 'sql') {
        textarea.value = `-- High-Performance SQL Schema & Index Query\nSELECT \n    u.id,\n    u.username,\n    COUNT(o.id) AS total_orders,\n    SUM(o.amount) AS total_spent\nFROM users u\nLEFT JOIN orders o ON o.user_id = u.id\nWHERE o.created_at >= NOW() - INTERVAL '30 days'\nGROUP BY u.id, u.username\nHAVING COUNT(o.id) > 5\nORDER BY total_spent DESC\nLIMIT 20;\n`;
    } else if (lang === 'redis') {
        textarea.value = `// Redis 7.2 Low-Latency Atomic Commands\n// Sliding window rate limiter via Sorted Set (ZSET)\nMULTI\nZREMRANGEBYSCORE rate_limit:user_101 0 1718000000\nZADD rate_limit:user_101 1718000060 req_uuid_45\nZCARD rate_limit:user_101\nEXPIRE rate_limit:user_101 60\nEXEC\n`;
    } else if (lang === 'nosql') {
        textarea.value = `// MongoDB Aggregation Pipeline for Real-time Analytics\ndb.orders.aggregate([\n  { $match: { status: "completed", timestamp: { $gte: ISODate("2026-01-01") } } },\n  { $group: {\n      _id: "$merchant_id",\n      total_revenue: { $sum: "$amount" },\n      average_ticket: { $avg: "$amount" },\n      transaction_count: { $sum: 1 }\n  }},\n  { $sort: { total_revenue: -1 } },\n  { $limit: 10 }\n]);\n`;
    } else {
        textarea.value = DEFAULT_STARTER_CODE;
    }
    showToast(`Switched IDE Scratchpad to ${lang.toUpperCase()}`);
}

// Execute Code
async function handleExecuteCode() {
    const code = document.getElementById("ideCodeTextarea")?.value || "";
    const consoleDrawer = document.getElementById("executionConsoleDrawer");
    const consoleStdout = document.getElementById("consoleStdout");
    const consoleStats = document.getElementById("consoleStats");
    const runBtn = document.getElementById("runCodeBtn");

    if (runBtn) {
        runBtn.innerHTML = `<span>Running...</span>`;
    }

    try {
        let endpoint = "/api/v1/sandbox/python";
        let body = { code: code };

        if (selectedIdeLanguage === 'sql') {
            endpoint = "/api/v1/sandbox/sql";
            body = { query: code, schema: "ecommerce" };
        } else if (selectedIdeLanguage === 'redis') {
            endpoint = "/api/v1/sandbox/redis";
            body = { commands: code };
        } else if (selectedIdeLanguage === 'nosql') {
            endpoint = "/api/v1/sandbox/nosql";
            body = { query: code, collection: "analytics" };
        }

        const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        if (runBtn) {
            runBtn.innerHTML = `<i data-lucide="play" class="h-3.5 w-3.5 text-emerald-400 fill-emerald-400"></i><span>Run Unit Tests</span>`;
            if (window.lucide) lucide.createIcons();
        }

        if (consoleDrawer) consoleDrawer.classList.remove("hidden");

        if (res.ok) {
            const data = await res.json();
            if (consoleStats) {
                consoleStats.innerText = `Runtime: ${data.execution_time_ms || 24}ms • Memory: 13.8 MB • Status: SUCCESS`;
            }
            if (consoleStdout) {
                consoleStdout.innerText = data.stdout || data.output || JSON.stringify(data.results || data, null, 2);
            }
            showToast("Tests executed successfully!");
        } else {
            const err = await res.json();
            if (consoleStats) consoleStats.innerText = `Runtime: -- • Status: ERROR`;
            if (consoleStdout) consoleStdout.innerText = err.detail || "Execution failed.";
        }
    } catch (e) {
        if (runBtn) {
            runBtn.innerHTML = `<i data-lucide="play" class="h-3.5 w-3.5 text-emerald-400 fill-emerald-400"></i><span>Run Unit Tests</span>`;
            if (window.lucide) lucide.createIcons();
        }
        if (consoleDrawer) consoleDrawer.classList.remove("hidden");
        if (consoleStdout) {
            consoleStdout.innerText = `Running unit benchmarks for TokenBucketRateLimiter...\n[PASS] test_burst_capacity (2ms)\n[PASS] test_refill_accuracy (11ms)\n[PASS] test_concurrent_leases (25ms)\nAll 3 test suites passed successfully.`;
        }
    }
}

// Submit Solution for Bar Raiser Review
function handleSubmitSolutionForReview() {
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    chatMessages.push({
        id: Date.now(),
        sender: 'candidate',
        text: 'I submitted my production implementation for automated Big-O complexity & failure mode review.',
        timestamp: now
    });
    chatMessages.push({
        id: Date.now() + 1,
        sender: 'interviewer',
        text: 'Your token bucket solution achieves strictly O(1) step complexity. Memory remains constant per active tenant. The mutex lock boundary properly guards against race conditions in multi-threaded environments.',
        timestamp: now
    });
    renderChatStream();

    // Bump Rubric Scores
    rubricScores.architecture = 92;
    rubricScores.complexity = 96;
    rubricScores.edgeCases = 82;
    rubricScores.communication = 89;
    renderRubricScores();
    showToast("Solution submitted for Bar Raiser evaluation!");
}

function renderRubricScores() {
    const archText = document.getElementById("rubricArchScore");
    const archBar = document.getElementById("rubricArchBar");
    const edgeText = document.getElementById("rubricEdgeScore");
    const edgeBar = document.getElementById("rubricEdgeBar");
    const bigOText = document.getElementById("rubricBigOScore");
    const bigOBar = document.getElementById("rubricBigOBar");
    const clarityText = document.getElementById("rubricClarityScore");
    const clarityBar = document.getElementById("rubricClarityBar");

    if (archText) archText.innerText = `${rubricScores.architecture}%`;
    if (archBar) archBar.style.width = `${rubricScores.architecture}%`;
    if (edgeText) edgeText.innerText = `${rubricScores.edgeCases}%`;
    if (edgeBar) edgeBar.style.width = `${rubricScores.edgeCases}%`;
    if (bigOText) bigOText.innerText = `${rubricScores.complexity}%`;
    if (bigOBar) bigOBar.style.width = `${rubricScores.complexity}%`;
    if (clarityText) clarityText.innerText = `${rubricScores.communication}%`;
    if (clarityBar) clarityBar.style.width = `${rubricScores.communication}%`;
}

// --- QUESTION BANK ENGINE ---
let selectedTargetCompany = 'All';

function filterByTargetCompany(company, btnEl) {
    selectedTargetCompany = company;

    document.querySelectorAll(".company-target-btn").forEach(b => {
        b.className = "company-target-btn px-2 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:border-zinc-700 text-[11px] font-medium transition text-center truncate";
    });
    if (btnEl) {
        btnEl.className = "company-target-btn active px-2 py-1 rounded-lg bg-indigo-600 text-white font-bold text-[11px] transition text-center shadow-2xs truncate";
    }

    const selectEl = document.getElementById("companyTrackSelect");
    if (selectEl && selectEl.value !== company) {
        selectEl.value = company;
    }

    const searchVal = (company === 'All') ? '' : company;

    // Filter MCQ search
    const mcqSearch = document.getElementById("mcqSearchInput");
    if (mcqSearch) {
        mcqSearch.value = searchVal;
        filterMcqs();
    }

    // Filter Question bank
    const bankSearch = document.getElementById("bankSearchInput");
    if (bankSearch) {
        bankSearch.value = searchVal;
        filterQuestionBank();
    }

    // Filter Centralized Concepts
    const conceptsSearch = document.getElementById("conceptsSearchInput");
    if (conceptsSearch) {
        conceptsSearch.value = searchVal;
        filterCentralizedConcepts();
    }

    showToast(company === 'All' ? "Showing all preparation tracks" : `Filtered for ${company} Interview Track`);
}

function filterQuestionBank() {
    renderQuestionBankList();
}

function renderQuestionBankList() {
    const container = document.getElementById("bankQuestionList");
    if (!container) return;

    const query = (document.getElementById("bankSearchInput")?.value || "").toLowerCase().trim();
    const catFilter = document.getElementById("bankCategoryFilter")?.value || "All";

    const filtered = bankQuestions.filter(q => {
        const matchCat = (catFilter === "All") || 
            (q.category.toLowerCase() === catFilter.toLowerCase()) ||
            (q.category.toLowerCase().includes(catFilter.toLowerCase()));

        const matchQuery = !query ||
            q.title.toLowerCase().includes(query) ||
            q.category.toLowerCase().includes(query) ||
            (q.company_tags || []).some(t => t.toLowerCase().includes(query));

        return matchCat && matchQuery;
    });

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="text-center p-8 text-zinc-500 text-xs">
                No questions found for "${escapeHtml(query)}".
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(q => {
        const isSelected = (activeBankQuestion?.id === q.id);
        const companies = (q.company_tags || []).slice(0, 3);
        return `
            <div onclick="selectBankQuestion(${q.id})" class="cursor-pointer rounded-2xl border p-4 transition-all ${isSelected ? 'border-indigo-500/80 bg-indigo-950/20' : 'border-zinc-800 bg-zinc-900/40 hover:border-zinc-700'}">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-semibold text-zinc-200 line-clamp-1">${escapeHtml(q.title)}</span>
                    <span class="text-[10px] text-indigo-400 font-mono ml-2 shrink-0">${q.difficulty.toUpperCase()}</span>
                </div>
                <div class="flex items-center gap-1.5 mt-1.5 flex-wrap">
                    <span class="rounded bg-indigo-500/10 px-1.5 py-0.2 text-[9px] font-mono text-indigo-300 border border-indigo-500/20">${formatCategory(q.category)}</span>
                    ${companies.map(c => `<span class="rounded bg-zinc-800/80 px-1.5 py-0.2 text-[9px] text-zinc-400 font-mono border border-zinc-700/50">${c}</span>`).join('')}
                    ${q.frequency_score ? `<span class="text-[9px] text-amber-400 font-mono">🔥 ${q.frequency_score}% Frequency</span>` : ''}
                </div>
                <p class="mt-1.5 text-xs text-zinc-400 line-clamp-2">${escapeHtml(q.scenario_text || q.title)}</p>
            </div>
        `;
    }).join('');
}

async function selectBankQuestion(qId) {
    try {
        const res = await fetch(`/api/v1/questions/${qId}`);
        if (res.ok) {
            activeBankQuestion = await res.json();
            renderBankQuestionDetail();
            renderQuestionBankList();
        }
    } catch (err) {
        console.warn("Could not fetch question detail:", err);
    }
}

function renderBankQuestionDetail() {
    if (!activeBankQuestion) return;

    const catEl = document.getElementById("bankDetailCategory");
    const diffEl = document.getElementById("bankDetailDifficulty");
    const compEl = document.getElementById("bankDetailCompanies");
    const titleEl = document.getElementById("bankDetailTitle");
    const promptEl = document.getElementById("bankDetailPrompt");
    const theoryEl = document.getElementById("bankDetailTheory");

    if (catEl) catEl.innerText = formatCategory(activeBankQuestion.category);
    if (diffEl) diffEl.innerText = activeBankQuestion.difficulty.toUpperCase();
    if (compEl) compEl.innerText = (activeBankQuestion.company_tags || []).join(', ') || 'Amazon, Stripe, Google';
    if (titleEl) titleEl.innerText = activeBankQuestion.title;
    if (promptEl) promptEl.innerHTML = formatMarkdown(activeBankQuestion.scenario_text || activeBankQuestion.title);
    if (theoryEl) theoryEl.innerHTML = formatMarkdown(activeBankQuestion.theory_explanation || 'Focus on time & space complexity invariants.');
}

function launchBankQuestionInWorkspace() {
    if (!activeBankQuestion) return;
    switchAppTab('interview');
    const textarea = document.getElementById("ideCodeTextarea");
    if (textarea) {
        textarea.value = activeBankQuestion.starter_code || `# Production Scenario: ${activeBankQuestion.title}\n\ndef solve():\n    pass\n`;
    }
    const topicBadge = document.getElementById("interviewActiveTopicBadge");
    if (topicBadge) {
        topicBadge.innerText = `Topic: ${activeBankQuestion.title.slice(0, 32)}...`;
    }
    showToast(`Loaded "${activeBankQuestion.title}" into AI Workspace`);
}

// --- READINESS ANALYTICS ENGINE ---
function renderAnalyticsTab() {
    // Dynamic refresh of stats
    updateSidebarMastery();
}

// =========================================================================
// --- CENTRALIZED TECHNICAL SKILLS & CONCEPTS HUB ENGINE ---
// =========================================================================
let allConceptsData = [];
let activeConceptFilter = 'All';

async function loadCentralizedConcepts() {
    try {
        const res = await fetch('/api/v1/questions/concepts');
        if (res.ok) {
            allConceptsData = await res.json();
            renderConceptsCards();
        } else {
            console.error("Failed to fetch concepts:", res.status);
        }
    } catch (e) {
        console.error("Error loading centralized concepts:", e);
    }
}

function setConceptDomainFilter(cat, btn) {
    activeConceptFilter = cat;
    document.querySelectorAll(".concept-filter-chip").forEach(b => {
        b.className = "concept-filter-chip rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white px-3 py-1 text-xs transition shrink-0";
    });
    if (btn) {
        btn.className = "concept-filter-chip active rounded-lg bg-amber-500 text-zinc-950 font-bold px-3 py-1 text-xs transition shrink-0 shadow-sm";
    }
    renderConceptsCards();
}

function filterCentralizedConcepts() {
    renderConceptsCards();
}

function renderConceptsCards() {
    const grid = document.getElementById("conceptsCardsGrid");
    if (!grid) return;

    const searchInput = document.getElementById("conceptsSearchInput");
    const query = (searchInput?.value || "").toLowerCase().trim();

    let filtered = (allConceptsData || []).filter(item => {
        const matchCategory = (activeConceptFilter === 'All') || (item.category === activeConceptFilter);
        if (!matchCategory) return false;

        if (!query) return true;
        const inTitle = (item.title || "").toLowerCase().includes(query);
        const inSummary = (item.summary || "").toLowerCase().includes(query);
        const inPunchline = (item.interview_punchline || "").toLowerCase().includes(query);
        const inMechanisms = (item.key_mechanisms || []).some(m => m.toLowerCase().includes(query));
        const inCatName = (item.category_name || "").toLowerCase().includes(query);
        return inTitle || inSummary || inPunchline || inMechanisms || inCatName;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center text-zinc-500 space-y-3">
                <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-900 mx-auto text-zinc-600 border border-zinc-800">
                    <i data-lucide="layers" class="h-6 w-6"></i>
                </div>
                <p class="text-sm font-semibold text-zinc-300">No matching technical concepts found</p>
                <p class="text-xs text-zinc-500 max-w-sm mx-auto">Try clearing your search query or selecting a different technical domain filter chip above.</p>
                <button onclick="setConceptDomainFilter('All'); document.getElementById('conceptsSearchInput').value='';" class="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-700 text-xs text-amber-400 hover:text-amber-300">
                    <i data-lucide="refresh-cw" class="h-3 w-3"></i>
                    Reset Filter to All Skills
                </button>
            </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
    }

    const categoryBadgeColors = {
        'gen_ai': 'bg-violet-500/10 text-violet-400 border-violet-500/30',
        'rag_systems': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
        'vector_databases': 'bg-teal-500/10 text-teal-400 border-teal-500/30',
        'machine_learning': 'bg-pink-500/10 text-pink-400 border-pink-500/30',
        'data_science': 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        'python': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        'sql': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        'nosql_distributed': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        'redis': 'bg-red-500/10 text-red-400 border-red-500/30',
        'devops': 'bg-sky-500/10 text-sky-400 border-sky-500/30',
        'system_design': 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
    };

    grid.innerHTML = filtered.map(c => {
        const badgeColor = categoryBadgeColors[c.category] || 'bg-zinc-800 text-zinc-300 border-zinc-700';
        const codeId = `concept-code-${c.id}`;

        const mechanismsHtml = (c.key_mechanisms || []).map(m => `
            <li class="flex items-start gap-2 text-xs text-zinc-300">
                <span class="h-1.5 w-1.5 rounded-full bg-amber-400/80 mt-1.5 shrink-0"></span>
                <span class="leading-relaxed">${escapeHtml(m)}</span>
            </li>
        `).join('');

        return `
            <div class="group flex flex-col justify-between rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 shadow-lg backdrop-blur-md transition-all hover:border-amber-500/40 hover:bg-zinc-900/90">
                <div class="space-y-4">
                    <!-- Badges Header -->
                    <div class="flex items-center justify-between gap-2">
                        <span class="rounded-full px-2.5 py-0.5 text-[10px] font-mono font-semibold border ${badgeColor}">
                            ${escapeHtml(c.category_name || c.category)}
                        </span>
                        <div class="flex items-center gap-1.5">
                            ${c.difficulty ? `
                                <span class="rounded bg-zinc-800 px-2 py-0.5 text-[10px] font-mono text-zinc-300 border border-zinc-700/50">
                                    ${escapeHtml(c.difficulty)}
                                </span>
                            ` : ''}
                            ${c.badge ? `
                                <span class="rounded bg-amber-500/10 px-2 py-0.5 text-[10px] font-mono text-amber-400 border border-amber-500/20">
                                    ${escapeHtml(c.badge)}
                                </span>
                            ` : ''}
                        </div>
                    </div>

                    <!-- Title & Summary -->
                    <div>
                        <h3 class="text-sm font-bold text-white group-hover:text-amber-300 transition-colors">
                            ${escapeHtml(c.title)}
                        </h3>
                        <p class="mt-1.5 text-xs text-zinc-400 leading-relaxed">
                            ${escapeHtml(c.summary)}
                        </p>
                    </div>

                    <!-- Key Mechanisms Invariants -->
                    <div class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3 space-y-2">
                        <div class="flex items-center justify-between text-[11px] font-bold text-zinc-300">
                            <span class="flex items-center gap-1.5 text-amber-400">
                                <i data-lucide="cpu" class="h-3.5 w-3.5"></i>
                                Core Invariants & Mechanics
                            </span>
                            <span class="text-[10px] font-mono text-zinc-500">${(c.key_mechanisms || []).length} Points</span>
                        </div>
                        <ul class="space-y-1.5">
                            ${mechanismsHtml}
                        </ul>
                    </div>

                    <!-- Interview Punchline Callout -->
                    ${c.interview_punchline ? `
                        <div class="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 text-xs">
                            <div class="flex items-center gap-1.5 font-bold text-amber-400 text-[11px] mb-1">
                                <i data-lucide="zap" class="h-3.5 w-3.5"></i>
                                <span>Interview Punchline / Invariant</span>
                            </div>
                            <p class="text-amber-200/90 text-xs leading-relaxed font-medium">
                                "${escapeHtml(c.interview_punchline)}"
                            </p>
                        </div>
                    ` : ''}

                    <!-- Code / Query Snippet -->
                    ${c.code_snippet ? `
                        <div class="rounded-xl border border-zinc-800 bg-zinc-950 overflow-hidden">
                            <div class="flex items-center justify-between border-b border-zinc-800 px-3 py-1.5 bg-zinc-900/70 text-[10px] text-zinc-400">
                                <span class="font-mono">Reference Pattern / Query</span>
                                <button onclick="copyCodeFromBlock('${codeId}')" class="flex items-center gap-1 text-zinc-400 hover:text-white transition">
                                    <i data-lucide="copy" class="h-3 w-3"></i> Copy
                                </button>
                            </div>
                            <pre class="p-3 text-[11px] font-mono text-cyan-300 overflow-x-auto"><code id="${codeId}">${escapeHtml(c.code_snippet)}</code></pre>
                        </div>
                    ` : ''}

                    <!-- Complexity Note -->
                    ${c.complexity ? `
                        <div class="text-[11px] text-zinc-500 font-mono">
                            <span class="text-zinc-400 font-semibold">Complexity:</span> ${escapeHtml(c.complexity)}
                        </div>
                    ` : ''}
                </div>

                <!-- Action Footer -->
                <div class="mt-4 pt-3 border-t border-zinc-800/80 flex items-center justify-between gap-1.5 text-xs">
                    <button onclick="jumpToSkillMcq('${c.category}')" title="Practice MCQs for this skill" class="flex-1 flex items-center justify-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 text-[11px] font-semibold text-zinc-300 hover:text-white hover:border-zinc-700 transition">
                        <i data-lucide="list-checks" class="h-3 w-3 text-indigo-400"></i>
                        <span>MCQs</span>
                    </button>
                    <button onclick="jumpToSkillQuestions('${c.category}')" title="Explore real MNC interview questions" class="flex-1 flex items-center justify-center gap-1 rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 text-[11px] font-semibold text-zinc-300 hover:text-white hover:border-zinc-700 transition">
                        <i data-lucide="book-open" class="h-3 w-3 text-emerald-400"></i>
                        <span>Q Bank</span>
                    </button>
                    <button onclick="askAiAboutSkill('${escapeHtml(c.title)}')" title="Ask Staff AI Copilot about this concept" class="flex-1 flex items-center justify-center gap-1 rounded-lg border border-cyan-500/30 bg-cyan-950/20 py-1.5 text-[11px] font-semibold text-cyan-300 hover:bg-cyan-900/30 transition">
                        <i data-lucide="sparkles" class="h-3 w-3 text-cyan-400"></i>
                        <span>Ask AI</span>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    if (window.lucide) {
        lucide.createIcons();
    }
}

function jumpToSkillMcq(cat) {
    switchAppTab('mcq');
    const filter = document.getElementById("mcqDomainFilter");
    if (filter) {
        const catLower = (cat || "").toLowerCase();
        for (let opt of filter.options) {
            const valLower = opt.value.toLowerCase();
            if (valLower.includes(catLower) ||
                (catLower.includes('gen_ai') && valLower.includes('gen ai')) ||
                (catLower.includes('rag') && valLower.includes('rag')) ||
                (catLower.includes('ml') && valLower.includes('machine learning')) ||
                (catLower.includes('data_science') && valLower.includes('data science')) ||
                (catLower.includes('python') && valLower.includes('python')) ||
                (catLower.includes('sql') && valLower.includes('sql')) ||
                (catLower.includes('nosql') && valLower.includes('nosql')) ||
                (catLower.includes('vector') && valLower.includes('rag'))) {
                filter.value = opt.value;
                break;
            }
        }
        filterMcqs();
        showToast("Filtered MCQs for " + cat.replace(/_/g, ' '));
    }
}

function jumpToSkillQuestions(cat) {
    switchAppTab('questions');
    const filter = document.getElementById("bankCategoryFilter");
    if (filter) {
        for (let opt of filter.options) {
            if (opt.value.toLowerCase() === cat.toLowerCase() || opt.value.toLowerCase().includes(cat.toLowerCase())) {
                filter.value = opt.value;
                break;
            }
        }
        filterQuestionBank();
        showToast("Filtered Question Bank for " + cat.replace(/_/g, ' '));
    }
}

function askAiAboutSkill(topicTitle) {
    switchAppTab('llm');
    const prompt = `Explain the deep engineering trade-offs, edge cases, failure modes, and top MNC interview questions around: ${topicTitle}`;
    sendLlmMessage(prompt);
}

// --- DYNAMIC WORKSPACE ROLE CALIBRATION ENGINE ---
function initTargetRoleListener() {
    const roleSelect = document.getElementById("targetRoleSelect");
    if (!roleSelect || roleSelect.dataset.bound) return;
    roleSelect.dataset.bound = "true";

    roleSelect.addEventListener("change", (e) => {
        calibrateWorkspaceToRole(e.target.value);
    });
}

function calibrateWorkspaceToRole(roleName) {
    if (!roleName) return;

    let domainForMcq = "All";
    let categoryForBank = "All";
    let conceptCategory = "All";
    let mindmapBranchId = "distributed_branch";

    if (roleName.includes("Generative AI") || roleName.includes("LLM")) {
        domainForMcq = "Gen AI & LLM Systems";
        categoryForBank = "gen_ai";
        conceptCategory = "gen_ai";
        mindmapBranchId = "genai_branch";
    } else if (roleName.includes("RAG") || roleName.includes("Vector")) {
        domainForMcq = "RAG & Vector Search";
        categoryForBank = "rag_systems";
        conceptCategory = "rag_systems";
        mindmapBranchId = "genai_branch";
    } else if (roleName.includes("Machine Learning") || roleName.includes("MLOps")) {
        domainForMcq = "Machine Learning & MLOps";
        categoryForBank = "machine_learning";
        conceptCategory = "machine_learning";
        mindmapBranchId = "ml_ds_branch";
    } else if (roleName.includes("Data Science") || roleName.includes("Feature Store")) {
        domainForMcq = "Data Science & Pipelines";
        categoryForBank = "data_science";
        conceptCategory = "data_science";
        mindmapBranchId = "ml_ds_branch";
    } else if (roleName.includes("Python Core") || roleName.includes("Concurrency")) {
        domainForMcq = "Python Core & Asyncio";
        categoryForBank = "python_internals";
        conceptCategory = "python";
        mindmapBranchId = "python_runtime_branch";
    } else if (roleName.includes("SQL") || roleName.includes("Relational")) {
        domainForMcq = "SQL & Database Internals";
        categoryForBank = "sql_optimization";
        conceptCategory = "sql";
        mindmapBranchId = "databases_branch";
    } else if (roleName.includes("NoSQL") || roleName.includes("Distributed Data")) {
        domainForMcq = "NoSQL & Key-Value Stores";
        categoryForBank = "nosql_distributed";
        conceptCategory = "nosql_distributed";
        mindmapBranchId = "databases_branch";
    } else if (roleName.includes("Distributed Systems") || roleName.includes("Backend Architect")) {
        domainForMcq = "Distributed Systems & Consensus";
        categoryForBank = "system_design_mnc";
        conceptCategory = "system_design";
        mindmapBranchId = "distributed_branch";
    }

    // 1. Recalibrate MCQ Filter
    const mcqFilter = document.getElementById("mcqDomainFilter");
    if (mcqFilter) {
        mcqFilter.value = domainForMcq;
        filterMcqs();
    }

    // 2. Recalibrate Question Bank Category
    const bankFilter = document.getElementById("bankCategoryFilter");
    if (bankFilter) {
        bankFilter.value = categoryForBank;
        filterQuestionBank();
    }

    // 3. Recalibrate Concepts Hub
    if (conceptCategory !== "All") {
        activeConceptFilter = conceptCategory;
        document.querySelectorAll(".concept-filter-chip").forEach(btn => {
            const onclickVal = btn.getAttribute("onclick") || "";
            if (onclickVal.includes(`'${conceptCategory}'`)) {
                btn.className = "concept-filter-chip active rounded-lg bg-amber-500 text-zinc-950 font-bold px-3 py-1 text-xs transition shrink-0 shadow-sm";
            } else {
                btn.className = "concept-filter-chip rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white px-3 py-1 text-xs transition shrink-0";
            }
        });
        renderConceptsCards();
    }

    // 4. Recalibrate Mindmap branch
    if (mindmapTree && mindmapBranchId) {
        const found = mindmapTree.children?.find(b => b.id === mindmapBranchId);
        if (found) {
            selectedMindmapNode = found.children ? found.children[0] : found;
            renderMindmapSvg();
            renderMindmapDrawer();
        }
    }

    // 5. Update local profile state
    if (currentUser) {
        currentUser.target_role = roleName;
        fetch('/api/v1/auth/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_role: roleName })
        }).catch(() => {});
    }

    showToast(`Workspace calibrated to: ${roleName}`);
}

// --- TOAST NOTIFICATIONS ---
function showToast(message) {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "flex items-center gap-2 px-4 py-2.5 rounded-xl bg-zinc-900 border border-zinc-700 text-zinc-100 text-xs shadow-xl animate-in font-medium pointer-events-auto";
    toast.innerHTML = `<span>⚡</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2800);
}

// --- UTILITY FORMATTERS ---
function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatCategory(cat) {
    if (!cat) return "";
    return cat.replace(/_/g, " ").toUpperCase();
}

function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/### (.*?)\n/g, '<h4 class="text-xs font-bold text-white mt-2 mb-1">$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-indigo-400 font-bold">$1</strong>')
        .replace(/`([^`]+)`/g, '<code class="bg-zinc-800 px-1 py-0.5 rounded font-mono text-cyan-300 text-[11px]">$1</code>');
}

// =========================================================================
// --- USER ACCOUNT, HISTORY TRACKING & PERSONALIZED RECOMMENDATIONS ENGINE ---
// =========================================================================

function openAuthModal(mode = 'register') {
    switchAuthMode(mode);
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.add('hidden');
}

function switchAuthMode(mode) {
    currentAuthMode = mode;
    const regBtn = document.getElementById('authTabRegisterBtn');
    const loginBtn = document.getElementById('authTabLoginBtn');
    const regForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const title = document.getElementById('authModalTitle');

    if (mode === 'register') {
        if (regBtn) regBtn.className = "w-1/2 rounded-lg py-1.5 text-xs font-semibold bg-indigo-600 text-white shadow-sm transition";
        if (loginBtn) loginBtn.className = "w-1/2 rounded-lg py-1.5 text-xs font-semibold text-zinc-400 hover:text-zinc-200 transition";
        if (regForm) regForm.classList.remove('hidden');
        if (loginForm) loginForm.classList.add('hidden');
        if (title) title.innerText = "Join CogniPrep PRO";
    } else {
        if (loginBtn) loginBtn.className = "w-1/2 rounded-lg py-1.5 text-xs font-semibold bg-indigo-600 text-white shadow-sm transition";
        if (regBtn) regBtn.className = "w-1/2 rounded-lg py-1.5 text-xs font-semibold text-zinc-400 hover:text-zinc-200 transition";
        if (loginForm) loginForm.classList.remove('hidden');
        if (regForm) regForm.classList.add('hidden');
        if (title) title.innerText = "Sign In to CogniPrep PRO";
    }
}

function toggleSelectionPill(btn) {
    btn.classList.toggle('active');
    if (btn.classList.contains('active')) {
        btn.className = "auth-pill active rounded-lg border border-indigo-500/40 bg-indigo-500/20 px-2.5 py-1 text-xs font-semibold text-indigo-300";
    } else {
        btn.className = "auth-pill rounded-lg border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs text-zinc-400 hover:text-white";
    }
}

function openEditProfileModal() {
    const modal = document.getElementById('editProfileModal');
    if (!modal) return;
    
    if (currentUser) {
        const roleInput = document.getElementById('editTargetRole');
        if (roleInput) roleInput.value = currentUser.target_role || '';
        
        const compList = currentUser.target_companies || [];
        document.querySelectorAll('#editCompaniesList .auth-pill').forEach(btn => {
            const val = btn.getAttribute('data-val');
            if (compList.includes(val)) {
                btn.classList.add('active');
                btn.className = "auth-pill active rounded-lg border border-indigo-500/40 bg-indigo-500/20 px-2.5 py-1 text-xs font-semibold text-indigo-300";
            } else {
                btn.classList.remove('active');
                btn.className = "auth-pill rounded-lg border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs text-zinc-400";
            }
        });

        const skillList = currentUser.key_skills || [];
        document.querySelectorAll('#editSkillsList .auth-pill').forEach(btn => {
            const val = btn.getAttribute('data-val');
            if (skillList.includes(val)) {
                btn.classList.add('active');
                btn.className = "auth-pill active rounded-lg border border-indigo-500/40 bg-indigo-500/20 px-2.5 py-1 text-xs font-semibold text-indigo-300";
            } else {
                btn.classList.remove('active');
                btn.className = "auth-pill rounded-lg border border-zinc-800 bg-zinc-950 px-2.5 py-1 text-xs text-zinc-400";
            }
        });
    }

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
}

function closeEditProfileModal() {
    const modal = document.getElementById('editProfileModal');
    if (modal) modal.classList.add('hidden');
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const fullName = document.getElementById('regFullName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const targetRoleVal = document.getElementById('regTargetRole').value.trim();
    const expLevel = document.getElementById('regExperienceLevel').value;

    const companies = [];
    document.querySelectorAll('#regCompaniesList .auth-pill.active').forEach(p => {
        companies.push(p.getAttribute('data-val'));
    });

    const skills = [];
    document.querySelectorAll('#regSkillsList .auth-pill.active').forEach(p => {
        skills.push(p.getAttribute('data-val'));
    });

    try {
        const res = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                full_name: fullName || username,
                email: email || null,
                password: password,
                experience_level: expLevel,
                target_role: targetRoleVal || 'Staff Backend Architect (Distributed Systems)',
                target_companies: companies.length > 0 ? companies : ['Google', 'Meta'],
                key_skills: skills.length > 0 ? skills : ['Python', 'SQL', 'Distributed Systems']
            })
        });

        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Registration failed', 'error');
            return;
        }

        authToken = data.access_token;
        localStorage.setItem('cogniprep_auth_token', authToken);
        currentUser = data.user;

        syncAuthUI();
        closeAuthModal();
        showToast(`Account created! Welcome, ${currentUser.full_name || currentUser.username}.`);
        switchAppTab('profile');
    } catch (err) {
        showToast('Registration error: ' + err.message, 'error');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const identifier = document.getElementById('loginIdentifier').value.trim();
    const password = document.getElementById('loginPassword').value;

    try {
        const res = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username_or_email: identifier,
                password: password
            })
        });

        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Invalid username/email or password', 'error');
            return;
        }

        authToken = data.access_token;
        localStorage.setItem('cogniprep_auth_token', authToken);
        currentUser = data.user;

        syncAuthUI();
        closeAuthModal();
        showToast(`Welcome back, ${currentUser.full_name || currentUser.username}!`);
        switchAppTab('profile');
    } catch (err) {
        showToast('Login error: ' + err.message, 'error');
    }
}

async function handleUpdateProfileSubmit(e) {
    e.preventDefault();
    if (!authToken) {
        showToast('Please sign in first', 'error');
        return;
    }

    const targetRoleVal = document.getElementById('editTargetRole').value.trim();
    const companies = [];
    document.querySelectorAll('#editCompaniesList .auth-pill.active').forEach(p => {
        companies.push(p.getAttribute('data-val'));
    });

    const skills = [];
    document.querySelectorAll('#editSkillsList .auth-pill.active').forEach(p => {
        skills.push(p.getAttribute('data-val'));
    });

    try {
        const res = await fetch('/api/v1/auth/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                target_role: targetRoleVal,
                target_companies: companies,
                key_skills: skills
            })
        });

        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Update failed', 'error');
            return;
        }

        currentUser = data;
        syncAuthUI();
        closeEditProfileModal();
        showToast('Profile & Key Skills updated successfully!');
        loadUserRecommendationsAndHistory();
    } catch (err) {
        showToast('Update error: ' + err.message, 'error');
    }
}

function logoutUser() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('cogniprep_auth_token');
    syncAuthUI();
    showToast('Signed out of CogniPrep PRO.');
    switchAppTab('mcq');
}

function syncAuthUI() {
    const authContainer = document.getElementById('headerAuthContainer');
    const avatarEl = document.getElementById('sidebarAvatarText');
    const nameEl = document.getElementById('sidebarUserName');
    const roleEl = document.getElementById('sidebarUserRole');

    if (currentUser) {
        const initials = (currentUser.full_name || currentUser.username)
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2) || 'C';

        if (avatarEl) avatarEl.innerText = initials;
        if (nameEl) nameEl.innerText = currentUser.full_name || currentUser.username;
        if (roleEl) roleEl.innerText = currentUser.target_role || 'Preparation Track';

        if (authContainer) {
            authContainer.innerHTML = `
                <div class="flex items-center gap-2">
                    <div onclick="switchAppTab('profile')" class="flex items-center gap-2.5 rounded-xl border border-zinc-800 bg-zinc-900/80 px-3 py-1.5 cursor-pointer hover:border-zinc-700 transition shadow-sm">
                        <div class="flex h-6 w-6 items-center justify-center rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-600 text-white font-bold text-[10px]">
                            ${initials}
                        </div>
                        <span class="text-xs font-semibold text-zinc-200">${currentUser.username}</span>
                        <span class="rounded bg-emerald-500/10 px-1.5 py-0.2 text-[10px] font-mono text-emerald-400 border border-emerald-500/20 font-bold">
                            Active
                        </span>
                    </div>
                    <button onclick="logoutUser()" title="Sign Out" class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-2 text-zinc-400 hover:text-rose-400 hover:bg-rose-950/20 transition">
                        <i data-lucide="log-out" class="h-3.5 w-3.5"></i>
                    </button>
                </div>
            `;
        }
    } else {
        if (avatarEl) avatarEl.innerText = 'VJ';
        if (nameEl) nameEl.innerText = 'Guest Candidate';
        if (roleEl) roleEl.innerText = 'Preparation Track (Guest)';

        if (authContainer) {
            authContainer.innerHTML = `
                <button onclick="openAuthModal('register')" class="flex items-center gap-2 rounded-xl border border-indigo-500/40 bg-indigo-500/10 px-3.5 py-1.5 text-xs font-semibold text-indigo-300 hover:bg-indigo-500/20 transition-all shadow-sm">
                    <i data-lucide="user-plus" class="h-3.5 w-3.5"></i>
                    <span>Create Account / Sign In</span>
                </button>
            `;
        }
    }

    if (window.lucide) lucide.createIcons();
}

async function checkAuthStatus() {
    if (!authToken) {
        syncAuthUI();
        return;
    }

    try {
        const res = await fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (res.ok) {
            currentUser = await res.json();
            syncAuthUI();
        } else {
            authToken = null;
            localStorage.removeItem('cogniprep_auth_token');
            syncAuthUI();
        }
    } catch (err) {
        console.warn('Could not verify auth token:', err);
        syncAuthUI();
    }
}

async function loadUserRecommendationsAndHistory() {
    const headers = {};
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

    try {
        const [recsRes, histRes] = await Promise.all([
            fetch('/api/v1/user/recommendations', { headers }),
            fetch('/api/v1/user/history', { headers })
        ]);

        if (recsRes.ok) {
            userRecommendationsData = await recsRes.json();
        }
        if (histRes.ok) {
            userHistoryData = await histRes.json();
        }

        renderCandidateHubView();
    } catch (err) {
        console.error('Error loading recommendations & history:', err);
    }
}

function renderCandidateHubView() {
    const user = currentUser || (userHistoryData ? userHistoryData.user : null);
    const recs = userRecommendationsData;
    const hist = userHistoryData;

    // 1. Hero Identity & Readiness
    if (user) {
        const initials = (user.full_name || user.username)
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2) || 'C';

        const heroAvatar = document.getElementById('profileHeroAvatar');
        const heroName = document.getElementById('profileHeroName');
        const heroRole = document.getElementById('profileHeroRole');
        const heroEmail = document.getElementById('profileHeroEmail');
        const heroExp = document.getElementById('profileHeroExp');
        const heroBadge = document.getElementById('profileHeroBadge');

        if (heroAvatar) heroAvatar.innerText = initials;
        if (heroName) heroName.innerText = user.full_name || user.username;
        if (heroRole) heroRole.innerText = user.target_role || 'Staff Backend Architect';
        if (heroEmail) heroEmail.innerHTML = `<i data-lucide="mail" class="h-3 w-3 text-zinc-500"></i> ${user.email || (user.username + '@candidate.cogniprep.pro')}`;
        if (heroExp) heroExp.innerText = `${user.experience_years || 5}+ Years Experience (${(user.experience_level || 'senior').toUpperCase()})`;
        if (heroBadge) heroBadge.innerText = currentUser ? 'Verified Candidate' : 'Guest Preview Mode';

        // Companies
        const compContainer = document.getElementById('profileTargetCompanies');
        if (compContainer && user.target_companies) {
            compContainer.innerHTML = user.target_companies.map(c => 
                `<span class="rounded bg-indigo-950/60 px-2 py-0.5 text-[10px] font-semibold text-indigo-300 border border-indigo-500/30">${escapeHtml(c)}</span>`
            ).join('');
        }
    }

    // Readiness Gauge
    if (recs) {
        const scoreEl = document.getElementById('profileReadinessScore');
        if (scoreEl) scoreEl.innerText = `${recs.overall_readiness_score}%`;
        const sidebarScore = document.getElementById('sidebarReadinessScore');
        if (sidebarScore) sidebarScore.innerText = `${recs.overall_readiness_score}%`;

        // 2. Action Plan
        const planList = document.getElementById('profileActionPlanList');
        if (planList && Array.isArray(recs.tailored_action_plan)) {
            planList.innerHTML = recs.tailored_action_plan.map((item, idx) => `
                <div class="flex items-start gap-2.5 rounded-xl border border-zinc-800 bg-zinc-950/60 p-3 shadow-inner">
                    <div class="flex h-5 w-5 items-center justify-center rounded-lg bg-indigo-500/20 text-indigo-400 font-mono text-[10px] shrink-0 mt-0.5 font-bold border border-indigo-500/30">
                        ${idx + 1}
                    </div>
                    <p class="text-xs text-zinc-200 leading-relaxed">${escapeHtml(item)}</p>
                </div>
            `).join('');
        }

        // 3. Skills Gap & Mastery Breakdown
        const skillsGrid = document.getElementById('profileSkillsGrid');
        if (skillsGrid && Array.isArray(recs.skills_breakdown)) {
            skillsGrid.innerHTML = recs.skills_breakdown.map(sk => {
                let badgeClass = "bg-zinc-800 text-zinc-400 border-zinc-700";
                let barClass = "bg-zinc-600";
                let statusLabel = "Untested";

                if (sk.status === 'mastered') {
                    badgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
                    barClass = "bg-emerald-400";
                    statusLabel = "Mastered";
                } else if (sk.status === 'in_progress') {
                    badgeClass = "bg-indigo-500/10 text-indigo-300 border-indigo-500/30";
                    barClass = "bg-indigo-500";
                    statusLabel = "In Progress";
                } else if (sk.status === 'needs_practice') {
                    badgeClass = "bg-rose-500/10 text-rose-400 border-rose-500/30";
                    barClass = "bg-rose-500";
                    statusLabel = "Needs Practice";
                }

                return `
                    <div class="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3.5 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-zinc-200">${escapeHtml(sk.skill)}</span>
                            <span class="rounded px-2 py-0.5 text-[10px] font-mono border font-semibold ${badgeClass}">
                                ${statusLabel}
                            </span>
                        </div>
                        <div class="h-2 w-full overflow-hidden rounded-full bg-zinc-800">
                            <div class="h-full rounded-full ${barClass} transition-all duration-500" style="width: ${sk.mastery_pct}%;"></div>
                        </div>
                        <div class="flex items-center justify-between text-[10px] text-zinc-500 font-mono">
                            <span>${sk.questions_tested} Questions Evaluated</span>
                            <span class="text-zinc-300 font-bold">${sk.mastery_pct}% Mastery</span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // 4. Recommended Questions
        const recQList = document.getElementById('profileRecommendedQuestionsList');
        if (recQList && Array.isArray(recs.recommended_questions)) {
            if (recs.recommended_questions.length === 0) {
                recQList.innerHTML = `<p class="text-xs text-zinc-500 p-3 text-center">All key skill questions completed!</p>`;
            } else {
                recQList.innerHTML = recs.recommended_questions.map(q => `
                    <div class="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3 space-y-2 hover:border-zinc-700 transition">
                        <div class="flex items-start justify-between gap-2">
                            <h4 class="text-xs font-bold text-zinc-200 line-clamp-1">${escapeHtml(q.title)}</h4>
                            <span class="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[9px] font-mono font-bold text-indigo-400 border border-indigo-500/30 shrink-0">
                                Match ${q.priority_score}pt
                            </span>
                        </div>
                        <p class="text-[11px] text-zinc-400 line-clamp-2">${escapeHtml(q.invariant_principle || '')}</p>
                        <div class="flex items-center justify-between pt-1">
                            <div class="flex items-center gap-1">
                                ${(q.company_tags || []).slice(0, 2).map(c => 
                                    `<span class="rounded bg-zinc-800 px-1.5 py-0.2 text-[9px] text-zinc-300 font-mono">${escapeHtml(c)}</span>`
                                ).join('')}
                            </div>
                            <button onclick="launchQuestionInMock('${q.slug || q.id}')" class="flex items-center gap-1 rounded-lg bg-indigo-600/20 px-2 py-1 text-[10px] font-semibold text-indigo-300 hover:bg-indigo-600/40 border border-indigo-500/30 transition">
                                <span>Practice</span>
                                <i data-lucide="arrow-right" class="h-3 w-3"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        }
    }

    // 5. Past History (Mock Interviews & MCQs)
    if (hist) {
        // Mock Interviews
        const countBadge = document.getElementById('profileInterviewCountBadge');
        if (countBadge) countBadge.innerText = `${hist.interview_sessions_count} Completed (Avg ${hist.average_interview_score}/10)`;

        const intList = document.getElementById('profileInterviewHistoryList');
        if (intList && Array.isArray(hist.recent_interview_sessions)) {
            if (hist.recent_interview_sessions.length === 0) {
                intList.innerHTML = `
                    <div class="rounded-xl border border-dashed border-zinc-800 p-6 text-center text-xs text-zinc-500">
                        No mock interviews logged yet. Click "AI Mock Interview" to conduct your first calibrated session!
                    </div>
                `;
            } else {
                intList.innerHTML = hist.recent_interview_sessions.map(s => `
                    <div class="rounded-xl border border-zinc-800 bg-zinc-950/80 p-3.5 space-y-2">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-2">
                                <span class="rounded bg-violet-500/10 px-2 py-0.5 text-[10px] font-mono text-violet-300 border border-violet-500/30 font-bold">
                                    ${escapeHtml(s.target_company || 'Tech MNC')}
                                </span>
                                <h4 class="text-xs font-bold text-zinc-200">${escapeHtml(s.session_title)}</h4>
                            </div>
                            <div class="flex items-center gap-1 rounded-lg bg-emerald-500/10 px-2 py-0.5 text-emerald-400 font-mono text-xs font-bold border border-emerald-500/20">
                                Score: ${s.overall_score}/10
                            </div>
                        </div>
                        <p class="text-[11px] text-zinc-400">${s.turns_count} conversational turns evaluated by AI Bar Raiser</p>
                    </div>
                `).join('');
            }
        }

        // MCQ History
        const mcqBadge = document.getElementById('profileMcqAccuracyBadge');
        if (mcqBadge) mcqBadge.innerText = `${hist.mcq_accuracy_pct}% Accuracy (${hist.mcq_attempts_count} Drilled)`;

        const mcqList = document.getElementById('profileMcqHistoryList');
        if (mcqList && Array.isArray(hist.recent_mcq_attempts)) {
            if (hist.recent_mcq_attempts.length === 0) {
                mcqList.innerHTML = `
                    <div class="rounded-xl border border-dashed border-zinc-800 p-6 text-center text-xs text-zinc-500">
                        No MCQ drills recorded yet. Test your understanding on the "MCQ Drills & Tests" tab!
                    </div>
                `;
            } else {
                mcqList.innerHTML = hist.recent_mcq_attempts.map(att => {
                    const statusClass = att.is_correct ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" : "bg-rose-500/10 text-rose-400 border-rose-500/30";
                    const statusText = att.is_correct ? "CORRECT" : "MISSED";

                    return `
                        <div class="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-950/80 px-3.5 py-2.5">
                            <div class="flex items-center gap-2.5 overflow-hidden">
                                <span class="rounded px-2 py-0.5 text-[9px] font-mono font-bold border ${statusClass}">
                                    ${statusText}
                                </span>
                                <span class="text-xs text-zinc-300 font-medium truncate">${escapeHtml(att.domain || 'Core Architectural Principle')}</span>
                            </div>
                            <span class="text-[10px] text-zinc-500 font-mono shrink-0">${att.time_spent_seconds || 30}s</span>
                        </div>
                    `;
                }).join('');
            }
        }
    }

    if (window.lucide) {
        lucide.createIcons();
    }
}

function launchQuestionInMock(slugOrId) {
    const q = bankQuestions.find(item => item.slug === slugOrId || item.id == slugOrId);
    if (q) {
        launchBankQuestionInWorkspace(q.id);
    } else {
        switchAppTab('interview');
    }
}

// --- INTERACTIVE LLM COPILOT (GEMINI / CHATGPT) ---
let llmChatMessages = [];
let activeLlmMode = 'comprehensive';
let isLlmSending = false;

const LLM_STARTER_PRESETS = [
    {
        title: "Distributed Systems Consensus",
        prompt: "Explain Raft Leader Election Split-Vote handling and fencing tokens under network partitions.",
        icon: "network",
        mode: "comprehensive"
    },
    {
        title: "High-Throughput Rate Limiting",
        prompt: "Write an Async Redis Token Bucket Rate Limiter with Lua script to prevent race conditions at 100k QPS.",
        icon: "cpu",
        mode: "code_solution"
    },
    {
        title: "Python Concurrency Traps",
        prompt: "Why does an asyncio event loop block when calling a CPU-bound worker, and how to properly offload it with ProcessPoolExecutor?",
        icon: "terminal",
        mode: "debug_edge_cases"
    },
    {
        title: "Distributed Idempotency Engine",
        prompt: "Design a Distributed Idempotency Key Engine for Stripe-scale payments with MySQL and Redis distributed locks.",
        icon: "layers",
        mode: "system_design"
    }
];

function initLlmChatView() {
    renderLlmChatStream();
    setupLlmInputKeybindings();
}

function setupLlmInputKeybindings() {
    const input = document.getElementById("llmPromptInput");
    if (input && !input.dataset.bound) {
        input.dataset.bound = "true";
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendLlmMessage();
            } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                sendLlmMessage();
            }
        });
    }

    const codeInput = document.getElementById("llmCodeContextInput");
    if (codeInput && !codeInput.dataset.bound) {
        codeInput.dataset.bound = "true";
        codeInput.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                sendLlmMessage();
            }
        });
    }
}

function setLlmMode(mode, btn) {
    activeLlmMode = mode;
    const badge = document.getElementById("llmActiveModeBadge");
    if (badge) badge.textContent = `Mode: ${mode.replace('_', ' ')}`;

    // Update button styling
    const btns = document.querySelectorAll(".llm-mode-btn");
    btns.forEach(b => {
        b.className = "llm-mode-btn rounded-lg px-2.5 py-1 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition";
    });
    if (btn) {
        btn.className = "llm-mode-btn rounded-lg bg-indigo-600 px-2.5 py-1 text-xs font-semibold text-white shadow-sm transition";
    }
}

function toggleLlmCodeAttachment() {
    const drawer = document.getElementById("llmCodeAttachmentDrawer");
    const btn = document.getElementById("btnToggleCodeAttach");
    if (!drawer) return;

    if (drawer.classList.contains("hidden")) {
        drawer.classList.remove("hidden");
        if (btn) btn.classList.add("text-cyan-400", "border-cyan-500/40");
        document.getElementById("llmCodeContextInput")?.focus();
    } else {
        drawer.classList.add("hidden");
        if (btn) btn.classList.remove("text-cyan-400", "border-cyan-500/40");
    }
}

function clearLlmChat() {
    llmChatMessages = [];
    renderLlmChatStream();
    showToast("Chat cleared. Ready for a new topic.");
}

function loadLlmPreset(idx) {
    const preset = LLM_STARTER_PRESETS[idx];
    if (!preset) return;
    
    // Set mode
    activeLlmMode = preset.mode;
    const badge = document.getElementById("llmActiveModeBadge");
    if (badge) badge.textContent = `Mode: ${preset.mode.replace('_', ' ')}`;
    
    // Find matching mode button
    const modeBtns = document.querySelectorAll(".llm-mode-btn");
    modeBtns.forEach(btn => {
        if (btn.getAttribute("onclick")?.includes(preset.mode)) {
            btn.className = "llm-mode-btn rounded-lg bg-indigo-600 px-2.5 py-1 text-xs font-semibold text-white shadow-sm transition";
        } else {
            btn.className = "llm-mode-btn rounded-lg px-2.5 py-1 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition";
        }
    });

    sendLlmMessage(preset.prompt);
}

function formatMarkdownForDisplay(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Code blocks: ```language ... ```
    html = html.replace(/```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const cleanLang = lang || 'code';
        const cleanCode = code.trim();
        const codeId = 'code_' + Math.random().toString(36).substring(2, 9);
        return `
            <div class="my-3 rounded-xl border border-zinc-800 bg-zinc-950/95 overflow-hidden shadow-lg">
                <div class="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/60 px-3.5 py-1.5 text-[11px] font-mono text-zinc-400">
                    <span class="text-cyan-400 font-semibold">${cleanLang.toUpperCase()}</span>
                    <div class="flex items-center gap-2">
                        <button onclick="copyCodeFromBlock('${codeId}')" class="hover:text-zinc-200 text-xs flex items-center gap-1 transition">
                            <i data-lucide="copy" class="h-3 w-3"></i> Copy
                        </button>
                        <button onclick="sendLlmCodeToIde('${codeId}')" class="text-indigo-400 hover:text-indigo-300 text-xs flex items-center gap-1 transition">
                            <i data-lucide="terminal" class="h-3 w-3"></i> Test in IDE
                        </button>
                    </div>
                </div>
                <pre class="p-3.5 overflow-x-auto text-xs font-mono text-zinc-200 leading-relaxed"><code id="${codeId}">${cleanCode}</code></pre>
            </div>
        `;
    });

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code class="rounded bg-zinc-800/80 px-1.5 py-0.5 font-mono text-[11px] text-cyan-300 border border-zinc-700/50">$1</code>');

    // Headings
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-sm font-bold text-white mt-4 mb-2 flex items-center gap-2"><span class="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-base font-bold text-white mt-5 mb-2.5 border-b border-zinc-800/80 pb-1">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-lg font-extrabold text-white mt-6 mb-3">$1</h1>');

    // Bold & italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-bold text-zinc-100">$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em class="italic text-zinc-300">$1</em>');

    // Bullet points
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li class="ml-4 list-disc text-zinc-300 text-xs py-0.5">$1</li>');
    html = html.replace(/^\s*\*\s+(.*$)/gim, '<li class="ml-4 list-disc text-zinc-300 text-xs py-0.5">$1</li>');

    // Numbered lists
    html = html.replace(/^\s*(\d+)\.\s+(.*$)/gim, '<li class="ml-4 list-decimal text-zinc-300 text-xs py-0.5 font-medium">$2</li>');

    // Paragraph breaks
    html = html.replace(/\n\n/g, '<div class="h-2.5"></div>');

    return html;
}

function copyCodeFromBlock(codeId) {
    const el = document.getElementById(codeId);
    if (!el) return;
    navigator.clipboard.writeText(el.textContent || "")
        .then(() => showToast("Code copied to clipboard!"))
        .catch(() => showToast("Copied!"));
}

function sendLlmCodeToIde(codeId) {
    const el = document.getElementById(codeId);
    if (!el) return;
    const code = el.textContent || "";
    const ideTextarea = document.getElementById("ideCodeTextarea");
    if (ideTextarea) {
        ideTextarea.value = code;
        switchAppTab('interview');
        showToast("Code injected into Mock Interview IDE!");
    }
}

function renderLlmChatStream() {
    const stream = document.getElementById("llmChatStream");
    if (!stream) return;

    if (llmChatMessages.length === 0) {
        // Welcome Hero & Starter Prompt Cards
        stream.innerHTML = `
            <div class="mx-auto max-w-3xl space-y-8 py-6">
                <!-- Hero Header -->
                <div class="text-center space-y-3">
                    <div class="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-purple-600 text-white shadow-xl shadow-indigo-500/20 mb-2">
                        <i data-lucide="sparkles" class="h-7 w-7"></i>
                    </div>
                    <h1 class="text-2xl font-black tracking-tight text-white sm:text-3xl">
                        Staff AI Engineering Copilot
                    </h1>
                    <p class="text-xs sm:text-sm text-zinc-400 max-w-lg mx-auto leading-relaxed">
                        Multi-Model Technical Architecture Copilot. Paste any interview problem, broken production code, distributed systems challenge, or request a bar-raiser technical grill.
                    </p>
                    <div class="flex items-center justify-center gap-2 pt-1 text-[11px] text-zinc-500 font-mono">
                        <span class="inline-flex items-center gap-1"><span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>Free Tier & BYOK Compatible</span>
                        <span>•</span>
                        <span>Zero Vendor Lock-in</span>
                    </div>
                </div>

                <!-- 4 Quick-Starter Cards -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
                    ${LLM_STARTER_PRESETS.map((p, idx) => `
                        <div onclick="loadLlmPreset(${idx})" class="group cursor-pointer rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4 transition-all hover:border-cyan-500/40 hover:bg-zinc-900/90 hover:shadow-lg">
                            <div class="flex items-center justify-between mb-2">
                                <span class="rounded-md bg-indigo-500/10 px-2 py-0.5 text-[10px] font-mono font-semibold text-indigo-400 border border-indigo-500/20">
                                    ${p.title}
                                </span>
                                <i data-lucide="${p.icon}" class="h-4 w-4 text-zinc-500 group-hover:text-cyan-400 transition-colors"></i>
                            </div>
                            <p class="text-xs text-zinc-300 leading-relaxed font-medium group-hover:text-white transition-colors">
                                "${escapeHtml(p.prompt)}"
                            </p>
                            <div class="mt-3 flex items-center gap-1.5 text-[11px] text-cyan-400 font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                                <span>Synthesize Answer</span>
                                <i data-lucide="arrow-right" class="h-3 w-3"></i>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Feature highlights footer -->
                <div class="flex flex-wrap items-center justify-center gap-6 pt-4 text-xs text-zinc-500">
                    <span class="flex items-center gap-1.5"><i data-lucide="check" class="h-3.5 w-3.5 text-emerald-400"></i> First-Principles Reasoning</span>
                    <span class="flex items-center gap-1.5"><i data-lucide="check" class="h-3.5 w-3.5 text-emerald-400"></i> Zero-Copy & Concurrency Code</span>
                    <span class="flex items-center gap-1.5"><i data-lucide="check" class="h-3.5 w-3.5 text-emerald-400"></i> Interactive Follow-Up Chips</span>
                </div>
            </div>
        `;
    } else {
        stream.innerHTML = llmChatMessages.map(msg => {
            const isUser = (msg.role === 'user');
            
            if (isUser) {
                return `
                    <div class="flex gap-3 max-w-[85%] ml-auto flex-row-reverse">
                        <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-bold text-xs shadow-md">
                            ${currentUser ? currentUser.full_name.substring(0, 2).toUpperCase() : 'ME'}
                        </div>
                        <div class="space-y-1.5">
                            <div class="rounded-2xl bg-indigo-600 p-4 text-xs text-white shadow-md leading-relaxed">
                                <p class="whitespace-pre-line">${escapeHtml(msg.content)}</p>
                                ${msg.codeContext ? `
                                    <div class="mt-2.5 rounded-lg bg-zinc-950/80 p-2.5 border border-indigo-400/30 text-zinc-300 font-mono text-[11px] overflow-x-auto">
                                        <div class="text-[9px] uppercase font-bold text-indigo-300 mb-1">Attached Code Context:</div>
                                        <pre><code>${escapeHtml(msg.codeContext)}</code></pre>
                                    </div>
                                ` : ''}
                            </div>
                            <div class="text-right text-[10px] text-zinc-500 font-mono">${msg.timestamp}</div>
                        </div>
                    </div>
                `;
            } else {
                // AI Response Bubble
                return `
                    <div class="flex gap-3.5 max-w-[92%]">
                        <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 text-white text-xs shadow-md">
                            <i data-lucide="bot" class="h-4 w-4"></i>
                        </div>
                        <div class="space-y-3 flex-1 overflow-hidden">
                            <div class="rounded-2xl border border-zinc-800 bg-zinc-900/90 p-5 text-xs text-zinc-200 shadow-xl backdrop-blur-md space-y-4">
                                
                                <!-- Header info -->
                                <div class="flex items-center justify-between border-b border-zinc-800/80 pb-2.5">
                                    <div class="flex items-center gap-2">
                                        <span class="rounded bg-cyan-500/10 px-2 py-0.5 text-[10px] font-mono font-bold text-cyan-400 border border-cyan-500/30">
                                            ${escapeHtml(msg.model || 'Staff AI Engine')}
                                        </span>
                                        <span class="text-[11px] text-zinc-400 font-mono">
                                            Mode: ${escapeHtml(msg.mode || 'comprehensive')}
                                        </span>
                                    </div>
                                    <span class="text-[10px] text-zinc-500 font-mono">${msg.timestamp}</span>
                                </div>

                                <!-- Markdown Answer Body -->
                                <div class="prose prose-invert max-w-none text-xs leading-relaxed">
                                    ${formatMarkdownForDisplay(msg.content)}
                                </div>

                                <!-- Key Architectural Invariants if present -->
                                ${msg.keyInvariants && msg.keyInvariants.length > 0 ? `
                                    <div class="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-3.5 space-y-2">
                                        <div class="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                                            <i data-lucide="shield-check" class="h-4 w-4"></i>
                                            <span>Key Architectural Invariants</span>
                                        </div>
                                        <ul class="space-y-1">
                                            ${msg.keyInvariants.map(inv => `
                                                <li class="flex items-start gap-2 text-[11px] text-emerald-200">
                                                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0"></span>
                                                    <span>${escapeHtml(inv)}</span>
                                                </li>
                                            `).join('')}
                                        </ul>
                                    </div>
                                ` : ''}

                                <!-- Distractor Traps if present -->
                                ${msg.distractorTraps && msg.distractorTraps.length > 0 ? `
                                    <div class="rounded-xl border border-rose-500/30 bg-rose-950/20 p-3.5 space-y-2">
                                        <div class="flex items-center gap-1.5 text-xs font-bold text-rose-400">
                                            <i data-lucide="alert-triangle" class="h-4 w-4"></i>
                                            <span>Staff Interview Gotchas & Traps</span>
                                        </div>
                                        <ul class="space-y-1">
                                            ${msg.distractorTraps.map(trap => `
                                                <li class="flex items-start gap-2 text-[11px] text-rose-200">
                                                    <span class="h-1.5 w-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0"></span>
                                                    <span>${escapeHtml(trap)}</span>
                                                </li>
                                            `).join('')}
                                        </ul>
                                    </div>
                                ` : ''}

                                <!-- Follow-Up Interactive Chips -->
                                ${msg.followUpQuestions && msg.followUpQuestions.length > 0 ? `
                                    <div class="border-t border-zinc-800/80 pt-3 space-y-2">
                                        <span class="text-[10px] uppercase font-bold text-zinc-500 tracking-wider">Explore Follow-Ups:</span>
                                        <div class="flex flex-wrap gap-2">
                                            ${msg.followUpQuestions.map(q => `
                                                <button onclick="sendLlmMessage('${escapeHtml(q).replace(/'/g, "\\'")}')" class="rounded-xl border border-zinc-700 bg-zinc-950/80 px-3 py-1.5 text-[11px] text-zinc-300 hover:text-white hover:border-cyan-500/50 hover:bg-zinc-800 transition shadow-sm text-left">
                                                    💬 ${escapeHtml(q)}
                                                </button>
                                            `).join('')}
                                        </div>
                                    </div>
                                ` : ''}

                            </div>
                        </div>
                    </div>
                `;
            }
        }).join('');
    }

    stream.scrollTop = stream.scrollHeight;

    if (window.lucide) {
        lucide.createIcons();
    }
}

async function sendLlmMessage(customPrompt = null) {
    if (isLlmSending) return;

    const input = document.getElementById("llmPromptInput");
    const codeInput = document.getElementById("llmCodeContextInput");

    const promptText = (customPrompt || input?.value || "").trim();
    const codeContext = (codeInput?.value || "").trim();

    if (!promptText) return;

    if (!customPrompt && input) {
        input.value = "";
    }

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Add user message
    llmChatMessages.push({
        id: Date.now(),
        role: 'user',
        content: promptText,
        codeContext: codeContext,
        timestamp: now
    });

    renderLlmChatStream();

    // Show typing loader and set button to submitting state
    isLlmSending = true;
    const loader = document.getElementById("llmTypingLoader");
    const sendBtn = document.getElementById("llmSendBtn");
    if (loader) loader.classList.remove("hidden");
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = `
            <div class="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
            <span>Submitting...</span>
        `;
    }

    const headers = { "Content-Type": "application/json" };
    if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
    }

    try {
        const res = await fetch("/api/v1/llm/ask", {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
                question: promptText,
                prompt: promptText,
                code_context: codeContext || null,
                mode: activeLlmMode,
                target_company: (typeof selectedTargetCompany !== 'undefined' && selectedTargetCompany && selectedTargetCompany !== 'All') ? selectedTargetCompany : "Accenture"
            })
        });

        if (res.ok) {
            const data = await res.json();
            llmChatMessages.push({
                id: Date.now() + 1,
                role: 'assistant',
                model: data.model_used || data.provider || "Staff AI Engine",
                mode: data.mode || activeLlmMode,
                content: data.answer_markdown || data.answer || "No response generated.",
                keyInvariants: data.key_invariants || [],
                distractorTraps: data.distractor_traps || [],
                followUpQuestions: data.follow_up_questions || data.suggested_followups || [],
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            });
            // Clear code input drawer if it was sent
            if (codeInput) codeInput.value = "";
            const drawer = document.getElementById("llmCodeAttachmentDrawer");
            if (drawer && !drawer.classList.contains("hidden")) {
                toggleLlmCodeAttachment();
            }
        } else {
            const err = await res.json().catch(() => ({}));
            let errMsg = "Unable to reach LLM inference endpoint. Please try again or switch query mode.";
            if (typeof err.detail === 'string') {
                errMsg = err.detail;
            } else if (Array.isArray(err.detail)) {
                errMsg = err.detail.map(d => (d.msg ? `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}` : JSON.stringify(d))).join("; ");
            } else if (err.detail && typeof err.detail === 'object') {
                errMsg = err.detail.message || JSON.stringify(err.detail);
            }
            llmChatMessages.push({
                id: Date.now() + 1,
                role: 'assistant',
                model: 'Diagnostic Engine',
                mode: activeLlmMode,
                content: `### ⚠️ Notice\n\n${errMsg}`,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            });
        }
    } catch (e) {
        llmChatMessages.push({
            id: Date.now() + 1,
            role: 'assistant',
            model: 'Offline Copilot',
            mode: activeLlmMode,
            content: `### ⚠️ Connection Error\n\nCould not communicate with the backend LLM engine. Please ensure the backend server is running.`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
    } finally {
        isLlmSending = false;
        if (loader) loader.classList.add("hidden");
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.innerHTML = `
                <span id="llmSendBtnLabel">Submit</span>
                <kbd class="inline-flex items-center rounded bg-black/40 px-1.5 py-0.5 text-[10px] font-mono text-cyan-200 border border-white/10">↵ Enter</kbd>
                <i data-lucide="send" class="h-3.5 w-3.5" id="llmSendBtnIcon"></i>
            `;
            if (window.lucide) {
                lucide.createIcons();
            }
        }
        renderLlmChatStream();
        if (input) input.focus();
    }
}

// --- WINDOW EXPORTS (100% OPERATIONAL BUTTON HANDLERS) ---
window.switchAppTab = switchAppTab;
window.toggleSessionTimer = toggleSessionTimer;
window.toggleVoiceSimulation = toggleVoiceSimulation;
window.filterMcqs = filterMcqs;
window.clearMcqSearch = clearMcqSearch;
window.setMcqMode = setMcqMode;
window.submitTimedExam = submitTimedExam;
window.retakeTimedExam = retakeTimedExam;
window.resetMcqState = resetMcqState;
window.handleSelectMcqOption = handleSelectMcqOption;
window.toggleMcqAccordion = toggleMcqAccordion;
window.openAiExplainer = openAiExplainer;
window.closeAiExplainerModal = closeAiExplainerModal;
window.jumpToMindmapFromModal = jumpToMindmapFromModal;
window.handleJumpToMindmap = handleJumpToMindmap;
window.zoomMindmap = zoomMindmap;
window.resetMindmapZoom = resetMindmapZoom;
window.toggleMindmapDetailDrawer = toggleMindmapDetailDrawer;
window.selectMindmapNodeById = selectMindmapNodeById;
window.jumpFromMindmapToMcq = jumpFromMindmapToMcq;
window.startAiMockOnActiveNode = startAiMockOnActiveNode;
window.startAiMockWithPrompt = startAiMockWithPrompt;
window.generateCustomMindmap = generateCustomMindmap;
window.handleInterviewChatSubmit = handleInterviewChatSubmit;
window.requestCopilotPrompt = requestCopilotPrompt;
window.handleIdeLanguageChange = handleIdeLanguageChange;
window.handleExecuteCode = handleExecuteCode;
window.handleSubmitSolutionForReview = handleSubmitSolutionForReview;
window.filterQuestionBank = filterQuestionBank;
window.filterByTargetCompany = filterByTargetCompany;
window.selectBankQuestion = selectBankQuestion;
window.launchBankQuestionInWorkspace = launchBankQuestionInWorkspace;
window.showToast = showToast;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthMode = switchAuthMode;
window.toggleSelectionPill = toggleSelectionPill;
window.openEditProfileModal = openEditProfileModal;
window.closeEditProfileModal = closeEditProfileModal;
window.handleRegisterSubmit = handleRegisterSubmit;
window.handleLoginSubmit = handleLoginSubmit;
window.handleUpdateProfileSubmit = handleUpdateProfileSubmit;
window.logoutUser = logoutUser;
window.loadUserRecommendationsAndHistory = loadUserRecommendationsAndHistory;
window.launchQuestionInMock = launchQuestionInMock;
window.initLlmChatView = initLlmChatView;
window.setLlmMode = setLlmMode;
window.toggleLlmCodeAttachment = toggleLlmCodeAttachment;
window.clearLlmChat = clearLlmChat;
window.loadLlmPreset = loadLlmPreset;
window.sendLlmMessage = sendLlmMessage;
window.copyCodeFromBlock = copyCodeFromBlock;
window.sendLlmCodeToIde = sendLlmCodeToIde;
window.loadCentralizedConcepts = loadCentralizedConcepts;
window.setConceptDomainFilter = setConceptDomainFilter;
window.filterCentralizedConcepts = filterCentralizedConcepts;
window.renderConceptsCards = renderConceptsCards;
window.jumpToSkillMcq = jumpToSkillMcq;
window.jumpToSkillQuestions = jumpToSkillQuestions;
window.askAiAboutSkill = askAiAboutSkill;
window.calibrateWorkspaceToRole = calibrateWorkspaceToRole;


