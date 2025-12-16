# 🧪 Provider Comparison Test Protocol

## Step 1: Create Test Directory Structure

```bash
# Navigate to workspace
cd workspace

# Create comparison test folder
mkdir -p provider_comparison
cd provider_comparison

# Create subfolders
mkdir -p mediapipe rtmpose comparison_data visualizations reports
```

**Result:**
```
workspace/provider_comparison/
├── mediapipe/           # MediaPipe tracking outputs
├── rtmpose/             # RTMPose tracking outputs
├── comparison_data/     # Quality metrics, CSVs
├── visualizations/      # Side-by-side comparisons
└── reports/             # Final analysis documents
```

---

## Step 2: Select Test Videos

### Criteria for Test Set:

**Choose 7-10 videos** that represent different difficulty levels:

| Category | Videos | Why |
|----------|--------|-----|
| **Simple** | 5.mp4, andre.mp4 | Baseline validation |
| **Medium** | moss.mp4, ANB.mp4 | Common complexity |
| **Complex** | 3-2-1-haandballformasjon.mp4, bistandsadvokat.mp4 | Multi-word phrases |
| **Challenging** | argument-2.mp4, motta-gaver-ol.mp4 | Fast motion, occlusion |

### Create Test Manifest:

```bash
# Create test_videos.txt
cat > test_videos.txt << 'EOF'
5.mp4
5-000-m.mp4
andre.mp4
moss.mp4
ANB.mp4
yoghurt-2.mp4
3-2-1-haandballformasjon.mp4
bistandsadvokat.mp4
argument-2.mp4
motta-gaver-ol.mp4
EOF
```

---

## Step 3: Batch Processing Script

### Create Automated Test Runner:

**File**: `workspace/provider_comparison/run_comparison.sh`

```bash
#!/bin/bash

# Provider Comparison Test Runner
# Usage: bash run_comparison.sh

set -e  # Exit on error

# Configuration
PROJECT_ROOT="c:/Users/magnu/Documents/Antigravity/NSL-avatar"
VIDEO_DIR="$PROJECT_ROOT/video-eksempler"
TEST_VIDEOS="test_videos.txt"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 Provider Comparison Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Process with MediaPipe
echo -e "${GREEN}[1/3] Processing with MediaPipe...${NC}"
mkdir -p mediapipe
cd "$PROJECT_ROOT"

while IFS= read -r video; do
    echo -e "\n${BLUE}Processing: $video (MediaPipe)${NC}"
    
    python -m tracker_app process-video \
        "$VIDEO_DIR/$video" \
        --provider mediapipe \
        --visualize \
        --output-dir "workspace/provider_comparison/mediapipe/$video" \
        2>&1 | tee "workspace/provider_comparison/mediapipe/${video%.mp4}_log.txt"
    
    # Extract quality score
    if [ -f "workspace/provider_comparison/mediapipe/$video/meta.json" ]; then
        echo "✅ $video completed (MediaPipe)"
    else
        echo "❌ $video failed (MediaPipe)"
    fi
done < "workspace/provider_comparison/$TEST_VIDEOS"

echo -e "\n${GREEN}MediaPipe processing complete!${NC}\n"

# Step 2: Process with RTMPose
echo -e "${GREEN}[2/3] Processing with RTMPose...${NC}"
cd "$PROJECT_ROOT"

while IFS= read -r video; do
    echo -e "\n${BLUE}Processing: $video (RTMPose)${NC}"
    
    python -m tracker_app process-video \
        "$VIDEO_DIR/$video" \
        --provider rtmpose \
        --visualize \
        --output-dir "workspace/provider_comparison/rtmpose/$video" \
        2>&1 | tee "workspace/provider_comparison/rtmpose/${video%.mp4}_log.txt"
    
    # Extract quality score
    if [ -f "workspace/provider_comparison/rtmpose/$video/meta.json" ]; then
        echo "✅ $video completed (RTMPose)"
    else
        echo "❌ $video failed (RTMPose)"
    fi
done < "workspace/provider_comparison/$TEST_VIDEOS"

echo -e "\n${GREEN}RTMPose processing complete!${NC}\n"

# Step 3: Collect metrics
echo -e "${GREEN}[3/3] Collecting comparison metrics...${NC}"
cd "$PROJECT_ROOT"

python workspace/provider_comparison/collect_metrics.py

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Test suite complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Results saved to: workspace/provider_comparison/"
echo "View report: workspace/provider_comparison/reports/comparison_report.html"
```

