"""Command line interface for the Riddler"""

import argparse
import os
import sys
from typing import List, Optional

from core.riddler import Riddler
from utils.logger import log, StructuredLogger
from utils.validators import validate_category, validate_difficulty

def parse_args() -> argparse.Namespace:
    """Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate riddle videos for TikTok"
    )
    
    parser.add_argument(
        "-c", "--category",
        help="Riddle category (e.g., geography, math, physics)",
        type=str
    )
    
    parser.add_argument(
        "-d", "--difficulty",
        help="Difficulty level (easy, medium, hard)",
        type=str,
        default="medium"
    )
    
    parser.add_argument(
        "-n", "--num-riddles",
        help="Number of riddles to generate",
        type=int,
        default=1
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory for videos",
        type=str,
        default="output"
    )
    
    parser.add_argument(
        "--list-categories",
        help="List available riddle categories",
        action="store_true"
    )
    
    return parser.parse_args()

def list_categories() -> None:
    """List available riddle categories with descriptions"""
    categories = {
        "geography": "Riddles about places, landmarks, and natural features",
        "math": "Mathematical puzzles and number-based riddles",
        "physics": "Riddles about physical phenomena and laws of nature",
        "history": "Historical events, figures, and artifacts",
        "logic": "Logic puzzles and brain teasers",
        "wordplay": "Word games, puns, and linguistic riddles"
    }
    
    print("\nAvailable Categories:")
    print("-" * 50)
    for category, description in categories.items():
        print(f"{category:12} - {description}")
    print()

def main() -> None:
    """Main entry point"""
    try:
        # Parse arguments
        args = parse_args()
        
        # Initialize logger
        logger = StructuredLogger()
        
        # List categories if requested
        if args.list_categories:
            list_categories()
            return
        
        # Validate category if provided
        if not args.category:
            logger.error("Category is required")
            list_categories()
            sys.exit(1)
        
        try:
            validate_category(args.category)
            validate_difficulty(args.difficulty)
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize Riddler
        riddler = Riddler(
            output_dir=args.output_dir,
            logger=logger
        )
        
        # Generate riddles
        for i in range(args.num_riddles):
            try:
                # Generate riddle
                logger.info(
                    f"Generating riddle {i+1}/{args.num_riddles} "
                    f"({args.category}, {args.difficulty})"
                )
                
                riddle_data = riddler.generate_riddle(
                    args.category,
                    args.difficulty
                )
                
                # Create video
                output_path = riddler.create_video(
                    riddle_data,
                    args.category
                )
                
                logger.info(f"Created video: {output_path}")
                
            except Exception as e:
                logger.error(f"Error generating riddle {i+1}: {str(e)}")
                continue
        
        logger.info("Done!")
        
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 