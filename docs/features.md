# Riddler Features
*Version: 1.0.0*

This document provides an overview of Riddler's features and capabilities.

## Table of Contents
- [Riddle Generation](#riddle-generation)
- [Categories](#categories)
- [Difficulty Levels](#difficulty-levels)
- [Multimedia Capabilities](#multimedia-capabilities)
- [Smart Caching](#smart-caching)
- [Output Formats](#output-formats)

## Riddle Generation

Riddler uses OpenAI's GPT models to generate high-quality, engaging riddles. The system creates:

- The riddle text itself
- An explanation of the answer
- Hints for difficult riddles
- Metadata for categorization

Each riddle is structured for optimal engagement and educational value.

## Categories

Riddler supports the following riddle categories:

| Category | Description |
|----------|-------------|
| Geography | Riddles about countries, landmarks, and geographical features |
| Math | Mathematical puzzles and number-based riddles |
| Physics | Riddles about physical phenomena and scientific concepts |
| History | Historical events, figures, and periods |
| Logic | Logic puzzles and brain teasers |
| Wordplay | Linguistic puzzles and word-based riddles |
| Biker Mechanic | Riddles related to motorcycle mechanics and biker culture |

## Difficulty Levels

Riddles can be generated at three difficulty levels:

- **Easy**: Suitable for children and casual audiences
- **Medium**: Moderate difficulty for most audiences
- **Hard**: Challenging riddles for experienced puzzle solvers

## Multimedia Capabilities

### Text-to-Speech

Riddler converts riddle text into high-quality speech using ElevenLabs' API:

- Multiple voice options
- Natural speech patterns
- Adjustable speech parameters

### Video Generation

The system creates engaging videos with:

- Dynamic text overlays
- Background videos relevant to the riddle category
- Custom animations for question and answer segments
- TikTok-optimized vertical video output

## Smart Caching

Riddler implements an intelligent caching system to:

- Store generated riddles for reuse
- Cache video components for faster processing
- Retain API responses to reduce API calls
- Enable offline operation when possible

## Output Formats

Riddler can output content in several formats:

- MP4 video files
- Audio-only MP3 files
- JSON riddle data for integration with other systems
- Text-only riddle output

---

*Navigate: [Back to Index](index.md) | [Previous: Getting Started](getting-started.md) | [Next: Architecture](architecture.md)* 