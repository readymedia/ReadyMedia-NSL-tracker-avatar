# IMPLEMENTATION GUIDE – Bygge Open NSL Avatar med Cursor

Dette dokumentet forklarer **hvordan** du bruker Cursor til å bygge prosjektet steg-for-steg.

---

## 🎯 Overordnet strategi

### Filosofi
Cursor er best til:
- ✅ Generere boilerplate og struktur
- ✅ Implementere veldefinerte algoritmer
- ✅ Skrive tests basert på spesifikasjoner

Cursor er IKKE perfekt til:
- ❌ Å "finne ut" hva du vil ha (trenger klare specs)
- ❌ Kompleks domenelogikk uten eksempler
- ❌ Debugging av subtile edge cases

**Derfor**: Vi gir Cursor MEGET detaljerte prompts med eksempler.

---

## 📅 Utviklingsplan

### Week 1: Foundation (Phase 1)
**Mål**: Fungerende end-to-end pipeline på 1 video.

**Dag 1-2**: Repo struktur + Database
- ✅ Cursor Prompt: Phase 1 (se 10_CURSOR_PROMPTS.md)
- ✅ Generer hele repoet
- ⚠️ **Du må**: Review koden, installer dependencies, test init-db

**Dag 3**: Ingest + Video metadata
- ✅ Test `ingest` command på manifest
- ✅ Verify database entries
- ⚠️ **Du må**: Fikse encoding-issues hvis CSV er feil format

**Dag 4**: Tracking på 1 video
- ✅ Test `run --limit 1`
- ✅ Inspect tracking output
- ⚠️ **Du må**: Adjustere MediaPipe params hvis tracking er dårlig

**Dag 5**: Batch på 10-100 videoer
- ✅ Test `run --limit 10`
- ✅ Check for crashes/errors
- ⚠️ **Du må**: Fix error handling, logging

---

### Week 2: Quality & Optimization (Phase 1.5)
**Mål**: Robust pipeline som kan kjøre på alle 9000 videoer.

**Dag 6-7**: Smoothing & Quality scoring
- ✅ Implement EMA filter
- ✅ Implement quality scorer
- ⚠️ **Du må**: Tune alpha values based on results

**Dag 8-9**: Batch processing
- ✅ Run på 100+ videoer
- ✅ Analyze failures
- ✅ Fix bugs

**Dag 10**: Full batch (9000 videoer)
- ✅ Start overnight batch run
- ✅ Monitor progress
- ⚠️ **Du må**: Resume if crashes, analyze quality distribution

---

### Week 3-4: SOTA Tracking (Phase 2)
**Mål**: Upgrade tracking til RTMPose/MMPose.

**Dag 11-12**: Setup RTMPose
- ✅ Install MMPose dependencies
- ✅ Download pretrained models
- ⚠️ **Du må**: CUDA/PyTorch må være korrekt installert

**Dag 13-14**: Implement RTMPose provider
- ✅ Cursor Prompt: Phase 2 provider implementation
- ✅ Test on 10 videos
- ✅ Compare with MediaPipe baseline

**Dag 15-16**: Temporal stabilization
- ✅ Implement advanced smoothing (OneEuro eller Kalman)
- ✅ Test on challenging videos
- ⚠️ **Du må**: Tune parameters

**Dag 17-18**: Re-run with Phase 2
- ✅ Full batch with new tracking
- ✅ Quality comparison

---

### Week 5-6: MetaHuman Integration (Phase 2.1)
**Mål**: Generate Unreal-import-ready packages.

**Dag 19-21**: Hand rotation solver
- ✅ Cursor Prompt: Phase 2.1 (hand solver)
- ✅ Implement landmarks → quaternions
- ✅ Unit tests
- ⚠️ **Du må**: Visual inspection in Unreal

**Dag 22-23**: Face curve extraction
- ✅ Implement FaceMesh → ARKit curves
- ✅ Test mapping

**Dag 24-26**: Unreal import script
- ✅ Generate unreal_import.py per word
- ✅ Test on 5-10 words in Unreal
- ⚠️ **Du må**: Manual testing in Unreal, adjust mapping

**Dag 27-30**: Full MetaHuman pipeline
- ✅ Generate all 9000 export packages
- ✅ Import subset to Unreal
- ✅ Create DataTable for word → AnimSequence
- ✅ Build trigger system

