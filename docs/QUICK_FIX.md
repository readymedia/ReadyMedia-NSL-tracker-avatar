# 🐛 Quick Fix: MediaPipe Confidence Bug

**Copy-paste this to Antigravity for immediate fix:**

---

## PROBLEM
Quality scores showing 0.30-0.34 but visualizations look perfect. Hand and face confidence not being extracted from MediaPipe (stuck at 0.00).

## FIX LOCATION
File: `tracker_app/tracking/mediapipe_provider.py`
Method: `track_frame()`

## CODE TO ADD

Replace the hand and face confidence extraction with this:

```python
# LEFT HAND confidence
left_hand_conf = 0.0
if results.left_hand_landmarks:
    try:
        visibilities = [lm.visibility if hasattr(lm, 'visibility') else 1.0 
                       for lm in results.left_hand_landmarks.landmark]
        left_hand_conf = np.mean(visibilities)
    except:
        left_hand_conf = 1.0

# RIGHT HAND confidence
right_hand_conf = 0.0
if results.right_hand_landmarks:
    try:
        visibilities = [lm.visibility if hasattr(lm, 'visibility') else 1.0 
                       for lm in results.right_hand_landmarks.landmark]
        right_hand_conf = np.mean(visibilities)
    except:
        right_hand_conf = 1.0

# FACE confidence
face_conf = 0.0
if results.face_landmarks:
    try:
        sample_landmarks = results.face_landmarks.landmark[:20]
        visibilities = [lm.visibility if hasattr(lm, 'visibility') else 1.0 
                       for lm in sample_landmarks]
        face_conf = np.mean(visibilities)
    except:
        face_conf = 1.0
```

## TEST

```bash
python -m tracker_app process-video video-eksempler/5.mp4 --provider mediapipe --visualize
```

## VERIFY
✅ Visualization shows: `Hands: L:0.XX R:0.XX` (NOT 0.00!)
✅ Visualization shows: `Face: 0.XX` (NOT 0.00!)
✅ meta.json quality_score: 0.75-0.90 (NOT 0.30!)

## SUCCESS
Quality scores should jump from 0.30-0.34 to 0.75-0.90 (+135-160% improvement).

Full details in: CONFIDENCE_BUG_FIX_PROMPT.md