**Make executable:**
```bash
chmod +x workspace/provider_comparison/run_comparison.sh
```

---

## Step 4: Metrics Collection Script

### Create Automated Data Harvester:

**File**: `workspace/provider_comparison/collect_metrics.py`

```python
#!/usr/bin/env python3
"""
Collect and compare metrics from MediaPipe and RTMPose tracking results.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Configuration
BASE_DIR = Path(__file__).parent
MEDIAPIPE_DIR = BASE_DIR / "mediapipe"
RTMPOSE_DIR = BASE_DIR / "rtmpose"
OUTPUT_DIR = BASE_DIR / "comparison_data"

OUTPUT_DIR.mkdir(exist_ok=True)


def load_meta(meta_path: Path) -> Dict:
    """Load meta.json file"""
    try:
        with open(meta_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading {meta_path}: {e}")
        return {}


def collect_provider_metrics(provider_dir: Path) -> List[Dict]:
    """Collect metrics for a specific provider"""
    metrics = []
    
    # Find all meta.json files
    for meta_path in provider_dir.rglob("meta.json"):
        video_name = meta_path.parent.name
        data = load_meta(meta_path)
        
        if data:
            metrics.append({
                'video': video_name,
                'quality_score': data.get('quality_score', 0.0),
                'hand_visibility': data.get('hand_visibility', 0.0),
                'face_coverage': data.get('face_coverage', 0.0),
                'tracking_stability': data.get('tracking_stability', 0.0),
                'avg_confidence': data.get('avg_confidence', 0.0),
                'frames': data.get('frames', 0),
                'duration_s': data.get('duration_s', 0.0),
                'processing_time_s': data.get('processing_time_s', 0.0),
            })
    
    return metrics


def compare_providers(mp_metrics: List[Dict], rtm_metrics: List[Dict]) -> List[Dict]:
    """Compare MediaPipe vs RTMPose metrics"""
    comparisons = []
    
    # Match videos
    mp_dict = {m['video']: m for m in mp_metrics}
    rtm_dict = {m['video']: m for m in rtm_metrics}
    
    common_videos = set(mp_dict.keys()) & set(rtm_dict.keys())
    
    for video in sorted(common_videos):
        mp = mp_dict[video]
        rtm = rtm_dict[video]
        
        comparisons.append({
            'video': video,
            'mp_quality': mp['quality_score'],
            'rtm_quality': rtm['quality_score'],
            'quality_delta': rtm['quality_score'] - mp['quality_score'],
            'quality_delta_pct': ((rtm['quality_score'] - mp['quality_score']) / mp['quality_score'] * 100) if mp['quality_score'] > 0 else 0,
            'mp_hand_vis': mp['hand_visibility'],
            'rtm_hand_vis': rtm['hand_visibility'],
            'hand_vis_delta': rtm['hand_visibility'] - mp['hand_visibility'],
            'mp_face_cov': mp['face_coverage'],
            'rtm_face_cov': rtm['face_coverage'],
            'face_cov_delta': rtm['face_coverage'] - mp['face_coverage'],
            'mp_stability': mp['tracking_stability'],
            'rtm_stability': rtm['tracking_stability'],
            'stability_delta': rtm['tracking_stability'] - mp['tracking_stability'],
            'mp_time': mp['processing_time_s'],
            'rtm_time': rtm['processing_time_s'],
            'time_ratio': rtm['processing_time_s'] / mp['processing_time_s'] if mp['processing_time_s'] > 0 else 0,
        })
    
    return comparisons


def save_csv(data: List[Dict], filename: str):
    """Save data to CSV"""
    if not data:
        print(f"⚠️  No data to save for {filename}")
        return
    
    output_path = OUTPUT_DIR / filename
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Saved: {output_path}")


def print_summary(comparisons: List[Dict]):
    """Print summary statistics"""
    if not comparisons:
        print("⚠️  No comparisons available")
        return
    
    print("\n" + "="*60)
    print("📊 COMPARISON SUMMARY")
    print("="*60)
    
    # Overall statistics
    quality_deltas = [c['quality_delta'] for c in comparisons]
    hand_vis_deltas = [c['hand_vis_delta'] for c in comparisons]
    face_cov_deltas = [c['face_cov_delta'] for c in comparisons]
    stability_deltas = [c['stability_delta'] for c in comparisons]
    time_ratios = [c['time_ratio'] for c in comparisons]
    
    print(f"\n📈 Quality Score:")
    print(f"   MediaPipe avg:  {statistics.mean([c['mp_quality'] for c in comparisons]):.3f}")
    print(f"   RTMPose avg:    {statistics.mean([c['rtm_quality'] for c in comparisons]):.3f}")
    print(f"   Avg improvement: {statistics.mean(quality_deltas):+.3f} ({statistics.mean([c['quality_delta_pct'] for c in comparisons]):+.1f}%)")
    
    print(f"\n👐 Hand Visibility:")
    print(f"   MediaPipe avg:  {statistics.mean([c['mp_hand_vis'] for c in comparisons]):.3f}")
    print(f"   RTMPose avg:    {statistics.mean([c['rtm_hand_vis'] for c in comparisons]):.3f}")
    print(f"   Avg improvement: {statistics.mean(hand_vis_deltas):+.3f}")
    
    print(f"\n😊 Face Coverage:")
    print(f"   MediaPipe avg:  {statistics.mean([c['mp_face_cov'] for c in comparisons]):.3f}")
    print(f"   RTMPose avg:    {statistics.mean([c['rtm_face_cov'] for c in comparisons]):.3f}")
    print(f"   Avg improvement: {statistics.mean(face_cov_deltas):+.3f}")
    
    print(f"\n⚡ Processing Speed:")
    print(f"   Avg time ratio: {statistics.mean(time_ratios):.2f}x slower")
    
    print(f"\n🏆 Winner Count:")
    rtm_wins = sum(1 for c in comparisons if c['quality_delta'] > 0)
    mp_wins = sum(1 for c in comparisons if c['quality_delta'] < 0)
    ties = len(comparisons) - rtm_wins - mp_wins
    print(f"   RTMPose better: {rtm_wins}/{len(comparisons)} videos")
    print(f"   MediaPipe better: {mp_wins}/{len(comparisons)} videos")
    print(f"   Tie: {ties}/{len(comparisons)} videos")
    
    # Best/worst cases
    print(f"\n📊 Best Improvements (RTMPose):")
    sorted_comps = sorted(comparisons, key=lambda x: x['quality_delta'], reverse=True)
    for comp in sorted_comps[:3]:
        print(f"   {comp['video']}: {comp['quality_delta']:+.3f} ({comp['quality_delta_pct']:+.1f}%)")
    
    print(f"\n⚠️  Worst Cases (RTMPose worse):")
    for comp in sorted_comps[-3:]:
        if comp['quality_delta'] < 0:
            print(f"   {comp['video']}: {comp['quality_delta']:+.3f} ({comp['quality_delta_pct']:+.1f}%)")
    
    print("\n" + "="*60)


def main():
    """Main execution"""
    print("🔍 Collecting metrics from provider outputs...\n")
    
    # Collect metrics
    print("📊 MediaPipe metrics...")
    mp_metrics = collect_provider_metrics(MEDIAPIPE_DIR)
    print(f"   Found {len(mp_metrics)} results\n")
    
    print("📊 RTMPose metrics...")
    rtm_metrics = collect_provider_metrics(RTMPOSE_DIR)
    print(f"   Found {len(rtm_metrics)} results\n")
    
    if not mp_metrics or not rtm_metrics:
        print("❌ No metrics found! Ensure videos have been processed.")
        return
    
    # Compare
    print("🔬 Comparing providers...")
    comparisons = compare_providers(mp_metrics, rtm_metrics)
    print(f"   {len(comparisons)} videos compared\n")
    
    # Save CSVs
    print("💾 Saving data...")
    save_csv(mp_metrics, "mediapipe_metrics.csv")
    save_csv(rtm_metrics, "rtmpose_metrics.csv")
    save_csv(comparisons, "provider_comparison.csv")
    
    # Print summary
    print_summary(comparisons)
    
    # Generate recommendation
    if comparisons:
        avg_improvement = statistics.mean([c['quality_delta_pct'] for c in comparisons])
        rtm_wins = sum(1 for c in comparisons if c['quality_delta'] > 0)
        
        print("\n" + "="*60)
        print("💡 RECOMMENDATION")
        print("="*60)
        
        if avg_improvement > 10 and rtm_wins > len(comparisons) * 0.7:
            print("✅ USE RTMPose")
            print("   - Significant quality improvement (>10%)")
            print("   - Better on majority of videos")
            print("   - Worth the extra processing time")
        elif avg_improvement > 5:
            print("⚖️  OFFER BOTH OPTIONS")
            print("   - Moderate improvement (5-10%)")
            print("   - Use MediaPipe for speed")
            print("   - Use RTMPose for publication quality")
        else:
            print("⚡ STICK WITH MediaPipe")
            print("   - Minimal improvement (<5%)")
            print("   - Faster processing")
            print("   - Simpler deployment")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
```

