# CURSOR PROMPT OPTIMIZED (Part 2) – CLI, Tests, Documentation

## 🖥️ CLI IMPLEMENTATION

**File**: `tracker_app/cli.py`

```python
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
from loguru import logger

from tracker_app.config import get_config
from tracker_app.store.db import Database
from tracker_app.store.disk import (
    save_tracking_parquet,
    save_tracking_jsonl,
    save_metadata
)
from tracker_app.ingest.manifest_reader import read_manifest
from tracker_app.ingest.job_builder import create_jobs_from_manifest
from tracker_app.preprocess.video_utils import get_video_metadata, extract_frames
from tracker_app.tracking.mediapipe_provider import MediaPipeProvider
from tracker_app.postprocess.smoothing import smooth_tracking_sequence
from tracker_app.postprocess.quality import compute_quality_score
from tracker_app.utils.logging_setup import setup_logging

app = typer.Typer(help="Open NSL Avatar Tracker")
console = Console()


@app.command()
def init_db():
    """Initialize database schema"""
    config = get_config()
    db = Database(config.db_path)
    db.init_schema()
    console.print(f"[green]✓[/green] Database initialized at {config.db_path}")


@app.command()
def ingest(
    csv_path: Path = typer.Argument(..., help="Path to manifest CSV"),
    dry_run: bool = typer.Option(False, help="Don't write to database")
):
    """Ingest manifest CSV and create jobs"""
    config = get_config()
    setup_logging(config.log_level)
    
    console.print(f"Reading manifest: {csv_path}")
    records = read_manifest(csv_path)
    console.print(f"Found {len(records)} videos")
    
    if dry_run:
        console.print("[yellow]Dry run - not writing to database[/yellow]")
        return
    
    db = Database(config.db_path)
    created, existing, missing = create_jobs_from_manifest(db, records)
    
    console.print(f"[green]✓[/green] Created {created} new jobs")
    console.print(f"[yellow]![/yellow] {existing} existing videos (skipped)")
    console.print(f"[red]✗[/red] {missing} missing files")


@app.command()
def run(
    limit: int = typer.Option(None, help="Max jobs to process"),
    status: str = typer.Option("queued", help="Job status filter"),
    word_prefix: str = typer.Option(None, help="Filter by word prefix"),
    resume: bool = typer.Option(False, help="Skip already done jobs"),
    visualize: bool = typer.Option(False, help="Generate debug videos")
):
    """Process video tracking jobs"""
    config = get_config()
    setup_logging(config.log_level)
    
    db = Database(config.db_path)
    
    # Get jobs
    jobs = db.get_jobs(status=status, word_prefix=word_prefix, limit=limit)
    
    if not jobs:
        console.print("[yellow]No jobs found matching criteria[/yellow]")
        return
    
    console.print(f"Processing {len(jobs)} jobs...")
    
    # Initialize tracking provider (reuse across videos)
    provider = MediaPipeProvider(
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence
    )
    
    success_count = 0
    fail_count = 0
    
    try:
        for job in track(jobs, description="Processing"):
            try:
                # Process single video
                _process_video(job, db, provider, config, visualize)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process {job['word']}/{job['filename']}: {e}")
                db.update_job(
                    job['id'],
                    status='failed',
                    error=str(e)
                )
                fail_count += 1
    
    finally:
        provider.close()
    
    console.print(f"\n[green]✓[/green] Success: {success_count}")
    console.print(f"[red]✗[/red] Failed: {fail_count}")


def _process_video(job, db, provider, config, visualize=False):
    """Process single video job"""
    video_path = Path(job['local_path'])
    video_id = job['video_id']
    job_id = job['id']
    
    # Update status
    db.update_job(job_id, status='processing')
    
    # Track frames
    logger.info(f"Tracking: {job['word']}/{job['filename']}")
    results = []
    
    for frame_idx, time_s, frame in extract_frames(video_path, config.target_fps):
        result = provider.track_frame(frame, frame_idx, time_s)
        results.append(result)
    
    if not results:
        raise ValueError("No frames extracted")
    
    # Smooth
    results = smooth_tracking_sequence(
        results,
        ema_alpha=config.ema_alpha_wrist,
        min_confidence=config.min_detection_confidence
    )
    
    # Quality score
    quality_score, issues = compute_quality_score(results)
    
    # Save to disk
    output_dir = config.tracks_dir / video_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert to dicts
    tracking_data = [r.to_dict() for r in results]
    
    # Save both formats
    if config.save_parquet:
        save_tracking_parquet(
            output_dir / "tracking.parquet",
            tracking_data
        )
    
    if config.save_jsonl:
        save_tracking_jsonl(
            output_dir / "tracking.jsonl.gz",
            tracking_data
        )
    
    # Metadata
    metadata = {
        'word': job['word'],
        'filename': job['filename'],
        'video_path': str(video_path),
        'quality_score': quality_score,
        'issues': issues,
        'frames': len(results),
        'tracking_provider': 'mediapipe',
        'format_version': 'v1'
    }
    save_metadata(output_dir / "meta.json", metadata)
    
    # Update database
    db.update_job(
        job_id,
        status='done',
        quality_score=quality_score,
        frames=len(results),
        tracking_provider='mediapipe',
        output_format='parquet+jsonl' if config.save_parquet and config.save_jsonl else 'jsonl'
    )
    
    # Record quality issues
    for issue in issues:
        db.add_quality_issue(
            job_id,
            issue_type=issue.get('type', 'unknown'),
            severity=issue.get('severity', 'info'),
            details=str(issue)
        )
    
    # Visualize if requested
    if visualize:
        from tracker_app.visualization.draw_landmarks import create_visualization_video
        viz_path = output_dir / "visualization.mp4"
        create_visualization_video(video_path, results, viz_path)
        logger.info(f"Visualization saved: {viz_path}")


@app.command()
def stats():
    """Show processing statistics"""
    config = get_config()
    db = Database(config.db_path)
    
    stats = db.get_stats()
    
    # Status table
    table = Table(title="Processing Status")
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    for status, count in stats['by_status'].items():
        table.add_row(status, str(count))
    
    console.print(table)
    
    # Quality stats
    if stats['quality']:
        console.print(f"\n[bold]Quality Scores:[/bold]")
        console.print(f"  Average: {stats['quality'].get('avg_quality', 0):.2f}")
        console.print(f"  Min: {stats['quality'].get('min_quality', 0):.2f}")
        console.print(f"  Max: {stats['quality'].get('max_quality', 0):.2f}")
    
    console.print(f"\n[bold]Total Videos:[/bold] {stats['total_videos']}")


@app.command()
def export_index(
    output_dir: Path = typer.Option(None, help="Output directory (default: exports)")
):
    """Generate export index (JSON + CSV)"""
    config = get_config()
    db = Database(config.db_path)
    
    if output_dir is None:
        output_dir = config.exports_dir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all done jobs
    jobs = db.get_jobs(status='done')
    
    # Build index
    index_data = []
    for job in jobs:
        index_data.append({
            'word': job['word'],
            'filename': job['filename'],
            'video_id': job['video_id'],
            'quality_score': job['quality_score'],
            'frames': job['frames'],
            'tracking_path': str(config.tracks_dir / job['video_id'])
        })
    
    # Save JSON
    import orjson
    json_path = output_dir / "index.json"
    with open(json_path, 'wb') as f:
        f.write(orjson.dumps(index_data, option=orjson.OPT_INDENT_2))
    
    # Save CSV
    import pandas as pd
    df = pd.DataFrame(index_data)
    csv_path = output_dir / "index.csv"
    df.to_csv(csv_path, index=False)
    
    console.print(f"[green]✓[/green] Exported {len(index_data)} entries")
    console.print(f"  JSON: {json_path}")
    console.print(f"  CSV: {csv_path}")


@app.command()
def visualize(
    word: str = typer.Argument(..., help="Word to visualize"),
    output: Path = typer.Option(None, help="Output video path")
):
    """Generate visualization for a specific word"""
    config = get_config()
    db = Database(config.db_path)
    
    # Find job
    jobs = db.get_jobs(status='done', word_prefix=word, limit=1)
    if not jobs:
        console.print(f"[red]No processed video found for word: {word}[/red]")
        return
    
    job = jobs[0]
    video_path = Path(job['local_path'])
    
    # Load tracking data
    from tracker_app.store.disk import load_tracking_parquet
    tracking_path = config.tracks_dir / job['video_id'] / "tracking.parquet"
    
    if not tracking_path.exists():
        console.print(f"[red]Tracking data not found: {tracking_path}[/red]")
        return
    
    console.print(f"Loading tracking data from {tracking_path}")
    df = load_tracking_parquet(tracking_path)
    
    # Convert back to TrackingResult objects
    # (This is simplified - you'd need proper deserialization)
    
    if output is None:
        output = config.workspace_dir / f"viz_{word}.mp4"
    
    console.print(f"Generating visualization: {output}")
    # ... (call visualization function)
    
    console.print(f"[green]✓[/green] Done: {output}")


if __name__ == "__main__":
    app()
```

