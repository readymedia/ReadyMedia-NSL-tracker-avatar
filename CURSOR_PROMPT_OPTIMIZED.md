# CURSOR MASTER PROMPT – Open NSL Avatar (OPTIMIZED v2)

## 🎯 OVERVIEW

Build a local batch processing pipeline to extract tracking data from 9000+ Norwegian Sign Language videos and prepare them for MetaHuman/Unreal animation.

**Key improvements in v2:**
- ✅ SQLite instead of Supabase (simpler, faster to start)
- ✅ Parquet + JSONL output (efficient + debuggable)
- ✅ Built-in visualization/debugging
- ✅ Better error handling and logging
- ✅ Clearer code structure

---

## 📋 PROJECT CONTEXT

**Dataset:**
- 9000+ MP4 videos in `D:\tegnspråk\minetegn_videos\`
- Manifest CSV: `D:\tegnspråk\minetegn_manifest_app_excel.csv`
- Columns: `word`, `filename`, `local_path`, `remote_url`

**Target:**
- Windows PC with NVIDIA GPU
- Local processing only (no cloud)
- Output: Tracking data ready for Unreal/MetaHuman

**This is Phase 1 MVP**: Working end-to-end pipeline.

---

## 🏗️ REPOSITORY STRUCTURE

Generate complete repository:

```
open-nsl-avatar-tracker/
  tracker_app/
    __init__.py
    __main__.py
    cli.py
    config.py

    ingest/
      __init__.py
      manifest_reader.py
      job_builder.py

    preprocess/
      __init__.py
      video_utils.py
      normalize.py

    tracking/
      __init__.py
      base.py                    # Abstract provider interface
      mediapipe_provider.py      # MediaPipe implementation
      models.py                  # Data models

    postprocess/
      __init__.py
      smoothing.py               # EMA + OneEuro filters
      quality.py                 # Quality scoring

    store/
      __init__.py
      db.py                      # SQLite operations
      disk.py                    # File I/O (Parquet + JSONL)
      schema.sql                 # Database schema

    visualization/
      __init__.py
      draw_landmarks.py          # Draw tracking on video
      quality_report.py          # Generate HTML reports

    utils/
      __init__.py
      paths.py
      text.py
      hashing.py
      logging_setup.py

  scripts/
    visualize_tracking.py        # Standalone visualization tool
    quality_dashboard.py         # Generate quality report
    run_batch.ps1               # PowerShell batch script

  tests/
    __init__.py
    test_manifest_reader.py
    test_smoothing.py
    test_tracking.py
    fixtures/
      sample_manifest.csv

  .env.example
  .gitignore
  requirements.txt
  README.md
  pyproject.toml
```

---

## 🔧 TECHNOLOGY STACK

### Core Dependencies:
```txt
# Python 3.11+
typer>=0.9.0              # CLI
rich>=13.7.0              # Terminal UI
pydantic>=2.5.0           # Config validation
python-dotenv>=1.0.0      # Environment

# Video processing
opencv-python>=4.8.0
ffmpeg-python>=0.2.0

# Data handling
pandas>=2.1.0
pyarrow>=14.0.0           # Parquet support
orjson>=3.9.0             # Fast JSON

# ML/Tracking
mediapipe>=0.10.9
numpy>=1.26.0

# Database
# (SQLite is built-in, no dependency needed)

# Logging
loguru>=0.7.0

# Visualization
matplotlib>=3.8.0
plotly>=5.18.0            # For interactive reports

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 📊 DATABASE SCHEMA (SQLite)

**File**: `tracker_app/store/schema.sql`