**Make executable:**
```bash
chmod +x workspace/provider_comparison/collect_metrics.py
```

---

## Step 5: Visualization Comparison Tool

### Create Side-by-Side Visualization Script:

**File**: `workspace/provider_comparison/create_side_by_side.py`

```python
#!/usr/bin/env python3
"""
Create side-by-side comparison videos of MediaPipe vs RTMPose.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple

# Configuration
BASE_DIR = Path(__file__).parent
MEDIAPIPE_DIR = BASE_DIR / "mediapipe"
RTMPOSE_DIR = BASE_DIR / "rtmpose"
OUTPUT_DIR = BASE_DIR / "visualizations"

OUTPUT_DIR.mkdir(exist_ok=True)


def load_video(video_path: Path) -> Tuple[cv2.VideoCapture, int, int, float]:
    """Load video and return capture object with metadata"""
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    return cap, width, height, fps


def add_label(frame: np.ndarray, text: str, color: Tuple[int, int, int]):
    """Add provider label to frame"""
    height, width = frame.shape[:2]
    
    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (200, 50), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Text
    cv2.putText(frame, text, (20, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    return frame


def create_side_by_side(video_name: str):
    """Create side-by-side comparison video"""
    mp_viz = MEDIAPIPE_DIR / video_name / "visualization.mp4"
    rtm_viz = RTMPOSE_DIR / video_name / "visualization.mp4"
    
    if not mp_viz.exists() or not rtm_viz.exists():
        print(f"⚠️  Skipping {video_name}: visualization missing")
        return
    
    print(f"🎬 Creating comparison: {video_name}")
    
    # Load videos
    mp_cap, mp_w, mp_h, mp_fps = load_video(mp_viz)
    rtm_cap, rtm_w, rtm_h, rtm_fps = load_video(rtm_viz)
    
    # Output settings
    output_width = mp_w + rtm_w
    output_height = max(mp_h, rtm_h)
    fps = min(mp_fps, rtm_fps)
    
    output_path = OUTPUT_DIR / f"{Path(video_name).stem}_comparison.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, 
                          (output_width, output_height))
    
    frame_count = 0
    
    while True:
        ret_mp, frame_mp = mp_cap.read()
        ret_rtm, frame_rtm = rtm_cap.read()
        
        if not ret_mp or not ret_rtm:
            break
        
        # Resize if needed
        if frame_mp.shape != (mp_h, mp_w, 3):
            frame_mp = cv2.resize(frame_mp, (mp_w, mp_h))
        if frame_rtm.shape != (rtm_h, rtm_w, 3):
            frame_rtm = cv2.resize(frame_rtm, (rtm_w, rtm_h))
        
        # Add labels
        frame_mp = add_label(frame_mp, "MediaPipe", (0, 255, 0))
        frame_rtm = add_label(frame_rtm, "RTMPose", (255, 0, 255))
        
        # Combine side-by-side
        combined = np.hstack([frame_mp, frame_rtm])
        
        # Write frame
        out.write(combined)
        frame_count += 1
    
    # Cleanup
    mp_cap.release()
    rtm_cap.release()
    out.release()
    
    print(f"   ✅ Saved: {output_path} ({frame_count} frames)")


def main():
    """Process all videos"""
    print("🎬 Creating side-by-side comparison videos...\n")
    
    # Find all processed videos
    mp_videos = set(d.name for d in MEDIAPIPE_DIR.iterdir() if d.is_dir())
    rtm_videos = set(d.name for d in RTMPOSE_DIR.iterdir() if d.is_dir())
    
    common_videos = mp_videos & rtm_videos
    
    print(f"Found {len(common_videos)} videos to compare\n")
    
    for video in sorted(common_videos):
        try:
            create_side_by_side(video)
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Complete! Comparisons saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
```

