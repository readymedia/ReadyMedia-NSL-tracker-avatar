# Technical Decisions – Evaluering og alternativer

Dette dokumentet evaluerer de tekniske valgene gjort i prosjektet, gir min vurdering, og foreslår alternativer der relevant.

---

## 🏗️ Arkitekturvalg

### ✅ VALG: Lokal prosessering (ikke cloud)

**Begrunnelse i dokumentene**:
- GDPR-compliance
- Full kontroll over data
- Ingen API-kostnader

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
- **Pro**: 
  - Korrekt for sensitive data (tegnspråk kan inneholde personer)
  - Ingen vendor lock-in
  - Reproducerbarhet
  - Offline-capable
- **Con**:
  - Krever kraftig lokal hardware
  - Skalering krever flere maskiner (ikke cloud-elastisk)

**Alternativer**:
1. **Hybrid**: Preprocessing lokalt, tungregning i cloud (GPU-instanser)
   - ❌ Bryter GDPR-krav
2. **On-premise cluster**: Flere maskiner lokalt
   - ⚠️ Overkill for 9000 videoer, men relevant ved 100k+

**Anbefaling**: Behold lokal. Vurder cluster kun ved >50k videoer.

---

### ✅ VALG: Python som hovedspråk

**Begrunnelse**:
- Rikt ML/CV-økosystem
- Rask prototyping
- Cursor-vennlig

**Min vurdering**: ⭐⭐⭐⭐ Good
- **Pro**:
  - Alle ML-biblioteker tilgjengelig
  - God for data-pipeline
  - Typer via mypy/pydantic mulig
- **Con**:
  - GIL kan begrense parallellisering
  - Tregere enn Rust/C++ for tight loops
  - Dependency management kan være komplisert

**Alternativer**:
1. **Rust** for pipeline + Python for ML
   - ✅ Bedre performance
   - ❌ Lengre utviklingstid
   - ❌ Færre ML-bindings
2. **C++** med Python-bindings (pybind11)
   - ✅ Maksimal performance
   - ❌ Mye mer komplekst

**Anbefaling**: Behold Python. Hvis performance blir issue:
- Bruk Cython for bottlenecks
- Parallelliser med `multiprocessing` (unngå GIL)
- Vurder Rust-plugins for kritiske deler (f.eks. smoothing)

---

## 🗄️ Database-valg

### ⚠️ VALG: Supabase (lokal)

**Begrunnelse**:
- "Du ønsket Supabase"
- Postgres + JSONB
- God filtrering/søk
- Vei til cloud senere

**Min vurdering**: ⭐⭐⭐ Mixed feelings
- **Pro**:
  - Postgres er solid og fleksibel
  - JSONB for frame data fungerer
  - Supabase gir god DX (developer experience)
  - Autogenererte REST/GraphQL APIs (nyttig hvis du skal bygge UI senere)
- **Con**:
  - **Unødvendig kompleksitet for MVP**: Supabase er primært cloud-first
  - Lokal Supabase krever Docker + setup
  - For en batch pipeline er SQLite eller ren Postgres enklere
  - Supabase-spesifikke features (auth, realtime) brukes ikke

**Alternativer**:
1. **Bare Postgres** (lokalt)
   - ✅ Enklere setup
   - ✅ Alle Postgres-features tilgjengelig
   - ❌ Ingen autogenerert API (men trengs ikke for batch)
   
2. **SQLite** (enda enklere)
   - ✅ Zero-config, fil-basert
   - ✅ Perfekt for lokale apps
   - ❌ Dårligere for concurrent writes (men batch er mest sequential)
   - ❌ Mindre kraftig JSONB-støtte

3. **DuckDB** (moderne alternativ)
   - ✅ Ekstremt rask for analytics
   - ✅ Embedded som SQLite
   - ✅ God parquet-integrasjon
   - ⚠️ Mindre mature enn Postgres/SQLite

**Anbefaling**: 
- **For MVP**: Vurder **SQLite** eller **ren Postgres**
  - SQLite hvis du ikke trenger concurrent processing
  - Postgres hvis du vil ha samme DB i prod/cloud senere
- **Behold Supabase hvis**:
  - Du faktisk skal bygge et web-UI senere
  - Du vil ha realtime updates under batch-kjøring
- **Pragmatisk løsning**: Støtt både (abstraksjonslay i `store/`)

---

## 🎥 Video-prosessering

### ✅ VALG: FFmpeg

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
- FFmpeg er industri-standard
- Håndterer alle formater
- Rask og pålitelig

**Ingen alternativer nødvendig.**

---

## 🤖 Tracking-modeller

