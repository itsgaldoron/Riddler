import sys
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
from riddler.config.exceptions import TextOverlayError
from riddler.services.video.base import TextOverlayServiceBase
from riddler.utils.logger import log

class TextOverlayService(TextOverlayServiceBase):
    def __init__(self, config: Dict = None, logger=None):
        self.config = config or {}
        self.logger = logger or log
        # Use system font on macOS, fallback to downloaded font on other systems
        if sys.platform == "darwin":  # macOS
            self.font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        else:
            self.font_path = self.config.get("font_path", "src/riddler/resources/fonts/Roboto-Bold.ttf")
        
        # Get text overlay config
        text_overlay_config = self.config.get("presentation", {}).get("text_overlay", {})
        
        # Font settings
        self.font_size = text_overlay_config.get("font_size", 96)
        self.text_color = text_overlay_config.get("color", "#FFFFFF")
        if isinstance(self.text_color, str):
            # Convert hex to RGB
            self.text_color = tuple(int(self.text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        self.highlight_color = self.config.get("highlight_color", (255, 255, 0))
        self.stroke_width = self.config.get("stroke_width", 3)
        self.stroke_color = self.config.get("stroke_color", (0, 0, 0))
        
        # Padding settings
        self.padding_x = text_overlay_config.get("padding", 30)
        self.padding_y = text_overlay_config.get("padding", 30)
        
        # Emoji settings
        emoji_config = text_overlay_config.get("emoji", {})
        self.emoji_font_size = emoji_config.get("font_size", 96)
        self.emoji_scale_factor = emoji_config.get("scale_factor", 3)
        self.emoji_vertical_position = emoji_config.get("vertical_position", 0.7)
        self.emoji_horizontal_spacing = emoji_config.get("horizontal_spacing", 0.15)
        self.emoji_center_position = emoji_config.get("center_position", 0.5)
        
        # Fade duration
        self.fade_duration = self.config.get("text", {}).get("fade_duration", 0.15)
        
        # Keep both fonts - one for emojis, one for text
        if sys.platform == "darwin":  # macOS
            self.emoji_font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
        else:
            self.emoji_font_path = None  # No emoji font for other systems

    def create_text_overlay(
        self, 
        clip: VideoFileClip, 
        text: str, 
        emoji: Optional[str] = None,
        timestamps: Optional[Dict] = None
    ) -> VideoFileClip:
        try:
            # Get video dimensions
            width, height = clip.size
            
            # Calculate text layout
            lines = self.calculate_text_layout(text, width * 0.8)  # Use 80% of width
            
            # Create base text clip without highlighting
            base_text_clip = self.create_base_text_clip(clip, lines, width, height, emoji)
            
            if timestamps:
                # Create highlight clips for each word
                highlight_clips = self.create_word_highlight_clips(
                    clip, lines, width, height, timestamps
                )
                
                # Composite all clips
                clips = [clip, base_text_clip] + highlight_clips
                return CompositeVideoClip(clips)
            
            return CompositeVideoClip([clip, base_text_clip])
            
        except Exception as e:
            self.logger.error(f"Failed to create text overlay: {str(e)}")
            raise TextOverlayError(f"Failed to create text overlay: {str(e)}")

    def create_base_text_clip(
        self, 
        clip: VideoFileClip,
        lines: List[str],
        width: int,
        height: int,
        emoji: Optional[str] = None
    ) -> VideoFileClip:
        # Create PIL Image for text
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        font = ImageFont.truetype(self.font_path, self.font_size)
        emoji_font = ImageFont.truetype(self.emoji_font_path, self.emoji_font_size) if self.emoji_font_path else font
        
        # Calculate total text height
        line_height = self.font_size * 1.5
        total_height = len(lines) * line_height
        
        # Start position (centered vertically and horizontally)
        y = (height - total_height) / 2
        
        # Draw each line
        for line in lines:
            # Get line width
            text_width = draw.textlength(line, font=font)
            x = (width - text_width) / 2
            
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

        # Draw emoji if present - in lower third of video
        if emoji and self.emoji_font_path:
            self.logger.info(f"Video dimensions: {width}x{height}")
            self.logger.info(f"Emoji string: {emoji}, length: {len(emoji)}")  # Debug log
            
            # Create a smaller container for the emojis
            container_width = width // self.emoji_scale_factor
            container_height = height // self.emoji_scale_factor
            emoji_img = Image.new('RGBA', (container_width, container_height), (0, 0, 0, 0))
            emoji_draw = ImageDraw.Draw(emoji_img)
            
            # Load emoji font
            emoji_font = ImageFont.truetype(self.emoji_font_path, self.emoji_font_size)
            
            # Split the emoji string into individual emojis
            emojis = [emoji for emoji in emoji]
            num_emojis = len(emojis)
            self.logger.info(f"Split emojis: {emojis}, count: {num_emojis}")
            
            # Calculate center position and spacing
            center_x = int(container_width * self.emoji_center_position)
            spacing = int(container_width * self.emoji_horizontal_spacing * 2)  # Double the spacing
            vertical_pos = int(container_height * self.emoji_vertical_position)
            
            # Calculate total width of all emojis including spacing
            total_emoji_width = (num_emojis - 1) * spacing
            start_x = center_x - (total_emoji_width // 2)
            
            # Draw each emoji at its position
            for i, emoji_char in enumerate(emojis[:3]):  # Limit to 3 emojis
                x = start_x + (i * spacing)
                self.logger.info(f"Drawing emoji {i+1}: {emoji_char} at position ({x}, {vertical_pos})")
                emoji_draw.text((x, vertical_pos), emoji_char, font=emoji_font, anchor="mm", embedded_color=True)
            
            # Scale up the image
            emoji_img = emoji_img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Paste emoji image onto main image
            img.paste(emoji_img, (0, 0), emoji_img)

        # Convert PIL image to numpy array
        text_array = np.array(img)
        
        # Create MoviePy clip from text overlay
        return ImageClip(text_array, duration=clip.duration)

    def create_word_highlight_clips(
        self,
        clip: VideoFileClip,
        lines: List[str],
        width: int,
        height: int,
        timestamps: Dict
    ) -> List[VideoFileClip]:
        highlight_clips = []
        font = ImageFont.truetype(self.font_path, self.font_size)
        line_height = self.font_size * 1.5
        total_height = len(lines) * line_height
        start_y = (height - total_height) / 2
        
        # Create a temporary image and draw object for text measurements
        temp_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp_img)

        # Group characters into words with position tracking
        words = []
        current_word = {
            'chars': [],
            'start_time': None,
            'end_time': None,
            'position': 0  # Track the word's position in the text
        }

        # Process characters to form words
        word_position = 0
        for char, start_time, end_time in zip(
            timestamps["characters"],
            timestamps["character_start_times_seconds"],
            timestamps["character_end_times_seconds"]
        ):
            if char.isspace():
                if current_word['chars']:
                    words.append(current_word)
                    word_position += 1
                    current_word = {
                        'chars': [],
                        'start_time': None,
                        'end_time': None,
                        'position': word_position
                    }
            else:
                if not current_word['chars']:
                    current_word['start_time'] = start_time
                    current_word['position'] = word_position
                current_word['chars'].append(char)
                current_word['end_time'] = end_time

        # Add the last word if it exists
        if current_word['chars']:
            words.append(current_word)

        # Create highlight clips for each word
        for word in words:
            word_text = ''.join(word['chars'])
            duration = word['end_time'] - word['start_time']
            target_position = word['position']

            # Find the specific instance of this word based on position
            current_y = start_y
            current_word_position = 0
            found_target = False
            
            for line in lines:
                words_in_line = line.split()
                line_start_x = (width - draw.textlength(line, font=font)) / 2
                x = line_start_x
                
                for word_in_line in words_in_line:
                    if current_word_position == target_position:
                        # This is the specific word instance we want to highlight
                        word_width = draw.textlength(word_text, font=font)
                        word_height = self.font_size
                        
                        # Calculate text metrics for vertical centering
                        text_bbox = draw.textbbox((0, 0), word_text, font=font)
                        text_height = text_bbox[3] - text_bbox[1]
                        
                        # Calculate the vertical center position
                        line_center_y = current_y + (line_height / 2)
                        text_center_y = line_center_y - (text_height / 4)  # Adjust baseline offset
                        
                        # Position highlight box with adjusted padding
                        highlight_height = text_height + self.padding_y * 1.5  # Increase padding
                        highlight_y = text_center_y - (highlight_height / 2.2)  # Move highlight box higher up
                        
                        # Create highlight rectangle centered around the text
                        highlight_clip = ColorClip(
                            size=(int(word_width + self.padding_x * 2), int(highlight_height)),
                            color=self.highlight_color,
                            duration=duration
                        ).set_position((int(x - self.padding_x), int(highlight_y)))
                        
                        # Set opacity
                        highlight_clip = highlight_clip.set_opacity(0.5)
                        
                        # Set start time and add to list
                        highlight_clip = highlight_clip.set_start(word['start_time'])
                        highlight_clips.append(highlight_clip)
                        found_target = True
                        break
                    
                    # Move x position to next word
                    word_width = draw.textlength(word_in_line, font=font)
                    space_width = draw.textlength(" ", font=font)
                    x += word_width + space_width
                    current_word_position += 1
                
                if found_target:
                    break
                    
                current_y += line_height

        return highlight_clips

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