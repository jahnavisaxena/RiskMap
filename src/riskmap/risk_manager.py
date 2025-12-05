import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RISKS_FILE = DATA_DIR / "risks.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Risk:
    id: int
    name: str
    description: Optional[str]
    likelihood: int
    impact: int
    score: int = 0
    controls: List[str] = field(default_factory=list)
    
    # Risk Treatment & Remediation fields
    treatment: str = "Mitigate"  # Accept, Mitigate, Transfer, Avoid
    action_items: str = ""
    owner: str = ""
    due_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    status: str = "Open"  # Open, In Progress, Mitigated, Closed
    framework: str = "soc2"  # soc2, iso27001, hipaa, etc.

class RiskManager:
    def __init__(self):
        self.risks: List[Risk] = []
        self._load_risks()

    def _load_risks(self):
        if not RISKS_FILE.exists():
            return
        
        try:
            with open(RISKS_FILE, "r") as f:
                data = json.load(f)
                self.risks = [Risk(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            self.risks = []

    def _save_risks(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(RISKS_FILE, "w") as f:
            json.dump([asdict(r) for r in self.risks], f, indent=2)

    def add_risk(self, name: str, description: str, likelihood: int, impact: int, framework: str = "soc2") -> Risk:
        new_id = 1
        if self.risks:
            new_id = max(r.id for r in self.risks) + 1
        
        risk = Risk(
            id=new_id,
            name=name,
            description=description,
            likelihood=likelihood,
            impact=impact,
            framework=framework
        )
        self.risks.append(risk)
        self._save_risks()
        return risk

    def list_risks(self) -> List[Risk]:
        return self.risks

    def get_risk(self, risk_id: int) -> Optional[Risk]:
        for risk in self.risks:
            if risk.id == risk_id:
                return risk
        return None

    def delete_risk(self, risk_id: int) -> bool:
        initial_len = len(self.risks)
        self.risks = [r for r in self.risks if r.id != risk_id]
        if len(self.risks) < initial_len:
            self._save_risks()
            return True
        return False

    def update_risk(self, risk: Risk):
        for i, r in enumerate(self.risks):
            if r.id == risk.id:
                self.risks[i] = risk
                self._save_risks()
                return
