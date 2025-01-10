"""Command line interface for the Riddler"""

import argparse
import os
from core.application import Application
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
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file"
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
        riddle_duration = config.get("video.tiktok_optimization.target_duration", 27)  # seconds per riddle
        min_duration = config.get("video.duration.min_total", 60)
        max_duration = config.get("video.duration.max_total", 90)
        
        # Calculate optimal number of riddles
        min_riddles = max(2, int(min_duration / riddle_duration))
        max_riddles = min(4, int(max_duration / riddle_duration))
        optimal_riddles = min(max(args.num_riddles, min_riddles), max_riddles)
        
        app.logger.info(f"Optimal number of riddles: {optimal_riddles}")
        
        # Generate riddles
        riddles = []
        for i in range(optimal_riddles):
            try:
                riddle_data = app.generate_riddle(
                    category=args.category,
                    difficulty=args.difficulty
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
                hook_text = "Can You Solve These Mind-Bending Riddles?"
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
            segments.append({
                "id": f"thinking_{i}",
                "type": "thinking",
                "text": "Time to think...",
                "index": len(segments)
            })
            
            # Add answer segment
            answer_text = f"Answer: {riddle['answer']}"
            if riddle.get("explanation"):
                answer_text += f"\n\n{riddle['explanation']}"
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
                transition_text = "Next Riddle..."
                transition_speech = app.generate_speech(transition_text)
                segments.append({
                    "id": f"transition_{i}",
                    "type": "transition",
                    "text": transition_text,
                    "voice_path": transition_speech,
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