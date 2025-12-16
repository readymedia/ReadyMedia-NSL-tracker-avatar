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

    def get_video_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Find video by filename"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM videos WHERE filename = ?", (filename,)
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
