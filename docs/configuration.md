# Riddler Configuration Guide

This document explains all configuration options available in the `config/config.json` file.

## Configuration Structure

The configuration file is structured in several sections:

```json
{
    "tts": { /* Text-to-speech settings */ },
    "video": { /* Video output settings */ },
    "style": { /* Visual style settings */ },
    "cache": { /* Caching behavior */ },
    "openai": { /* OpenAI API settings */ },
    "riddle": { /* Riddle generation settings */ }
}
```

## Text-to-Speech Settings

```json
"tts": {
    "provider": "elevenlabs",
    "voice": "alloy",
    "model": "tts-1",
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": true
}
```

- `provider`: TTS provider to use (currently supported: "elevenlabs")
- `voice`: Voice ID to use for synthesis
- `model`: Model name (e.g., "tts-1")
- `stability`: Voice stability (0.0-1.0)
- `similarity_boost`: Voice similarity boost (0.0-1.0)
- `style`: Style intensity (0.0-1.0)
- `use_speaker_boost`: Whether to use speaker boost feature

## Video Settings

```json
"video": {
    "resolution": [1080, 1920],
    "fps": 30,
    "background_color": "black",
    "codec": "h264_videotoolbox",
    "bitrate": "8M",
    "audio_bitrate": "192k",
    "format": "mp4"
}
```

- `resolution`: Video resolution as [width, height]
- `fps`: Frames per second
- `background_color`: Default background color
- `codec`: Video codec for encoding
- `bitrate`: Video bitrate
- `audio_bitrate`: Audio bitrate
- `format`: Output file format

## Style Settings

```json
"style": {
    "riddle_duration": 5.0,
    "answer_duration": 3.0,
    "transition_duration": 1.0,
    "font": "Arial",
    "font_size": 70,
    "text_color": "white",
    "text_shadow": true,
    "text_shadow_color": "black",
    "text_background": true,
    "text_background_opacity": 0.7
}
```

- `riddle_duration`: Duration to display riddle question (seconds)
- `answer_duration`: Duration to display answer (seconds)
- `transition_duration`: Transition time between segments (seconds)
- `font`: Font family for text
- `font_size`: Font size for main text
- `text_color`: Text color
- `text_shadow`: Whether to apply text shadow
- `text_shadow_color`: Shadow color
- `text_background`: Whether to apply text background
- `text_background_opacity`: Background opacity (0.0-1.0)

## Cache Settings

```json
"cache": {
    "max_size_gb": 10,
    "max_age_days": 7,
    "cleanup_threshold": 0.9,
    "compression_level": 6,
    "enabled": true
}
```

- `max_size_gb`: Maximum cache size in gigabytes
- `max_age_days`: Maximum age of cache items in days
- `cleanup_threshold`: Threshold to trigger cleanup (0.0-1.0)
- `compression_level`: Compression level for cached items (0-9)
- `enabled`: Whether caching is enabled

## OpenAI Settings

```json
"openai": {
    "model": "gpt-4o-2024-08-06",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

- `model`: OpenAI model to use
- `temperature`: Sampling temperature (0.0-2.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Nucleus sampling parameter
- `frequency_penalty`: Frequency penalty (0.0-2.0)
- `presence_penalty`: Presence penalty (0.0-2.0)

## Riddle Settings

```json
"riddle": {
    "complexity": {
        "easy": 0.3,
        "medium": 0.6,
        "hard": 0.9
    },
    "target_age": {
        "easy": "elementary",
        "medium": "high school",
        "hard": "college"
    },
    "educational": true,
    "style": "entertaining",
    "max_question_length": 150,
    "max_answer_length": 50
}
```

- `complexity`: Complexity levels for different difficulties
- `target_age`: Target age groups for different difficulties
- `educational`: Whether riddles should be educational
- `style`: Riddle style (e.g., "entertaining", "challenging")
- `max_question_length`: Maximum length for questions
- `max_answer_length`: Maximum length for answers

## Example Complete Configuration

See `config/config.json` for a complete example configuration. 