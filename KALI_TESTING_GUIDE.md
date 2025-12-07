# RiskMap Testing Guide for Kali Linux Terminal

This guide provides step-by-step instructions to install, run, and test the RiskMap application on Kali Linux.

---

## 📋 Prerequisites

Ensure Kali Linux has Python 3.8+ installed:

```bash
python3 --version
```

If Python is not installed or outdated:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

---

## 🚀 Installation Steps

### Step 1: Transfer Project to Kali Linux

If you're developing on Windows and testing on Kali, transfer the project:

**Option A: Using Git**
```bash
# Clone the repository
git clone https://github.com/jahnavisaxena/RiskMap.git
cd RiskMap
```

**Option B: Using SCP (if Kali is on same network)**
```bash
# From Windows PowerShell
scp -r "C:\Users\JAHNAVI SAXENA\OneDrive\Desktop\Academic\SEM 5\Ethical Hacking And Penetration Testing\RiskMap" kali@<KALI_IP>:~/
```

**Option C: Using Shared Folder (if using VM)**
- If running Kali in VirtualBox/VMware, set up a shared folder
- Access via `/mnt/hgfs/RiskMap` or similar

### Step 2: Navigate to Project Directory

```bash
cd ~/RiskMap  # or wherever you placed the project
```

### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues, install packages individually:
```bash
pip install typer rich pandas openai reportlab flask flask-cors requests beautifulsoup4 dnspython
```

---

## 🧪 Testing Methods

### Method 1: Test the Web Dashboard

#### Start the Flask Server

```bash
python3 app.py
```

You should see:
```
🚀 RiskMap Web UI starting...
📊 Access the dashboard at: http://localhost:5000
Press CTRL+C to stop the server
```

#### Access the Dashboard

**From Kali Browser:**
```bash
# Open Firefox (default in Kali)
firefox http://localhost:5000 &
```

**From External Machine (if Kali is in VM):**
1. Find Kali's IP address:
   ```bash
   ip addr show | grep inet
   ```
2. Access from host machine: `http://<KALI_IP>:5000`

#### Test API Endpoints with curl

```bash
# Get all risks
curl http://localhost:5000/api/risks

# Get statistics
curl http://localhost:5000/api/stats

# Add a new risk
curl -X POST http://localhost:5000/api/risks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SQL Injection Vulnerability",
    "description": "Unsanitized user input in login form",
    "likelihood": 4,
    "impact": 5,
    "framework": "soc2",
    "scanner_type": "Vulnerability"
  }'

# Export to PDF
curl -O http://localhost:5000/api/export/pdf
```

---

### Method 2: Test the CLI Tool

#### Add a Risk via CLI

```bash
python3 main.py add "Weak Password Policy" \
  --desc "Users can set passwords with only 6 characters" \
  --likelihood 4 \
  --impact 4 \
  --category "Security"
```

#### List All Risks

```bash
python3 main.py list
```

#### Export Risk Register

```bash
# Export to CSV
python3 main.py export --format csv

# Export to JSON
python3 main.py export --format json

# Export to PDF
python3 main.py export --format pdf
```

#### View Generated Files

```bash
ls -lh risk_register.*
cat risk_register.csv
cat risk_register.json
```

---

### Method 3: Test Security Scanners

The RiskMap tool includes automated security scanners. Test them from the web UI or by manually triggering scans.

#### Test Vulnerability Scanner

```bash
# Add a vulnerability risk
curl -X POST http://localhost:5000/api/risks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CVE-2024-XXXX: Critical RCE",
    "description": "Remote code execution in Apache Struts",
    "likelihood": 5,
    "impact": 5,
    "scanner_type": "Vulnerability",
    "owner": "Security Team"
  }'
```

#### Test Cloud Configuration Scanner

```bash
curl -X POST http://localhost:5000/api/risks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "S3 Bucket Publicly Accessible",
    "description": "Sensitive data exposed to internet",
    "likelihood": 3,
    "impact": 5,
    "scanner_type": "Cloud Config",
    "owner": "DevOps Team"
  }'
```

---

## 🔬 Penetration Testing Scenarios

### Scenario 1: Test Input Validation

```bash
# Test for XSS in risk name
curl -X POST http://localhost:5000/api/risks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<script>alert(1)</script>",
    "likelihood": 3,
    "impact": 3
  }'

# Test for SQL injection
curl -X POST http://localhost:5000/api/risks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Risk'; DROP TABLE risks;--",
    "likelihood": 3,
    "impact": 3
  }'
```

### Scenario 2: Test API Rate Limiting

```bash
# Send multiple requests rapidly
for i in {1..100}; do
  curl -X POST http://localhost:5000/api/risks \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Test Risk $i\", \"likelihood\": 2, \"impact\": 2}" &
done
```

