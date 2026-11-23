# Fraud Shield — Architecture Specification
### *Detect. Connect. Dismantle.*
**Rajasthan Police Hackathon 2026 · Problem Statement 01**  
**Team: Dholakpurwale · MIT Academy of Engineering**

---

## 1. Dual Execution Architecture

Fraud Shield features a robust dual execution model:
1. **Standalone Offline Client Engine (`index.html`):** Zero-dependency, pure client-side execution running directly via `file:///` in any modern browser. Features full client-side URL lookalike parsing, SMS social engineering detection, QR code UPI collect trap decoding, APK manifest static analysis, Canvas gauge and graph rendering, Web Speech API audio warnings, and jsPDF document generation.
2. **Full-Stack Microservice Engine (`/backend`):** High-throughput FastAPI service with SQLite database, scikit-learn machine learning classifiers, NetworkX graph connected components, and Server-Sent Events (SSE) live threat feed.

```mermaid
flowchart TD
    subgraph Client["👤 User / Law Enforcement Officer"]
        WEB["Desktop / Mobile Browser"]
    end

    subgraph DualModes["⚙️ Deployment Modes"]
        MODE_OFFLINE["Mode 1: 100% Offline Standalone\n(Double-click index.html · No Servers)"]
        MODE_FULL["Mode 2: FastAPI + Uvicorn + SQLite\n(make run / run.bat · Port 8000)"]
    end

    subgraph Engines["🛡️ Multi-Signal Detection Engines"]
        URL_ENG["URL Lookalike & TLD Engine\nRapidfuzz + Homoglyph + Brand Dictionary"]
        SMS_ENG["SMS Smishing Classifier\nTF-IDF + Hinglish/Devanagari Lexicon"]
        APK_ENG["APK Static Analyzer\nManifest Bytecode Permissions & C2 Flags"]
        QR_ENG["QR Code Fraud Inspector\nUPI Payment URI & Trap Decoder"]
    end

    subgraph Intel["🚔 Police Intelligence & Takedown"]
        NETX["NetworkX Graph Clustering\nConnected Components + Shared IoCs"]
        MAP_ENG["Leaflet Hotspot Threat Map\nCentroid Coordinates for Rajasthan Districts"]
        CRPC["Statutory Legal Notice Generator\nSection 91 CrPC + Section 79(3)(b) IT Act"]
        SYND["Interstate Syndicate Profiler\nMewat, JVVNL, RTO, Digital Arrest"]
    end

    WEB --> MODE_OFFLINE
    WEB --> MODE_FULL

    MODE_OFFLINE --> Engines
    MODE_FULL --> Engines

    Engines --> Intel
    Intel --> PDF_EXP["jsPDF / ReportLab Dossiers & FIR Drafts"]
```

---

## 2. Citizen Checker Data Flow

```mermaid
sequenceDiagram
    participant Citizen as 👤 Citizen
    participant UI as 🖥️ Fraud Shield UI
    participant Scanner as 🔍 Multi-Signal Analyzer
    participant Audio as 🔊 Web Speech Engine
    participant Legal as ⚖️ NCRP Grievance Module

    Citizen->>UI: Submit URL, SMS text, APK, or QR Payload
    UI->>Scanner: Run Hybrid ML + Rule-based Feature Extraction
    Scanner->>Scanner: Calculate 0.6*ML + 0.4*Rules Score
    Scanner->>Scanner: Extract IoCs (Phones, Domains, UPI VPAs)
    Scanner-->>UI: Risk Score (0-100), Verdict, Explainable Reason Chips
    UI-->>Citizen: Render Animated Gauge + Threat Weights
    Citizen->>UI: Click "Listen Police Audio Warning"
    UI->>Audio: Trigger SpeechSynthesis in Hindi / English
    Audio-->>Citizen: Audio Speech Warning Broadcast
    Citizen->>UI: Click "Download NCRP Complaint PDF"
    UI->>Legal: Compile Official Forensic Grievance Document
    Legal-->>Citizen: Deliver Signed PDF for 1930 / cybercrime.gov.in
```

---

## 3. NetworkX Coordinated Campaign Clustering

```mermaid
flowchart LR
    R1["Citizen Report A\nDomain: sbi-kyc-update.xyz"] -->|"shared domain"| G["NetworkX Coordinated Graph"]
    R2["Citizen Report B\nDomain: sbi-kyc-update.xyz\nPhone: +91 9876543210"] -->|"shared domain"| G
    R3["Citizen Report C\nPhone: +91 9876543210\nUPI: sbikyc@fake"] -->|"shared caller"| G
    R4["Citizen Report D\nUPI: sbikyc@fake"] -->|"shared extortion VPA"| G
    R5["Citizen Report E\nTF-IDF Cosine Similarity ≥ 0.7"] -->|"semantic link"| G

    G --> CAMP["🚨 Coordinated Campaign Dossier\n'SBI KYC Scam – Jaipur Cluster'"]
    CAMP --> NOTICE["⚖️ Section 91 Cr.P.C. Registrar Notice"]
    CAMP --> DOSSIER["📄 Forensic Evidence PDF"]
```

---

## 4. Multi-Signal Scoring Formulation

$$\text{Final Risk Score} = 0.6 \times (\text{ML Model Probability} \times 100) + 0.4 \times (\text{Rules Weight Hit})$$

### Risk Stratification:
- **0 – 39: Safe (Green)** &rarr; Standard domain/sender telemetry, verified SSL/TLS, no social engineering urgency keywords.
- **40 – 69: Suspicious (Orange)** &rarr; Unverified sender, generic shorteners, moderate brand resemblance, unencrypted HTTP.
- **70 – 100: High Risk (Red)** &rarr; Brand lookalike/typosquatting &ge; 65%, suspicious TLD (`.xyz`, `.top`, `.click`), social engineering keywords, dangerous APK permissions (`READ_SMS` + `SYSTEM_ALERT_WINDOW`), or deceptive UPI refund collect request.

---

## 5. Security & Safety Compliance

- **Zero Untrusted Execution:** APK files are subjected strictly to static manifest analysis. Binaries are never executed or emulated.
- **100% Offline Capability:** All ML weights, lookup tables, and threat signatures reside locally. No external paid APIs or telemetry keys are required.
- **Synthetic Data Governance:** All complaints, phone numbers, and names are synthetically generated for hackathon benchmarking. The `⚗️ Synthetic demo data` watermark is enforced across all dashboard views.
