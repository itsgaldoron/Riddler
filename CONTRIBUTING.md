# Contributing to Riddler

Thank you for considering contributing to Riddler! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct: be respectful, considerate, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a new issue with a descriptive title
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots or logs if applicable

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with a descriptive title
3. Describe the feature and its benefits
4. Include any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes following the coding standards
4. Add or update tests as necessary
5. Ensure all tests pass with `pytest`
6. Submit a pull request with a clear description of your changes

## Development Setup

1. Clone your fork of the repository
2. Run the setup script: `./setup.sh`
3. Install development dependencies: `pip install -r requirements.txt`
4. Set up pre-commit hooks: `pre-commit install`

## Coding Standards

- Follow PEP 8 for Python code style
- Use descriptive variable and function names
- Write docstrings for all functions, classes, and modules
- Maintain test coverage above 80%

## Testing

- Run tests with: `pytest`
- Run tests with coverage: `pytest --cov=.`
- Add tests for new features and bug fixes

## Git Workflow

1. Create a branch for your feature/fix: `git checkout -b feature/your-feature`
2. Commit regularly with descriptive messages
3. Keep your branch updated with main: `git pull --rebase origin main`
4. Push your branch: `git push origin feature/your-feature`
5. Create a pull request against the main branch

## License

By contributing, you agree that your contributions will be licensed under the project's Creative Commons Attribution-NonCommercial 4.0 International License. All intellectual property rights remain with the original author. Contributors retain copyright to their contributions but grant the project the rights to use those contributions under the CC BY-NC license. 