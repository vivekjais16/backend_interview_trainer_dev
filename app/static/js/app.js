// AI Python Backend & MNC Interview Trainer - Interactive Jupyter Engine
let currentQuestion = null;
let currentExperienceLevel = "mid";
let currentDomainFilter = "";
let activeSessionId = null;
let currentMindmapSlug = "python-internals";

document.addEventListener("DOMContentLoaded", async () => {
    // Initialize Mermaid in Light Theme
    if (window.mermaid) {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'neutral',
            themeVariables: {
                darkMode: false,
                background: '#ffffff',
                primaryColor: '#e0e7ff',
                primaryTextColor: '#0f172a',
                primaryBorderColor: '#6366f1',
                lineColor: '#4f46e5',
                secondaryColor: '#ecfdf5',
                secondaryTextColor: '#065f46',
                tertiaryColor: '#fffbeb'
            }
        });
    }

    setupEventListeners();
    await initInterviewSession();
    await loadQuestions();
    await loadMindmaps();
    await loadSQLSchemas();
});

function setupEventListeners() {
    // Experience Level Switcher Buttons
    document.querySelectorAll(".exp-selector-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            document.querySelectorAll(".exp-selector-btn").forEach(b => {
                b.className = "exp-selector-btn px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-white/60 transition";
            });
            const target = e.currentTarget;
            target.className = "exp-selector-btn px-3.5 py-1.5 rounded-lg text-xs font-bold bg-white text-indigo-600 shadow-xs border border-slate-200/80 transition";
            currentExperienceLevel = target.dataset.level;
            
            await initInterviewSession();
            await loadQuestions();
        });
    });

    // Search bar
    document.getElementById("questionSearchInput")?.addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase();
        document.querySelectorAll("#questionList > div").forEach(item => {
            const text = item.innerText.toLowerCase();
            item.style.display = text.includes(term) ? "flex" : "none";
        });
    });

    // Run Python Code Shortcut (Ctrl+Enter / Cmd+Enter)
    document.getElementById("pythonCodeInput")?.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            runPythonCode();
        }
    });

    // Run SQL Shortcut
    document.getElementById("sqlQueryInput")?.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            runSQLCode();
        }
    });
}

function filterByDomain(domain) {
    currentDomainFilter = domain;
    
    // Update chip buttons
    document.querySelectorAll("#domainChips button").forEach(b => {
        b.className = "px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 shrink-0 font-medium transition";
    });
    if (window.event && window.event.currentTarget) {
        window.event.currentTarget.className = "px-2.5 py-1 rounded-lg bg-indigo-600 text-white shrink-0 font-bold shadow-2xs transition";
    }

    // Highlight roadmap steps
    document.querySelectorAll(".stage-step-btn").forEach(s => {
        s.className = "stage-step-btn px-3 py-1 rounded-lg border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-300 hover:text-indigo-600 font-medium transition flex items-center gap-1.5";
    });

    loadQuestions();
}

async function initInterviewSession() {
    try {
        const res = await fetch("/api/v1/interview/sessions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_title: `MNC Prep - ${currentExperienceLevel.toUpperCase()} Track`,
                experience_level: currentExperienceLevel,
                target_company: "Top Tech MNC"
            })
        });
        const data = await res.json();
        activeSessionId = data.id;
    } catch (err) {
        console.error("Failed to create interview session:", err);
    }
}

