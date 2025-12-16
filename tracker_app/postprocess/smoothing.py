from typing import List, Optional
from dataclasses import dataclass
import numpy as np

from tracker_app.tracking.base import TrackingResult, Landmark2D


class EMAFilter:
    """Exponential Moving Average filter"""
    
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.last_value: Optional[float] = None
    
    def update(self, value: float, confidence: float = 1.0) -> float:
        """
        Update filter with new value.
        
        Args:
            value: New measurement
            confidence: Confidence in measurement (0..1)
        
        Returns:
            Smoothed value
        """
        if self.last_value is None:
            self.last_value = value
            return value
        
        # Confidence-weighted update
        effective_alpha = self.alpha * confidence
        smoothed = effective_alpha * value + (1 - effective_alpha) * self.last_value
        
        self.last_value = smoothed
        return smoothed
    
    def reset(self):
        """Reset filter state"""
        self.last_value = None


class VelocityClamp:
    """Clamp maximum velocity between frames"""
    
    def __init__(self, max_change_per_frame: float):
        self.max_change = max_change_per_frame
        self.last_value: Optional[float] = None
    
    def update(self, value: float) -> float:
        """Clamp velocity and update"""
        if self.last_value is None:
            self.last_value = value
            return value
        
        delta = value - self.last_value
        
        # Clamp delta
        if abs(delta) > self.max_change:
            delta = np.sign(delta) * self.max_change
        
        clamped = self.last_value + delta
        self.last_value = clamped
        return clamped
    
    def reset(self):
        """Reset filter state"""
        self.last_value = None


def smooth_tracking_sequence(
    results: List[TrackingResult],
    ema_alpha: float = 0.5,
    velocity_clamp: Optional[float] = None,
    min_confidence: float = 0.6
) -> List[TrackingResult]:
    """
    Apply smoothing to tracking sequence.
    
    Args:
        results: List of tracking results
        ema_alpha: EMA smoothing factor
        velocity_clamp: Max change per frame (optional)
        min_confidence: Minimum confidence to update filter
    
    Returns:
        Smoothed tracking results
    """
    if not results:
        return results
    
    # Create filters for each landmark dimension
    # This is simplified - in practice, you'd want per-landmark filters
    filters = {}
    
    smoothed_results = []
    
    for result in results:
        smoothed_result = TrackingResult(
            frame_index=result.frame_index,
            time_s=result.time_s,
            image_size=result.image_size,
            pose_confidence=result.pose_confidence,
            left_hand_confidence=result.left_hand_confidence,
            right_hand_confidence=result.right_hand_confidence,
            face_confidence=result.face_confidence
        )
        
        # Smooth pose landmarks
        smoothed_result.pose_landmarks = _smooth_landmarks(
            result.pose_landmarks,
            'pose',
            filters,
            ema_alpha,
            min_confidence
        )
        
        # Smooth hands
        smoothed_result.left_hand_landmarks = _smooth_landmarks(
            result.left_hand_landmarks,
            'left_hand',
            filters,
            ema_alpha,
            min_confidence
        )
        smoothed_result.right_hand_landmarks = _smooth_landmarks(
            result.right_hand_landmarks,
            'right_hand',
            filters,
            ema_alpha,
            min_confidence
        )
        
        # Face landmarks (subset only - 468 is too many)
        # In practice, extract key features instead
        
        smoothed_results.append(smoothed_result)
    
    return smoothed_results


def _smooth_landmarks(
    landmarks: List[Landmark2D],
    prefix: str,
    filters: dict,
    alpha: float,
    min_confidence: float
) -> List[Landmark2D]:
    """Smooth list of landmarks"""
    smoothed = []
    
    for idx, lm in enumerate(landmarks):
        # Create filters if not exist
        key_x = f"{prefix}_{idx}_x"
        key_y = f"{prefix}_{idx}_y"
        
        if key_x not in filters:
            filters[key_x] = EMAFilter(alpha)
            filters[key_y] = EMAFilter(alpha)
        
        # Apply smoothing if confidence is sufficient
        if lm.confidence >= min_confidence:
            x = filters[key_x].update(lm.x, lm.confidence)
            y = filters[key_y].update(lm.y, lm.confidence)
        else:
            # Low confidence - hold previous value
            x = filters[key_x].last_value if filters[key_x].last_value is not None else lm.x
            y = filters[key_y].last_value if filters[key_y].last_value is not None else lm.y
        
        smoothed.append(Landmark2D(
            x=x,
            y=y,
            confidence=lm.confidence,
            name=lm.name
        ))
    
    return smoothed
