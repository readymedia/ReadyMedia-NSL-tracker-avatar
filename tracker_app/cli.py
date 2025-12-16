import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
from loguru import logger
import csv

from tracker_app.config import get_config
from tracker_app.store.db import Database
from tracker_app.store.disk import (
    save_tracking_parquet,
    save_tracking_jsonl,
    save_metadata
)
from tracker_app.ingest.manifest_reader import read_manifest, ManifestRecord
from tracker_app.ingest.job_builder import create_jobs_from_manifest
from tracker_app.preprocess.video_utils import get_video_metadata, extract_frames
from tracker_app.postprocess.smoothing import smooth_tracking_sequence
from tracker_app.postprocess.quality import compute_quality_score
from tracker_app.utils.logging_setup import setup_logging
from tracker_app.tracking.factory import get_tracking_provider

# Deleted old get_provider function here


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
def process_video(
    video_path: Path = typer.Argument(..., help="Path to single video file"),
    word: str = typer.Option("unknown", help="Word label for the video"),
    visualize: bool = typer.Option(False, help="Generate debug video"),
    provider: str = typer.Option("mediapipe", help="Tracking provider (mediapipe/rtmpose)")
):
    """Process a single video file directly (bypass jobs table for testing)"""
    config = get_config()
    setup_logging(config.log_level)
    
    # Mock a job dictionary
    job = {
        'id': 'manual-test',
        'video_id': 'manual-test-video',
        'word': word,
        'filename': video_path.name,
        'local_path': str(video_path)
    }
    
    # We need a DB instance passing even if we don't strictly use it for keeping state effectively
    # But _process_video expects it to update status. 
    # Let's create a temporary in-memory DB or just reuse main DB but insert a dummy job if needed.
    # Actually, let's just use the main logic but careful about the DB calls.
    
    # To keep it simple and reuse _process_video, we should probably insert this into the DB first.
    db = Database(config.db_path)
    # Ensure DB is init
    if not config.db_path.exists():
        db.init_schema()
        
    try:
        # Check if video exists, if not insert
        existing = db.get_video_by_filename(job['filename'])
        if existing:
            video_id = existing['id']
            # job entry?
        else:
            video_id = db.insert_video(word, job['filename'], str(video_path))
            
        # Create a specific job for this run
        job_id = db.create_job(video_id)
        
        # Now fetch the full job record
        jobs = db.get_jobs(limit=1) # This filter is weak, let's just make a valid job dict manually
        job['id'] = job_id
        job['video_id'] = video_id
        
        provider_instance = get_tracking_provider(provider, config.min_detection_confidence)
        
        try:
            _process_video(job, db, provider_instance, config, visualize, provider_name=provider)
            console.print(f"[green]✓[/green] Successfully processed {video_path}")
        finally:
            provider_instance.close()
            
    except Exception as e:
        console.print(f"[red]Error processing video:[/red] {e}")
        raise e


@app.command()
def run(
    limit: int = typer.Option(None, help="Max jobs to process"),
    status: str = typer.Option("queued", help="Job status filter"),
    word_prefix: str = typer.Option(None, help="Filter by word prefix"),
    resume: bool = typer.Option(False, help="Skip already done jobs"),
    visualize: bool = typer.Option(False, help="Generate debug videos"),
    provider: str = typer.Option("mediapipe", help="Tracking provider (mediapipe/rtmpose)")
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
    provider_instance = get_tracking_provider(provider, config.min_detection_confidence)
    
    success_count = 0
    fail_count = 0
    
    try:
        for job in track(jobs, description="Processing"):
            try:
                # Process single video
                _process_video(job, db, provider_instance, config, visualize, provider_name=provider)
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
        provider_instance.close()
    
    console.print(f"\n[green]✓[/green] Success: {success_count}")
    console.print(f"[red]✗[/red] Failed: {fail_count}")


def _process_video(job, db, provider, config, visualize=False, provider_name='mediapipe'):
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
        'tracking_provider': provider_name,
        'format_version': 'v1'
    }
    save_metadata(output_dir / "meta.json", metadata)
    
    # Update database
    db.update_job(
        job_id,
        status='done',
        quality_score=quality_score,
        frames=len(results),
        tracking_provider=provider_name,
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
    if stats['quality'] and stats['quality'].get('avg_quality') is not None:
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
    """Generate visualization for a Job looking up by word"""
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
    
    # Convert back only what's needed for visualization (simplified)
    # Ideally we reconstruct TrackingResult objects
    # But for now, let's just implement a quick reader or ensure create_visualization_video handles df?
    # No, create_visualization_video expects List[TrackingResult].
    # We need to reconstruct.
    
    # Lazy reconstruction - in real usage we would have a deserializer
    # For now, let's warn that this is not fully implemented in CLI without deserializer
    console.print("[yellow]Visualization from disk not fully implemented in CLI yet. Use --visualize flag during run/process-video instead.[/yellow]")


if __name__ == "__main__":
    app()
