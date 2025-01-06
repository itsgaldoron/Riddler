import click
from pathlib import Path
import json
from typing import Optional, List, Dict, Any
from core.app import RiddleApp
from config.config import Config
from utils.logger import log

@click.group()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to config file"
)
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]) -> None:
    """TikTok Riddle Video Generator CLI"""
    try:
        # Initialize application with config path
        config_path = config if config else "config/config.json"
        ctx.obj = RiddleApp(config_path=config_path)
        
    except Exception as e:
        click.echo(f"Error initializing application: {str(e)}", err=True)
        ctx.exit(1)

@cli.command()
@click.argument(
    "riddle_file",
    type=click.Path(exists=True)
)
@click.option(
    "--output",
    "-o",
    help="Output filename"
)
@click.option(
    "--background",
    "-b",
    type=click.Path(exists=True),
    help="Background video path"
)
@click.option(
    "--voice",
    "-v",
    help="TTS voice to use"
)
@click.pass_obj
def generate(
    app: RiddleApp,
    riddle_file: str,
    output: Optional[str],
    background: Optional[str],
    voice: Optional[str]
) -> None:
    """Generate a single riddle video"""
    try:
        # Load riddle data
        with open(riddle_file, "r") as f:
            riddle = json.load(f)
            
        # Generate video
        video_path = app.generate_video(
            category=riddle["category"],
            output_name=output,
            background_video=background,
            voice=voice
        )
        
        click.echo(f"Generated video: {video_path}")
        
    except Exception as e:
        click.echo(f"Error generating video: {str(e)}", err=True)

@cli.command()
@click.argument(
    "riddles_dir",
    type=click.Path(exists=True)
)
@click.option(
    "--backgrounds-dir",
    "-b",
    type=click.Path(exists=True),
    help="Directory containing background videos"
)
@click.option(
    "--output-prefix",
    "-o",
    default="riddle",
    help="Prefix for output filenames"
)
@click.option(
    "--voice",
    "-v",
    help="TTS voice to use for all videos"
)
@click.pass_obj
def batch(
    app: RiddleApp,
    riddles_dir: str,
    backgrounds_dir: Optional[str],
    output_prefix: str,
    voice: Optional[str]
) -> None:
    """Generate multiple riddle videos from a directory"""
    try:
        # Load all riddle files
        riddles = []
        riddle_files = sorted(Path(riddles_dir).glob("*.json"))
        
        if not riddle_files:
            click.echo("No riddle files found", err=True)
            return
            
        for file_path in riddle_files:
            with open(file_path, "r") as f:
                riddles.append(json.load(f))
                
        # Load background videos if specified
        background_videos = None
        if backgrounds_dir:
            background_videos = sorted(Path(backgrounds_dir).glob("*.mp4"))
            
        # Generate videos
        voices = [voice] * len(riddles) if voice else None
        
        videos = app.generate_batch(
            riddles,
            background_videos=background_videos,
            voices=voices,
            output_prefix=output_prefix
        )
        
        click.echo(f"Generated {len(videos)} videos")
        
    except Exception as e:
        click.echo(f"Error generating videos: {str(e)}", err=True)

@cli.command()
@click.pass_obj
def stats(app: RiddleApp) -> None:
    """Show application statistics"""
    try:
        stats = app.get_stats()
        
        click.echo("\nApplication Statistics:")
        click.echo("-" * 30)
        
        # Cache stats
        cache_stats = stats["cache"]
        click.echo("\nCache:")
        click.echo(f"Total Size: {cache_stats['total_size'] / 1024 / 1024:.2f} MB")
        click.echo(f"Items: {cache_stats['item_count']}")
        
        # Output stats
        click.echo(f"\nOutput Files: {stats['output_files']}")
        
        # Config summary
        click.echo("\nConfiguration:")
        cfg = stats["config"]
        click.echo(f"TTS Voice: {cfg['tts']['voice']}")
        click.echo(f"Video Resolution: {cfg['video']['resolution']}")
        
    except Exception as e:
        click.echo(f"Error getting stats: {str(e)}", err=True)

@cli.command()
@click.confirmation_option(
    prompt="Are you sure you want to clear all caches?"
)
@click.pass_obj
def clear_cache(app: RiddleApp) -> None:
    """Clear all cache directories"""
    try:
        app.clear_cache()
        click.echo("Cache cleared successfully")
    except Exception as e:
        click.echo(f"Error clearing cache: {str(e)}", err=True)

@cli.command()
@click.pass_obj
def voices(app: RiddleApp) -> None:
    """List available TTS voices"""
    try:
        voices = app.tts_service.get_available_voices()
        
        click.echo("\nAvailable Voices:")
        click.echo("-" * 30)
        
        for name, info in voices.items():
            click.echo(f"\n{name}:")
            click.echo(f"  Description: {info['description']}")
            click.echo(f"  Gender: {info['gender']}")
            
    except Exception as e:
        click.echo(f"Error listing voices: {str(e)}", err=True)

if __name__ == "__main__":
    cli() 