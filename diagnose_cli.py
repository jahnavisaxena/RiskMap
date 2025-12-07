#!/usr/bin/env python3
"""
Diagnostic script to check if all CLI dependencies are properly installed.
Run this on Kali Linux to troubleshoot the missing 'scan' command.
"""

import sys

print("=" * 60)
print("RiskMap CLI Diagnostic Tool")
print("=" * 60)
print()

# Track issues
issues = []
warnings = []

# 1. Check Python version
print("[1/7] Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"    ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    issues.append(f"Python version {sys.version_info.major}.{sys.version_info.minor} is too old. Need 3.8+")
    print(f"    ✗ Python {sys.version_info.major}.{sys.version_info.minor} (Need 3.8+)")

# 2. Check required modules
print("\n[2/7] Checking required modules...")
required_modules = {
    'typer': 'typer',
    'rich': 'rich',
    'pandas': 'pandas',
    'requests': 'requests',
    'bs4': 'beautifulsoup4',
    'dns.resolver': 'dnspython',
    'flask': 'flask',
    'flask_cors': 'flask-cors',
    'reportlab': 'reportlab'
}

for module, package in required_modules.items():
    try:
        __import__(module)
        print(f"    ✓ {package}")
    except ImportError as e:
        issues.append(f"Missing module: {package}")
        print(f"    ✗ {package} - MISSING")

# 3. Check if scanner.py exists and can be imported
print("\n[3/7] Checking scanner module...")
try:
    sys.path.insert(0, 'src')
    from riskmap.scanner import WebsiteScanner
    print("    ✓ scanner.py imports successfully")
    scanner = WebsiteScanner()
    print("    ✓ WebsiteScanner can be instantiated")
except Exception as e:
    issues.append(f"Scanner module error: {str(e)}")
    print(f"    ✗ Scanner error: {str(e)}")

# 4. Check if cli.py can be imported
print("\n[4/7] Checking CLI module...")
try:
    from riskmap.cli import app
    print("    ✓ cli.py imports successfully")
except Exception as e:
    issues.append(f"CLI module error: {str(e)}")
    print(f"    ✗ CLI error: {str(e)}")

# 5. Check available commands
print("\n[5/7] Checking available CLI commands...")
try:
    from riskmap.cli import app
    commands = [cmd.name for cmd in app.registered_commands]
    print(f"    Available commands: {', '.join(commands)}")
    
    if 'scan' in commands:
        print("    ✓ 'scan' command is registered")
    else:
        issues.append("'scan' command is NOT registered in CLI")
        print("    ✗ 'scan' command is MISSING")
except Exception as e:
    issues.append(f"Cannot list commands: {str(e)}")
    print(f"    ✗ Error: {str(e)}")

# 6. Check network capabilities (for scanning)
print("\n[6/7] Checking network capabilities...")
try:
    import socket
    import ssl
    print("    ✓ socket module available")
    print("    ✓ ssl module available")
except Exception as e:
    warnings.append(f"Network capabilities limited: {str(e)}")
    print(f"    ⚠ Warning: {str(e)}")

# 7. Check file permissions
print("\n[7/7] Checking file system...")
import os
if os.access('.', os.W_OK):
    print("    ✓ Current directory is writable")
else:
    warnings.append("Current directory not writable - exports may fail")
    print("    ⚠ Current directory not writable")

# Summary
print("\n" + "=" * 60)
print("DIAGNOSTIC SUMMARY")
print("=" * 60)

if not issues and not warnings:
    print("✓ ALL CHECKS PASSED!")
    print("\nThe CLI should work correctly. Try running:")
    print("  python3 main.py --help")
elif issues:
    print(f"✗ FOUND {len(issues)} CRITICAL ISSUE(S):\n")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print("\n📋 RECOMMENDED FIXES:")
    print("\n# Install missing dependencies:")
    print("pip3 install -r requirements.txt")
    print("\n# Or install individually:")
    for module, package in required_modules.items():
        try:
            __import__(module)
        except ImportError:
            print(f"pip3 install {package}")

if warnings:
    print(f"\n⚠ {len(warnings)} WARNING(S):")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")

print("\n" + "=" * 60)
