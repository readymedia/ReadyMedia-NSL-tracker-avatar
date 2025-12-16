import cv2
import numpy as np
import torch
from typing import Optional, List, Any
try:
    from mmpose.apis import MMPoseInferencer
except ImportError:
    MMPoseInferencer = None

from tracker_app.tracking.base import TrackingProvider, TrackingResult, Landmark2D

class RTMPoseProvider(TrackingProvider):
    def __init__(
        self,
        pose_model: str = 'rtmpose-l_8xb32-270e_coco-wholebody-384x288',
        det_model: str = 'rtmdet-m',
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        min_confidence: float = 0.3
    ):
        if MMPoseInferencer is None:
            raise ImportError("MMPose not installed. Run 'python scripts/setup_phase2.py'")
            
        print(f"Initializing RTMPose on {device}...")
        self.device = device
        self.min_confidence = min_confidence
        
        # Initialize Inferencer
        self.inferencer = MMPoseInferencer(
            pose2d=pose_model,
            det_model=det_model,
            device=device,
            show_progress=False
        )
        print("RTMPose initialized.")

    def track_frame(self, frame: np.ndarray, frame_idx: int, timestamp: float) -> TrackingResult:
        height, width = frame.shape[:2]
        
        # MMPose expects RGB usually, or BGR? 
        # MMPose APIs mostly accept image path or numpy array (BGR usually for cv2)
        # We'll rely on it accepting the frame as is (BGR from cv2).
        
        # Run inference
        # inferencer returns a generator
        result_generator = self.inferencer(frame, return_vis=False)
        result = next(result_generator)
        
        # Initialize empty result
        tracking_result = TrackingResult(
            frame_index=frame_idx,
            time_s=timestamp,
            image_size=(width, height)
        )
        
        # Parse predictions
        # structure: {'predictions': [{'keypoints': [[x,y], ...], 'keypoint_scores': [...], 'bbox': ...}], ...}
        predictions = result.get('predictions', [])
        
        # DEBUG
        # print(f"DEBUG RTMPose result keys: {result.keys()}")
        # if predictions:
        #    print(f"DEBUG First pred type: {type(predictions[0])}")
        
        if not predictions:
            return tracking_result
            
        # Take the first person (or max confidence person)
        per = predictions[0]
        # In some versions, 'predictions' is a list of dicts. In others it might be valid.
        
        # Check if it's new structure where predictions contain 'instances' or similar?
        # Actually in recent mmpose, inferencer returns dict with 'predictions'.
        # Let's handle list of points directly if that's what it is?
        
        # If per is NOT a dict, that's the issue.
        if not isinstance(per, dict):
            # Maybe it provides objects?
            # print(f"Unexpected prediction format: {type(per)} - {per}")
            return tracking_result
            
        keypoints = per.get('keypoints')
        if not keypoints:
            return tracking_result
            
        scores = per.get('keypoint_scores')
        
        # COCO-WholeBody Mapping
        # 0-16: Body
        # 17-22: Foot
        # 23-90: Face (68)
        # 91-111: Left Hand (21)
        # 112-132: Right Hand (21)
        
        # Helper to extract points
        def extract_points(start, end, name_prefix=None) -> tuple[List[Landmark2D], float]:
            points = []
            total_score = 0.0
            count = 0
            
            for i in range(start, end):
                if i >= len(keypoints):
                    break
                
                x, y = keypoints[i]
                score = scores[i]
                
                # Normalize
                norm_x = x / width
                norm_y = y / height
                
                points.append(Landmark2D(
                    x=float(norm_x),
                    y=float(norm_y),
                    confidence=float(score)
                ))
                
                total_score += score
                count += 1
            
            avg_conf = total_score / count if count > 0 else 0.0
            return points, avg_conf

        # Extract
        # Body (0-17)
        tracking_result.pose_landmarks, tracking_result.pose_confidence = extract_points(0, 17)
        
        # Face (23-91)
        tracking_result.face_landmarks, tracking_result.face_confidence = extract_points(23, 91)
        
        # Left Hand (91-112)
        tracking_result.left_hand_landmarks, tracking_result.left_hand_confidence = extract_points(91, 112)
        
        # Right Hand (112-133)
        tracking_result.right_hand_landmarks, tracking_result.right_hand_confidence = extract_points(112, 133)
        
        # Filter by overall confidence if needed?
        # For now, we keep all and let post-processing handle it/filter by confidence
        
        return tracking_result

    def close(self):
        # Clean up
        if hasattr(self, 'inferencer'):
            del self.inferencer
        if self.device == 'cuda':
            torch.cuda.empty_cache()
