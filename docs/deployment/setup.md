# Deployment Guide

## Local Development

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| Rust | Latest | Tauri desktop build |
| Typst | Latest | PDF compilation |

### Backend Setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Frontend Setup

```bash
npm install
npm run dev          # Starts dev server at localhost:1420
```

### Environment Configuration

Copy `.env.example` to `.env` and configure:
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite+aiosqlite:///data/careerforge.db
```

## Running the Application

### Backend only
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend only
```bash
npm run dev
```

### Desktop app
```bash
npm run tauri dev     # Development mode
npm run tauri build   # Production build
```

## Typst Installation

PDF compilation requires Typst:

```bash
# Windows (winget)
winget install typst

# macOS (brew)
brew install typst

# Cargo (cross-platform)
cargo install --git https://github.com/typst/typst --locked typst-cli

# Verify
typst --version
```

## Testing

```bash
# All backend tests
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest

# Frontend tests
npm run test

# Lint
cd backend && ruff check app/
npm run lint
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///data/careerforge.db` | Database path |
| `DATA_DIR` | `~/.careerforge` | Application data directory |
| `AI_PROVIDER` | `openai` | Default AI provider |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `LOG_LEVEL` | `INFO` | Logging level |
| `APP_DEBUG` | `true` | Debug mode |

## Troubleshooting

### "No module named 'aiosqlite'"
```bash
pip install aiosqlite
```

### "unable to open database file"
Ensure the `data/` directory exists. The app creates it on startup.

### "Typst compiler not installed"
Install Typst (see above). PDF export requires it.

### "No AI providers registered"
Set at least one API key in `.env`.
