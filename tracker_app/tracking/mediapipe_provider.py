import mediapipe as mp
import numpy as np
import cv2  # Added cv2 import
from typing import List
from loguru import logger

from .base import TrackingProvider, TrackingResult, Landmark2D


class MediaPipeProvider(TrackingProvider):
    """MediaPipe-based tracking provider"""
    
    # Pose landmark names (MediaPipe Pose has 33 landmarks)
    POSE_LANDMARKS = [
        'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
        'right_eye_inner', 'right_eye', 'right_eye_outer',
        'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
        'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
        'left_index', 'right_index', 'left_thumb', 'right_thumb',
        'left_hip', 'right_hip', 'left_knee', 'right_knee',
        'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
        'left_foot_index', 'right_foot_index'
    ]
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe solutions
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        logger.info("MediaPipe provider initialized")
    
    def track_frame(
        self,
        frame: np.ndarray,
        frame_index: int,
        time_s: float
    ) -> TrackingResult:
        """Track single frame"""
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        
        result = TrackingResult(
            frame_index=frame_index,
            time_s=time_s,
            image_size=(width, height)
        )
        
        # Process pose
        pose_results = self.pose.process(frame_rgb)
        if pose_results.pose_landmarks:
            result.pose_landmarks = self._convert_pose_landmarks(
                pose_results.pose_landmarks
            )
            result.pose_confidence = self._calculate_avg_confidence(
                result.pose_landmarks
            )
        
        # Process hands
        hands_results = self.hands.process(frame_rgb)
        if hands_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                hands_results.multi_hand_landmarks,
                hands_results.multi_handedness
            ):
                # For hands, use presence as confidence (force 1.0)
                landmarks = self._convert_landmarks(hand_landmarks, use_visibility=False)
                confidence = self._calculate_avg_confidence(landmarks)
                
                # Determine left/right
                hand_type = handedness.classification[0].label  # "Left" or "Right"
                if hand_type == "Left":
                    result.left_hand_landmarks = landmarks
                    result.left_hand_confidence = confidence
                else:
                    result.right_hand_landmarks = landmarks
                    result.right_hand_confidence = confidence
        
        # Process face
        face_results = self.face_mesh.process(frame_rgb)
        if face_results.multi_face_landmarks:
            # Take first face only
            face_landmarks = face_results.multi_face_landmarks[0]
            # For face, use presence as confidence (force 1.0)
            result.face_landmarks = self._convert_landmarks(face_landmarks, use_visibility=False)
            result.face_confidence = self._calculate_avg_confidence(
                result.face_landmarks
            )
        
        return result
    
    def _convert_pose_landmarks(self, landmarks) -> List[Landmark2D]:
        """Convert MediaPipe pose landmarks to our format"""
        result = []
        for idx, lm in enumerate(landmarks.landmark):
            name = self.POSE_LANDMARKS[idx] if idx < len(self.POSE_LANDMARKS) else None
            result.append(Landmark2D(
                x=lm.x,
                y=lm.y,
                confidence=lm.visibility,  # Note: pose uses 'visibility'
                name=name
            ))
        return result
    
    def _convert_landmarks(self, landmarks, use_visibility: bool = True) -> List[Landmark2D]:
        """Convert MediaPipe landmarks to our format"""
        result = []
        for lm in landmarks.landmark:
            conf = getattr(lm, 'visibility', 1.0) if use_visibility else 1.0
            result.append(Landmark2D(
                x=lm.x,
                y=lm.y,
                confidence=conf
            ))
        return result
    
    def _calculate_avg_confidence(self, landmarks: List[Landmark2D]) -> float:
        """Calculate average confidence across landmarks"""
        if not landmarks:
            return 0.0
        return sum(lm.confidence for lm in landmarks) / len(landmarks)
    
    def close(self) -> None:
        """Release resources"""
        self.pose.close()
        self.hands.close()
        self.face_mesh.close()
        logger.info("MediaPipe provider closed")
