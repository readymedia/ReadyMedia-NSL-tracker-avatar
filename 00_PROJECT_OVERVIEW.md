# Open NSL Avatar – Prosjektoversikt

## 🎯 Executive Summary

**Open NSL Avatar** er et lokalt kjørende system som konverterer ekte videoer av norsk tegnspråk (NSL) til høypresisjons animasjoner på MetaHuman-avatarer i Unreal Engine.

### Kjerneverdier
- ✅ **Autentisitet**: Motion capture fra virkelige tegnspråkutøvere, ikke generativ AI
- ✅ **Presisjon**: State-of-the-art tracking for hender, ansikt og kropp
- ✅ **Skalerbarhet**: Designet for 9000+ tegn
- ✅ **Lokalt**: Ingen cloud-avhengigheter (GDPR-vennlig)
- ✅ **Åpent**: Ikke låst til én leverandør eller plattform

### Hva dette IKKE er
- ❌ Ikke tekst-til-tegnspråk (generativ)
- ❌ Ikke cloud-tjeneste
- ❌ Ikke "fake signing" - dette er motion truth

---

## 📊 Datasett

**Kilde**: minetegn.no  
**Antall**: 9000+ videoer (én per ord/variant)  
**Lokasjon**: `D:\tegnspråk\minetegn_videos\`  
**Manifest**: `D:\tegnspråk\minetegn_manifest_app_excel.csv`

### Video-karakteristikk
- Nøytral bakgrunn (blå/svart)
- Konsistent framing og startposisjon
- Varierende oppløsning (eldre = lavere kvalitet)
- Stabil kameravinkel
- Hender starter i nøytral posisjon (→ bra for auto-trimming)

---

## 🏗️ Arkitektur (overordnet)

```
Video (MP4)
    ↓
Preprosessering (normalisering, ROI, trimming)
    ↓
Multi-pass tracking (pose + hender + ansikt)
    ↓
Temporal stabilisering + fusjon
    ↓
Canonical NSL skeleton + face features
    ↓
MetaHuman Control Rig mapping
    ↓
Unreal AnimSequence + Curves
    ↓
Triggerbar avatar per ord
```

**Alt kjører lokalt på PC med NVIDIA GPU.**

---

## 📚 Dokumentasjonsstruktur

### Kjernefilter (må leses i rekkefølge)
1. **[01_REQUIREMENTS.md](01_REQUIREMENTS.md)** – Mål, scope, leveranser
2. **[02_ARCHITECTURE.md](02_ARCHITECTURE.md)** – Teknisk arkitektur og dataflyt
3. **[03_TECH_STACK.md](03_TECH_STACK.md)** – Verktøy, biblioteker, valg
4. **[04_TRACKING_PIPELINE.md](04_TRACKING_PIPELINE.md)** – Tracking-modeller og algoritmer
5. **[05_DATABASE_SCHEMA.md](05_DATABASE_SCHEMA.md)** – Supabase struktur
6. **[06_OUTPUT_FORMATS.md](06_OUTPUT_FORMATS.md)** – Data-formater og konvensjoner
7. **[07_METAHUMAN_MAPPING.md](07_METAHUMAN_MAPPING.md)** – Control Rig mapping (NSL-optimalisert)
8. **[08_UNREAL_INTEGRATION.md](08_UNREAL_INTEGRATION.md)** – Unreal import og AnimSequence
9. **[09_IMPLEMENTATION_PHASES.md](09_IMPLEMENTATION_PHASES.md)** – Utviklingsplan (Phase 1, 2, 2.1)
10. **[10_CURSOR_PROMPTS.md](10_CURSOR_PROMPTS.md)** – Master prompts for hver fase

### Støttedokumenter
- **[TECH_DECISIONS.md](TECH_DECISIONS.md)** – Evaluering av valg + alternativer
- **[QUALITY_SCORING.md](QUALITY_SCORING.md)** – Kvalitetsscore-algoritmer
- **[BATCH_OPTIMIZATION.md](BATCH_OPTIMIZATION.md)** – Batch-strategier for 9000+ filer
- **[FAILURE_MODES.md](FAILURE_MODES.md)** – Kjente problemer og mitigering

---

## 🚀 Quick Start (for utviklere)

### Forutsetninger
- Windows PC med kraftig NVIDIA GPU (CUDA)
- Python 3.11+
- Docker Desktop (for Supabase local)
- Disk: minimum 500 GB (video + cache + eksport)

### Utviklingsfaser
**Phase 1** (MVP): Basis pipeline + MediaPipe tracking + disk/database  
**Phase 2**: SOTA tracking (OpenPose + MediaPipe + temporal stabilisering)  
**Phase 2.1**: MetaHuman Control Rig mapping + Unreal Python import

### Første steg
1. Les [01_REQUIREMENTS.md](01_REQUIREMENTS.md)
2. Gå gjennom [03_TECH_STACK.md](03_TECH_STACK.md)
3. Bruk [10_CURSOR_PROMPTS.md](10_CURSOR_PROMPTS.md) for implementering i Cursor

---

## 🎓 Bruksområder (langsiktig)

- **Undervisning**: Interaktive læringsapper
- **Kiosker**: Selvbetjening med tegnspråk
- **Spill**: Tilgjengelige NPCer
- **Web**: Three.js-avatarer
- **XR**: VR/AR tegnspråktolking
- **Forskning**: Åpne NSL-ressurser med høy kvalitet

---

## 📖 Viktige prinsipper

### Motion truth, ikke gjetning
Dette prosjektet ekstraherer ekte bevegelse fra virkelige tegnspråkutøvere. Ingen generative modeller som "finner på" tegn.

### Avatar-agnostisk
Selv om MetaHuman er førsteprioritet, er arkitekturen designet slik at:
- Canonical skeleton kan mappes til andre rigger
- Data kan brukes i andre motorer (Blender, Unity, Three.js)

### Kvalitet over kvantitet
Systemet skal:
- Detektere dårlig tracking
- Score kvalitet per ord
- Tillate re-prosessering med bedre modeller senere

---

## 📝 Status og roadmap

### Ferdigstilt (før Cursor)
- [x] Dataset nedlastet (9000+ videoer)
- [x] Manifest CSV laget
- [x] Konseptvalidering

### Neste (Cursor-implementering)
- [ ] Phase 1: Basis pipeline
- [ ] Phase 2: SOTA tracking
- [ ] Phase 2.1: MetaHuman integration
- [ ] Testing med 100+ ord
- [ ] Full batch-kjøring

---

## 🤝 Hvordan bidra / bruke dokumentasjonen

### For AI-assistert koding (Cursor)
Bruk **[10_CURSOR_PROMPTS.md](10_CURSOR_PROMPTS.md)** direkte som input.

### For menneskelige utviklere
Start med **[01_REQUIREMENTS.md](01_REQUIREMENTS.md)** og følg rekkefølgen.

### For teknisk review
Les **[TECH_DECISIONS.md](TECH_DECISIONS.md)** for å evaluere valg.

---

**Neste: Gå til [01_REQUIREMENTS.md](01_REQUIREMENTS.md) →**
