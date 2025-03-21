# Getting Started with Riddler
*Version: 1.0.0*

This guide will help you set up and start using the Riddler application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Keys](#api-keys)
- [Basic Usage](#basic-usage)
- [Next Steps](#next-steps)

## Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** installed on your system
2. **FFmpeg 4.2+** installed for video processing
3. Required API keys (see [API Keys](#api-keys) section)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd riddler
   ```

2. Run the setup script to create directories and install dependencies:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Alternatively, install dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the required directories:
   ```bash
   mkdir -p output cache logs assets
   ```

## API Keys

Riddler requires the following API keys:

1. **OpenAI API Key**: For AI-based riddle generation
   - Sign up at [OpenAI Platform](https://platform.openai.com/account/api-keys)

2. **ElevenLabs API Key**: For text-to-speech functionality
   - Sign up at [ElevenLabs](https://elevenlabs.io/app/api-key)

3. **Pexels API Key**: For video background content
   - Sign up at [Pexels](https://www.pexels.com/api/new/)

Create a `.env` file in the project root with your API keys:
```
RIDDLER_OPENAI_API_KEY=your_openai_key
RIDDLER_ELEVENLABS_API_KEY=your_elevenlabs_key
RIDDLER_PEXELS_API_KEY=your_pexels_key
RIDDLER_ENV=development
```

## Basic Usage

Generate your first riddle with this command:

```bash
# Generate 2 medium difficulty geography riddles
python main.py -c geography -d medium -n 2 -o output
```

### Command-line Options

- `-c, --category`: Riddle category (geography, math, physics, etc.)
- `-d, --difficulty`: Difficulty level (easy, medium, hard)
- `-n, --num_riddles`: Number of riddles to generate (default: 2)
- `-o, --output`: Output directory (default: output)
- `--no-riddle-cache`: Disable riddle caching
- `--no-video-cache`: Disable video caching
- `--config`: Path to custom configuration file

## Next Steps

- See [Configuration](configuration.md) for customizing the application
- Explore [Advanced Usage](advanced_usage.md) for more features
- Check the [Troubleshooting](troubleshooting.md) guide if you encounter issues

---

*Navigate: [Back to Index](index.md) | [Next: Configuration](configuration.md)* 