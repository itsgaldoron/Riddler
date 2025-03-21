# Development Guidelines
*Version: 1.0.0*

This guide provides information for developers who want to contribute to or extend the Riddler project.

## Table of Contents
- [Development Environment](#development-environment)
- [Code Structure](#code-structure)
- [Testing](#testing)
- [Adding New Categories](#adding-new-categories)
- [Extending Video Capabilities](#extending-video-capabilities)
- [Contributing Guidelines](#contributing-guidelines)

## Development Environment

### Setting Up a Development Environment

1. Create a fork of the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/riddler.git
   cd riddler
   ```
3. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black isort flake8
   ```
5. Create a `.env.dev` file for development settings:
   ```
   RIDDLER_OPENAI_API_KEY=your_openai_key
   RIDDLER_ELEVENLABS_API_KEY=your_elevenlabs_key
   RIDDLER_PEXELS_API_KEY=your_pexels_key
   RIDDLER_ENV=development
   ```

### Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make changes and test locally
3. Format your code:
   ```bash
   black .
   isort .
   flake8
   ```
4. Run tests:
   ```bash
   pytest
   ```
5. Commit and push changes:
   ```bash
   git commit -am "Add your feature description"
   git push origin feature/your-feature-name
   ```
6. Create a pull request

## Code Structure

### Key Modules and Components

- **Core Components**:
  - `core/riddle_generator.py`: Handles riddle generation logic
  - `core/tts_provider.py`: Manages text-to-speech conversion
  - `core/video_creator.py`: Creates video content

- **Services**:
  - `services/openai_service.py`: OpenAI API integration
  - `services/elevenlabs_service.py`: ElevenLabs API integration
  - `services/pexels_service.py`: Pexels API integration
  
- **Utilities**:
  - `utils/cache_manager.py`: Caching functionality
  - `utils/logger.py`: Logging functions
  - `utils/media_processor.py`: Media file processing

### Design Patterns

- **Factory Pattern**: Used for creating riddle generators
- **Strategy Pattern**: Used for different TTS providers
- **Singleton Pattern**: Used for configuration management
- **Pipeline Pattern**: For the riddle generation to video output flow

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=.

# Run specific test file
pytest tests/test_riddle_generator.py
```

### Writing Tests

1. Place test files in the `tests/` directory
2. Use descriptive test names with format `test_<what_being_tested>_<expected_result>`
3. Mock external API calls
4. Include both success and failure test cases

Example test:
```python
import pytest
from unittest.mock import patch
from core.riddle_generator import RiddleGenerator

def test_generate_riddle_valid_parameters_returns_riddle():
    generator = RiddleGenerator()
    riddle = generator.generate_riddle(category="geography", difficulty="medium")
    assert "question" in riddle
    assert "answer" in riddle
    assert "difficulty" in riddle
```

## Adding New Categories

To add a new riddle category:

1. Update the category list in `config/config.json`:
   ```json
   "riddle": {
     "categories": ["geography", "math", "physics", "your_new_category"]
   }
   ```
2. Add category-specific prompts in `core/prompt_templates/`:
   ```
   your_new_category_prompt.txt
   ```
3. Add category-specific tests in `tests/`
4. Update documentation in `docs/features.md`

## Extending Video Capabilities

### Adding New Video Effects

1. Create a new effect function in `utils/video_effects.py`
2. Register the effect in the `VideoCreator` class
3. Update the configuration to support the new effect

### Integrating a New Video Provider

1. Create a new service in `services/your_provider_service.py`
2. Implement the required methods:
   - `search_videos(query, limit)`
   - `download_video(video_id, output_path)`
3. Integrate the new provider in `core/video_creator.py`

## Contributing Guidelines

### Pull Request Process

1. Ensure all tests pass
2. Update documentation to reflect changes
3. Follow the code style guidelines
4. Include a clear description of changes
5. Link to any related issues

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions and classes
- Keep functions small and focused on a single responsibility

For more information, see the [CONTRIBUTING.md](../CONTRIBUTING.md) file.

---

*Navigate: [Back to Index](index.md) | [Previous: Troubleshooting](troubleshooting.md)* 