# Test Video Analysis

## Sample Set Overview

Total: 14 videos
Total size: ~3.8 MB
Format: MP4 (H.264)
FPS: 25.0 (Consistent)

## Video Characteristics

### Resolution Variants
1. **640x480 (SD)**
   - `5.mp4` (1.16s)
   - `yoghurt-2.mp4` (verified size)

2. **960x720 (HD Ready)**
   - `aalesund-2.mp4` (2.56s)
   - `bistandsadvokat.mp4` (2.88s)
   - Most others likely fall in this category

### By Category

**Simple Single Signs (good for initial testing):**
1. `5.mp4` – 196 kB – Number sign, 640x480
2. `andre.mp4` – 279 kB – Common word
3. `moss.mp4` – 247 kB – Place name
4. `ANB.mp4` – 327 kB – Abbreviation

**Norwegian Characters (æøå handling):**
**Note**: Filenames appear normalized (e.g., `aalesund` instead of `ålesund`, `haandball` instead of `håndball`).
1. `yoghurt-2.mp4` – 190 kB
2. `aalesund-2.mp4` – 324 kB

**Complex Words:**
1. `bistandsadvokat.mp4` – 370 kB – 960x720
2. `transformator.mp4` – 297 kB
3. `muhammed-islam-2.mp4` – 244 kB

**Multi-word Phrases:**
1. `3-2-1-haandballformasjon.mp4` – 507 kB (longest)
2. `argument-2.mp4` – 317 kB
3. `motta-gaver-ol.mp4` – 292 kB

**Food Terms:**
1. `tortilla.mp4` – 263 kB
2. `yoghurt-2.mp4` – 190 kB

## Testing Strategy

### Phase 1: Basic Validation (3 videos)
1. Start with `5.mp4` (Low res, short)
2. Test `aalesund-2.mp4` (Higher res, normalized name)
3. Test `bistandsadvokat.mp4` (Complex motion)

### Phase 2: Broader Coverage
Test remaining videos to ensure resolution independence (640x480 vs 960x720) in the pipeline.

## Success Criteria Per Phase

**Phase 1**:
- ✅ All 3 process without errors
- ✅ Tracking data saved correctly
- ✅ Pipeline handles resolution changes automatically

## Expected Challenges

1. **Resolution Scale**: Landmarks must be normalized (0..1) to handle 480p vs 720p.
2. **Filename Mapping**: `aalesund` -> `Ålesund` (might need a lookup table if correct display name is required).
3. **Variable Light/Background**: To be assessed visually.

## Manual Inspection Checklist

For each processed video, verify:
- [ ] Hands detected in >70% of frames
- [ ] Face detected in >70% of frames
- [ ] Tracking is stable (low jitter)
- [ ] No obvious errors in landmarks
- [ ] Parquet file readable
- [ ] JSONL file valid JSON
- [ ] meta.json contains quality score