---

## 🔧 Cursor Workflow (per feature)

### Step 1: Skriv spesifikasjon
Før du bruker Cursor, skriv en klar spec:
```
Feature: EMA Smoothing Filter

Input: List of (x, y, confidence) tuples
Output: Smoothed list
Algorithm: x_smooth[t] = α * x[t] + (1-α) * x_smooth[t-1]
Config: α = 0.35 for wrists, 0.55 for fingers

Handle:
- First frame (no previous): x_smooth[0] = x[0]
- Missing data (confidence < 0.6): hold previous value
```

### Step 2: Gi Cursor contexten
I Cursor chat:
```
I need to implement an EMA smoothing filter.

Context:
- Language: Python 3.11
- Input: List[Landmark2D] where Landmark2D has x, y, confidence
- Output: List[Landmark2D] (smoothed)
- Config: alpha parameter (0.35 for wrists)

Spec:
[paste spec from Step 1]

Generate:
1. A class EMAFilter in tracker_app/postprocess/smoothing.py
2. Unit test in tests/test_smoothing.py
```

### Step 3: Review og test
**Ikke blindt akseptere Cursor output!**
1. Read the code
2. Check type hints
3. Run unit tests
4. Test on real data
5. Adjust if needed

### Step 4: Iterér
Hvis ikke perfekt:
```
The EMA filter is too aggressive for fingers. 
Modify to use different alpha values:
- wrist: 0.35
- fingers: 0.55
- face: 0.40

Add a `signal_type` parameter to the filter.
```

---

## 🎨 Cursor Best Practices

### DO:
- ✅ **Gi eksempler**: "Like this: `[1, 2, 3] → [1.0, 1.5, 2.1]`"
- ✅ **Spesifiser typer**: "Return `Dict[str, List[float]]`"
- ✅ **Navngi filer**: "In `tracker_app/utils/paths.py`"
- ✅ **Gi kontekst**: "Using MediaPipe Pose with 33 landmarks"
- ✅ **Be om tests**: "Also generate pytest tests"

### DON'T:
- ❌ Vage forespørsler: "Make tracking better"
- ❌ For store prompts: Bryt opp i mindre deler
- ❌ Anta at Cursor vet domenet ditt: Forklar NSL-specifics
- ❌ Stol blindt på output: ALLTID review

---

## 🧪 Testing Strategy

### Unit tests (lage med Cursor)
For hver modul, generer unit tests:
```python
# tests/test_smoothing.py
def test_ema_filter_basic():
    filter = EMAFilter(alpha=0.5)
    input = [1.0, 2.0, 3.0]
    output = [filter.update(x) for x in input]
    assert output == [1.0, 1.5, 2.25]  # roughly

def test_ema_filter_confidence_gating():
    # Test that low confidence values are held
    pass
```

### Integration tests (du må skrive)
Test full pipeline på 1 video:
```python
def test_full_pipeline_on_test_video():
    # Ingest
    # Run
    # Check output exists
    # Validate format
    pass
```

### Manual inspection (kritisk!)
Du må faktisk se på resultater:
1. **Visualiser tracking**: Draw landmarks on frames
2. **Check smoothness**: Plot x/y over time
3. **Inspect Unreal**: Se om animasjonen ser riktig ut

---

## 🔍 Debugging Workflow

### Problem: Cursor-generert kode crasher
**Step 1**: Read error message
**Step 2**: Identify the file/function
**Step 3**: Prompt Cursor:
```
The function `smooth_tracking_sequence` in tracker_app/postprocess/smoothing.py 
crashes with:
[paste error]

The input is:
[paste input sample]

Fix the bug and add a check for this edge case.
```

### Problem: Output format er feil
**Step 1**: Compare output vs. spec (use JSON diff)
**Step 2**: Prompt Cursor:
```
The output JSON has wrong structure. 
Expected: {"frame": 0, "pose_2d": [...]}
Actual: {"frameIndex": 0, "pose": [...]}

Fix the serialization in TrackingResult.to_dict() to match expected format.
```

---

## 📊 Monitoring Progress

### Metrics to track:
1. **Jobs completed**: Check `jobs` table daily
2. **Quality distribution**: Plot histogram of quality_score
3. **Failure rate**: `COUNT(*) WHERE status='failed'`
4. **Processing speed**: Time per video

