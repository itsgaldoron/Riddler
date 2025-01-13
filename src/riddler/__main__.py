"""Command-line interface for the Riddler application."""

import argparse
import os
import sys
from typing import Optional

from riddler.core.application import Application
from riddler.config.exceptions import RiddlerException
from riddler.utils.logger import log

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate riddle videos for TikTok",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-c", "--category",
        required=True,
        choices=[
            "geography", "math", "physics",
            "history", "logic", "wordplay",
            "biker_mechanic"
        ],
        help="Riddle category"
    )
    
    parser.add_argument(
        "-d", "--difficulty",
        default="medium",
        choices=["easy", "medium", "hard"],
        help="Riddle difficulty"
    )
    
    parser.add_argument(
        "-n", "--num-riddles",
        type=int,
        default=2,
        help="Number of riddles per video"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory for generated videos"
    )
    
    parser.add_argument(
        "--config",
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--no-riddle-cache",
        action="store_true",
        help="Disable riddle caching"
    )
    
    return parser.parse_args()

def main() -> Optional[int]:
    """Main entry point for the Riddler application."""
    try:
        args = parse_args()
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        # Initialize application
        app = Application(config_path=args.config)
        
        # Generate riddles
        riddles = app.generate_riddle(
            category=args.category,
            num_riddles=args.num_riddles,
            difficulty=args.difficulty,
            no_cache=args.no_riddle_cache
        )
        
        if not riddles:
            raise RiddlerException("Failed to generate any riddles")
        
        # Create the video
        output_path = os.path.join(
            args.output,
            f"riddle_{args.category}_{os.urandom(4).hex()}.mp4"
        )
        
        app.create_riddle_video(
            riddles=riddles,
            output_path=output_path,
            category=args.category,
            difficulty=args.difficulty
        )
        
        log.info(f"Successfully created video: {output_path}")
        return 0
        
    except RiddlerException as e:
        log.error(f"Application error: {str(e)}")
        return 1
        
    except KeyboardInterrupt:
        log.info("\nOperation cancelled by user")
        return 130
        
    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 