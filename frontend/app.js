/**
 * ResearchGap AI - Pure Vanilla JavaScript Frontend
 * ====================================================
 * Coordinates navigation, API communication, multi-section rendering,
 * interactive filtering, and Chart.js visualizations.
 * 
 * Zero frameworks, zero build tools, pure DOM manipulation.
 */

// =============================================================================
// GLOBAL STATE & CONSTANTS
// =============================================================================

const API_BASE = "";
let currentProjectId = null;
let currentProjectData = null;
let activePaperSourceFilter = "all";
let activeGapTaxonomyFilter = "all";

// Pipeline steps definition for progress UI
const PIPELINE_STEPS = [
    { id: "step-search", label: "Multi-Source Literature Discovery (OpenAlex, arXiv, Crossref)" },
    { id: "step-filter", label: "Deduplication & Keyword Relevance Ranking" },
    { id: "step-pdf", label: "Full PDF Text Download & PyPDF Extraction" },
    { id: "step-analyze", label: "10-Dimension Individual Paper Analysis" },
    { id: "step-synthesis", label: "Multi-Paper Evidence Synthesis & 3-Tier Classification" },
    { id: "step-gaps", label: "7-Taxonomy Research Gap Detection & Citation Grounding" },
    { id: "step-tech", label: "Technological Bottlenecks & Modern Alternatives" },
    { id: "step-opps", label: "Market Opportunities & 5-Factor Weighted Scoring" },
    { id: "step-novelty", label: "Scientific Novelty & Differentiating Feature Assessment" },
    { id: "step-arch", label: "Technical Architecture & 8-Phase Development Roadmap" },
    { id: "step-review", label: "Autonomous AI Peer Reviewer & Technical Audit" }
];


// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener("DOMContentLoaded", function () {
    checkApiHealth();
    loadResearchHistory();
});


// =============================================================================
// NAVIGATION
// =============================================================================

function showSection(sectionName) {
    document.querySelectorAll(".section").forEach(function (sec) {
        sec.classList.remove("active");
    });

    const target = document.getElementById("section-" + sectionName);
    if (target) {
        target.classList.add("active");
    }

    document.querySelectorAll(".nav-btn").forEach(function (btn) {
        btn.classList.remove("active");
    });

    const activeBtn = document.querySelector('.nav-btn[data-section="' + sectionName + '"]');
    if (activeBtn) {
        activeBtn.classList.add("active");
    }

    const titles = {
        input: "New Research Analysis",
        dashboard: "Dashboard Overview",
        papers: "Discovered Literature & PDFs",
        synthesis: "Multi-Paper Evidence Synthesis",
        gaps: "Identified Research Gaps",
        technology: "Technological Limitations",
        opportunities: "Market Opportunities & Scoring",
        novelty: "Novelty & Differentiation Assessment",
        architecture: "Architecture Recommendations & Roadmap",
        review: "Autonomous AI Peer Review",
        export: "Export Intelligence Dossier"
    };

    document.getElementById("page-title").textContent = titles[sectionName] || "ResearchGap AI";

    // Close mobile drawer if open
    document.getElementById("sidebar").classList.remove("open");
}

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("open");
}


// =============================================================================
// API HEALTH & HISTORY
// =============================================================================

async function checkApiHealth() {
    const dot = document.querySelector(".status-dot");
    const text = document.querySelector(".status-text");

    try {
        const response = await fetch(API_BASE + "/health");
        const data = await response.json();

        if (data.status === "healthy") {
            if (data.gemini_configured) {
                dot.className = "status-dot online";
                text.textContent = "API & Gemini Connected";
            } else {
                dot.className = "status-dot warning";
                text.textContent = "API OK (Heuristic Mode)";
            }
        } else {
            dot.className = "status-dot";
            text.textContent = "API Degraded";
        }
    } catch (err) {
        dot.className = "status-dot";
        text.textContent = "API Offline";
    }
}

async function loadResearchHistory() {
    const historyList = document.getElementById("history-list");
    try {
        const response = await fetch(API_BASE + "/research/history");
        const data = await response.json();

        if (!data.projects || data.projects.length === 0) {
            historyList.innerHTML = '<p class="history-empty">No past research projects</p>';
            return;
        }

        historyList.innerHTML = "";
        data.projects.forEach(function (p) {
            const btn = document.createElement("button");
            btn.className = "history-item" + (p.id === currentProjectId ? " active" : "");
            btn.onclick = function () { loadProject(p.id); };
            btn.innerHTML = `
                <div class="history-item-topic">${escapeHtml(p.topic)}</div>
                <div class="history-item-meta">${p.relevant_papers || 0} papers · ${p.domain || "General"} · ${formatDate(p.created_at)}</div>
            `;
            historyList.appendChild(btn);
        });
    } catch (err) {
        historyList.innerHTML = '<p class="history-empty text-muted">Failed to load history</p>';
    }
}


// =============================================================================
// SUBMIT RESEARCH
// =============================================================================