```sql
-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,              -- UUID
    word TEXT NOT NULL,
    filename TEXT NOT NULL,
    remote_url TEXT,
    local_path TEXT NOT NULL,
    sha1 TEXT UNIQUE,                 -- For deduplication
    duration_s REAL,
    fps REAL,
    width INTEGER,
    height INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_videos_word ON videos(word);
CREATE INDEX idx_videos_sha1 ON videos(sha1);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL,
    status TEXT NOT NULL,             -- queued|processing|done|failed|missing_file
    error TEXT,
    started_at TEXT,
    finished_at TEXT,
    quality_score REAL,
    frames INTEGER,
    tracking_provider TEXT,           -- e.g., "mediapipe"
    output_format TEXT,               -- e.g., "parquet+jsonl"
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_video_id ON jobs(video_id);
CREATE INDEX idx_jobs_quality ON jobs(quality_score);

-- Quality issues table (for detailed tracking)
CREATE TABLE IF NOT EXISTS quality_issues (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    issue_type TEXT NOT NULL,        -- e.g., "hand_missing", "low_confidence"
    severity TEXT NOT NULL,           -- "warning"|"error"
    frame_start INTEGER,
    frame_end INTEGER,
    details TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX idx_quality_job ON quality_issues(job_id);
```

---

## ⚙️ CONFIGURATION

**File**: `tracker_app/config.py`

```python
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration"""
    
    # Paths
    workspace_dir: Path = Path("D:/tegnspråk/workspace")
    cache_dir: Optional[Path] = None
    tracks_dir: Optional[Path] = None
    exports_dir: Optional[Path] = None
    db_path: Optional[Path] = None
    
    # Video processing
    target_fps: int = 25
    target_height: int = 720
    enable_normalization: bool = False  # Set True if videos vary greatly
    
    # Tracking
    tracking_provider: str = "mediapipe"
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    
    # Smoothing
    ema_alpha_wrist: float = 0.35
    ema_alpha_fingers: float = 0.55
    ema_alpha_face: float = 0.40
    velocity_clamp_deg_per_frame: float = 18.0
    
    # Output
    save_parquet: bool = True
    save_jsonl: bool = True  # For debugging
    
    # Quality
    min_quality_score: float = 0.5
    
    # Logging
    log_level: str = "INFO"
    log_dir: Optional[Path] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-derive paths
        if self.cache_dir is None:
            self.cache_dir = self.workspace_dir / "cache"
        if self.tracks_dir is None:
            self.tracks_dir = self.workspace_dir / "tracks"
        if self.exports_dir is None:
            self.exports_dir = self.workspace_dir / "exports"
        if self.db_path is None:
            self.db_path = self.workspace_dir / "tracker.db"
        if self.log_dir is None:
            self.log_dir = self.workspace_dir / "logs"
        
        # Ensure directories exist
        for path in [self.workspace_dir, self.cache_dir, self.tracks_dir, 
                     self.exports_dir, self.log_dir]:
            path.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Optional[Config] = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
```

---

## 🗄️ DATABASE LAYER

**File**: `tracker_app/store/db.py`

