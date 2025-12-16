from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import numpy as np


@dataclass
class Landmark2D:
    """2D landmark point"""
    x: float  # Normalized 0..1
    y: float  # Normalized 0..1
    confidence: float  # 0..1
    name: Optional[str] = None


@dataclass
class TrackingResult:
    """Complete tracking result for one frame"""
    frame_index: int
    time_s: float
    image_size: tuple[int, int]  # (width, height)
    
    # Body pose landmarks
    pose_landmarks: List[Landmark2D] = field(default_factory=list)
    
    # Hand landmarks (21 per hand)
    left_hand_landmarks: List[Landmark2D] = field(default_factory=list)
    right_hand_landmarks: List[Landmark2D] = field(default_factory=list)
    
    # Face landmarks
    face_landmarks: List[Landmark2D] = field(default_factory=list)
    
    # Confidence scores
    pose_confidence: float = 0.0
    left_hand_confidence: float = 0.0
    right_hand_confidence: float = 0.0
    face_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        return {
            'frame_index': self.frame_index,
            'time_s': self.time_s,
            'image_size': {'width': self.image_size[0], 'height': self.image_size[1]},
            'pose_landmarks': [
                {'x': lm.x, 'y': lm.y, 'c': lm.confidence, 'name': lm.name}
                for lm in self.pose_landmarks
            ],
            'left_hand_landmarks': [
                {'x': lm.x, 'y': lm.y, 'c': lm.confidence}
                for lm in self.left_hand_landmarks
            ],
            'right_hand_landmarks': [
                {'x': lm.x, 'y': lm.y, 'c': lm.confidence}
                for lm in self.right_hand_landmarks
            ],
            'face_landmarks': [
                {'x': lm.x, 'y': lm.y, 'c': lm.confidence}
                for lm in self.face_landmarks
            ],
            'confidence': {
                'pose': self.pose_confidence,
                'left_hand': self.left_hand_confidence,
                'right_hand': self.right_hand_confidence,
                'face': self.face_confidence
            }
        }


class TrackingProvider(ABC):
    """Abstract base class for tracking providers"""
    
    @abstractmethod
    def track_frame(
        self,
        frame: np.ndarray,
        frame_index: int,
        time_s: float
    ) -> TrackingResult:
        """Track single frame, return results"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Clean up resources"""
        pass
