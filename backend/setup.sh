#!/bin/bash

# Exit on error
set -e

echo "Setting up TikTok Riddle Video Generator Backend..."

# Create virtual environment if it doesn't exist
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create required directories
echo "Creating directories..."
mkdir -p config core services utils tests cache/voice cache/video assets/audio assets/video output

# Copy default config if it doesn't exist
if [ ! -f config/config.json ]; then
    echo "Creating default configuration..."
    cat > config/config.json << EOF
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
EOF
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here

# Game Settings
COUNTDOWN_DURATION=5
EOF
fi

# Create example riddle if it doesn't exist
if [ ! -f examples/riddle.json ]; then
    echo "Creating example riddle..."
    mkdir -p examples
    cat > examples/riddle.json << EOF
{
    "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
    "answer": "An Echo",
    "category": "nature",
    "difficulty": "medium"
}
EOF
fi

# Download sample audio files if they don't exist
echo "Checking audio assets..."
AUDIO_FILES=("background.mp3" "celebration.mp3" "countdown.mp3" "hook.mp3" "reveal.mp3")
for file in "${AUDIO_FILES[@]}"; do
    if [ ! -f "assets/audio/$file" ]; then
        echo "Warning: Missing audio file: $file"
        echo "Please add required audio files to assets/audio/"
    fi
done

echo "Backend setup complete!"
echo
echo "Next steps:"
echo "1. Add your API keys to .env"
echo "2. Add audio files to assets/audio/"
echo "3. Add background videos to assets/video/ (optional)"
echo "4. Run 'python main.py --help' to see available commands" 