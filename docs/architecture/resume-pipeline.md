# Resume Generation Pipeline

## Overview

The resume pipeline transforms a raw Job Description into a professional, ATS-optimized, evidence-backed resume. Every generated sentence is traceable to candidate evidence.

## Pipeline Steps

```
1. Job Description Input
   ↓
2. Job Intelligence Engine
   → Parse JD into structured JobProfile
   → Extract: title, company, skills, keywords, seniority
   ↓
3. Knowledge Engine
   → Build knowledge graph from all profile entities
   → Discover relationships between entities
   → Score entities across 13 dimensions
   ↓
4. Evidence Engine
   → Generate evidence bundle from job profile
   → Score each evidence item by relevance
   → Track relationship paths and confidence
   ↓
5. Resume Planner Agent (AI)
   → Generate strategic blueprint
   → Determine sections, order, word counts
   → Identify keywords to emphasize
   ↓
6. Resume Writer Agent (AI)
   → Write each section using evidence bundle
   → Never fabricate — only use provided evidence
   → Track provenance for every bullet
   ↓
7. Canonical Resume Model
   → JSON source of truth
   → Every bullet has metadata: evidence_source, entity_id, confidence, reason
   ↓
8. Resume Validator
   → 10 quality checks
   → Duplicate detection, weak bullets, keyword coverage
   ↓
9. Reflection Loop
   → If validation fails, improve via AI
   → Re-validate after each iteration
   → Stop when validation passes or max iterations reached
   ↓
10. Version Storage
    → Store resume JSON + blueprint + job profile
    → Track ATS score, iteration count, template used
```

## Key Data Models

### ResumeBlueprint
Strategic plan generated BEFORE any writing:
- Target role, industry, strategy, tone
- Section ordering and word count targets
- Keywords to emphasize and missing keywords
- Evidence mappings per section
- ATS coverage estimate

### CanonicalResume
JSON source of truth with full provenance:
- Candidate info (name, email, links)
- Ordered sections with items
- Every item has `metadata.evidence_source`, `metadata.entity_id`, `metadata.confidence`
- Validation report attached
- Template used, prompt version, model

### EvidenceBundle
All evidence for resume generation:
- Projects, skills, experience, certificates, achievements, awards, languages, publications
- Each item has confidence_score, similarity_score, relationship_path, supporting_keywords
