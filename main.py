import sys
import os

# Add src directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from riskmap.cli import app

if __name__ == "__main__":
    app()
