# Research Papers Analytics — INNOVATE AI

> **Research → Evidence → Gaps → Opportunities → Build**

**INNOVATE AI** is a production-grade AI Research & Innovation Intelligence Platform that transforms project ideas into evidence-backed opportunities using verified academic literature and structured AI intelligence pipelines.

---

## 🌟 Key Capabilities

* **Multi-Source Academic Literature Discovery**: Audited paper retrieval across **OpenAlex, arXiv, Semantic Scholar, and Crossref** with 0% mock or fabricated data.
* **4-Tier Relevance Classification**: Rigorously categorizes every retrieved paper into `DIRECT`, `RELATED`, `BACKGROUND`, and `IRRELEVANT`.
* **Legal Open-Access Full-Text PDF Extraction**: Downloads and parses open-access scientific PDFs (via `pypdf`) with extraction-level transparency (`Full-text PDF analyzed` vs `Abstract-only analysis`).
* **Multi-Paper Evidence Clustering**: Synthesizes recurring limitations and future work across literature into evidence-backed Research Gaps, Technology Gaps, and Market Gaps.
* **Transparent Weighted Opportunity Scoring**: Prioritizes buildable projects using an explainable formula across Research Gap (30%), Market Evidence (20%), Tech Feasibility (20%), Data Availability (10%), Differentiation (10%), and Evidence Confidence (10%).
* **Objective Novelty Assessment & Build Recommendations**: Generates end-to-end system architectures, 7-phase execution roadmaps, and prior-art similarity assessments.
* **14-Tab Interactive Intelligence Dashboard**: Built with Next.js 14, Tailwind CSS, Lucide icons, and Recharts.

---

## 🏗️ Architecture & Technology Stack

```
USER IDEA
  │
  ▼
Idea Understanding & Query Expansion
  │
  ▼
Multi-Source Academic Repository Search (OpenAlex, arXiv, Semantic Scholar, Crossref)
  │
  ▼
Candidate Deduplication & 4-Tier Relevance Classification (DIRECT / RELATED / BACKGROUND / IRRELEVANT)
  │
  ▼
Legal Open-Access PDF Retrieval & Scientific Document Parsing (pypdf)
  │
  ▼
Multi-Paper Evidence Clustering ──► Research Gaps & Market Gaps
  │
  ▼
Opportunity Synthesis & Weighted Scoring ──► Novelty Assessment
  │
  ▼
Recommended Architecture & 7-Phase Execution Roadmap
```

### Backend:
* **FastAPI** (Python 3.12, Async REST API)
* **SQLAlchemy** + **aiosqlite** (Async SQLite persistence)
* **Google GenAI SDK / Gemini AI** for structured synthesis
* **pypdf** & **httpx** for legal open-access PDF extraction

### Frontend:
* **Next.js 14** (App Router, Server-side proxy rewrites)
* **TypeScript** & **Tailwind CSS**
* **Recharts** (Radar score breakdowns, comparative benchmark metrics)
* **Lucide React** (Modern minimal iconography)

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Node.js 18+ & npm
* Google Gemini API Key (or OpenAI / Anthropic / Groq)

---

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=sqlite+aiosqlite:///./innovate_ai.db
GEMINI_API_KEY=your_gemini_api_key_here
CORS_ORIGINS=http://localhost:3000
```

Start backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run build
npm run start
```
Web App will be live at `http://localhost:3000`.

---

## 📊 Verification & Test Scenarios

The platform includes an automated end-to-end validation test:

```bash
cd backend
python test_upgrade_pipeline.py
```

---

## 📄 License

MIT License. Open-source and free for academic and commercial innovation.
