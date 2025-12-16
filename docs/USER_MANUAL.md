# 📘 NSL Avatar - User & Analysis Guide

**Version**: 0.2.0 (Phase 2 - Dual Provider)
**Last Updated**: 2025-12-16

This guide explains how to use the ReaddyMedia NSL Avatar Tracking System, interpret the data visuals, and understand the underlying AI models.

---

## 🖥️ 1. Interface Guide (The GUI)

The Graphical User Interface (GUI) is divided into 4 main tabs. Here is how to master each one:

### 📥 Tab 1: Process Videos (The Workhorse)
This is where you input raw videos and convert them into tracking data.

*   **Select Videos Panel** (Left):
    *   Lists all MP4 files found in the `video-eksempler/` folder.
    *   **Pro Tip**: You can select multiple videos at once for batch processing.
    *   **Yellow Folder Icon**: Click to collapse/expand if the list is long.

*   **Settings Panel** (Bottom Left):
    *   **Min Confidence (Slider)**: Default `0.5`.
        *   *Lower (0.1-0.3)*: Detects more, but introduces "jitter" (shaking).
        *   *Higher (0.7-0.9)*: Rock solid stability, but might lose tracking during fast signs.
        *   **Recommendation**: Keep at `0.5` for standard testing.
    *   **Tracking Provider (Dropdown)**: The brain of the operation.
        *   `MediaPipe`: Fast, CPU-friendly, Google's standard.
        *   `RTMPose`: High-precision, GPU-heavy, State-of-the-Art (SOTA).
    *   **Generate Visualization**: Always keep this checked if you want to see the "skeleton" video afterwards.

*   **Live Preview** (Right):
    *   Shows the real-time processing.
    *   **Overlay Legend**:
        *   **Green Points**: Confident detection (>0.5).
        *   **Red Points**: Low confidence/Uncertain.
        *   **Blue skeleton**: Hand structure.
    *   **Note**: If using RTMPose, this might update slowly (e.g., 2-5 FPS) depending on your GPU.

---

### 🔍 Tab 2: Browse Results (The Inspector)
This is your database of processed clips.

*   **Results Table**:
    *   **Word/Filename**: Name of the video.
    *   **Quality**: The aggregate score (0.0 - 1.0).
        *   ✅ **> 0.70**: Excellent. Production ready.
        *   ⚠️ **0.50 - 0.70**: Good. Usable for filtering.
        *   ❌ **< 0.50**: Poor. Bad lighting, blur, or occlusion.
    *   **Frames**: Total length of tracking data.

*   **Preview Panel** (Right):
    *   Click any row in the table to load its data here.
    *   **Play Video**: Watch the "Debug Video" (the original video with skeleton overlay).
    *   **Download**: Export the tracking data (`.jsonl` or `.parquet`) for use in Unreal Engine/Blender.

---

### 📊 Tab 3: Dashboard (The Analyst)
High-level statistics about your dataset.

*   **Quality Score Distribution (Histogram)**:
    *   Visualizes the health of your dataset.
    *   **Goal**: You want a big cluster of bars on the *right side* (0.7-1.0).
    *   **Bad Sign**: A cluster of bars on the *left side* (0.0-0.3) indicates systemic issues (like the "Confidence Bug" we fixed in Phase 1.5).

*   **JSON Stats**: Raw numbers for the data nerd.

---

## 🧠 2. Understanding the Models

We use two competing technologies to track the Sign Language moves.

### 🔵 Model A: MediaPipe (The Baseline)
*   **Developer**: Google
*   **Type**: "Bottom-Up" / Holistic
*   **Pros**: Extremely fast. Runs on almost any laptop (CPU).
*   **Cons**: Struggles with self-occlusion (when hands cross in front of face). Can be "jittery".
*   **Best For**: Quick previews, real-time feedback, mobile apps.
*   **Documentation**: [MediaPipe Holistic Solutions](https://developers.google.com/mediapipe/solutions/vision/holistic_landmarker)

### 🟠 Model B: RTMPose (The Heavyweight)
*   **Developer**: OpenMMLab (MMPose)
*   **Type**: "Top-Down" (Two-stage)
    1.  **RTMDest-m**: Finds the human bounding box.
    2.  **RTMPose-l**: Finds the keypoints inside that box.
*   **Architecture**: ResNet-based backbone (SimCC).
*   **Key Feature**: Trained on **COCO-WholeBody**, meaning it understands the relationship between Face, Hands, and Body as a single unit, not separate parts.
*   **Pros**: Superior stability. "Sticky" tracking (doesn't lose hands as easily).
*   **Cons**: Requires NVIDIA GPU. Heavier installation (~4GB).
*   **Best For**: Offline processing, High-Quality Animation, MetaHuman creation.
*   **Documentation**: [MMPose / RTMPose Paper](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmpose)

---

## 📉 3. Interpreting Output Data

When looking at the `meta.json` or Quality Logs:

### The "Quality Score" Formula
The single number (e.g., `0.68`) is calculated based on:
1.  **Hand Visibility (40%)**: Does the AI see *both* hands?
2.  **Stability (30%)**: Are the points shaking, or moving smoothly?
3.  **Face Coverage (20%)**: Is the face consistently detected?
4.  **Confidence (10%)**: How sure is the AI about its own guess?

### Common Issues
*   **"low_hand_visibility"**: Usually means the person signed partly outside the camera frame from the bottom or sides.
*   **"unstable_tracking"**: Fast motion blur often causes this. RTMPose fixes this significantly compared to MediaPipe.
