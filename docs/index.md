# Riddler - AI-Powered Riddle Generation System

## Description
Riddler is an advanced AI system that generates, processes, and manages riddles with multimedia capabilities including video and voice outputs. The system handles riddle generation, caching, and multimedia processing in an efficient and organized manner.

## Main Features
- AI-powered riddle generation across multiple categories (geography, math, physics, history, logic, wordplay)
- Text-to-speech voice synthesis using ElevenLabs
- Video processing with dynamic text overlays and effects
- Smart caching system with compression
- TikTok-optimized video output
- Multi-riddle video compilation
- Background video management with Pexels integration

## Project Structure

### Main Application

#### Entry Point (`main.py`)
- Description: Application entry point and CLI interface
- Features:
  - Command-line argument parsing
  - Service initialization
  - Riddle generation workflow
  - Error handling and logging setup
- CLI Arguments:
  ```bash
  -c, --category    Riddle category (required)
  -d, --difficulty  Riddle difficulty (default: medium)
  -n, --num_riddles Number of riddles per video (default: 2)
  -o, --output      Output directory (default: output)
  ```
- Example Usage:
  ```bash
  python main.py -c geography -d medium -n 3 -o output/
  ```
- Video Duration Management:
  - Target duration: 27 seconds per riddle
  - Minimum total: 60 seconds
  - Maximum total: 90 seconds
  - Optimal riddles: 2-4 based on duration constraints

### Command Line Interface

#### CLI Usage (`main.py`)
- Description: Command-line interface for riddle generation
- Base Command:
  ```bash
  python main.py [options]
  ```

##### Required Arguments
- `-c, --category CATEGORY`
  - Description: Riddle category to generate
  - Valid values: geography, math, physics, history, logic, wordplay
  - Example: `-c geography`

##### Optional Arguments
- `-d, --difficulty DIFFICULTY`
  - Description: Riddle difficulty level
  - Default: "medium"
  - Values: easy, medium, hard
  - Example: `-d hard`

- `-n, --num_riddles NUM`
  - Description: Number of riddles per video
  - Default: 2
  - Range: 2-4 (automatically adjusted based on duration)
  - Example: `-n 3`

- `-o, --output OUTPUT`
  - Description: Output directory path
  - Default: "output"
  - Example: `-o output/geography`

##### Duration Management
- Target Duration:
  - Per riddle: 27 seconds
  - Minimum total: 60 seconds
  - Maximum total: 90 seconds
  - Target total: 75 seconds

- Automatic Adjustments:
  - Minimum riddles: max(2, min_duration/27)
  - Maximum riddles: min(4, max_duration/27)
  - Optimal count: Adjusted based on input and constraints

##### Example Commands
```bash
# Basic usage with defaults
python main.py -c geography

# Full specification
python main.py -c physics -d hard -n 3 -o output/physics

# Multiple riddles with custom output
python main.py -c math -n 4 -o output/math_collection
```

##### Error Handling
- Category validation
- Difficulty level validation
- Output directory creation
- Duration constraints
- API availability checks

##### Output
- Video file: `riddle_[category]_[hash].mp4`
- Location: Specified output directory
- Format: Portrait video (1080x1920)
- Encoding: h264 with AAC audio

### Core Components

#### Core (`core/`)
Core application logic:

- **`riddler.py`**
  - Description: Main riddle generation and processing engine
  - Features:
    - Riddle generation orchestration
    - Service coordination
    - Video compilation management
    - End-to-end riddle processing

- **`__init__.py`**
  - Description: Package initialization
  - Purpose: Makes core a Python package

#### Services (`services/`)
Service integrations and APIs:

- **`openai_service.py`**
  - Description: OpenAI integration service
  - Features:
    - GPT-4 riddle generation
    - Category-specific prompting
    - Response validation
    - Error handling

- **`video_service.py`**
  - Description: Video processing service
  - Features:
    - Pexels API integration
    - Background video management
    - Video segment processing
    - Format standardization

- **`tts_service.py`**
  - Description: Text-to-speech service
  - Features:
    - ElevenLabs integration
    - Voice synthesis
    - Audio caching
    - Format conversion

- **`__init__.py`**
  - Description: Package initialization
  - Purpose: Makes services a Python package

### Asset Management

#### Assets (`assets/`)
Static assets and resources:

- **Audio** (`audio/`)
  - Description: Static audio assets
  - Files:
    - `countdown.mp3`: Countdown timer sound effect (3 seconds)
    - `reveal.mp3`: Answer reveal sound effect
  - Usage:
    - Countdown: Played during thinking time segments
    - Reveal: Played before answer reveals
  - Format: MP3, optimized for TikTok

- **Video** (`video/`)
  - Description: Directory for static video assets
  - Status: Currently empty
  - Purpose: Reserved for future static video assets like:
    - Transition effects
    - Background templates
    - Overlay elements
  - Note: Currently using dynamic video generation and Pexels API for backgrounds

