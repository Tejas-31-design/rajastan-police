# 🛡️ Fraud Shield
### *Detect. Connect. Dismantle.*
**Rajasthan Police Hackathon 2026 · PS01: Cyber Fraud, Phishing & Malicious Apps**  
**Team: Dholakpurwale · MIT Academy of Engineering**  
*Members: Tejas Bhadait, Jatin Sonawane, Bhavarth Baviskar, Shreyash Dube*

> ⚠️ **All data is entirely SYNTHETIC.** No real personal data is stored or used anywhere in this project. All dashboards and reports display the `⚗️ Synthetic demo data` badge.

---

## 🌟 Instant 1-Click Launch (Zero Setup Required)

**Fraud Shield** is built with a dual architecture:
1. **100% Offline Standalone App:** Simply **double-click [`index.html`](file:///C:/Users/bhada/OneDrive/Desktop/rajastan%20police/index.html)** in any web browser (Chrome, Edge, Firefox, Brave) on any computer. No command line, Python, Node.js, server, or API keys needed!
2. **Full-Stack Microservice App:** Run `run.bat` or `make run` to spin up the FastAPI + SQLite backend with Server-Sent Events (SSE) live feed on `http://localhost:8000`.

---

## 🏆 Game-Winning Features (PS01 Specialized)

1. **🔍 Multi-Signal Explainable AI Citizen Checker:**
   - **🌐 URL Scanner:** Analyzes TLD risk (.xyz, .top, .click), brand lookalike metric via Rapidfuzz against top Indian brands (SBI, HDFC, ICICI, Axis, Paytm, PhonePe, IRCTC, RTO, JVVNL), homoglyphs/character substitutions, TLS encryption status, and domain registration age.
   - **💬 SMS Smishing Classifier:** Identifies scam themes (KYC threat, JVVNL electricity cutoff, lucky draw, WFH job, parcel hold) with full multilingual support for **English, Hindi (Devanagari), and Hinglish**. Extracts phone numbers, URLs, and UPI IDs.
   - **📱 APK Static Analyzer:** Safe sandboxed static bytecode & AndroidManifest inspector. Flags critical threats: `READ_SMS` + `RECEIVE_SMS` (OTP theft), `SYSTEM_ALERT_WINDOW` (credential overlay attack), `BIND_ACCESSIBILITY_SERVICE` (keylogging/touch hijacking), device admin abuse, and hardcoded C2 servers without ever executing binaries.
   - **📷 QR Code Fraud Scanner (UPI Trap Detector):** Detects fraudulent UPI collect requests disguised as refunds/cashback. Features the statutory police rule: *"You NEVER enter your UPI PIN or scan a QR code to RECEIVE money!"*

2. **🔊 Multilingual AI Voice Speech Advisory:**
   - 1-click voice audio advisory in Hindi and English using the browser's native Web Speech API. Ensures elderly and rural citizens can listen to life-saving police advisories even if they cannot read text.

3. **📊 Rajasthan Police Command Dashboard:**
   - Real-time KPIs (Reports Today, Active Campaigns, High-Risk Domains, Top District, Total Reports, Resolved).
   - **Interactive Leaflet District Threat Map:** Visualizes centroids across Jaipur, Jodhpur, Udaipur, Bikaner, Kota, Alwar with threat radius proportional to report volume.
   - 14-day complaints trend line chart.
   - **⚡ "Simulate Threat Surge" Button:** Live tactical simulation demonstrating real-time incoming attacks, audio alerts, pulsing radar markers, and automatic NetworkX clustering into campaign dossiers.

4. **🕵️ Interstate Cyber Crime Syndicate Profiler:**
   - In-depth tactical intelligence dossiers on major syndicates active in Rajasthan:
     - **Mewat (Bharatpur/Alwar/Deeg) Vehicle & Army Impersonation Ring**
     - **JVVNL / AVVNL Power Cutoff Smishing Ring**
     - **RTO e-Challan APK Trojan Ring**
     - **Digital Arrest & Fake CBI/ED Video Call Extortion Syndicate**
   - Full mapping to the **MITRE ATT&CK for Cybercrime Matrix** (T1566, T1204, T1411, T1499, T1656) with law enforcement countermeasures (TAFCOP SIM deactivation, IMEI blacklisting).

5. **🔗 NetworkX Campaign Graph & IoC Inspector:**
   - Force-directed interactive canvas connecting citizen reports to shared IoCs (🌐 Domains, 📞 Phone Numbers, 💸 UPI VPAs).
   - Node filtering buttons: *All, Domains, Phones, UPI VPAs, Citizen Reports*.
   - Clickable Node Forensic Inspector with 1-click addition to legal seizure notices.

6. **⚖️ Statutory Legal Takedown Notice Generator:**
   - Pre-formatted statutory notices under **Section 91 Cr.P.C.** for registrar DNS seizure and **Section 79(3)(b) IT Act** for telecom SIM blocking and NPCI UPI account freezing.
   - 1-click **"Download Official PDF"** formatted for immediate police dispatch.

7. **🛡️ Cyber Suraksha Citizen Quiz & Certificate:**
   - 3 interactive scenario challenges covering fake challans, OLX QR traps, and electricity bill APKs.
   - Generates an official, personalized **"Rajasthan Police Cyber Suraksha Warrior Certificate"** PDF upon completion.

8. **📄 1-Click NCRP Citizen Complaint PDF:**
   - Citizens can download a pre-filled grievance statement formatted for direct submission to the National Cybercrime Reporting Portal (cybercrime.gov.in) or local police stations.

---

## ⏱️ 2-Minute Winning Presentation Script

1. **Step 1: Citizen Safety (0:00 - 0:35)**
   - Double-click [`index.html`](file:///C:/Users/bhada/OneDrive/Desktop/rajastan%20police/index.html).
   - Click **"🎣 Phishing URL"** sample (`sbi-kyc-update.xyz`) &rarr; Click **"Analyze Now"**.
   - Show the animated 0-100 risk gauge (88% High Risk), explainable signal chips, and breakdown bars.
   - Click **"🔊 Listen Police Audio Warning"** &rarr; Browser speaks the official police warning out loud in Hindi/English!
   - Switch to **"📷 QR Code Scanner"** &rarr; Click **"💸 Fake Refund QR"** &rarr; Explain how fraudsters use UPI collect requests to deceive citizens.
   - Click **"📄 Download NCRP Complaint PDF"** to demonstrate immediate citizen grievance filing.

2. **Step 2: Police Intelligence & Live Attack Surge (0:35 - 1:15)**
   - Click **"Police Dashboard"** in the top navigation.
   - Show the interactive Rajasthan District Threat Map (Jaipur, Jodhpur, Bikaner, Udaipur).
   - Click **"⚡ Simulate Threat Surge"** &rarr; Watch live tactical audio pulses, pulsing radar circles on the map, and dynamic KPI increments demonstrating real-time ingestion.
   - Filter by district (e.g. *Jaipur* or *Bikaner*) &rarr; Map smoothly flies to the district with filtered campaigns.

3. **Step 3: NetworkX Campaign Clustering & Legal Dismantling (1:15 - 1:45)**
   - Click **"Graph View &rarr;"** on *SBI KYC Scam – Jaipur Cluster*.
   - Explore the NetworkX force-directed graph. Click filter chips (*Phones*, *UPI*, *Domains*).
   - Click on any indicator node &rarr; **Node Intelligence Inspector** displays connected incident count.
   - Click **"📄 Export Evidence PDF"** &rarr; Demonstrates instant forensic dossier generation for court evidence.
   - Navigate to **"Legal Notices (CrPC)"** &rarr; Show the editable Section 91 CrPC notice ready for domain registrar and telecom blocking.

4. **Step 4: Syndicate Profiler, Quiz & Closing (1:45 - 2:00)**
   - Open **"Syndicate MO Profiler"** &rarr; Highlight Mewat and JVVNL syndicate tracking with MITRE ATT&CK mapping.
   - Open **"Cyber Suraksha Quiz"** &rarr; Show how citizen education directly prevents fraud before it occurs.
   - Conclude with team tagline: *"Detect. Connect. Dismantle."*

---

## 🧪 Automated Test Suite (35 Tests Passing)

Verify the backend engines with pytest:
```bash
# Run 1-click test launcher on Windows:
test.bat

# Or run via pytest directly:
cd backend
pytest tests/ -v
```
**Results:** `35 passed, 4 warnings in 2.43s`
- `test_url_analyzer.py`: Lookalike brand detection, typosquatting, TLD scoring, homoglyphs.
- `test_sms_classifier.py`: Hindi, Hinglish, English classification, entity extraction (phones, URLs, UPIs).
- `test_clustering.py`: NetworkX graph clustering, cosine similarity merge &ge; 0.7, incremental updates.
- `test_api.py`: FastAPI endpoints, error handling, synthetic data validation.

---

## 👥 Team: Dholakpurwale
**MIT Academy of Engineering** · Rajasthan Police Hackathon 2026
- **Tejas Bhadait** – ML & Full-Stack Lead
- **Jatin Sonawane** – Frontend & UI/UX
- **Bhavarth Baviskar** – Clustering & Graph Architect
- **Shreyash Dube** – PDF, Security & Integration