async function loadQuestions() {
    const listEl = document.getElementById("questionList");
    if (!listEl) return;

    listEl.innerHTML = `<div class="p-6 text-slate-400 text-xs font-medium animate-pulse text-center">Loading ${currentExperienceLevel.toUpperCase()} questions...</div>`;

    try {
        let url = `/api/v1/questions?experience_level=${currentExperienceLevel}`;
        if (currentDomainFilter) {
            url += `&category=${currentDomainFilter}`;
        }
        const res = await fetch(url);
        const questions = await res.json();

        if (!questions.length) {
            listEl.innerHTML = `
                <div class="p-8 text-center text-slate-500 text-xs space-y-2">
                    <p class="font-semibold text-slate-700">No questions found for this filter.</p>
                    <p>Try clicking <button onclick="filterByDomain('')" class="text-indigo-600 font-bold underline">Show All</button> to see all available questions.</p>
                </div>
            `;
            return;
        }

        listEl.innerHTML = questions.map((q, idx) => `
            <div onclick="selectQuestion(${q.id})" id="q-card-${q.id}" class="p-4 hover:bg-indigo-50/50 cursor-pointer transition flex flex-col gap-1.5 ${idx === 0 ? 'bg-indigo-50/70 border-l-4 border-l-indigo-600' : 'border-l-4 border-l-transparent'}">
                <div class="flex items-center justify-between">
                    <span class="text-[11px] font-bold px-2 py-0.5 rounded-full ${getDifficultyClass(q.difficulty)}">${q.difficulty.toUpperCase()}</span>
                    <span class="text-[11px] text-slate-500 font-mono font-medium">${q.min_exp_years}-${q.max_exp_years} YOE</span>
                </div>
                <h4 class="text-xs font-bold text-slate-800 line-clamp-2 leading-relaxed">${q.title}</h4>
                <div class="flex flex-wrap gap-1 mt-1">
                    <span class="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md border border-indigo-200/80 font-semibold">${formatCategory(q.category)}</span>
                    ${(q.company_tags || []).slice(0, 2).map(tag => `<span class="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-medium">${tag}</span>`).join('')}
                </div>
            </div>
        `).join('');

        if (questions.length > 0) {
            await selectQuestion(questions[0].id);
        }
    } catch (err) {
        listEl.innerHTML = `<div class="p-4 text-rose-600 text-xs font-medium">Error loading questions: ${err.message}</div>`;
    }
}

async function selectQuestion(qId) {
    try {
        // Highlight active card
        document.querySelectorAll("#questionList > div").forEach(card => {
            card.classList.remove("bg-indigo-50/70", "border-l-indigo-600");
            card.classList.add("border-l-transparent");
        });
        const activeCard = document.getElementById(`q-card-${qId}`);
        if (activeCard) {
            activeCard.classList.add("bg-indigo-50/70", "border-l-indigo-600");
            activeCard.classList.remove("border-l-transparent");
        }

        const res = await fetch(`/api/v1/questions/${qId}`);
        currentQuestion = await res.json();
        renderQuestionDetail(currentQuestion);
    } catch (err) {
        console.error("Error loading question:", err);
    }
}