### Scenario 3: Test Authentication Bypass

```bash
# Check if sensitive endpoints are unprotected
curl -X DELETE http://localhost:5000/api/risks/1
curl http://localhost:5000/api/export/pdf -O
```

### Scenario 4: Port Scanning

```bash
# Scan the Flask application with nmap
nmap -sV -p 5000 localhost

# For comprehensive scan
nmap -A -p- localhost
```

### Scenario 5: Web Vulnerability Scanning

```bash
# Using Nikto (pre-installed in Kali)
nikto -h http://localhost:5000

# Using dirb for directory enumeration
dirb http://localhost:5000

# Using sqlmap for SQL injection testing
sqlmap -u "http://localhost:5000/api/risks/1" --batch
```

---

## 🛠️ Advanced Testing with Kali Tools

### Use Burp Suite

```bash
# Start Burp Suite
burpsuite &

# Configure Firefox proxy to 127.0.0.1:8080
# Navigate to http://localhost:5000 and intercept requests
```

### Use OWASP ZAP

```bash
# Start ZAP
zaproxy &

# Point ZAP to http://localhost:5000
# Run automated scan
```

### Traffic Analysis with Wireshark

```bash
# Capture traffic on loopback interface
sudo wireshark -i lo -f "tcp port 5000"
```

---

## 📊 Load Testing

### Using Apache Bench (ab)

```bash
# Install if not present
sudo apt install apache2-utils -y

# Test with 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:5000/
ab -n 100 -c 10 http://localhost:5000/api/risks
```

### Using wrk

```bash
# Install wrk
sudo apt install wrk -y

# Run benchmark
wrk -t4 -c100 -d30s http://localhost:5000/
```

---

## 🐛 Debugging & Troubleshooting

### Check Application Logs

```bash
# Run Flask in debug mode (already enabled in app.py)
python3 app.py

# For more verbose output
FLASK_ENV=development python3 app.py
```

### Check for Port Conflicts

```bash
# See what's using port 5000
sudo netstat -tulpn | grep 5000
# or
sudo lsof -i :5000
```

### Test Database Access

```bash
# Check if risk_register.csv exists
cat risk_register.csv

# Check file permissions
ls -la risk_register.*
```

### Enable AI Control Mapping

```bash
# Set OpenAI API key (if you have one)
export OPENAI_API_KEY="sk-your-api-key-here"

# Test AI-powered risk mapping
python3 main.py add "Phishing Attack" \
  --desc "Social engineering targeting employees" \
  --likelihood 5 \
  --impact 4
```

---

## ✅ Verification Checklist

- [ ] Flask server starts without errors
- [ ] Web UI loads in browser at http://localhost:5000
- [ ] Can add risks via web interface
- [ ] Can add risks via CLI
- [ ] API endpoints return valid JSON
- [ ] PDF export generates successfully
- [ ] CSV export generates successfully
- [ ] Charts render correctly on dashboard
- [ ] Scanner findings appear with correct severity
- [ ] Risk scoring calculates correctly (Likelihood × Impact)
- [ ] SOC 2 control mapping works

---

## 🔐 Security Testing Findings Template

Document your findings:

```bash
# Create a findings report
nano penetration_test_findings.md
```

```markdown
# RiskMap Penetration Test Report

**Tester:** [Your Name]
**Date:** [Date]
**Target:** RiskMap v1.0 on Kali Linux

## Vulnerabilities Found

### 1. [Vulnerability Name]
- **Severity:** Critical/High/Medium/Low
- **CVSS Score:** 
- **Description:** 
- **Steps to Reproduce:** 
- **Impact:** 
- **Remediation:** 

## Summary
- Total Risks Found: 
- Critical: 
- High: 
- Medium: 
- Low: 
```

---

## 📚 Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **SOC 2 Controls:** https://www.aicpa.org/soc4so
- **Kali Linux Tools:** https://www.kali.org/tools/

---

## 💡 Tips for Effective Testing

1. **Always test on localhost first** before exposing to network
2. **Use a virtual environment** to avoid dependency conflicts
3. **Document all findings** with screenshots and steps to reproduce
4. **Test both authenticated and unauthenticated access** (if auth is added)
5. **Check for sensitive data exposure** in error messages
6. **Verify HTTPS is used in production** (not HTTP)
7. **Test with various input types:** special chars, Unicode, very long strings
8. **Monitor resource usage** during load tests

---

## 🎯 Next Steps

After testing on Kali:
1. Document all security findings
2. Implement fixes for discovered vulnerabilities
3. Add authentication/authorization if missing
4. Implement rate limiting
5. Add input validation and sanitization
6. Enable HTTPS with SSL/TLS
7. Add security headers (CSP, HSTS, etc.)
8. Perform regression testing

---

**Happy Testing! 🚀**
