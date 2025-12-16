# 🧪 Testing Strategy

**Version**: 0.2.0 (Phase 2)
**Last Updated**: 2025-12-16

This document outlines how we validate the correctness and performance of the NSL Avatar system.

---

## 🎯 Testing Levels

### 1. Unit Tests (Functionality)
*   **Goal**: Ensure individual functions work (e.g., "Does the quality scorer calculate correctly?").
*   **Tools**: `pytest`.
*   **Location**: `tests/`.
*   **Run**: `pytest tests/`

### 2. Integration Tests (Pipeline)
*   **Goal**: Ensure the whole pipeline runs from Video -> Parquet without crashing.
*   **Method**: "Smoke Test".
*   **Command**:
    ```bash
    python -m tracker_app process-video video-eksempler/5.mp4 --provider mediapipe
    ```
*   **Success Criteria**: No exceptions, output files created in `workspace/tracks`.

### 3. Validation Tests (Quality)
*   **Goal**: Ensure the AI output is *accurate* enough for a MetaHuman.
*   **Method**: Comparison against Ground Truth (or SOTA baseline).
*   **Protocol**: See [PROVIDER_TEST_PROTOCOL.md](PROVIDER_TEST_PROTOCOL.md).
*   **Metrics**:
    *   **Jitter**: Frame-to-frame noise.
    *   **Inversion**: Left/Right hand swaps.
    *   **Ghosting**: False positives when hands are out of frame.

---

## 🔍 Validation Checklists

### New Release Checklist
Before pushing `main` branch:
1.  [ ] Clean install environment (`requirements.txt`).
2.  [ ] Run `scripts/setup_phase2.py` (Verify MMPose install).
3.  [ ] Process `5.mp4` with MediaPipe (Verify speed).
4.  [ ] Process `5.mp4` with RTMPose (Verify quality).
5.  [ ] Check `meta.json` quality score > 0.5 for both.
6.  [ ] Open `visualization.mp4` and visually check for "glitches".

### Environment Verification
To verify GPU usage:
```bash
python -c "import torch; print(torch.cuda.is_available())"
# Must return True
```

---

## 🐛 Bug Reporting
See [BUGS.md](BUGS.md) for known issues.
When reporting a bug, include:
1.  Video filename.
2.  Provider used.
3.  Log output (Error message).
4.  Resulting `meta.json`.
