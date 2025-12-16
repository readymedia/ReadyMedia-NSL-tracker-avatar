# 02 – System Architecture

## 🏗️ High-Level Overview

```
┌─────────────────┐
│   Video Files   │ 9000+ MP4s
│  + Manifest CSV │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                    TRACKER APP                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. INGEST                                       │  │
│  │     - Read CSV                                   │  │
│  │     - Validate paths                             │  │
│  │     - Create jobs                                │  │
│  └──────────┬───────────────────────────────────────┘  │
│             ▼                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  2. PREPROCESS                                   │  │
│  │     - Normalize video (fps, size)                │  │
│  │     - Extract ROI                                │  │
│  │     - Trim dead frames (optional)                │  │
│  └──────────┬───────────────────────────────────────┘  │
│             ▼                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  3. TRACKING                                     │  │
│  │     - Multi-pass extraction:                     │  │
│  │       • Pose (body/arms)                         │  │
│  │       • Hands (21 landmarks × 2)                 │  │
│  │       • Face (468 landmarks → features)          │  │
│  └──────────┬───────────────────────────────────────┘  │
│             ▼                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  4. POSTPROCESS                                  │  │
│  │     - Temporal smoothing (EMA, clamp)            │  │
│  │     - Outlier removal                            │  │
│  │     - Confidence gating                          │  │
│  │     - Quality scoring                            │  │
│  └──────────┬───────────────────────────────────────┘  │
│             ▼                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  5. STORE                                        │  │
│  │     - Supabase (metadata, status)                │  │
│  │     - Disk (tracking data, parquet/jsonl)        │  │
│  └──────────┬───────────────────────────────────────┘  │
│             ▼                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  6. EXPORT (Phase 2.1)                           │  │
│  │     - MetaHuman mapping                          │  │
│  │     - Unreal import scripts                      │  │
│  │     - AnimSequence-ready packages                │  │
│  └──────────┬───────────────────────────────────────┘  │
└─────────────┼───────────────────────────────────────────┘
              ▼
     ┌─────────────────┐
     │  Export folder  │  per-word packages
     │  + index.json   │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ Unreal Engine   │  Import scripts
     │  + MetaHuman    │  → AnimSequence
     └─────────────────┘
```

---

## 📦 Component Breakdown

### 1. INGEST (`tracker_app/ingest/`)

**Purpose**: Read manifest and create processing jobs.

#### Components:
- **`manifest_reader.py`**
  - Parse CSV (autodetect delimiter, encoding)
  - Normalize text (NFC for æøå)
  - Validate `local_path` exists
  - Return list of records

- **`job_builder.py`**
  - Create/update `videos` table entries
  - Create `jobs` table entries (status=queued)
  - Handle duplicates (SHA1 hash for deduplication)

#### Dataflow:
```
CSV → validate → normalize → DB (videos + jobs)
```

#### Error handling:
- Missing files → `jobs.status = missing_file`
- Duplicate videos → reuse existing `video_id`
- Malformed CSV → log error, skip row

---

### 2. PREPROCESS (`tracker_app/preprocess/`)

**Purpose**: Normalize videos for consistent tracking.

#### Components:
- **`ffmpeg_utils.py`**
  - Extract metadata (fps, duration, width, height)
  - Decode video to frame sequence
  - Re-encode to standard format (optional)

- **`normalize.py`**
  - Target FPS (e.g., 25)
  - Target resolution (e.g., 720p for internal work)
  - Color normalization (mild histogram equalization)

- **`roi.py`**
  - Detect person bounding box (MediaPipe Pose detection)
  - Stabilize ROI across frames (smooth box movement)
  - Crop video to ROI (optional, for tracking efficiency)

#### Dataflow:
```
Video → metadata → normalize → ROI → cached frames/video
```

#### Caching:
- Preprocessed videos cached in `CACHE_DIR`
- Skip preprocessing if cache exists and video unchanged (check SHA1)

---

### 3. TRACKING (`tracker_app/tracking/`)

**Purpose**: Extract pose, hand, and face landmarks per frame.

#### Architecture: Provider Pattern

```python
# base.py
class TrackingProvider(ABC):
    @abstractmethod
    def track_frame(self, frame: np.ndarray) -> TrackingResult:
        pass
```

#### Providers (Phase 1):
- **`mediapipe_provider.py`**
  - Pose: MediaPipe Pose (33 landmarks)
  - Hands: MediaPipe Hands (21 × 2 landmarks)
  - Face: MediaPipe FaceMesh (468 landmarks)

#### Providers (Phase 2):
- **`rtmpose_provider.py`** (body)
- **`mmpose_provider.py`** (whole-body)
- **`ensemble_provider.py`** (combine multiple)

