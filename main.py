"""Command line interface for the Riddler"""

import argparse
import os
import sys
from typing import List, Dict
from core.riddler import Riddler
from config.exceptions import RiddlerException

def parse_args():
    """Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate riddle videos for TikTok"
    )
    
    parser.add_argument(
        "-c", "--category",
        type=str,
        required=True,
        help="Riddle category"
    )
    
    parser.add_argument(
        "-d", "--difficulty",
        type=str,
        default="medium",
        help="Riddle difficulty"
    )
    
    parser.add_argument(
        "-n", "--num_riddles",
        type=int,
        default=2,
        help="Number of riddles per video"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output",
        help="Output directory"
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    try:
        # Initialize Riddler with output directory
        riddler = Riddler(output_dir=args.output)
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        # Get timing configuration from riddler's config
        riddle_duration = riddler.config.get("video.tiktok_optimization.target_duration", 27)  # seconds per riddle
        min_duration = riddler.config.get("video.duration.min_total", 60)
        max_duration = riddler.config.get("video.duration.max_total", 90)
        target_duration = riddler.config.get("video.duration.target_total", 75)
        
        # Calculate optimal number of riddles
        min_riddles = max(2, int(min_duration / riddle_duration))
        max_riddles = min(4, int(max_duration / riddle_duration))
        optimal_riddles = min(max(args.num_riddles, min_riddles), max_riddles)
        
        # Generate riddles
        riddles = []
        for _ in range(optimal_riddles):
            try:
                riddle_data = riddler.generate_riddle(args.category, args.difficulty)
                riddles.append(riddle_data)
            except Exception as e:
                print(f"Error generating riddle: {str(e)}")
                continue
        
        if not riddles:
            raise RiddlerException("Failed to generate any riddles")
        
        # Create multi-riddle video
        output_path = os.path.join(args.output, f"riddle_{args.category}_{os.urandom(4).hex()}.mp4")
        final_video = riddler.create_multi_riddle_video(
            riddles=riddles,
            category=args.category,
            output_path=output_path
        )
        
        print(f"Successfully created video: {final_video}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 