### Phase 1: MediaPipe (baseline)

**Min vurdering**: ⭐⭐⭐⭐ Good starting point
- **Pro**:
  - All-in-one: pose + hands + face
  - CPU/GPU-agnostisk
  - God dokumentasjon
  - Gratis og open-source
- **Con**:
  - Ikke best-in-class for hvert domene
  - Håndpresisjon kan være middels på vanskelige scener

**Anbefaling**: Perfekt for MVP. Hold provider-interface for å bytte senere.

---

### Phase 2: Multi-model ensemble

#### ⚠️ VALG: OpenPose for kropp

**Min vurdering**: ⭐⭐⭐ Dated but proven
- **Pro**:
  - Solid for kropp/overkropp
  - God strukturell stabilitet
- **Con**:
  - **OpenPose er ikke aktivt vedlikeholdt** (siste commit 2022)
  - Tung å sette opp (C++/CUDA)
  - Nyere modeller er raskere og bedre

**Alternativer (BEDRE)**:
1. **MMPose** (OpenMMLab)
   - ✅ State-of-the-art
   - ✅ Aktivt vedlikeholdt
   - ✅ Mange pretrained modeller
   - ✅ Python-first
   
2. **RTMPose** (Real-Time Multi-Person Pose)
   - ✅ Ekstremt rask
   - ✅ God presisjon
   - ✅ Del av MMPose-familien

3. **Mediapipe Pose** (upgrade)
   - ✅ Allerede i stack
   - ⚠️ Kan være nok hvis OpenPose-kvalitet ikke trengs

**Anbefaling**: 
- **Bytt fra OpenPose til RTMPose/MMPose**
- Hvis du virkelig vil ha OpenPose: ok, men vær forberedt på setup-problemer

---

#### ✅ VALG: MediaPipe Hands

**Min vurdering**: ⭐⭐⭐⭐ Good
- Fortsatt et solid valg
- 21 landmarks er tilstrekkelig

**Alternativer**:
1. **MMPose WholeBody** (inkluderer hands)
   - ✅ Kan gi bedre integrasjon hvis du bruker MMPose for kropp
2. **Hamer** (3D hand mesh)
   - ✅ Full 3D mesh, ikke bare landmarks
   - ❌ Tyngre, kanskje overkill

**Anbefaling**: Behold MediaPipe Hands, men test MMPose WholeBody hvis du bytter body-model.

---

#### ✅ VALG: MediaPipe FaceMesh

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
- 468 landmarks er mer enn nok
- Stabil og rask

**Ingen bedre alternativer for dette use case.**

---

### 🔄 Temporal stabilisering

#### ✅ VALG: EMA + velocity clamp + confidence gating

**Min vurdering**: ⭐⭐⭐⭐ Good pragmatic approach
- Enkel og effektiv
- Fungerer godt for tegnspråk

**Alternativer (mer avansert)**:
1. **Kalman filter**
   - ✅ Bedre teoretisk fundament
   - ⚠️ Krever tuning per signal
   
2. **OneEuro filter**
   - ✅ Designet for HCI (Human-Computer Interaction)
   - ✅ Adaptiv til velocity
   - ⚠️ Litt mer kompleks
   
3. **LSTM-based smoothing**
   - ✅ Lært fra data
   - ❌ Krever trening
   - ❌ Overkill for MVP

**Anbefaling**: 
- Start med EMA (som foreslått)
- Hvis jitter fortsatt er problem: test OneEuro (det er en liten modul)

---

## 🎮 Unreal/MetaHuman-integrasjon

### ✅ VALG: MetaHuman som primær avatar

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
- Best-in-class ansiktsrigg
- God dokumentasjon
- Fremtidssikker i Unreal-økosystemet

**Anbefaling**: Korrekt valg. Hold canonical format slik at andre avatarer kan legges til senere.

---

### ✅ VALG: Control Rig for armer/hender, Curves for ansikt

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
- IK for armer = stabilitet
- FK for fingre = presisjon
- Curves for ansikt = MetaHuman-standard

**Anbefaling**: Perfekt. Følg denne strategien.

---

### ⚠️ VALG: Unreal Python scripts for import

**Min vurdering**: ⭐⭐⭐⭐ Good but fragile
- **Pro**:
  - Scriptbare
  - Automatiserbare
  - Versjonskontrollerbare
- **Con**:
  - Unreal Python API er noe ustabil mellom versjoner
  - Ikke all funksjonalitet tilgjengelig via Python
  - Blueprint/C++ kan noen ganger være nødvendig

