# Testing Strategy

## 🧪 Unit Tests

We use `pytest` for unit testing.

### Running Tests
```bash
pytest
```

### Coverage
```bash
pytest --cov=tracker_app
```

## 🎥 Integration Tests

### Single Video Test
To test the full pipeline on a single video without adding it to the batch job queue:

```bash
python -m tracker_app process-video video-eksempler/5.mp4 --word "test" --visualize
```

**What to check:**
1. **Output files created**:
   - `meta.json`
   - `tracking.parquet`
   - `tracking.jsonl.gz`
   - `visualization.mp4`
2. **Quality Score**: Check `meta.json` for `quality_score > 0.5`.
3. **Visualization**: Watch `visualization.mp4`. Landmarks should stick to body/hands.

### Batch Test
To test the batch ingestion system:

1. **Ingest Manifest**:
   ```bash
   python -m tracker_app ingest tests/fixtures/sample_manifest.csv --dry-run
   ```

2. **Run Batch**:
   ```bash
   python -m tracker_app run --limit 5
   ```

## 🖥️ GUI Testing (Manual)

1. **Launch**: `python -m scripts.gui`
2. **Process**: Select 1 video in "Process" tab and run. Verify live preview updates.
3. **Verify**: Go to "Browse" tab and find the processed video.
4. **Dashboard**: Check "Dashboard" tab to see if counts increased.

## 🐛 Debugging

If tracking fails or quality is low:
1. **Enable Visualization**: Always use `--visualize` to see what the model sees.
2. **Check JSONL**: Open `tracking.jsonl.gz` to see raw confidence scores.
3. **Logs**: Check `workspace/logs/` for detailed error traces.
