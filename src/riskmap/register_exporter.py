import csv
import json
from typing import List
from .risk_manager import Risk

def export_to_csv(risks: List[Risk], filepath: str):
    if not risks:
        return

    fieldnames = ["id", "name", "description", "likelihood", "impact", "score", "controls", 
                  "treatment", "action_items", "owner", "due_date", "status"]
    
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for risk in risks:
            row = {
                "id": risk.id,
                "name": risk.name,
                "description": risk.description,
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "score": risk.score,
                "controls": ";".join(risk.controls),
                "treatment": risk.treatment,
                "action_items": risk.action_items,
                "owner": risk.owner,
                "due_date": risk.due_date or "",
                "status": risk.status
            }
            writer.writerow(row)

def export_to_json(risks: List[Risk], filepath: str):
    data = [
        {
            "id": risk.id,
            "name": risk.name,
            "description": risk.description,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
            "score": risk.score,
            "controls": risk.controls,
            "treatment": risk.treatment,
            "action_items": risk.action_items,
            "owner": risk.owner,
            "due_date": risk.due_date,
            "status": risk.status
        }
        for risk in risks
    ]
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
