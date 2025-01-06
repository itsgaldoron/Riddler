# TikTok Riddle Video Generator

An automated system for generating engaging riddle videos optimized for TikTok. The generator creates videos with text overlays, voice-overs, background music, and reveal animations.

## Features

- Generate single or batch riddle videos
- Text-to-speech voice-over using OpenAI's API
- Customizable video styles and transitions
- Background music and sound effects
- Caching system for generated content
- Command-line interface for easy use
- Configurable video resolution and formatting
- Multiple TTS voices to choose from
- Support for custom background videos

## Requirements

- Python 3.8+
- OpenAI API key
- FFmpeg (for video processing)
- Required audio assets (background music, sound effects)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tiktok-riddle-generator.git
cd tiktok-riddle-generator
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Add your API keys to `.env`:
```bash
OPENAI_API_KEY=your_openai_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

4. Add required audio files to `assets/audio/`:
- `background.mp3`: Background music
- `celebration.mp3`: Success sound
- `countdown.mp3`: Timer sound
- `hook.mp3`: Intro sound
- `reveal.mp3`: Answer reveal sound

## Usage

### Command Line Interface

Generate a single riddle video:
```bash
python -m core.cli generate examples/riddle.json --output my_riddle
```

Generate multiple videos from a directory:
```bash
python -m core.cli batch examples/ --output-prefix batch_riddle
```

Show available TTS voices:
```bash
python -m core.cli voices
```

View application statistics:
```bash
python -m core.cli stats
```

Clear cache:
```bash
python -m core.cli clear-cache
```

### Configuration

The application can be configured through `config/config.json`:

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

### Riddle Format

Riddles should be provided in JSON format:

```json
{
    "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
    "answer": "An Echo",
    "category": "nature",
    "difficulty": "medium"
}
```

## Project Structure

```
├── assets/
│   ├── audio/         # Audio assets
│   └── video/         # Background videos
├── cache/
│   ├── voice/         # TTS cache
│   └── video/         # Video cache
├── config/
│   ├── config.json    # Main configuration
│   └── schema.py      # Configuration schema
├── core/
│   ├── app.py         # Main application
│   └── cli.py         # Command line interface
├── services/
│   ├── tts.py         # Text-to-speech service
│   └── video.py       # Video generation service
├── utils/
│   ├── cache.py       # Cache management
│   ├── helpers.py     # Utility functions
│   └── logger.py      # Logging setup
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── setup.sh          # Setup script
```

## Development

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

### Running Tests

```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Missing FFmpeg**
   - Install FFmpeg using your package manager
   - Windows: Download from ffmpeg.org

2. **API Key Issues**
   - Ensure API keys are correctly set in `.env`
   - Check API key permissions and quotas

3. **Audio File Errors**
   - Verify all required audio files are present
   - Check audio file formats (MP3 recommended)

4. **Video Generation Fails**
   - Check FFmpeg installation
   - Verify sufficient disk space
   - Check log files for details

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for TTS API
- MoviePy developers
- FFmpeg project
- All contributors

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Roadmap

- [ ] Add more voice options
- [ ] Implement video templates
- [ ] Add background video library
- [ ] Improve caching system
- [ ] Add web interface 