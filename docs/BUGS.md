# Bug Tracker – Open NSL Avatar

## 🐛 Active Bugs

*None*

---

## 🔍 Investigation Queue

*Issues that need analysis before fixing*

---

## ✅ Resolved Bugs

## BUG-003: MediaPipe Zero Confidence & Low Quality Scores
**Severity**: High
**Component**: Tracking / Quality
**Phase**: Phase 1.5

### Resolution
- **Issue**: MediaPipe Hand/Face landmarks do not provide `visibility` scores, defaulting to 0.0. This caused quality scores to stay around 0.30 regardless of actual tracking quality.
- **Fix**:
    1. Updated `mediapipe_provider.py` to force confidence to 1.0 when hands/face are present (Presence = Confidence).
    2. Updated `quality.py` to relax hand visibility (average of L/R instead of requiring both) and check stability on both hands.
- **Result**: Quality score for `5.mp4` improved from 0.33 to 0.47 (video likely lacks face/second hand).
**Date Fixed**: 2025-12-16
**Fixed By**: Antigravity

## Bug ID: BUG-002: PyTorch Installation Failure
**Severity**: Critical
**Component**: Environment
**Phase**: Phase 2

### Resolution
User freed up disk space on C:.
Uninstalled corrupted PyTorch.
Installed PyTorch 2.1.2 + CUDA 11.8 and `openmim` dependencies.
Verified import of `mmpose` and `torch.cuda`.
**Date Fixed**: 2025-12-16
**Fixed By**: Antigravity

---

## 📝 Bug Report Template

```
## Bug ID: BUG-001

**Severity**: Critical / High / Medium / Low
**Component**: [e.g., tracking, database, CLI]
**Phase**: [e.g., Phase 1]

### Description
[Clear description of the bug]

### Steps to Reproduce
1. ...
2. ...

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Environment
- OS: [Windows/Linux]
- Python: [version]
- GPU: [model]

### Investigation Notes
[Analysis, root cause, attempted solutions]

### Proposed Solution
[How to fix it]

### Resolution
[What was done]
Date Fixed: [date]
Fixed By: [person]
Commit: [commit hash]
```