---

## Step 6: HTML Report Generator

**File**: `workspace/provider_comparison/generate_report.py`

```python
#!/usr/bin/env python3
"""
Generate HTML report with charts and comparisons.
"""

import csv
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).parent
COMPARISON_CSV = BASE_DIR / "comparison_data" / "provider_comparison.csv"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)


def load_comparison_data() -> List[Dict]:
    """Load comparison CSV"""
    data = []
    with open(COMPARISON_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric strings to floats
            for key in row:
                if key != 'video':
                    try:
                        row[key] = float(row[key])
                    except:
                        pass
            data.append(row)
    return data


def generate_html_report(data: List[Dict]):
    """Generate interactive HTML report"""
    
    # Prepare data for charts
    videos = [d['video'] for d in data]
    mp_quality = [d['mp_quality'] for d in data]
    rtm_quality = [d['rtm_quality'] for d in data]
    quality_delta = [d['quality_delta_pct'] for d in data]
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Provider Comparison Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #2563EB;
            color: white;
        }}
        .positive {{ color: #10B981; font-weight: bold; }}
        .negative {{ color: #EF4444; font-weight: bold; }}
        .neutral {{ color: #6B7280; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Provider Comparison Report</h1>
        <p>MediaPipe vs RTMPose - Tracking Quality Analysis</p>
    </div>
    
    <div class="section">
        <h2>📊 Quality Score Comparison</h2>
        <div id="qualityChart"></div>
    </div>
    
    <div class="section">
        <h2>📈 Improvement Breakdown</h2>
        <div id="deltaChart"></div>
    </div>
    
    <div class="section">
        <h2>📋 Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Video</th>
                    <th>MediaPipe</th>
                    <th>RTMPose</th>
                    <th>Delta</th>
                    <th>Winner</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add table rows
    for d in data:
        delta_class = "positive" if d['quality_delta'] > 0 else "negative" if d['quality_delta'] < 0 else "neutral"
        winner = "RTMPose" if d['quality_delta'] > 0 else "MediaPipe" if d['quality_delta'] < 0 else "Tie"
        
        html += f"""
                <tr>
                    <td>{d['video']}</td>
                    <td>{d['mp_quality']:.3f}</td>
                    <td>{d['rtm_quality']:.3f}</td>
                    <td class="{delta_class}">{d['quality_delta']:+.3f} ({d['quality_delta_pct']:+.1f}%)</td>
                    <td>{winner}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    <script>
        // Quality comparison chart
        var qualityTrace1 = {
            x: """ + str(videos) + """,
            y: """ + str(mp_quality) + """,
            name: 'MediaPipe',
            type: 'bar',
            marker: {color: '#10B981'}
        };
        
        var qualityTrace2 = {
            x: """ + str(videos) + """,
            y: """ + str(rtm_quality) + """,
            name: 'RTMPose',
            type: 'bar',
            marker: {color: '#7C3AED'}
        };
        
        var qualityLayout = {
            barmode: 'group',
            title: 'Quality Scores by Provider',
            xaxis: {title: 'Video'},
            yaxis: {title: 'Quality Score', range: [0, 1]}
        };
        
        Plotly.newPlot('qualityChart', [qualityTrace1, qualityTrace2], qualityLayout);
        
        // Delta chart
        var deltaTrace = {
            x: """ + str(videos) + """,
            y: """ + str(quality_delta) + """,
            type: 'bar',
            marker: {
                color: """ + str(quality_delta) + """,
                colorscale: [
                    [0, '#EF4444'],
                    [0.5, '#6B7280'],
                    [1, '#10B981']
                ],
                cmin: -20,
                cmax: 20
            }
        };
        
        var deltaLayout = {
            title: 'Quality Improvement (RTMPose vs MediaPipe)',
            xaxis: {title: 'Video'},
            yaxis: {title: 'Improvement (%)'},
            shapes: [{
                type: 'line',
                x0: 0,
                x1: 1,
                xref: 'paper',
                y0: 0,
                y1: 0,
                line: {color: 'black', width: 1, dash: 'dash'}
            }]
        };
        
        Plotly.newPlot('deltaChart', [deltaTrace], deltaLayout);
    </script>
</body>
</html>
"""
    
    # Save report
    report_path = REPORT_DIR / "comparison_report.html"
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"✅ Report generated: {report_path}")


def main():
    """Generate report"""
    print("📄 Generating HTML report...\n")
    
    if not COMPARISON_CSV.exists():
        print(f"❌ Comparison data not found: {COMPARISON_CSV}")
        print("   Run collect_metrics.py first!")
        return
    
    data = load_comparison_data()
    generate_html_report(data)
    
    print(f"\n🎉 Report complete!")
    print(f"Open: file:///{REPORT_DIR.absolute()}/comparison_report.html")


if __name__ == "__main__":
    main()
```

