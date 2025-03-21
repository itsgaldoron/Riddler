# Riddler - AI-Powered Riddle Generation System

![Riddler](https://img.shields.io/badge/Riddler-AI--Powered%20Riddles-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey)

Riddler is an advanced AI system that generates interactive riddles with video and voice capabilities, perfect for educational content and social media.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg 4.2+
- API keys for OpenAI, ElevenLabs, and Pexels

### Installation

```bash
# Clone repository
git clone <repository-url>
cd riddler

# Set up environment
./setup.sh

# Add your API keys to .env file
```

### Basic Usage

```bash
# Generate 2 medium difficulty geography riddles
python main.py -c geography -d medium -n 2 -o output
```

## 📚 Documentation

For complete documentation, see the [docs](docs/) directory.

Key documentation files:
- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)
- [Features](docs/features.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development Guidelines](docs/development.md)

## 🔑 Features

- AI-powered riddle generation across multiple categories
- Text-to-speech voice synthesis
- Dynamic video generation with text overlays
- Smart caching system
- TikTok-optimized video output

## 📋 Categories

- geography
- math
- physics
- history
- logic
- wordplay
- biker mechanic

## 🛠️ Configuration

Configuration is managed through `config/config.json`. See [configuration documentation](docs/configuration.md) for details.

## 📝 License

This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](LICENSE). Copyright (c) 2025 Riddler. 