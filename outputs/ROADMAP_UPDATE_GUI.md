# 🎨 ROADMAP UPDATE: Add GUI (Phase 1.5)

## 📋 TASK

Update `docs/ROADMAP.md` to include **Phase 1.5: Professional GUI** based on the complete specification in `outputs/GUI_SPECIFICATION.md`.

---

## 🎯 What to Add

Insert **Phase 1.5** between Phase 1 (MVP Pipeline) and Phase 2 (SOTA Tracking).

### New Section:

```markdown
## Phase 1.5: Professional GUI (Week 3)

**Goal**: Professional Gradio-based interface for processing, browsing, and monitoring

**Product Name**: ReaddyMedia - NSL Avatar

### F020: GUI Foundation ⭐⭐ Medium [P1]
**Prerequisites**: F001-F019 (Phase 1 complete)
**Estimated Time**: 4 hours

Tasks:
- [ ] Create `scripts/gui.py` with Gradio
- [ ] Implement custom CSS styling (ReaddyMedia theme)
- [ ] Setup tab structure (Process / Browse / Dashboard / Settings)
- [ ] Basic layout and navigation

**Success Criteria**:
- ✅ GUI launches on localhost:7860
- ✅ All 4 tabs render correctly
- ✅ ReaddyMedia branding applied

---

### F021: Live Tracking Preview ⭐⭐⭐ Hard [P1]
**Prerequisites**: F020
**Estimated Time**: 6 hours

Tasks:
- [ ] Implement real-time frame annotation
- [ ] Color-coded confidence visualization:
  - 🟢 Green dots: High confidence (>0.7)
  - 🟡 Yellow dots: Medium (0.5-0.7)
  - 🔴 Red dots: Low (<0.5)
- [ ] Draw hand connections and skeleton
- [ ] Add info overlay (pose/hands/face confidence)
- [ ] Update preview every N frames during processing

**Success Criteria**:
- ✅ Can see tracking in real-time during processing
- ✅ Landmarks drawn correctly with confidence colors
- ✅ Preview updates smoothly (no lag)
- ✅ Metrics overlay shows current frame stats

**Implementation Notes**:
- Use `draw_tracking_overlay()` from GUI spec
- Queue-based frame passing (max 5 frames buffered)
- Update every 5 frames to avoid slowdown

---

### F022: Video Browser ⭐⭐ Medium [P1]
**Prerequisites**: F020
**Estimated Time**: 4 hours

Tasks:
- [ ] Load processed videos from database
- [ ] Filterable table (search, quality threshold)
- [ ] Video preview with annotated overlay
- [ ] Quality detail panel (scores, issues)
- [ ] Download buttons (tracking data, visualization)

**Success Criteria**:
- ✅ Can browse all processed videos
- ✅ Search works correctly
- ✅ Quality filtering functional
- ✅ Can preview and download results

---

### F023: Dashboard & Analytics ⭐⭐ Medium [P2]
**Prerequisites**: F020
**Estimated Time**: 5 hours

Tasks:
- [ ] Statistics cards (Total/Done/Failed/Pending)
- [ ] Quality distribution histogram (Plotly)
- [ ] Processing time bar chart
- [ ] Common issues summary
- [ ] Storage usage indicator
- [ ] Recent activity log
- [ ] Export report functionality (PDF/CSV)

**Success Criteria**:
- ✅ Dashboard shows real-time stats
- ✅ Charts render correctly
- ✅ Can export reports

---

### F024: Batch Processing UI ⭐⭐⭐ Hard [P1]
**Prerequisites**: F020, F021
**Estimated Time**: 5 hours

Tasks:
- [ ] Video selection checklist
- [ ] Configurable processing settings
- [ ] Start/Pause/Stop controls
- [ ] Progress bar with ETA
- [ ] Live log output
- [ ] Integration with CLI backend

**Success Criteria**:
- ✅ Can select multiple videos
- ✅ Processing runs with live preview
- ✅ Can pause/stop processing
- ✅ Progress accurate
- ✅ Log shows all events

---

### F025: Settings Panel ⭐ Easy [P2]
**Prerequisites**: F020
**Estimated Time**: 2 hours

Tasks:
- [ ] Path configuration (workspace, videos)
- [ ] Video processing settings
- [ ] Tracking configuration (provider, confidence)
- [ ] Smoothing sliders
- [ ] Output options
- [ ] Save/Load settings

**Success Criteria**:
- ✅ All settings accessible
- ✅ Settings persist to .env
- ✅ Can reset to defaults

---

## 📊 Phase 1.5 Summary

**Total Estimated Time**: 26 hours (~3-4 days of focused work)

| Feature | Priority | Difficulty | Time |
|---------|----------|------------|------|
| F020: GUI Foundation | P1 | ⭐⭐ | 4h |
| F021: Live Preview | P1 | ⭐⭐⭐ | 6h |
| F022: Video Browser | P1 | ⭐⭐ | 4h |
| F023: Dashboard | P2 | ⭐⭐ | 5h |
| F024: Batch Processing UI | P1 | ⭐⭐⭐ | 5h |
| F025: Settings Panel | P2 | ⭐ | 2h |

**Success Criteria for Phase 1.5**:
- ✅ GUI fully functional
- ✅ Can process videos through GUI
- ✅ Live tracking preview works
- ✅ Can browse and download results
- ✅ Professional appearance (ReaddyMedia branding)

**Test Plan**:
1. Process 3 videos through GUI
2. Verify live preview shows tracking
3. Browse results in video browser
4. Check dashboard statistics
5. Export a report
6. Save/load settings
```

---

## 🔗 Reference

Full implementation details in: `outputs/GUI_SPECIFICATION.md`

This includes:
- Complete UI mockups/wireframes
- Full Python code for `scripts/gui.py`
- Color scheme and branding
- All callbacks and event handlers
- Live tracking preview implementation

---

## 📝 Update Instructions

1. Open `docs/ROADMAP.md`
2. Find "Phase 2: SOTA Tracking"
3. **Insert** the Phase 1.5 section above Phase 2
4. Update the feature overview table at the top:
   - Add rows F020-F025
   - Set correct priorities and difficulties
   - Mark status as "⏸️ Planned"
5. Update phase numbering if needed
6. Save file

---

## ✅ Validation

After updating, verify:
- [ ] Phase 1.5 is clearly separated from Phase 1 and 2
- [ ] All features F020-F025 are in the overview table
- [ ] Feature IDs are sequential
- [ ] Success criteria are clear
- [ ] Reference to GUI_SPECIFICATION.md is included
