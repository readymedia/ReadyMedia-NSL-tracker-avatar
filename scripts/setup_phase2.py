import subprocess
import sys
import os

def run_cmd(cmd):
    print(f"Running: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {cmd}: {e}")
        sys.exit(1)

def setup_phase2():
    print("🚀 Setting up Phase 2 Environment (RTMPose)...")
    
    # 1. Install openmim
    print("\n📦 Installing openmim...")
    run_cmd(f"{sys.executable} -m pip install -U openmim")
    
    # 2. Install mmengine
    print("\n📦 Installing mmengine...")
    run_cmd(f"{sys.executable} -m mim install mmengine")
    
    # 3. Install mmcv (auto-detects torch version)
    print("\n📦 Installing mmcv...")
    run_cmd(f"{sys.executable} -m mim install \"mmcv>=2.0.1\"")
    
    # 4. Install mmdet (required for PoseDemo)
    print("\n📦 Installing mmdet...")
    run_cmd(f"{sys.executable} -m mim install mmdet")
    
    # 5. Install mmpose
    print("\n📦 Installing mmpose...")
    run_cmd(f"{sys.executable} -m mim install \"mmpose>=1.3.0\"")
    
    print("\n✅ Phase 2 environment setup complete!")
    print("You can now run the RTMPose provider.")

if __name__ == "__main__":
    setup_phase2()
