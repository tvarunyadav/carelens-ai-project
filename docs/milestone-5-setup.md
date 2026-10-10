# CareLens AI Milestone 5 Setup & Verification Guide

**Date:** October 9, 2026  
**Feature Branch:** `feature/auth-patients`

---

## 1. Milestone 5 Capabilities Overview

1. **Combined History & Pending Order Answering**:
   - Responds to multi-part questions covering both fertility cycles (dates, metrics) and outstanding pending orders (requested date, non-implication of results).
   - Validated against Sophia Patel's live DB records: Cycle 1 (May 1–28, 2026), FET cycle (July 10–Sept 1, 2026), Pending Karyotype Panel (Requested Sept 15, 2026).

2. **Multilingual Speech-to-Text Voice Input**:
   - Browser Web Speech Recognition API (`SpeechRecognition` / `webkitSpeechRecognition`) integrated with zero paid third-party dependencies.
   - Microphone toggle button beside question input field.
   - Input language toggle: English (`en`) / தமிழ் (`ta-IN`).
   - Visual listening state (pulse animation), stop controls, clear controls, and editable transcript before submitting.
   - Microphone access requested only upon user click.
   - Resource cleanup on patient change, tab change, or logout.
   - Typed input fallback for unsupported browsers or permission denial.

3. **Cross-Language Retrieval & Answer Generation**:
   - Translates / normalizes non-English (Tamil / mixed) queries into English via LLM before computing 384-dimensional embeddings using `BAAI/bge-small-en-v1.5`.
   - Supports answer output in English (`en`) or Tamil (`ta`).
   - Maintains evidence provenance, citation IDs (`[EV-1]`, `[EV-2]`), and date/numeric accuracy across languages.
   - Retains original query in audit logs alongside normalized English translation.

4. **User-Triggered Audio Readout (Text-to-Speech)**:
   - Web Speech Synthesis API (`SpeechSynthesisUtterance`) integration.
   - User-triggered "Read Answer" button on AI answer cards.
   - Never autoplays.
   - Graceful fallback notice if Tamil TTS voice is not pre-installed in user's browser.

5. **Restricted Audit Persistence (Migration 006)**:
   - `database/migrations/006_restricted_audit_policies.sql` enforces append-only audit telemetry (`staff_id = auth.uid()`).
   - Anonymous access (`anon`) is completely revoked.

---

## 2. Verification Commands

```bash
# Backend Test Suite
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v

# Frontend Production Build
cd ../frontend
npm run build
```
