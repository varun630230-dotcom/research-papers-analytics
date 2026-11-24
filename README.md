# ResearchGap AI

**Intelligent Research Paper Analysis & Gap Detection Platform**

An AI-powered research intelligence platform that discovers and analyzes academic papers from OpenAlex, arXiv, Semantic Scholar, and Crossref. Identifies research gaps, technological limitations, and market opportunities using Google Gemini.

## Features

- 🔍 **Paper Discovery** — Search 4 academic databases simultaneously
- 📄 **PDF Extraction** — Extract text from research paper PDFs
- 🧠 **AI Analysis** — Structured analysis of individual papers using Gemini
- 🔗 **Evidence Synthesis** — Cross-paper pattern detection and theme analysis
- 🎯 **Gap Detection** — Evidence-supported research gap identification
- ⚙️ **Tech Analysis** — Technological limitation identification
- 💡 **Opportunities** — Market opportunity analysis with weighted scoring
- 🆕 **Novelty Assessment** — Evaluate research idea originality
- 🏗️ **Architecture** — System design recommendations
- 📊 **Dashboard** — Interactive visualizations with Chart.js
- 📥 **Export** — JSON and Markdown report export

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| AI | Google Gemini API |
| PDF Processing | PyPDF |
| Charts | Chart.js |
| Academic APIs | OpenAlex, arXiv, Semantic Scholar, Crossref |

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Run the application
cd backend
uvicorn main:app --reload --port 8000
```

Then open http://localhost:8000 in your browser.

## Project Structure

```
ResearchGap-AI/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # SQLite operations
│   ├── models.py            # Pydantic models
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   └── utils/               # Helpers
├── frontend/
│   ├── index.html           # Dashboard
│   ├── style.css            # Styles
│   └── app.js               # Frontend logic
├── data/                    # Database (auto-created)
├── .env                     # API keys (not committed)
└── requirements.txt
```

## API Documentation

Visit http://localhost:8000/docs for interactive Swagger documentation.

## License

MIT
