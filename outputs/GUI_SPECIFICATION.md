# 🎨 ReaddyMedia NSL Avatar – GUI Specification

## 🎯 Overview

**Product Name**: ReaddyMedia - NSL Avatar  
**Purpose**: Professional research-grade interface for Norwegian Sign Language tracking  
**Technology**: Gradio + Custom CSS  
**Target Users**: Researchers, operators, sign language specialists

---

## 🎨 Design Philosophy

**Balance:**
- Professional & clean (not sterile)
- Research-grade (metrics, data) + User-friendly (visual, intuitive)
- Modern UI (colors, spacing) but functional-first

**Color Palette:**
```
Primary:   #2563EB (Blue 600) - Actions, headers
Secondary: #7C3AED (Purple 600) - Accents
Success:   #10B981 (Green 500) - Done, good quality
Warning:   #F59E0B (Amber 500) - Issues, low quality
Danger:    #EF4444 (Red 500) - Errors, failed
Neutral:   #6B7280 (Gray 500) - Text, borders
Background:#F9FAFB (Gray 50) - Main background
Surface:   #FFFFFF (White) - Cards, panels
```

---

## 📐 Layout Structure

### Main Window (Tabs):

1. **🎬 Process** – Process videos with live preview
2. **🔍 Browse** – Browse processed results
3. **📊 Dashboard** – Statistics and overview
4. **⚙️ Settings** – Configuration

---

## 🎬 TAB 1: Process (with Live Tracking Preview)

### Layout:

```
┌─────────────────────────────────────────────────────────────────────┐
│  🎥 ReaddyMedia - NSL Avatar                              [⚙️] [❓]  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  📁 SELECT VIDEOS           │  │  🎥 LIVE TRACKING PREVIEW    │ │
│  ├─────────────────────────────┤  ├──────────────────────────────┤ │
│  │                             │  │                              │ │
│  │ 📂 video-eksempler/         │  │  ┌────────────────────────┐ │ │
│  │                             │  │  │                        │ │ │
│  │ ☑ 5.mp4               192KB │  │  │    [Video Preview      │ │ │
│  │ ☑ andre.mp4           274KB │  │  │     with landmarks     │ │ │
│  │ ☐ bistandsadvokat.mp4 363KB │  │  │     drawn in real-time]│ │ │
│  │ ☑ moss.mp4            242KB │  │  │                        │ │ │
│  │ ☐ aalesund-2.mp4      318KB │  │  │                        │ │ │
│  │ ...                         │  │  └────────────────────────┘ │ │
│  │                             │  │                              │ │
│  │ ✓ Selected: 3 videos        │  │  Frame: 45/120 (37%)        │ │
│  │ Total: 708 KB               │  │  FPS: 24.8                  │ │
│  │                             │  │                              │ │
│  │ [Select All] [Clear]        │  │  📊 Current Tracking:       │ │
│  └─────────────────────────────┘  │  • Pose:  ✅ 0.94          │ │
│                                    │  • Hands: ✅ L:0.89 R:0.91  │ │
│  ┌─────────────────────────────┐  │  • Face:  ✅ 0.87          │ │
│  │  ⚙️ PROCESSING SETTINGS     │  │                              │ │
│  ├─────────────────────────────┤  │  ⚠️ Issues: None            │ │
│  │                             │  └──────────────────────────────┘ │
│  │ Min Confidence: 0.5 ━━━●━━  │                                   │
│  │ Target FPS:     [25  ]      │  ┌──────────────────────────────┐ │
│  │ □ Save JSONL (debug)        │  │  📝 PROCESSING LOG          │ │
│  │ ☑ Save Parquet (main)       │  ├──────────────────────────────┤ │
│  │ ☑ Generate Visualization    │  │                              │ │
│  │                             │  │ 12:34:56 [✓] 5.mp4          │ │
│  │ [▶️ START PROCESSING]       │  │          Quality: 0.87       │ │
│  │ [⏸️ Pause] [⏹️ Stop]         │  │                              │ │
│  └─────────────────────────────┘  │ 12:35:12 [✓] andre.mp4      │ │
│                                    │          Quality: 0.92       │ │
│  ┌─────────────────────────────┐  │          Hands: 95%          │ │
│  │  📊 BATCH PROGRESS          │  │          Face: 98%           │ │
│  ├─────────────────────────────┤  │                              │ │
│  │                             │  │ 12:35:45 [→] moss.mp4       │ │
│  │ ████████████░░░░░ 2/3 (67%) │  │          Processing...       │ │
│  │                             │  │                              │ │
│  │ Current: moss.mp4           │  │                              │ │
│  │ Estimated: 1m 24s           │  │ [Auto-scroll ▼]             │ │
│  │                             │  └──────────────────────────────┘ │
│  └─────────────────────────────┘                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Live Tracking Visualization:

**What's shown on video:**
- 🟢 Green dots: High confidence landmarks (>0.7)
- 🟡 Yellow dots: Medium confidence (0.5-0.7)
- 🔴 Red dots: Low confidence (<0.5)
- Lines connecting: Hand bones, pose skeleton
- Bounding boxes: Person detection
- Labels: "Left Hand", "Right Hand", "Face"

**Real-time metrics below video:**
- Current frame / Total frames
- FPS
- Confidence scores per modality
- Detected issues

---

## 🔍 TAB 2: Browse Results

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔍 BROWSE PROCESSED VIDEOS                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 🔎 [Search words...]            Min Quality: 0.5 ━━━●━━━━━━    │ │
│  │ [Filter: All ▼] [Sort: Quality ▼]              [🔄 Refresh]    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌─────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  📊 RESULTS (8/14)          │  │  📹 PREVIEW: andre.mp4       │ │
│  ├─────────────────────────────┤  ├──────────────────────────────┤ │
│  │                             │  │                              │ │
│  │ Word        Quality  Frames │  │  [Annotated video player]    │ │
│  │ ──────────  ───────  ────── │  │                              │ │
│  │ andre       ⭐ 0.92   120   │  │  [Timeline scrubber with     │ │
│  │ moss        ⭐ 0.87    95   │  │   quality heatmap]           │ │
│  │ 5           ✓ 0.84    54   │  │                              │ │
│  │ aalesund-2  ✓ 0.78   108   │  │  🎚️ ──●────────────         │ │
│  │ yoghurt-2   ✓ 0.76    62   │  │                              │ │
│  │ ANB         ✓ 0.72    88   │  │  0:00 / 0:04                │ │
│  │ bistands... ⚠ 0.65   180   │  └──────────────────────────────┘ │
│  │ argument-2  ⚠ 0.58   142   │                                   │
│  │                             │  ┌──────────────────────────────┐ │
│  │ [< Prev] [Next >]           │  │  📊 QUALITY ANALYSIS         │ │
│  └─────────────────────────────┘  ├──────────────────────────────┤ │
│                                    │                              │ │
│                                    │ Overall Score:    0.92 / 1.0 │ │
│                                    │                              │ │
│                                    │ Hand Visibility:  ███████ 95%│ │
│                                    │ Face Coverage:    █████████ 98%│ │
│                                    │ Track Stability:  ████████ 91%│ │
│                                    │ Avg Confidence:   ████████ 88%│ │
│                                    │                              │ │
│                                    │ ⚠️ Issues Detected: None    │ │
│                                    │                              │ │
│                                    │ 📈 Frame-by-frame:          │ │
│                                    │ [Quality graph over time]    │ │
│                                    │                              │ │
│                                    │ [📥 Download Tracking]      │ │
│                                    │ [🎥 Download Viz]           │ │
│                                    │ [📊 Generate Report]        │ │
│                                    └──────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 TAB 3: Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 DASHBOARD & ANALYTICS                              [🔄 Refresh] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐        │
│  │   TOTAL     │    DONE     │   FAILED    │   PENDING   │        │
│  │             │             │             │             │        │
│  │     14      │      8      │      1      │      5      │        │
│  │  ━━━━━━━    │  ━━━━━━━    │  ━━━━━━━    │  ━━━━━━━    │        │
│  │   videos    │   (57%)     │   (7%)      │   (36%)     │        │
│  └─────────────┴─────────────┴─────────────┴─────────────┘        │
│                                                                     │
│  ┌────────────────────────────────┐ ┌──────────────────────────┐  │
│  │  📈 QUALITY DISTRIBUTION       │ │  ⏱️ PROCESSING TIME      │  │
│  ├────────────────────────────────┤ ├──────────────────────────┤  │
│  │                                │ │                          │  │
│  │  [Histogram with quality       │ │  [Bar chart showing      │  │
│  │   scores on X-axis,            │ │   time per video]        │  │
│  │   count on Y-axis]             │ │                          │  │
│  │                                │ │  Avg: 45s per video      │  │
│  │  Mean: 0.77                    │ │  Total: 6m 15s           │  │
│  │  Median: 0.80                  │ │                          │  │
│  │  Std Dev: 0.12                 │ │                          │  │
│  │                                │ │                          │  │
│  └────────────────────────────────┘ └──────────────────────────┘  │
│                                                                     │
│  ┌────────────────────────────────┐ ┌──────────────────────────┐  │
│  │  ⚠️ COMMON ISSUES              │ │  💾 STORAGE              │  │
│  ├────────────────────────────────┤ ├──────────────────────────┤  │
│  │                                │ │                          │  │
│  │  • Low hand visibility: 3      │ │  Tracking Data:  2.3 GB  │  │
│  │  • High jitter: 2              │ │  Visualizations: 1.1 GB  │  │
│  │  • Face not detected: 1        │ │  Database:       8.4 MB  │  │
│  │  • Hands overlap: 2            │ │  ────────────────────    │  │
│  │                                │ │  Total: 3.4 GB / 50 GB   │  │
│  │  [View Details]                │ │  ███░░░░░░░░░░░░░ (7%)  │  │
│  │                                │ │                          │  │
│  └────────────────────────────────┘ └──────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  📋 RECENT ACTIVITY                                          │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  12:35:45  ✅  moss.mp4 processed (Quality: 0.87)           │  │
│  │  12:35:12  ✅  andre.mp4 processed (Quality: 0.92)          │  │
│  │  12:34:56  ✅  5.mp4 processed (Quality: 0.84)              │  │
│  │  12:34:12  ⚠️  bistandsadvokat.mp4 - Low hand visibility    │  │
│  │  12:33:45  ❌  argument-2.mp4 failed - MediaPipe error      │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [📄 Export Full Report (PDF)] [📊 Export Data (CSV)]             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ TAB 4: Settings

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚙️ SETTINGS & CONFIGURATION                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  📁 PATHS                                                      │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  Workspace Directory:                                          │ │
│  │  [D:\tegnspråk\workspace                        ] [📁 Browse] │ │
│  │                                                                │ │
│  │  Video Source Folder:                                          │ │
│  │  [D:\tegnspråk\video-eksempler                  ] [📁 Browse] │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  🎥 VIDEO PROCESSING                                           │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  Target FPS:              [25     ] (0 = use original)        │ │
│  │  Target Resolution:       [720p ▼] (480p/720p/1080p/Original)│ │
│  │  □ Enable Normalization   (resize/color correction)           │ │
│  │  □ Auto-trim Dead Frames  (remove start/end padding)          │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  🤖 TRACKING CONFIGURATION                                     │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  Provider:                [MediaPipe ▼]                        │ │
│  │                           (MediaPipe / RTMPose / Ensemble)     │ │
│  │                                                                │ │
│  │  Min Detection Confidence: 0.5 ━━━━━●━━━━━━━━                 │ │
│  │  Min Tracking Confidence:  0.5 ━━━━━●━━━━━━━━                 │ │
│  │                                                                │ │
│  │  🎚️ Smoothing Settings:                                       │ │
│  │  EMA Alpha (Wrist):       0.35 ━━━●━━━━━━━━━━                 │ │
│  │  EMA Alpha (Fingers):     0.55 ━━━━━●━━━━━━━━                 │ │
│  │  EMA Alpha (Face):        0.40 ━━━●━━━━━━━━━━                 │ │
│  │  Velocity Clamp (deg/frame): [18.0]                           │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  💾 OUTPUT & STORAGE                                           │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  ☑ Save Parquet Files      (primary format, efficient)        │ │
│  │  ☑ Save JSONL Files         (debug format, human-readable)    │ │
│  │  ☑ Generate Visualizations  (annotated videos)                │ │
│  │  □ Keep Cache Files         (normalized videos, frames)       │ │
│  │                                                                │ │
│  │  Quality Threshold:        0.5 ━━━━━●━━━━━━━━                 │ │
│  │  (flag videos below this score)                                │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  📝 LOGGING & DIAGNOSTICS                                      │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │  Log Level:               [INFO ▼] (DEBUG/INFO/WARNING/ERROR) │ │
│  │  □ Save Frame Snapshots    (for debugging tracking issues)    │ │
│  │  □ Verbose MediaPipe Output                                    │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  [💾 Save Settings] [🔄 Reset to Defaults] [📋 Export Config]      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation Code

### `scripts/gui.py`:

```python
"""
ReaddyMedia - NSL Avatar
Professional GUI for Norwegian Sign Language tracking
"""

