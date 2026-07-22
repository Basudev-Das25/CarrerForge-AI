# Frontend Architecture

## Application Structure

```
src/
├── main.tsx                 # React entry point
├── App.tsx                  # Route definitions
├── components/
│   ├── common/              # Reusable UI primitives
│   │   ├── Button.tsx       # Multi-variant button
│   │   ├── Input.tsx        # Labeled input with error/hint
│   │   ├── Modal.tsx        # Dialog overlay
│   │   ├── Toast.tsx        # Notification system
│   │   └── EmptyState.tsx   # Placeholder for empty views
│   └── layout/
│       ├── AppLayout.tsx    # Shell layout (sidebar + topbar + outlet)
│       ├── Sidebar.tsx      # Navigation sidebar
│       └── TopBar.tsx       # Search and notifications
├── screens/                 # Route-level page components
│   ├── Dashboard.tsx        # Stats grid, profile completion, quick actions
│   ├── Profile.tsx          # Personal info editor
│   ├── Education.tsx        # Education CRUD
│   ├── Experience.tsx       # Experience CRUD
│   ├── Projects.tsx         # Projects CRUD (enhanced)
│   ├── Skills.tsx           # Skills with categories
│   ├── Certificates.tsx     # Certificates with verification
│   ├── Achievements.tsx     # Achievements CRUD
│   ├── Languages.tsx        # Languages with proficiency
│   ├── Publications.tsx     # Publications CRUD
│   ├── Awards.tsx           # Awards CRUD
│   ├── Links.tsx            # Social links CRUD
│   ├── ResumeGenerator.tsx  # Full resume workspace (4 tabs)
│   └── ATSDashboard.tsx     # ATS analysis workspace (3 tabs)
├── services/
│   └── api.ts               # Typed API client (50+ methods)
├── hooks/
│   └── useStore.ts          # Zustand global state
├── types/
│   └── index.ts             # TypeScript type definitions
├── utils/
│   └── cn.ts                # Tailwind class merging utility
└── styles/
    └── globals.css          # Design system (CSS custom properties)
```

## Routing

| Path | Component | Description |
|---|---|---|
| `/` | Dashboard | Stats, profile completion, quick actions |
| `/profile` | Profile | Personal information editor |
| `/education` | Education | Education CRUD |
| `/experience` | Experience | Experience CRUD |
| `/projects` | Projects | Projects CRUD |
| `/skills` | Skills | Skills with category filters |
| `/certificates` | Certificates | Certificates with verification status |
| `/achievements` | Achievements | Achievements CRUD |
| `/languages` | Languages | Languages with proficiency levels |
| `/publications` | Publications | Publications CRUD |
| `/awards` | Awards | Awards CRUD |
| `/links` | Links | Social links CRUD |
| `/resume` | ResumeGenerator | Resume generation workspace (4 tabs) |
| `/ats` | ATSDashboard | ATS analysis workspace (3 tabs) |
| `/documents` | Placeholder | Document vault (coming soon) |
| `/settings` | Placeholder | Settings (coming soon) |

## State Management

Zustand store with localStorage persistence:
- User profile data
- Theme preference (light/dark/system)
- Active AI provider
- Current resume
- Documents list
- Sidebar collapsed state
- Onboarding completion

## Design System

CSS custom properties for theming:
- `--surface-0` through `--surface-3` — Background layers
- `--text-primary`, `--text-secondary`, `--text-tertiary` — Text hierarchy
- `--border`, `--border-strong` — Border colors
- `--brand-50` through `--brand-900` — Brand color scale

Dark mode via `.dark` class on `<html>`.