---

## Step 7: Master Test Runner

**File**: `workspace/provider_comparison/run_full_test.sh`

```bash
#!/bin/bash

# Master test script - runs entire comparison pipeline

set -e

PROJECT_ROOT="c:/Users/magnu/Documents/Antigravity/NSL-avatar"
cd "$PROJECT_ROOT/workspace/provider_comparison"

echo "🚀 Starting full comparison test suite..."
echo ""

# Step 1: Process videos
echo "⏳ Step 1/4: Processing videos (this may take 1-2 hours)..."
bash run_comparison.sh

# Step 2: Collect metrics
echo ""
echo "⏳ Step 2/4: Collecting metrics..."
python collect_metrics.py

# Step 3: Create visualizations
echo ""
echo "⏳ Step 3/4: Creating side-by-side comparisons..."
python create_side_by_side.py

# Step 4: Generate report
echo ""
echo "⏳ Step 4/4: Generating HTML report..."
python generate_report.py

echo ""
echo "✅ ALL TESTS COMPLETE!"
echo ""
echo "📂 Results:"
echo "   - Metrics: comparison_data/"
echo "   - Videos: visualizations/"
echo "   - Report: reports/comparison_report.html"
echo ""
echo "🌐 Open report in browser:"
echo "   file:///$PWD/reports/comparison_report.html"
```

