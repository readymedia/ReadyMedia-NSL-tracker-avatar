# OPTIMALISERT CURSOR PROMPT – Endringsliste (v2)

## 📋 Hva er endret fra original?

Dette er en komplett liste over forbedringer i den optimaliserte versjonen.

---

## 🔴 KRITISKE forbedringer

### 1. Database: Supabase → SQLite
**Før**: Supabase (complex, Docker-dependent)  
**Nå**: SQLite (file-based, zero-config)

**Fordeler**:
- ✅ Ingen Docker setup nødvendig
- ✅ Enklere å komme i gang
- ✅ Raskere for single-machine batch processing
- ✅ Kan oppgraderes til Postgres senere hvis nødvendig

**Implementering**:
- `tracker_app/store/db.py` – Komplett SQLite wrapper
- Context managers for sikre transaksjoner
- Proper indexes for performance

---

### 2. Output: JSONL only → Parquet + JSONL
**Før**: Kun JSONL.gz  
**Nå**: Parquet (primary) + JSONL (debug)

**Fordeler**:
- ✅ Parquet er 5-10x mindre
- ✅ Kolonne-basert = raskere queries
- ✅ Industry standard
- ✅ JSONL fremdeles tilgjengelig for debugging

**Implementering**:
- `tracker_app/store/disk.py`:
  - `save_tracking_parquet()`
  - `save_tracking_jsonl()`
  - `load_tracking_parquet()`

---

### 3. Lagt til: Visualisering/debugging
**Før**: Ingen visualisering planlagt  
**Nå**: Innebygd visualisering

**Nye features**:
- ✅ Tegne landmarks på video
- ✅ Generere annoterte videoer
- ✅ CLI command: `visualize <word>`
- ✅ Quality report generation

**Implementering**:
- `tracker_app/visualization/draw_landmarks.py`
- `scripts/visualize_tracking.py`

---

### 4. Lagt til: Quality issues tracking
**Før**: Kun én quality_score  
**Nå**: Detaljert issue tracking

**Fordeler**:
- ✅ Spesifikke issues per frame range
- ✅ Severity levels (warning/error/info)
- ✅ Ny database tabell: `quality_issues`
- ✅ Bedre failure analysis

**Implementering**:
- Database schema: `quality_issues` table
- `db.add_quality_issue()` method
- Quality scorer returnerer structured issues

---

## 🟡 VIKTIGE forbedringer

### 5. Bedre config management
**Før**: Basic config  
**Nå**: Pydantic-based config med auto-derived paths

**Forbedringer**:
- ✅ Type-validated settings
- ✅ Auto-create directories
- ✅ Global `get_config()` singleton
- ✅ Better defaults

**Eksempel**:
```python
from tracker_app.config import get_config

config = get_config()
# All paths ready to use, directories created
```

---

### 6. Robust error handling
**Før**: Basic try-catch  
**Nå**: Comprehensive error handling