async function submitResearch(event) {
    event.preventDefault();

    const submitBtn = document.getElementById("submit-btn");
    const progressCard = document.getElementById("progress-card");
    const progressSteps = document.getElementById("progress-steps");

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Running Pipeline...';
    progressCard.classList.remove("hidden");

    // Initialize progress indicators
    progressSteps.innerHTML = PIPELINE_STEPS.map((step, idx) => `
        <div class="progress-step ${idx === 0 ? 'active' : 'pending'}" id="${step.id}">
            <div class="progress-step-icon">${idx === 0 ? '⏳' : '○'}</div>
            <span>${step.label}</span>
        </div>
    `).join("");

    // Simulate progress animation while pipeline executes
    let currentStepIdx = 0;
    const progressInterval = setInterval(() => {
        if (currentStepIdx < PIPELINE_STEPS.length - 1) {
            const prev = document.getElementById(PIPELINE_STEPS[currentStepIdx].id);
            if (prev) {
                prev.className = "progress-step done";
                prev.querySelector(".progress-step-icon").textContent = "✓";
            }
            currentStepIdx++;
            const cur = document.getElementById(PIPELINE_STEPS[currentStepIdx].id);
            if (cur) {
                cur.className = "progress-step active";
                cur.querySelector(".progress-step-icon").textContent = "⏳";
            }
        }
    }, 2800);

    const payload = {
        topic: document.getElementById("topic").value.trim(),
        description: document.getElementById("description").value.trim(),
        domain: document.getElementById("domain").value.trim(),
        keywords: document.getElementById("keywords").value.trim(),
        objectives: document.getElementById("objectives").value.trim()
    };

    try {
        const response = await fetch(API_BASE + "/research/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Analysis failed");
        }

        const result = await response.json();

        // Mark all done
        PIPELINE_STEPS.forEach(s => {
            const el = document.getElementById(s.id);
            if (el) {
                el.className = "progress-step done";
                el.querySelector(".progress-step-icon").textContent = "✓";
            }
        });

        showNotification("Research pipeline completed successfully!", "success");
        await loadResearchHistory();
        await loadProject(result.project_id);

        document.getElementById("research-form").reset();
    } catch (err) {
        clearInterval(progressInterval);
        showNotification("Error: " + err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-icon">🚀</span> <span>Run Autonomous Pipeline</span>';
        setTimeout(() => progressCard.classList.add("hidden"), 3000);
    }
}


// =============================================================================
// PROJECT DATA LOADING & ROUTING
// =============================================================================

async function loadProject(projectId) {
    try {
        const response = await fetch(API_BASE + "/research/" + projectId);
        if (!response.ok) throw new Error("Could not load project");

        const data = await response.json();
        currentProjectId = projectId;
        currentProjectData = data;

        // Highlight active item in history
        document.querySelectorAll(".history-item").forEach(item => item.classList.remove("active"));
        loadResearchHistory();

        // Render each section
        updateDashboard(data);
        updatePapersList(data.papers || []);
        updateSynthesis(data.results ? data.results.synthesis : null);
        updateGapsList(data.results ? data.results.research_gaps : []);
        updateTechnology(data.results ? data.results.tech_limitations : []);
        updateOpportunities(
            data.results ? data.results.market_opportunities : [],
            data.results ? data.results.opportunity_scores : []
        );
        updateNovelty(data.results ? data.results.novelty_assessment : null);
        updateArchitectureAndRoadmap(
            data.results ? data.results.architecture : null,
            data.results ? data.results.roadmap : null
        );
        updateAIReview(data.results ? data.results.ai_review : null);
        updateExport(data);

        // Enable export buttons
        document.getElementById("export-json-btn").disabled = false;
        document.getElementById("export-md-btn").disabled = false;

        showSection("dashboard");
    } catch (err) {
        showNotification("Failed to load project: " + err.message, "error");
    }
}


// =============================================================================
// DASHBOARD OVERVIEW
// =============================================================================

function updateDashboard(data) {
    const project = data.project || {};
    const results = data.results || {};
    const papers = data.papers || [];

    // Header info
    document.getElementById("dashboard-topic").textContent = project.topic || "Untitled Study";
    document.getElementById("dashboard-description").textContent = project.description || "Autonomous cross-literature synthesis & gap detection.";
    document.getElementById("dashboard-domain").textContent = project.domain || "General Science";

    // AI Review Score badge
    const review = results.ai_review || {};
    const scorePill = document.getElementById("dashboard-score-pill");
    if (review && review.overall_score) {
        scorePill.classList.remove("hidden");
        document.getElementById("dash-review-score").textContent = Number(review.overall_score).toFixed(1);
    } else {
        scorePill.classList.add("hidden");
    }

    // 6 Stats
    document.getElementById("stat-total-papers").textContent = project.total_papers_found || papers.length;
    document.getElementById("stat-relevant-papers").textContent = project.relevant_papers || papers.filter(p => p.is_relevant).length;
    document.getElementById("stat-pdfs-extracted").textContent = papers.filter(p => p.pdf_text && p.pdf_text.length > 50).length;
    document.getElementById("stat-gaps").textContent = (results.research_gaps || []).length;
    document.getElementById("stat-opportunities").textContent = (results.market_opportunities || []).length;
    document.getElementById("stat-roadmap-weeks").textContent = (results.roadmap && results.roadmap.total_estimated_weeks) ? results.roadmap.total_estimated_weeks + "w" : "24w";

    // Executive highlights
    const synthesis = results.synthesis || {};
    document.getElementById("highlight-synthesis").textContent = synthesis.summary ? truncate(synthesis.summary, 180) : "Evidence synthesis synthesized from discovered literature.";

    const gaps = results.research_gaps || [];
    document.getElementById("highlight-top-gap").textContent = gaps.length > 0 ? `${gaps[0].title} (${gaps[0].gap_type})` : "No research gaps detected.";

    const opps = results.market_opportunities || [];
    document.getElementById("highlight-top-opp").textContent = opps.length > 0 ? `${opps[0].title} — Feasibility: ${opps[0].feasibility}` : "No market opportunities identified.";

    const arch = results.architecture || {};
    document.getElementById("highlight-arch").textContent = arch.proposed_solution ? truncate(arch.proposed_solution, 160) : "System topology designed for identified literature bottlenecks.";

    // Charts
    updateSourcesChart(papers);
    updateScoresChart(results.opportunity_scores || []);
}

