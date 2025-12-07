# Quick Fix for Kali Linux - Missing `scan` Command

## 🚀 Quick Commands (Copy-Paste These)

```bash
# Navigate to your project
cd ~/RiskMap  # or wherever you placed the project

# Run the diagnostic script
python3 diagnose_cli.py

# If it shows missing dnspython (most common issue):
pip3 install dnspython

# Or install all dependencies:
pip3 install -r requirements.txt

# Verify the scan command appears:
python3 main.py --help

# Test the scan command:
python3 main.py scan https://example.com
```

## 📋 Full Setup (Recommended for Kali)

```bash
# 1. Navigate to project directory
cd ~/RiskMap

# 2. Create virtual environment (recommended)
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Verify installation
python3 diagnose_cli.py

# 6. Test CLI
python3 main.py --help

# 7. Run a scan
python3 main.py scan https://example.com
```

## ❓ Why is `scan` Missing?

The `scan` command requires these modules:
- ✅ `requests` - For HTTP requests
- ✅ `beautifulsoup4` - For HTML parsing
- ✅ `dnspython` - For DNS/email security checks (SPF/DMARC)
- ✅ `socket` & `ssl` - Built-in Python modules

**If any module is missing**, the CLI silently fails to register the `scan` command.

## 🔍 Quick Check

```bash
# Check if dnspython is installed:
python3 -c "import dns.resolver; print('OK')"

# If you see an error, install it:
pip3 install dnspython
```

## 📚 Full Documentation

See these files for detailed troubleshooting:
- `KALI_CLI_TROUBLESHOOTING.md` - Complete troubleshooting guide
- `KALI_TESTING_GUIDE.md` - Full testing guide for Kali
- `diagnose_cli.py` - Automated diagnostic script

---

**Need Help?** Run `python3 diagnose_cli.py` and it will tell you exactly what's wrong!