```python
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from contextlib import contextmanager
from loguru import logger


class Database:
    """SQLite database operations"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_schema(self) -> None:
        """Initialize database schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path) as f:
            schema_sql = f.read()
        
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def insert_video(
        self,
        word: str,
        filename: str,
        local_path: str,
        remote_url: Optional[str] = None,
        sha1: Optional[str] = None,
        duration_s: Optional[float] = None,
        fps: Optional[float] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> str:
        """Insert video record, return video_id"""
        video_id = str(uuid4())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO videos (id, word, filename, local_path, remote_url, 
                                   sha1, duration_s, fps, width, height)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (video_id, word, filename, local_path, remote_url, 
                  sha1, duration_s, fps, width, height))
        
        return video_id
    
    def get_video_by_sha1(self, sha1: str) -> Optional[Dict[str, Any]]:
        """Find video by SHA1 hash"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM videos WHERE sha1 = ?", (sha1,)
            ).fetchone()
        
        return dict(row) if row else None
    
    def create_job(self, video_id: str) -> str:
        """Create processing job for video"""
        job_id = str(uuid4())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO jobs (id, video_id, status)
                VALUES (?, ?, 'queued')
            """, (job_id, video_id))
        
        return job_id
    
    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        error: Optional[str] = None,
        quality_score: Optional[float] = None,
        frames: Optional[int] = None,
        tracking_provider: Optional[str] = None,
        output_format: Optional[str] = None
    ) -> None:
        """Update job fields"""
        updates = []
        values = []
        
        if status:
            updates.append("status = ?")
            values.append(status)
            
            if status == "processing":
                updates.append("started_at = ?")
                values.append(datetime.now().isoformat())
            elif status in ("done", "failed"):
                updates.append("finished_at = ?")
                values.append(datetime.now().isoformat())
        
        if error is not None:
            updates.append("error = ?")
            values.append(error)
        
        if quality_score is not None:
            updates.append("quality_score = ?")
            values.append(quality_score)
        
        if frames is not None:
            updates.append("frames = ?")
            values.append(frames)
        
        if tracking_provider:
            updates.append("tracking_provider = ?")
            values.append(tracking_provider)
        
        if output_format:
            updates.append("output_format = ?")
            values.append(output_format)
        
        if not updates:
            return
        
        values.append(job_id)
        sql = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
        
        with self.get_connection() as conn:
            conn.execute(sql, values)
    
    def get_jobs(
        self,
        status: Optional[str] = None,
        word_prefix: Optional[str] = None,
        limit: Optional[int] = None,
        min_quality: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Query jobs with filters"""
        sql = """
            SELECT j.*, v.word, v.filename, v.local_path
            FROM jobs j
            JOIN videos v ON j.video_id = v.id
            WHERE 1=1
        """
        params = []
        
        if status:
            sql += " AND j.status = ?"
            params.append(status)
        
        if word_prefix:
            sql += " AND v.word LIKE ?"
            params.append(f"{word_prefix}%")
        
        if min_quality is not None:
            sql += " AND (j.quality_score IS NULL OR j.quality_score >= ?)"
            params.append(min_quality)
        
        sql += " ORDER BY v.word, v.filename"
        
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        
        with self.get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            # Job counts by status
            rows = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM jobs
                GROUP BY status
            """).fetchall()
            stats['by_status'] = {row['status']: row['count'] for row in rows}
            
            # Quality distribution
            row = conn.execute("""
                SELECT 
                    AVG(quality_score) as avg_quality,
                    MIN(quality_score) as min_quality,
                    MAX(quality_score) as max_quality
                FROM jobs
                WHERE quality_score IS NOT NULL
            """).fetchone()
            stats['quality'] = dict(row) if row else {}
            
            # Total videos
            row = conn.execute("SELECT COUNT(*) as count FROM videos").fetchone()
            stats['total_videos'] = row['count']
        
        return stats
    
    def add_quality_issue(
        self,
        job_id: str,
        issue_type: str,
        severity: str,
        frame_start: Optional[int] = None,
        frame_end: Optional[int] = None,
        details: Optional[str] = None
    ) -> None:
        """Record quality issue for a job"""
        issue_id = str(uuid4())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO quality_issues 
                (id, job_id, issue_type, severity, frame_start, frame_end, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (issue_id, job_id, issue_type, severity, frame_start, frame_end, details))
```

---

## 💾 DISK STORAGE

**File**: `tracker_app/store/disk.py`

```python
import gzip
import orjson
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from loguru import logger


def save_tracking_parquet(
    output_path: Path,
    tracking_data: List[Dict[str, Any]]
) -> None:
    """Save tracking data as Parquet (efficient, columnar)"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(tracking_data)
    df.to_parquet(
        output_path,
        engine='pyarrow',
        compression='snappy',
        index=False
    )
    
    logger.debug(f"Saved Parquet: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


def save_tracking_jsonl(
    output_path: Path,
    tracking_data: List[Dict[str, Any]]
) -> None:
    """Save tracking data as JSONL.gz (human-readable, for debugging)"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        for record in tracking_data:
            json_str = orjson.dumps(record).decode('utf-8')
            f.write(json_str + '\n')
    
    logger.debug(f"Saved JSONL: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


def save_metadata(
    output_path: Path,
    metadata: Dict[str, Any]
) -> None:
    """Save metadata JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(orjson.dumps(metadata, option=orjson.OPT_INDENT_2))
    
    logger.debug(f"Saved metadata: {output_path}")


def load_tracking_parquet(filepath: Path) -> pd.DataFrame:
    """Load tracking data from Parquet"""
    return pd.read_parquet(filepath, engine='pyarrow')
```

