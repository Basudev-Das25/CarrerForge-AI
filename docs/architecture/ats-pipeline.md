# ATS Intelligence Platform

## Overview

The ATS Intelligence Platform analyzes, scores, optimizes, and compares resumes against job descriptions. It uses a multi-dimensional scoring system with evidence-backed recommendations.

## Analysis Pipeline

```
Resume + Job Profile
    ↓
1. Keyword Analysis
   → Match resume text against JD keywords
   → Compute density, coverage, missing keywords
    ↓
2. Section Analysis
   → Check required sections present
   → Verify section ordering and completeness
    ↓
3. Bullet Analysis
   → Detect weak verbs (helped, assisted, etc.)
   → Check for quantified metrics
   → Verify minimum length
    ↓
4. Recruiter Metrics
   → Readability (sentence complexity)
   → Impact (action verbs + numbers)
   → Achievement orientation (result verbs)
   → Specificity (company names, dates, metrics)
    ↓
5. Evidence Verification
   → Check provenance metadata on bullets
   → Count unsupported claims
    ↓
6. Weighted Overall Score
   → 7 dimensions with configured weights
   → keywords: 25%, sections: 15%, formatting: 10%
   → bullets: 15%, readability: 10%, impact: 15%, specificity: 10%
    ↓
7. Suggestions
   → Priority-ranked improvement recommendations
   → Each suggestion has section, category, expected improvement
```

## Optimization Loop

```
1. Analyze current resume → score
2. If score < target:
   a. Generate optimization plan (AI)
   b. Apply optimizations (AI)
   c. Re-analyze
   d. Only accept if score improved
   e. Record iteration
3. Repeat until target score or max iterations
```

## Comparison Engine

Compares two resumes or a resume against a job:
- Score delta tracking
- Keyword diff (added/removed)
- Semantic improvement measurement
- Section-level differences
