# 03 – Technology Stack

## 🐍 Python Core

### Version
- **Python 3.11+** (required)
  - Type hints support
  - Performance improvements
  - Match statement (nice-to-have)

### Environment
- **Poetry** eller **uv** (anbefalt) eller **pip + venv**
- Virtual environment obligatorisk

---

## 📚 Core Dependencies

### CLI & Application
```toml
[tool.poetry.dependencies]
typer = "^0.9.0"           # Modern CLI framework
rich = "^13.7.0"           # Beautiful terminal output
pydantic = "^2.5.0"        # Data validation
python-dotenv = "^1.0.0"   # .env support
tqdm = "^4.66.0"           # Progress bars
```

### Video Processing
```toml
opencv-python = "^4.8.0"   # Video I/O, basic CV
ffmpeg-python = "^0.2.0"   # FFmpeg wrapper
imageio-ffmpeg = "^0.4.9"  # FFmpeg binaries
```

**Alternative**: Call FFmpeg directly via `subprocess` (more control)

### Data Handling
```toml
pandas = "^2.1.0"          # CSV/dataframe ops
pyarrow = "^14.0.0"        # Parquet support
orjson = "^3.9.0"          # Fast JSON (faster than stdlib)
```

### Database
```toml
# Option 1: Supabase (via Python client)
supabase = "^2.3.0"        # Supabase client
psycopg = {extras = ["binary"], version = "^3.1.0"}  # Postgres driver

# Option 2: Just Postgres
psycopg = {extras = ["binary"], version = "^3.1.0"}

# Option 3: SQLite (simplest for MVP)
# (built-in, no dependency)
```

**Recommendation**: Start with SQLite, migrate to Postgres if needed.

---

## 🤖 Machine Learning & Tracking

### MediaPipe (Phase 1 baseline)
```toml
mediapipe = "^0.10.9"      # Pose + Hands + Face
```

**What it includes**:
- Pose: 33 landmarks (BODY_25-ish)
- Hands: 21 landmarks per hand
- Face: 468 landmarks (FaceMesh)

**Pros**: All-in-one, CPU/GPU, well-documented  
**Cons**: Not best-in-class for every task

---

### MMPose / RTMPose (Phase 2, recommended upgrade)

**Option A: MMPose (full suite)**
```toml
mmpose = "^1.3.0"
mmengine = "^0.10.0"
mmcv = "^2.1.0"
```

**Installation**:
```bash
pip install -U openmim
mim install mmengine
mim install "mmcv>=2.0.1"
mim install "mmpose>=1.3.0"
```

**Models to use**:
- **RTMPose-l** (body, 133 keypoints)
- **RTMPose-x** (whole-body including hands)

**Pros**: SOTA, actively maintained, fast inference  
**Cons**: Larger setup

---

**Option B: Just MediaPipe + manual OpenPose** (if you insist)
```bash
# OpenPose (manual install from source, CMake + CUDA)
# Not recommended - outdated and complex
```

---

### NumPy & Math
```toml
numpy = "^1.26.0"          # Core math
scipy = "^1.11.0"          # Filters, optimization (optional)
```

For quaternions (Phase 2.1):
```python
# Built-in or use scipy.spatial.transform.Rotation
from scipy.spatial.transform import Rotation as R
```

---

## 💾 Storage

### Local Database Options

**Option 1: SQLite** (simplest)
```python
import sqlite3  # built-in
```
- Zero config
- File-based: `workspace/tracker.db`
- Perfect for local batch processing

**Option 2: PostgreSQL** (more robust)
```toml
psycopg = {extras = ["binary"], version = "^3.1.0"}
```
- Run locally via Docker:
  ```bash
  docker run -d \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    postgres:16-alpine
  ```

**Option 3: Supabase Local** (if you want full Supabase features)
```bash
npm install -g supabase
supabase init
supabase start
```
- Includes: Postgres + PostgREST + Auth + Realtime
- Overkill for batch pipeline, but nice if building UI later

---

## 🎨 Logging & Debugging

### Logging
```toml
loguru = "^0.7.0"          # Better logging than stdlib
```

**Alternative**: Use `rich.logging` (built into rich)

### Profiling
```python
import cProfile
import pstats
```

Or use **py-spy** for live profiling:
```bash
pip install py-spy
py-spy top -- python -m tracker_app run
```

---

## 🧪 Testing

### Test Framework
```toml
pytest = "^7.4.0"
pytest-cov = "^4.1.0"      # Coverage
pytest-asyncio = "^0.21.0" # Async tests (if using async DB)
```

### Test Data
- Store small test videos in `tests/fixtures/`
- Use real data samples, not synthetic

---

## 🔧 Development Tools

### Type Checking
```toml
mypy = "^1.7.0"
```

