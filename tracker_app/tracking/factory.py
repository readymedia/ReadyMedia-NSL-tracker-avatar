from typing import Any
from tracker_app.tracking.mediapipe_provider import MediaPipeProvider
import logging

logger = logging.getLogger(__name__)

def get_tracking_provider(name: str, min_confidence: float = 0.5):
    """
    Factory to create tracking provider instance.
    
    Args:
        name: 'mediapipe' or 'rtmpose'
        min_confidence: content threshold
    """
    name = name.lower()
    
    if "mediapipe" in name:
        return MediaPipeProvider(
            min_detection_confidence=min_confidence,
            min_tracking_confidence=min_confidence
        )
    elif "rtmpose" in name or "mmpose" in name:
        try:
            from tracker_app.tracking.rtmpose_provider import RTMPoseProvider
            return RTMPoseProvider(min_confidence=min_confidence)
        except Exception as e:
            logger.error(f"Failed to load RTMPose: {e}")
            raise ImportError(f"RTMPose not installed or failed to load: {e}")
    else:
        raise ValueError(f"Unknown tracking provider: {name}")