---

## 🎬 VIDEO UTILITIES

**File**: `tracker_app/preprocess/video_utils.py`

```python
import cv2
import ffmpeg
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, Tuple
import numpy as np
from loguru import logger


def get_video_metadata(video_path: Path) -> Dict[str, Any]:
    """Extract video metadata using ffmpeg-python"""
    try:
        probe = ffmpeg.probe(str(video_path))
        video_stream = next(
            (s for s in probe['streams'] if s['codec_type'] == 'video'),
            None
        )
        
        if not video_stream:
            raise ValueError("No video stream found")
        
        # Calculate FPS
        fps_str = video_stream.get('r_frame_rate', '0/1')
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 0
        
        # Duration
        duration = float(probe['format'].get('duration', 0))
        
        metadata = {
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'fps': fps,
            'duration_s': duration,
            'codec': video_stream.get('codec_name'),
            'frames': int(video_stream.get('nb_frames', duration * fps))
        }
        
        return metadata
    
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error reading {video_path}: {e.stderr.decode()}")
        raise


def extract_frames(
    video_path: Path,
    target_fps: Optional[int] = None
) -> Iterator[Tuple[int, float, np.ndarray]]:
    """
    Yield frames from video.
    
    Yields:
        (frame_index, time_s, frame_array)
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate frame skip if target_fps specified
    frame_skip = 1
    if target_fps and target_fps < original_fps:
        frame_skip = int(original_fps / target_fps)
    
    frame_index = 0
    actual_frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames if needed
            if frame_index % frame_skip != 0:
                frame_index += 1
                continue
            
            time_s = frame_index / original_fps
            
            yield (actual_frame_count, time_s, frame)
            
            frame_index += 1
            actual_frame_count += 1
    
    finally:
        cap.release()


def save_debug_frame(
    frame: np.ndarray,
    output_path: Path,
    landmarks: Optional[List] = None
) -> None:
    """Save frame with optional landmarks drawn (for debugging)"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    debug_frame = frame.copy()
    
    if landmarks:
        # Draw landmarks on frame
        for lm in landmarks:
            if hasattr(lm, 'x') and hasattr(lm, 'y'):
                x = int(lm.x * frame.shape[1])
                y = int(lm.y * frame.shape[0])
                cv2.circle(debug_frame, (x, y), 3, (0, 255, 0), -1)
    
    cv2.imwrite(str(output_path), debug_frame)
```

---

## 🤖 TRACKING PROVIDER (MediaPipe)

**File**: `tracker_app/tracking/base.py`

```python
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
```

**File**: `tracker_app/tracking/mediapipe_provider.py`

```python
import mediapipe as mp
import numpy as np
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
                landmarks = self._convert_landmarks(hand_landmarks)
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
            result.face_landmarks = self._convert_landmarks(face_landmarks)
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
    
    def _convert_landmarks(self, landmarks) -> List[Landmark2D]:
        """Convert MediaPipe landmarks to our format"""
        result = []
        for lm in landmarks.landmark:
            result.append(Landmark2D(
                x=lm.x,
                y=lm.y,
                confidence=getattr(lm, 'visibility', 1.0)  # Some don't have visibility
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
```

---

## 🔄 SMOOTHING

**File**: `tracker_app/postprocess/smoothing.py`

```python
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
```

---

## ✅ QUALITY SCORING

**File**: `tracker_app/postprocess/quality.py`

```python
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
    """Ratio of frames where both hands are detected"""
    both_hands = sum(
        1 for r in results
        if r.left_hand_landmarks and r.right_hand_landmarks
    )
    return both_hands / len(results)


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
            prev_wrist = prev.left_hand_landmarks[0]  # Wrist is index 0
            curr_wrist = curr.left_hand_landmarks[0]
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
```

---

## 🎨 VISUALIZATION

**File**: `tracker_app/visualization/draw_landmarks.py`

```python
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
```

---

**(Due to length, I'll continue in next message with CLI, tests, and scripts...)**

Would you like me to continue with the complete implementation?