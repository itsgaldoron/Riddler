# Riddler

A Python application that generates and presents geographic riddles with text-to-speech capabilities and video visualization. The app creates engaging TikTok-style videos featuring geographic riddles with voice-overs and background visuals.

## Features

- Geographic riddle generation
- Text-to-speech conversion using ElevenLabs and OpenAI
- Video visualization with background clips from Pexels
- TikTok-optimized video output (1080x1920)
- Caching system for voice and video assets
- Parallel processing for efficient video generation
- Configurable settings for video, audio, and text styling

## Project Structure

```
riddler/
├── config.py           # Configuration settings
├── riddle_content.py   # Riddle content generation
├── geographic_riddles.py # Geographic riddle specific logic
├── utils.py           # Utility functions
├── test_tts.py        # Text-to-speech testing
├── voice_cache/       # Cached voice files
├── pexels_cache/      # Cached video assets
└── output/            # Generated video output
```

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- ImageMagick installed on your system (for text rendering)

### Installing FFmpeg

- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)

### Installing ImageMagick

- **macOS**: `brew install imagemagick`
- **Linux**: `sudo apt-get install imagemagick`
- **Windows**: Download from [ImageMagick website](https://imagemagick.org/script/download.php)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd riddler
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
PEXELS_API_KEY=your_pexels_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Usage

Run the main script to generate geographic riddles:

```bash
python geographic_riddles.py
```

The generated video will be saved in the `output/` directory as `geographic_riddles.mp4`.

## Configuration

The application is highly configurable through the `config.py` file:

- Video settings (dimensions, FPS, font, colors)
- Timing settings for different video segments
- Cache directory locations
- API configurations
- Output settings (codecs, bitrate, etc.)
- Text styling and positioning
- Progress bar settings

## Cache Directories

- `voice_cache/`: Stores generated text-to-speech audio files
- `pexels_cache/`: Stores video assets used in the final output
- `output/`: Stores the final generated videos

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for text-to-speech capabilities
- [ElevenLabs](https://elevenlabs.io/) for voice generation
- [Pexels](https://www.pexels.com/) for video assets
- [MoviePy](https://zulko.github.io/moviepy/) for video processing 