### Tools:
```bash
# Quick stats
sqlite3 workspace/tracker.db "SELECT status, COUNT(*) FROM jobs GROUP BY status"

# Export results
python -m tracker_app export-index
```

---

## 🚨 Common Pitfalls

### 1. Encoding issues med æøå
**Problem**: CSV ikke lest riktig, ord blir "??" eller mojibake.
**Solution**: 
```python
# Try utf-8-sig first (Excel BOM)
# Then utf-8
# Then cp1252 (Windows legacy)
```

### 2. MediaPipe ikke detekterer hender
**Problem**: Hender er utenfor bilde eller occluded.
**Solution**: 
- Adjust `min_detection_confidence` (lower = more sensitive)
- Implement confidence gating (hold last known position)

### 3. CUDA/GPU ikke brukt
**Problem**: Tracking går på CPU (sakte).
**Solution**:
- Check `nvidia-smi`
- Verify CUDA installed
- Use `device='cuda'` i PyTorch models

### 4. Unreal import crashes
**Problem**: Unreal Python API er versjonsspesifikk.
**Solution**:
- Test på målversjon (UE 5.3+)
- Check Unreal Python docs
- Isolate API calls, add try-except

---

## 📦 Deliverables Checklist

### Phase 1 (MVP)
- [ ] Repo structure med alle moduler
- [ ] Database schema (SQLite)
- [ ] CLI commands (ingest, run, export-index)
- [ ] MediaPipe tracking working
- [ ] Smoothing implemented
- [ ] Quality scoring implemented
- [ ] 10 videoer prosessert successfully
- [ ] Output i riktig format

### Phase 2 (SOTA)
- [ ] RTMPose provider implemented
- [ ] Temporal stabilization advanced
- [ ] Quality scoring v2
- [ ] 100 videoer prosessert successfully
- [ ] Quality improvement vs. Phase 1 documented

### Phase 2.1 (MetaHuman)
- [ ] Hand rotation solver working
- [ ] Face curve extraction working
- [ ] MetaHuman mapping config
- [ ] Unreal import script generated per word
- [ ] 5-10 ord importert til Unreal successfully
- [ ] AnimSequence playable i Unreal

### Full Production
- [ ] All 9000 videoer prosessert
- [ ] Quality report generated
- [ ] Failure analysis documented
- [ ] Exports indexed
- [ ] Documentation complete

---

## 🎓 Learning Resources

### Mens du venter på Cursor output:
- **MediaPipe docs**: https://developers.google.com/mediapipe
- **MMPose docs**: https://mmpose.readthedocs.io/
- **Unreal Python API**: https://docs.unrealengine.com/5.3/en-US/PythonAPI/
- **MetaHuman docs**: https://docs.metahuman.unrealengine.com/

---

## ✅ Success Metrics

### Technical success:
- [ ] Pipeline processes 9000 videos without manual intervention
- [ ] <5% failure rate
- [ ] Quality score >0.7 for 80%+ of videos
- [ ] Processing speed <30 sec/video average

### Product success:
- [ ] MetaHuman can sign at least 100 words
- [ ] Animations look natural (manual inspection)
- [ ] System is reproducible (others can run it)

---

## 🔮 Future Extensions (etter MVP)

1. **Web UI**: Visualize tracking, browse exports
2. **Auto-retake detector**: Flag videos that need re-recording
3. **Multi-person support**: Handle multiple signers
4. **Real-time mode**: Live sign language avatar
5. **Other languages**: Extend beyond NSL

---

## 🆘 Getting Unstuck

### If Cursor doesn't understand:
1. **Simplify prompt**: Break into smaller pieces
2. **Give example**: Show input/output pair
3. **Reference code**: "Like the pattern used in X file"

### If code doesn't work:
1. **Add logging**: Print intermediate values
2. **Unit test**: Isolate the problem
3. **Ask Cursor to debug**: Give error + context

### If quality is bad:
1. **Visualize**: Draw landmarks on video
2. **Compare**: MediaPipe vs. RTMPose vs. manual
3. **Tune params**: Alpha, confidence thresholds

---

**Du er nå klar til å starte!**

**Første steg**: 
1. Kopier Cursor Prompt fra `10_CURSOR_PROMPTS.md` (Phase 1)
2. Paste inn i Cursor
3. Review output grundig
4. Start testing

**Lykke til! 🚀**
