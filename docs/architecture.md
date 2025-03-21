# Riddler System Architecture
*Version: 1.0.0*

This document describes the architecture and main components of the Riddler system.

## Table of Contents
- [Overview](#overview)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Service Integration](#service-integration)
- [Folder Structure](#folder-structure)

## Overview

Riddler is built with a modular architecture that separates concerns between riddle generation, multimedia processing, and output creation. The application follows a pipeline architecture where each component handles a specific task in the riddle creation process.

## System Components

### Core Components

| Component | Description |
|-----------|-------------|
| **RiddleGenerator** | Handles riddle creation using OpenAI's API |
| **TTSProvider** | Converts text to speech using ElevenLabs |
| **VideoCreator** | Creates video with riddle content |
| **CacheManager** | Manages caching of riddles and media |
| **ConfigurationManager** | Handles configuration and settings |

### Support Services

| Service | Description |
|---------|-------------|
| **Logger** | Provides logging functionality |
| **APIClient** | Base class for API interactions |
| **MediaProcessor** | Handles media file manipulations |

## Data Flow

1. **Riddle Generation**
   - User initiates riddle creation with parameters
   - RiddleGenerator calls OpenAI API to create riddle content
   - Output is structured JSON with riddle text and metadata

2. **Text-to-Speech Conversion**
   - TTSProvider receives riddle text
   - Converts text to speech using ElevenLabs
   - Returns audio file path

3. **Video Creation**
   - VideoCreator receives riddle content and audio
   - Fetches background video from Pexels or local cache
   - Creates video with text overlays and audio
   - Returns final video file

## Service Integration

Riddler integrates with the following external services:

1. **OpenAI API**
   - Used for: Riddle generation
   - Integration point: `services/openai_service.py`
   - Authentication: API key in `.env` file

2. **ElevenLabs API**
   - Used for: Text-to-speech
   - Integration point: `services/elevenlabs_service.py`
   - Authentication: API key in `.env` file

3. **Pexels API**
   - Used for: Background video content
   - Integration point: `services/pexels_service.py`
   - Authentication: API key in `.env` file

## Folder Structure

```
riddler/
├── main.py                 # Application entry point
├── config/                 # Configuration files
│   └── config.json         # Main configuration
├── core/                   # Core functionality
│   ├── riddle_generator.py # Riddle generation
│   ├── tts_provider.py     # Text-to-speech
│   └── video_creator.py    # Video creation
├── services/               # External service integrations
│   ├── openai_service.py   # OpenAI API client
│   ├── elevenlabs_service.py # ElevenLabs API client
│   └── pexels_service.py   # Pexels API client
├── utils/                  # Utility functions
│   ├── cache_manager.py    # Cache management
│   ├── logger.py           # Logging utilities
│   └── media_processor.py  # Media processing utilities
├── assets/                 # Static assets
├── output/                 # Output directory
└── cache/                  # Cache directory
```

---

*Navigate: [Back to Index](index.md) | [Previous: Features](features.md) | [Next: Troubleshooting](troubleshooting.md)* 