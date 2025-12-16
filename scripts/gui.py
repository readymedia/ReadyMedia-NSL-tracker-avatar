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
from tracker_app.tracking.factory import get_tracking_provider
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
    provider_name: str,
    progress=gr.Progress()
):
    """Process videos with live preview"""
    global processing_active
    processing_active = True
    
    # Use factory
    try:
        provider = get_tracking_provider(provider_name, min_conf)
    except Exception as e:
        yield (f"Failed to initialize provider: {e}", None, "Error", "")
        processing_active = False
        return
    
    results_log = []
    
    # Helper to parse video name from "name (size KB)"
    video_paths = []
    for v_str in selected_videos:
         # Assuming format "filename.mp4 (size KB)"
         name = v_str.split(" (")[0]
         video_paths.append(Path("video-eksempler") / name)

    
    for i, video_path in enumerate(video_paths):
        if not video_path.exists():
             results_log.append(f"[!] File not found: {video_path}")
             continue

        progress((i, len(video_paths)), desc=f"Processing {video_path.name}")
        
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
                    # Gradio expects RGB
                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    
                    yield (
                        "\n".join(results_log[-10:]),
                        annotated_rgb,
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
            
            # Save results (simplified - ideally reuse CLI logic but here just for show as requested)
            # In Phase 1.5 we want it functional
            # Let's save just like CLI does
            from tracker_app.postprocess.smoothing import smooth_tracking_sequence
            from tracker_app.postprocess.quality import compute_quality_score
            from tracker_app.store.disk import save_tracking_parquet, save_tracking_jsonl, save_metadata
            
            # Smooth
            tracking_results = smooth_tracking_sequence(tracking_results)
             
            # Quality
            quality_score, issues = compute_quality_score(tracking_results)
            
            # Save
            # Need video ID. Let's just use filename hash or lookup in DB if we had ingested it?
            # For "Process" tab which acts on file browser, we might act outside DB or upsert.
            # Let's simple upsert.
            
            # Upsert video to DB
            vid_rec = db.get_video_by_filename(video_path.name)
            if vid_rec:
                video_id = vid_rec['id']
            else:
                video_id = db.insert_video(video_path.stem, video_path.name, str(video_path))
            
            job_id = db.create_job(video_id)
            
            # Save files
            output_dir = config.tracks_dir / video_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            tracking_data = [r.to_dict() for r in tracking_results]
            
            if save_parquet:
                save_tracking_parquet(output_dir / "tracking.parquet", tracking_data)
            if save_jsonl:
                save_tracking_jsonl(output_dir / "tracking.jsonl.gz", tracking_data)
                
            save_metadata(output_dir / "meta.json", {
                'quality_score': quality_score,
                'issues': issues,
                'frames': len(tracking_results)
            })
            
            # Update Job
            db.update_job(job_id, status='done', quality_score=quality_score, frames=len(tracking_results))
            
            # Viz
            if generate_viz:
                from tracker_app.visualization.draw_landmarks import create_visualization_video
                create_visualization_video(video_path, tracking_results, output_dir / "visualization.mp4")

            
            results_log.append(f"[✓] {video_path.name} - Quality: {quality_score:.2f}")
            
        except Exception as e:
            results_log.append(f"[✗] {video_path.name} - Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
        quality_score = j['quality_score'] if j['quality_score'] is not None else 0.0
        quality_icon = (
            "⭐" if quality_score > 0.8 else
            "✓" if quality_score > 0.7 else
            "⚠"
        )
        table_data.append([
            j['word'],
            f"{quality_icon} {quality_score:.2f}",
            j['frames']
        ])
    
    return table_data


def show_video_preview(selected_row):
    """Show video preview when row selected"""
    if not selected_row:
        return None, "Select a video to preview"
    
    # Load video and tracking data
    # ... implementation ...
    
    return None, "Preview not implemented yet"  # Placeholder


# ============================================================================
# TAB 3: DASHBOARD
# ============================================================================

def generate_dashboard():
    """Generate dashboard statistics"""
    stats = db.get_stats()
    
    # Create quality histogram
    import plotly.graph_objects as go
    
    jobs = db.get_jobs(status='done')
    quality_scores = [j['quality_score'] for j in jobs if j['quality_score'] is not None]
    
    if not quality_scores:
        quality_scores = [0]
    
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
                        
                        provider_dropdown_proc = gr.Dropdown(
                            choices=["MediaPipe", "RTMPose"],
                            value="MediaPipe",
                            label="Tracking Provider"
                        )
                        
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
                           save_jsonl, save_parquet, generate_viz, provider_dropdown_proc],
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
