# Security

## Threat Model

CareerForge AI is a local-first desktop application. The threat surface is limited to:

1. **Local data** — All profile data, resumes, and documents stored on local disk
2. **AI API calls** — Requests sent to external AI providers (OpenAI, Anthropic, etc.)
3. **PDF processing** — PyMuPDF and Tesseract for document text extraction
4. **Typst compilation** — Subprocess execution for PDF generation

## Secrets Management

- API keys stored in `.env` file (never committed to git)
- `.env` listed in `.gitignore`
- Settings loaded via `pydantic-settings`
- No secrets in code, logs, or error messages

## Data Protection

- All data stored locally in SQLite (`~/.careerforge/`)
- Database path configurable via `DATABASE_URL` env var
- No network sync or cloud storage
- Documents stored in `~/.careerforge/documents/`
- LanceDB vectors stored in `./vector_store/`

## API Security

- Backend listens on `127.0.0.1:8000` (localhost only)
- CORS configured for Tauri webview origins only
- No authentication required (single-user local app)
- Input validation via Pydantic schemas on all endpoints

## Dependency Security

- Regular `npm audit` and `pip-audit` in CI
- GitHub CodeQL analysis weekly
- TruffleHog secret scanning on all PRs
- Dependency versions pinned in `requirements.txt` and `package.json`

## Subprocess Security

- Typst compilation runs in a temporary directory
- Timeout of 30 seconds prevents hangs
- Input is escaped before passing to Typst
- No user-controlled strings passed directly to shell commands
