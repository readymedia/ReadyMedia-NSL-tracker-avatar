import cv2
import numpy as np
from pathlib import Path
from typing import List

from tracker_app.tracking.base import TrackingResult, Landmark2D


def draw_landmarks_on_frame(
    frame: np.ndarray,
    result: TrackingResult,
    draw_pose: bool = True,
    draw_hands: bool = True,
    draw_face: bool = False  # Too many points
) -> np.ndarray:
    """Draw tracking landmarks on frame"""
    output = frame.copy()
    height, width = frame.shape[:2]
    
    # Draw pose
    if draw_pose and result.pose_landmarks:
        for lm in result.pose_landmarks:
            x = int(lm.x * width)
            y = int(lm.y * height)
            color = (0, 255, 0) if lm.confidence > 0.7 else (0, 255, 255)
            cv2.circle(output, (x, y), 4, color, -1)
    
    # Draw hands
    if draw_hands:
        if result.left_hand_landmarks:
            _draw_hand(output, result.left_hand_landmarks, (255, 0, 0), width, height)
        if result.right_hand_landmarks:
            _draw_hand(output, result.right_hand_landmarks, (0, 0, 255), width, height)
    
    # Draw quality info
    info_text = f"Frame {result.frame_index} | Pose: {result.pose_confidence:.2f} | " \
                f"L: {result.left_hand_confidence:.2f} | R: {result.right_hand_confidence:.2f}"
    cv2.putText(output, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, (255, 255, 255), 2)
    
    return output


def _draw_hand(
    frame: np.ndarray,
    landmarks: List[Landmark2D],
    color: tuple,
    width: int,
    height: int
) -> None:
    """Draw hand landmarks and connections"""
    # Draw landmarks
    for lm in landmarks:
        x = int(lm.x * width)
        y = int(lm.y * height)
        cv2.circle(frame, (x, y), 3, color, -1)
    
    # Draw connections (simplified)
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),  # Index
        (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    ]
    
    for start_idx, end_idx in connections:
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            x1, y1 = int(start.x * width), int(start.y * height)
            x2, y2 = int(end.x * width), int(end.y * height)
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)


def create_visualization_video(
    input_video: Path,
    tracking_results: List[TrackingResult],
    output_video: Path
) -> None:
    """Create video with tracking overlay"""
    import cv2
    from tracker_app.preprocess.video_utils import extract_frames
    
    # Open input video
    cap = cv2.VideoCapture(str(input_video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Create output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_video), fourcc, fps, (width, height))
    
    # Process frames
    for (frame_idx, time_s, frame), result in zip(
        extract_frames(input_video),
        tracking_results
    ):
        annotated = draw_landmarks_on_frame(frame, result)
        out.write(annotated)
    
    out.release()
