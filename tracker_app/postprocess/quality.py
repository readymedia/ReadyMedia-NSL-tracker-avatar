from typing import List, Tuple, Dict
import numpy as np

from tracker_app.tracking.base import TrackingResult


def compute_quality_score(
    results: List[TrackingResult]
) -> Tuple[float, List[Dict]]:
    """
    Compute quality score 0..1 and list of issues.
    
    Returns:
        (score, issues)
    """
    if not results:
        return 0.0, [{"type": "empty", "severity": "error"}]
    
    issues = []
    
    # 1. Hand visibility (40% weight)
    hand_visibility = _compute_hand_visibility(results)
    if hand_visibility < 0.7:
        issues.append({
            "type": "low_hand_visibility",
            "severity": "warning",
            "value": hand_visibility
        })
    
    # 2. Tracking stability (30% weight)
    stability = _compute_stability(results)
    if stability < 0.7:
        issues.append({
            "type": "unstable_tracking",
            "severity": "warning",
            "value": stability
        })
    
    # 3. Face coverage (20% weight)
    face_coverage = _compute_face_coverage(results)
    if face_coverage < 0.5:
        issues.append({
            "type": "low_face_coverage",
            "severity": "info",
            "value": face_coverage
        })
    
    # 4. Average confidence (10% weight)
    avg_confidence = _compute_average_confidence(results)
    
    # Weighted score
    score = (
        0.4 * hand_visibility +
        0.3 * stability +
        0.2 * face_coverage +
        0.1 * avg_confidence
    )
    
    return score, issues


def _compute_hand_visibility(results: List[TrackingResult]) -> float:
    """Average ratio of frames where hands are detected (avg of left and right)"""
    left_count = sum(1 for r in results if r.left_hand_landmarks)
    right_count = sum(1 for r in results if r.right_hand_landmarks)
    return (left_count + right_count) / (2 * len(results))


def _compute_stability(results: List[TrackingResult]) -> float:
    """Measure tracking stability (inverse of jitter)"""
    if len(results) < 2:
        return 1.0
    
    # Compute frame-to-frame movement for wrists
    movements = []
    
    for i in range(1, len(results)):
        prev = results[i-1]
        curr = results[i]
        
        # Left wrist movement
        if prev.left_hand_landmarks and curr.left_hand_landmarks:
            prev_wrist = prev.left_hand_landmarks[0]
            curr_wrist = curr.left_hand_landmarks[0]
            dx = curr_wrist.x - prev_wrist.x
            dy = curr_wrist.y - prev_wrist.y
            movements.append(np.sqrt(dx*dx + dy*dy))
            
        # Right wrist movement
        if prev.right_hand_landmarks and curr.right_hand_landmarks:
            prev_wrist = prev.right_hand_landmarks[0]
            curr_wrist = curr.right_hand_landmarks[0]
            dx = curr_wrist.x - prev_wrist.x
            dy = curr_wrist.y - prev_wrist.y
            movements.append(np.sqrt(dx*dx + dy*dy))
    
    if not movements:
        return 0.0
    
    # Stability = inverse of std deviation of movements
    std = np.std(movements)
    stability = 1.0 / (1.0 + std * 10)  # Scale factor
    
    return stability


def _compute_face_coverage(results: List[TrackingResult]) -> float:
    """Ratio of frames with face detected"""
    with_face = sum(1 for r in results if r.face_landmarks)
    return with_face / len(results)


def _compute_average_confidence(results: List[TrackingResult]) -> float:
    """Average of all confidence scores"""
    confidences = []
    for r in results:
        confidences.extend([
            r.pose_confidence,
            r.left_hand_confidence,
            r.right_hand_confidence,
            r.face_confidence
        ])
    
    valid = [c for c in confidences if c > 0]
    return np.mean(valid) if valid else 0.0