#### Dataflow:
```
Frame → Provider → TrackingResult (pose + hands + face + confidence)
```

#### TrackingResult structure:
```python
@dataclass
class TrackingResult:
    pose_2d: List[Landmark2D]
    hands_2d: Dict[str, List[Landmark2D]]  # {"left": [...], "right": [...]}
    face_2d: List[Landmark2D]
    bbox_person: BBox
    confidence: Dict[str, float]  # {"pose": 0.95, "hands": 0.87, "face": 0.92}
```

---

### 4. POSTPROCESS (`tracker_app/postprocess/`)

**Purpose**: Stabilize tracking and score quality.

#### Components:
- **`smoothing.py`**
  - EMA filter (configurable α per signal type)
  - Velocity clamp (max deg/pixel per frame)
  - Confidence-weighted smoothing
  - Gap filling (≤3 frames)

- **`quality.py`**
  - Hand visibility ratio
  - Face detection coverage
  - Tracking stability (jitter metric)
  - Overall score 0..1
  - List of issues (e.g., "left_hand_missing_30%")

#### Dataflow:
```
Raw tracking → smooth → quality_score → final tracking
```

#### Smoothing strategy (EMA):
```python
x_smooth[t] = α * x[t] + (1-α) * x_smooth[t-1]
```
- **α = 0.3** for wrists (more smooth)
- **α = 0.55** for fingers (more responsive)
- **α = 0.4** for face (balanced)

#### Quality score formula:
```
score = 0.4 * hand_visibility 
      + 0.3 * tracking_stability
      + 0.2 * face_coverage
      + 0.1 * resolution_factor
```

---

### 5. STORE (`tracker_app/store/`)

**Purpose**: Persist tracking data and metadata.

#### Components:
- **`supabase_store.py`**
  - Insert/update `videos`, `jobs`, `tracks` tables
  - Transaction support
  - Retry logic for transient failures

- **`disk_store.py`**
  - Write tracking data to JSONL.gz or Parquet
  - Atomic writes (temp file → rename)
  - Verify writes (checksum)

#### Dataflow:
```
Tracking + metadata → Supabase (metadata) + Disk (data)
```

#### Storage locations:
- **Metadata**: Supabase (`videos`, `jobs`, `tracks`)
- **Tracking data**: `workspace/tracks/<video_id>/tracking.jsonl.gz`
- **Exports**: `workspace/exports/<word>/<filename_base>/`

---

### 6. EXPORT (`tracker_app/export/`)

**Purpose**: Generate Unreal-ready packages.

#### Components (Phase 2.1):
- **`export_unreal_package.py`**
  - Read tracking v2
  - Apply MetaHuman mapping
  - Generate `unreal_import.py`
  - Write `meta.json`, `index_entry.json`

- **`formats.py`**
  - Define tracking v1 and v2 formats
  - Version migrations

#### Dataflow:
```
Tracking v2 → MetaHuman mapping → Export package
```

#### Export package structure:
```
exports/
  <word>/
    <filename_base>/
      tracking_v2.jsonl.gz
      meta.json
      metahuman_mapping.json
      unreal_import.py
      index_entry.json
```

---

## 🗄️ Database Architecture (Supabase/Postgres)

### Schema overview:

```sql
videos (
  id uuid PRIMARY KEY,
  word text NOT NULL,
  filename text NOT NULL,
  remote_url text,
  local_path text NOT NULL,
  sha1 text,
  duration_s float,
  fps float,
  width int,
  height int,
  created_at timestamptz DEFAULT now()
)

jobs (
  id uuid PRIMARY KEY,
  video_id uuid REFERENCES videos(id),
  status text NOT NULL,  -- queued|processing|done|failed|missing_file
  error text,
  started_at timestamptz,
  finished_at timestamptz,
  quality_score float,
  frames int,
  export_path text,
  created_at timestamptz DEFAULT now()
)

tracks (
  id uuid PRIMARY KEY,
  video_id uuid REFERENCES videos(id),
  provider text NOT NULL,  -- e.g., "mediapipe", "rtmpose"
  format_version text NOT NULL,  -- e.g., "v1", "v2"
  data_path text NOT NULL,
  created_at timestamptz DEFAULT now()
)
```

### Indexes:
```sql
CREATE INDEX idx_videos_word ON videos(word);
CREATE INDEX idx_videos_filename ON videos(filename);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_video_id ON jobs(video_id);
CREATE INDEX idx_tracks_video_id ON tracks(video_id);
```

---

## 🔄 Processing Workflow

