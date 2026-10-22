// AI Python Backend & MNC Interview Trainer - Interactive Jupyter Engine
let currentQuestion = null;
let currentExperienceLevel = "mid";
let currentDomainFilter = "";
let currentPhaseFilter = "basic"; // "basic", "intermediate", "advanced", or ""
let activeSessionId = null;
let currentMindmapSlug = "python-internals";
let currentAppMode = "studio"; // "studio", "mcq", or "concepts"
let currentMostAskedFilter = false;
let allMasterConcepts = [];
let currentConceptCategory = "";
let currentIbTab = "problem"; // "problem", "editorial", "copilot"
let activeSandboxTab = "python"; // "python", "sql", "redis", "nosql"

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// MCQ Speed Arena State
let arenaQuestions = [];
let arenaCurrentIndex = 0;
let arenaPhase = "basic";
let arenaScore = 0;
let arenaTotalAnswered = 0;
let arenaStreak = 0;
let arenaBestStreak = 0;
let arenaAnsweredCurrent = false;

function getPhaseClass(phase) {
    const p = (phase || '').toLowerCase();
    if (p === 'basic') return 'bg-emerald-100 text-emerald-800 border border-emerald-300';
    if (p === 'intermediate') return 'bg-blue-100 text-blue-800 border border-blue-300';
    return 'bg-purple-100 text-purple-800 border border-purple-300';
}

function selectCareerPhase(phase, el) {
    currentPhaseFilter = phase;
    currentDomainFilter = ""; // Reset technology domain filter to show all questions for this phase

    // Reset domain chip buttons to 'All'
    document.querySelectorAll("#domainChips button").forEach(b => {
        b.className = "px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 shrink-0 font-medium transition";
    });
    const allChip = document.querySelector("#domainChips button:nth-child(2)");
    if (allChip) allChip.className = "px-2.5 py-1 rounded-lg bg-indigo-600 text-white shrink-0 font-bold shadow-2xs transition";

    // Update button styles in phase bar
    document.querySelectorAll(".phase-step-btn").forEach(btn => {
        btn.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold transition flex items-center gap-2";
    });
    
    if (!el) {
        const map = { 'basic': 'phaseBtnBasic', 'intermediate': 'phaseBtnInter', 'advanced': 'phaseBtnAdv', '': 'phaseBtnAll' };
        el = document.getElementById(map[phase] || 'phaseBtnAll');
    }

    if (el) {
        if (phase === 'basic') {
            el.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-emerald-300 bg-emerald-50 text-emerald-800 font-bold transition flex items-center gap-2 shadow-2xs";
        } else if (phase === 'intermediate') {
            el.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-blue-300 bg-blue-50 text-blue-800 font-bold transition flex items-center gap-2 shadow-2xs";
        } else if (phase === 'advanced') {
            el.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-purple-300 bg-purple-50 text-purple-800 font-bold transition flex items-center gap-2 shadow-2xs";
        } else {
            el.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-indigo-300 bg-indigo-50 text-indigo-800 font-bold transition flex items-center gap-1.5 shadow-2xs";
        }
    }
    
    if (currentAppMode === 'mcq') {
        switchArenaPhase(phase);
    } else {
        loadQuestions();
    }
}

function switchAppMode(mode) {
    currentAppMode = mode;
    const studioWorkspace = document.getElementById("studioWorkspace");
    const mcqArenaWorkspace = document.getElementById("mcqArenaWorkspace");
    const conceptsHubWorkspace = document.getElementById("conceptsHubWorkspace");
    const modeStudioBtn = document.getElementById("modeStudioBtn");
    const modeMcqBtn = document.getElementById("modeMcqBtn");
    const modeConceptBtn = document.getElementById("modeConceptBtn");

    // Hide all workspaces
    if (studioWorkspace) studioWorkspace.classList.add("hidden");
    if (mcqArenaWorkspace) mcqArenaWorkspace.classList.add("hidden");
    if (conceptsHubWorkspace) conceptsHubWorkspace.classList.add("hidden");

    // Reset button styles
    const inactiveClass = "px-3.5 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 font-semibold transition flex items-center gap-1.5";
    if (modeStudioBtn) modeStudioBtn.className = inactiveClass;
    if (modeMcqBtn) modeMcqBtn.className = inactiveClass;
    if (modeConceptBtn) modeConceptBtn.className = inactiveClass;

    if (mode === "studio") {
        if (studioWorkspace) studioWorkspace.classList.remove("hidden");
        if (modeStudioBtn) modeStudioBtn.className = "px-3.5 py-1.5 rounded-lg bg-white text-indigo-700 font-bold shadow-2xs transition flex items-center gap-1.5";
    } else if (mode === "mcq") {
        if (mcqArenaWorkspace) mcqArenaWorkspace.classList.remove("hidden");
        if (modeMcqBtn) modeMcqBtn.className = "px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white font-bold shadow-2xs transition flex items-center gap-1.5";
        startMcqQuiz(currentPhaseFilter || arenaPhase);
    } else if (mode === "concepts") {
        if (conceptsHubWorkspace) conceptsHubWorkspace.classList.remove("hidden");
        if (modeConceptBtn) modeConceptBtn.className = "px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white font-bold shadow-2xs transition flex items-center gap-1.5";
        loadConceptsHub();
    }
}

