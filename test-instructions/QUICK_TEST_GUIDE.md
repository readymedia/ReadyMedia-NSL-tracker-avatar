# ⚡ Quick Start: Provider Testing (15 Minutes)

**For immediate testing** - streamlined version

---

## 🚀 Fastest Path to Results

### Step 1: Setup (2 minutes)

```bash
cd c:/Users/magnu/Documents/Antigravity/NSL-avatar
mkdir -p workspace/provider_comparison
cd workspace/provider_comparison
```

### Step 2: Test 3 Videos (10 minutes)

**Simple test videos:**

```bash
# MediaPipe
python -m tracker_app process-video ../video-eksempler/5.mp4 --provider mediapipe --visualize
python -m tracker_app process-video ../video-eksempler/andre.mp4 --provider mediapipe --visualize
python -m tracker_app process-video ../video-eksempler/moss.mp4 --provider mediapipe --visualize

# RTMPose
python -m tracker_app process-video ../video-eksempler/5.mp4 --provider rtmpose --visualize
python -m tracker_app process-video ../video-eksempler/andre.mp4 --provider rtmpose --visualize
python -m tracker_app process-video ../video-eksempler/moss.mp4 --provider rtmpose --visualize
```

### Step 3: Quick Compare (3 minutes)

**Check quality scores:**

```bash
# Find latest tracking outputs
cd workspace/tracks

# List all job folders (sorted by time)
ls -ltr

# Check last 6 meta.json files
# First 3 = MediaPipe, Last 3 = RTMPose

# Example:
cat <uuid-1>/meta.json | grep quality_score  # 5.mp4 MediaPipe
cat <uuid-4>/meta.json | grep quality_score  # 5.mp4 RTMPose

# Compare visually
vlc <uuid-1>/visualization.mp4  # MediaPipe
vlc <uuid-4>/visualization.mp4  # RTMPose
```

### Step 4: Quick Decision (1 minute)

**Fill this table:**

| Video | MediaPipe | RTMPose | Delta | Winner |
|-------|-----------|---------|-------|--------|
| 5.mp4 | 0.___ | 0.___ | +_.__ | ? |
| andre.mp4 | 0.___ | 0.___ | +_.__ | ? |
| moss.mp4 | 0.___ | 0.___ | +_.__ | ? |
| **AVG** | **0.___** | **0.___** | **+_.___** | ? |

**Decision:**
- Delta >10%? → RTMPose is better
- Delta 5-10%? → Both have value
- Delta <5%? → MediaPipe is enough

---

## 📊 Even Faster: Use GUI

### Option 1: GUI Side-by-Side Test

```bash
python scripts/gui.py
```

**Process Tab:**
1. Select: 5.mp4, andre.mp4, moss.mp4
2. Provider: MediaPipe
3. Click "Start Processing"
4. Note quality scores

**Repeat with RTMPose:**
1. Select same videos
2. Provider: RTMPose
3. Click "Start Processing"
4. Compare scores

**Browse Tab:**
- Filter by each video name
- Compare quality metrics
- Download visualizations

---

## 🎯 Quick Analysis Script

**Create:** `quick_compare.py`

```python
#!/usr/bin/env python3
import json
from pathlib import Path
import sys

workspace = Path("workspace/tracks")

# Get all meta.json files
meta_files = sorted(workspace.glob("*/meta.json"), key=lambda x: x.stat().st_mtime)

print("Recent Tracking Results:")
print("-" * 60)

for meta in meta_files[-6:]:  # Last 6 results
    with open(meta) as f:
        data = json.load(f)
    
    provider = "MediaPipe" if "mediapipe" in str(meta) else "RTMPose"  # You'll need to track this
    
    print(f"{data['word']:20} | {data['quality_score']:.3f} | {provider}")

print("-" * 60)
```

**Run:**
```bash
python quick_compare.py
```

---

## ✅ 15-Minute Decision Tree

```
START
  │
  ├─ Process 3 videos (both providers)
  │   └─ 10 minutes
  │
  ├─ Compare quality scores
  │   └─ 2 minutes
  │
  ├─ Watch 2 visualizations
  │   └─ 2 minutes
  │
  └─ Make decision
      └─ 1 minute
         │
         ├─ RTMPose >10% better? → Use RTMPose
         ├─ RTMPose 5-10% better? → Offer both
         └─ RTMPose <5% better? → Use MediaPipe

DONE (15 minutes total)
```

---

## 🎬 Expected Results

### MediaPipe (Baseline):
```
5.mp4:     Quality ~0.75-0.85
andre.mp4: Quality ~0.70-0.80
moss.mp4:  Quality ~0.72-0.82
```

### RTMPose (SOTA):
```
5.mp4:     Quality ~0.80-0.95  (+5-10%)
andre.mp4: Quality ~0.75-0.90  (+5-10%)
moss.mp4:  Quality ~0.78-0.90  (+5-10%)
```

**If these numbers hold:** RTMPose is worth it! ✅

---

## 🚨 Quick Troubleshooting

**RTMPose fails?**
```bash
# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Check MMPose
python -c "import mmpose; print(mmpose.__version__)"

# Try CPU fallback
python -m tracker_app process-video 5.mp4 --provider rtmpose --device cpu
```

**Can't find meta.json?**
```bash
# Check workspace
ls -la workspace/tracks/

# Look for recent folders
find workspace/tracks -name "meta.json" -mtime -1
```

---

## 💡 Pro Tips

1. **Use simple videos first** (5.mp4, andre.mp4, moss.mp4)
2. **Watch visualizations** (more important than numbers!)
3. **Trust your eyes** (if RTMPose looks worse, it IS worse)
4. **3 videos is enough** for initial decision
5. **Full test later** if results are promising

---

## 🎯 Success Criteria (15 min test)

- ✅ 3 videos processed with both providers
- ✅ Quality scores compared
- ✅ 2+ visualizations watched
- ✅ Decision made (RTMPose vs MediaPipe)
- ✅ Ready to commit or test more

---

**This gives you 80% confidence in 20% of the time!** ⚡

Full test (from PROVIDER_TEST_PROTOCOL.md) provides 100% confidence but takes 4-6 hours.

**Start with this quick test, then decide if full test is needed.** 🚀
