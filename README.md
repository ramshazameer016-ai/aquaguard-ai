# AquaGuard AI

### See it. Understand it. Verify it. Act on it.

AquaGuard AI is an explainable environmental intelligence platform that transforms citizen-reported water observations into evidence-backed water-health intelligence.

Instead of treating a single photograph or citizen observation as proof of pollution, AquaGuard AI combines available citizen, environmental, community, spatial, and temporal evidence to identify potential anomalies, explain how the evidence contributes to the assessment, support human verification, and provide contextual risk outlooks and recommended next actions.

---

## 🚀 Live Demo

### Frontend
https://https://aquaguard-frontend-j6md.onrender.com/

### Backend API
https://aquaguard-api-tmz8.onrender.com

### API Documentation
https://aquaguard-api-tmz8.onrender.com/docs

### GitHub Repository
https://github.com/ramshazameer016-ai/aquaguard-ai

---

## 🌊 Project Overview

Water-quality problems are often noticed first by citizens through changes in water appearance, odor, surface conditions, or other unusual observations.

However, a single observation does not provide enough evidence to establish whether pollution or another environmental anomaly is actually occurring.

AquaGuard AI addresses this challenge through:

- Citizen reporting
- Environmental context
- Community intelligence
- Spatial and temporal relationships
- AI-assisted text and image analysis
- Explainable evidence fusion
- Human verification
- Short-term contextual risk outlook
- Recommended investigation actions
- Authority-oriented monitoring

The complete workflow is:

**Observation → Evidence → Explanation → Verification → Prediction → Action**

---

# 💡 Core Innovation

## Explainable Evidence Fusion

The central innovation of AquaGuard AI is **explainable evidence fusion for citizen-reported water-health anomalies**.

Rather than producing a single unexplained AI score, the system combines multiple evidence components and shows:

- What evidence was available
- Which evidence supported the anomaly
- Which evidence conflicted with the anomaly
- Which evidence was missing
- How much each component contributed
- How reliable the current assessment is
- What should be reviewed next

This makes the system more transparent and auditable than a black-box anomaly score.

---

# 🔎 Evidence Sources

AquaGuard AI is designed to combine multiple evidence sources when available.

### Citizen Evidence

- Observation category
- Citizen description
- Location
- Timestamp
- Optional image reference

### AI-Assisted Evidence

- Text-based anomaly signals
- Image-based visual signals
- Photo/text agreement

### Community Evidence

- Nearby reports
- Reports occurring within a relevant time window
- Independent reporter groups
- Duplicate-report reduction

### Environmental Evidence

- Rainfall
- Dissolved oxygen
- Water temperature
- Environmental trends

### Contextual Evidence

- Spatial relationships
- Temporal patterns
- Historical similarity

The system does not require every source to be available.

Missing evidence is explicitly reported rather than fabricated.

---

# 🧮 Mathematical Explainability

AquaGuard AI does not hard-code the final Evidence Confidence or risk metrics as demonstration values.

**The outputs are computed by deterministic mathematical scoring rules over the evidence available to the system; the architecture-defined maximum weights are fixed parameters, while the actual contributions and final metrics are calculated from the current evidence.**

For example, the photo-and-text component has a defined maximum contribution of 25 points and combines image signal, image quality, and text signal using the architecture-defined formula.

The actual contribution shown on screen is therefore calculated from the evidence available at runtime.

Every contribution comes from a named evidence component, making the assessment auditable.

The system does not add points simply for visual presentation.

If an evidence source is unavailable, its contribution is absent and the system reports the evidence as missing.

---

# 📊 Evidence Confidence

**Evidence Confidence** is an ordinal prioritisation index representing how strongly the available evidence supports a potential aquatic-health anomaly.

It is **not**:

- A probability of pollution
- Proof of toxicity
- A medical diagnosis
- Proof of legal causation
- A guarantee that pollution exists

The dashboard shows the evidence contributions behind the current assessment.

For example:

