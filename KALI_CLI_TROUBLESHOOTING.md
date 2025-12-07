# Troubleshooting: Missing `scan` Command on Kali Linux

## Problem
When running `python3 main.py --help` on Kali Linux, the `scan` command doesn't appear in the help output.

## Root Cause
The `scan` command relies on the `WebsiteScanner` class which imports several dependencies:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing  
- `dnspython` - DNS lookups (SPF/DMARC checks)
- `socket` & `ssl` - Network scanning

If any of these modules fail to import, the CLI module may silently fail to register the `scan` command.

---

## 🔧 Solution: Run Diagnostic and Fix

### Step 1: Run the Diagnostic Script

```bash
cd ~/RiskMap  # or your project directory
python3 diagnose_cli.py
```

This will check:
- ✅ Python version (need 3.8+)
- ✅ All required modules
- ✅ Scanner module imports
- ✅ CLI module imports  
- ✅ Available commands list
- ✅ Network capabilities
- ✅ File permissions

### Step 2: Install Missing Dependencies

If you see missing modules, install them:

```bash
# Install all dependencies at once
pip3 install -r requirements.txt

# Or install individually if requirements.txt fails
pip3 install typer rich pandas openai reportlab flask flask-cors requests beautifulsoup4 dnspython
```

**Kali Linux Note:** You may need to use `pip3` instead of `pip`:
```bash
sudo apt update
sudo apt install python3-pip -y
pip3 install -r requirements.txt
```

### Step 3: Verify the Fix

```bash
# Check help output - you should now see 'scan' command
python3 main.py --help

# Test the scan command
python3 main.py scan https://example.com
```

---

## 🐛 Manual Debugging Commands

### Check if CLI module loads without errors:

```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from riskmap.cli import app; print([c.name for c in app.registered_commands])"
```

**Expected output:**
```
['add', 'list', 'score', 'map-controls', 'export', 'delete', 'scan']
```

### Check if scanner module imports:

```bash
python3 -c "import sys; sys.path.insert(0, 'src'); from riskmap.scanner import WebsiteScanner; print('Scanner OK')"
```

**Expected output:**
```
Scanner OK
```

### Check individual dependencies:

```bash
# Check dnspython (most likely culprit)
python3 -c "import dns.resolver; print('dnspython OK')"

# Check requests
python3 -c "import requests; print('requests OK')"

# Check beautifulsoup4
python3 -c "from bs4 import BeautifulSoup; print('beautifulsoup4 OK')"
```

---

## 📝 Common Issues on Kali Linux

### Issue 1: `dnspython` Not Installed

**Symptoms:**
```python
ModuleNotFoundError: No module named 'dns'
```

**Fix:**
```bash
pip3 install dnspython
```

### Issue 2: Using System Python vs Virtual Environment

**Symptoms:** Packages installed but still showing as missing

**Fix:** Create and use a virtual environment:
```bash
cd ~/RiskMap
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --help  # Should now show scan command
```

### Issue 3: Permission Issues

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Fix:**
```bash
# Don't use sudo with pip in virtual env
# Instead, ensure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Outdated pip

**Symptoms:** Installation fails with cryptic errors

**Fix:**
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

---

## ✅ Verification Checklist

After fixing, verify these:

- [ ] `python3 diagnose_cli.py` shows all checks passed
- [ ] `python3 main.py --help` shows the `scan` command
- [ ] `python3 main.py scan --help` shows scan-specific help
- [ ] Test scan works: `python3 main.py scan https://example.com`

---

## 🎯 Complete Test Run on Kali

Here's a complete test sequence after fixing:

```bash
# 1. Navigate to project
cd ~/RiskMap

# 2. Activate virtual environment (if using one)
source venv/bin/activate

# 3. Verify help shows scan command
python3 main.py --help

# 4. Test scan command help
python3 main.py scan --help

# 5. Run an actual scan
python3 main.py scan https://example.com

# 6. List risks to see scanner findings
python3 main.py list

# 7. Export results
python3 main.py export --format pdf
ls -la risk_register.pdf
```

---

## 🔍 Still Not Working?

If the `scan` command still doesn't appear:

1. **Check Python path:**
   ```bash
   python3 -c "import sys; print('\\n'.join(sys.path))"
   ```

2. **Manually test CLI loading:**
   ```bash
   python3 -c "
   import sys
   import traceback
   sys.path.insert(0, 'src')
   try:
       from riskmap.cli import app
       print('Commands:', [c.name for c in app.registered_commands])
   except Exception as e:
       traceback.print_exc()
   "
   ```

3. **Check for syntax errors:**
   ```bash
   python3 -m py_compile src/riskmap/cli.py
   python3 -m py_compile src/riskmap/scanner.py
   ```

4. **View full error messages:**
   ```bash
   python3 -v main.py --help 2>&1 | tee debug.log
   ```

---

## 💡 Pro Tip: Using Virtual Environments on Kali

Always use virtual environments to avoid dependency conflicts:

```bash
# Create virtual environment
python3 -m venv venv

# Activate (do this every time you open a new terminal)
source venv/bin/activate

# Your prompt will change to show (venv)
# Now install and run everything within this environment
pip install -r requirements.txt
python main.py --help

# Deactivate when done
deactivate
```

---

**Need more help?** Run `python3 diagnose_cli.py` and share the output!
