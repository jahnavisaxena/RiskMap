# RiskMap - GRC Automation Tool

A CLI-based Governance, Risk, and Compliance (GRC) tool that automates risk assessment and control mapping for SOC 2 and ISO 27001 frameworks.

## Features

- 📊 **Risk Management**: Add, list, score, and delete risks
- 🤖 **AI-Powered Mapping**: Intelligent control mapping using OpenAI GPT-4o-mini
- 🔄 **Multi-Framework Support**: SOC 2 and ISO 27001 (extensible to HIPAA, GDPR, etc.)
- 📁 **Export**: Generate audit-ready reports in CSV or JSON
- ⚡ **Fallback Logic**: Keyword-based mapping when AI is unavailable

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/RiskMap.git
   cd RiskMap
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Commands

**Add a risk (SOC 2):**
```bash
python main.py add "Data Breach" --likelihood 4 --impact 5
```

**Add a risk (ISO 27001):**
```bash
python main.py add "SQL Injection" --desc "Web app vulnerable" --likelihood 5 --impact 5 --framework iso27001
```

**List all risks:**
```bash
python main.py list
```

**Export to CSV:**
```bash
python main.py export --format csv
```

**Delete a risk:**
```bash
python main.py delete 1
```

### AI-Powered Mapping

To enable AI-powered control mapping, set your OpenAI API key:

**PowerShell:**
```powershell
$env:OPENAI_API_KEY="sk-..."
```

**Bash:**
```bash
export OPENAI_API_KEY="sk-..."
```

## Project Structure

```
RiskMap/
├── main.py                      # Entry point
├── src/
│   ├── riskmap/
│   │   ├── cli.py              # CLI commands
│   │   ├── risk_manager.py     # Risk CRUD operations
│   │   ├── risk_scoring.py     # Scoring logic
│   │   ├── control_mapper.py   # AI + keyword mapping
│   │   └── register_exporter.py# CSV/JSON export
│   └── data/
│       ├── soc2_controls.json  # SOC 2 controls database
│       └── iso27001_controls.json # ISO 27001 controls
├── tests/
│   └── test_core.py            # Unit tests
└── requirements.txt
```

## Frameworks Supported

- **SOC 2**: Common Criteria (CC) controls
- **ISO 27001**: Annex A controls

## Technologies Used

- **Typer**: Modern CLI framework
- **Rich**: Beautiful terminal formatting
- **OpenAI**: GPT-4o-mini for intelligent mapping
- **Pandas**: Data manipulation
- **Python Dataclasses**: Clean data structures

## License

MIT

## Author

Jahnavi Saxena
