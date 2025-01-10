from typing import Dict, List
import logging
from moviepy.editor import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from config.exceptions import VideoCompositionError
from services.video.base import VideoCompositionServiceBase
from services.external.pexels_service import PexelsService
from services.video.effects_service import VideoEffectsService
from services.video.text_overlay_service import TextOverlayService
from services.audio.composition_service import AudioCompositionService
from services.timing.segment_timing_service import SegmentTimingService
from utils.logger import log

class VideoCompositionService(VideoCompositionServiceBase):
    def __init__(
        self,
        pexels_service: PexelsService,
        text_overlay: TextOverlayService,
        video_effects: VideoEffectsService,
        audio_composition: AudioCompositionService,
        segment_timing: SegmentTimingService,
        config: Dict = None,
        logger: logging.Logger = None
    ):
        self.pexels_service = pexels_service
        self.text_overlay = text_overlay
        self.video_effects = video_effects
        self.audio_composition = audio_composition
        self.segment_timing = segment_timing
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
            
            # Get background videos
            background_videos = []
            for segment in segment_timings:
                try:
                    video_path = self.pexels_service.get_video(category)
                    clip = VideoFileClip(video_path)
                    
                    # Ensure clip duration is sufficient
                    if clip.duration < segment["duration"]:
                        # Loop the clip if needed
                        n_loops = int(segment["duration"] / clip.duration) + 1
                        clip = clip.loop(n=n_loops)
                    
                    # Process the video
                    processed_video = self.video_effects.standardize_video(
                        clip, 
                        segment["duration"]
                    )
                    background_videos.append(processed_video)
                except Exception as e:
                    self.logger.error(f"Failed to process video for segment {segment['id']}: {str(e)}")
                    raise VideoCompositionError(f"Failed to process video: {str(e)}")
            
            # log the background videos
            self.logger.info(f"Background videos: {background_videos}")
            
            # Create video segments with overlays
            video_segments = []
            for bg_video, segment, timing in zip(
                background_videos, 
                riddle_segments, 
                segment_timings
            ):
                try:
                    
                    # Create text overlay
                    text = segment.get("text", "")
                    if text:
                        bg_video = self.text_overlay.create_text_overlay(bg_video, text)
                    
                    video_segments.append(bg_video)
                except Exception as e:
                    self.logger.error(f"Failed to create segment {segment['id']}: {str(e)}")
                    raise VideoCompositionError(f"Failed to create segment: {str(e)}")
                
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
                    for video in background_videos:
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
                for video in background_videos:
                    video.close()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {str(e)}") 