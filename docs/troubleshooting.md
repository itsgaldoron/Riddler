# Troubleshooting Guide
*Version: 1.0.0*

This guide provides solutions for common issues you might encounter when using Riddler.

## Table of Contents
- [API and Authentication Issues](#api-and-authentication-issues)
- [Installation Problems](#installation-problems)
- [Video Generation Issues](#video-generation-issues)
- [Performance Problems](#performance-problems)
- [Error Messages](#common-error-messages)

## API and Authentication Issues

### OpenAI API Key Issues

**Symptom**: `Authentication error: Invalid API key provided`

**Solutions**:
1. Check that your API key is correctly set in the `.env` file
2. Ensure the API key is active in your OpenAI dashboard
3. Try regenerating your API key in the OpenAI dashboard

### ElevenLabs API Issues

**Symptom**: `Unauthorized: Invalid API key` or no speech output

**Solutions**:
1. Verify your ElevenLabs API key in the `.env` file
2. Check your ElevenLabs subscription status and usage limits
3. Try a different voice ID in your configuration

### Pexels API Issues

**Symptom**: No background videos or `API rate limit exceeded`

**Solutions**:
1. Confirm your Pexels API key is correct in the `.env` file
2. Check if you've reached your API rate limit
3. Set a local video file as fallback in the configuration

## Installation Problems

### FFmpeg Not Found

**Symptom**: `FFmpeg executable not found` or `FFmpeg command failed`

**Solutions**:
1. Install FFmpeg: 
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt install ffmpeg`
   - Windows: Download from [FFmpeg.org](https://ffmpeg.org/download.html)
2. Add FFmpeg to your system PATH
3. Set the full path to FFmpeg in your configuration file

### Python Dependencies Issues

**Symptom**: Import errors or module not found errors

**Solutions**:
1. Reinstall dependencies: `pip install -r requirements.txt`
2. Try installing dependencies individually
3. Create a fresh virtual environment: 
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Video Generation Issues

### Invalid Segment Timings

**Symptom**: `Error: Invalid segment timings` or `Timestamps must be monotonically increasing`

**Solutions**:
1. Try increasing the pause between segments in the configuration
2. Generate more riddles (`-n 3` or higher)
3. Check if your audio files are valid

### Poor Video Quality

**Symptom**: Blurry or low-quality videos

**Solutions**:
1. Increase the video resolution in the configuration:
   ```json
   "video": {
     "width": 1080,
     "height": 1920,
     "fps": 30
   }
   ```
2. Use higher quality background videos
3. Check your FFmpeg installation for encoding support

## Performance Problems

### Slow Riddle Generation

**Symptom**: Riddle generation takes more than 30 seconds

**Solutions**:
1. Use caching: enable `"cache_riddles": true` in the configuration
2. Try a faster OpenAI model, such as "gpt-4-1106-preview"
3. Generate fewer riddles at a time

### High Memory Usage

**Symptom**: Application crashes with memory errors

**Solutions**:
1. Reduce video resolution in the configuration
2. Process fewer riddles at once
3. Clear the cache directory: `rm -rf cache/*`

## Common Error Messages

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| `OpenAI API request timed out` | Network issue or API overload | Retry or check OpenAI status page |
| `FFmpeg exited with code 1` | Invalid FFmpeg parameters | Check FFmpeg command in logs |
| `No such file or directory` | Missing directory | Create required directories |
| `JSONDecodeError` | Invalid API response | Check API key and retry |
| `Cache file corrupted` | Cache file issue | Clear cache: `--no-riddle-cache` |

---

*Navigate: [Back to Index](index.md) | [Previous: Architecture](architecture.md) | [Next: Development Guidelines](development.md)* 