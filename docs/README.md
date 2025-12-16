# Open NSL Avatar – Norwegian Sign Language to MetaHuman Pipeline

Open NSL Avatar is a research-grade system designed to convert Norwegian Sign Language (NSL) videos into high-precision MetaHuman animations for Unreal Engine.

---

## 📚 Documentation Index

### 🚀 Getting Started
- **[User Manual](USER_MANUAL.md)** – Complete guide for the GUI and Models (Start Here!)
- **[Deployment Guide](DEPLOYMENT.md)** – Installation on new Production PCs
- **[Roadmap](ROADMAP.md)** – Development plan & priorities

### 🛠️ Development & Testing
- **[Quick Test Guide](QUICK_TEST_GUIDE.md)** – 15-minute validation steps
- **[Provider Protocol](PROVIDER_TEST_PROTOCOL.md)** – Detailed MediaPipe vs RTMPose comparison
- **[Bug Tracker](BUGS.md)** – Known issues (and fixes like BUG-003)
- **[Testing Strategy](TESTING.md)** – General test units

### 🧠 Technical Reference
- **[Architecture](ARCHITECTURE.md)** – System design & Data Flow
- **[Data Schema](DATA_SCHEMA.md)** – JSON/Parquet output formats explained
- **[Tech Stack](../03_TECH_STACK.md)** – Libraries & Versions (PyTorch 2.1.2)
- **[Environment Check](ENVIRONMENT_CHECK.md)** – Verify GPU/CUDA status

### 📂 Legacy / Superseded
- *INSTALLATION.md* (Use DEPLOYMENT.md)
- *GUI_USER_GUIDE.md* (Use USER_MANUAL.md)

---

## 🎯 Project Status

**Current Phase**: **Phase 2 - Dual Provider (RTMPose Integrated)**
**Version**: 0.2.0
**Last Updated**: 2025-12-16

### ✅ Key Features
- **Dual Tracking**: Switch between MediaPipe (Speed) and RTMPose (Quality).
- **Pro GUI**: Batch processing, Live Preview, Dashboard.
- **Robust Data**: JSONL + Parquet storage.
- **Verified Environment**: CUDA 11.8 + PyTorch 2.1.2.

---

## 🚀 Quick Links
- [Project Overview](../00_PROJECT_OVERVIEW.md)
- [Implementation Guide](../IMPLEMENTATION_GUIDE.md)

