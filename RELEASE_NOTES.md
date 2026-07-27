# Release Notes — CareerForge AI v0.5.0-alpha

**Release Date:** July 22, 2026
**Channel:** Alpha
**Platform:** Windows (x64)

## What's New

### Candidate Profile System
- Complete CRUD for 12 entity types: Personal Info, Education, Experience, Projects, Skills, Certificates, Achievements, Languages, Publications, Awards, Social Links
- Search, filter, sort, and pagination across all entities
- Profile completion tracking with progress indicators
- Soft delete and version history support

### Knowledge Engine
- Automatic relationship discovery between profile entities
- 13-dimension scoring system (leadership, ML, backend, frontend, cloud, devops, etc.)
- Semantic retrieval with hybrid search
- Knowledge graph visualization

### AI Orchestration
- Centralized AI gateway supporting 6 providers: OpenAI, Anthropic, OpenRouter, Ollama, Grok, HuggingFace
- Automatic failover between providers
- Response caching and rate limiting
- 12 AI agents for resume generation, ATS analysis, and optimization
- Version-controlled YAML prompt registry

### Resume Generation Pipeline
- Job description parsing into structured job profiles
- Evidence bundle generation from knowledge graph
- AI-powered resume writing with provenance tracking
- Resume validation with quality scoring
- Iterative reflection loop for improvement

### Template System
- 4 production Typst templates: Modern, Minimal, Software Engineer, Academic CV
- Theme system with customizable colors and typography
- Export to PDF, Typst source, text, and Markdown
- ATS-friendly layout (no tables, no images in text)

### ATS Intelligence
- Comprehensive ATS scoring across 7 dimensions
- Keyword matching and gap analysis
- Recruiter-focused metrics (readability, impact, achievement)
- Iterative optimization with evidence verification
- Resume comparison engine

### Desktop Application
- Tauri v2 desktop shell
- Desktop update system with automatic update checks
- Onboarding wizard for first-time setup
- Backup and restore system
- Diagnostics and export
- Error boundary for crash recovery

## Installation

### Option 1: Installer (Recommended)
Download `CareerForgeAI_Setup_v0.5.0-alpha.exe` and run the installer. This will:
- Install to Program Files
- Create desktop and Start Menu shortcuts
- Set up auto-updates

### Option 2: Portable
Download `CareerForgeAI_Portable_v0.5.0-alpha.zip`, extract, and run `CareerForge AI.exe` directly.

## System Requirements
- Windows 10 or later (x64)
- 4 GB RAM minimum
- 500 MB disk space

## Known Limitations
- Alpha release — expect occasional issues
- PDF rendering requires Typst (bundled in installer, manual install for portable)
- AI features require an API key (OpenAI, Anthropic, or Ollama for local)
- Desktop vault and document processing are placeholder features

## Upgrading
The application checks for updates automatically. Manual check available in Settings > Updates.

## Feedback
Report bugs or request features at: https://github.com/Basudev-Das/CareerForge-AI/issues
