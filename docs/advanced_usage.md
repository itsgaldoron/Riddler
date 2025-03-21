# Advanced Usage Guide
*Version: 1.0.0*

This guide covers advanced usage scenarios and customization options for the Riddler application.

## Custom Configuration Profiles

You can create multiple configuration profiles for different use cases:

1. Create a new configuration file based on the default:
   ```bash
   cp config/config.json config/tiktok_profile.json
   ```

2. Edit the new configuration file with your preferred settings.

3. Use the custom configuration:
   ```bash
   python main.py -c geography --config config/tiktok_profile.json
   ```

## Customizing Voice Settings

### Using Different ElevenLabs Voices

1. Get your voice ID from the ElevenLabs dashboard
2. Update your configuration:
   ```json
   "tts": {
     "provider": "elevenlabs",
     "voice": "your-voice-id",
     "stability": 0.7,
     "similarity_boost": 0.8
   }
   ```

## Custom Video Effects

### Modifying Video Style

Edit the `style` section in your configuration:

```json
"style": {
  "riddle_duration": 6.0,
  "answer_duration": 4.0,
  "transition_duration": 1.5,
  "font": "Helvetica",
  "font_size": 80,
  "text_color": "#ffffff",
  "text_shadow": true,
  "text_shadow_color": "#000000",
  "text_background": true,
  "text_background_opacity": 0.8
}
```

### Using Local Background Videos

1. Place your background videos in `assets/video/`
2. Update your code to use local videos by setting the `use_local_backgrounds` flag:
   ```bash
   python main.py -c geography --use-local-backgrounds
   ```

## Caching Strategies

### Fine-tuning Cache Management

Adjust cache settings in your configuration:

```json
"cache": {
  "max_size_gb": 5,
  "max_age_days": 3,
  "cleanup_threshold": 0.85,
  "compression_level": 9,
  "enabled": true
}
```

### Manual Cache Management

Clear specific cache directories:

```bash
# Clear riddle cache
rm -rf cache/riddles/*

# Clear voice cache
rm -rf cache/voice/*

# Clear video cache
rm -rf cache/video/*

# Clear all caches
rm -rf cache/*/* && mkdir -p cache/voice cache/video cache/riddles cache/intermediate
```

## Extending the Application

### Adding a New Riddle Category

1. Modify `utils/validators.py` to include your new category
2. Update the OpenAI prompts in `services/openai/service.py` to support the new category
3. Optionally add category-specific background video queries

### Creating Custom Prompt Templates

1. Create a new prompt template file in `services/openai/prompts/`
2. Add your custom prompt with placeholders for variable content
3. Update the service to use your custom prompt

## Performance Optimization

### Hardware Acceleration

Enable hardware acceleration by setting the appropriate codec:

```json
"video": {
  "codec": "h264_videotoolbox"  # For macOS
  // "codec": "h264_nvenc"      # For NVIDIA GPUs
  // "codec": "h264_amf"        # For AMD GPUs
}
```

### Parallel Processing

Adjust the concurrency settings:

```json
"processing": {
  "max_workers": 4,
  "chunk_size": 10
}
```

## Debugging

### Enabling Debug Logs

Set the `LOG_LEVEL` environment variable in your `.env` file:

```
LOG_LEVEL=DEBUG
```

### Generating Test Riddles

Generate test riddles without creating videos:

```bash
python main.py -c geography -d medium --dry-run
```

## Integration with Other Systems

### Automated Video Generation

Set up a cron job for automated generation:

```bash
# Generate new riddles daily at 2 AM
0 2 * * * cd /path/to/riddler && python main.py -c geography -d medium -n 3 -o output/daily
```

### Webhooks and Notifications

Configure the application to send notifications when videos are complete:

```json
"notifications": {
  "enabled": true,
  "webhook_url": "https://your-webhook-url",
  "email": "your-email@example.com"
}
```

## Batch Processing with Scripts

For bulk riddle generation, you can create simple shell scripts:

```bash
#!/bin/bash
CATEGORIES=("geography" "math" "physics" "history")
DIFFICULTY=("easy" "medium" "hard")

for cat in "${CATEGORIES[@]}"; do
  for diff in "${DIFFICULTY[@]}"; do
    python main.py -c "$cat" -d "$diff" -n 3 -o "output/$cat/$diff"
  done
done
```

Save as `batch_generate.sh`, make executable with `chmod +x batch_generate.sh`, and run.

---

*Navigate: [Back to Index](index.md) | [Previous: Configuration](configuration.md) | [Next: Features](features.md)* 