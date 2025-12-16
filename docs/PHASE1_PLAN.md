# Phase 1 Implementation Plan

## Overview
**Goal**: Build a working end-to-end pipeline that ingests video, tracks pose/hands/face using MediaPipe, and saves data to SQLite and Parquet.

**Timeline**: ~22 hours estimated.

## Detailed Tasks

### 1. Project Skeleton & CLI (2 hours)
- [ ] Initialize `tracker_app` package structure
- [ ] Setup `poetry` or `requirements.txt`
- [ ] Implement `cli.py` with `Typer`
- [ ] Add `config.py` using `pydantic-settings`
- [ ] Setup logging (`loguru`)

### 2. Database Layer (SQLite) (4 hours)
- [ ] implement `tracker_app/store/sqlite_store.py`
- [ ] Define SQL schema (`videos`, `jobs`, `tracks`)
- [ ] Implement `init-db` command
- [ ] Write tests for CRUD operations
- [ ] **Deliverable**: Working DB with tests.

### 3. Ingest Module (3 hours)
- [ ] Create `tracker_app/ingest/video_scanner.py`
- [ ] Implement directory scanning (glob)
- [ ] Implement deduplication (SHA1 hash)
- [ ] Populate `videos` and `jobs` tables from `video-eksempler/`
- [ ] **Deliverable**: `python -m tracker_app ingest` populates DB.

### 4. Video Preprocessing (3 hours)
- [ ] Implement `tracker_app/preprocess/ffmpeg_utils.py`
- [ ] Get video metadata (FFmpeg probe)
- [ ] Create frame generator (yield numpy arrays)
- [ ] **Deliverable**: Ability to iterate frames from any DB video.

### 5. Tracking Provider (MediaPipe) (6 hours)
- [ ] Define `TrackingProvider` abstract base class
- [ ] Implement `MediaPipeProvider`
  - [ ] Initialize Solutions (Holistic or separate modules)
  - [ ] Convert MP output to `TrackingResult` (dataclass)
  - [ ] Handle missing landmarks (NaN or None)
- [ ] **Deliverable**: `provider.process_frame(frame)` returns structured data.

### 6. Storage & Output (4 hours)
- [ ] Implement `tracker_app/store/disk_store.py`
- [ ] Save `TrackingResult` list to Parquet (using `pyarrow`)
- [ ] Save to JSONL (for debugging)
- [ ] Update `jobs` status to `done` on success
- [ ] **Deliverable**: Full pipeline run generates output files.

### 7. End-to-End Test (Optional/Buffer)
- [ ] Run on all 14 sample videos
- [ ] Verify output integrities

## Technical Decisions Re-confirmed
- **DB**: SQLite (file-based, easy backup).
- **Tracking**: MediaPipe (CPU-friendly, easy install).
- **Output**: Parquet (primary), JSONL (secondary).
- **Video Lib**: `opencv-python` for reading frames (easier than piping ffmpeg stdout for MVP, though `ffmpeg-python` is more robust for weird formats. We stick to OpenCV for Phase 1 unless issues arise).

## Next Immediate Step
Start with **Task 1: Project Skeleton**.
