# Development Roadmap – Open NSL Avatar

## 📊 Feature Overview Table

| ID | Feature | Phase | Priority | Difficulty | Status | Assignee |
|----|---------|-------|----------|------------|--------|----------|
| F001 | Project Setup | 0 | P0 | ⭐ Easy | 🟡 In Progress | Antigravity |
| F002 | Documentation Foundation | 0 | P0 | ⭐ Easy | 🟡 In Progress | Antigravity |
| F003 | Database Layer (SQLite) | 1 | P0 | ⭐⭐ Medium | ⏸️ Planned | - |
| F004 | Video Processing (FFmpeg) | 1 | P0 | ⭐ Medium | ⏸️ Planned | - |
| F005 | MediaPipe Tracking | 1 | P0 | ⭐⭐⭐ Hard | ⏸️ Planned | - |
| F006 | Post-Processing (Smoothing) | 1 | P1 | ⭐⭐ Medium | ⏸️ Planned | - |
| F007 | Quality Scoring | 1 | P1 | ⭐⭐ Medium | ⏸️ Planned | - |
| F008 | CLI Interface | 1 | P1 | ⭐ Easy | ⏸️ Planned | - |
| F020 | GUI Foundation | 1.5 | P1 | ⭐⭐ Medium | ✅ Done | - |
| F021 | Live Tracking Preview | 1.5 | P1 | ⭐⭐⭐ Hard | ✅ Done | - |
| F022 | Video Browser | 1.5 | P1 | ⭐⭐ Medium | ✅ Done | - |
| F023 | Dashboard & Analytics | 1.5 | P2 | ⭐⭐ Medium | ✅ Done | - |
| F024 | Batch Processing UI | 1.5 | P1 | ⭐⭐⭐ Hard | ✅ Done | - |
| F025 | Settings Panel | 1.5 | P2 | ⭐ Easy | ✅ Done | - |
| F009 | RTMPose Integration | 2 | P1 | ⭐⭐⭐ Hard | ✅ Done | - |
| F010 | MetaHuman Mapping | 2.1 | P0 | ⭐⭐⭐⭐ Very Hard | ⏸️ Planned | - |
| F011 | Unreal Import Script | 2.1 | P1 | ⭐⭐⭐ Hard | ⏸️ Planned | - |
| F012 | Stop Processing Button | 3 | P1 | ⭐⭐ Medium | ⏸️ Planned | - |
| F013 | Resume Previous Run | 3 | P1 | ⭐⭐⭐ Hard | ⏸️ Planned | - |

**Legend:**
- **Priority**: P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Low)
- **Difficulty**: ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Hard | ⭐⭐⭐⭐ Very Hard
- **Status**: ⏸️ Planned | 🟡 In Progress | ✅ Done | ❌ Blocked

---

## Phase 0: Foundation (Week 1)

**Goal**: Solid project structure, documentation, basic tooling

### F001: Project Setup ⭐ Easy [P0]
- [x] Read all documentation
- [x] Create docs/ structure
- [x] Setup Python environment
- [x] Install dependencies
- [x] Verify FFmpeg, CUDA

### F002: Documentation Foundation ⭐ Easy [P0]
- [x] Create README.md
- [x] Create ROADMAP.md
- [x] Create BUGS.md
- [x] Create INSTALLATION.md
- [x] Create TESTING.md

---

## Phase 1: MVP Pipeline (Week 2-3)

**Goal**: Working end-to-end pipeline on test videos

### F003: Database Layer ⭐⭐ Medium [P0]
**Prerequisites**: F001, F002
**Estimated Time**: 4 hours

Tasks:
- [x] Implement SQLite wrapper (db.py)
- [x] Create schema.sql
- [x] Add migration support
- [x] Unit tests for DB operations

**Success Criteria**:
- ✅ Can create database
- ✅ Can insert/query videos and jobs
- ✅ Tests pass

---

### F004: Video Processing ⭐⭐ Medium [P0]
**Prerequisites**: F003
**Estimated Time**: 6 hours

Tasks:
- [x] FFmpeg metadata extraction
- [x] Frame iterator implementation
- [x] Video normalization (optional)
- [x] Test on all 14 sample videos

**Success Criteria**:
- ✅ Extract metadata from all test videos
- ✅ Frame extraction works
- ✅ Handle Norwegian filenames (æøå)

---

### F005: MediaPipe Tracking ⭐⭐⭐ Hard [P0]
**Prerequisites**: F004
**Estimated Time**: 12 hours

Tasks:
- [x] Implement TrackingProvider interface
- [x] MediaPipe pose tracking
- [x] MediaPipe hands tracking (21 landmarks x 2)
- [x] MediaPipe face mesh
- [x] Confidence scoring
- [x] Test on 3 simple videos first

**Success Criteria**:
- ✅ Track 1 video end-to-end
- ✅ Output valid Parquet + JSONL
- ✅ Landmarks visible in data

---

### F006: Post-Processing ⭐⭐ Medium [P1]
**Prerequisites**: F005
**Estimated Time**: 8 hours

Tasks:
- [x] EMA smoothing implementation
- [x] Velocity clamping
- [x] Outlier removal

**Success Criteria**:
- ✅ Reduced jitter in output
- ✅ Configurable smoothing parameters

### F007: Quality Scoring ⭐⭐ Medium [P1]
**Prerequisites**: F005
**Estimated Time**: 6 hours

