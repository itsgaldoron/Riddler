from config import API
from elevenlabs.client import ElevenLabs
from pathlib import Path

def test_elevenlabs():
    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=API['elevenlabs']['api_key'])
    
    # Test text
    text = "Welcome to Geographic Riddles! Let's test if this voice generation works."
    
    # Generate audio with different voices
    for voice_name in ['Adam', 'Rachel', 'Antoni']:
        print(f"Testing voice: {voice_name}")
        try:
            # Generate audio
            audio = client.generate(
                text=text,
                voice=voice_name,
                model="eleven_monolingual_v1"
            )
            
            # Create test directory if it doesn't exist
            test_dir = Path("test_output")
            test_dir.mkdir(exist_ok=True)
            
            # Save the audio file
            output_path = test_dir / f"test_{voice_name.lower()}.mp3"
            with open(output_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            print(f"Successfully generated audio with {voice_name}. Saved to {output_path}")
            
        except Exception as e:
            print(f"Error with voice {voice_name}: {e}")

if __name__ == "__main__":
    test_elevenlabs() 