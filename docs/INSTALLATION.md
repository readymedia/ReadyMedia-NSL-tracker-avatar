# Installation Guide

## 🔧 Prerequisites

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **FFmpeg** (Must be in PATH)
   ```bash
   ffmpeg -version
   ```

3. **NVIDIA GPU** (Optional but recommended for speed)
   - CUDA Toolkit 11.8 or 12.x
   - Drivers installed

## 📥 Setup

1. **Clone Repository**
   ```bash
   git clone <repo-url>
   cd NSL-avatar
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   - Copy `.env.example` to `.env` (already done if using provided file)
   - Edit `.env` to set your paths if needed:
     ```env
     WORKSPACE_DIR=./workspace
     ```

5. **Initialize Database**
   ```bash
   python -m tracker_app init-db
   ```
   This creates `tracker.db` in your workspace directory.

## 🖥️ Running the GUI
The project now includes a professional GUI (Phase 1.5).

```bash
python -m scripts.gui
```
Open **http://localhost:7860** in your browser.

## 🏃‍♂️ Verification (CLI)

Run the test command to verify everything works:

```bash
python -m tracker_app process-video video-eksempler/5.mp4 --word "test" --visualize
```

If successful, check `workspace/tracks/` for output.
