# 📦 Deployment Guide

**Project**: ReadyMedia NSL Avatar Tracker
**Version**: 0.2.0 (Phase 2)
**Date**: 2025-12-16

This guide details how to clone, install, and run the system on a **fresh Production PC** (preferably with a strong NVIDIA GPU).

---

## 🛠️ 1. Hardware Requirements

*   **OS**: Windows 10/11 (Recommended) or Linux (Ubuntu 22.04).
*   **GPU**: NVIDIA GeForce RTX 3060 or better (8GB+ VRAM recommended for RTMPose).
*   **CPU**: Modern multi-core (i7/Ryzen 7).
*   **RAM**: 16GB+.
*   **Storage**: 10GB+ free space (Models are large).

### 🖥️ 2. Prerequisite Software

Before cloning the repo, ensure these are installed on the Production PC:

1.  **Git**: [Download Git](https://git-scm.com/downloads)
2.  **Python 3.11**: [Download Python](https://www.python.org/downloads/release/python-3110/)
    *   *Important*: Check "Add Python to PATH" during install.
3.  **CUDA Toolkit 11.8**: [Download Archive](https://developer.nvidia.com/cuda-11-8-0-download-archive)
    *   *Critical*: Do NOT install CUDA 12.x unless you know how to map PyTorch versions manually. Use 11.8 for stability with our scripts.
    *   *Check*: Run `nvcc --version` in CMD after install.

---

## 🚀 3. Installation Steps

### Step A: Clone Repository
Open PowerShell or Terminal:

```bash
cd Documents
git clone https://github.com/readymedia/ReadyMedia-NSL-tracker-avatar.git
cd ReadyMedia-NSL-tracker-avatar
```

### Step B: Create Virtual Environment
Isolate dependencies to avoid conflicts.

```bash
python -m venv .venv
.\.venv\Scripts\activate
# You should see (.venv) at the start of your line
```

### Step C: Install Dependencies (The "Golden Path")
We have a verified installation order. **Do not use `pip install -r requirements.txt` directly for GPU**.

1.  **Install Core Libraries**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install PyTorch with CUDA**:
    ```bash
    pip uninstall torch torchvision torchaudio -y
    pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
    ```

3.  **Install OpenMMLab (RTMPose)**:
    Run our auto-setup script. It handles the complex versions:
    ```bash
    python scripts/setup_phase2.py
    ```

    *If that fails, run manually:*
    ```bash
    pip install -U openmim
    mim install mmengine
    mim install "mmcv==2.1.0"
    mim install "mmpose>=1.3.0"
    mim install mmdet
    ```

---

## 🎮 4. Running the System

### Option A: The GUI (Recommended)
This starts the web interface at `http://localhost:7860`.

```bash
.\.venv\Scripts\activate
python -m scripts.gui
```

### Option B: The CLI (Automated/Batch)
Good for processing thousands of videos overnight.

```bash
# Process a single video
python -m tracker_app process-video "C:/path/to/video.mp4" --provider rtmpose --visualize

# Process a folder
# (Script coming in Phase 3)
```

---

## 🌩️ 5. Troubleshooting Common Issues

### "CUDA not available"
*   **Symptom**: RTMPose runs very slow (on CPU).
*   **Fix**: Run `python -c "import torch; print(torch.cuda.is_available())"`. If `False`, reinstall PyTorch using the command in "Step C.2".

### "ImportError: mmcv"
*   **Symptom**: Crash when starting RTMPose.
*   **Fix**: Ensure `mmcv` matches your CUDA version. Try `mim uninstall mmcv` then `mim install mmcv==2.1.0`.

### "Disk Full"
*   **Symptom**: Crash during model download.
*   **Fix**: MMPose stores checkpoints in `C:\Users\YourUser\.cache\torch`. Clear it if needed.

---

## 📡 6. Git Workflow

**Repository**: `https://github.com/readymedia/ReadyMedia-NSL-tracker-avatar`

**Pushing Changes**:
```bash
git config user.name "ReadyMedia"
git config user.email "magnus@readymedia.no"

git add .
git commit -m "Update: Phase 2 Complete (RTMPose Integrated)"
git push origin main
```
