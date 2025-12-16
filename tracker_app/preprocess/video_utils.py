import cv2
import ffmpeg
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, Tuple, List
import numpy as np
from loguru import logger


def get_video_metadata(video_path: Path) -> Dict[str, Any]:
    """Extract video metadata using ffmpeg-python"""
    try:
        probe = ffmpeg.probe(str(video_path))
        video_stream = next(
            (s for s in probe['streams'] if s['codec_type'] == 'video'),
            None
        )
        
        if not video_stream:
            raise ValueError("No video stream found")
        
        # Calculate FPS
        fps_str = video_stream.get('r_frame_rate', '0/1')
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 0
        
        # Duration
        duration = float(probe['format'].get('duration', 0))
        
        metadata = {
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'fps': fps,
            'duration_s': duration,
            'codec': video_stream.get('codec_name'),
            'frames': int(video_stream.get('nb_frames', duration * fps))
        }
        
        return metadata
    
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error reading {video_path}: {e.stderr.decode()}")
        raise


def extract_frames(
    video_path: Path,
    target_fps: Optional[int] = None
) -> Iterator[Tuple[int, float, np.ndarray]]:
    """
    Yield frames from video.
    
    Yields:
        (frame_index, time_s, frame_array)
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate frame skip if target_fps specified
    frame_skip = 1
    if target_fps and target_fps < original_fps:
        frame_skip = int(original_fps / target_fps)
    
    frame_index = 0
    actual_frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames if needed
            if frame_index % frame_skip != 0:
                frame_index += 1
                continue
            
            time_s = frame_index / original_fps
            
            yield (actual_frame_count, time_s, frame)
            
            frame_index += 1
            actual_frame_count += 1
    
    finally:
        cap.release()


def save_debug_frame(
    frame: np.ndarray,
    output_path: Path,
    landmarks: Optional[List] = None
) -> None:
    """Save frame with optional landmarks drawn (for debugging)"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    debug_frame = frame.copy()
    
    if landmarks:
        # Draw landmarks on frame
        for lm in landmarks:
            if hasattr(lm, 'x') and hasattr(lm, 'y'):
                x = int(lm.x * frame.shape[1])
                y = int(lm.y * frame.shape[0])
                cv2.circle(debug_frame, (x, y), 3, (0, 255, 0), -1)
    
    cv2.imwrite(str(output_path), debug_frame)