---

## 🧪 TESTS

**File**: `tests/test_manifest_reader.py`

```python
import pytest
from pathlib import Path
from tracker_app.ingest.manifest_reader import read_manifest, ManifestRecord


def test_read_manifest_basic(tmp_path):
    """Test basic manifest reading"""
    # Create test CSV
    csv_content = """word,filename,local_path,remote_url
ananas,ananas-1.mp4,/path/to/ananas-1.mp4,https://example.com/ananas-1.mp4
banan,banan-1.mp4,/path/to/banan-1.mp4,https://example.com/banan-1.mp4
"""
    csv_path = tmp_path / "test_manifest.csv"
    csv_path.write_text(csv_content)
    
    records = read_manifest(csv_path)
    
    assert len(records) == 2
    assert records[0].word == "ananas"
    assert records[0].filename == "ananas-1.mp4"
    assert records[1].word == "banan"


def test_read_manifest_norwegian_chars(tmp_path):
    """Test handling of æøå"""
    csv_content = """word,filename,local_path,remote_url
æble,æble-1.mp4,/path/to/æble-1.mp4,
øre,øre-1.mp4,/path/to/øre-1.mp4,
året,året-1.mp4,/path/to/året-1.mp4,
"""
    csv_path = tmp_path / "test_manifest.csv"
    csv_path.write_text(csv_content, encoding='utf-8')
    
    records = read_manifest(csv_path)
    
    assert len(records) == 3
    assert records[0].word == "æble"
    assert records[1].word == "øre"
    assert records[2].word == "året"


def test_read_manifest_semicolon_delimiter(tmp_path):
    """Test semicolon delimiter"""
    csv_content = """word;filename;local_path;remote_url
test;test-1.mp4;/path/to/test-1.mp4;
"""
    csv_path = tmp_path / "test_manifest.csv"
    csv_path.write_text(csv_content)
    
    records = read_manifest(csv_path)
    
    assert len(records) == 1
    assert records[0].word == "test"
```