### Cache Directories

#### Cache (`cache/`)
Cached assets storage system with the following subdirectories:

- **Voice** (`voice/`)
  - Description: Voice output cache for TTS generations
  - File types: `.mp3`
  - Naming: SHA-256 hash-based filenames
  - Provider: ElevenLabs TTS

- **Video** (`video/`)
  - Description: Video output and background cache
  - File types: `.mp4`
  - Naming: SHA-256 hash-based filenames
  - Features: Hardware-accelerated encoding (h264_videotoolbox)

- **Riddles** (`riddles/`)
  - Description: Generated riddles and metadata cache
  - File types: `.json`, `.pkl`
  - Naming: SHA-256 hash-based filenames
  - Content: Riddle text, answers, and metadata

- **Intermediate** (`intermediate/`)
  - Description: Temporary processing files
  - Purpose: Stores intermediate files during video generation
  - Content: Partial video segments, audio mixes
  - Status: Cleaned up after final video compilation
  - Management: Automatic cleanup during processing

- **Pexels Cache** (`pexels_cache/`)
  - Description: Cached Pexels API responses and videos
  - Content: Background videos and metadata
  - Management: Automatic cleanup based on usage

- **Voice Cache** (`voice_cache/`)
  - Description: Legacy voice cache directory
  - Status: Deprecated, use `cache/voice/` instead

#### Configuration (`config/`)
Schema-validated configuration management:

- **`config.py`**
  - Description: Configuration loader and manager
  - Features: JSON config loading, schema validation, default config generation

- **`schema.py`**
  - Description: Configuration schema definitions
  - Validates: Video settings, TTS settings, riddle formats, OpenAI parameters

- **`config.json`**
  - Description: Main configuration file
  - Contains: All configurable parameters with defaults

- **`exceptions.py`**
  - Description: Custom exception definitions
  - Exceptions:
    - `RiddlerException`: Base exception class
    - `ConfigurationError`: Configuration-related errors
    - `ConfigValidationError`: Schema validation errors
    - `VideoProcessingError`: Video processing failures
    - `AudioProcessingError`: Audio processing issues
    - `ContentGenerationError`: AI generation errors
    - `ResourceError`: System resource issues
    - `CacheError`: Cache operation failures
    - `ValidationError`: Input validation errors

- **`__init__.py`**
  - Description: Package initialization
  - Purpose: Makes config a Python package

#### Utils (`utils/`)
Utility functions and helpers:

- **`cache.py`**
  - Description: Advanced cache management
  - Features:
    - Compression with zlib
    - Thread-pooled operations
    - Automatic cleanup
    - Cache statistics tracking

- **`video_effects_engine.py`**
  - Description: Video processing engine
  - Features:
    - Text overlays with smart positioning
    - Dynamic zoom effects
    - Background video management
    - Multi-segment video compilation
    - Hardware-accelerated encoding
    - Audio-video synchronization

- **`helpers.py`**
  - Description: General utility functions
  - Features: API key management, directory handling, environment loading

- **`validators.py`**
  - Description: Input validation utilities
  - Validates: Categories, difficulties, file paths, cache directories

- **`logger.py`**
  - Description: Advanced logging system
  - Features:
    - Structured logging with loguru
    - Rotating log files
    - Log compression
    - Error-specific logging
    - Custom log formatting
    - Log retention policies
    - Debug/Info/Error levels
    - Console and file outputs

- **`decorators.py`**
  - Description: Utility decorators
  - Features:
    - Retry mechanism with exponential backoff
    - Error handling
    - Logging integration
    - Performance monitoring
    - Thread safety

- **`__init__.py`**
  - Description: Package initialization
  - Purpose: Makes utils a Python package

### Python Package Structure
The project follows standard Python packaging conventions:
- Each directory containing Python modules has an `__init__.py`
- Package hierarchy:
  ```
  riddler/
  ├── core/
  │   └── __init__.py
  ├── services/
  │   └── __init__.py
  ├── config/
  │   └── __init__.py
  └── utils/
      └── __init__.py
  ```
- Purpose:
  - Marks directories as Python packages
  - Enables relative imports
  - Maintains clean import hierarchy
  - Supports future PyPI packaging

#### Output (`output/`)
Generated video output directory:
- File types: `.mp4`
- Naming pattern: `riddle_[category]_[hash].mp4`
- Video specs: 1080x1920 (portrait), 30fps, h264 encoding

#### Logs (`logs/`)
Application logging directory:
- File types: `.log`, `.zip`
- Features:
  - Rotating log files
  - Compressed archives
  - Error-specific logs
  - Structured logging

