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
