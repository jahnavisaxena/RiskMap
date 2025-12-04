import json
import os
from pathlib import Path
from typing import List, Dict
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

DATA_DIR = Path(__file__).parent.parent / "data"
CONTROLS_FILE = DATA_DIR / "soc2_controls.json"

class ControlMapper:
    def __init__(self):
        self.controls_cache = {}
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

    def _load_controls(self, framework: str) -> List[Dict]:
        if framework in self.controls_cache:
            return self.controls_cache[framework]

        filename = f"{framework}_controls.json"
        file_path = DATA_DIR / filename
        
        if not file_path.exists():
            print(f"[yellow]Warning: Controls file for {framework} not found. Using empty list.[/yellow]")
            return []
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.controls_cache[framework] = data
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def map_controls(self, risk_name: str, risk_description: str, framework: str = "soc2") -> List[str]:
        """
        Map controls to a risk for a specific framework.
        """
        controls = self._load_controls(framework)
        if not controls:
            return []

        if self.client:
            try:
                return self._map_with_ai(risk_name, risk_description, controls, framework)
            except Exception as e:
                print(f"[yellow]AI Mapping failed ({str(e)}). Falling back to keywords.[/yellow]")
        
        return self._map_with_keywords(risk_name, risk_description, controls)

    def _map_with_keywords(self, risk_name: str, risk_description: str, controls: List[Dict]) -> List[str]:
        mapped_controls = []
        text_to_search = (risk_name + " " + (risk_description or "")).lower()

        for control in controls:
            keywords = control.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in text_to_search:
                    mapped_controls.append(control["id"])
                    break 
        
        return list(set(mapped_controls))

    def _map_with_ai(self, risk_name: str, risk_description: str, controls: List[Dict], framework: str) -> List[str]:
        controls_context = "\n".join([f"{c['id']}: {c['description']}" for c in controls])
        
        prompt = f"""
        You are a GRC expert. Map the following risk to the most relevant {framework.upper()} controls from the list below.
        
        RISK:
        Name: {risk_name}
        Description: {risk_description}
        
        AVAILABLE CONTROLS:
        {controls_context}
        
        INSTRUCTIONS:
        - Return ONLY a JSON list of Control IDs.
        - If no control is relevant, return [].
        - Be strict. Only map if it's a direct mitigation.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        content = response.choices[0].message.content.strip()
        
        # Clean up code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return []
