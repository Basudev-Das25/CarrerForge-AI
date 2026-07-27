# Template System

## Overview

Production-quality Typst templates for resume rendering. Templates are self-contained, hot-swappable, and theme-configurable.

## Template Directory Structure

```
templates/
├── modern/
│   ├── template.typ        # Typst source (124 lines)
│   ├── metadata.yaml       # Template metadata
│   ├── theme.json          # Theme configuration
│   └── readme.md           # Documentation
├── minimal/
│   ├── template.typ        # Minimal clean (104 lines)
│   ├── metadata.yaml
│   ├── theme.json
│   └── readme.md
├── software/
│   ├── template.typ        # Software engineer (123 lines)
│   ├── metadata.yaml
│   └── theme.json
└── academic/
    ├── template.typ        # Academic CV (113 lines)
    ├── metadata.yaml
    └── theme.json
```

## Template API

Each `template.typ` defines these functions:
- `header(name, email, phone, location, linkedin, github, portfolio)`
- `section-heading(name)`
- `bullet(text)`
- `skills-section(items)`
- `languages-section(items)`
- `links-section(items)`
- `detail-section(name, items)`
- `generic-section(name, items)`

## Theme Configuration

`theme.json` controls:
- Colors: primary, accent, text, secondary, muted, divider, link
- Typography: font family, heading/body/small/header sizes
- Spacing: line spacing, margins, section spacing
- Styling: bullet style, heading weight, divider width

## Rendering Pipeline

```
CanonicalResume JSON
    ↓
Template Engine
    → Load template.typ from template directory
    → Load theme from theme.json
    → Render sections using template functions
    → Escape special characters
    ↓
Typst Source Code
    ↓
Typst Compiler (subprocess)
    → Compile to PDF
    → Return PDF path
    ↓
PDF Output
```

## Supported Export Formats

| Format | Method | Use Case |
|---|---|---|
| Typst | `render_to_typst()` | Source editing |
| PDF | `compile_typst()` | Final output |
| Text | `render_to_text()` | Plain text copy |
| Markdown | `render_to_markdown()` | Documentation |
| JSON | Direct serialization | API consumption |
