from typing import Dict, List
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from riddler.config.exceptions import TextOverlayError
from riddler.services.video.base import TextOverlayServiceBase
from riddler.utils.logger import log

class TextOverlayService(TextOverlayServiceBase):
    def __init__(self, config: Dict = None, logger=None):
        self.config = config or {}
        self.logger = logger or log
        self.font_path = self.config.get("text", {}).get("font_path", "Arial")
        self.font_size = self.config.get("text", {}).get("font_size", 48)
        self.text_color = self.config.get("text", {}).get("color", "white")
        self.stroke_width = self.config.get("text", {}).get("stroke_width", 2)
        self.stroke_color = self.config.get("text", {}).get("stroke_color", "black")

    def create_text_overlay(self, clip: VideoFileClip, text: str) -> VideoFileClip:
        try:
            # Get video dimensions
            width, height = clip.size
            
            # Calculate text layout
            lines = self.calculate_text_layout(text, width * 0.8)  # Use 80% of width
            
            # Create PIL Image for text
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Load font
            font = ImageFont.truetype(self.font_path, self.font_size)
            
            # Calculate total text height
            line_height = self.font_size * 1.5
            total_height = len(lines) * line_height
            
            # Start position (centered vertically and horizontally)
            y = (height - total_height) / 2
            
            # Draw each line
            for line in lines:
                # Get line width
                line_width = draw.textlength(line, font=font)
                x = (width - line_width) / 2
                
                # Draw text stroke (outline)
                for offset_x in range(-self.stroke_width, self.stroke_width + 1):
                    for offset_y in range(-self.stroke_width, self.stroke_width + 1):
                        draw.text(
                            (x + offset_x, y + offset_y),
                            line,
                            font=font,
                            fill=self.stroke_color
                        )
                
                # Draw main text
                draw.text((x, y), line, font=font, fill=self.text_color)
                y += line_height
            
            # Convert PIL image to numpy array
            text_array = np.array(img)
            
            # Create MoviePy clip from text overlay
            text_clip = ImageClip(text_array, duration=clip.duration)
            
            # Composite text over video
            return CompositeVideoClip([clip, text_clip])
            
        except Exception as e:
            self.logger.error(f"Failed to create text overlay: {str(e)}")
            raise TextOverlayError(f"Failed to create text overlay: {str(e)}")

    def calculate_text_layout(self, text: str, max_width: int) -> List[str]:
        try:
            words = text.split()
            lines = []
            current_line = []
            
            # Load font for text measurements
            font = ImageFont.truetype(self.font_path, self.font_size)
            
            # Create temporary PIL Draw object for text measurements
            img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            for word in words:
                # Add word to current line
                test_line = current_line + [word]
                test_text = ' '.join(test_line)
                
                # Measure line width
                line_width = draw.textlength(test_text, font=font)
                
                if line_width <= max_width:
                    # Word fits, add it to current line
                    current_line = test_line
                else:
                    # Word doesn't fit, start new line
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            # Add last line if there is one
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
            
        except Exception as e:
            self.logger.error(f"Failed to calculate text layout: {str(e)}")
            raise TextOverlayError(f"Failed to calculate text layout: {str(e)}") 