import gradio as gr
from pathlib import Path
import cv2
import numpy as np
from typing import List, Tuple, Optional
import threading
import queue

from tracker_app.config import get_config
from tracker_app.store.db import Database
from tracker_app.tracking.mediapipe_provider import MediaPipeProvider
from tracker_app.preprocess.video_utils import extract_frames, get_video_metadata
from tracker_app.visualization.draw_landmarks import draw_landmarks_on_frame

config = get_config()
db = Database(config.db_path)

# Global state for live preview
preview_queue = queue.Queue(maxsize=5)
processing_active = False


# ============================================================================
# LIVE TRACKING PREVIEW
# ============================================================================

def draw_tracking_overlay(frame: np.ndarray, result) -> np.ndarray:
    """
    Draw tracking landmarks on frame with color-coded confidence.
    
    Green: >0.7 (high confidence)
    Yellow: 0.5-0.7 (medium)
    Red: <0.5 (low)
    """
    annotated = frame.copy()
    height, width = frame.shape[:2]
    
    # Draw pose
    for lm in result.pose_landmarks:
        color = (
            (0, 255, 0) if lm.confidence > 0.7 else
            (0, 255, 255) if lm.confidence > 0.5 else
            (0, 0, 255)
        )
        x, y = int(lm.x * width), int(lm.y * height)
        cv2.circle(annotated, (x, y), 5, color, -1)
    
    # Draw hands with connections
    if result.left_hand_landmarks:
        draw_hand_landmarks(annotated, result.left_hand_landmarks, 
                          (255, 0, 0), "Left Hand", width, height)
    
    if result.right_hand_landmarks:
        draw_hand_landmarks(annotated, result.right_hand_landmarks, 
                          (0, 0, 255), "Right Hand", width, height)
    
    # Draw face mesh (simplified - just outline)
    if result.face_landmarks and len(result.face_landmarks) > 10:
        draw_face_outline(annotated, result.face_landmarks, width, height)
    
    # Add info overlay
    add_info_overlay(annotated, result)
    
    return annotated


