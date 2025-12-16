# 01 – Requirements & Goals

## 🎯 Primærmål (MVP - Phase 1)

Bygge en lokal Windows-app (kraftig NVIDIA GPU) som:

### 1. Inndata og ingest
- ✅ Leser manifest-CSV (`minetegn_manifest_app_excel.csv`)
- ✅ Validerer at alle `local_path` finnes
- ✅ Håndterer æøå korrekt (NFC normalisering)
- ✅ Autodetekterer CSV-format (`,` vs `;`, encoding)

### 2. Batch-prosessering
- ✅ Prosesserer alle 9000+ videoer automatisk
- ✅ Støtter resume (hopper over allerede prosesserte)
- ✅ Parallellisering (design for, men MVP kan være serial)
- ✅ Robust feilhåndtering (én feil stopper ikke hele batchen)

### 3. Tracking-ekstraksjon
Ekstrahere per frame:
- **Kropp**: pose keypoints (overkropp, armer, hender)
- **Hender**: 21 landmarks per hånd (MediaPipe eller bedre)
- **Ansikt**: ansiktslandmarks + munn (non-manual markers)
- **Kvalitet**: confidence scores per modalitet

### 4. Datalagring
- ✅ **Lokal Supabase** (Postgres): metadata, job-status, søk
- ✅ **Disk**: tracking data (parquet/jsonl.gz)
- ✅ Strukturert og gjenopprettbart

### 5. Eksport (Unreal-ready)
Per ord genereres:
- `tracking.jsonl.gz` (eller `tracking_v2.jsonl.gz` i Phase 2)
- `meta.json` (video metadata + quality score)
- `unreal_import.py` (Python script for Unreal)
- `index_entry.json` (for eksport-katalog)

### 6. MetaHuman-animasjon
Gjøre at vi kan:
- Importere eksportpakker til Unreal
- Lage AnimSequence-assets per ord
- Trigge MetaHuman-avatar på ord og spille av animasjon

---

## 🎯 Sekundærmål (etter MVP)

### Kvalitetsforbedringer
- Auto cleanup av tracking (smoothing, outlier removal)
- Quality scoring per klipp (tracking quality, visibility)
- Automatisk flagging av dårlige opptak

### Infrastruktur
- Støtte for å bytte fra `remote_url` til egen CDN
- Versjoner av tracking (v1, v2, v3...)
- Migrering mellom formater

### Avansert tracking (Phase 2)
- Multi-model ensemble (OpenPose + MediaPipe + ...)
- Temporal stabilisering (EMA, Kalman, gap-filling)
- Super-resolution på lavoppløste klipp

### Unreal-integrasjon (Phase 2.1)
- Ferdig Control Rig mapping for MetaHuman
- Automatisk bone + curve keyframe baking
- DataTable for word → AnimSequence lookup

---

## 📦 Leveranser (hva Cursor skal produsere)

### 1. Kildekode (`tracker_app/`)
Python-pakke med:
- **CLI** (Typer-basert): `ingest`, `run`, `export-index`, `export-metahuman`
- **Pipeline-moduler**:
  - `ingest/` – manifest reading, job creation
  - `preprocess/` – ffmpeg utils, normalization, ROI
  - `tracking/` – provider interface + MediaPipe implementation
  - `postprocess/` – smoothing, quality scoring
  - `store/` – disk + Supabase persistence
  - `export/` – Unreal package generation
  - `rig/` – hand rotation solver, face curve mapping (Phase 2.1)
  - `unreal/` – import script templates
- **Utils**: paths, text, hashing, logging

### 2. Database schema
- `schema.sql` – full schema
- `migrations/` – versjonerte SQL-migrasjoner

### 3. Konfigurasjon
- `.env.example` – template for lokal setup
- `config.py` – lesing av miljøvariabler
- `configs/metahuman_mapping_nsl.json` – MetaHuman mapping (Phase 2.1)

### 4. Scripts
PowerShell-scripts for enkel kjøring:
- `run_supabase_local.ps1`
- `run_all.ps1`
- `run_subset.ps1`

### 5. Tester
- Unit tests for core logic
- Integration tests for full pipeline (subset av data)

### 6. Dokumentasjon
- `README.md` – Quick start
- `docs/` – Detaljert dokumentasjon

### 7. Outputformat-definisjon
- JSON schema for tracking data
- Naming conventions
- Versjonering

### 8. Unreal import demo
- Testpakke med 5–10 ord som proof-of-concept
- Fungerende import til Unreal (kan ha manuelle steg, men skal være dokumentert)