**Alternativer**:
1. **FBX import + manual rigging**
   - ⚠️ Ikke skalerbart for 9000 ord
   
2. **Unreal Automation Tools (C++)**
   - ✅ Mer robust
   - ❌ Mye tyngre utvikling

**Anbefaling**: 
- Behold Python for MVP
- Isoler Unreal API-calls i egne funksjoner
- Ha en TODO-seksjon for versjonsspesifikke issues
- Test grundig på målversjon (UE 5.3+)

---

## 📊 Output-formater

### ✅ VALG: JSONL.gz (line-delimited JSON, gzipped)

**Min vurdering**: ⭐⭐⭐⭐ Good
- **Pro**:
  - Streaming-vennlig (frame-by-frame)
  - Human-readable (når decompressed)
  - Lett å parse
- **Con**:
  - Ikke optimal for analytics
  - Større enn binære formater

**Alternativer**:
1. **Parquet**
   - ✅ Kolonne-basert → rask for analytics
   - ✅ Bedre kompresjon
   - ⚠️ Mindre menneskelig lesbar
   
2. **MessagePack** eller **CBOR**
   - ✅ Binær JSON-ekvivalent
   - ✅ Raskere parsing
   - ❌ Ikke human-readable

**Anbefaling**: 
- **Hybrid**: 
  - Primært format: **Parquet** (for effektivitet)
  - Debug/export format: JSONL (for lesbarhet)
- ELLER: Behold JSONL.gz, det er "good enough" for 9000 videoer

---

## 🗂️ Filstruktur

### ✅ VALG: Per-word export packages

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
```
exports/
  ananas/
    ananas-3/
      tracking_v2.jsonl.gz
      meta.json
      unreal_import.py
```
- Lett å flytte
- Lett å re-prosessere enkeltord
- Git-friendly (kan committes per ord)

**Anbefaling**: Perfekt struktur.

---

## 🔧 Development workflow

### ✅ VALG: Typer for CLI

**Min vurdering**: ⭐⭐⭐⭐⭐ Excellent
- Typer er moderne, type-safe, og autodokumenterende
- Bedre enn argparse eller click

**Anbefaling**: Behold.

---

### ⚠️ VALG: Cursor som primær utviklingsmetode

**Min vurdering**: ⭐⭐⭐⭐ Good but requires discipline
- **Pro**:
  - Rask iterasjon
  - God kode-generering for boilerplate
  - Kan håndtere store prompts
- **Con**:
  - AI kan generere subtile bugs
  - Trenger god testing
  - Kan "overdrive" abstraksjon

**Anbefaling**:
- **JA** til Cursor for struktur og boilerplate
- **ALLTID** review generert kode
- **SKRIV TESTER** for core logic (ikke stol blindt på AI)
- **BRUK TYPER** (mypy) for å fange feil tidlig

---

## 🚀 Deployment

### ✅ VALG: Ingen "deployment" (lokal workstation)

**Min vurdering**: ⭐⭐⭐⭐ Correct for MVP
- Holder det enkelt
- Ingen infrastruktur-kompleksitet

**Fremtidige alternativer**:
1. **Docker container**
   - ✅ Reproducerbar miljø
   - ✅ Lett å flytte til andre maskiner
   
2. **Kubernetes** (hvis mange maskiner)
   - ⚠️ Overkill for nå

**Anbefaling**: 
- MVP: Bare virtualenv/conda
- Fremtid: Docker-container for portabilitet

---

## 📈 Summary: Anbefalte endringer

### 🔴 Høy prioritet (vurder å endre)
1. **Database**: Vurder SQLite eller ren Postgres i stedet for Supabase (enklere for lokal batch)
2. **Body tracking**: Bytt fra OpenPose til RTMPose/MMPose (modernere, bedre vedlikeholdt)

### 🟡 Medium prioritet (kan vurderes)
3. **Output format**: Parquet i stedet for JSONL (mer effektivt, men mindre readable)
4. **Temporal smoothing**: Test OneEuro filter hvis EMA ikke er nok

### 🟢 Lav prioritet (ok som det er)
5. Alt annet er solide valg for MVP

---

## 🎯 Min overordnede vurdering

**Prosjektet er veldesignet og realistisk.** 

De fleste valg er gode. Mine hovedanbefalinger:
1. Forenkle database-setup (SQLite for MVP)
2. Bruk moderne pose-tracking (RTMPose > OpenPose)
3. Hold ting enkelt i Phase 1, optimaliser i Phase 2

**Prosjektet er 100% gjennomførbart med Cursor.**

---

**Neste: [02_ARCHITECTURE.md](02_ARCHITECTURE.md) →**