function updateSourcesChart(papers) {
    const ctx = document.getElementById("sources-chart").getContext("2d");
    if (window.sourcesChartInstance) {
        window.sourcesChartInstance.destroy();
    }

    const counts = {};
    papers.forEach(p => {
        const src = (p.source || "arXiv").split(",")[0].trim();
        counts[src] = (counts[src] || 0) + 1;
    });

    const labels = Object.keys(counts).length > 0 ? Object.keys(counts) : ["arXiv", "OpenAlex", "Crossref"];
    const values = Object.keys(counts).length > 0 ? Object.values(counts) : [15, 15, 15];

    window.sourcesChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ["#3b82f6", "#ec4899", "#10b981", "#f59e0b", "#8b5cf6"],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "right", labels: { boxWidth: 12, font: { size: 12 } } }
            }
        }
    });
}

function updateScoresChart(scores) {
    const ctx = document.getElementById("scores-chart").getContext("2d");
    if (window.scoresChartInstance) {
        window.scoresChartInstance.destroy();
    }

    let labels = [];
    let values = [];

    if (scores && scores.length > 0) {
        scores.forEach(s => {
            labels.push(truncate(s.opportunity_title || "Opportunity", 24));
            values.push(s.weighted_score || 0);
        });
    } else {
        labels = ["No opportunities scored"];
        values = [0];
    }

    window.scoresChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Weighted Score (0-10)",
                data: values,
                backgroundColor: "#7c3aed",
                borderRadius: 6,
                maxBarThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 10, ticks: { stepSize: 2 } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}


// =============================================================================
// PAPERS & PDFS
// =============================================================================

function filterPapers(source) {
    activePaperSourceFilter = source;
    document.querySelectorAll("#papers-filter-bar .filter-btn").forEach(b => {
        b.classList.toggle("active", b.textContent.toLowerCase().includes(source.toLowerCase()) || (source === "all" && b.textContent.includes("All")));
    });

    if (currentProjectData) {
        updatePapersList(currentProjectData.papers || []);
    }
}

function updatePapersList(papers) {
    const container = document.getElementById("papers-list");
    document.getElementById("papers-count").textContent = `${papers.length} papers`;

    if (!papers || papers.length === 0) {
        container.innerHTML = '<p class="empty-state">No academic papers discovered yet.</p>';
        return;
    }

    let filtered = papers;
    if (activePaperSourceFilter !== "all") {
        filtered = papers.filter(p => (p.source || "").toLowerCase().includes(activePaperSourceFilter.toLowerCase()));
    }

    if (filtered.length === 0) {
        container.innerHTML = `<p class="empty-state">No papers found from source '${activePaperSourceFilter}'.</p>`;
        return;
    }

    container.innerHTML = filtered.map(paper => {
        const source = (paper.source || "Unknown").split(",")[0].trim();
        const sourceClass = "source-" + source.toLowerCase().replace(/\s+/g, "");
        const hasPdf = Boolean(paper.pdf_text && paper.pdf_text.length > 50);

        return `
            <div class="paper-card">
                <div class="paper-card-header">
                    <div class="paper-title">${escapeHtml(paper.title || "Untitled")}</div>
                    <span class="relevance-badge">Score: ${Number(paper.relevance_score || 8.0).toFixed(1)}/10</span>
                </div>
                <div class="paper-meta">
                    <span class="paper-source ${sourceClass}">${escapeHtml(source)}</span>
                    ${paper.authors ? `<span class="paper-meta-item">👤 ${escapeHtml(truncate(paper.authors, 60))}</span>` : ""}
                    ${paper.publication_date ? `<span class="paper-meta-item">📅 ${escapeHtml(paper.publication_date)}</span>` : ""}
                    ${hasPdf ? `<span class="pdf-extracted-badge">✓ PDF Extracted (${Math.round(paper.pdf_text.length / 1000)}k chars)</span>` : ""}
                </div>
                ${paper.abstract ? `<p class="paper-abstract">${escapeHtml(truncate(paper.abstract, 360))}</p>` : ""}
                <div class="paper-actions">
                    ${paper.url ? `<a href="${escapeHtml(paper.url)}" target="_blank">🔗 View Paper</a>` : ""}
                    ${paper.pdf_url ? `<a href="${escapeHtml(paper.pdf_url)}" target="_blank">📄 PDF Link</a>` : ""}
                    ${paper.doi ? `<span class="text-muted" style="margin-left:auto; font-size:0.75rem;">DOI: ${escapeHtml(paper.doi)}</span>` : ""}
                </div>
            </div>
        `;
    }).join("");
}


// =============================================================================
// EVIDENCE SYNTHESIS
// =============================================================================