### Job lifecycle:

```
queued → processing → (done | failed)
```

### State transitions:

1. **queued**: Job created, waiting for processing
2. **processing**: Currently being tracked
3. **done**: Successfully completed, tracking saved
4. **failed**: Error occurred, see `jobs.error`
5. **missing_file**: Video file not found

### Resume capability:

```python
# CLI: run --resume
SELECT * FROM jobs 
WHERE status IN ('queued', 'failed') 
ORDER BY created_at
```

---

## 🧩 Module Dependencies

```
cli.py
  ↓
ingest/
  ↓
preprocess/  →  ffmpeg_utils
  ↓
tracking/    →  models (MediaPipe, etc.)
  ↓
postprocess/ →  smoothing, quality
  ↓
store/       →  supabase_store, disk_store
  ↓
export/      →  unreal export (Phase 2.1)
```

---

## 🎛️ Configuration Management

### Configuration sources (priority order):
1. CLI arguments (highest)
2. Environment variables (`.env`)
3. Config file (`config.py` defaults)

### Key config values:
```python
# .env
SUPABASE_DB_URL=postgresql://postgres:postgres@localhost:54322/postgres
WORKSPACE_DIR=D:\tegnspråk\workspace
EXPORT_DIR=D:\tegnspråk\workspace\exports
CACHE_DIR=D:\tegnspråk\workspace\cache
LOG_LEVEL=INFO

# Tracking config
TRACKING_PROVIDER=mediapipe  # or: rtmpose, ensemble
EMA_ALPHA_WRIST=0.35
EMA_ALPHA_FINGERS=0.55
EMA_ALPHA_FACE=0.40
VELOCITY_CLAMP_DEG=18.0
MIN_CONFIDENCE=0.60

# Export config
EXPORT_FPS=25
UNREAL_ASSET_PATH=/Game/NSL/Animations
```

---

## 🚀 Performance Considerations

### Bottlenecks:
1. **Video decoding** (I/O bound)
   - Solution: SSD + FFmpeg hardware decoding
2. **Tracking models** (GPU bound)
   - Solution: Batch inference, reuse models
3. **Database writes** (I/O bound)
   - Solution: Batch inserts, async writes

### Optimization strategies:

#### Batch processing:
```python
# Process N videos in parallel (separate processes to avoid GIL)
with Pool(processes=4) as pool:
    pool.map(process_video, video_list)
```

#### Model reuse:
```python
# Reuse loaded models across videos
provider = MediaPipeProvider()
for video in videos:
    results = provider.track_video(video)
```

#### Async DB writes:
```python
# Write to DB asynchronously
await supabase_store.update_job_async(job_id, status="done")
```

---

## 🔌 Extensibility Points

### Add new tracking provider:
1. Implement `TrackingProvider` interface
2. Add to `tracking/` folder
3. Register in config

### Add new export format:
1. Define format in `export/formats.py`
2. Implement exporter in `export/`
3. Add CLI command

### Add new database backend:
1. Implement store interface
2. Add to `store/` folder
3. Update config

---

## 📏 Canonical Data Model

All tracking providers must output to a **canonical format** for consistency.

### Canonical skeleton (Phase 2+):
```python
{
  "root": {"x": 0.5, "y": 0.6, "z": 0.0},
  "spine_01": {...},
  "spine_02": {...},
  "spine_03": {...},
  "neck": {...},
  "head": {...},
  "clavicle_l": {...},
  "upperarm_l": {...},
  "lowerarm_l": {...},
  "wrist_l": {...},
  "hand_l_thumb_1": {...},
  "hand_l_index_1": {...},
  # ... all fingers
  "clavicle_r": {...},
  # ... right side
}
```

### Canonical face features:
```python
{
  "jaw_open": 0.62,      # 0..1
  "mouth_open": 0.55,
  "mouth_funnel": 0.1,
  "mouth_pucker": 0.0,
  "brow_inner_up": 0.2,
  "eye_blink_l": 0.05,
  "eye_blink_r": 0.03,
  "look_left": 0.0,
  "look_right": 0.0,
  # ... more curves
}
```

---

## 🧪 Testing Architecture

### Test levels:
1. **Unit tests**: Individual functions
2. **Integration tests**: Full pipeline on 1 video
3. **System tests**: Batch processing on 10-100 videos

### Test data:
- `tests/fixtures/` – Small test videos (5-10 seconds)
- `tests/expected/` – Expected outputs

### CI/CD (future):
- GitHub Actions
- Run tests on each commit
- Fail if quality degrades

---

**Neste: [03_TECH_STACK.md](03_TECH_STACK.md) →**