```text
Evidence Confidence
        ↓
Supporting Evidence
        ↓
Conflicting Evidence
        ↓
Missing Evidence
        ↓
Final Explainable Assessment
````

This allows reviewers to understand not only the score, but also why the score was produced.

---

# 🤖 AI Belief vs Evidence Confidence

AquaGuard AI deliberately separates **Evidence Confidence** from **AI Belief**.

### Evidence Confidence

Answers:

> How strongly does the available evidence support the potential anomaly?

### AI Belief

Considers factors such as:

* Evidence quality
* Agreement between evidence sources
* Source independence
* Evidence completeness

This distinction is important because strong evidence and reliable evidence are not necessarily the same thing.

For example, a single strong-looking observation may contribute evidence, while the overall assessment may still have lower reliability because there are no independent sources.

---

# 👥 Community Intelligence

AquaGuard AI does not simply count the number of reports.

Community evidence considers:

* Spatial proximity
* Temporal proximity
* Independent reporter groups
* Duplicate reports

Multiple reports from the same source should not artificially inflate confidence.

This helps distinguish repeated observations from genuinely independent community evidence.

---

# 🧠 Graceful AI Fallback

AquaGuard AI is designed to continue operating when an AI component is unavailable.

For example:

> If image analysis is unavailable, the system can continue using text and contextual evidence and explicitly mark the photo evidence as missing.

The system does not invent a visual signal that it did not obtain.

This makes the evidence pipeline more robust and transparent.

---

# 🛡️ Responsible AI

AquaGuard AI is designed around responsible evidence interpretation.

The system does **not** claim that a citizen photograph proves toxic pollution.

Instead, it:

* Communicates uncertainty
* Shows missing evidence
* Shows evidence contributions
* Separates contextual risk from probability
* Shows AI calibration status
* Supports investigation rather than replacing it
* Keeps consequential decisions with human reviewers

The AI assessment is therefore intended to support triage, investigation, and evidence review.

---

# 👮 Human-in-the-Loop Verification

A potential anomaly is not automatically treated as confirmed.

The verification workflow allows an authorised reviewer to:

1. Open an event for review
2. Request testing when required
3. Review available evidence
4. Confirm the anomaly
5. Maintain an audit trail

Reviewer actions are recorded so that changes in event status remain traceable.

The principle is:

> **AI supports the decision — it does not silently make the decision.**

---

# 🏛️ Authority Dashboard

The Authority Dashboard provides an operational overview of detected events.

It includes:

* Total events
* Potential events
* Confirmed anomalies
* Events under review
* Event locations
* Evidence assessments
* Risk outlook
* Verification history
* Recommended actions

This allows individual citizen observations to be viewed within a broader operational context.

---

# 📈 Contextual Risk Outlook

AquaGuard AI also provides a short-term **risk outlook** to help prioritize attention.

The risk outlook considers available evidence and event context and produces:

* Risk score
* Risk band
* Direction
* Evidence confidence
* Supporting contextual factors

The system uses categories such as:

* Minimal
* Low
* Moderate
* High

The risk outlook is explicitly a **contextual prioritisation signal**, not a calibrated probability that pollution will occur.

When sufficient information is unavailable, the system avoids fabricating a prediction.

---

# 🧭 Recommended Actions

Based on the current event context, AquaGuard AI can generate human-reviewed recommendations such as:

* Site inspection
* Water sample collection
* Environmental monitoring
* Evidence review
* Authority review

These recommendations are intended to support human decision-making.

They are **not automatically executed consequential interventions**.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   Citizen Report    │
                    │ Location / Text /   │
                    │ Category / Image    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Potential Anomaly  │
                    │       Event         │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐     ┌──────────────┐    ┌──────────────┐
   │ Text Analysis│     │ Vision       │    │ Environmental│
   │              │     │ Analysis     │    │ Context      │
   └──────┬───────┘     └──────┬───────┘    └──────┬───────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Community + Spatial │
                    │ + Temporal Evidence │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Explainable Evidence│
                    │       Fusion        │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌────────────┐  ┌────────────┐  ┌─────────────┐
        │  Evidence  │  │ AI Belief  │  │ Explanation │
        │ Confidence │  │            │  │             │
        └──────┬─────┘  └──────┬─────┘  └──────┬──────┘
               │               │               │
               └───────────────┼───────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Human Verification │
                    │ & Audit Trail       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Contextual Risk     │
                    │ Outlook             │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Recommended Actions │
                    └─────────────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

## AI / Intelligence

* Text analysis
* Vision analysis
* Explainable evidence fusion
* Deterministic mathematical scoring
* Contextual risk calculation

## Database

* PostgreSQL
* PostGIS

## Deployment

* GitHub
* Render
* Render PostgreSQL

---

# 📁 Project Structure

```text
aquaguard-ai/
│
├── ai/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── text_analysis.py
│   │   │   └── vision_analysis.py
│   │   │
│   │   ├── api/
│   │   │   ├── reports.py
│   │   │   ├── events.py
│   │   │   ├── evidence.py
│   │   │   ├── environmental.py
│   │   │   ├── correlation.py
│   │   │   ├── ai.py
│   │   │   ├── dashboard.py
│   │   │   ├── verification.py
│   │   │   ├── one_health.py
│   │   │   └── risk.py
│   │   │
│   │   ├── config/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
│
├── data/
│
├── docs/
│   └── screenshots/
│       ├── 01-citizen-report.png
│       ├── 02-evidence-assessment.png
│       ├── 03-evidence-contributions.png
│       ├── 04-authority-dashboard.png
│       ├── 05-verification-audit.png
│       ├── 06-risk-outlook.png
│       └── 07-recommended-actions.png
│
├── frontend/
│   ├── public/
│   └── src/
│
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