Tasks:
- [x] Compute hand visibility ratio
- [x] Compute tracking confidence
- [x] Store quality metrics in DB/meta.json

**Success Criteria**:
- ✅ Videos flagged as good/bad automatically

---


---

## Phase 1.5: Professional GUI (Week 3)

**Goal**: Professional Gradio-based interface for processing, browsing, and monitoring

**Product Name**: ReaddyMedia - NSL Avatar

### F020: GUI Foundation ⭐⭐ Medium [P1]
**Prerequisites**: F001-F019 (Phase 1 complete)
**Estimated Time**: 4 hours

Tasks:
- [x] Create `scripts/gui.py` with Gradio
- [x] Implement custom CSS styling (ReaddyMedia theme)
- [x] Setup tab structure (Process / Browse / Dashboard / Settings)
- [x] Basic layout and navigation

**Success Criteria**:
- ✅ GUI launches on localhost:7860
- ✅ All 4 tabs render correctly
- ✅ ReaddyMedia branding applied

---

### F021: Live Tracking Preview ⭐⭐⭐ Hard [P1]
**Prerequisites**: F020
**Estimated Time**: 6 hours

Tasks:
- [x] Implement real-time frame annotation
- [x] Color-coded confidence visualization:
  - 🟢 Green dots: High confidence (>0.7)
  - 🟡 Yellow dots: Medium (0.5-0.7)
  - 🔴 Red dots: Low (<0.5)
- [x] Draw hand connections and skeleton
- [x] Add info overlay (pose/hands/face confidence)
- [x] Update preview every N frames during processing

**Success Criteria**:
- ✅ Can see tracking in real-time during processing
- ✅ Landmarks drawn correctly with confidence colors
- ✅ Preview updates smoothly (no lag)
- ✅ Metrics overlay shows current frame stats

**Implementation Notes**:
- Use `draw_tracking_overlay()` from GUI spec
- Queue-based frame passing (max 5 frames buffered)
- Update every 5 frames to avoid slowdown

---

### F022: Video Browser ⭐⭐ Medium [P1]
**Prerequisites**: F020
**Estimated Time**: 4 hours

Tasks:
- [x] Load processed videos from database
- [x] Filterable table (search, quality threshold)
- [ ] Video preview with annotated overlay
- [x] Quality detail panel (scores, issues)
- [ ] Download buttons (tracking data, visualization)

**Success Criteria**:
- ✅ Can browse all processed videos
- ✅ Search works correctly
- ✅ Quality filtering functional
- ✅ Can preview and download results

---

### F023: Dashboard & Analytics ⭐⭐ Medium [P2]
**Prerequisites**: F020
**Estimated Time**: 5 hours

Tasks:
- [x] Statistics cards (Total/Done/Failed/Pending)
- [x] Quality distribution histogram (Plotly)
- [ ] Processing time bar chart
- [ ] Common issues summary
- [ ] Storage usage indicator
- [ ] Recent activity log
- [ ] Export report functionality (PDF/CSV)

**Success Criteria**:
- ✅ Dashboard shows real-time stats
- ✅ Charts render correctly
- ✅ Can export reports

---

### F024: Batch Processing UI ⭐⭐⭐ Hard [P1]
**Prerequisites**: F020, F021
**Estimated Time**: 5 hours

Tasks:
- [x] Video selection checklist
- [x] Configurable processing settings
- [x] Start/Pause/Stop controls
- [ ] Progress bar with ETA
- [x] Live log output
- [x] Integration with CLI backend

**Success Criteria**:
- ✅ Can select multiple videos
- ✅ Processing runs with live preview
- ✅ Can pause/stop processing
- ✅ Progress accurate
- ✅ Log shows all events

---

### F025: Settings Panel ⭐ Easy [P2]
**Prerequisites**: F020
**Estimated Time**: 2 hours

Tasks:
- [x] Path configuration (workspace, videos)
- [x] Video processing settings
- [x] Tracking configuration (provider, confidence)
- [ ] Smoothing sliders
- [ ] Output options
- [ ] Save/Load settings

**Success Criteria**:
- ✅ All settings accessible
- ✅ Settings persist to .env
- ✅ Can reset to defaults

---

## Phase 2: Refinement & Scaling (Week 4-6)

**Goal**: High-quality tracking and batch processing

### F009: RTMPose Integration ⭐⭐⭐ Hard [P1]
**Prerequisites**: F005
**Estimated Time**: 20 hours
**Status**: ✅ Complete (PyTorch 2.1.2)

Tasks:
- [x] Implement RTMPoseProvider (Code Complete)
- [x] Setup MMPose/RTMPose environment (PyTorch 2.1.2 + CUDA 11.8)
- [x] Compare quality with MediaPipe

**Success Criteria**:
- ✅ Superior body tracking stability

---

## Phase 2.1: MetaHuman Integration (Week 7-8)

**Goal**: Import to Unreal Engine

### F010: MetaHuman Mapping ⭐⭐⭐⭐ Very Hard [P0]
**Prerequisites**: F009
**Estimated Time**: 25 hours

Tasks:
- [ ] Map 2D/3D landmarks to Control Rig controls
- [ ] Map FaceMesh to ArKit face curves
- [ ] Handle rotations (wrist, arm)

### F011: Unreal Import Script ⭐⭐⭐ Hard [P1]
**Prerequisites**: F010
**Estimated Time**: 15 hours

Tasks:
- [ ] Python script for Unreal Editor
- [ ] Import JSONL/Parquet to Animation Sequence

