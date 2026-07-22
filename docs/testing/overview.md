# Testing

## Test Framework

- **Backend**: pytest with pytest-asyncio
- **Frontend**: Vitest (configured but not actively used)

## Running Tests

```bash
# Backend tests (uses in-memory SQLite automatically)
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest

# Specific test file
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest tests/unit/test_knowledge_graph.py -v

# With coverage
PYTHONPATH=backend TEST_DATABASE_URL="sqlite+aiosqlite://" pytest --cov=app --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py                          # Fixtures: in-memory DB, session cleanup, test client
├── unit/
│   ├── test_ai_orchestrator.py          # 24 tests: orchestrator, observability, prompts, providers
│   ├── test_errors.py                   # 10 tests: error hierarchy
│   ├── test_knowledge_graph.py          # 20 tests: graph, scoring, relationships, retrieval
│   ├── test_profile_service.py          # 12 tests: profile CRUD operations
│   ├── test_providers.py                # 5 tests: provider abstraction
│   ├── test_resume_pipeline.py          # 17 tests: blueprint, canonical, validator
│   ├── test_template_engine.py          # 23 tests: rendering, themes, Typst, exports
│   └── test_ats_engine.py               # 19 tests: analysis, scoring, formatting
├── integration/
│   ├── test_api.py                      # 6 tests: admin, health, root
│   ├── test_ai_api.py                   # 12 tests: orchestrator, prompts, agents
│   ├── test_knowledge_api.py            # 20 tests: knowledge engine APIs
│   ├── test_profile_api.py              # 17 tests: profile CRUD APIs
│   ├── test_resume_api.py               # 7 tests: resume generation APIs
│   └── test_ats_api.py                  # 5 tests: ATS intelligence APIs
```

**Total: 186 tests, all passing.**

## Test Environment

Tests use an in-memory SQLite database configured via:
```bash
TEST_DATABASE_URL="sqlite+aiosqlite://"
```

The `conftest.py` fixtures:
1. Set `TEST_DATABASE_URL` at module import time (before app imports)
2. Create all tables once per session
3. Clean data between tests (autouse `cleanup_db` fixture)
4. Drop all tables after session
5. No file system or manual configuration needed

## Writing New Tests

```python
# Unit test example
def test_my_feature():
    from app.services.knowledge.graph import KnowledgeGraph, KnowledgeNode
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="test:1", entity_type="test", entity_id="1", properties={}))
    assert graph.get_node("test", "1") is not None


# Integration test example
@pytest.mark.asyncio
async def test_my_endpoint(client):
    response = await client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```
