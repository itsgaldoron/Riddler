from typing import Dict, List
import logging
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from riddler.config.exceptions import VideoCompositionError
from riddler.services.video.base import VideoCompositionServiceBase
from riddler.services.external.pexels_service import PexelsService
from riddler.services.video.effects_service import VideoEffectsService
from riddler.services.video.text_overlay_service import TextOverlayService
from riddler.services.audio.composition_service import AudioCompositionService
from riddler.services.timing.segment_timing_service import SegmentTimingService
from riddler.services.video.segment_service import SegmentService
from riddler.utils.logger import log

class VideoCompositionService(VideoCompositionServiceBase):
    def __init__(
        self,
        pexels_service: PexelsService,
        text_overlay: TextOverlayService,
        video_effects: VideoEffectsService,
        audio_composition: AudioCompositionService,
        segment_timing: SegmentTimingService,
        segment_service: SegmentService,
        config: Dict = None,
        logger: logging.Logger = None
    ):
        self.pexels_service = pexels_service
        self.text_overlay = text_overlay
        self.video_effects = video_effects
        self.audio_composition = audio_composition
        self.segment_timing = segment_timing
        self.segment_service = segment_service
        self.config = config or {}
        self.logger = logger or log

    def create_multi_riddle_video(
        self,
        riddle_segments: List[Dict],
        output_path: str,
        category: str
    ) -> bool:
        try:
            # Calculate timings first
            segment_timings = self.segment_timing.calculate_segment_timings(
                riddle_segments,
                self.config
            )
            
            # Process video segments
            video_segments = []
            
            for segment, timing in zip(riddle_segments, segment_timings):
                try:
                    # Get background video
                    video_path = self.pexels_service.get_video(category)
                    
                    # Create segment with video path and text
                    processed_segment = {
                        "video_path": video_path,
                        "text": segment.get("text", "")
                    }
                    
                    # Process the segment using SegmentService
                    processed_clip = self.segment_service.process_segment(
                        processed_segment,
                        {"duration": timing["duration"]}
                    )
                    
                    video_segments.append(processed_clip)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process segment {segment.get('id', '')}: {str(e)}")
                    raise VideoCompositionError(f"Failed to process segment: {str(e)}")
            
            # Concatenate all segments
            try:
                final_video = concatenate_videoclips(video_segments)
            except Exception as e:
                self.logger.error(f"Failed to concatenate video segments: {str(e)}")
                raise VideoCompositionError(f"Failed to concatenate segments: {str(e)}")
            
            # Handle audio composition
            try:
                final_audio = self.audio_composition.create_audio_composition(
                    riddle_segments,
                    {timing["id"]: timing["duration"] for timing in segment_timings}
                )
                
                # Combine video with audio
                final_video = final_video.set_audio(final_audio)
            except Exception as e:
                self.logger.error(f"Failed to add audio: {str(e)}")
                raise VideoCompositionError(f"Failed to add audio: {str(e)}")
            
            # Write final video
            try:
                # Get target resolution
                target_width = self.config.get("video", {}).get("resolution", {}).get("width", 1080)
                target_height = self.config.get("video", {}).get("resolution", {}).get("height", 1920)
                
                # Scale down for faster processing
                processing_width = target_width // 2
                processing_height = target_height // 2
                
                # Resize video for processing
                processing_video = final_video.resize((processing_width, processing_height))
                
                # Write video with optimized settings
                processing_video.write_videofile(
                    output_path,
                    codec='h264_videotoolbox',  # Use Apple Silicon hardware encoder
                    audio_codec='aac',
                    fps=self.config.get("video", {}).get("fps", 30),
                    preset='ultrafast',
                    threads=10,  # Use all available cores
                    temp_audiofile="temp-audio.m4a",
                    remove_temp=True,
                    ffmpeg_params=[
                        "-b:v", "8000k",  # High bitrate for quality
                        "-maxrate", "10000k",
                        "-bufsize", "20000k",
                        "-movflags", "+faststart",  # Enable streaming optimization
                        "-tune", "zerolatency",  # Minimize encoding latency
                        "-tag:v", "avc1",  # Ensure compatibility
                        "-vf", f"scale={target_width}:{target_height}"  # Scale back up for final output
                    ],
                    write_logfile=True,
                    logger="bar"
                )
            except Exception as e:
                self.logger.error(f"Failed to write video file: {str(e)}")
                raise VideoCompositionError(f"Failed to write video: {str(e)}")
            finally:
                # Clean up
                try:
                    final_video.close()
                    for video in video_segments:
                        video.close()
                except Exception as e:
                    self.logger.error(f"Error during cleanup: {str(e)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create video: {str(e)}")
            raise VideoCompositionError(f"Failed to create video: {str(e)}")
            
        finally:
            # Ensure all video files are closed
            try:
                for video in video_segments:
                    video.close()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {str(e)}") 