---

## 🚀 EXECUTION

### Run Complete Test Suite:

```bash
# Navigate to project
cd c:/Users/magnu/Documents/Antigravity/NSL-avatar

# Create test structure
mkdir -p workspace/provider_comparison
cd workspace/provider_comparison

# Copy scripts (from this document)
# - run_comparison.sh
# - collect_metrics.py
# - create_side_by_side.py
# - generate_report.py
# - run_full_test.sh

# Create test video list
cat > test_videos.txt << 'EOF'
5.mp4
5-000-m.mp4
andre.mp4
moss.mp4
ANB.mp4
yoghurt-2.mp4
3-2-1-haandballformasjon.mp4
bistandsadvokat.mp4
argument-2.mp4
motta-gaver-ol.mp4
EOF

# RUN FULL TEST SUITE
bash run_full_test.sh
```

**Expected Duration**: 2-4 hours (depends on GPU and video count)

---

## 📊 ANALYSIS & DECISION

### After Tests Complete:

1. **Open HTML Report**:
   ```bash
   # Windows
   start workspace/provider_comparison/reports/comparison_report.html
   
   # Linux/Mac
   open workspace/provider_comparison/reports/comparison_report.html
   ```

2. **Review Metrics**:
   - Overall quality improvement
   - Per-video improvements
   - Winner count (RTMPose vs MediaPipe)

