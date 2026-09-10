# Nexus Resilience AI

> **Predict. Understand. Act. Before Risk Becomes Loss.**

Nexus Resilience AI is an agentic AI-powered operational resilience platform designed to help organizations identify emerging operational risk, understand why it is occurring, prioritize facilities, and support timely intervention.

The platform combines **Google Cloud, BigQuery, Gemini, Google ADK, predictive analytics, and executive visualization** into a unified decision-support workflow.

---

## 🎯 What It Does

Nexus Resilience AI turns operational data into decision-ready intelligence:

```text
OBSERVE → DETECT → PREDICT → EXPLAIN → RECOMMEND → ACT

It helps decision-makers answer:

What is happening?
Which facility needs attention first?
Why is it a priority?
What evidence supports the decision?
What does the prediction indicate?

🚨 Problem

Operational environments generate large volumes of information across:

Energy consumption
Equipment performance
Production
Environmental conditions
Operating costs
Maintenance
Inventory
Demand
Waste
Carbon emissions

The challenge is transforming these signals into trusted, explainable, actionable intelligence.

Nexus Resilience AI addresses this by connecting predictive analytics with an AI agent and an executive dashboard.

💡 Solution

The platform provides:

Risk detection — identifies elevated operational risk.
Facility prioritization — determines which facilities require attention first.
Prediction — provides predictive risk information.
Explanation — connects conclusions to measurable evidence.
Recommendation — provides decision-support guidance.
Executive Q&A — allows natural-language investigation.

🏆 Validated Facility Priorities

The current authoritative facility ranking is:
| Rank | Facility   | Priority | Avg Risk Score | High-Risk Alerts |
| ---: | ---------- | -------- | -------------: | ---------------: |
|    1 | Facility_A | CRITICAL |          97.71 |              380 |
|    2 | Facility_D | CRITICAL |          97.58 |              247 |
|    3 | Facility_C | HIGH     |          97.37 |              298 |
|    4 | Facility_B | HIGH     |              — |                — |

Facility_A
Priority rank: 1
Priority level: CRITICAL
Average risk score: 97.71
High-risk alerts: 380
Recommended action: Immediate intervention required
Facility_D
Priority rank: 2
Priority level: CRITICAL
Average risk score: 97.58
High-risk alerts: 247
Recommended action: Immediate intervention required
Facility_C
Priority rank: 3
Priority level: HIGH
Average risk score: 97.37
High-risk alerts: 298
Recommended action: Priority monitoring and optimization required

These are validated analytical outputs from the project's BigQuery environment, not illustrative example values.

🤖 AI Agent

The current Google ADK agent is:
nexus_resilience_agent
The agent is designed to answer executive questions using authoritative analytical sources.

Example

Question

Why is Facility_A the top priority?

Evidence

The response can connect the priority to:

Rank 1
CRITICAL priority level
Average risk score of 97.71
380 high-risk alerts
Recommended action
Supporting BigQuery sources

Another supported question:

Compare Facility_A and Facility_D.

The agent compares their priority, risk, alerts, and other validated operational metrics.

🗄️ BigQuery Data Sources

Project:

nexus-resilience-ai

Dataset:

nexus_resilience
facility_final_priorities

Authoritative source for:

Facility ranking
Priority level
High-risk alert totals
Average risk
Efficiency
Operating cost
Recommended action
nexus_risk_alerts

Source for:

Active risk alerts
Risk levels
Facility alert evidence
Operational risk signals
risk_predictions

Source for:

Individual prediction outputs
Risk-event probability
Predictive intelligence

The system deliberately separates these sources to maintain data lineage and explainability.

📊 Data

The project uses approximately 10,000 synthetic operational records representing multiple facilities and operational conditions.

Signals include:

Temperature
Humidity
Energy consumption
Production
Equipment efficiency
Operating cost
Waste
Carbon emissions
Inventory
Demand
Maintenance
Equipment status
Risk events
Risk scores
Scenarios

The demonstration dataset includes:

Normal Operations
Energy Stress
Equipment Degradation
Environmental Stress
Combined Critical Risk

Data coverage:
Minimum date: 2025-01-01
Maximum date: 2025-12-31
Distinct dates: 365
The data is synthetic demonstration data and does not contain confidential organizational data.

🏗️ Architecture
                 Operational Data
                       │
                       ▼
              Google Cloud Storage
                       │
                       ▼
                    BigQuery
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Risk Data   Predictions   Priorities
          │            │            │
          └────────────┼────────────┘
                       ▼
                  Gemini + ADK
                       │
                       ▼
              Nexus AI Agent
                       │
              ┌────────┴────────┐
              ▼                 ▼
      Executive Q&A       Looker Studio
              │                 │
              └────────┬────────┘
                       ▼
              Human Decision Maker

🧠 Agentic Architecture

The broader architecture is designed to support specialized intelligence components:
                  Nexus Orchestrator
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 Data Guardian      Risk Analyst     Prediction Agent
        │                │                │
        └────────────────┼────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
 Business Impact Agent        Sustainability Agent
          │                             │
          └──────────────┬──────────────┘
                         ▼
                  Strategy Agent
The current implementation establishes the validated agent foundation while providing a path toward broader multi-agent orchestration.

📈 Executive Dashboard

Nexus Resilience AI is designed to work with the Executive Nexus Resilience Looker Studio dashboard.

The dashboard provides visibility into:

Facility priorities
Risk
Alerts
Efficiency
Operating cost

The intended workflow is:

Dashboard
   ↓
Identify priority facility
   ↓
Ask the AI agent "Why?"
   ↓
Receive evidence-based explanation
   ↓
Compare / investigate
   ↓
Support a human decision

🔍 Reliability & Validation

The agent has been tested against targeted regression and executive-question scenarios.

Validated behaviors include:

Correct all-facility ranking
Correct authoritative priority source
Correct active alert source
Correct prediction source
Correct P(event=1) extraction
Correct disagreement definition

🛡️ Responsible AI

Nexus Resilience AI follows a human-in-the-loop approach.

The system distinguishes:

Observed Data
      ↓
Predictions
      ↓
AI Explanation
      ↓
Recommendation
      ↓
Human Decision

Key principles:

Evidence-based explanations
Data-source traceability
No fabricated operational causes
No fabricated actions
Clear distinction between observations and predictions
Governed enterprise access
Human oversight for high-impact decisions

The AI provides recommendations and decision support; it does not independently make high-impact operational decisions.

☁️ Technology Stack
| Layer                | Technology                        |
| -------------------- | --------------------------------- |
| AI                   | Gemini                            |
| Agent Framework      | Google ADK                        |
| Analytics            | BigQuery                          |
| Predictive Analytics | BigQuery ML / Vertex AI ecosystem |
| Data Storage         | Google Cloud Storage              |
| Runtime              | Cloud Run                         |
| Dashboard            | Looker Studio                     |
| Messaging            | Pub/Sub                           |
| Application Data     | Firestore                         |
| Security             | Google Cloud IAM                  |
| Integration          | MCP                               |
| Language             | Python                            |

💻 Local Setup
Requirements
Python 3.x
Google Cloud project
BigQuery access
Google Cloud authentication
Google ADK-compatible environment

### Install dependencies

```powershell
pip install -r requirements.txt
Requirement already satisfied: yarl==1.24.5 in c:\windows\system32\nexus-resilience-agent\nexus-resilience-ai\nexus-resilience-ai\nexus-resilience-ai\nexus-resilience-ai\.venv\lib\site-packages (from -r requirements.txt (line 69)) (1.24.5)