# 🖼️ Screenshots

## Citizen Reporting
<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/ff437424-28bd-43eb-8188-ac6361580a77" />


The citizen reporting interface allows users to provide an observation category, description, location, timestamp, and optional image reference.

---

## Evidence Assessment

<img width="675" height="670" alt="image" src="https://github.com/user-attachments/assets/481599f1-9b75-4a6f-a1f7-b6df83b8b929" />


The evidence assessment shows the current Evidence Confidence and AI Belief together with their interpretation.

---

## Evidence Contributions

<img width="639" height="871" alt="image" src="https://github.com/user-attachments/assets/ecc72a6d-19ab-4472-92ea-7701fb1a6510" />


The contribution panel explains which evidence components supported the assessment and which evidence is missing or conflicting.

---

## Authority Dashboard

<img width="1333" height="953" alt="image" src="https://github.com/user-attachments/assets/7d80ad16-6c71-4cd9-aff0-58ef46c813d9" />


The dashboard provides an operational overview of potential, confirmed, and under-review events.

---

## Verification and Audit Trail



Human verification actions are recorded through the audit trail.

---

## Risk Outlook


The contextual risk outlook provides a risk band, direction, and supporting context.

---

## Recommended Actions


The system can generate human-reviewed recommendations such as site inspection, water sampling, and environmental monitoring.

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/d32ec261-81d4-483f-b442-454d698ca137" />





---

