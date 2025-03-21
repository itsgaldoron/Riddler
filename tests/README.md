# Riddler Tests

This directory contains tests for the Riddler application. The tests are organized by module and functionality.

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=.
```

To run a specific test file:

```bash
pytest tests/test_specific_file.py
```

To run a specific test:

```bash
pytest tests/test_specific_file.py::test_specific_function
```

## Test Organization

- `test_core/`: Tests for core functionality
- `test_services/`: Tests for service integrations
- `test_utils/`: Tests for utility functions
- `test_config/`: Tests for configuration handling
- `test_integration/`: Integration tests

## Writing Tests

When adding new features, please include corresponding tests. Tests should:

1. Be independent and not rely on other tests
2. Clean up any resources they create
3. Mock external services when appropriate
4. Include meaningful assertions

Example test:

```python
def test_riddle_generation():
    # Arrange
    category = "geography"
    difficulty = "medium"
    
    # Act
    result = generate_riddle(category, difficulty)
    
    # Assert
    assert result is not None
    assert "question" in result
    assert "answer" in result
    assert result["category"] == category
    assert result["difficulty"] == difficulty
```

## Test Coverage

We aim to maintain at least 80% test coverage. Coverage reports are generated when running tests with the `--cov` flag. 