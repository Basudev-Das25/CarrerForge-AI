# Architectural Decisions

## ADR-001: Local-First Architecture

**Decision**: All data stored locally. No cloud sync.

**Rationale**: Privacy-first approach for career documents. Users control their data completely. No server infrastructure needed.

**Consequences**: Single-user only. No collaboration features. Data not backed up automatically.

## ADR-002: SQLite + LanceDB Dual Storage

**Decision**: SQLite for relational data, LanceDB for vector embeddings.

**Rationale**: SQLite provides ACID compliance and structured queries. LanceDB provides efficient vector similarity search for semantic retrieval. Both are file-based and require no server.

**Consequences**: Two storage systems to maintain. Embedding regeneration needed after schema changes.

## ADR-003: Provider Abstraction for AI

**Decision**: All AI calls go through a centralized orchestrator with provider abstraction.

**Rationale**: Users may prefer different AI providers. Cost and latency vary. Failover prevents single-provider dependency.

**Consequences**: Extra abstraction layer. Provider-specific features (like streaming) need adapter implementation.

## ADR-004: Canonical Resume JSON

**Decision**: Resume generation produces a structured JSON, not direct Typst output.

**Rationale**: JSON enables template switching, validation, versioning, and multiple export formats from a single source of truth. Every bullet point carries provenance metadata.

**Consequences**: Extra serialization step. Template rendering must handle JSON→Typst conversion.

## ADR-005: In-Memory Knowledge Graph

**Decision**: Knowledge graph built in memory per query, not persisted.

**Rationale**: Simplicity. Graph rebuilds in <100ms for typical profiles. No migration complexity for graph schema changes.

**Consequences**: Must rebuild on every request. Could be cached at application level for better performance.

## ADR-006: Version-Controlled Prompts

**Decision**: AI prompts stored as YAML files, not in Python source code.

**Rationale**: Enables prompt iteration without code changes. Supports versioning, testing, and provider-specific overrides. Non-developers can edit prompts.

**Consequences**: Extra file I/O on first load. Cache mitigates this.

## ADR-007: Typst for PDF Generation

**Decision**: Use Typst instead of WeasyPrint or ReportLab.

**Rationale**: Typst produces clean, professional PDFs with modern typography. Source is human-readable. Templates are self-contained.

**Consequences**: Requires system-installed Typst binary. No in-process rendering (subprocess call).