function renderQuestionDetail(q) {
    document.getElementById("qTitle").innerText = q.title;
    document.getElementById("qScenario").innerHTML = formatMarkdown(q.scenario_text);
    
    // Badges
    const badgeContainer = document.getElementById("qBadges");
    badgeContainer.innerHTML = `
        <span class="px-3 py-1 text-xs rounded-full font-bold ${getDifficultyClass(q.difficulty)}">${q.difficulty.toUpperCase()}</span>
        <span class="px-3 py-1 text-xs rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold font-mono">${formatCategory(q.category)}</span>
        <span class="px-3 py-1 text-xs rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-semibold font-mono">Frequency: ${q.frequency_score}%</span>
        ${(q.company_tags || []).map(t => `<span class="px-2.5 py-1 text-xs bg-slate-100 text-slate-700 rounded-lg border border-slate-200 font-medium">🏢 ${t}</span>`).join('')}
    `;

    // Theory & Gotchas
    if (q.theory_explanation) {
        document.getElementById("qTheoryCard").classList.remove("hidden");
        document.getElementById("qTheoryText").innerHTML = formatMarkdown(q.theory_explanation);
    } else {
        document.getElementById("qTheoryCard").classList.add("hidden");
    }

    // Common Traps
    const trapsList = document.getElementById("qTrapsList");
    if (trapsList && q.common_traps) {
        trapsList.innerHTML = q.common_traps.map(trap => `
            <li class="text-xs text-amber-800 leading-relaxed flex items-start gap-2">
                <span class="text-amber-500 font-bold shrink-0">⚠️</span>
                <span>${trap}</span>
            </li>
        `).join('');
    }

    // Auto-focus the relevant sandbox tab based on question capabilities
    if (q.has_redis_sandbox) {
        switchSandboxTab("redis");
        document.getElementById("redisCommandInput").value = q.starter_redis || "SET mykey 'val'\nGET mykey";
        document.getElementById("redisOutputTerminal").innerText = "// Click 'Execute Redis CLI' to test in-memory commands";
    } else if (q.has_nosql_sandbox) {
        switchSandboxTab("nosql");
        document.getElementById("nosqlQueryInput").value = q.starter_nosql || "db.orders.find({})";
        document.getElementById("nosqlOutputTerminal").innerText = "// Click 'Run Mongo Query' to execute aggregation pipeline";
    } else if (q.has_sql_sandbox && !q.has_python_sandbox) {
        switchSandboxTab("sql");
        document.getElementById("sqlQueryInput").value = q.starter_sql || "-- Write your SQL query here\nSELECT 1;";
        document.getElementById("sqlSchemaSelect").value = q.sql_schema || "ecommerce";
        document.getElementById("sqlOutputContainer").innerHTML = `<div class="text-xs text-slate-500 font-mono p-4">Click 'Execute SQL' to run query with execution plan.</div>`;
    } else {
        switchSandboxTab("python");
        document.getElementById("pythonCodeInput").value = q.starter_code || "# Write your Python solution here\n";
        document.getElementById("pyOutputTerminal").innerText = "// Click 'Run Python (Ctrl+Enter)' to test execution";
    }

    // Prepopulate SQL if question supports it
    if (q.has_sql_sandbox && document.getElementById("sqlQueryInput")) {
        document.getElementById("sqlQueryInput").value = q.starter_sql || "-- Write your SQL query here\nSELECT 1;";
        if (q.sql_schema) document.getElementById("sqlSchemaSelect").value = q.sql_schema;
    }

    // Reset AI Feedback area
    document.getElementById("aiEvaluationCard").classList.add("hidden");
    document.getElementById("candidateResponseInput").value = "";
}

async function runPythonCode() {
    const code = document.getElementById("pythonCodeInput").value;
    const terminal = document.getElementById("pyOutputTerminal");
    const runBtn = document.getElementById("runPythonBtn");

    runBtn.disabled = true;
    runBtn.innerHTML = `<span class="animate-spin inline-block mr-1">⌛</span> Running...`;
    terminal.innerText = "Executing sandboxed code...";

    try {
        const res = await fetch("/api/v1/sandbox/python", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                code: code,
                question_id: currentQuestion ? currentQuestion.id : null
            })
        });
        const result = await res.json();

        let out = "";
        if (result.stdout) out += result.stdout + "\n";
        if (result.return_value) out += `[Return Value]: ${result.return_value}\n`;
        if (result.stderr) out += `\n[STDERR / Exception]:\n${result.stderr}\n`;
        out += `\n--------------------------------------------\n`;
        out += `Status: ${result.success ? 'SUCCESS' : 'FAILED'} | Execution Time: ${result.execution_time_ms} ms`;

        terminal.innerText = out;
        terminal.className = result.success ? "text-emerald-400 font-mono text-xs whitespace-pre-wrap" : "text-rose-400 font-mono text-xs whitespace-pre-wrap";
    } catch (err) {
        terminal.innerText = `Network/Execution Error: ${err.message}`;
        terminal.className = "text-rose-400 font-mono text-xs";
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `<span>▶</span> Run Python <kbd class="ml-1 text-[10px] bg-emerald-800/60 px-1.5 py-0.5 rounded text-white font-mono">Ctrl+Enter</kbd>`;
    }
}