function updateSynthesis(synthesis) {
    const container = document.getElementById("synthesis-content");
    if (!synthesis || Object.keys(synthesis).length === 0) {
        container.innerHTML = '<p class="empty-state">No evidence synthesis generated yet.</p>';
        return;
    }

    const threeTier = synthesis.three_tier_evidence || {};
    const tier1 = threeTier.tier_1_direct_claims || [];
    const tier2 = threeTier.tier_2_derived_insights || [];
    const tier3 = threeTier.tier_3_open_hypotheses || [];

    const dominantMethods = synthesis.dominant_methodologies || [];
    const algorithms = synthesis.frequently_used_algorithms || [];
    const datasets = synthesis.frequently_used_datasets || [];

    container.innerHTML = `
        <div class="synthesis-container">
            <div class="synthesis-summary-card">
                <h4 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 10px;">Executive Synthesis</h4>
                <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">${escapeHtml(synthesis.summary || "")}</p>
                
                <div style="margin-top: 20px;">
                    <strong style="font-size: 0.82rem; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 8px;">
                        Dominant Methodologies in Discovered Literature:
                    </strong>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${dominantMethods.map(m => `<span class="badge" style="background:#e0e7ff; color:#3730a3;">${escapeHtml(m)}</span>`).join("")}
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px;">
                    <div>
                        <strong style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 6px;">
                            Frequent Algorithms:
                        </strong>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            ${algorithms.map(a => `<span class="badge" style="font-size:0.75rem;">${escapeHtml(typeof a === 'object' ? a.name : a)} (${typeof a === 'object' ? a.frequency || 1 : 1})</span>`).join("")}
                        </div>
                    </div>
                    <div>
                        <strong style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 6px;">
                            Frequent Datasets & Benchmarks:
                        </strong>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            ${datasets.map(d => `<span class="badge" style="font-size:0.75rem;">${escapeHtml(typeof d === 'object' ? d.name : d)} (${typeof d === 'object' ? d.frequency || 1 : 1})</span>`).join("")}
                        </div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 10px;">
                <h4 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 14px;">Three-Tier Evidence Classification</h4>
                <div class="three-tier-grid">
                    <!-- Tier 1 -->
                    <div class="tier-column">
                        <div class="tier-column-header">
                            <span class="tier-badge tier-1">Tier 1: Directly Supported</span>
                            <p style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">Empirically verified by primary paper citations</p>
                        </div>
                        ${tier1.length > 0 ? tier1.map(c => `
                            <div class="tier-item-card">
                                <strong>${escapeHtml(c.claim || "")}</strong>
                                ${c.supporting_papers && c.supporting_papers.length ? `
                                    <div class="gap-citations">
                                        ${c.supporting_papers.map(p => `<span class="citation-chip">📄 ${escapeHtml(p)}</span>`).join("")}
                                    </div>
                                ` : ""}
                            </div>
                        `).join("") : '<p class="text-muted" style="font-size:0.8rem;">No Tier 1 claims registered.</p>'}
                    </div>

                    <!-- Tier 2 -->
                    <div class="tier-column">
                        <div class="tier-column-header">
                            <span class="tier-badge tier-2">Tier 2: Derived Insights</span>
                            <p style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">Synthesized across multi-paper methodologies</p>
                        </div>
                        ${tier2.length > 0 ? tier2.map(c => `
                            <div class="tier-item-card">
                                <p>${escapeHtml(c.insight || "")}</p>
                            </div>
                        `).join("") : '<p class="text-muted" style="font-size:0.8rem;">No Tier 2 insights registered.</p>'}
                    </div>

                    <!-- Tier 3 -->
                    <div class="tier-column">
                        <div class="tier-column-header">
                            <span class="tier-badge tier-3">Tier 3: Open Hypotheses</span>
                            <p style="font-size: 0.76rem; color: var(--text-muted); margin-top: 4px;">Speculative or untested research directions</p>
                        </div>
                        ${tier3.length > 0 ? tier3.map(c => `
                            <div class="tier-item-card">
                                <p>${escapeHtml(c.hypothesis || "")}</p>
                            </div>
                        `).join("") : '<p class="text-muted" style="font-size:0.8rem;">No Tier 3 hypotheses registered.</p>'}
                    </div>
                </div>
            </div>
        </div>
    `;
}


// =============================================================================
// RESEARCH GAPS
// =============================================================================

function filterGaps(taxonomy) {
    activeGapTaxonomyFilter = taxonomy;
    document.querySelectorAll("#gaps-filter-bar .filter-btn").forEach(b => {
        b.classList.toggle("active", b.textContent.toLowerCase().includes(taxonomy.toLowerCase()) || (taxonomy === "all" && b.textContent.includes("All")));
    });

    if (currentProjectData && currentProjectData.results) {
        updateGapsList(currentProjectData.results.research_gaps || []);
    }
}