##### Log File Types
- **Main Logs** (`riddler_[timestamp].log`)
  - Description: General application logs
  - Content:
    - Info level messages
    - Debug information
    - Operation statistics
    - Processing details
  - Format: Structured JSON with timestamps

- **Error Logs** (`riddler_errors_[timestamp].log`)
  - Description: Error-specific logging
  - Content:
    - Error messages
    - Stack traces
    - Exception details
    - Failure diagnostics
  - Format: Structured JSON with error context

##### Log File Management
- **Naming Convention**:
  - Pattern: `riddler_[type]_YYYY-MM-DD_HH-mm-ss_microseconds.log`
  - Example: `riddler_2025-01-09_00-32-33_838088.log`

- **Rotation Policy**:
  - Size-based: 100MB per file
  - Time-based: Daily rotation
  - Compression: Automatic ZIP after rotation

- **Retention Policy**:
  - Duration: 1 week
  - Cleanup: Automatic
  - Archive: Compressed storage

- **Log Levels**:
  - DEBUG: Detailed debugging information
  - INFO: General operational information
  - WARNING: Warning messages
  - ERROR: Error conditions
  - CRITICAL: Critical conditions

- **Structured Data**:
  - Timestamp
  - Log level
  - Module/Function
  - Line number
  - Message
  - Context data
  - Performance metrics

## Technical Capabilities

### Riddle Generation
- **Categories**: geography, math, physics, history, logic, wordplay
- **Difficulty Levels**: 
  - Easy (complexity: 0.3, elementary level)
  - Medium (complexity: 0.6, high school level)
  - Hard (complexity: 0.9, college level)
- **OpenAI Integration**:
  - Model: gpt-4o-2024-08-06
  - Temperature: 0.7
  - Max tokens: 500
  - Cached responses

### Video Processing
- **Resolution Support**:
  - Portrait: 1080x1920 (default)
  - Landscape: Configurable
  - Square: Configurable
- **Video Effects**:
  - Smart text overlays with gradient backgrounds
  - Dynamic zoom animations
  - Configurable transitions
  - Background video looping
- **TikTok Optimization**:
  - Target duration: 27 seconds
  - Hook duration: 3 seconds
  - End screen: 2 seconds
  - Optimized sound effects

### Voice Synthesis
- **Provider**: ElevenLabs
- **Features**:
  - Configurable voice stability
  - Similarity boost adjustment
  - Language support (default: en-US)
  - Cached voice outputs

### Cache Management
- **Features**:
  - Hierarchical storage
  - Compression (zlib)
  - Thread-pooled operations
  - Automatic cleanup
  - Cache statistics
- **Default Limits**:
  - Video cache: 5GB
  - Cleanup threshold: 90%
  - Compression levels: Configurable

## Development Guidelines

### Cache Management
- Use `CacheManager` for all caching operations
- Implement proper cleanup with `cleanup_threshold`
- Utilize compression for non-media files
- Follow hash-based naming convention

### Video Processing
- Use hardware acceleration when available
- Implement proper resource cleanup
- Follow TikTok optimization guidelines
- Handle video segment transitions properly

### Configuration
- Always validate against schema
- Use environment variables for sensitive data
- Follow the configuration hierarchy
- Implement proper error handling

## Testing
- Framework: pytest
- Coverage tracking: pytest-cov
- Async testing: pytest-asyncio
- Parallel testing: pytest-xdist
- Timeout handling: pytest-timeout

## Dependencies
Key packages:
- openai>=1.0.0: AI riddle generation
- moviepy>=1.0.3: Video processing
- elevenlabs>=0.2.26: TTS synthesis
- opencv-python>=4.8.0: Video effects
- ffmpeg-python>=0.2.0: Video encoding
- loguru>=0.7.2: Structured logging

## Setup and Installation

### Environment Setup

#### Environment Variables (`.env`)
Required environment variables:
```
RIDDLER_OPENAI_API_KEY=your_openai_key
RIDDLER_ELEVENLABS_API_KEY=your_elevenlabs_key
RIDDLER_PEXELS_API_KEY=your_pexels_key
RIDDLER_ENV=development|production
```

#### Setup Script (`setup.sh`)
Installation and setup script:
- Features:
  - Environment setup
  - Dependency installation
  - Directory structure creation
  - Permission configuration
  - Asset download and verification

- Directory Creation:
  ```bash
  config/
  core/
  services/
  utils/
  tests/
  cache/voice/
  cache/video/
  assets/audio/
  assets/video/
  output/
  ```

- Configuration Setup:
  - Creates default `config.json` if not exists
  - Default settings:
    ```json
    {
        "tts": {
            "voice": "alloy",
            "model": "tts-1"
        },
        "video": {
            "resolution": [1080, 1920],
            "fps": 30,
            "background_color": "black"
        },
        "style": {
            "riddle_duration": 5.0,
            "answer_duration": 3.0,
            "transition_duration": 1.0,
            "font": "Arial",
            "font_size": 70
        },
        "cache": {
            "max_size_gb": 10,
            "max_age_days": 7
        }
    }
    ```