Config (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Formatting
```toml
black = "^23.12.0"         # Code formatter
isort = "^5.13.0"          # Import sorter
```

### Linting
```toml
ruff = "^0.1.9"            # Fast linter (replaces flake8, pylint)
```

---

## 🖼️ Computer Vision Extras

### Image Processing
```toml
pillow = "^10.1.0"         # Image I/O
scikit-image = "^0.22.0"   # Advanced image ops (optional)
```

### Visualization (for debugging)
```toml
matplotlib = "^3.8.0"      # Plotting
```

---

## 🎮 Unreal Integration (Phase 2.1)

### Unreal Python API
**Not a pip package** - runs inside Unreal Editor.

**Access**:
1. Enable Python plugin in Unreal
2. Write scripts in `Content/Python/`
3. Execute via:
   ```python
   import unreal
   ```

**Key modules**:
- `unreal.AnimSequence`
- `unreal.EditorAssetLibrary`
- `unreal.AssetToolsHelpers`

**External helpers** (for script generation):
```python
# No external deps, just generate .py files
```

---

## 🚀 GPU & CUDA

### NVIDIA Setup

**CUDA** (required for GPU acceleration):
- CUDA 11.8 (Verified Environment)
- PyTorch 2.1.2 + CUDA 11.8 works best with OpenMMLab.

**Verified Installation**:
```bash
# Core
pip install torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu118
pip install numpy==1.26.4  # Must be < 2.0

# OpenMMLab
pip install -U openmim
mim install mmengine
pip install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.1.0/index.html
mim install "mmpose>=1.3.0"
mim install mmdet
```

**PyTorch** (if using MMPose):
```toml
torch = "^2.1.0+cu118"  # CUDA 11.8
torchvision = "^0.16.0+cu118"
```

Install from PyTorch site:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 📦 Complete `requirements.txt` (MVP)

```txt
# Core
python>=3.11
typer>=0.9.0
rich>=13.7.0
pydantic>=2.5.0
python-dotenv>=1.0.0
tqdm>=4.66.0

# Video
opencv-python>=4.8.0
ffmpeg-python>=0.2.0

# Data
pandas>=2.1.0
pyarrow>=14.0.0
orjson>=3.9.0

# DB (choose one)
psycopg[binary]>=3.1.0  # Postgres
# or just use sqlite3 (built-in)

# ML/Tracking
mediapipe>=0.10.9
numpy>=1.26.0

# Logging
loguru>=0.7.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Development
mypy>=1.7.0
black>=23.12.0
ruff>=0.1.9
```

---

## 📦 Complete `pyproject.toml` (Poetry)

```toml
[tool.poetry]
name = "open-nsl-avatar-tracker"
version = "0.1.0"
description = "NSL video to MetaHuman animation pipeline"
authors = ["Your Name <you@example.com>"]
python = "^3.11"

[tool.poetry.dependencies]
python = "^3.11"
typer = "^0.9.0"
rich = "^13.7.0"
pydantic = "^2.5.0"
python-dotenv = "^1.0.0"
tqdm = "^4.66.0"
opencv-python = "^4.8.0"
ffmpeg-python = "^0.2.0"
pandas = "^2.1.0"
pyarrow = "^14.0.0"
orjson = "^3.9.0"
mediapipe = "^0.10.9"
numpy = "^1.26.0"
loguru = "^0.7.0"
psycopg = {extras = ["binary"], version = "^3.1.0"}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
mypy = "^1.7.0"
black = "^23.12.0"
ruff = "^0.1.9"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 🛠️ System Requirements

### Hardware (minimum)
- **GPU**: NVIDIA RTX 3060 or better (8GB+ VRAM)
- **CPU**: 8+ cores (for parallel preprocessing)
- **RAM**: 32GB (16GB may work but tight)
- **Disk**: 500GB+ SSD
  - ~100GB for videos
  - ~200GB for cache/preprocessing
  - ~100GB for tracking output
  - ~100GB for exports

### Hardware (recommended)
- **GPU**: NVIDIA RTX 4080 or A5000 (16GB VRAM)
- **CPU**: 16+ cores
- **RAM**: 64GB
- **Disk**: 1TB+ NVMe SSD

### Software
- **OS**: Windows 10/11 (primary), Linux (also supported)
- **FFmpeg**: 5.0+ (in PATH)
- **Docker** (if using Supabase local)
- **CUDA**: 11.8 or 12.x
- **Python**: 3.11+

---

## 🔄 Installation Order

### 1. System setup
```bash
# Install CUDA 11.8 or 12.x
# Install cuDNN (optional)
# Install FFmpeg (add to PATH)
```

### 2. Python environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
# or
poetry install
```

### 4. Database setup (if using Postgres)
```bash
docker run -d \
  --name tracker-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine
```

### 5. Environment config
```bash
cp .env.example .env
# Edit .env with your paths
```

### 6. Initialize database
```bash
python -m tracker_app init-db
```

### 7. Test installation
```bash
pytest tests/
```

---

## 🎯 Tech Stack Summary

| Component | Technology | Alternatives |
|-----------|-----------|--------------|
| Language | Python 3.11+ | - |
| CLI | Typer | Click, argparse |
| Video | OpenCV + FFmpeg | PyAV, imageio |
| Tracking (Phase 1) | MediaPipe | - |
| Tracking (Phase 2) | RTMPose/MMPose | OpenPose (outdated) |
| Database | SQLite / Postgres | Supabase (overkill) |
| Data format | JSONL.gz | Parquet (better) |
| Testing | pytest | unittest |
| Typing | mypy | pyright |
| Formatting | black + ruff | - |

---

**Neste: [04_TRACKING_PIPELINE.md](04_TRACKING_PIPELINE.md) →**