Key validated packages include:
google-adk==2.8.0
google-cloud-bigquery==3.44.0
google-genai==2.20.0
fastapi==0.141.1
uvicorn==0.52.4

Installation verification returned:

Requirement already satisfied

for all 69 pinned dependencies.

Cloning into 'Nexus-Resilience-AI'...
remote: Enumerating objects: 32, done.
remote: Counting objects: 100% (32/32), done.
remote: Compressing objects: 100% (29/29), done.
remote: Total 32 (delta 5), reused 21 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (32/32), 17.83 KiB | 2.23 MiB/s, done.
Resolving deltas: 100% (5/5), done.

🔐 Security

Never commit:

.env files
API keys
Service-account credentials
Private keys
Certificates
Local virtual environments

The repository .gitignore excludes common secret and credential formats.

Use Google Cloud IAM and appropriate authentication mechanisms for access to cloud resources.

🧪 Agent Verification

To verify that the ADK agent imports correctly:
python -c "from my_agent.agent import root_agent; print('Agent:', root_agent.name)"
Agent: nexus_resilience_agent

📋 Project Status Completed

Synthetic operational data foundation
BigQuery analytical environment
Facility risk analysis
Authoritative facility prioritization
Risk alert analysis
Prediction-source integration
Google ADK agent implementation
Executive question handling
Facility comparison
Unknown-facility handling
Source-grounded responses
Regression testing
Executive dashboard integration
GitHub repository
Repository secret protection
Next Development Areas
Expanded multi-agent orchestration
Real-time monitoring
Automated alerting
Business impact analysis
Sustainability intelligence
MCP enterprise integrations
Human approval workflows
Expanded agent evaluation
Production deployment hardening

🎬 Recommended Demo Flow

A concise demonstration can show:

1. Open Executive Nexus Resilience dashboard
2. Show facility priority ranking
3. Identify Facility_A as Priority #1
4. Ask: "Why is Facility_A the top priority?"
5. Show supporting evidence
6. Ask: "Compare Facility_A and Facility_D."
7. Show comparative intelligence
8. Explain the human-in-the-loop approach
9. Close with:
   Predict → Understand → Act
🌍 Project Vision

Traditional analytics often answer:

What happened?

Predictive analytics asks:

What is likely to happen?

Nexus Resilience AI goes further:

Why is it happening, and what should decision-makers consider doing next?

The goal is to transform operational data into predictive, explainable, decision-ready intelligence before risk becomes loss.

📚 Submission Materials

The project submission is supported by:

GitHub — source code and technical implementation
Google Docs — detailed project documentation
Demo Video — end-to-end product demonstration
Project Blog — professional technical case study

🏷️ Project Classification

Agentic AI | Predictive Analytics | Data Intelligence | Sustainability

Nexus Resilience AI

Predict. Understand. Act. Before Risk Becomes Loss.