async function runSQLCode() {
    const query = document.getElementById("sqlQueryInput").value;
    const schema = document.getElementById("sqlSchemaSelect").value;
    const container = document.getElementById("sqlOutputContainer");
    const runBtn = document.getElementById("runSqlBtn");

    runBtn.disabled = true;
    runBtn.innerHTML = `<span class="animate-spin inline-block mr-1">⌛</span> Running...`;
    container.innerHTML = `<div class="p-4 text-xs font-mono text-slate-500">Executing SQL in isolated sandbox...</div>`;

    try {
        const res = await fetch("/api/v1/sandbox/sql", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: query,
                schema_name: schema,
                include_explain: true,
                question_id: currentQuestion ? currentQuestion.id : null
            })
        });
        const result = await res.json();

        if (!result.success) {
            container.innerHTML = `
                <div class="p-4 bg-rose-50 border border-rose-200 text-rose-800 font-mono text-xs">
                    <p class="font-bold mb-1">❌ SQL Syntax / Execution Error:</p>
                    <pre class="whitespace-pre-wrap">${result.error}</pre>
                </div>
            `;
            return;
        }

        let html = `
            <div class="flex items-center justify-between p-3 bg-slate-50 border-b border-slate-200 text-xs">
                <span class="text-emerald-700 font-bold">✓ ${result.row_count} rows returned</span>
                <span class="text-slate-500 font-mono font-medium">Execution Time: ${result.execution_time_ms} ms</span>
            </div>
            <div class="overflow-x-auto max-h-64">
                <table class="sql-table">
                    <thead>
                        <tr>${result.columns.map(c => `<th>${c}</th>`).join('')}</tr>
                    </thead>
                    <tbody>
                        ${result.rows.map(row => `<tr>${row.map(cell => `<td>${cell === null ? '<span class="text-slate-400 italic">NULL</span>' : cell}</td>`).join('')}</tr>`).join('')}
                    </tbody>
                </table>
            </div>
        `;

        if (result.query_plan && result.query_plan.length > 0) {
            html += `
                <div class="p-4 bg-indigo-50/50 border-t border-slate-200 text-xs">
                    <div class="font-bold text-indigo-800 mb-1.5 flex items-center gap-1">
                        <span>🔍</span> EXPLAIN Query Execution Plan:
                    </div>
                    <div class="font-mono text-slate-700 space-y-1 text-[11px]">
                        ${result.query_plan.map(p => `<div><span class="text-indigo-400 font-bold">•</span> ${p.detail}</div>`).join('')}
                    </div>
                </div>
            `;
        }

        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<div class="p-4 text-xs font-mono text-rose-600">Error: ${err.message}</div>`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `<span>▶</span> Execute SQL <kbd class="ml-1 text-[10px] bg-blue-800/60 px-1.5 py-0.5 rounded text-white font-mono">Ctrl+Enter</kbd>`;
    }
}

async function runRedisCode() {
    const commands = document.getElementById("redisCommandInput").value;
    const terminal = document.getElementById("redisOutputTerminal");
    const runBtn = document.getElementById("runRedisBtn");

    runBtn.disabled = true;
    runBtn.innerText = "Executing Redis...";

    try {
        const res = await fetch("/api/v1/sandbox/redis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ commands: commands })
        });
        const result = await res.json();
        let out = "";
        result.logs.forEach(log => {
            if (log.type === "comment") {
                out += `${log.command}\n`;
            } else {
                out += `> ${log.command}\n${JSON.stringify(log.output, null, 2)}\n\n`;
            }
        });
        out += `Execution Time: ${result.execution_time_ms} ms`;
        terminal.innerText = out;
        terminal.className = "text-rose-300 font-mono text-xs whitespace-pre-wrap";
    } catch (err) {
        terminal.innerText = `Redis Error: ${err.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "▶ Execute Redis CLI";
    }
}

