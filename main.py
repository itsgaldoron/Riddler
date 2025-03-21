"""
Riddler - AI-Powered Riddle Generation System

This file is part of Riddler.
Copyright (c) 2025 Riddler

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0
International License. To view a copy of this license, visit:
https://creativecommons.org/licenses/by-nc/4.0/
"""

"""Command line interface for the Riddler"""

import argparse
import os
from core.application import Application
from config.exceptions import RiddlerException
import random

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
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--no-riddle-cache",
        action="store_true",
        help="Disable riddle caching"
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    try:
        # Initialize application with optional config path
        app = Application(config_path=args.config)
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        
        # Get timing configuration
        config = app.config
        
        # Generate riddles
        riddles = []
        for i in range(args.num_riddles):
            try:
                riddle_data = app.generate_riddle(
                    category=args.category,
                    difficulty=args.difficulty,
                    no_cache=args.no_riddle_cache
                )
                # Add segment metadata
                riddle_data.update({
                    "id": f"riddle_{i}",
                    "type": "riddle",
                    "index": i
                })
                riddles.append(riddle_data)
            except Exception as e:
                print(f"Error generating riddle: {str(e)}")
                continue
        
        if not riddles:
            raise RiddlerException("Failed to generate any riddles")
        
        
        # Create segments for the video
        segments = []
        for i, riddle in enumerate(riddles):
            # Add hook segment for first riddle
            if i == 0:
                hook_patterns = config.get("riddle.format.hook_patterns", [])
                hook_text = random.choice(hook_patterns)
                hook_speech = app.generate_speech(hook_text)
                segments.append({
                    "id": "hook",
                    "type": "hook",
                    "text": hook_text,
                    "voice_path": hook_speech,
                    "index": len(segments)
                })
            
            # Add riddle question segment
            question_speech = app.generate_speech(riddle["riddle"])
            segments.append({
                "id": f"question_{i}",
                "type": "question",
                "text": riddle["riddle"],
                "voice_path": question_speech,
                "index": len(segments)
            })
            
            # Add thinking time segment
            thinking_patterns = config.get("riddle.format.thinking_patterns", [])
            thinking_text = random.choice(thinking_patterns)
            segments.append({
                "id": f"thinking_{i}",
                "type": "thinking",
                "text": thinking_text,
                "index": len(segments)
            })
            
            # Add answer segment
            answer_text = f"{riddle['answer']}"
            answer_speech = app.generate_speech(answer_text)
            segments.append({
                "id": f"answer_{i}",
                "type": "answer",
                "text": answer_text,
                "voice_path": answer_speech,
                "index": len(segments)
            })
            
            # Add transition for all but last riddle
            if i < len(riddles) - 1:
                next_riddle_patterns = config.get("riddle.format.next_riddle_patterns", [])
                transition_text = random.choice(next_riddle_patterns)
                transition_speech = app.generate_speech(transition_text)
                segments.append({
                    "id": f"transition_{i}",
                    "type": "transition",
                    "text": transition_text,
                    "voice_path": transition_speech,
                    "index": len(segments)
                })
        
        # Add CTA at the end of the video
        cta_patterns = config.get("riddle.format.call_to_action_patterns", [])
        cta_text = random.choice(cta_patterns)
        cta_speech = app.generate_speech(cta_text)
        segments.append({
            "id": "cta",
            "type": "cta",
            "text": cta_text,
            "voice_path": cta_speech,
            "index": len(segments)
        })
        
        # Create multi-riddle video
        output_path = os.path.join(args.output, f"riddle_{args.category}_{os.urandom(4).hex()}.mp4")
        final_video = app.create_riddle_video(
            riddle_segments=segments,
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