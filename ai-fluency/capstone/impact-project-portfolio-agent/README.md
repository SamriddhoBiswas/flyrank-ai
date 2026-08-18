# Impact Project — Personal Portfolio & AI Agent

A personal brand website built as a capstone for the **General AI Fluency Track — Impact Project**.

## What it is

A single-page developer portfolio styled like a code editor (file tabs, terminal hero, dark theme) showcasing education, skills, experience, projects, and achievements — paired with a live AI chat agent that answers visitor questions using the resume as its knowledge base.

## Stack

- **Frontend:** HTML, CSS, vanilla JS (no framework, fully static)
- **Agent:** Google Gemini API (`gemini-2.0-flash`), free tier
- **Backend:** Vercel serverless function (`api/chat.js`) — keeps the API key private, never exposed to the browser
- **Hosting:** Vercel (free tier)

## How the agent works

The resume content is embedded as a system prompt. When a visitor asks a question in the chat widget, the browser sends it to the serverless function, which forwards it to Gemini along with that context, then returns a grounded answer — a lightweight RAG-style pattern without needing a vector database.

## Files

- `index.html` — the full site + chat widget
- `api/chat.js` — serverless function that calls Gemini
- `README.md` (this file) — description of the project

`Deployed` https://sam-portfolio-agent.vercel.app/