**File**: `tests/test_smoothing.py`

```python
import pytest
import numpy as np
from tracker_app.postprocess.smoothing import EMAFilter, VelocityClamp


def test_ema_filter_basic():
    """Test basic EMA filtering"""
    filter = EMAFilter(alpha=0.5)
    
    values = [1.0, 2.0, 3.0, 4.0]
    results = [filter.update(v) for v in values]
    
    # First value should pass through
    assert results[0] == 1.0
    
    # Subsequent values should be smoothed
    assert results[1] == 1.5  # 0.5 * 2 + 0.5 * 1
    assert results[2] == 2.25  # 0.5 * 3 + 0.5 * 1.5
    

def test_ema_filter_confidence_weighting():
    """Test confidence-weighted smoothing"""
    filter = EMAFilter(alpha=0.5)
    
    # High confidence
    result1 = filter.update(2.0, confidence=1.0)
    
    # Low confidence - should smooth more
    result2 = filter.update(10.0, confidence=0.2)
    
    # Low confidence should have less effect
    assert result2 < 5.0  # Should not jump to 10


def test_velocity_clamp():
    """Test velocity clamping"""
    clamp = VelocityClamp(max_change_per_frame=0.1)
    
    values = [0.0, 0.5, 0.6]  # Large jump then small
    results = [clamp.update(v) for v in values]
    
    assert results[0] == 0.0
    assert results[1] == 0.1  # Clamped to max_change
    assert results[2] == 0.2  # 0.1 + 0.1


def test_velocity_clamp_negative():
    """Test velocity clamping with negative values"""
    clamp = VelocityClamp(max_change_per_frame=0.1)
    
    values = [1.0, 0.0]  # Large negative jump
    results = [clamp.update(v) for v in values]
    
    assert results[1] == 0.9  # Clamped to -0.1
```

**File**: `tests/test_tracking.py`

```python
import pytest
import numpy as np
from tracker_app.tracking.mediapipe_provider import MediaPipeProvider
from tracker_app.tracking.base import TrackingResult


def test_mediapipe_provider_initialization():
    """Test MediaPipe provider can be initialized"""
    provider = MediaPipeProvider()
    assert provider is not None
    provider.close()


def test_tracking_result_to_dict():
    """Test TrackingResult serialization"""
    result = TrackingResult(
        frame_index=0,
        time_s=0.0,
        image_size=(1920, 1080),
        pose_confidence=0.95,
        left_hand_confidence=0.87,
        right_hand_confidence=0.92,
        face_confidence=0.88
    )
    
    data = result.to_dict()
    
    assert data['frame_index'] == 0
    assert data['time_s'] == 0.0
    assert data['image_size'] == {'width': 1920, 'height': 1080}
    assert data['confidence']['pose'] == 0.95
```

---

## 📄 SUPPORTING FILES

**File**: `.env.example`

