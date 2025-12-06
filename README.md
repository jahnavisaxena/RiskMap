# RiskMap - SOC 2 GRC Automation Tool 

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-green.svg)](https://flask.palletsprojects.com/)

A specialized Governance, Risk, and Compliance (GRC) tool designed to streamline **SOC 2** compliance. It features both a **CLI** for rapid risk management and a **Web Dashboard** for visual analytics and evidence tracking.

![RiskMap Dashboard](Screenshot.png)

## Features

### SOC 2 Focused Web Dashboard
- **Comprehensive Analytics**: 6 interactive charts including Risk Severity, Status, and Heat Map.
- **Readiness Checklist**: Automated tracking for SOC 2 Type 1 (Design) and Type 2 (Operating Effectiveness).
- **Evidence Management**: Manage required artifacts (Policies, Logs, Screenshots) with status indicators.
- **Modern UI/UX**: Premium **Inter** typography, **Slate & Indigo** theme, and high-contrast **Dark Mode**.

### CLI Tool
-  **Risk Management**: Quickly add, score, and manage risks related to Trust Service Criteria (TSC).
-  **AI-Powered Mapping**: Automatically maps risks to relevant SOC 2 Common Criteria (CC) controls using OpenAI.
-  **Export**: Generate audit-ready risk registers in CSV, JSON, or PDF.

---

##  Installation

### Option 1: Install via pip

```bash
pip install git+https://github.com/jahnavisaxena/RiskMap.git
```

### Option 2: Clone and Run Locally

```bash
# Clone the repository
git clone https://github.com/jahnavisaxena/RiskMap.git
cd RiskMap

# Install dependencies
pip install -r requirements.txt

# Run Web Dashboard
python app.py
# Visit http://localhost:5000
```

---

##  CLI Usage for SOC 2

### Add a Risk
```bash
riskmap add "Data Breach" --likelihood 4 --impact 5 --category "Security"
```

### Add a Risk with Control Mapping
```bash
# Automatically maps to SOC 2 CC controls (e.g., CC6.1)
riskmap add "Unauthorised Access" --desc "Lack of MFA" --likelihood 5 --impact 5
```

### Export Risk Register
```bash
riskmap export --format pdf
```

### Enable AI Mapping
Set your OpenAI API key to enable intelligent control mapping:
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
```

---

## 🌐 Web Dashboard Guide

Start the server with `python app.py` and navigate to `http://localhost:5000`.

### SOC 2 Widgets
- **Audit Scope**: Toggle between **Type 1** (Point-in-time) and **Type 2** (Period of time) views.
- **Readiness Tracker**: Visual gauge showing your % readiness for the audit.
- **Evidence Panel**: List of required evidence documents (Green = Ready, Red = Missing).

### Visualizations
- **Risk Heat Map**: Interactive 5x5 matrix (Likelihood × Impact).
- **TSC Coverage**: Polar chart showing risk distribution across Security, Availability, Confidentiality, etc.
- **Control Implementation**: Gauge chart tracking mitigated risks vs total risks.

---

## 📁 Project Structure

```
RiskMap/
├── app.py                    # Flask web server
├── main.py                   # CLI entry point
├── src/
│   ├── riskmap/
│   │   ├── risk_manager.py   # Core logic
│   │   ├── control_mapper.py # AI mapping for SOC 2
│   │   └── ...
│   └── data/
│       └── soc2_controls.json # SOC 2 Common Criteria
├── static/
│   ├── css/style.css         # Modern styling (Slate/Indigo)
│   └── js/app.js             # Dashboard logic & Chart.js
└── templates/
    └── index.html            # Dashboard UI
```

---

## 🛠️ Technologies
- **Python 3.8+** & **Flask**
- **Chart.js** for visual analytics
- **OpenAI GPT-4o-mini** for intelligent mapping
- **Typer** for CLI operations

---

## 📄 License
MIT License

---

## 👩‍💻 Author
**Jahnavi Saxena**