async function runNoSQLCode() {
    const query = document.getElementById("nosqlQueryInput").value;
    const terminal = document.getElementById("nosqlOutputTerminal");
    const runBtn = document.getElementById("runNosqlBtn");

    runBtn.disabled = true;
    runBtn.innerText = "Running Query...";

    try {
        const res = await fetch("/api/v1/sandbox/nosql", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });
        const result = await res.json();

        if (!result.success) {
            terminal.innerText = `Error: ${result.error}`;
            terminal.className = "text-rose-400 font-mono text-xs whitespace-pre-wrap";
            return;
        }

        let out = `// Matches: ${result.document_count} documents | Time: ${result.execution_time_ms} ms\n\n`;
        out += JSON.stringify(result.documents, null, 2);
        terminal.innerText = out;
        terminal.className = "text-emerald-300 font-mono text-xs whitespace-pre-wrap";
    } catch (err) {
        terminal.innerText = `NoSQL Error: ${err.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "▶ Run Mongo Query";
    }
}

async function submitToAIInterviewer() {
    const candidateAnswer = document.getElementById("candidateResponseInput").value;
    const pyCode = document.getElementById("pythonCodeInput")?.value || "";
    const sqlCode = document.getElementById("sqlQueryInput")?.value || "";
    const submitBtn = document.getElementById("submitAiBtn");
    const aiCard = document.getElementById("aiEvaluationCard");

    if (!candidateAnswer.trim() && !pyCode.trim() && !sqlCode.trim()) {
        alert("Please write an architectural explanation or code solution before submitting for review!");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="animate-spin inline-block mr-1">🤖</span> AI Bar Raiser Evaluating...`;

    try {
        const res = await fetch("/api/v1/interview/turns", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: activeSessionId,
                question_id: currentQuestion ? currentQuestion.id : null,
                candidate_response: candidateAnswer,
                candidate_code: pyCode,
                candidate_sql: sqlCode
            })
        });
        const turn = await res.json();

        aiCard.classList.remove("hidden");
        document.getElementById("aiScoreValue").innerText = `${turn.score} / 10`;
        document.getElementById("aiFeedbackContent").innerHTML = formatMarkdown(turn.feedback);

        const crossQContainer = document.getElementById("aiCrossQuestions");
        if (turn.cross_questions_asked && turn.cross_questions_asked.length > 0) {
            crossQContainer.innerHTML = `
                <div class="mt-4 p-5 bg-indigo-50/80 border border-indigo-200 rounded-xl">
                    <h5 class="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                        <span>🎯</span> Follow-Up MNC Cross-Questions from Bar Raiser:
                    </h5>
                    <div class="space-y-2">
                        ${turn.cross_questions_asked.map((cq, i) => `
                            <div class="p-3 bg-white border border-indigo-100 rounded-xl text-xs text-slate-800 flex items-start justify-between gap-3 shadow-2xs">
                                <div><span class="font-bold text-indigo-600">Q${i+1}:</span> ${cq}</div>
                                <button onclick="injectCrossQuestion('${cq.replace(/'/g, "\\'")}')" class="text-[11px] font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-lg shrink-0 transition">Address This</button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        aiCard.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        alert(`AI Evaluation Failed: ${err.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>🎙️</span> Submit Answer & Code to AI Bar Raiser`;
    }
}

function injectCrossQuestion(cqText) {
    const textarea = document.getElementById("candidateResponseInput");
    textarea.value = `[Addressing Follow-Up Cross Question: "${cqText}"]\n\n` + textarea.value;
    textarea.focus();
}

function revealSolution() {
    if (!currentQuestion) return;
    if (currentQuestion.solution_code && document.getElementById("pythonCodeInput")) {
        document.getElementById("pythonCodeInput").value = currentQuestion.solution_code;
    }
    if (currentQuestion.solution_sql && document.getElementById("sqlQueryInput")) {
        document.getElementById("sqlQueryInput").value = currentQuestion.solution_sql;
    }
}