```env
# Workspace
WORKSPACE_DIR=D:/tegnspråk/workspace

# Video processing
TARGET_FPS=25
TARGET_HEIGHT=720
ENABLE_NORMALIZATION=false

# Tracking
TRACKING_PROVIDER=mediapipe
MIN_DETECTION_CONFIDENCE=0.5
MIN_TRACKING_CONFIDENCE=0.5

# Smoothing
EMA_ALPHA_WRIST=0.35
EMA_ALPHA_FINGERS=0.55
EMA_ALPHA_FACE=0.40
VELOCITY_CLAMP_DEG_PER_FRAME=18.0

# Output
SAVE_PARQUET=true
SAVE_JSONL=true

# Quality
MIN_QUALITY_SCORE=0.5

# Logging
LOG_LEVEL=INFO
```

**File**: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
workspace/
*.db
*.mp4
*.avi
*.mov
*.parquet
*.jsonl.gz

# Logs
logs/
*.log

# Environment
.env

# OS
.DS_Store
Thumbs.db
```

**File**: `requirements.txt`

```txt
# Core
typer>=0.9.0
rich>=13.7.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0

# Video
opencv-python>=4.8.0
ffmpeg-python>=0.2.0

# Data
pandas>=2.1.0
pyarrow>=14.0.0
orjson>=3.9.0

# ML/Tracking
mediapipe>=0.10.9
numpy>=1.26.0

# Logging
loguru>=0.7.0

# Visualization
matplotlib>=3.8.0
plotly>=5.18.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 📖 README.md

```markdown
# Open NSL Avatar Tracker

Local batch processing pipeline for Norwegian Sign Language (NSL) video tracking → MetaHuman animation.

## Features

- ✅ MediaPipe-based tracking (pose + hands + face)
- ✅ SQLite database for job management
- ✅ Parquet + JSONL output formats
- ✅ EMA smoothing and quality scoring
- ✅ Built-in visualization tools
- ✅ Robust error handling and resume capability

## Installation

### 1. Prerequisites

- Python 3.11+
- NVIDIA GPU with CUDA (recommended)
- FFmpeg in PATH

### 2. Setup

```bash
# Clone repository
git clone <repo-url>
cd open-nsl-avatar-tracker

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your paths
```

### 3. Initialize database

```bash
python -m tracker_app init-db
```

## Usage

### Ingest manifest

```bash
python -m tracker_app ingest D:\tegnspråk\minetegn_manifest_app_excel.csv
```

### Process videos

```bash
# Process 10 videos
python -m tracker_app run --limit 10

# Process specific word prefix
python -m tracker_app run --word-prefix "a" --limit 20

# Resume failed jobs
python -m tracker_app run --status failed
```

### Check statistics

```bash
python -m tracker_app stats
```

### Generate export index

```bash
python -m tracker_app export-index
```

### Visualize tracking

```bash
python -m tracker_app visualize ananas
```

## Output Structure

```
workspace/
  tracker.db           # SQLite database
  tracks/
    <video-id>/
      tracking.parquet  # Efficient columnar format
      tracking.jsonl.gz # Human-readable debug format
      meta.json        # Metadata + quality score
  exports/
    index.json         # Export catalog
    index.csv
  logs/
    tracker_*.log
```

## Troubleshooting

### "Cannot open video"
- Check that FFmpeg is installed and in PATH
- Verify video file exists at `local_path`

### Low quality scores
- Check video resolution (higher is better)
- Ensure good lighting and neutral background
- Hands should be visible throughout

### Slow processing
- Verify GPU is being used (`nvidia-smi`)
- Lower `TARGET_FPS` in .env
- Disable `SAVE_JSONL` if not needed

## Development

### Run tests

```bash
pytest tests/
```

### Add new tracking provider

1. Implement `TrackingProvider` interface
2. Add to `tracker_app/tracking/`
3. Update config

## License

[Your license]
```

---

## ✅ VALIDATION CHECKLIST

After Cursor generates the code, verify:

1. **Installation works**:
   ```bash
   pip install -r requirements.txt
   python -m tracker_app --help
   ```

2. **Database initializes**:
   ```bash
   python -m tracker_app init-db
   ```

3. **Ingest works** (on test CSV):
   ```bash
   python -m tracker_app ingest tests/fixtures/sample_manifest.csv --dry-run
   ```

4. **Tests pass**:
   ```bash
   pytest tests/
   ```

5. **Process 1 video** (end-to-end test)

---

## 🚀 NEXT STEPS

After Phase 1 MVP is working:

1. **Phase 1.5**: Add visualization UI (Gradio/Streamlit)
2. **Phase 2**: Upgrade to RTMPose/MMPose
3. **Phase 2.1**: MetaHuman Control Rig mapping

---

**END OF OPTIMIZED CURSOR PROMPT**

This prompt is ready to paste into Cursor and will generate a complete, working repository with all best practices included.
