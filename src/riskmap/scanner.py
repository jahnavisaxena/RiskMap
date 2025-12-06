import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlparse
import socket
import ssl
import dns.resolver

class WebsiteScanner:
    def __init__(self):
        self.risks_found = []

    def scan(self, url: str) -> List[Dict]:
        """
        Perform a passive scan of the target URL.
        Returns a list of potential risks found.
        """
        self.risks_found = []
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            print(f"Scanning {url}...")
            
            # --- PHASE 1: Network & Infrastructure ---
            self._check_ssl(domain)
            self._check_open_ports(domain)
            self._check_email_security(domain)
            self._check_s3_buckets(domain)
            
            # --- PHASE 2: Web Application ---
            response = requests.get(url, timeout=10, verify=False) # verify=False to prevent crashing on self-signed
            self._check_headers(response.headers)
            self._check_cookies(response.cookies)
            self._check_content(response.text)
            self._check_robots_txt(url)
            
        except requests.exceptions.RequestException as e:
            self.risks_found.append({
                "name": "Site Unreachable",
                "description": f"Scanner could not reach {url}. Error: {str(e)}",
                "likelihood": 5,
                "impact": 5,
                "category": "Availability",
                "scanner_type": "Availability"
            })
        except Exception as e:
            self.risks_found.append({
                "name": "Scan Failed",
                "description": f"Internal scanner error: {str(e)}",
                "likelihood": 1,
                "impact": 1,
                "category": "Unknown",
                "scanner_type": "Unknown"
            })
            
        return self.risks_found

    def _check_ssl(self, domain: str):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    pass
        except Exception as e:
            self.risks_found.append({
                "name": "Weak or Missing SSL/TLS",
                "description": f"Unable to establish a secure HTTPS connection to {domain}. Error: {str(e)}",
                "likelihood": 5,
                "impact": 5,
                "category": "Security",
                "scanner_type": "Vulnerability Scanner"
            })

    def _check_open_ports(self, domain: str):
        # Specific "Danger Ports" to check responsibly
        ports = {
            21: "FTP (File Transfer)",
            22: "SSH (Secure Shell)",
            23: "Telnet (Unencrypted Admin)",
            3306: "MySQL Database",
            5432: "Postgres Database",
            8080: "Alternative HTTP"
        }
        
        for port, service in ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1) # Fast timeout
                result = sock.connect_ex((domain, port))
                if result == 0:
                    self.risks_found.append({
                        "name": f"Open Port Detected: {port}",
                        "description": f"The {service} port ({port}) is open to the public internet.",
                        "likelihood": 3,
                        "impact": 4,
                        "category": "Security",
                        "scanner_type": "Attack Surface Scanner"
                    })
                sock.close()
            except:
                pass

    def _check_email_security(self, domain: str):
        # 1. SPF Check
        has_spf = False
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                if 'v=spf1' in rdata.to_text():
                    has_spf = True
                    break
        except:
            pass
            
        if not has_spf:
             self.risks_found.append({
                "name": "Missing Email SPF Record",
                "description": "Domain lacks an SPF record. Attackers can easily spoof emails from this domain.",
                "likelihood": 4,
                "impact": 4,
                "category": "Security",
                "scanner_type": "Cloud Configuration"
            })

        # 2. DMARC Check
        has_dmarc = False
        try:
            answers = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
            for rdata in answers:
                if 'v=DMARC1' in rdata.to_text():
                    has_dmarc = True
                    break
        except:
            pass

        if not has_dmarc:
             self.risks_found.append({
                "name": "Missing Email DMARC Record",
                "description": "Domain lacks a DMARC record. No policy exists to reject spoofed emails.",
                "likelihood": 3,
                "impact": 4,
                "category": "Security",
                "scanner_type": "Cloud Configuration"
            })

    def _check_s3_buckets(self, domain: str):
        # Clean domain for bucket naming conventions
        base_name = domain.split(':')[0] # remove port if present
        bucket_names = [
            base_name.replace('.', '-'),
            base_name.replace('.', ''),
            f"{base_name}-assets",
            f"{base_name}-data"
        ]
        
        for bucket in bucket_names:
            try:
                bucket_url = f"https://{bucket}.s3.amazonaws.com"
                resp = requests.head(bucket_url, timeout=2)
                if resp.status_code == 200:
                    self.risks_found.append({
                        "name": "Public S3 Bucket Found",
                        "description": f"A public S3 bucket '{bucket}' was found. It may contain sensitive data.",
                        "likelihood": 4,
                        "impact": 5,
                        "category": "Security",
                        "scanner_type": "Cloud Configuration"
                    })
            except:
                pass

    def _check_headers(self, headers: Dict):
        if 'Strict-Transport-Security' not in headers:
            self.risks_found.append({
                "name": "Missing HSTS Header",
                "description": "The site does not enforce HTTPS via Strict-Transport-Security.",
                "likelihood": 3,
                "impact": 4,
                "category": "Security",
                "scanner_type": "Vulnerability Scanner"
            })
            
        if 'X-Frame-Options' not in headers:
            self.risks_found.append({
                "name": "Missing Clickjacking Protection",
                "description": "Missing X-Frame-Options header.",
                "likelihood": 3,
                "impact": 3,
                "category": "Security",
                "scanner_type": "Vulnerability Scanner"
            })
            
        if 'Content-Security-Policy' not in headers:
            self.risks_found.append({
                "name": "Missing Content Security Policy",
                "description": "No CSP header found.",
                "likelihood": 4,
                "impact": 4,
                "category": "Security",
                "scanner_type": "Vulnerability Scanner"
            })

        if 'Server' in headers or 'X-Powered-By' in headers:
            server_info = headers.get('Server', '') + " " + headers.get('X-Powered-By', '')
            self.risks_found.append({
                "name": "Server Information Leakage",
                "description": f"The server is revealing its software version: '{server_info.strip()}'.",
                "likelihood": 2,
                "impact": 3,
                "category": "Security",
                "scanner_type": "Dependency Scanner"
            })

    def _check_cookies(self, cookies):
        for cookie in cookies:
            if not cookie.secure:
                self.risks_found.append({
                    "name": f"Insecure Cookie: {cookie.name}",
                    "description": f"Cookie '{cookie.name}' is missing the 'Secure' flag.",
                    "likelihood": 3,
                    "impact": 3,
                    "category": "Security",
                    "scanner_type": "Vulnerability Scanner"
                })
            if not cookie.has_nonstandard_attr('HttpOnly'): # RequestCookieJar specific
                # Note: requests cookies handling of HttpOnly is tricky as client doesn't enforce it, but we can check if server sent it?
                # Actually, requests.cookies are usually strictly client-side view. 
                # A better check is looking at 'Set-Cookie' header raw string if needed, but for now we might skip deep HttpOnly check on requests object 
                # unless we parse headers manually. Let's rely on 'Secure' for now as it's easier to access from object.
                pass

    def _check_content(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text().lower()
        if 'admin' in text and 'password' in text:
             self.risks_found.append({
                "name": "Admin Portal Exposure",
                "description": "An administrative login interface appears to be exposed.",
                "likelihood": 3,
                "impact": 5,
                "category": "Security",
                "scanner_type": "Attack Surface Scanner"
            })

    def _check_robots_txt(self, url: str):
        try:
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            resp = requests.get(f"{base_url}/robots.txt", timeout=5)
            if resp.status_code == 200:
                content = resp.text.lower()
                sensitive_paths = ['/admin', '/backup', '/db', '/private', '/config']
                found_paths = [p for p in sensitive_paths if p in content]
                
                if found_paths:
                    self.risks_found.append({
                        "name": "Sensitive Paths in robots.txt",
                        "description": f"Robots.txt reveals sensitive paths: {', '.join(found_paths)}.",
                        "likelihood": 2,
                        "impact": 3,
                        "category": "Security",
                        "scanner_type": "Attack Surface Scanner"
                    })
        except:
            pass
