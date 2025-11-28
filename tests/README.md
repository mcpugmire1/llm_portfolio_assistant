# Ask MattGPT Test Suite

## Overview

This test suite provides comprehensive coverage for Ask MattGPT using:

- **Unit Tests**: Fast, isolated tests for individual functions
- **Integration Tests**: Tests requiring external services (Pinecone, OpenAI)
- **BDD Tests**: Behavior-driven tests with Gherkin feature files
- **Visual Regression**: Screenshot comparison tests

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-bdd playwright
playwright install chromium

# Run all unit tests
pytest tests/unit -v

# Run specific test file
pytest tests/unit/test_backend_service.py -v

# Run with coverage
pytest tests/unit --cov=. --cov-report=html
```

## Directory Structure

```
tests/
├── conftest.py              # Shared fixtures (mock data, etc.)
├── pytest.ini               # Pytest configuration
├── unit/                    # Unit tests
│   ├── test_backend_service.py
│   ├── test_utils.py
│   └── test_story_intelligence.py
├── integration/             # Integration tests
│   └── (requires running services)
├── bdd/                     # Behavior-driven tests
│   ├── features/            # Gherkin feature files
│   │   ├── search.feature
│   │   └── landing_page.feature
│   └── steps/               # Step definitions
│       └── test_steps.py
└── screenshots/             # Visual regression baselines
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast tests that don't require external services:

```bash
# Run all unit tests
pytest tests/unit -v -m unit

# Run specific test class
pytest tests/unit/test_backend_service.py::TestDiversifyResults -v
```

**Key test files:**
- `test_backend_service.py`: RAG orchestration, story scoring, client diversity
- `test_utils.py`: Utility functions, text processing
- `test_story_intelligence.py`: Theme inference, behavioral query detection

### BDD Tests (`tests/bdd/`)

Behavior-driven tests using Gherkin syntax:

```bash
# Run BDD tests (requires running Streamlit app)
streamlit run app.py &  # Start app in background
pytest tests/bdd -v

# Run specific feature
pytest tests/bdd -k "search" -v
```

**Feature files:**
- `search.feature`: Semantic search, behavioral queries, client diversity
- `landing_page.feature`: UI elements, input handling, responsive design

### Visual Regression Tests

Compare screenshots against baselines:

```bash
# Generate baseline screenshots
pytest tests/visual/test_screenshots.py --update-baseline

# Run visual comparison
pytest tests/visual -v
```

## Writing Tests

### Unit Test Example

```python
class TestMyFunction:
    """Tests for my_function()."""

    def test_happy_path(self, sample_stories):
        """Should return expected result for valid input."""
        result = my_function(sample_stories)
        assert result == expected

    def test_edge_case(self):
        """Should handle edge case gracefully."""
        result = my_function([])
        assert result is None
```

### BDD Feature Example

```gherkin
Feature: Story Search

  Scenario: Behavioral query returns leadership stories
    When the user searches "tell me about a time you led a team"
    Then the top 3 results should include Talent & Enablement stories
```

## Fixtures

Common fixtures are defined in `conftest.py`:

- `sample_stories`: Mock story data (5 stories with different categories/clients)
- `sample_search_results`: Stories with Pinecone-style scores
- `behavioral_query_examples`: Example behavioral interview queries
- `technical_query_examples`: Example technical queries
- `nonsense_queries`: Queries that should be filtered
- `valid_queries`: Queries that should pass filters

## CI/CD Integration

Add to GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/unit -v --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only BDD tests
pytest -m bdd

# Skip slow tests
pytest -m "not slow"
```

## Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| backend_service.py | 80% |
| utils.py | 80% |
| story_intelligence.py | 70% |
| styles.py | N/A (CSS) |
| landing_view.py | 50% (UI) |
| conversation_view.py | 50% (UI) |

## Next Steps

1. [ ] Run existing unit tests, fix any import issues
2. [ ] Add tests for `diversify_results()` once implemented
3. [ ] Add integration tests for Pinecone search
4. [ ] Set up visual regression baseline screenshots
5. [ ] Add GitHub Actions CI workflow
6. [ ] Achieve 70% coverage on Tier 1 modules