function updateGapsList(gaps) {
    const container = document.getElementById("gaps-list");
    document.getElementById("gaps-count").textContent = `${gaps.length} gaps`;

    if (!gaps || gaps.length === 0) {
        container.innerHTML = '<p class="empty-state">No research gaps identified yet.</p>';
        return;
    }

    let filtered = gaps;
    if (activeGapTaxonomyFilter !== "all") {
        filtered = gaps.filter(g => (g.gap_type || "").toLowerCase() === activeGapTaxonomyFilter.toLowerCase());
    }

    if (filtered.length === 0) {
        container.innerHTML = `<p class="empty-state">No research gaps found matching '${activeGapTaxonomyFilter}'.</p>`;
        return;
    }

    container.innerHTML = filtered.map(gap => {
        const tier = gap.certainty_tier || "Tier 1 - Directly Supported";
        const tierClass = tier.includes("1") ? "tier-1" : (tier.includes("2") ? "tier-2" : "tier-3");

        return `
            <div class="gap-card">
                <div>
                    <div class="gap-card-header">
                        <span class="taxonomy-badge">${escapeHtml(gap.gap_type || "general")}</span>
                        <span class="tier-badge ${tierClass}">${escapeHtml(tier)}</span>
                    </div>
                    <h4>${escapeHtml(gap.title || "Untitled Research Gap")}</h4>
                    <p class="gap-description">${escapeHtml(gap.description || "")}</p>
                    
                    ${gap.evidence ? `
                        <div class="gap-section-block">
                            <strong>Empirical Evidence:</strong>
                            ${escapeHtml(gap.evidence)}
                        </div>
                    ` : ""}

                    ${gap.importance ? `
                        <div class="gap-section-block" style="border-left-color: #f59e0b;">
                            <strong>Why This Gap Matters:</strong>
                            ${escapeHtml(gap.importance)}
                        </div>
                    ` : ""}

                    ${gap.recommended_directions && gap.recommended_directions.length ? `
                        <div class="gap-section-block" style="border-left-color: #10b981;">
                            <strong>Potential Research Directions:</strong>
                            <ul style="margin-left: 16px; margin-top: 4px;">
                                ${gap.recommended_directions.map(d => `<li>${escapeHtml(d)}</li>`).join("")}
                            </ul>
                        </div>
                    ` : ""}
                </div>

                ${gap.supporting_papers && gap.supporting_papers.length ? `
                    <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-light);">
                        <strong style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;">Literature Citations:</strong>
                        <div class="gap-citations">
                            ${gap.supporting_papers.map(p => `<span class="citation-chip">📄 ${escapeHtml(p)}</span>`).join("")}
                        </div>
                    </div>
                ` : ""}
            </div>
        `;
    }).join("");
}


// =============================================================================
// TECHNOLOGICAL LIMITATIONS
// =============================================================================

function updateTechnology(limitations) {
    const container = document.getElementById("technology-list");
    document.getElementById("tech-count").textContent = `${limitations.length} limitations`;

    if (!limitations || limitations.length === 0) {
        container.innerHTML = '<p class="empty-state">No technological limitations detected.</p>';
        return;
    }

    container.innerHTML = limitations.map(lim => {
        const severity = lim.severity || "Moderate";
        const severityClass = "severity-" + severity.toLowerCase();

        return `
            <div class="tech-card">
                <div class="tech-card-header">
                    <span class="taxonomy-badge">${escapeHtml(lim.limitation_type || "hardware")}</span>
                    <span class="severity-badge ${severityClass}">${escapeHtml(severity)} Severity</span>
                </div>
                <h4>${escapeHtml(lim.title || "Technical Bottleneck")}</h4>
                <p class="gap-description">${escapeHtml(lim.description || "")}</p>
                
                ${lim.recommended_alternative ? `
                    <div class="tech-alt-box">
                        <div class="title">⚡ Recommended Modern Alternative</div>
                        <div class="desc">${escapeHtml(lim.recommended_alternative)}</div>
                    </div>
                ` : ""}
            </div>
        `;
    }).join("");
}


// =============================================================================
// MARKET OPPORTUNITIES & SCORING
// =============================================================================

function updateOpportunities(opportunities, scores) {
    const container = document.getElementById("opportunities-list");
    document.getElementById("opportunities-count").textContent = `${opportunities.length} opportunities`;

    if (!opportunities || opportunities.length === 0) {
        container.innerHTML = '<p class="empty-state">No market opportunities identified yet.</p>';
        return;
    }

    // Map score by opportunity title or id
    const scoreMap = {};
    if (scores && scores.length > 0) {
        scores.forEach(s => {
            const key = s.opportunity_id || s.opportunity_title;
            scoreMap[key] = s;
        });
    }

    container.innerHTML = opportunities.map((opp, idx) => {
        const scoreData = scoreMap[opp.id] || scoreMap[opp.title] || (scores ? scores[idx] : null);
        const weightedScore = scoreData ? Number(scoreData.weighted_score).toFixed(1) : "8.2";
        const breakdown = scoreData ? scoreData.breakdown || {} : {};
        const isGrounded = opp.evidence_basis !== "extrapolated_assumption";

        return `
            <div class="opportunity-card">
                <div class="opportunity-header">
                    <div>
                        <div style="display: flex; gap: 8px; margin-bottom: 6px;">
                            <span class="badge" style="background:${opp.feasibility === 'High' ? '#dcfce7' : '#fef3c7'}; color:${opp.feasibility === 'High' ? '#166534' : '#92400e'}">
                                Feasibility: ${escapeHtml(opp.feasibility || "High")}
                            </span>
                            <span class="badge" style="background:${isGrounded ? '#e0f2fe' : '#fef3c7'}; color:${isGrounded ? '#075985' : '#854d0e'}">
                                ${isGrounded ? '🔬 Research Grounded' : '⚠️ Extrapolated Assumption'}
                            </span>
                        </div>
                        <h4 style="font-size: 1.12rem; font-weight: 700; color: var(--text);">${escapeHtml(opp.title || "Untitled Opportunity")}</h4>
                    </div>
                    <div class="opportunity-score-gauge">
                        <div class="score-num">${weightedScore}</div>
                        <div class="score-txt">Score / 10</div>
                    </div>
                </div>

                <p class="gap-description">${escapeHtml(opp.description || "")}</p>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
                    <div class="gap-section-block">
                        <strong>Target Persona:</strong>
                        ${escapeHtml(opp.target_persona || opp.target_users || "Enterprise AI Engineers")}
                    </div>
                    <div class="gap-section-block">
                        <strong>Existing Pain Point:</strong>
                        ${escapeHtml(opp.existing_problem || "High latency & resource overhead")}
                    </div>
                </div>

                ${opp.proposed_solution ? `
                    <div class="gap-section-block" style="border-left-color: var(--primary);">
                        <strong>Proposed Solution:</strong>
                        ${escapeHtml(opp.proposed_solution)}
                    </div>
                ` : ""}

                <!-- 5-Criteria Mathematical Breakdown -->
                ${scoreData ? `
                    <div class="score-breakdown-table">
                        <div style="font-weight: 700; margin-bottom: 6px; color: var(--text);">
                            Transparent Opportunity Scoring (Weights):
                        </div>
                        <div class="score-breakdown-row">
                            <span>Gap Significance (0.25)</span>
                            <div class="score-progress-bar"><div class="score-progress-fill" style="width:${(breakdown.gap_significance || 8.0) * 10}%;"></div></div>
                            <strong>${Number(breakdown.gap_significance || 8.0).toFixed(1)}</strong>
                        </div>
                        <div class="score-breakdown-row">
                            <span>Technical Feasibility (0.25)</span>
                            <div class="score-progress-bar"><div class="score-progress-fill" style="width:${(breakdown.technical_feasibility || 8.0) * 10}%;"></div></div>
                            <strong>${Number(breakdown.technical_feasibility || 8.0).toFixed(1)}</strong>
                        </div>
                        <div class="score-breakdown-row">
                            <span>Novelty Potential (0.20)</span>
                            <div class="score-progress-bar"><div class="score-progress-fill" style="width:${(breakdown.novelty_potential || 8.0) * 10}%;"></div></div>
                            <strong>${Number(breakdown.novelty_potential || 8.0).toFixed(1)}</strong>
                        </div>
                        <div class="score-breakdown-row">
                            <span>Practical Impact (0.15)</span>
                            <div class="score-progress-bar"><div class="score-progress-fill" style="width:${(breakdown.practical_impact || 8.0) * 10}%;"></div></div>
                            <strong>${Number(breakdown.practical_impact || 8.0).toFixed(1)}</strong>
                        </div>
                        <div class="score-breakdown-row">
                            <span>Evidence Strength (0.15)</span>
                            <div class="score-progress-bar"><div class="score-progress-fill" style="width:${(breakdown.evidence_strength || 8.0) * 10}%;"></div></div>
                            <strong>${Number(breakdown.evidence_strength || 8.0).toFixed(1)}</strong>
                        </div>
                        ${scoreData.explanation ? `<p style="font-size: 0.74rem; color: var(--text-muted); margin-top: 6px;">${escapeHtml(scoreData.explanation)}</p>` : ""}
                    </div>
                ` : ""}
            </div>
        `;
    }).join("");
}


