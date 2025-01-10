# Video Effects Engine Restructuring Plan

This document outlines the plan to restructure the `video_effects_engine.py` into a more service-oriented architecture.

## 1. New Directory Structure

```
services/
├── video/
│   ├── __init__.py
│   ├── composition_service.py    # Main video composition logic
│   ├── effects_service.py        # Video effects and filters
│   ├── text_overlay_service.py   # Text rendering and overlay
│   └── segment_service.py        # Video segment management
├── audio/
│   ├── __init__.py
│   └── composition_service.py    # Audio mixing and timing
└── timing/
    ├── __init__.py
    └── segment_timing_service.py # Timing calculations and management
```

## 2. Service Responsibilities

### VideoCompositionService
- **Purpose**: Main orchestrator for video creation
- **Responsibilities**:
  - Handles video segment concatenation
  - Manages the overall video creation workflow
  - Coordinates between other services
  - Handles final video output and encoding
- **Key Methods**:
  ```python
  def create_multi_riddle_video(
      self,
      riddle_segments: List[Dict],
      output_path: str,
      category: str
  ) -> bool
  ```

### VideoEffectsService
- **Purpose**: Handles video effects and processing
- **Responsibilities**:
  - Manages video effects and filters
  - Handles background video processing
  - Standardizes video formats
  - Applies transitions between segments
- **Key Methods**:
  ```python
  def apply_effect(self, clip: VideoFileClip, effect_type: str) -> VideoFileClip
  def standardize_video(self, clip: VideoFileClip, target_duration: float) -> VideoFileClip
  ```

### TextOverlayService
- **Purpose**: Manages text rendering and positioning
- **Responsibilities**:
  - Text rendering and positioning
  - Text wrapping and formatting
  - Safe zone calculations
  - Font and style management
- **Key Methods**:
  ```python
  def create_text_overlay(self, frame: np.ndarray, text: str) -> np.ndarray
  def calculate_text_layout(self, text: str, max_width: int) -> List[str]
  ```

### AudioCompositionService
- **Purpose**: Handles audio processing and synchronization
- **Responsibilities**:
  - Audio clip management
  - Audio mixing and synchronization
  - Audio timing management
  - Sound effects integration
- **Key Methods**:
  ```python
  def create_audio_composition(
      self,
      segments: List[Dict],
      timings: Dict[str, float]
  ) -> CompositeAudioClip
  ```

### SegmentTimingService
- **Purpose**: Manages timing calculations and synchronization
- **Responsibilities**:
  - Calculates segment durations
  - Manages timing between segments
  - Handles synchronization points
  - Maintains overall video timing
- **Key Methods**:
  ```python
  def calculate_segment_timings(
      self,
      segments: List[Dict],
      config: Dict
  ) -> List[Dict[str, float]]
  ```

## 3. Implementation Strategy

### Phase 1: Service Interfaces
1. Create base interfaces/abstract classes for each service
2. Define common types and data structures
3. Establish service boundaries and interactions

### Phase 2: Core Implementation
1. Implement each service following established patterns from existing services
2. Use dependency injection for service composition
3. Implement proper error handling and logging

### Phase 3: Integration
1. Create factory classes for service instantiation
2. Implement service coordinator/facade
3. Add configuration management

## 4. Benefits

### Improved Code Organization
- Single Responsibility Principle: Each service handles one specific aspect
- Clear separation of concerns
- Better code organization and navigation

### Enhanced Maintainability
- Smaller, focused files instead of one large file
- Easier to understand and modify individual components
- Better error isolation and handling

### Better Testing
- Easier to unit test individual components
- Improved test coverage
- Simpler mocking and dependency injection

### Increased Reusability
- Services can be used independently
- Easier to share code between projects
- Better component isolation

### Better Scalability
- Easier to add new features
- Simpler to modify existing functionality
- Better performance optimization opportunities

## 5. Migration Strategy

### Step 1: Create New Structure
- Set up new directory structure
- Create placeholder files
- Set up necessary imports

### Step 2: Incremental Migration
- Move functionality one service at a time
- Maintain backwards compatibility
- Add comprehensive tests

### Step 3: Integration
- Update main video creation flow
- Add proper error handling
- Implement logging and monitoring

### Step 4: Cleanup
- Remove old code
- Update documentation
- Finalize tests

## 6. Next Steps

1. Create base interfaces for each service
2. Implement VideoCompositionService as the first component
3. Add comprehensive tests
4. Continue with remaining services
5. Update main application to use new services

## 7. Service Integration Details

### Service Renaming and Reorganization
Current `video_service.py` should be renamed to better reflect its responsibility:

```
services/
├── external/
│   └── pexels_service.py    # Pexels API integration (formerly video_service.py)
├── video/
│   ├── __init__.py
│   ├── composition_service.py
│   ├── effects_service.py
│   ├── text_overlay_service.py
│   └── segment_service.py
├── audio/
│   ├── __init__.py
│   └── composition_service.py
└── timing/
    ├── __init__.py
    └── segment_timing_service.py
```

### Service Dependencies

#### VideoCompositionService
- **Dependencies**:
  - PexelsService (for background videos)
  - TextOverlayService (for text rendering)
  - VideoEffectsService (for effects)
  - AudioCompositionService (for audio)
  - SegmentTimingService (for timing)

#### Integration with Riddler
The Riddler class will:
1. Initialize all services
2. Coordinate service interactions
3. Handle error propagation

Example initialization:
```python
class Riddler:
    def __init__(self):
        self.pexels_service = PexelsService(
            min_duration=self.config.get("video.min_duration"),
            max_duration=self.config.get("video.max_duration"),
            min_width=self.config.get("video.min_width"),
            min_height=self.config.get("video.min_height"),
            orientation=self.config.get("video.orientation"),
            cache_dir=self.config.get("video.cache_dir"),
            logger=self.logger
        )
        
        self.video_composition = VideoCompositionService(
            pexels_service=self.pexels_service,
            text_overlay=TextOverlayService(),
            video_effects=VideoEffectsService(),
            audio_composition=AudioCompositionService(),
            segment_timing=SegmentTimingService(),
            config=self.config,
            logger=self.logger
        )
```

### Data Flow

1. **Request Initiation**
   - Riddler receives riddle generation request
   - Validates inputs and prepares data structures

2. **Timing Calculation**
   - SegmentTimingService calculates timing for all segments
   - Determines durations for each video section

3. **Resource Gathering**
   - PexelsService fetches background videos based on category
   - Audio files are prepared and validated

4. **Video Processing**
   - VideoEffectsService processes background videos
   - TextOverlayService adds text overlays
   - AudioCompositionService handles audio synchronization

5. **Final Composition**
   - VideoCompositionService combines all elements
   - Renders final video with proper encoding

### Example Flow Implementation

```python
class VideoCompositionService:
    def create_multi_riddle_video(
        self,
        riddle_segments: List[Dict],
        output_path: str,
        category: str
    ) -> bool:
        try:
            # Calculate timings first
            segment_timings = self.segment_timing.calculate_timings(riddle_segments)
            
            # Get background videos
            background_videos = []
            for segment in segment_timings:
                video_path = self.pexels_service.get_video(category)
                processed_video = self.video_effects.process_video(
                    video_path, 
                    segment.duration
                )
                background_videos.append(processed_video)
            
            # Create video segments with overlays
            video_segments = []
            for bg_video, segment, timing in zip(
                background_videos, 
                riddle_segments, 
                segment_timings
            ):
                overlay = self.text_overlay.create_overlay(
                    segment.text,
                    timing.duration
                )
                final_segment = self.video_effects.combine_video_overlay(
                    bg_video,
                    overlay
                )
                video_segments.append(final_segment)
                
            # Handle audio composition
            final_audio = self.audio_composition.create_composition(
                riddle_segments,
                segment_timings
            )
            
            return self.render_final_video(
                video_segments,
                final_audio,
                output_path
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create video: {str(e)}")
            return False
```

### Error Handling Strategy

#### Service-Specific Exceptions
```python
class PexelsServiceError(Exception): pass
class VideoCompositionError(Exception): pass
class AudioCompositionError(Exception): pass
class TextOverlayError(Exception): pass
class TimingServiceError(Exception): pass
```

#### Error Handling Flow
1. Each service implements its own error handling
2. Services throw specific exceptions
3. Riddler catches and handles service-specific errors
4. Proper cleanup is performed on error
5. Errors are logged with appropriate context

### Configuration Management

#### Configuration Structure
```python
config = {
    "video": {
        "resolution": {
            "width": 1080,
            "height": 1920
        },
        "fps": 30,
        "encoding": {
            "codec": "h264",
            "bitrate": "8000k"
        }
    },
    "audio": {
        "codec": "aac",
        "bitrate": "192k"
    },
    "timing": {
        "hook": {
            "min_duration": 5,
            "padding": 1
        },
        "question": {
            "padding": 2
        }
    }
}
```

#### Configuration Distribution
1. Each service accepts its own configuration section
2. Riddler loads master configuration and distributes to services
3. Services validate their specific config sections
4. Default values are provided for missing configurations

### Testing Strategy

#### Unit Tests
- Each service has its own test suite
- Mock dependencies for isolated testing
- Test error handling paths
- Validate configuration handling

#### Integration Tests
- Test service interactions
- Verify data flow between services
- Test end-to-end video creation
- Validate resource cleanup

#### Performance Tests
- Measure video processing times
- Monitor memory usage
- Test with various input sizes
- Validate resource management