**Forbedringer**:
- ✅ Per-video error isolation (one failure doesn't stop batch)
- ✅ Detailed error messages in database
- ✅ Resume capability after crashes
- ✅ Proper logging at all levels

---

### 7. Better CLI UX
**Før**: Basic commands  
**Nå**: Rich terminal UI + more commands

**Nye features**:
- ✅ `stats` command – Show processing statistics
- ✅ `visualize` command – Generate debug videos
- ✅ Progress bars med rich
- ✅ Colored output
- ✅ Better help text

---

### 8. Testing infrastructure
**Før**: Minimal tests  
**Nå**: Comprehensive test suite

**Coverage**:
- ✅ Manifest reading (including æøå)
- ✅ EMA filter behavior
- ✅ Velocity clamping
- ✅ Serialization/deserialization
- ✅ Test fixtures

---

## 🟢 Mindre forbedringer

### 9. Video utilities improvement
- Extract metadata with ffmpeg-python
- Iterator-based frame extraction (memory efficient)
- Debug frame saving

### 10. Better data models
- Proper `TrackingResult` dataclass
- `Landmark2D` with optional name field
- Clean `to_dict()` serialization

### 11. Smoothing improvements
- Separate EMA filters per landmark
- Confidence-weighted smoothing
- Velocity clamp support
- Per-signal-type alpha values

### 12. Documentation
- Complete README.md
- Inline docstrings
- .env.example with all options
- Troubleshooting guide

---

## 📊 Sammenligning: Før vs. Nå

| Aspekt | Original | Optimalisert v2 | Forbedring |
|--------|----------|-----------------|------------|
| Database setup | Supabase (Docker) | SQLite (file) | ⭐⭐⭐⭐⭐ |
| Time to first run | 30-60 min | 5-10 min | ⭐⭐⭐⭐⭐ |
| Output format | JSONL only | Parquet + JSONL | ⭐⭐⭐⭐ |
| Debugging | None | Visualization | ⭐⭐⭐⭐⭐ |
| Quality tracking | Score only | Score + issues | ⭐⭐⭐⭐ |
| Error handling | Basic | Comprehensive | ⭐⭐⭐⭐ |
| Testing | Minimal | Full suite | ⭐⭐⭐⭐ |
| CLI UX | Basic | Rich + Colors | ⭐⭐⭐ |
| Config | Simple | Pydantic-validated | ⭐⭐⭐ |

---

## 🚀 Hva er IKKE endret

Disse tingene er fortsatt de samme (og det er bra):

- ✅ MediaPipe for Phase 1 (solid baseline)
- ✅ Provider interface pattern
- ✅ Phase-based approach
- ✅ Canonical skeleton model (for fremtiden)
- ✅ MetaHuman som mål
- ✅ Lokal prosessering

---

## 📝 Hvordan bruke den optimaliserte versjonen

### Step 1: Kopier begge prompt-filer
Cursor kan ta lange prompts, så gi den:
1. `CURSOR_PROMPT_OPTIMIZED.md` (Part 1)
2. `CURSOR_PROMPT_OPTIMIZED_PART2.md` (Part 2)

**Eller**: Kombiner dem til én fil først.

### Step 2: Paste i Cursor
```
[Paste hele prompten]

Now generate the complete repository with all files.
```

### Step 3: Review output
- Check at alle filer er generert
- Review kode kvalitet
- Run tests

### Step 4: Test
```bash
pip install -r requirements.txt
python -m tracker_app init-db
python -m tracker_app --help
pytest tests/
```

---

## 🎯 Forventet resultat

Etter Cursor-generering skal du ha:
- ✅ Komplett, kjørbart repo
- ✅ ~20 Python-filer med type hints
- ✅ SQLite database setup
- ✅ CLI med 6+ commands
- ✅ Test suite (10+ tests)
- ✅ Dokumentasjon (README + docstrings)

**Estimert tid**: 5-10 minutter for Cursor å generere alt.

---

## ⚠️ Viktige notater

### 1. Cursor kan gjøre feil
Selv den optimaliserte prompten er ikke perfekt. **Review alltid**:
- Import statements
- Type hints
- Error handling
- Edge cases

### 2. Testing er kritisk
Ikke stol blindt på AI-generert kode:
```bash
pytest tests/ -v
```

### 3. Start smått
Test på 1-10 videoer først, ikke full batch:
```bash
python -m tracker_app run --limit 10
```

---

## 🔮 Neste steg etter MVP

Når Phase 1 fungerer:

1. **Visualisering UI** (Gradio/Streamlit)
   ```bash
   pip install gradio
   python scripts/quality_dashboard.py
   ```

2. **Phase 2**: RTMPose tracking
   - Installer MMPose
   - Implement new provider
   - Compare quality

3. **Phase 2.1**: MetaHuman mapping
   - Hand rotation solver
   - Face curves
   - Unreal import

---

## 💡 Tips for suksess

### DO:
- ✅ Les hele prompten først (forståelse)
- ✅ Kjør tests umiddelbart etter generering
- ✅ Visualiser resultater (bruk `visualize` command)
- ✅ Check quality scores (`stats` command)

### DON'T:
- ❌ Kjør full batch uten testing
- ❌ Skip code review
- ❌ Ignorer test failures
- ❌ Glem å backup workspace/

---

**Den optimaliserte versjonen er KLAR til bruk! 🚀**

Neste: Paste i Cursor og generer repoet.