- Environment Setup:
  - Creates `.env` template
  - Required API keys:
    - OpenAI API key
    - Pexels API key
  - Game settings configuration

- Asset Verification:
  - Checks for required audio files:
    - `background.mp3`
    - `celebration.mp3`
    - `countdown.mp3`
    - `hook.mp3`
    - `reveal.mp3`

- Example Content:
  - Creates example riddle in `examples/riddle.json`
  - Sample riddle format:
    ```json
    {
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "answer": "An Echo",
        "category": "nature",
        "difficulty": "medium"
    }
    ```

- Usage:
  ```bash
  chmod +x setup.sh
  ./setup.sh
  ```

- Post-Setup Steps:
  1. Add API keys to `.env`
  2. Add required audio files to `assets/audio/`
  3. Add background videos to `assets/video/` (optional)
  4. Run CLI help command for available options

### Dependencies

#### Package Requirements (`requirements.txt`)
Core dependencies:
- AI and ML:
  - openai>=1.0.0
  - scikit-image>=0.22.0
  - openai-whisper>=20231117

- Video Processing:
  - moviepy>=1.0.3
  - opencv-python>=4.8.0
  - ffmpeg-python>=0.2.0
  - pillow>=10.0.0

- Audio Processing:
  - elevenlabs>=0.2.26
  - python-magic>=0.4.27

- Utilities:
  - requests>=2.31.0
  - python-dotenv>=1.0.0
  - pathlib>=1.0.1
  - tqdm>=4.66.0
  - loguru>=0.7.2
  - alive-progress>=3.1.5

- Data Handling:
  - pydantic>=2.5.0
  - jsonschema>=4.20.0
  - pyyaml>=6.0.1
  - toml>=0.10.2

- Development Tools:
  - pytest>=7.4.0
  - pytest-cov>=4.1.0
  - pytest-asyncio>=0.21.1
  - pytest-xdist>=3.3.1
  - black>=23.11.0
  - ruff>=0.1.6
  - mypy>=1.7.0

### Testing Configuration

#### Test Settings (`pytest.ini`)
Test framework configuration:
- Features:
  - Test discovery patterns
  - Timeout settings
  - Parallel execution settings
  - Coverage reporting
  - Environment variables
- Options:
  ```ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = --verbose --cov=. --cov-report=term-missing
  timeout = 300
  ```

## Version Control

### Git Configuration

#### Ignored Files (`.gitignore`)
Files and directories excluded from version control:
```
# Environment and IDE
.env
.venv/
venv/
.idea/
.vscode/
__pycache__/
*.pyc

# Cache directories
cache/
voice_cache/
pexels_cache/
output/

# Logs and temporary files
logs/
*.log
temp-*
.DS_Store

# Test coverage
.coverage
coverage.xml
htmlcov/
```

### Directory Structure
```
riddler/
├── assets/
│   ├── audio/
│   └── video/
├── cache/
│   ├── riddles/
│   ├── video/
│   └── voice/
├── config/
│   ├── config.json
│   ├── config.py
│   └── schema.py
├── core/
│   └── riddler.py
├── services/
│   ├── openai_service.py
│   ├── tts_service.py
│   └── video_service.py
├── utils/
│   ├── cache.py
│   ├── helpers.py
│   └── validators.py
├── .env
├── main.py
├── requirements.txt
└── setup.sh
```

### Documentation

#### Documentation Files
- **`docs.md`**
  - Description: Main documentation file
  - Format: Markdown
  - Content: Complete system documentation

- **`docs.json`**
  - Description: Machine-readable documentation
  - Format: JSON
  - Purpose:
    - API documentation generation
    - Documentation validation
    - Automated tooling support
  - Content:
    - Project metadata
    - Structure definitions
    - Development guidelines
    - Technical specifications

### Temporary Files

#### Processing Files
- **Temporary Audio** (`temp-audio.m4a`)
  - Description: Temporary audio file for video processing
  - Purpose: FFmpeg audio encoding buffer
  - Format: M4A/AAC
  - Status: Automatically cleaned up

- **Log Files** (`temp-audio.m4a.log`)
  - Description: FFmpeg processing logs
  - Content: 
    - Encoding parameters
    - Processing statistics
    - Debug information
  - Status: Temporary, cleaned up after processing

### Example Content

#### Examples Directory (`examples/`)
- Description: Example content directory
- Status: Created during setup
- Purpose: Provides sample content and templates
- Files:
  - `riddle.json`: Sample riddle format
    ```json
    {
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "answer": "An Echo",
        "category": "nature",
        "difficulty": "medium"
    }
    ```
- Note: Directory and files are created by `setup.sh`