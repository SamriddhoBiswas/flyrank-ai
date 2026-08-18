

<div align="center">

## `flyrank-ai`

![Track](https://img.shields.io/badge/Track-Backend%20AI%20Engineering-6C63FF?style=flat-square)
![Org](https://img.shields.io/badge/and-General%20AI%20Fluency-0A0A0A?style=flat-square)
![Status](https://img.shields.io/badge/Organization-FlyRank-brightgreen?style=flat-square)

</div>

---


### `backend-ai/`

The backend engineering track is arranged chronologically. Each week is a self-contained project with its own README, dependencies, and runnable entry point.

| Project | Focus |
| --- | --- |
| [`w1-fastapi-backend`](backend-ai/w1-fastapi-backend/) | Minimal FastAPI service and basic routes |
| [`w2-crud-fastapi`](backend-ai/w2-crud-fastapi/) | CRUD task API backed by in-memory data |
| [`w3-database-sqlite-api`](backend-ai/w3-database-sqlite-api/) | CRUD API with SQLite persistence |
| [`w3-docker-containerized-api`](backend-ai/w3-docker-containerized-api/) | Containerized FastAPI, PostgreSQL, and Docker Compose stack |
| [`w4-jwt-auth-fastapi`](backend-ai/w4-jwt-auth-fastapi/) | Supabase authentication and protected JWT routes |
| [`w5-polite-scraper`](backend-ai/w5-polite-scraper/) | Rate-limited, cached, validated web-scraping pipeline |
| [`w6-background-job`](backend-ai/w6-background-job/) | Redis/RQ background jobs with retries, idempotency, and alerts |
| [`w7-llm-api`](backend-ai/w7-llm-api/) | Schema-constrained LLM enrichment with repair retries and evaluation |
| [`w7-pdf-report-generator`](backend-ai/w7-pdf-report-generator/) | SQL aggregation, background processing, and downloadable PDF artifacts |
| [`capstone/ai-image-matching-engine`](backend-ai/capstone/ai-image-matching-engine/) | Image understanding, embeddings, content matching, and mismatch detection |
| [`capstone/embeddable-widget-lead-capture-platform`](backend-ai/capstone/embeddable-widget-lead-capture-platform/) | Embeddable customer widget and lead-capture backend |

### `ai-fluency/`

The AI fluency track documents the reasoning and communication work around building an impact-oriented portfolio.

| Project | Focus |
| --- | --- |
| [`capstone/impact-project-portfolio-agent`](ai-fluency/capstone/impact-project-portfolio-agent/) | Portfolio experience with an AI agent interface |
| [`week1/AI Workflow Audit and Tool Setup`](ai-fluency/week1/AI%20Workflow%20Audit%20and%20Tool%20Setup/) | Workflow audit and tooling setup |
| [`week1/Draw the Path Portfolio Sitemap + Toolkit`](ai-fluency/week1/Draw%20the%20Path%20Portfolio%20Sitemap%20%2B%20Toolkit/) | Portfolio sitemap, toolkit, and visual iterations |
| [`week2/Frame-It-As-Cases.md`](ai-fluency/week2/Frame-It-As-Cases.md) | Framing work as case studies |
| [`week2/The-Prompt-Ladder.md`](ai-fluency/week2/The-Prompt-Ladder.md) | Prompting practice and prompt progression |

## Full structure

```text
flyrank-ai/
├── README.md
├── .gitattributes
├── ai-fluency/
│   ├── capstone/
│   │   └── impact-project-portfolio-agent/
│   │       ├── README.md
│   │       ├── index.html
│   │       ├── package.json
│   │       └── api/
│   │           └── chat.js
│   ├── week1/
│   │   ├── proof-statement.txt
│   │   ├── AI Workflow Audit and Tool Setup/
│   │   │   ├── FL-01-Workflow-Audit.md
│   │   │   └── AI Workflow Audit and Tool Setup.docx
│   │   └── Draw the Path Portfolio Sitemap + Toolkit/
│   │       ├── portfolio_sitemap_toolkit.md
│   │       ├── portfolio_sitemap_toolkit.txt
│   │       ├── 01-initial-sitemap.png
│   │       ├── 02-claude-project.png
│   │       ├── 03-claude-pressure-test.png
│   │       └── 04-revised-sitemap.png
│   └── week2/
│       ├── Frame-It-As-Cases.md
│       ├── The-Prompt-Ladder.md
│       └── Prompting Fundamentals on Real Tasks v2.docx
│
└── backend-ai/
    │
	├── capstone/
	│   ├── ai-image-matching-engine/
	│   └── embeddable-widget-lead-capture-platform/
	│ 
	├── w1-fastapi-backend/
	├── w2-crud-fastapi/
	├── w3-database-sqlite-api/
	├── w3-docker-containerized-api/
	├── w4-jwt-auth-fastapi/
	├── w5-polite-scraper/
	├── w6-background-job/
	├── w7-llm-api/
	└── w7-pdf-report-generator/

```

## Getting started

Each project is independent. Start with its local README and install dependencies from that project's `requirements.txt` or `package.json`.

### Python projects

```powershell
cd backend-ai\w1-fastapi-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Later projects may require Docker, PostgreSQL, Redis, Supabase, or an LLM provider. Their local READMEs contain the project-specific environment variables, startup commands, and API examples. Never commit a real `.env` file or provider secret.

