# Quickstart Guide (Deprecated)
*Version: 1.0.0*

> **Note:** This quickstart guide has been replaced by the more comprehensive [Getting Started Guide](getting-started.md). Please refer to that document for the most up-to-date information.

This document will be removed in a future release.

---

*Navigate: [Getting Started](getting-started.md) | [Back to Index](index.md)*

# Riddler Quick Start Guide

This guide provides the fastest way to get up and running with Riddler.

## 1. Prerequisites

- Python 3.8+
- FFmpeg 4.2+
- API keys:
  - [OpenAI](https://platform.openai.com/account/api-keys)
  - [ElevenLabs](https://elevenlabs.io/app/api-key)
  - [Pexels](https://www.pexels.com/api/new/)

## 2. Installation

```bash
# Clone the repo
git clone <repository-url>
cd riddler

# Run setup script to create directories and install dependencies
chmod +x setup.sh
./setup.sh

# Create .env file (or copy from .env.example)
cp .env.example .env
```

## 3. Configure API Keys

Edit your `.env` file and add your API keys:

```
RIDDLER_OPENAI_API_KEY=your_openai_key
RIDDLER_ELEVENLABS_API_KEY=your_elevenlabs_key
RIDDLER_PEXELS_API_KEY=your_pexels_key
```

## 4. Generate Your First Riddle Video

```bash
# Generate 2 geography riddles of medium difficulty
python main.py -c geography -d medium -n 2 -o output
```

The video will be saved to the `output` directory.

## 5. Command Options

- `-c, --category`: Riddle category (geography, math, physics, etc.)
- `-d, --difficulty`: Difficulty level (easy, medium, hard)
- `-n, --num_riddles`: Number of riddles (default: 2)
- `-o, --output`: Output directory (default: output)

## 6. Troubleshooting

- If you get API errors, verify your API keys are correct
- For "Invalid segment timings" errors, try increasing the number of riddles
- Run without caching using `--no-riddle-cache` if you encounter cache errors

## Next Steps

See the [full documentation](../docs.md) for detailed information about the project. 