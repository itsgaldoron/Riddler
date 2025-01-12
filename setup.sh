#!/bin/bash

# Exit on error
set -e

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python $required_version or higher is required"
    exit 1
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Use the appropriate activate command based on OS
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source .venv/bin/activate
else
    source .venv/Scripts/activate
fi

# Upgrade pip and install build tools
echo "Upgrading pip and installing build tools..."
python -m pip install --upgrade pip
python -m pip install hatch

# Install the package in editable mode with dev dependencies
echo "Installing package..."
pip install -e ".[dev]"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p cache/{voice,video,riddles} output logs

# Create .env template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << EOL
# Required API Keys
RIDDLER_PEXELS_API_KEY=your_pexels_api_key_here
RIDDLER_ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
RIDDLER_OPENAI_API_KEY=your_openai_api_key_here

# Optional Settings
RIDDLER_GAME_COUNTDOWN_DURATION=60
EOL
fi

echo -e "\nSetup completed successfully!"
echo -e "\nNext steps:"
echo "1. Edit the .env file with your API keys"
echo "2. Activate the virtual environment:"
echo "   - On Unix/macOS: source .venv/bin/activate"
echo "   - On Windows: .\\venv\\Scripts\\activate"
echo "3. Run the application: python -m riddler -c <category> -d <difficulty>" 