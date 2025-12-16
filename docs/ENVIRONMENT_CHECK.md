# 💻 Environment Check

**Version**: 0.2.0
**Last Updated**: 2025-12-16

Use this guide to verify your PC is ready for AI tracking.

---

## 🟢 Quick Check Script

Run this command in your terminal:

```bash
python -c "import torch; import mmpose; print(f'Torch: {torch.__version__}, CUDA: {torch.cuda.is_available()}, MMPose: {mmpose.__version__}')"
```

### ✅ Expected Output (Golden Path)
```
Torch: 2.1.2+cu118, CUDA: True, MMPose: 1.3.2
```

---

## 🔴 Troubleshooting Scores

| Component | Status | Fix |
|-----------|--------|-----|
| **CUDA** | `False` | You are running on CPU. RTMPose will be 10x slower. Reinstall PyTorch with CUDA 11.8 (See DEPLOYMENT.md). |
| **Torch** | `2.4.x` | Too new! MMPose works best with 2.1.0 - 2.1.2. Downgrade torch. |
| **MMPose** | `Error` | Library not found. Run `python scripts/setup_phase2.py`. |

---

## 💾 Storage Check

RTMPose downloads models to:
`C:\Users\<YOU>\.cache\torch\hub\checkpoints`

Ensure you have 5-10GB free on C: drive, or set `TORCH_HOME` to move the cache.