function toggleMostAskedFilter(btn) {
    currentMostAskedFilter = !currentMostAskedFilter;
    const mostAskedBtn = document.getElementById("mostAskedBtn");
    const chipMostAsked = document.getElementById("chipMostAsked");

    if (currentMostAskedFilter) {
        if (mostAskedBtn) mostAskedBtn.className = "px-3.5 py-1.5 rounded-lg border border-amber-500 bg-amber-500 text-white font-bold shadow-md shadow-amber-500/20 transition flex items-center gap-1.5 ml-2";
        if (chipMostAsked) chipMostAsked.className = "px-2.5 py-1 rounded-lg bg-amber-600 text-white font-bold shrink-0 shadow-2xs transition flex items-center gap-1";
        showToast("🔥 Filtered by Most Asked MNC Interview Questions");
    } else {
        if (mostAskedBtn) mostAskedBtn.className = "px-3 py-1.5 rounded-lg border border-amber-300 bg-amber-50 hover:bg-amber-100 text-amber-900 font-bold transition flex items-center gap-1.5 shadow-2xs ml-2";
        if (chipMostAsked) chipMostAsked.className = "px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-300 hover:bg-amber-100 text-amber-800 shrink-0 font-bold transition flex items-center gap-1 shadow-2xs";
        showToast("Cleared Most Asked Filter — Showing All Questions");
    }

    if (currentAppMode === 'concepts') {
        switchAppMode('studio');
    }

    loadQuestions();
}

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
    await updatePhaseCounts();
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

    // Candidate Response Submit Shortcut (Cmd+Enter sends prompt to Copilot)
    document.getElementById("candidateResponseInput")?.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            sendCandidateCustomPrompt();
        }
    });

    // Tab key indentation support for IDE editors
    function enableTabIndentation(id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener("keydown", function(e) {
            if (e.key === "Tab") {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    }
    enableTabIndentation("pythonCodeInput");
    enableTabIndentation("sqlQueryInput");
    enableTabIndentation("redisCommandInput");
    enableTabIndentation("nosqlQueryInput");

    // SQL Schema Change notification
    document.getElementById("sqlSchemaSelect")?.addEventListener("change", (e) => {
        const val = e.target.value;
        showToast(`Active SQL Schema: ${val.toUpperCase()}`);
    });
}


function filterByDomain(domain, btnElement) {
    currentDomainFilter = domain;
    
    // When filtering by a specific technology domain, unlock phase so user sees all questions in this topic!
    if (domain) {
        currentPhaseFilter = "";
        document.querySelectorAll(".phase-step-btn").forEach(btn => {
            btn.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold transition flex items-center gap-2";
        });
        const allPhaseBtn = document.getElementById("phaseBtnAll");
        if (allPhaseBtn) {
            allPhaseBtn.className = "phase-step-btn px-3 py-1.5 rounded-lg border border-indigo-300 bg-indigo-50 text-indigo-800 font-bold transition flex items-center gap-1.5 shadow-2xs";
        }
    }

    // Update chip buttons
    document.querySelectorAll("#domainChips button").forEach(b => {
        b.className = "px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 shrink-0 font-medium transition";
    });
    
    let target = btnElement;
    if (!target && window.event && window.event.currentTarget) {
        target = window.event.currentTarget;
    }
    if (!target) {
        const btns = Array.from(document.querySelectorAll("#domainChips button"));
        target = btns.find(b => b.getAttribute("onclick")?.includes(`'${domain}'`)) || btns[0];
    }
    if (target) {
        target.className = "px-2.5 py-1 rounded-lg bg-indigo-600 text-white shrink-0 font-bold shadow-2xs transition";
    }

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

    listEl.innerHTML = `<div class="p-6 text-slate-400 text-xs font-medium animate-pulse text-center">Loading questions...</div>`;

    try {
        const params = [];
        if (currentMostAskedFilter) {
            params.push("most_asked=true");
        }
        if (currentPhaseFilter) {
            params.push(`phase=${encodeURIComponent(currentPhaseFilter)}`);
        } else if (currentExperienceLevel) {
            params.push(`experience_level=${encodeURIComponent(currentExperienceLevel)}`);
        }
        if (currentDomainFilter) {
            params.push(`category=${encodeURIComponent(currentDomainFilter)}`);
        }
        
        const url = `/api/v1/questions` + (params.length ? `?${params.join("&")}` : "");
        const res = await fetch(url);
        const questions = await res.json();

        if (!questions.length) {
            listEl.innerHTML = `
                <div class="p-8 text-center text-slate-500 text-xs space-y-2">
                    <p class="font-semibold text-slate-700">No questions found for this filter.</p>
                    <p>Try clicking <button onclick="selectCareerPhase('', document.getElementById('phaseBtnAll'))" class="text-indigo-600 font-bold underline">Show All Questions</button>.</p>
                </div>
            `;
            return;
        }

        listEl.innerHTML = questions.map((q, idx) => `
            <div onclick="selectQuestion(${q.id})" id="q-card-${q.id}" class="p-3.5 hover:bg-indigo-50/40 cursor-pointer transition flex flex-col gap-1.5 ${idx === 0 ? 'bg-indigo-50/70 border-l-4 border-l-indigo-600' : 'border-l-4 border-l-transparent'}">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-1.5">
                        <span class="text-[9px] font-mono px-2 py-0.5 rounded-full font-bold ${getPhaseClass(q.phase)}">${(q.phase || 'basic').toUpperCase()}</span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${getDifficultyClass(q.difficulty)}">${q.difficulty.toUpperCase()}</span>
                    </div>
                    <span class="text-[10px] text-slate-400 font-mono font-medium">${q.min_exp_years}-${q.max_exp_years} YOE</span>
                </div>
                <h4 class="text-xs font-bold text-slate-800 line-clamp-2 leading-relaxed">${q.title}</h4>
                <div class="flex flex-wrap gap-1 mt-0.5 items-center">
                    ${q.is_most_asked ? `<span class="text-[9px] bg-rose-50 text-rose-700 border border-rose-200 px-1.5 py-0.2 rounded font-mono font-bold flex items-center gap-0.5">🔥 Most Asked</span>` : ''}
                    <span class="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded border border-slate-200/80 font-medium font-mono">${formatCategory(q.category)}</span>
                    ${(q.company_tags || []).slice(0, 3).map(tag => `<span class="company-tag">${tag}</span>`).join('')}
                    ${q.has_mcq ? `<span class="text-[9px] bg-amber-50 text-amber-800 border border-amber-200 px-1 rounded font-mono font-bold">MCQ</span>` : ''}
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
    
    // Clean Badges & Enterprise Company Chips + Walkthrough Button
    const badgeContainer = document.getElementById("qBadges");
    badgeContainer.innerHTML = `
        <button onclick="toggleEasyWalkthrough()" class="px-3 py-1 text-xs rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold transition flex items-center gap-1.5 shadow-2xs">
            <span>💡</span> Easy Answer Walkthrough
        </button>
        <span class="px-2.5 py-1 text-xs rounded-full font-bold ${getDifficultyClass(q.difficulty)}">${q.difficulty.toUpperCase()}</span>
        <span class="px-2.5 py-1 text-xs rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold font-mono">${formatCategory(q.category)}</span>
        <span class="px-2.5 py-1 text-xs rounded-full bg-slate-100 text-slate-700 border border-slate-200 font-semibold font-mono">Ask Frequency: ${q.frequency_score}%</span>
        ${(q.company_tags || []).map(t => `<span class="company-tag">${t}</span>`).join('')}
    `;

    // Theory & Gotchas
    if (q.theory_explanation) {
        document.getElementById("qTheoryCard").classList.remove("hidden");
        document.getElementById("qTheoryText").innerHTML = formatMarkdown(q.theory_explanation);
    } else {
        document.getElementById("qTheoryCard").classList.add("hidden");
    }

    // Common Traps without amateurish emojis
    const trapsList = document.getElementById("qTrapsList");
    if (trapsList && q.common_traps) {
        trapsList.innerHTML = q.common_traps.map(trap => `
            <li class="text-xs text-amber-900 leading-relaxed flex items-start gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0"></span>
                <span>${trap}</span>
            </li>
        `).join('');
    }

    // Populate Easy-to-Understand Walkthrough
    const walkthroughCard = document.getElementById("solutionWalkthroughCard");
    const walkthroughText = document.getElementById("solutionWalkthroughText");
    if (walkthroughCard && walkthroughText) {
        walkthroughCard.classList.add("hidden");
        let walkHtml = "";

        if (q.best_practices && q.best_practices.length > 0) {
            walkHtml += `
                <div class="mb-3">
                    <h5 class="font-bold text-emerald-950 text-xs mb-1">🎯 What Top MNC Interviewers Look For:</h5>
                    <ul class="list-disc pl-5 space-y-1 text-slate-700">
                        ${q.best_practices.map(bp => `<li>${bp}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (q.solution_code) {
            walkHtml += `
                <div class="mt-2">
                    <h5 class="font-bold text-slate-900 text-xs mb-1 font-mono">🐍 Model Python Solution with Line-by-Line Guide:</h5>
                    <pre class="terminal-console p-3 rounded-lg text-emerald-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">${q.solution_code}</pre>
                </div>
            `;
        }

        if (q.solution_sql) {
            walkHtml += `
                <div class="mt-2">
                    <h5 class="font-bold text-slate-900 text-xs mb-1 font-mono">🗄️ Optimal SQL Query Breakdown:</h5>
                    <pre class="terminal-console p-3 rounded-lg text-blue-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">${q.solution_sql}</pre>
                </div>
            `;
        }

        if (q.solution_redis) {
            walkHtml += `
                <div class="mt-2">
                    <h5 class="font-bold text-slate-900 text-xs mb-1 font-mono">⚡ Redis In-Memory Sequence:</h5>
                    <pre class="terminal-console p-3 rounded-lg text-rose-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">${q.solution_redis}</pre>
                </div>
            `;
        }

        if (q.solution_nosql) {
            walkHtml += `
                <div class="mt-2">
                    <h5 class="font-bold text-slate-900 text-xs mb-1 font-mono">🍃 MongoDB Document Pipeline Guide:</h5>
                    <pre class="terminal-console p-3 rounded-lg text-emerald-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">${q.solution_nosql}</pre>
                </div>
            `;
        }

        walkthroughText.innerHTML = walkHtml || "<p class='text-slate-500 italic'>No walkthrough content available for this problem.</p>";
    }

    // Populate Concept MCQ Quick Check Card in Cell 1
    const mcqCard = document.getElementById("qMcqCard");
    if (mcqCard) {
        if (q.mcq_question && q.mcq_options && q.mcq_options.length >= 2) {
            mcqCard.classList.remove("hidden");
            document.getElementById("qMcqPrompt").innerText = q.mcq_question;
            const phaseBadge = document.getElementById("qMcqPhaseBadge");
            if (phaseBadge) {
                const p = (q.phase || "basic").toUpperCase();
                phaseBadge.innerText = `PHASE: ${p}`;
                phaseBadge.className = `text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${getPhaseClass(q.phase)}`;
            }
            renderQuestionMcqOptions(q);
        } else {
            mcqCard.classList.add("hidden");
        }
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
        document.getElementById("pyOutputTerminal").innerText = "// Click 'Run Python' to test execution";
    }

    // Prepopulate SQL if question supports it
    if (q.has_sql_sandbox && document.getElementById("sqlQueryInput")) {
        document.getElementById("sqlQueryInput").value = q.starter_sql || "-- Write your SQL query here\nSELECT 1;";
        if (q.sql_schema) document.getElementById("sqlSchemaSelect").value = q.sql_schema;
    }

    // Reset AI Feedback area & Big-O complexity card
    document.getElementById("aiEvaluationCard").classList.add("hidden");
    document.getElementById("candidateResponseInput").value = "";
    document.getElementById("pyComplexityCard")?.classList.add("hidden");

    // Reset to Problem Spec tab on question change
    switchIbTab("problem");

    // Set phase tag if present
    const phaseTag = document.getElementById("qPhaseTag");
    if (phaseTag) {
        const p = (q.phase || "basic").toUpperCase();
        phaseTag.innerText = `PHASE: ${p}`;
        phaseTag.className = `text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${getPhaseClass(q.phase)}`;
    }

    // Initialize clean AI Copilot chat stream with welcome prompt for this question
    const stream = document.getElementById("copilotChatStream");
    if (stream) {
        stream.innerHTML = `
            <div class="copilot-msg-ai">
                <div class="flex items-center gap-1.5 font-bold text-indigo-900 text-xs mb-1">
                    <span>🤖</span>
                    <span>Senior Staff AI Copilot</span>
                </div>
                <p class="leading-relaxed text-slate-700">
                    Ready for <strong>${escapeHtml(q.title)}</strong>! Write code in the IDE on the right, click any quick prompt chip above, or submit your solution for a comprehensive MNC interview evaluation.
                </p>
            </div>
        `;
    }
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

        // Update IDE status bar
        const statusPill = document.getElementById("ideStatusPill");
        const statusText = document.getElementById("ideStatusText");
        if (statusPill && statusText) {
            statusPill.className = result.success ? "w-2 h-2 rounded-full bg-emerald-500" : "w-2 h-2 rounded-full bg-rose-500";
            statusText.innerText = result.success ? `Python • Executed in ${result.execution_time_ms} ms` : `Execution Failed`;
        }

        // Render Big-O Complexity Inspector Card
        const compCard = document.getElementById("pyComplexityCard");

        const timeBadge = document.getElementById("pyTimeBadge");
        const spaceBadge = document.getElementById("pySpaceBadge");
        const suggContainer = document.getElementById("pyComplexitySuggestions");

        if (compCard && result.complexity_analysis) {
            const comp = result.complexity_analysis;
            compCard.classList.remove("hidden");

            const tComp = comp.time_complexity || "O(N)";
            const sComp = comp.space_complexity || "O(1)";
            
            timeBadge.innerText = `⏱️ Time: ${tComp}`;
            if (tComp.includes("Quadratic") || tComp.includes("Cubic") || tComp.includes("Exponential")) {
                timeBadge.className = "text-xs font-mono font-bold px-2.5 py-0.5 rounded-lg bg-rose-100 text-rose-800 border border-rose-300";
            } else {
                timeBadge.className = "text-xs font-mono font-bold px-2.5 py-0.5 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300";
            }

            spaceBadge.innerText = `💾 Space: ${sComp}`;
            if (sComp.includes("Linear") || sComp.includes("Quadratic")) {
                spaceBadge.className = "text-xs font-mono font-bold px-2.5 py-0.5 rounded-lg bg-amber-100 text-amber-800 border border-amber-300";
            } else {
                spaceBadge.className = "text-xs font-mono font-bold px-2.5 py-0.5 rounded-lg bg-blue-100 text-blue-800 border border-blue-300";
            }

            let suggHtml = "";
            if (comp.time_bottlenecks && comp.time_bottlenecks.length > 0) {
                suggHtml += `<div class="p-2.5 bg-rose-50/70 border border-rose-200 rounded-lg text-rose-900 text-xs font-medium space-y-1">
                    <span class="font-bold">⚠️ Performance Bottleneck:</span>
                    <ul class="list-disc pl-4 space-y-0.5 text-[11px]">${comp.time_bottlenecks.map(b => `<li>${b}</li>`).join('')}</ul>
                </div>`;
            }

            if (comp.suggestions && comp.suggestions.length > 0) {
                suggHtml += `<div class="p-2.5 bg-indigo-50/70 border border-indigo-200 rounded-lg text-indigo-950 text-xs font-medium space-y-1">
                    <span class="font-bold">💡 Big-O Optimization Advice:</span>
                    <ul class="list-disc pl-4 space-y-0.5 text-[11px]">${comp.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
                </div>`;
            }

            suggContainer.innerHTML = suggHtml || "<p class='text-emerald-700 font-semibold'>✅ Code operates at optimal Big-O bounds.</p>";
        }
    } catch (err) {
        terminal.innerText = `Network/Execution Error: ${err.message}`;
        terminal.className = "text-rose-400 font-mono text-xs";
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `<span>▶</span> Run Python <kbd class="ml-1 text-[10px] bg-emerald-800/60 px-1.5 py-0.5 rounded text-white font-mono">⌘Enter</kbd>`;
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

        const statusPill = document.getElementById("ideStatusPill");
        const statusText = document.getElementById("ideStatusText");
        if (statusPill && statusText) {
            statusPill.className = "w-2 h-2 rounded-full bg-blue-500";
            statusText.innerText = `PostgreSQL • ${result.row_count} rows in ${result.execution_time_ms} ms`;
        }
    } catch (err) {
        container.innerHTML = `<div class="p-4 text-xs font-mono text-rose-600">Error: ${err.message}</div>`;
        const statusPill = document.getElementById("ideStatusPill");
        const statusText = document.getElementById("ideStatusText");
        if (statusPill && statusText) {
            statusPill.className = "w-2 h-2 rounded-full bg-rose-500";
            statusText.innerText = `SQL Execution Error`;
        }
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = `<span>▶</span> Execute SQL <kbd class="ml-1 text-[10px] bg-blue-800/60 px-1.5 py-0.5 rounded text-white font-mono">⌘Enter</kbd>`;
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

        const statusPill = document.getElementById("ideStatusPill");
        const statusText = document.getElementById("ideStatusText");
        if (statusPill && statusText) {
            statusPill.className = "w-2 h-2 rounded-full bg-rose-500";
            statusText.innerText = `Redis • Executed in ${result.execution_time_ms} ms`;
        }
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
            const statusPill = document.getElementById("ideStatusPill");
            const statusText = document.getElementById("ideStatusText");
            if (statusPill && statusText) {
                statusPill.className = "w-2 h-2 rounded-full bg-rose-500";
                statusText.innerText = `MongoDB Query Error`;
            }
            return;
        }

        let out = `// Matches: ${result.document_count} documents | Time: ${result.execution_time_ms} ms\n\n`;
        out += JSON.stringify(result.documents, null, 2);
        terminal.innerText = out;
        terminal.className = "text-emerald-300 font-mono text-xs whitespace-pre-wrap";

        const statusPill = document.getElementById("ideStatusPill");
        const statusText = document.getElementById("ideStatusText");
        if (statusPill && statusText) {
            statusPill.className = "w-2 h-2 rounded-full bg-emerald-500";
            statusText.innerText = `MongoDB • ${result.document_count} docs in ${result.execution_time_ms} ms`;
        }
    } catch (err) {
        terminal.innerText = `NoSQL Error: ${err.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "▶ Run Mongo Query";
    }
}


async function submitToAIInterviewer() {
    const candidateAnswer = document.getElementById("candidateResponseInput")?.value || "";
    const pyCode = document.getElementById("pythonCodeInput")?.value || "";
    const sqlCode = document.getElementById("sqlQueryInput")?.value || "";
    const submitBtn = document.getElementById("submitAiBtn");
    const aiCard = document.getElementById("aiEvaluationCard");
    const stream = document.getElementById("copilotChatStream");

    if (!candidateAnswer.trim() && !pyCode.trim() && !sqlCode.trim()) {
        showToast("Please write an architectural explanation or code solution before submitting for review!");
        return;
    }

    switchIbTab("copilot");

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="animate-spin inline-block mr-1">🤖</span> Evaluating Solution...`;
    }

    // Append candidate submission to chat stream
    if (stream) {
        const userDiv = document.createElement("div");
        userDiv.className = "copilot-msg-user";
        let subText = "";
        if (candidateAnswer.trim()) {
            subText += `<p class="mb-1">${escapeHtml(candidateAnswer.trim())}</p>`;
        }
        if (pyCode.trim()) {
            subText += `<pre class="bg-black/40 p-2 rounded text-[10px] text-emerald-300 font-mono overflow-x-auto"><code>${escapeHtml(pyCode.trim())}</code></pre>`;
        }
        userDiv.innerHTML = `<span class="font-bold text-indigo-300">Solution Submission:</span><div class="mt-1">${subText}</div>`;
        stream.appendChild(userDiv);

        const typingDiv = document.createElement("div");
        typingDiv.id = "copilotTypingIndicator";
        typingDiv.className = "copilot-typing";
        typingDiv.innerHTML = `
            <div class="copilot-dot"></div>
            <div class="copilot-dot"></div>
            <div class="copilot-dot"></div>
            <span>Senior Staff Bar Raiser is grading your submission...</span>
        `;
        stream.appendChild(typingDiv);
        stream.scrollTop = stream.scrollHeight;
    }

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

        const typingEl = document.getElementById("copilotTypingIndicator");
        if (typingEl) typingEl.remove();

        let verdict = "HIRE";
        let verdictClass = "bg-emerald-50 text-emerald-700 border-emerald-300";
        if (turn.score >= 8.5) {
            verdict = "STRONG HIRE";
            verdictClass = "bg-emerald-50 text-emerald-700 border-emerald-300";
        } else if (turn.score >= 7.0) {
            verdict = "HIRE";
            verdictClass = "bg-blue-50 text-blue-700 border-blue-300";
        } else if (turn.score >= 5.0) {
            verdict = "LEANING HIRE";
            verdictClass = "bg-amber-50 text-amber-700 border-amber-300";
        } else {
            verdict = "NEEDS REVISION";
            verdictClass = "bg-rose-50 text-rose-700 border-rose-300";
        }

        // Update evaluation scorecard card
        if (aiCard) {
            aiCard.classList.remove("hidden");
            const scoreEl = document.getElementById("aiScoreValue");
            if (scoreEl) {
                scoreEl.className = `text-xs font-mono font-bold px-3 py-1 rounded-full border ${verdictClass}`;
                scoreEl.innerText = `${verdict} • ${turn.score} / 10`;
            }

            const feedbackEl = document.getElementById("aiFeedbackContent");
            if (feedbackEl) feedbackEl.innerHTML = formatMarkdown(turn.feedback);

            const crossQContainer = document.getElementById("aiCrossQuestions");
            if (crossQContainer && turn.cross_questions_asked && turn.cross_questions_asked.length > 0) {
                window.lastCrossQuestions = turn.cross_questions_asked;
                crossQContainer.innerHTML = `
                    <div class="mt-4 p-4 bg-indigo-50/60 border border-indigo-200/80 rounded-xl">
                        <h5 class="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-2 flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-indigo-600"></span>
                            <span>MNC Senior Staff Follow-Up Cross-Questions:</span>
                        </h5>
                        <div class="space-y-1.5">
                            ${turn.cross_questions_asked.map((cq, i) => `
                                <div class="p-2.5 bg-white border border-indigo-100 rounded-xl text-xs text-slate-800 flex items-start justify-between gap-2 shadow-2xs">
                                    <div><span class="font-bold text-indigo-600">Q${i+1}:</span> ${cq}</div>
                                    <button onclick="injectCrossQuestionByIndex(${i})" class="text-[10px] font-semibold bg-indigo-600 hover:bg-indigo-700 text-white px-2.5 py-1 rounded-lg shrink-0 transition">Address This</button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        }

        // Append rich assessment directly into Copilot chat stream
        if (stream) {
            const aiDiv = document.createElement("div");
            aiDiv.className = "copilot-msg-ai";
            let crossQHtml = "";
            if (turn.cross_questions_asked && turn.cross_questions_asked.length > 0) {
                crossQHtml = `
                    <div class="mt-3 pt-2.5 border-t border-slate-200">
                        <div class="font-bold text-indigo-950 text-xs mb-1.5 flex items-center gap-1.5">
                            <span>🔥</span>
                            <span>Staff Principal Follow-Up Challenges:</span>
                        </div>
                        <div class="space-y-1.5">
                            ${turn.cross_questions_asked.map((cq, i) => `
                                <div class="p-2 bg-white border border-indigo-100 rounded-lg flex items-center justify-between gap-2">
                                    <span class="text-slate-800 text-[11px]"><span class="font-bold text-indigo-600">Q${i+1}:</span> ${cq}</span>
                                    <button onclick="injectCrossQuestionByIndex(${i})" class="text-[10px] bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-2 py-0.5 rounded transition shrink-0">Address</button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }

            aiDiv.innerHTML = `
                <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-indigo-100">
                    <div class="flex items-center gap-1.5 font-bold text-indigo-900 text-xs">
                        <span>🎯</span>
                        <span>Senior Staff Bar Raiser Assessment</span>
                    </div>
                    <span class="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full border ${verdictClass}">
                        ${verdict} • ${turn.score} / 10
                    </span>
                </div>
                <div class="text-slate-800 leading-relaxed font-normal">${formatMarkdown(turn.feedback)}</div>
                ${crossQHtml}
            `;
            stream.appendChild(aiDiv);
            stream.scrollTop = stream.scrollHeight;
        }

        // Update IDE status indicators
        const statusPill = document.getElementById("ideStatusPill");
        const statusText = document.getElementById("ideStatusText");
        if (statusPill && statusText) {
            statusPill.className = "w-2 h-2 rounded-full bg-emerald-500";
            statusText.innerText = `Evaluated • ${verdict} (${turn.score}/10)`;
        }

        showToast(`AI Bar Raiser: ${verdict} (${turn.score}/10)`);
    } catch (err) {
        const typingEl = document.getElementById("copilotTypingIndicator");
        if (typingEl) typingEl.remove();
        showToast(`AI Evaluation Failed: ${err.message}`);
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span>🎙️</span> Submit for Bar Raiser Review`;
        }
    }
}


function injectCrossQuestionByIndex(idx) {
    if (!window.lastCrossQuestions || !window.lastCrossQuestions[idx]) return;
    const cqText = window.lastCrossQuestions[idx];
    const textarea = document.getElementById("candidateResponseInput");
    if (!textarea) return;
    textarea.value = `[Addressing Follow-Up Cross Question: "${cqText}"]\n\n` + textarea.value;
    textarea.focus();
    showToast("Follow-up question added to response draft");
}

function injectCrossQuestion(cqText) {
    const textarea = document.getElementById("candidateResponseInput");
    if (!textarea) return;
    textarea.value = `[Addressing Follow-Up Cross Question: "${cqText}"]\n\n` + textarea.value;
    textarea.focus();
    showToast("Follow-up question added to response draft");
}

function toggleEasyWalkthrough() {
    const card = document.getElementById("solutionWalkthroughCard");
    if (!card) return;
    card.classList.toggle("hidden");
    if (!card.classList.contains("hidden")) {
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        showToast("💡 Easy-to-understand answer walkthrough opened");
    }
}

function revealSolution() {
    if (!currentQuestion) return;
    if (currentQuestion.solution_code && document.getElementById("pythonCodeInput")) {
        document.getElementById("pythonCodeInput").value = currentQuestion.solution_code;
    }
    if (currentQuestion.solution_sql && document.getElementById("sqlQueryInput")) {
        document.getElementById("sqlQueryInput").value = currentQuestion.solution_sql;
    }
    if (currentQuestion.solution_redis && document.getElementById("redisCommandInput")) {
        document.getElementById("redisCommandInput").value = currentQuestion.solution_redis;
    }
    if (currentQuestion.solution_nosql && document.getElementById("nosqlQueryInput")) {
        document.getElementById("nosqlQueryInput").value = currentQuestion.solution_nosql;
    }
    // Also reveal the step-by-step walkthrough card
    const walkthrough = document.getElementById("solutionWalkthroughCard");
    if (walkthrough) {
        walkthrough.classList.remove("hidden");
        walkthrough.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    showToast("💡 Model solution & step-by-step walkthrough loaded!");
}

function resetStarterCode() {
    if (!currentQuestion) return;
    if (document.getElementById("pythonCodeInput")) {
        document.getElementById("pythonCodeInput").value = currentQuestion.starter_code || "";
    }
    if (document.getElementById("sqlQueryInput")) {
        document.getElementById("sqlQueryInput").value = currentQuestion.starter_sql || "";
    }
    if (document.getElementById("redisCommandInput")) {
        document.getElementById("redisCommandInput").value = currentQuestion.starter_redis || "";
    }
    if (document.getElementById("nosqlQueryInput")) {
        document.getElementById("nosqlQueryInput").value = currentQuestion.starter_nosql || "";
    }
    showToast("Code reset to starter template");
}

async function loadMindmaps() {
    try {
        const res = await fetch("/api/v1/mindmaps");
        const topics = await res.json();
        const tabList = document.getElementById("mindmapTabList");
        if (!tabList) return;

        tabList.innerHTML = topics.map((t, idx) => `
            <button onclick="renderMindmap('${t.slug}', this)" class="mindmap-topic-btn px-3.5 py-2 text-xs rounded-xl transition font-semibold text-left border border-slate-200 ${idx === 0 ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs font-bold' : 'bg-white text-slate-700 hover:bg-slate-100'}">
                ${t.title}
            </button>
        `).join('');

        if (topics.length > 0) {
            await renderMindmap(topics[0].slug, tabList.querySelector("button"));
        }
    } catch (err) {
        console.error("Error loading mindmaps:", err);
    }
}

async function renderMindmap(slug, btnElement) {
    try {
        const visual = document.getElementById("mindmapVisualSection");
        if (visual) visual.classList.remove("hidden");

        // Update active topic button style
        document.querySelectorAll(".mindmap-topic-btn").forEach(b => {
            b.className = "mindmap-topic-btn px-3.5 py-2 text-xs rounded-xl transition font-semibold text-left border border-slate-200 bg-white text-slate-700 hover:bg-slate-100";
        });
        let target = btnElement;
        if (!target && window.event && window.event.currentTarget) {
            target = window.event.currentTarget;
        }
        if (target) {
            target.className = "mindmap-topic-btn px-3.5 py-2 text-xs rounded-xl transition font-bold text-left border border-indigo-600 bg-indigo-600 text-white shadow-xs";
        }

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

// ----------------------------------------------------
// Flowchart Learning Path & Visual Roadmap Navigation
// ----------------------------------------------------
function selectRoadmapStage(domain, mindmapSlug, element) {
    currentDomainFilter = domain;

    // Highlight the clicked flowchart step
    document.querySelectorAll(".stage-step-btn").forEach(s => {
        s.className = "stage-step-btn px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:border-indigo-300 hover:text-indigo-600 font-medium transition flex items-center gap-2";
    });
    if (element) {
        element.className = "stage-step-btn roadmap-step-active px-3 py-1.5 rounded-lg border border-indigo-600 bg-indigo-600 text-white shadow-xs font-bold transition flex items-center gap-2";
    }

    // Reset domain chips
    document.querySelectorAll("#domainChips button").forEach(b => {
        b.className = "px-2.5 py-1 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 shrink-0 font-medium transition";
    });

    // Reload question list with new domain filter
    loadQuestions();

    // Render corresponding architecture mindmap
    const mindmapSec = document.getElementById("mindmapVisualSection");
    if (mindmapSec) {
        mindmapSec.classList.remove("hidden");
    }
    if (mindmapSlug) {
        renderMindmap(mindmapSlug);
    }

    const title = domain ? domain.replace(/_/g, " ").toUpperCase() : "ALL TOPICS";
    showToast(`Track Milestone Active: ${title}`);
}

// ----------------------------------------------------
// Clipboard & Toast System
// ----------------------------------------------------
function copyToClipboard(elementId, message) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.value !== undefined ? el.value : el.innerText;
    if (!text || !text.trim()) {
        showToast("Nothing to copy", "info");
        return;
    }

    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showToast(message || "Copied to clipboard!");
        }).catch(() => {
            fallbackCopy(text, message);
        });
    } else {
        fallbackCopy(text, message);
    }
}

function fallbackCopy(text, message) {
    const temp = document.createElement("textarea");
    temp.value = text;
    temp.style.position = "fixed";
    temp.style.opacity = "0";
    document.body.appendChild(temp);
    temp.focus();
    temp.select();
    try {
        document.execCommand("copy");
        showToast(message || "Copied to clipboard!");
    } catch (e) {
        showToast("Failed to copy", "error");
    }
    document.body.removeChild(temp);
}

function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "pointer-events-auto flex items-center gap-2.5 px-4 py-2.5 bg-slate-900 text-white rounded-xl shadow-lg border border-slate-700 text-xs font-semibold transform translate-y-2 opacity-0 transition-all duration-200";

    let icon = "✓";
    if (type === "info") icon = "ℹ️";
    if (type === "error") icon = "⚠️";
    if (message.includes("🗺️") || message.includes("💡")) icon = "";

    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove("translate-y-2", "opacity-0");
    });

    setTimeout(() => {
        toast.classList.add("translate-y-2", "opacity-0");
        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 200);
    }, 2500);
}

// ----------------------------------------------------
// MNC Architectural Blueprint Generator
// ----------------------------------------------------
function giveArchitecturalHint() {
    const input = document.getElementById("candidateResponseInput");
    if (!input) return;

    const blueprint = `## 🏛️ MNC Architectural Blueprint & Technical Approach:

1. High-Level Architecture & Component Flow:
   - Identify entry points, async worker queues, and persistence layers.
   - Choose communication protocol (gRPC vs REST, Kafka event streaming).

2. Concurrency, Locking & Race Condition Mitigation:
   - Python asyncio event loop vs multiprocessing workers.
   - DB row-level locking (SELECT FOR UPDATE) vs Redis distributed lock (Redlock).

3. Edge Cases, Failover & Idempotency:
   - Retry policy with exponential backoff and jitter.
   - Idempotency keys to guarantee at-most-once processing.
   - Circuit breaking & fallback defaults for downstream outages.

4. Observability & P99 SLA Guarantees:
   - Distributed tracing (OpenTelemetry) on high-latency critical paths.
   - Connection pool limits (Hikari/SQLAlchemy max_overflow).
   - Target P99 latency: < 50ms at scale.
`;

    if (input.value.trim()) {
        input.value = blueprint + "\n\n" + input.value;
    } else {
        input.value = blueprint;
    }
    input.focus();
    showToast("💡 4-Pillar MNC Architectural Blueprint loaded!");
}

function clearCandidateAnswer() {
    const input = document.getElementById("candidateResponseInput");
    if (!input) return;
    if (input.value.trim() && !confirm("Clear your response draft?")) {
        return;
    }
    input.value = "";
    showToast("Response draft cleared");
}

// ----------------------------------------------------
// Mindmap Fullscreen Expansion Toggle
// ----------------------------------------------------
let isMindmapFullscreen = false;
function toggleMindmapFullscreen() {
    const sec = document.getElementById("mindmapVisualSection");
    const btn = document.getElementById("mindmapFullscreenBtn");
    if (!sec) return;

    isMindmapFullscreen = !isMindmapFullscreen;
    if (isMindmapFullscreen) {
        sec.classList.add("fixed", "inset-0", "z-50", "h-screen", "w-screen", "bg-white", "p-8", "overflow-y-auto");
        sec.classList.remove("p-6", "rounded-2xl", "mb-6");
        if (btn) btn.innerHTML = "<span>⤡</span> Collapse";
        showToast("Mindmap expanded to fullscreen");
    } else {
        sec.classList.remove("fixed", "inset-0", "z-50", "h-screen", "w-screen", "bg-white", "p-8", "overflow-y-auto");
        sec.classList.add("p-6", "rounded-2xl", "mb-6");
        if (btn) btn.innerHTML = "<span>⤢</span> Fullscreen";
        showToast("Mindmap collapsed");
    }
}

// ----------------------------------------------------
// Interactive Concept MCQ Quick Check (Cell 1)
// ----------------------------------------------------
function renderQuestionMcqOptions(q) {
    const container = document.getElementById("qMcqOptionsContainer");
    const expBox = document.getElementById("qMcqExplanationBox");
    if (expBox) expBox.classList.add("hidden");
    if (!container || !q.mcq_options) return;

    container.innerHTML = q.mcq_options.map((opt, idx) => `
        <button onclick="selectQuestionMcq(${idx})" id="q-opt-${idx}" class="q-opt-btn p-3 rounded-lg border border-slate-200 bg-white hover:border-indigo-400 hover:bg-indigo-50/40 text-left text-xs font-semibold text-slate-800 transition flex items-start gap-2.5 shadow-2xs">
            <span class="w-5 h-5 rounded bg-slate-100 border border-slate-300 text-slate-700 flex items-center justify-center font-bold text-[11px] shrink-0 font-mono">${String.fromCharCode(65 + idx)}</span>
            <span class="leading-relaxed mt-0.5">${opt.replace(/^[A-D]\)\s*/, '')}</span>
        </button>
    `).join('');
}

async function selectQuestionMcq(selectedIndex) {
    if (!currentQuestion) return;
    const q = currentQuestion;

    try {
        const res = await fetch("/api/v1/questions/verify-mcq", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question_id: q.id, selected_index: selectedIndex })
        });
        const result = await res.json();

        q.mcq_options.forEach((opt, idx) => {
            const btn = document.getElementById(`q-opt-${idx}`);
            if (!btn) return;
            btn.disabled = true;
            btn.classList.remove("hover:border-indigo-400", "hover:bg-indigo-50/40");
            
            if (idx === result.correct_index) {
                btn.className = "q-opt-btn p-3 rounded-lg border-2 border-emerald-500 bg-emerald-50 text-left text-xs font-bold text-emerald-950 transition flex items-start gap-2.5 shadow-xs";
                btn.querySelector("span").className = "w-5 h-5 rounded bg-emerald-600 text-white flex items-center justify-center font-bold text-[11px] shrink-0 font-mono";
                btn.querySelector("span").innerText = "✓";
            } else if (idx === selectedIndex && !result.is_correct) {
                btn.className = "q-opt-btn p-3 rounded-lg border-2 border-rose-400 bg-rose-50 text-left text-xs font-semibold text-rose-950 transition flex items-start gap-2.5 shadow-xs";
                btn.querySelector("span").className = "w-5 h-5 rounded bg-rose-500 text-white flex items-center justify-center font-bold text-[11px] shrink-0 font-mono";
                btn.querySelector("span").innerText = "✗";
            } else {
                btn.className = "q-opt-btn p-3 rounded-lg border border-slate-200 bg-slate-50 opacity-60 text-left text-xs font-medium text-slate-500 transition flex items-start gap-2.5";
            }
        });

        const expBox = document.getElementById("qMcqExplanationBox");
        const banner = document.getElementById("qMcqFeedbackBanner");
        const text = document.getElementById("qMcqExplanationText");

        if (expBox && banner && text) {
            expBox.classList.remove("hidden");
            if (result.is_correct) {
                banner.className = "font-bold text-emerald-800 flex items-center gap-2 text-xs";
                banner.innerHTML = `<span>✓ Correct Answer!</span>`;
                showToast("✓ Correct Concept Answer!", "success");
            } else {
                banner.className = "font-bold text-amber-800 flex items-center gap-2 text-xs";
                banner.innerHTML = `<span>⚠️ Conceptual Trap (Option ${String.fromCharCode(65 + result.correct_index)} is correct)</span>`;
                showToast("✗ Conceptual Trap detected", "warning");
            }
            text.innerText = result.explanation;
        }

    } catch (e) {
        console.error("Failed to verify question MCQ:", e);
    }
}

function resetCurrentMcq() {
    if (currentQuestion) {
        renderQuestionMcqOptions(currentQuestion);
        showToast("MCQ check reset");
    }
}

// ----------------------------------------------------
// Interactive MCQ Arena Controller (Phase-by-Phase Speed Mode)
// ----------------------------------------------------
async function switchArenaPhase(phase) {
    arenaPhase = phase;
    
    // Update button styling
    ["Basic", "Inter", "Adv", "All"].forEach(id => {
        const btn = document.getElementById(`arenaPhase${id}Btn`);
        if (btn) btn.className = "px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold transition flex items-center gap-1.5";
    });
    
    const activeMap = { 'basic': 'Basic', 'intermediate': 'Inter', 'advanced': 'Adv', '': 'All' };
    const activeBtn = document.getElementById(`arenaPhase${activeMap[phase] || 'All'}Btn`);
    if (activeBtn) {
        if (phase === 'basic') {
            activeBtn.className = "px-3 py-1.5 rounded-lg border border-emerald-300 bg-emerald-50 text-emerald-800 font-bold transition flex items-center gap-1.5 shadow-2xs";
        } else if (phase === 'intermediate') {
            activeBtn.className = "px-3 py-1.5 rounded-lg border border-blue-300 bg-blue-50 text-blue-800 font-bold transition flex items-center gap-1.5 shadow-2xs";
        } else if (phase === 'advanced') {
            activeBtn.className = "px-3 py-1.5 rounded-lg border border-purple-300 bg-purple-50 text-purple-800 font-bold transition flex items-center gap-1.5 shadow-2xs";
        } else {
            activeBtn.className = "px-3 py-1.5 rounded-lg border border-indigo-300 bg-indigo-50 text-indigo-800 font-bold transition flex items-center gap-1.5 shadow-2xs";
        }
    }
    
    await startMcqQuiz(phase);
}

async function startMcqQuiz(phase) {
    try {
        let url = `/api/v1/questions/mcq-quiz`;
        if (phase) url += `?phase=${encodeURIComponent(phase)}`;
        const res = await fetch(url);
        arenaQuestions = await res.json();
        arenaCurrentIndex = 0;
        arenaScore = 0;
        arenaTotalAnswered = 0;
        arenaStreak = 0;
        arenaAnsweredCurrent = false;

        const scoreEl = document.getElementById("arenaScore");
        const streakEl = document.getElementById("arenaStreak");
        if (scoreEl) scoreEl.innerText = `0 / ${arenaQuestions.length}`;
        if (streakEl) streakEl.innerText = `0`;

        const compCard = document.getElementById("arenaCompletionCard");
        const qCard = document.getElementById("arenaQuestionCard");
        if (compCard) compCard.classList.add("hidden");
        if (qCard) qCard.classList.remove("hidden");

        renderArenaQuestion();
    } catch (e) {
        console.error("Failed to load MCQ quiz:", e);
    }
}

function renderArenaQuestion() {
    if (!arenaQuestions.length || arenaCurrentIndex >= arenaQuestions.length) {
        showArenaCompletion();
        return;
    }
    const q = arenaQuestions[arenaCurrentIndex];
    arenaAnsweredCurrent = false;

    // Badges & Progress
    const progressText = document.getElementById("arenaProgressText");
    if (progressText) progressText.innerText = `Question ${arenaCurrentIndex + 1} of ${arenaQuestions.length}`;
    
    const pct = Math.round(((arenaCurrentIndex + 1) / arenaQuestions.length) * 100);
    const progressBar = document.getElementById("arenaProgressBar");
    if (progressBar) progressBar.style.width = `${pct}%`;

    const phaseBadge = document.getElementById("arenaCardPhaseBadge");
    if (phaseBadge) {
        phaseBadge.innerText = (q.phase || "basic").toUpperCase();
        phaseBadge.className = `text-xs font-mono font-bold px-2.5 py-0.5 rounded-full ${getPhaseClass(q.phase)}`;
    }

    const catBadge = document.getElementById("arenaCardCategoryBadge");
    if (catBadge) catBadge.innerText = formatCategory(q.category);

    const titleEl = document.getElementById("arenaQuestionTitle");
    if (titleEl) titleEl.innerText = q.title;

    const textEl = document.getElementById("arenaQuestionText");
    if (textEl) textEl.innerText = q.mcq_question;

    const tagsContainer = document.getElementById("arenaCompanyTags");
    if (tagsContainer) {
        tagsContainer.innerHTML = (q.company_tags || []).slice(0, 3).map(tag => `<span class="company-tag">${tag}</span>`).join('');
    }

    // Hide explanation box
    const expCard = document.getElementById("arenaExplanationCard");
    if (expCard) expCard.classList.add("hidden");

    // Render 4 options
    const optionsContainer = document.getElementById("arenaOptionsList");
    if (optionsContainer && q.mcq_options) {
        optionsContainer.innerHTML = q.mcq_options.map((opt, idx) => `
            <button onclick="selectArenaOption(${idx})" id="arena-opt-${idx}" class="arena-opt-btn p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-400 hover:bg-indigo-50/30 text-left text-xs font-semibold text-slate-800 transition flex items-start gap-3 shadow-2xs">
                <span class="w-6 h-6 rounded-lg bg-slate-100 border border-slate-300 text-slate-700 flex items-center justify-center font-bold text-xs shrink-0 font-mono">${String.fromCharCode(65 + idx)}</span>
                <span class="leading-relaxed mt-0.5">${opt.replace(/^[A-D]\)\s*/, '')}</span>
            </button>
        `).join('');
    }

    // Prev / Next button states
    const prevBtn = document.getElementById("arenaPrevBtn");
    const nextBtn = document.getElementById("arenaNextBtn");
    if (prevBtn) prevBtn.disabled = (arenaCurrentIndex === 0);
    if (nextBtn) nextBtn.innerText = (arenaCurrentIndex === arenaQuestions.length - 1) ? "Finish Phase 🏁" : "Next Question →";
}

async function selectArenaOption(selectedIndex) {
    if (arenaAnsweredCurrent) return;
    arenaAnsweredCurrent = true;

    const q = arenaQuestions[arenaCurrentIndex];
    
    try {
        const res = await fetch("/api/v1/questions/verify-mcq", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question_id: q.id, selected_index: selectedIndex })
        });
        const result = await res.json();
        
        arenaTotalAnswered++;
        if (result.is_correct) {
            arenaScore++;
            arenaStreak++;
            if (arenaStreak > arenaBestStreak) arenaBestStreak = arenaStreak;
            showToast("✓ Correct Answer! Well done.", "success");
        } else {
            arenaStreak = 0;
            showToast("✗ Incorrect Choice. See explanation below.", "warning");
        }

        const scoreEl = document.getElementById("arenaScore");
        const streakEl = document.getElementById("arenaStreak");
        if (scoreEl) scoreEl.innerText = `${arenaScore} / ${arenaQuestions.length}`;
        if (streakEl) streakEl.innerText = `${arenaStreak}`;

        // Colorize options
        q.mcq_options.forEach((opt, idx) => {
            const btn = document.getElementById(`arena-opt-${idx}`);
            if (!btn) return;
            btn.disabled = true;
            btn.classList.remove("hover:border-indigo-400", "hover:bg-indigo-50/30");
            
            if (idx === result.correct_index) {
                btn.className = "arena-opt-btn p-4 rounded-xl border-2 border-emerald-500 bg-emerald-50 text-left text-xs font-bold text-emerald-950 transition flex items-start gap-3 shadow-xs";
                btn.querySelector("span").className = "w-6 h-6 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shrink-0 font-mono";
                btn.querySelector("span").innerText = "✓";
            } else if (idx === selectedIndex && !result.is_correct) {
                btn.className = "arena-opt-btn p-4 rounded-xl border-2 border-rose-400 bg-rose-50 text-left text-xs font-semibold text-rose-950 transition flex items-start gap-3 shadow-xs";
                btn.querySelector("span").className = "w-6 h-6 rounded-lg bg-rose-500 text-white flex items-center justify-center font-bold text-xs shrink-0 font-mono";
                btn.querySelector("span").innerText = "✗";
            } else {
                btn.className = "arena-opt-btn p-4 rounded-xl border border-slate-200 bg-slate-50 opacity-60 text-left text-xs font-medium text-slate-500 transition flex items-start gap-3";
            }
        });

        // Show Explanation Box
        const expCard = document.getElementById("arenaExplanationCard");
        const expHeader = document.getElementById("arenaExplanationHeader");
        const expBody = document.getElementById("arenaExplanationBody");

        if (expCard && expHeader && expBody) {
            expCard.classList.remove("hidden");
            if (result.is_correct) {
                expCard.className = "p-5 rounded-xl border border-emerald-200 bg-emerald-50/60 space-y-2";
                expHeader.className = "font-bold text-xs text-emerald-900 flex items-center gap-2";
                expHeader.innerHTML = `<span>✓ Spot On!</span> <span class="font-normal text-emerald-700">Option ${String.fromCharCode(65 + result.correct_index)} is the optimal architectural answer.</span>`;
            } else {
                expCard.className = "p-5 rounded-xl border border-amber-200 bg-amber-50/60 space-y-2";
                expHeader.className = "font-bold text-xs text-amber-900 flex items-center gap-2";
                expHeader.innerHTML = `<span>⚠️ Conceptual Trap Detected!</span> <span class="font-normal text-amber-700">Correct Option is ${String.fromCharCode(65 + result.correct_index)}.</span>`;
            }
            expBody.innerText = result.explanation;
        }

    } catch (e) {
        console.error("Failed to verify MCQ:", e);
    }
}

function nextArenaQuestion() {
    if (arenaCurrentIndex < arenaQuestions.length - 1) {
        arenaCurrentIndex++;
        renderArenaQuestion();
    } else {
        showArenaCompletion();
    }
}

function prevArenaQuestion() {
    if (arenaCurrentIndex > 0) {
        arenaCurrentIndex--;
        renderArenaQuestion();
    }
}

function showArenaCompletion() {
    const qCard = document.getElementById("arenaQuestionCard");
    const completionCard = document.getElementById("arenaCompletionCard");
    if (qCard) qCard.classList.add("hidden");
    if (completionCard) completionCard.classList.remove("hidden");

    const phaseTitles = {
        'basic': 'Phase 1: Foundation (Basic)',
        'intermediate': 'Phase 2: Production Engineering (Intermediate)',
        'advanced': 'Phase 3: High Scale & Architecture (Advanced)',
        '': 'All 20 Questions'
    };

    const compTitle = document.getElementById("arenaCompletionTitle");
    const compSubtitle = document.getElementById("arenaCompletionSubtitle");
    const finalScore = document.getElementById("arenaFinalScore");
    const finalStreak = document.getElementById("arenaFinalStreak");

    if (compTitle) compTitle.innerText = `${phaseTitles[arenaPhase] || 'Assessment'} Complete!`;
    const accuracy = arenaQuestions.length > 0 ? Math.round((arenaScore / arenaQuestions.length) * 100) : 100;
    if (compSubtitle) compSubtitle.innerText = `You scored ${arenaScore} out of ${arenaQuestions.length} (${accuracy}% accuracy) with a top streak of ${arenaBestStreak}!`;
    if (finalScore) finalScore.innerText = `${arenaScore} / ${arenaQuestions.length} (${accuracy}%)`;
    if (finalStreak) finalStreak.innerText = `${arenaBestStreak} 🔥`;

    const advanceBtn = document.getElementById("arenaAdvancePhaseBtn");
    if (advanceBtn) {
        if (arenaPhase === 'basic') {
            advanceBtn.innerHTML = `<span>Advance to Phase 2: Intermediate</span> <span>→</span>`;
            advanceBtn.onclick = () => switchArenaPhase('intermediate');
            advanceBtn.classList.remove("hidden");
        } else if (arenaPhase === 'intermediate') {
            advanceBtn.innerHTML = `<span>Advance to Phase 3: Advanced</span> <span>→</span>`;
            advanceBtn.onclick = () => switchArenaPhase('advanced');
            advanceBtn.classList.remove("hidden");
        } else {
            advanceBtn.innerHTML = `<span>Review All 20 Questions</span> <span>→</span>`;
            advanceBtn.onclick = () => switchArenaPhase('');
        }
    }
}

function restartCurrentPhaseQuiz() {
    startMcqQuiz(arenaPhase);
}

function advanceToNextPhase() {
    if (arenaPhase === 'basic') {
        switchArenaPhase('intermediate');
    } else if (arenaPhase === 'intermediate') {
        switchArenaPhase('advanced');
    } else {
        switchArenaPhase('');
    }
}

function revealArenaInStudio() {
    if (!arenaQuestions.length) return;
    const q = arenaQuestions[arenaCurrentIndex];
    switchAppMode('studio');
    selectQuestion(q.id);
}

function switchSidebarTab(tab) {
    const qBtn = document.getElementById("tabQuestionsBtn");
    const mBtn = document.getElementById("tabMindmapBtn");
    const qPanel = document.getElementById("sidebarQuestionsPanel");
    const mPanel = document.getElementById("sidebarMindmapPanel");
    const visual = document.getElementById("mindmapVisualSection");

    if (tab === "questions") {
        if (qBtn) qBtn.className = "flex-1 py-3 text-center border-b-2 border-indigo-600 text-indigo-600 bg-white font-bold transition flex items-center justify-center gap-1.5";
        if (mBtn) mBtn.className = "flex-1 py-3 text-center text-slate-500 hover:text-slate-800 font-medium transition flex items-center justify-center gap-1.5";
        if (qPanel) qPanel.classList.remove("hidden");
        if (mPanel) mPanel.classList.add("hidden");
    } else {
        if (mBtn) mBtn.className = "flex-1 py-3 text-center border-b-2 border-indigo-600 text-indigo-600 bg-white font-bold transition flex items-center justify-center gap-1.5";
        if (qBtn) qBtn.className = "flex-1 py-3 text-center text-slate-500 hover:text-slate-800 font-medium transition flex items-center justify-center gap-1.5";
        if (mPanel) mPanel.classList.remove("hidden");
        if (qPanel) qPanel.classList.add("hidden");
        if (visual) visual.classList.remove("hidden");
    }
}

function switchIbTab(tab) {
    currentIbTab = tab;
    const btnProblem = document.getElementById("ibTabProblemBtn");
    const btnEditorial = document.getElementById("ibTabEditorialBtn");
    const btnCopilot = document.getElementById("ibTabCopilotBtn");

    const contentProblem = document.getElementById("ibTabProblemContent");
    const contentEditorial = document.getElementById("ibTabEditorialContent");
    const contentCopilot = document.getElementById("ibTabCopilotContent");

    [btnProblem, btnEditorial, btnCopilot].forEach(btn => {
        if (btn) btn.classList.remove("active");
    });

    if (contentProblem) contentProblem.classList.add("hidden");
    if (contentEditorial) contentEditorial.classList.add("hidden");
    if (contentCopilot) contentCopilot.classList.add("hidden");

    if (tab === "problem") {
        if (btnProblem) btnProblem.classList.add("active");
        if (contentProblem) contentProblem.classList.remove("hidden");
    } else if (tab === "editorial") {
        if (btnEditorial) btnEditorial.classList.add("active");
        if (contentEditorial) contentEditorial.classList.remove("hidden");
        const walkCard = document.getElementById("solutionWalkthroughCard");
        if (walkCard) walkCard.classList.remove("hidden");
    } else if (tab === "copilot") {
        if (btnCopilot) btnCopilot.classList.add("active");
        if (contentCopilot) contentCopilot.classList.remove("hidden");
        const stream = document.getElementById("copilotChatStream");
        if (stream) stream.scrollTop = stream.scrollHeight;
    }
}

async function requestCopilotPrompt(promptType) {
    if (!currentQuestion) {
        showToast("Please select a question first!");
        return;
    }

    switchIbTab("copilot");

    const stream = document.getElementById("copilotChatStream");
    const pyCode = document.getElementById("pythonCodeInput")?.value || "";
    const sqlCode = document.getElementById("sqlQueryInput")?.value || "";

    const promptLabels = {
        "eli5": "💬 Explain this to me like I'm 5 (ELI5)",
        "hint": "💡 Give me an architectural blueprint hint",
        "complexity": "⏱️ Audit Big-O time and space complexity of my code",
        "debug": "🐞 Review my code for edge cases, common traps, and race conditions",
        "cross_question": "🔥 Grill me with an Amazon/Google Staff Principal cross-question"
    };

    const userLabel = promptLabels[promptType] || `Prompt: ${promptType}`;

    if (stream) {
        const userDiv = document.createElement("div");
        userDiv.className = "copilot-msg-user";
        userDiv.innerHTML = `<span class="font-bold text-indigo-300">Candidate:</span> ${userLabel}`;
        stream.appendChild(userDiv);

        const typingDiv = document.createElement("div");
        typingDiv.id = "copilotTypingIndicator";
        typingDiv.className = "copilot-typing";
        typingDiv.innerHTML = `
            <div class="copilot-dot"></div>
            <div class="copilot-dot"></div>
            <div class="copilot-dot"></div>
            <span>Senior Staff AI Copilot is analyzing...</span>
        `;
        stream.appendChild(typingDiv);
        stream.scrollTop = stream.scrollHeight;
    }

    try {
        const res = await fetch("/api/v1/interview/copilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: activeSessionId,
                question_id: currentQuestion.id,
                prompt_type: promptType,
                candidate_code: pyCode,
                candidate_sql: sqlCode
            })
        });

        const data = await res.json();
        const typingEl = document.getElementById("copilotTypingIndicator");
        if (typingEl) typingEl.remove();

        if (stream) {
            const aiDiv = document.createElement("div");
            aiDiv.className = "copilot-msg-ai";
            let chipsHtml = "";
            if (data.action_chips && data.action_chips.length > 0) {
                chipsHtml = `
                    <div class="flex flex-wrap gap-1 mt-3 pt-2 border-t border-slate-200">
                        ${data.action_chips.map(chip => `
                            <button onclick="handleCopilotActionChip('${chip.replace(/'/g, "\\'")}')" class="copilot-chip text-[10px]">
                                ${chip}
                            </button>
                        `).join('')}
                    </div>
                `;
            }
            aiDiv.innerHTML = `
                <div class="flex items-center gap-1.5 font-bold text-indigo-900 text-xs mb-1.5">
                    <span>🤖</span>
                    <span>Senior Staff AI Copilot</span>
                </div>
                <div class="text-slate-800 leading-relaxed font-normal">${formatMarkdown(data.reply)}</div>
                ${chipsHtml}
            `;
            stream.appendChild(aiDiv);
            stream.scrollTop = stream.scrollHeight;
        }
    } catch (err) {
        const typingEl = document.getElementById("copilotTypingIndicator");
        if (typingEl) typingEl.remove();
        if (stream) {
            const errDiv = document.createElement("div");
            errDiv.className = "copilot-msg-ai text-rose-600";
            errDiv.innerText = `Error querying AI Copilot: ${err.message}`;
            stream.appendChild(errDiv);
        }
    }
}

async function sendCandidateCustomPrompt() {
    if (!currentQuestion) {
        showToast("Please select a question first!");
        return;
    }

    const input = document.getElementById("candidateResponseInput");
    const promptText = (input?.value || "").trim();
    if (!promptText) {
        showToast("Please type a question or thought for the Copilot!");
        return;
    }

    switchIbTab("copilot");

    const stream = document.getElementById("copilotChatStream");
    const pyCode = document.getElementById("pythonCodeInput")?.value || "";
    const sqlCode = document.getElementById("sqlQueryInput")?.value || "";

    if (stream) {
        const userDiv = document.createElement("div");
        userDiv.className = "copilot-msg-user";
        userDiv.innerHTML = `<span class="font-bold text-indigo-300">Candidate:</span> ${escapeHtml(promptText)}`;
        stream.appendChild(userDiv);

        const typingDiv = document.createElement("div");
        typingDiv.id = "copilotTypingIndicator";
        typingDiv.className = "copilot-typing";
        typingDiv.innerHTML = `
            <div class="copilot-dot"></div>
            <div class="copilot-dot"></div>
            <div class="copilot-dot"></div>
            <span>AI Copilot is reviewing...</span>
        `;
        stream.appendChild(typingDiv);
        stream.scrollTop = stream.scrollHeight;
    }

    try {
        const res = await fetch("/api/v1/interview/copilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: activeSessionId,
                question_id: currentQuestion.id,
                prompt_type: "custom",
                user_prompt: promptText,
                candidate_code: pyCode,
                candidate_sql: sqlCode
            })
        });

        const data = await res.json();
        const typingEl = document.getElementById("copilotTypingIndicator");
        if (typingEl) typingEl.remove();

        if (stream) {
            const aiDiv = document.createElement("div");
            aiDiv.className = "copilot-msg-ai";
            aiDiv.innerHTML = `
                <div class="flex items-center gap-1.5 font-bold text-indigo-900 text-xs mb-1.5">
                    <span>🤖</span>
                    <span>Senior Staff AI Copilot</span>
                </div>
                <div class="text-slate-800 leading-relaxed font-normal">${formatMarkdown(data.reply)}</div>
            `;
            stream.appendChild(aiDiv);
            stream.scrollTop = stream.scrollHeight;
        }
    } catch (err) {
        const typingEl = document.getElementById("copilotTypingIndicator");
        if (typingEl) typingEl.remove();
        if (stream) {
            const errDiv = document.createElement("div");
            errDiv.className = "copilot-msg-ai text-rose-600";
            errDiv.innerText = `Error querying AI Copilot: ${err.message}`;
            stream.appendChild(errDiv);
        }
    }
}

function handleCopilotActionChip(chipText) {
    if (chipText.includes("ELI5") || chipText.includes("Explain")) {
        requestCopilotPrompt("eli5");
    } else if (chipText.includes("hint") || chipText.includes("Hint")) {
        requestCopilotPrompt("hint");
    } else if (chipText.includes("Big-O") || chipText.includes("Complexity")) {
        requestCopilotPrompt("complexity");
    } else if (chipText.includes("Trap") || chipText.includes("Traps") || chipText.includes("debug")) {
        requestCopilotPrompt("debug");
    } else if (chipText.includes("cross") || chipText.includes("Grill") || chipText.includes("follow-up")) {
        requestCopilotPrompt("cross_question");
    } else {
        const input = document.getElementById("candidateResponseInput");
        if (input) {
            input.value = `Addressing: ${chipText}\n`;
            input.focus();
        }
    }
}

function runActiveSandbox() {
    if (activeSandboxTab === "python") {
        runPythonCode();
    } else if (activeSandboxTab === "sql") {
        runSQLCode();
    } else if (activeSandboxTab === "redis") {
        runRedisCode();
    } else if (activeSandboxTab === "nosql") {
        runNoSQLCode();
    }
}

function copyActiveCode() {
    if (activeSandboxTab === "python") {
        copyToClipboard('pythonCodeInput', 'Python code copied!');
    } else if (activeSandboxTab === "sql") {
        copyToClipboard('sqlQueryInput', 'SQL query copied!');
    } else if (activeSandboxTab === "redis") {
        copyToClipboard('redisCommandInput', 'Redis commands copied!');
    } else if (activeSandboxTab === "nosql") {
        copyToClipboard('nosqlQueryInput', 'MongoDB query copied!');
    }
}

function switchSandboxTab(tab) {
    activeSandboxTab = tab;
    const pySection = document.getElementById("pythonCellSection");
    const sqlSection = document.getElementById("sqlCellSection");
    const redisSection = document.getElementById("redisCellSection");
    const nosqlSection = document.getElementById("nosqlCellSection");

    const btnPy = document.getElementById("tabPyBtn");
    const btnSql = document.getElementById("tabSqlBtn");
    const btnRedis = document.getElementById("tabRedisBtn");
    const btnNosql = document.getElementById("tabNosqlBtn");

    const inactiveClass = "px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5 font-medium";

    [btnPy, btnSql, btnRedis, btnNosql].forEach(btn => {
        if (btn) btn.className = inactiveClass;
    });

    if (pySection) pySection.classList.add("hidden");
    if (sqlSection) sqlSection.classList.add("hidden");
    if (redisSection) redisSection.classList.add("hidden");
    if (nosqlSection) nosqlSection.classList.add("hidden");

    if (tab === "python") {
        if (pySection) pySection.classList.remove("hidden");
        if (btnPy) btnPy.className = "px-3 py-1.5 rounded-lg bg-[#1e293b] text-emerald-400 shadow-2xs font-bold transition flex items-center gap-1.5 border border-emerald-500/20";
    } else if (tab === "sql") {
        if (sqlSection) sqlSection.classList.remove("hidden");
        if (btnSql) btnSql.className = "px-3 py-1.5 rounded-lg bg-[#1e293b] text-blue-400 shadow-2xs font-bold transition flex items-center gap-1.5 border border-blue-500/20";
    } else if (tab === "redis") {
        if (redisSection) redisSection.classList.remove("hidden");
        if (btnRedis) btnRedis.className = "px-3 py-1.5 rounded-lg bg-[#1e293b] text-rose-400 shadow-2xs font-bold transition flex items-center gap-1.5 border border-rose-500/20";
    } else if (tab === "nosql") {
        if (nosqlSection) nosqlSection.classList.remove("hidden");
        if (btnNosql) btnNosql.className = "px-3 py-1.5 rounded-lg bg-[#1e293b] text-emerald-400 shadow-2xs font-bold transition flex items-center gap-1.5 border border-emerald-500/20";
    }
}


// ----------------------------------------------------
// ----------------------------------------------------
// Centralized Phase Counters & Concept Hub (IB / GFG Reference)
// ----------------------------------------------------
async function updatePhaseCounts() {
    try {
        const res = await fetch("/api/v1/questions/phases");
        if (!res.ok) return;
        const data = await res.json();
        const phases = data.phases || [];
        const total = data.total_questions || 1020;

        const basicPhase = phases.find(p => p.id === 'basic');
        const interPhase = phases.find(p => p.id === 'intermediate');
        const advPhase = phases.find(p => p.id === 'advanced');

        const btnBasic = document.getElementById("phaseBtnBasic");
        const btnInter = document.getElementById("phaseBtnInter");
        const btnAdv = document.getElementById("phaseBtnAdv");
        const labelAll = document.getElementById("labelPhaseAll");

        if (btnBasic && basicPhase) {
            const badge = btnBasic.querySelector("span:nth-child(3)");
            if (badge) badge.innerText = `${basicPhase.count} Qs`;
        }
        if (btnInter && interPhase) {
            const badge = btnInter.querySelector("span:nth-child(3)");
            if (badge) badge.innerText = `${interPhase.count} Qs`;
        }
        if (btnAdv && advPhase) {
            const badge = btnAdv.querySelector("span:nth-child(3)");
            if (badge) badge.innerText = `${advPhase.count} Qs`;
        }
        if (labelAll) {
            labelAll.innerText = `⚡ All (${total} Qs)`;
        }
    } catch (e) {
        console.warn("Could not fetch phase counts:", e);
    }
}

async function loadConceptsHub() {
    const container = document.getElementById("conceptsListContainer");
    if (!container) return;

    if (allMasterConcepts.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-slate-400 text-xs font-medium animate-pulse">Loading centralized master concepts...</div>`;
        try {
            const res = await fetch("/api/v1/questions/concepts");
            allMasterConcepts = await res.json();
        } catch (err) {
            container.innerHTML = `<div class="p-4 text-rose-600 text-xs font-semibold">Error loading concept guide: ${err.message}</div>`;
            return;
        }
    }
    renderConceptsList();
}

function renderConceptsList() {
    const container = document.getElementById("conceptsListContainer");
    if (!container) return;

    const searchTerm = (document.getElementById("conceptSearchInput")?.value || "").toLowerCase().trim();
    let filtered = allMasterConcepts;

    if (currentConceptCategory) {
        filtered = filtered.filter(c => c.category === currentConceptCategory);
    }
    if (searchTerm) {
        filtered = filtered.filter(c => 
            (c.title || "").toLowerCase().includes(searchTerm) ||
            (c.summary || "").toLowerCase().includes(searchTerm) ||
            (c.interview_punchline || "").toLowerCase().includes(searchTerm) ||
            (c.key_mechanisms || []).some(m => m.toLowerCase().includes(searchTerm))
        );
    }

    if (!filtered.length) {
        container.innerHTML = `
            <div class="p-10 text-center bg-white rounded-xl border border-slate-200 text-slate-500 text-xs space-y-2">
                <p class="font-bold text-slate-700 text-sm">No matching concept guide found.</p>
                <p>Try searching for "B-Tree", "GIL", "Cache Stampede", "Outbox", or "Memory Model".</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(concept => `
        <div class="premium-card p-6 bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:shadow-sm transition space-y-4">
            <div class="flex items-start justify-between gap-4 border-b border-slate-100 pb-3">
                <div class="space-y-1">
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-mono uppercase bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded-full font-bold">
                            ${concept.category_name}
                        </span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                            ⭐ ${concept.badge}
                        </span>
                        <span class="text-[10px] text-slate-400 font-mono font-medium">${concept.difficulty}</span>
                    </div>
                    <h3 class="text-base font-extrabold text-slate-900 tracking-tight">${concept.title}</h3>
                </div>
                ${concept.related_slugs && concept.related_slugs.length ? `
                    <button onclick="solveRelatedQuestion('${concept.related_slugs[0]}')" class="px-3 py-1.5 text-xs rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold transition flex items-center gap-1.5 shadow-2xs shrink-0">
                        <span>▶</span> Practice in Sandbox
                    </button>
                ` : ''}
            </div>

            <p class="text-xs text-slate-700 leading-relaxed font-medium">
                ${concept.summary}
            </p>

            <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 space-y-2">
                <div class="text-[11px] font-bold text-slate-700 flex items-center gap-1.5">
                    <span>⚙️</span> Under The Hood Mechanisms:
                </div>
                <ul class="text-xs text-slate-600 space-y-1 list-disc list-inside">
                    ${(concept.key_mechanisms || []).map(m => `<li>${m}</li>`).join('')}
                </ul>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                ${concept.complexity ? `
                    <div class="bg-indigo-50/50 border border-indigo-100 rounded-lg p-3">
                        <div class="text-[10px] font-mono font-bold text-indigo-700 uppercase tracking-wide">Time & Space Complexity</div>
                        <div class="text-slate-800 font-mono text-[11px] font-semibold mt-0.5">${concept.complexity}</div>
                    </div>
                ` : ''}
                <div class="bg-emerald-50/50 border border-emerald-100 rounded-lg p-3">
                    <div class="text-[10px] font-mono font-bold text-emerald-800 uppercase tracking-wide">30-Second Interview Punchline</div>
                    <div class="text-slate-800 italic text-[11px] font-medium mt-0.5">"${concept.interview_punchline}"</div>
                </div>
            </div>

            ${concept.code_snippet ? `
                <div class="ide-window text-xs rounded-lg overflow-hidden border border-slate-800">
                    <div class="ide-header py-1.5 px-3 bg-slate-900 flex items-center justify-between">
                        <span class="text-[10px] font-mono text-slate-400">REFERENCE IMPLEMENTATION</span>
                        <button onclick="navigator.clipboard.writeText(\`${concept.code_snippet.replace(/`/g, '\\`')}\`); showToast('Snippet copied!');" class="text-[10px] text-slate-400 hover:text-white underline">Copy</button>
                    </div>
                    <pre class="p-3 bg-slate-950 text-emerald-400 font-mono text-[11px] overflow-x-auto"><code>${concept.code_snippet}</code></pre>
                </div>
            ` : ''}
        </div>
    `).join('');
}

function filterConceptsList() {
    renderConceptsList();
}

function filterConceptsByCategory(cat, btnEl) {
    currentConceptCategory = cat;
    document.querySelectorAll("#conceptCategoryChips button").forEach(b => {
        b.className = "px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold shrink-0 transition";
    });
    if (btnEl) {
        btnEl.className = "px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-bold shrink-0 shadow-2xs transition";
    }
    renderConceptsList();
}

async function solveRelatedQuestion(slug) {
    switchAppMode('studio');
    try {
        const res = await fetch(`/api/v1/questions/${slug}`);
        if (res.ok) {
            const q = await res.json();
            await selectQuestion(q.id);
            showToast(`Loaded scenario: ${q.title}`);
        }
    } catch (err) {
        console.error("Failed to load related question:", err);
    }
}

// Global Window Export (ensures 100% operational buttons)
// ----------------------------------------------------
window.switchSidebarTab = switchSidebarTab;
window.switchSandboxTab = switchSandboxTab;
window.selectRoadmapStage = selectRoadmapStage;
window.copyToClipboard = copyToClipboard;
window.showToast = showToast;
window.giveArchitecturalHint = giveArchitecturalHint;
window.clearCandidateAnswer = clearCandidateAnswer;
window.toggleMindmapFullscreen = toggleMindmapFullscreen;
window.runPythonCode = runPythonCode;
window.runSQLCode = runSQLCode;
window.runRedisCode = runRedisCode;
window.runNoSQLCode = runNoSQLCode;
window.submitToAIInterviewer = submitToAIInterviewer;
window.injectCrossQuestion = injectCrossQuestion;
window.injectCrossQuestionByIndex = injectCrossQuestionByIndex;
window.revealSolution = revealSolution;
window.resetStarterCode = resetStarterCode;
window.filterByDomain = filterByDomain;
window.selectQuestion = selectQuestion;
window.renderMindmap = renderMindmap;
window.toggleEasyWalkthrough = toggleEasyWalkthrough;
window.selectCareerPhase = selectCareerPhase;
window.switchAppMode = switchAppMode;
window.switchArenaPhase = switchArenaPhase;
window.selectArenaOption = selectArenaOption;
window.nextArenaQuestion = nextArenaQuestion;
window.prevArenaQuestion = prevArenaQuestion;
window.revealArenaInStudio = revealArenaInStudio;
window.restartCurrentPhaseQuiz = restartCurrentPhaseQuiz;
window.advanceToNextPhase = advanceToNextPhase;
window.selectQuestionMcq = selectQuestionMcq;
window.resetCurrentMcq = resetCurrentMcq;
window.toggleMostAskedFilter = toggleMostAskedFilter;
window.loadConceptsHub = loadConceptsHub;
window.filterConceptsList = filterConceptsList;
window.filterConceptsByCategory = filterConceptsByCategory;
window.solveRelatedQuestion = solveRelatedQuestion;



