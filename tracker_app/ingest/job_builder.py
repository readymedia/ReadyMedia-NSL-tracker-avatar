from pathlib import Path
from typing import List, Tuple
from loguru import logger
from tracker_app.store.db import Database
from tracker_app.ingest.manifest_reader import ManifestRecord

def create_jobs_from_manifest(
    db: Database,
    records: List[ManifestRecord]
) -> Tuple[int, int, int]:
    """
    Create jobs from manifest records.
    Returns (created_count, existing_count, missing_count)
    """
    created = 0
    existing = 0
    missing = 0
    
    for record in records:
        # Check if file exists
        local_path = Path(record.local_path)
        if not local_path.exists():
            logger.warning(f"File not found: {local_path}")
            missing += 1
            continue
            
        # Check if video already exists in DB
        existing_video = db.get_video_by_filename(record.filename)
        
        if existing_video:
            existing += 1
            # Optional: Check if job exists, if not create one?
            # For now, we count specific video entries as existence
            continue
            
        # Insert video
        video_id = db.insert_video(
            word=record.word,
            filename=record.filename,
            local_path=str(local_path),
            remote_url=record.remote_url
        )
        
        # Create job
        db.create_job(video_id)
        created += 1
        
    return created, existing, missing