---

## 🔍 Scope (hva er INNENFOR og UTENFOR)

### ✅ Innenfor scope

#### MVP (Phase 1)
- Lokal batch-prosessering
- MediaPipe tracking (kropp + hender + ansikt)
- Basis smoothing og outlier removal
- Supabase local + disk lagring
- Eksport til disk i strukturert format
- Skeleton Unreal import script (må testes manuelt i Unreal)

#### Phase 2
- Multi-model tracking (OpenPose + MediaPipe)
- Temporal stabilisering (EMA, velocity clamp, gap-filling)
- Quality scoring v2
- Super-resolution på hånd-ROI (valgfritt)

#### Phase 2.1
- Fully functional Unreal Python import script
- MetaHuman Control Rig mapping (bones + curves)
- AnimSequence creation med keyframes

### ❌ Utenfor scope (i hvert fall for nå)

- **Tekst-til-tegnspråk** (generativ AI)
- **Real-time tracking** (alt er offline batch)
- **Cloud hosting** (alt lokalt)
- **Generative modeller** (kun motion capture, ikke syntese)
- **Automatisk Unreal trigger-system** (må bygges separat i Unreal)
- **Web-frontend** (kun CLI i MVP)
- **3D rekonstruksjon** (kun 2D→3D lifting der nødvendig)

---

## 📊 Success Criteria

### Teknisk
- [x] Pipeline kjører lokalt uten crashes
- [x] 95%+ av videoer prosesseres uten fatal feil
- [x] Tracking data er stabil og gjenopprettbar
- [x] Unreal-import fungerer på testdatasett

### Kvalitet
- [x] Hender er synlige og sporbare i 80%+ av frames
- [x] Ansikt/munn er synlig i 70%+ av frames
- [x] Quality score korrelerer med visuell kvalitet

### Performance
- [x] Prosessering: ~5–30 sekunder per video (avhengig av lengde/kvalitet)
- [x] Batch: fullføre 1000 videoer på <24 timer (single GPU)
- [x] Database query: <100ms for typiske oppslag

### Brukbarhet
- [x] CLI er selvforklarende og loggfører godt
- [x] Feil er forståelige og actionable
- [x] Resume fungerer pålitelig

---

## 🚧 Kjente begrensninger og risiko

### Høy risiko
1. **Hånd/finger-presisjon fra 2D video**
   - Håndoverlapp, okklusjon, dårlig belysning
   - *Mitigering*: Multi-model ensemble, confidence gating
   
2. **"Plug rett inn i MetaHuman"**
   - Kompleks mapping mellom tracking → Control Rig
   - *Mitigering*: Iterativ tilnærming, data-drevet mapping

### Medium risiko
3. **Varierende videokvalitet**
   - Eldre klipp er lavoppløselige
   - *Mitigering*: Super-resolution pass (valgfritt), quality scoring

4. **Temporal instabilitet**
   - Jitter, dropout, sudden jumps
   - *Mitigering*: Smoothing pipeline, gap-filling

### Lav risiko
5. **Performance på 9000+ filer**
   - Lang kjøretid
   - *Mitigering*: Parallellisering, GPU batch optimization

---

## 📋 Ikke-funksjonelle krav

### Ytelse
- Skal kjøre på single-workstation (ikke cluster)
- GPU utilization >70% under tracking
- Minimal I/O wait (bruk SSD)

### Sikkerhet
- Ingen data forlater maskinen
- GDPR-compliant (all prosessering lokal)

### Vedlikeholdbarhet
- Kode er typed (mypy-ready)
- Modulær arkitektur (lett å bytte tracking-provider)
- Versjonerte output-formater

### Dokumentasjon
- README med quick start
- Docstrings på alle public APIs
- Cursor-optimaliserte master prompts

---

## 🔄 Iterasjonsplan

### Fase 1: Foundation (Cursor session 1–2)
- Repo structure
- Ingest + preprocessing
- MediaPipe tracking (baseline)
- Disk + Supabase lagring

### Fase 2: Quality (Cursor session 3–4)
- Multi-model tracking
- Temporal stabilization
- Quality scoring

### Fase 3: MetaHuman (Cursor session 5–6)
- Hand rotation solver
- Face curve mapping
- Unreal import script
- Full test på 10+ ord

### Fase 4: Batch (Cursor session 7)
- Full batch-kjøring (9000 videoer)
- Performance tuning
- Failure analysis

---

**Neste: [02_ARCHITECTURE.md](02_ARCHITECTURE.md) →**
