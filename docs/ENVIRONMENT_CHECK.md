# Environment Verification Checklist

Before starting implementation, verify:

## ✅ System Requirements

- [ ] Windows 10/11 or Linux
- [ ] Python 3.11+ installed
- [ ] pip and venv available
- [ ] Git installed

## ✅ GPU & CUDA (for Phase 2+)

- [ ] NVIDIA GPU present
- [ ] CUDA 11.8 or 12.x installed
- [ ] `nvidia-smi` command works
- [ ] cuDNN installed (optional)

## ✅ External Tools

- [ ] FFmpeg installed and in PATH
- [ ] `ffmpeg -version` works
- [ ] `ffprobe` available

## ✅ Disk Space

- [ ] At least 50 GB free (for workspace)
- [ ] Fast SSD (recommended)

## ✅ Project Files

- [ ] All 11 documentation files present
- [ ] All 14 test videos in video-eksempler/
- [ ] Can open and read video files

## ✅ Python Dependencies (after setup)

- [ ] Can `import cv2`
- [ ] Can `import mediapipe`
- [ ] Can `import pandas`
- [ ] All requirements.txt packages installed
