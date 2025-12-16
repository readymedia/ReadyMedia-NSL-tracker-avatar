import json
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

def load_track_data(workspace_dir: Path):
    tracks_dir = workspace_dir / "workspace" / "tracks"
    data = []
    
    if not tracks_dir.exists():
        print(f"No tracks directory found at {tracks_dir}")
        return pd.DataFrame()

    print(f"Scanning {tracks_dir}...")
    
    for meta_file in tracks_dir.glob("*/meta.json"):
        try:
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                
            # Determine provider if missing (older runs)
            provider = meta.get('tracking_provider', 'mediapipe') # Default to mp for old runs
            
            # Get timestamp from folder creation
            timestamp = meta_file.parent.stat().st_mtime
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            
            data.append({
                'filename': meta.get('filename', 'unknown'),
                'provider': provider,
                'quality': meta.get('quality_score', 0.0),
                'date': date_str,
                'timestamp': timestamp,
                'path': str(meta_file.parent)
            })
        except Exception as e:
            print(f"Error reading {meta_file}: {e}")
            
    return pd.DataFrame(data)

def compare_providers():
    root_dir = Path(".")
    df = load_track_data(root_dir)
    
    if df.empty:
        print("No tracking data found.")
        return

    # Filter for recent runs only (last 24 hours) or just take all?
    # Let's take the BEST run for each provider/file combination
    
    # Sort by quality desc to get best first
    best_runs = df.sort_values('quality', ascending=False).groupby(['filename', 'provider']).first().reset_index()
    
    # Pivot to compare
    pivot = best_runs.pivot(index='filename', columns='provider', values='quality')
    
    if 'mediapipe' not in pivot.columns:
        print("Missing MediaPipe data.")
        print(pivot)
        return
        
    if 'rtmpose' not in pivot.columns:
        print("Missing RTMPose data.")
        pivot['rtmpose'] = 0.0

    # Calculate Delta
    pivot['delta'] = pivot['rtmpose'] - pivot['mediapipe']
    pivot['winner'] = pivot.apply(lambda row: 'RTMPose' if row['delta'] > 0 else 'MediaPipe', axis=1)
    
    print("\n" + "="*60)
    print("🏆 TRACKING PROVIDER SHOWDOWN 🏆")
    print("="*60)
    print(f"{'Filename':<30} | {'MediaPipe':<10} | {'RTMPose':<10} | {'Delta':<10} | {'Winner'}")
    print("-" * 80)
    
    for filename, row in pivot.iterrows():
        mp_score = row.get('mediapipe', 0.0)
        rtm_score = row.get('rtmpose', 0.0)
        if pd.isna(mp_score): mp_score = 0.0
        if pd.isna(rtm_score): rtm_score = 0.0
            
        delta = rtm_score - mp_score
        winner = "RTMPose" if delta > 0.05 else ("MediaPipe" if delta < -0.05 else "Tie")
        
        # Color coding (pseudo)
        delta_str = f"{delta:+.2f}"
        
        print(f"{filename[:30]:<30} | {mp_score:.2f}       | {rtm_score:.2f}       | {delta_str:<10} | {winner}")
        
    print("-" * 80)
    
    # Summary
    avg_mp = pivot['mediapipe'].mean()
    avg_rtm = pivot['rtmpose'].mean()
    print(f"\nAVERAGE SCORE: MediaPipe = {avg_mp:.2f} vs RTMPose = {avg_rtm:.2f}")
    
    if avg_rtm > avg_mp:
        print(f"\n🎉 CONCLUSION: RTMPose is better by {((avg_rtm - avg_mp)/avg_mp)*100:.1f}%!")
    else:
        print(f"\n🤔 CONCLUSION: MediaPipe is still competitive.")

if __name__ == "__main__":
    compare_providers()
