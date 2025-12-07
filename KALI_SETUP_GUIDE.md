# RiskMap - Kali Linux Setup Guide

## 📥 Download & Installation

### 1. Clone the Repository

```bash
# Navigate to your desired directory
cd ~

# Clone the repository
git clone https://github.com/jahnavisaxena/RiskMap.git

# Navigate into the project
cd RiskMap
```

### 2. Install Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3 and pip (usually pre-installed on Kali)
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### 3. Create Virtual Environment (Required for Kali)

**Important:** Kali Linux uses an "externally managed environment" to protect system Python. You MUST use a virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your prompt should now show (venv) at the beginning

# Install project dependencies
pip install -r requirements.txt

# OR install the package directly
pip install git+https://github.com/jahnavisaxena/RiskMap.git
```

> **Note:** You'll need to activate the virtual environment (`source venv/bin/activate`) every time you open a new terminal before running RiskMap.

### 4. Verify Installation

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check if all files are present
ls -la

# Verify RiskMap CLI is available
riskmap --help

# Or check installed packages
pip list | grep -i flask
```

## 🚀 Running RiskMap on Kali

### Start the Web Dashboard

```bash
# Navigate to project directory
cd ~/RiskMap

# Activate virtual environment
source venv/bin/activate

# Start the Flask server
python app.py

# The server will start on port 5000
```

### Access the Web Dashboard

Once running, access RiskMap at:
- **Local:** `http://localhost:5000`
- **Network:** `http://<your-kali-ip>:5000`

To find your Kali IP:
```bash
ip addr show
# or
hostname -I
```

## 🔧 CLI Usage

RiskMap includes a powerful CLI for rapid risk management:

```bash
# First, activate the virtual environment
source venv/bin/activate

# View CLI help
riskmap --help

# Add a risk with automatic SOC 2 control mapping
riskmap add "Data Breach" --likelihood 4 --impact 5 --category "Security"

# Add a risk with description
riskmap add "Unauthorized Access" --desc "Lack of MFA on admin accounts" --likelihood 5 --impact 5

# Export risk register
riskmap export --format pdf
riskmap export --format csv
riskmap export --format json
```

### Enable AI-Powered Control Mapping

```bash
# Set OpenAI API key for intelligent SOC 2 control mapping
export OPENAI_API_KEY="sk-your-api-key-here"

# Then add risks - they'll automatically map to SOC 2 CC controls
riskmap add "SQL Injection Vulnerability" --likelihood 5 --impact 5
```

## 🛠️ Troubleshooting

### Port Already in Use

If port 5000 is occupied:
```bash
# Find and kill the process
sudo lsof -i :5000
sudo kill -9 <PID>

# Or change the port in app.py
# Look for: app.run(debug=True, port=5000)
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER ~/RiskMap

# Fix permissions
chmod -R 755 ~/RiskMap
```

### Missing Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Reinstall dependencies
pip3 install -r requirements.txt --upgrade

# If specific packages fail, install individually
pip3 install typer rich pandas openai reportlab flask flask-cors
```

## 📊 Testing in Kali Environment

### Security Testing Context

RiskMap is designed for GRC (Governance, Risk, and Compliance) and SOC 2 assessment. In Kali, you can:

1. **Risk Assessment**: Document vulnerabilities found during penetration testing
2. **Control Mapping**: Map findings to SOC 2 controls
3. **Risk Scoring**: Automatically calculate risk scores based on likelihood and impact
4. **Compliance Tracking**: Track remediation progress

### Example Pentesting Workflow

```bash
# 1. Start RiskMap web dashboard
python3 app.py &

# 2. Conduct penetration testing with your favorite tools
nmap -sV target.com
nikto -h target.com

# 3. Document findings in RiskMap
riskmap add "Outdated SSH Version" --likelihood 4 --impact 4 --category "Security"
riskmap add "Missing Security Headers" --likelihood 3 --impact 3 --category "Security"

# 4. Access web dashboard to view:
#    - Risk heat map visualization
#    - SOC 2 control mapping
#    - Compliance readiness tracker
#    - Security scanner findings

# 5. Generate audit report
riskmap export --format pdf
```

## 🔐 Security Considerations

- **Network Exposure**: Be cautious when exposing the server on network
- **Default Credentials**: Change any default credentials if applicable
- **Data Persistence**: Ensure sensitive risk data is stored securely
- **Database**: If using a database, secure it properly

## 📝 Quick Reference

| Command | Purpose |
|---------|---------|
| `git pull origin main` | Update to latest version |
| `python3 app.py` | Start the web dashboard |
| `riskmap --help` | View CLI commands |
| `pytest tests/` | Run automated tests |
| `riskmap export --format pdf` | Generate risk register PDF |

## 🔄 Updating RiskMap

```bash
# Pull latest changes
cd ~/RiskMap
git pull origin main

# Reinstall dependencies if needed
pip3 install -r requirements.txt --upgrade

# Restart the application
python3 app.py
```

## 💡 Tips for Kali Usage

1. **Use tmux/screen**: Keep RiskMap running in background
   ```bash
   tmux new -s riskmap
   python3 app.py
   # Press Ctrl+B then D to detach
   ```

2. **Systemd Service**: Create a service for auto-start
   ```bash
   sudo nano /etc/systemd/system/riskmap.service
   ```

3. **Integrate with Workflow**: Use RiskMap alongside your pentesting tools

## 📧 Support

For issues or questions:
- GitHub Issues: https://github.com/jahnavisaxena/RiskMap/issues
- Check existing documentation in the repo