3. **Watch Side-by-Side Videos**:
   ```bash
   # Open comparison videos
   cd workspace/provider_comparison/visualizations
   # Watch 3-5 comparison videos
   ```

4. **Make Decision**:

   **If RTMPose >15% better on 70%+ videos:**
   → ✅ **USE RTMPose as default**
   
   **If RTMPose 5-15% better:**
   → ⚖️ **Offer both options** (user choice)
   
   **If RTMPose <5% better:**
   → ⚡ **Stick with MediaPipe** (faster, simpler)
   
   **If RTMPose worse or unstable:**
   → ❌ **Revert to MediaPipe** (debug RTMPose later)

---

## 📝 DOCUMENTATION

### Create Final Comparison Document:

**File**: `docs/PROVIDER_COMPARISON_RESULTS.md`

```markdown
# Provider Comparison Results

## Test Setup
- **Date**: [YYYY-MM-DD]
- **Videos Tested**: [X] videos
- **System**: [GPU model, CUDA version]
- **MediaPipe Version**: 0.10.9
- **RTMPose Version**: MMPose 1.3.2

## Results Summary

### Overall Statistics
- MediaPipe Average Quality: X.XXX
- RTMPose Average Quality: X.XXX
- Average Improvement: +XX.X%
- RTMPose Wins: X/Y videos

### Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

### Performance
- MediaPipe Average Time: XXs/video
- RTMPose Average Time: XXs/video
- Speed Ratio: X.Xx slower

## Detailed Results
[Paste comparison table from HTML report]

## Visual Examples
[Include 2-3 screenshots showing key differences]

## Decision
**Selected Provider**: [MediaPipe / RTMPose / Both]

**Justification**:
[Explain decision based on data]

## Recommendations
- For production: [...]
- For research papers: [...]
- For demos: [...]
```

---

## ✅ DELIVERABLES

After completing this protocol, you will have:

1. ✅ **Quantitative Comparison**:
   - CSV with all metrics
   - Statistical analysis
   - Quality scores per video

2. ✅ **Visual Comparison**:
   - Side-by-side videos (all test videos)
   - Screenshot comparisons
   - Quality difference visualization

3. ✅ **Interactive Report**:
   - HTML report with charts
   - Sortable data tables
   - Improvement breakdown

4. ✅ **Documentation**:
   - Test methodology
   - Results analysis
   - Decision rationale
   - Recommendations

5. ✅ **Data Archive**:
   - All tracking outputs
   - Visualizations
   - Metrics
   - Logs

---

## 🎯 SUCCESS CRITERIA

Test is complete when:

- ✅ All selected videos processed with both providers
- ✅ Quality metrics collected and compared
- ✅ Side-by-side visualizations created
- ✅ HTML report generated
- ✅ Clear recommendation documented
- ✅ Results committed to git

---

## ⏱️ TIMELINE

| Phase | Duration | Activity |
|-------|----------|----------|
| Setup | 15 min | Create folders, copy scripts |
| Processing | 2-3 hours | Batch process with both providers |
| Analysis | 30 min | Collect metrics, generate report |
| Review | 1 hour | Watch visualizations, analyze data |
| Document | 30 min | Write findings, make recommendation |
| **Total** | **4-6 hours** | End-to-end test |

---

## 🚨 TROUBLESHOOTING

### If processing fails:
```bash
# Check logs
cat workspace/provider_comparison/mediapipe/*_log.txt
cat workspace/provider_comparison/rtmpose/*_log.txt

# Process single video manually
python -m tracker_app process-video video-eksempler/5.mp4 --provider rtmpose --visualize
```

### If metrics collection fails:
```bash
# Check meta.json files exist
find workspace/provider_comparison -name "meta.json"

# Run collect_metrics.py with verbose output
python -v workspace/provider_comparison/collect_metrics.py
```

### If visualization comparison fails:
```bash
# Check visualization files exist
find workspace/provider_comparison -name "visualization.mp4"

# Test single video
python workspace/provider_comparison/create_side_by_side.py
```

---

**Ready to run? This protocol will give you publication-quality comparison data!** 🚀