function resetStarterCode() {
    if (!currentQuestion) return;
    if (document.getElementById("pythonCodeInput")) {
        document.getElementById("pythonCodeInput").value = currentQuestion.starter_code || "";
    }
    if (document.getElementById("sqlQueryInput")) {
        document.getElementById("sqlQueryInput").value = currentQuestion.starter_sql || "";
    }
}

async function loadMindmaps() {
    try {
        const res = await fetch("/api/v1/mindmaps");
        const topics = await res.json();
        const tabList = document.getElementById("mindmapTabList");
        if (!tabList) return;

        tabList.innerHTML = topics.map((t, idx) => `
            <button onclick="renderMindmap('${t.slug}')" class="px-3.5 py-2 text-xs rounded-xl transition font-semibold text-left border border-slate-200 ${idx === 0 ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs' : 'bg-white text-slate-700 hover:bg-slate-100'}">
                ${t.title}
            </button>
        `).join('');

        if (topics.length > 0) {
            await renderMindmap(topics[0].slug);
        }
    } catch (err) {
        console.error("Error loading mindmaps:", err);
    }
}

async function renderMindmap(slug) {
    try {
        const res = await fetch(`/api/v1/mindmaps/${slug}`);
        const topic = await res.json();
        const container = document.getElementById("mindmapDiagramContainer");
        const detailsContainer = document.getElementById("mindmapNodesDetail");

        if (topic.mermaid_diagram && window.mermaid) {
            container.innerHTML = `<pre class="mermaid">${topic.mermaid_diagram}</pre>`;
            mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
        }

        if (topic.nodes && detailsContainer) {
            detailsContainer.innerHTML = topic.nodes.map(n => `
                <div class="p-5 bg-white border border-slate-200 rounded-xl space-y-2 shadow-2xs">
                    <div class="flex items-center justify-between">
                        <h5 class="text-sm font-bold text-indigo-700">${n.label}</h5>
                        <span class="text-[11px] font-bold px-2 py-0.5 rounded-full ${getDifficultyClass(n.depth_level)}">${n.depth_level.toUpperCase()}</span>
                    </div>
                    <p class="text-xs text-slate-600 leading-relaxed">${n.summary}</p>
                    <div class="text-[11px] text-amber-700 font-semibold bg-amber-50 p-2 rounded-lg border border-amber-200/60">💡 MNC Significance: ${n.mnc_importance}</div>
                    ${n.code_sample ? `
                        <div class="terminal-console p-3 mt-2 text-xs text-slate-200">
                            <pre>${n.code_sample}</pre>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Error rendering mindmap:", err);
    }
}

async function loadSQLSchemas() {
    try {
        const res = await fetch("/api/v1/sandbox/sql/schemas");
        const data = await res.json();
        const select = document.getElementById("sqlSchemaSelect");
        if (select && data.schemas) {
            select.innerHTML = data.schemas.map(s => `
                <option value="${s.id}">${s.name} (${s.tables.join(', ')})</option>
            `).join('');
        }
    } catch (err) {
        console.error("Error loading schemas:", err);
    }
}

function getDifficultyClass(difficulty) {
    switch (String(difficulty).toLowerCase()) {
        case 'basic':
        case 'junior': return 'badge-junior';
        case 'intermediate':
        case 'mid': return 'badge-mid';
        case 'advanced':
        case 'senior': return 'badge-senior';
        default: return 'badge-lead';
    }
}

function formatCategory(cat) {
    if (!cat) return "";
    return cat.replace(/_/g, " ").toUpperCase();
}

function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/### (.*?)\n/g, '<h3 class="text-sm font-bold text-slate-900 mt-3 mb-1.5">$1</h3>')
        .replace(/#### (.*?)\n/g, '<h4 class="text-xs font-bold text-slate-800 mt-2 mb-1">$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-indigo-700 font-bold">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em class="text-slate-700">$1</em>')
        .replace(/`([^`]+)`/g, '<code class="bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-mono text-xs border border-indigo-200/60">$1</code>')
        .replace(/\n\n/g, '<br/><br/>')
        .replace(/\n- /g, '<br/>• ');
}
