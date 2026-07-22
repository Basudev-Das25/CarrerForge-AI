# User Guide

## Getting Started

1. **Install prerequisites** — Python 3.11+, Node.js 20+, Typst (optional)
2. **Configure API keys** — Copy `.env.example` to `.env`, add your AI provider keys
3. **Start the application** — Run `npm run dev` for web, or `npm run tauri dev` for desktop
4. **Build your profile** — Fill in personal info, education, experience, skills
5. **Generate resumes** — Paste a job description, select a template, generate

## Creating a Profile

Navigate through each section of the Profile menu:

- **Personal Information** — Name, email, phone, location, professional links
- **Education** — Degrees, institutions, GPA, highlights
- **Experience** — Work history with descriptions, achievements, skills used
- **Projects** — Portfolio projects with tech stack, links, status
- **Skills** — Categorized by type (programming, framework, tool, soft, domain)
- **Certificates** — Professional certifications with verification status
- **Achievements** — Awards, publications, patents
- **Languages** — Spoken languages with proficiency levels
- **Publications** — Papers, articles, conference presentations
- **Awards** — Recognition and honors
- **Links** — Social profiles and online presence

## Generating a Resume

1. Go to **Resume Generator**
2. Paste the full job description into the input
3. Select a template (Modern, Minimal, Software, Academic)
4. Click **Generate Blueprint** to see the strategy
5. Click **Generate Resume** for the full pipeline
6. Review the generated resume in the Preview tab
7. Check validation score in the Validation tab
8. Export as Typst, Text, or Markdown

## Running ATS Analysis

1. Go to **ATS Intelligence**
2. Paste your resume content and the job description
3. Click **Analyze Resume**
4. Review the score breakdown and keyword coverage
5. Use **Optimize** for iterative improvement
6. View suggestions and improvement history

## Managing Templates

- **Resume Generator → Templates tab** — View and select templates
- Each template has its own color scheme and typography
- Templates are ATS-friendly (no tables, no images, standard fonts)
- Switch templates before generation to preview different styles

## Exporting

From the Resume Generator:
- **Typst** — For editing the source before PDF compilation
- **Text** — Plain text for copying into online forms
- **Markdown** — For documentation or sharing
- **JSON** — Raw canonical resume data for programmatic use

## Troubleshooting

- **"AI provider not configured"** — Add API key to `.env`
- **"Database not found"** — App creates database on first run
- **PDF not generating** — Install Typst: `winget install typst`
- **"No skills added"** — Fill in profile sections before generating
- **Low ATS score** — Add more keywords matching the job description