# 🚀 Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/ramshazameer016-ai/aquaguard-ai.git
cd aquaguard-ai
```

---

## 2. Backend Setup

Create and activate a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

Start the backend:

```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001
```

Backend:

```text
http://127.0.0.1:8001
```

API documentation:

```text
http://127.0.0.1:8001/docs
```

---

# 💻 Frontend Setup

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔐 Environment Configuration

The frontend supports the following environment variable:

```text
VITE_API_BASE_URL
```

For local development:

```text
VITE_API_BASE_URL=http://127.0.0.1:8001
```

For the deployed frontend:

```text
VITE_API_BASE_URL=https://aquaguard-api-tmz8.onrender.com
```

Sensitive configuration should remain in environment variables and should not be committed to GitHub.

---

# ☁️ Deployment Architecture

AquaGuard AI is deployed using GitHub and Render.

```text
                    GitHub Repository
                           │
                           ▼
                       ┌───────┐
                       │ Render│
                       └───┬───┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        PostgreSQL     FastAPI API    React Frontend
         + PostGIS       Backend        Static Site
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                    AquaGuard AI
```

Backend:

```text
https://aquaguard-api-tmz8.onrender.com
```

API documentation:

```text
https://aquaguard-api-tmz8.onrender.com/docs
```

---

# 🔬 Demonstration Workflow

A typical demonstration follows this sequence:

### Step 1 — Citizen Observation

A citizen reports an unusual water condition.

### Step 2 — Event Creation

The observation is registered and linked to a potential anomaly event.

### Step 3 — AI Assessment

Text and image-related evidence are analyzed when available.

### Step 4 — Evidence Fusion

Available environmental, community, spatial, and temporal evidence is combined.

### Step 5 — Explanation

The system displays:

* Evidence Confidence
* AI Belief
* Supporting evidence
* Conflicting evidence
* Missing evidence
* Evidence quality
* Source independence

### Step 6 — Authority Review

An authorised reviewer opens the event for review.

### Step 7 — Verification

The reviewer can confirm the anomaly after reviewing the available evidence.

### Step 8 — Risk Outlook

The system provides a contextual short-term risk outlook.

### Step 9 — Recommended Actions

The system generates human-reviewed recommendations.

---

# 📌 Key Design Principles

### 1. Evidence Before Conclusions

AquaGuard AI treats observations as evidence requiring investigation rather than automatic proof of pollution.

### 2. Explainability

Every score should be traceable to named evidence components.

### 3. No Fabricated Evidence

Missing information is represented as missing.

### 4. Independent Community Evidence

Repeated reports from the same source should not artificially inflate evidence.

### 5. Graceful Degradation

If one AI component fails, available evidence from other components can still be used.

### 6. Human Oversight

Consequential decisions remain under authorised human control.

### 7. Responsible Communication

The platform avoids claiming toxicity, pollution certainty, medical diagnosis, or legal causation from insufficient evidence.

---

# ⚠️ Responsible Use and Limitations

AquaGuard AI is a prototype decision-support and environmental intelligence platform.

Its outputs should be interpreted as evidence-based prioritisation signals rather than definitive environmental measurements.

In particular:

* Citizen observations may be incomplete or subjective.
* AI image signals may be uncalibrated.
* Environmental data may be simulated or contextual depending on the deployment.
* Evidence Confidence is not a probability.
* Risk Outlook is not a calibrated prediction probability.
* A visual observation alone cannot establish toxicity.
* Human review remains necessary before consequential action.
* Real-world environmental validation requires appropriate sampling and domain expertise.

---

# 🔮 Future Development

Potential future improvements include:

* Real-time environmental data integration
* Additional water-quality sensor integration
* Larger community reporting networks
* Improved image-model calibration
* Behavioral and environmental drift detection
* More historical environmental datasets
* Advanced spatial-temporal modeling
* Mobile citizen reporting
* Improved authority workflows
* Expanded One Health contextual assessment
* Field validation with environmental experts

---

# 🎯 Why AquaGuard AI?

AquaGuard AI is designed around a simple principle:

> **Do not just produce an AI score. Show the evidence behind it.**

The platform connects:

**Citizen observations**

↓

**Multi-source evidence**

↓

**Mathematical explainability**

↓

**Human verification**

↓

**Contextual risk outlook**

↓

**Recommended action**

This creates an end-to-end workflow for turning community observations into transparent, reviewable environmental intelligence.

---

# 🏆 Project Highlights

* Explainable evidence fusion
* Multi-source environmental context
* Citizen-centered reporting
* Community intelligence
* Independent-source consideration
* AI-assisted text and image analysis
* Deterministic mathematical scoring
* Evidence contribution explanations
* Evidence Confidence
* Separate AI Belief assessment
* Missing-evidence reporting
* Graceful AI fallback
* Human verification
* Audit trail
* Authority dashboard
* Contextual risk outlook
* Human-reviewed recommended actions
* PostgreSQL/PostGIS backend
* FastAPI REST API
* React frontend
* Cloud deployment using Render

---

# 🔗 Project Links

**GitHub Repository**

[https://github.com/ramshazameer016-ai/aquaguard-ai](https://github.com/ramshazameer016-ai/aquaguard-ai)

**Live Frontend**

https://https://aquaguard-frontend-j6md.onrender.com/


**Backend API**

[https://aquaguard-api-tmz8.onrender.com](https://aquaguard-api-tmz8.onrender.com)

**API Documentation**

[https://aquaguard-api-tmz8.onrender.com/docs](https://aquaguard-api-tmz8.onrender.com/docs)

---

# 👥 Project

**AquaGuard AI**

### See it. Understand it. Verify it. Act on it.

Built as an environmental intelligence and explainable evidence-fusion prototype for citizen-reported water-health anomalies.

````


