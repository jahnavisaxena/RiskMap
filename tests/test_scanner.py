import unittest
from unittest.mock import patch, MagicMock
from src.riskmap.scanner import WebsiteScanner

class TestWebsiteScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = WebsiteScanner()

    @patch('src.riskmap.scanner.dns.resolver.resolve')
    @patch('src.riskmap.scanner.socket.socket')
    @patch('src.riskmap.scanner.requests.get')
    @patch('src.riskmap.scanner.socket.create_connection')
    @patch('src.riskmap.scanner.ssl.create_default_context')
    def test_scan_happy_path(self, mock_ssl, mock_create, mock_get, mock_socket, mock_dns):
        # Mock SSL
        mock_context = MagicMock()
        mock_ssl.return_value = mock_context
        mock_create.return_value.__enter__.return_value = MagicMock()
        
        # Mock HTTP Response
        mock_response = MagicMock()
        mock_response.headers = {'Server': 'Nginx'}
        mock_response.cookies = []
        mock_response.text = '<html></html>'
        mock_get.return_value = mock_response

        # Mock Port Scan (All closed)
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect_ex.return_value = 1 # 1 = connection failed (port closed)
        
        # Mock DNS (Empty/Fail for missing records)
        mock_dns.side_effect = Exception("No record")

        risks = self.scanner.scan('https://example.com')
        
        risk_names = [r['name'] for r in risks]
        self.assertIn("Missing Email SPF Record", risk_names)
        self.assertIn("Missing Email DMARC Record", risk_names)
        self.assertIn("Missing HSTS Header", risk_names)
        
    @patch('src.riskmap.scanner.socket.socket')
    def test_open_port(self, mock_socket):
        # Scan specifically for open ports logic
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        # Return 0 (Open) for first call, 1 (Closed) for others
        mock_socket_instance.connect_ex.side_effect = [0, 1, 1, 1, 1, 1] 
        
        self.scanner._check_open_ports('example.com')
        
        risk_names = [r['name'] for r in self.scanner.risks_found]
        self.assertTrue(any("Open Port Detected" in name for name in risk_names))

if __name__ == '__main__':
    unittest.main()