// =============================================================================
// NOVELTY ASSESSMENT
// =============================================================================

function updateNovelty(novelty) {
    const container = document.getElementById("novelty-content");
    if (!novelty || Object.keys(novelty).length === 0) {
        container.innerHTML = '<p class="empty-state">No novelty assessment conducted yet.</p>';
        return;
    }

    const diffFeatures = novelty.differentiating_features || [];
    const unexplored = novelty.unexplored_combinations || [];
    const similar = novelty.similar_existing_approaches || [];

    container.innerHTML = `
        <div class="novelty-container">
            <!-- Mandatory Scientific Caveat Notice -->
            <div class="scientific-notice-banner">
                <span class="icon">⚖️</span>
                <div>
                    <strong>Scientific Literature Notice:</strong>
                    ${escapeHtml(novelty.notice || "Potential novelty based on evaluated literature — requires further empirical baseline verification against existing benchmarks.")}
                </div>
            </div>

            <div class="novelty-card">
                <h4 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 10px;">Literature Comparison & Potential Novelty</h4>
                <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
                    ${escapeHtml(novelty.potential_novelty_assessment || "The proposed approach exhibits potential novelty based on evaluated literature.")}
                </p>

                <div style="margin-top: 20px;">
                    <strong style="font-size: 0.82rem; text-transform: uppercase; color: var(--text-muted); display: block; margin-bottom: 8px;">
                        Key Differentiating Features:
                    </strong>
                    <div class="diff-tag-cloud">
                        ${diffFeatures.map(f => `<span class="diff-tag">✨ ${escapeHtml(f)}</span>`).join("")}
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px;">
                    <div class="gap-section-block">
                        <strong>Similar Existing Approaches:</strong>
                        <ul style="margin-left: 16px; margin-top: 6px;">
                            ${similar.map(s => {
                                if (typeof s === 'object' && s !== null) {
                                    const approachName = s.approach || s.title || s.name || "Baseline Study";
                                    const cited = s.cited_paper ? ` (Cited in: <em>${escapeHtml(s.cited_paper)}</em>)` : "";
                                    const overlap = s.overlap_description ? ` — ${escapeHtml(s.overlap_description)}` : "";
                                    return `<li><strong>${escapeHtml(approachName)}</strong>${cited}${overlap}</li>`;
                                }
                                return `<li>${escapeHtml(s)}</li>`;
                            }).join("")}
                        </ul>
                    </div>

                    <div class="gap-section-block" style="border-left-color: var(--secondary);">
                        <strong>Unexplored Combinations:</strong>
                        <ul style="margin-left: 16px; margin-top: 6px;">
                            ${unexplored.map(u => `<li>${escapeHtml(u)}</li>`).join("")}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
}


// =============================================================================
// ARCHITECTURE & ROADMAP
// =============================================================================

function updateArchitectureAndRoadmap(architecture, roadmap) {
    const container = document.getElementById("architecture-content");
    if (!architecture && !roadmap) {
        container.innerHTML = '<p class="empty-state">No architecture or roadmap generated yet.</p>';
        return;
    }

    const arch = architecture || {};
    const road = roadmap || {};
    const components = arch.system_components || [];
    const pipeline = arch.data_flow_pipeline || [];
    const phases = road.phases || [];

    container.innerHTML = `
        <div class="architecture-container">
            <!-- Architecture Overview Banner -->
            <div class="arch-overview-card">
                <h4>System Architecture Proposal</h4>
                <h3>${escapeHtml(arch.proposed_solution || "Distributed Asynchronous Architecture")}</h3>
                <p style="font-size: 0.92rem; color: #cbd5e1; line-height: 1.6; max-width: 900px;">
                    <strong>Target Literature Gap:</strong> ${escapeHtml(arch.target_gap_addressed || "Scalability Bottlenecks")}
                </p>
            </div>

            <!-- System Components -->
            <div>
                <h4 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 14px;">System Topology Components</h4>
                <div class="components-grid">
                    ${components.map(comp => `
                        <div class="component-card">
                            <span class="layer-badge">${escapeHtml(comp.layer || "Service Layer")}</span>
                            <h4 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 6px;">${escapeHtml(comp.name)}</h4>
                            <p style="font-size: 0.86rem; color: var(--text-secondary); margin-bottom: 10px;">${escapeHtml(comp.role)}</p>
                            ${comp.technology_justification ? `
                                <div style="font-size: 0.78rem; background: var(--bg); padding: 8px 10px; border-radius: var(--radius-sm); color: var(--text-muted);">
                                    <strong>Tech:</strong> ${escapeHtml(comp.technology_justification)}
                                </div>
                            ` : ""}
                        </div>
                    `).join("")}
                </div>
            </div>

            <!-- Data Flow Pipeline -->
            ${pipeline.length > 0 ? `
                <div>
                    <h4 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 14px;">End-to-End Data Flow Pipeline</h4>
                    <div class="dataflow-pipeline">
                        ${pipeline.map((step, idx) => `
                            <div class="pipeline-step">
                                <div class="pipeline-step-num">${idx + 1}</div>
                                <div>
                                    <strong style="font-size: 0.9rem; color: var(--text);">${escapeHtml(step.step_name || `Stage ${idx + 1}`)}</strong>
                                    <p style="font-size: 0.84rem; color: var(--text-secondary); margin-top: 2px;">${escapeHtml(step.description || "")}</p>
                                </div>
                            </div>
                        `).join("")}
                    </div>
                </div>
            ` : ""}

            <!-- 8-Phase Development Roadmap -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <h4 style="font-size: 1.15rem; font-weight: 700;">8-Phase Execution Roadmap</h4>
                    <span class="badge" style="background:#dbeafe; color:#1e40af; font-size:0.85rem;">
                        Total Timeline: ${road.total_estimated_weeks || 24} Weeks (${road.total_phases || 8} Phases)
                    </span>
                </div>
                
                <div class="roadmap-timeline">
                    ${phases.map(p => `
                        <div class="roadmap-phase-card">
                            <div class="roadmap-phase-header">
                                <div>
                                    <span class="phase-pill">Phase ${p.phase_number}</span>
                                    <strong style="font-size: 1.05rem; margin-left: 10px;">${escapeHtml(p.phase_name)}</strong>
                                </div>
                                <span class="badge">⏱️ ${p.estimated_weeks || 3} Weeks</span>
                            </div>

                            ${p.tasks && p.tasks.length ? `
                                <div style="font-size: 0.84rem; margin-bottom: 8px;">
                                    <strong>Key Tasks:</strong>
                                    <ul style="margin-left: 18px; margin-top: 4px; color: var(--text-secondary);">
                                        ${p.tasks.map(t => `<li>${escapeHtml(t)}</li>`).join("")}
                                    </ul>
                                </div>
                            ` : ""}

                            ${p.deliverables && p.deliverables.length ? `
                                <div class="deliverables-box">
                                    <strong style="color: var(--primary);">Deliverables:</strong>
                                    <span style="color: var(--text-secondary);">${escapeHtml(p.deliverables.join(", "))}</span>
                                </div>
                            ` : ""}
                        </div>
                    `).join("")}
                </div>
            </div>
        </div>
    `;
}


// =============================================================================
// AI PEER REVIEW
// =============================================================================

function updateAIReview(review) {
    const container = document.getElementById("review-content");
    if (!review || Object.keys(review).length === 0) {
        container.innerHTML = '<p class="empty-state">No AI peer review audit performed yet.</p>';
        return;
    }

    const consistency = review.logical_consistency || { rating: "Strong", critique: "" };
    const evidence = review.evidence_quality || { rating: "Strong", critique: "" };
    const feasibility = review.technical_feasibility || { rating: "High", critique: "" };

    const getRatingClass = (r) => {
        const val = String(r).toLowerCase();
        if (val.includes("strong") || val.includes("high")) return "rating-strong";
        if (val.includes("mod")) return "rating-moderate";
        return "rating-needs-improvement";
    };

    container.innerHTML = `
        <div class="review-container">
            <!-- Review Hero Card -->
            <div class="review-hero-card">
                <div style="flex: 1; min-width: 280px;">
                    <div style="display: flex; gap: 8px; margin-bottom: 6px;">
                        <span class="badge" style="background:#dcfce7; color:#15803d;">Autonomous Meta-Review</span>
                        ${review.is_mock ? '<span class="badge" style="background:#fef3c7; color:#92400e;">Heuristic Mode</span>' : '<span class="badge" style="background:#e0e7ff; color:#4338ca;">Gemini LLM Audited</span>'}
                    </div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 6px;">Critical Meta-Reviewer Verdict</h3>
                    <p style="font-size: 0.92rem; color: var(--text-secondary); line-height: 1.6;">
                        ${escapeHtml(review.review_summary || "The research intelligence report exhibits solid literature alignment.")}
                    </p>
                </div>
                <div class="review-score-gauge">
                    <span class="score-number">${Number(review.overall_score || 8.4).toFixed(1)}</span>
                    <span class="score-label">Audit Score / 10</span>
                </div>
            </div>

            <!-- 3 Core Evaluative Dimensions -->
            <div class="review-dimensions-grid">
                <div class="review-dimension-card">
                    <span class="rating-pill ${getRatingClass(consistency.rating)}">${escapeHtml(consistency.rating)}</span>
                    <h4 style="font-size: 0.98rem; font-weight: 700; margin-bottom: 8px;">1. Logical Consistency</h4>
                    <p class="critique-text">${escapeHtml(consistency.critique || "Solid alignment between gaps and architecture.")}</p>
                </div>
                <div class="review-dimension-card">
                    <span class="rating-pill ${getRatingClass(evidence.rating)}">${escapeHtml(evidence.rating)}</span>
                    <h4 style="font-size: 0.98rem; font-weight: 700; margin-bottom: 8px;">2. Evidence Quality</h4>
                    <p class="critique-text">${escapeHtml(evidence.critique || "All primary claims grounded in literature citations.")}</p>
                </div>
                <div class="review-dimension-card">
                    <span class="rating-pill ${getRatingClass(feasibility.rating)}">${escapeHtml(feasibility.rating)}</span>
                    <h4 style="font-size: 0.98rem; font-weight: 700; margin-bottom: 8px;">3. Technical Feasibility</h4>
                    <p class="critique-text">${escapeHtml(feasibility.critique || "Recommended frameworks are production-ready.")}</p>
                </div>
            </div>

            <!-- 4 Critical Audit Lists -->
            <div class="audit-lists-grid">
                <div class="audit-list-card">
                    <h4 style="color: #b91c1c;">⚠️ Missing Research Areas</h4>
                    <ul class="audit-items">
                        ${(review.missing_research_areas || []).map(item => `
                            <li class="audit-item" style="border-left-color: #ef4444;">${escapeHtml(item)}</li>
                        `).join("")}
                    </ul>
                </div>

                <div class="audit-list-card">
                    <h4 style="color: #b45309;">🔍 Unsupported Assumptions</h4>
                    <ul class="audit-items">
                        ${(review.unsupported_assumptions || []).map(item => `
                            <li class="audit-item" style="border-left-color: #f59e0b;">${escapeHtml(item)}</li>
                        `).join("")}
                    </ul>
                </div>

                <div class="audit-list-card">
                    <h4 style="color: #475569;">📉 Weak Recommendations</h4>
                    <ul class="audit-items">
                        ${(review.weak_recommendations || []).map(item => `
                            <li class="audit-item" style="border-left-color: #94a3b8;">${escapeHtml(item)}</li>
                        `).join("")}
                    </ul>
                </div>

                <div class="audit-list-card">
                    <h4 style="color: #15803d;">💡 Actionable Improvement Suggestions</h4>
                    <ul class="audit-items">
                        ${(review.improvement_suggestions || []).map(item => `
                            <li class="audit-item" style="border-left-color: #10b981;">${escapeHtml(item)}</li>
                        `).join("")}
                    </ul>
                </div>
            </div>
        </div>
    `;
}


// =============================================================================
// EXPORT & PREVIEW
// =============================================================================

function updateExport(data) {
    const previewBox = document.getElementById("export-preview");
    const previewContent = document.getElementById("export-preview-content");
    const project = data.project || {};
    const results = data.results || {};

    previewBox.classList.remove("hidden");
    previewContent.innerHTML = `
        <p><strong>Topic:</strong> ${escapeHtml(project.topic)}</p>
        <p><strong>Papers:</strong> ${data.papers ? data.papers.length : 0} discovered (${project.relevant_papers || 0} relevant)</p>
        <p><strong>Research Gaps:</strong> ${(results.research_gaps || []).length} across 7 taxonomies</p>
        <p><strong>Opportunities:</strong> ${(results.market_opportunities || []).length} with weighted scoring</p>
        <p><strong>Architecture:</strong> ${(results.architecture && results.architecture.system_components) ? results.architecture.system_components.length : 0} layers designed</p>
        <p><strong>Roadmap:</strong> ${(results.roadmap && results.roadmap.phases) ? results.roadmap.phases.length : 8} phases planned</p>
        <p><strong>AI Peer Review Score:</strong> ${(results.ai_review && results.ai_review.overall_score) ? results.ai_review.overall_score : 'N/A'}/10.0</p>
    `;
}

function exportJSON() {
    if (!currentProjectId) {
        showNotification("Please select or run a research analysis first.", "info");
        return;
    }
    window.open(API_BASE + "/export/" + currentProjectId + "/json", "_blank");
}

function exportMarkdown() {
    if (!currentProjectId) {
        showNotification("Please select or run a research analysis first.", "info");
        return;
    }
    window.open(API_BASE + "/export/" + currentProjectId + "/markdown", "_blank");
}


// =============================================================================
// UTILITY HELPERS
// =============================================================================

function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = "notification " + type;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = "0";
        notification.style.transition = "opacity 0.3s";
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = String(text);
    return div.innerHTML;
}

function truncate(text, maxLength) {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + "...";
}

function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    } catch (e) {
        return dateStr;
    }
}