def draw_hand_landmarks(frame, landmarks, color, label, width, height):
    """Draw hand landmarks with connections"""
    # Hand connections (simplified)
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),  # Index
        (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    ]
    
    # Draw connections
    for start_idx, end_idx in connections:
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            x1, y1 = int(start.x * width), int(start.y * height)
            x2, y2 = int(end.x * width), int(end.y * height)
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)
    
    # Draw landmarks
    for lm in landmarks:
        x, y = int(lm.x * width), int(lm.y * height)
        cv2.circle(frame, (x, y), 4, color, -1)
    
    # Add label
    if landmarks:
        wrist = landmarks[0]
        x, y = int(wrist.x * width), int(wrist.y * height)
        cv2.putText(frame, label, (x-20, y-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def draw_face_outline(frame, landmarks, width, height):
    """Draw simplified face outline"""
    # Just draw a few key landmarks for face outline
    face_indices = [10, 234, 454, 162, 389]  # Face contour points
    
    for i in face_indices:
        if i < len(landmarks):
            lm = landmarks[i]
            x, y = int(lm.x * width), int(lm.y * height)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)


def add_info_overlay(frame, result):
    """Add info text overlay on frame"""
    height, width = frame.shape[:2]
    
    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, height-100), (300, height-10), 
                 (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Text
    y_offset = height - 80
    cv2.putText(frame, f"Pose:  {result.pose_confidence:.2f}", 
               (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    y_offset += 20
    cv2.putText(frame, f"Hands: L:{result.left_hand_confidence:.2f} R:{result.right_hand_confidence:.2f}", 
               (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    y_offset += 20
    cv2.putText(frame, f"Face:  {result.face_confidence:.2f}", 
               (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


# ============================================================================
# TAB 1: PROCESS VIDEOS
# ============================================================================

def process_videos_with_preview(
    selected_videos: List[str],
    min_conf: float,
    target_fps: int,
    save_jsonl: bool,
    save_parquet: bool,
    generate_viz: bool,
    progress=gr.Progress()
):
    """Process videos with live preview"""
    global processing_active
    processing_active = True
    
    provider = MediaPipeProvider(
        min_detection_confidence=min_conf,
        min_tracking_confidence=min_conf
    )
    
    results_log = []
    
    for i, video_path_str in enumerate(selected_videos):
        video_path = Path(video_path_str)
        
        progress((i, len(selected_videos)), desc=f"Processing {video_path.name}")
        
        results_log.append(f"[→] Processing {video_path.name}...")
        yield (
            "\n".join(results_log[-10:]),  # Log
            None,  # Preview frame (will be updated by thread)
            f"Processing {video_path.name}",  # Status
            f"Frame 0/?"  # Frame info
        )
        
        try:
            # Process video
            tracking_results = []
            
            for frame_idx, time_s, frame in extract_frames(video_path, target_fps):
                if not processing_active:
                    break
                
                # Track
                result = provider.track_frame(frame, frame_idx, time_s)
                tracking_results.append(result)
                
                # Update preview every 5 frames
                if frame_idx % 5 == 0:
                    annotated = draw_tracking_overlay(frame, result)
                    
                    yield (
                        "\n".join(results_log[-10:]),
                        annotated,
                        f"Processing {video_path.name}",
                        f"Frame {frame_idx}"
                    )
            
            # Compute quality (simplified)
            avg_quality = np.mean([
                r.pose_confidence * 0.3 + 
                r.left_hand_confidence * 0.25 +
                r.right_hand_confidence * 0.25 +
                r.face_confidence * 0.2
                for r in tracking_results
            ])
            
            # Save results (simplified)
            # ... actual saving logic here ...
            
            results_log.append(f"[✓] {video_path.name} - Quality: {avg_quality:.2f}")
            
        except Exception as e:
            results_log.append(f"[✗] {video_path.name} - Error: {str(e)}")
    
    provider.close()
    processing_active = False
    
    yield (
        "\n".join(results_log[-10:]),
        None,
        "✅ All done!",
        ""
    )


def get_video_list():
    """Get list of videos in video folder"""
    video_folder = Path("video-eksempler")
    if not video_folder.exists():
        return []
    
    videos = list(video_folder.glob("*.mp4"))
    # Return formatted: "filename (size)"
    return [
        f"{v.name} ({v.stat().st_size // 1024} KB)"
        for v in sorted(videos)
    ]


# ============================================================================
# TAB 2: BROWSE RESULTS
# ============================================================================

def browse_results(search_query: str, min_quality: float):
    """Browse processed videos"""
    jobs = db.get_jobs(status='done', min_quality=min_quality)
    
    if search_query:
        jobs = [j for j in jobs if search_query.lower() in j['word'].lower()]
    
    # Format for display
    table_data = []
    for j in jobs:
        quality_icon = (
            "⭐" if j['quality_score'] > 0.8 else
            "✓" if j['quality_score'] > 0.7 else
            "⚠"
        )
        table_data.append([
            j['word'],
            f"{quality_icon} {j['quality_score']:.2f}",
            j['frames']
        ])
    
    return table_data


def show_video_preview(selected_row):
    """Show video preview when row selected"""
    if not selected_row:
        return None, "Select a video to preview"
    
    # Load video and tracking data
    # ... implementation ...
    
    return video_path, quality_info


# ============================================================================
# TAB 3: DASHBOARD
# ============================================================================

def generate_dashboard():
    """Generate dashboard statistics"""
    stats = db.get_stats()
    
    # Create quality histogram
    import plotly.graph_objects as go
    
    jobs = db.get_jobs(status='done')
    quality_scores = [j['quality_score'] for j in jobs]
    
    fig = go.Figure(data=[
        go.Histogram(
            x=quality_scores,
            nbinsx=10,
            marker_color='rgb(37, 99, 235)'
        )
    ])
    fig.update_layout(
        title="Quality Score Distribution",
        xaxis_title="Quality Score",
        yaxis_title="Count",
        template="plotly_white"
    )
    
    return stats, fig


# ============================================================================
# MAIN UI
# ============================================================================

def create_ui():
    """Create main Gradio UI"""
    
    # Custom CSS
    custom_css = """
    .gradio-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .header {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .stat-box {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    """
    
    with gr.Blocks(css=custom_css, title="ReaddyMedia - NSL Avatar") as demo:
        
        # Header
        gr.HTML("""
        <div class="header">
            <h1>🎥 ReaddyMedia - NSL Avatar</h1>
            <p>Professional Norwegian Sign Language Tracking System</p>
        </div>
        """)
        
        with gr.Tabs():
            
            # TAB 1: Process
            with gr.Tab("🎬 Process Videos"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📁 Select Videos")
                        video_checklist = gr.CheckboxGroup(
                            choices=get_video_list(),
                            label="Videos",
                            info="Check videos to process"
                        )
                        
                        gr.Markdown("### ⚙️ Settings")
                        min_conf = gr.Slider(0, 1, value=0.5, 
                                           label="Min Confidence")
                        target_fps = gr.Number(value=25, label="Target FPS")
                        save_jsonl = gr.Checkbox(value=True, label="Save JSONL")
                        save_parquet = gr.Checkbox(value=True, label="Save Parquet")
                        generate_viz = gr.Checkbox(value=True, 
                                                   label="Generate Visualization")
                        
                        process_btn = gr.Button("▶️ START PROCESSING", 
                                               variant="primary", size="lg")
                        
                        gr.Markdown("### 📊 Progress")
                        batch_progress = gr.Textbox(label="Status", 
                                                    value="Ready to start")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 🎥 Live Tracking Preview")
                        video_preview = gr.Image(label="", type="numpy")
                        
                        with gr.Row():
                            frame_info = gr.Textbox(label="Frame", scale=1)
                            tracking_info = gr.Textbox(label="Tracking", scale=2)
                        
                        gr.Markdown("### 📝 Processing Log")
                        log_output = gr.Textbox(label="", lines=10)
                
                # Connect processing
                process_btn.click(
                    process_videos_with_preview,
                    inputs=[video_checklist, min_conf, target_fps, 
                           save_jsonl, save_parquet, generate_viz],
                    outputs=[log_output, video_preview, batch_progress, frame_info]
                )
            
            # TAB 2: Browse
            with gr.Tab("🔍 Browse Results"):
                with gr.Row():
                    search_box = gr.Textbox(label="Search", placeholder="Enter word...")
                    min_quality_slider = gr.Slider(0, 1, value=0.5, label="Min Quality")
                    refresh_btn = gr.Button("🔄 Refresh")
                
                with gr.Row():
                    with gr.Column():
                        results_table = gr.Dataframe(
                            headers=["Word", "Quality", "Frames"],
                            label="Results"
                        )
                    
                    with gr.Column():
                        video_player = gr.Video(label="Preview")
                        quality_details = gr.Markdown("Select a video to see details")
                
                refresh_btn.click(
                    browse_results,
                    inputs=[search_box, min_quality_slider],
                    outputs=results_table
                )
            
            # TAB 3: Dashboard
            with gr.Tab("📊 Dashboard"):
                refresh_dash = gr.Button("🔄 Refresh Dashboard")
                
                with gr.Row():
                    stats_display = gr.JSON(label="Statistics")
                    quality_plot = gr.Plot(label="Quality Distribution")
                
                refresh_dash.click(
                    generate_dashboard,
                    outputs=[stats_display, quality_plot]
                )
            
            # TAB 4: Settings
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("### 📁 Paths")
                workspace_input = gr.Textbox(
                    value=str(config.workspace_dir),
                    label="Workspace Directory"
                )
                
                gr.Markdown("### 🎥 Video Processing")
                target_fps_setting = gr.Number(value=25, label="Target FPS")
                
                gr.Markdown("### 🤖 Tracking")
                provider_dropdown = gr.Dropdown(
                    choices=["MediaPipe", "RTMPose (Phase 2)"],
                    value="MediaPipe",
                    label="Tracking Provider"
                )
                
                save_btn = gr.Button("💾 Save Settings", variant="primary")
        
        return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
```

---

## 🚀 Usage

### Start GUI:
```bash
python scripts/gui.py
```

**Opens at**: `http://localhost:7860`

---

## 📊 GUI Features Summary

✅ **Live tracking preview** with color-coded confidence  
✅ **Batch processing** with progress tracking  
✅ **Video browsing** with quality filtering  
✅ **Dashboard** with statistics and charts  
✅ **Configurable settings** for all parameters  
✅ **Professional design** (not sterile research UI)  
✅ **Real-time metrics** during processing  
✅ **Quality heatmap** on video timeline  
✅ **Export capabilities** (reports, data, visualizations)

---

## 🎨 Design Notes

**Colors match ReaddyMedia brand:**
- Primary blue (#2563EB) for actions
- Purple accent (#7C3AED) for highlights
- Clean, modern spacing
- Intuitive layout
- Research-grade but user-friendly

---

## 📝 Next Steps

1. Add to roadmap as **Phase 1.5: GUI**
2. Implement after Phase 1 core is working
3. Test with real videos
4. Polish based on user feedback
