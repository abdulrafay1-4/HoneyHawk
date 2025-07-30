"""
Network Monitor Module
Monitors for network usage of canary credentials
"""

import socket
import threading
import time
from datetime import datetime


class NetworkMonitor:
    def __init__(self, alert_logger):
        self.alert_logger = alert_logger
        self.is_running = False
        self.monitors = []
        
    def start(self):
        """Start network monitoring components"""
        self.is_running = True
        
        # Start fake SSH honeypot
        self._start_fake_ssh_server()
        
        # Start DNS canary monitoring (placeholder)
        self._start_dns_monitor()
        
        self.alert_logger.log_info("Network monitoring started")
        
    def stop(self):
        """Stop all network monitoring"""
        self.is_running = False
        for monitor in self.monitors:
            if hasattr(monitor, 'stop'):
                monitor.stop()
        self.alert_logger.log_info("Network monitoring stopped")
        
    def _start_fake_ssh_server(self):
        """Start a fake SSH server on port 2222 to catch SSH key usage"""
        def ssh_honeypot():
            try:
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(1.0)  # Non-blocking with timeout
                
                # Bind to localhost:2222
                sock.bind(('localhost', 2222))
                sock.listen(5)
                
                self.alert_logger.log_info("Fake SSH server started on localhost:2222")
                
                while self.is_running:
                    try:
                        client_socket, address = sock.accept()
                        
                        # Alert on connection attempt
                        alert_message = "CANARY TRIGGERED - SSH Connection Attempt!"
                        alert_details = f"""
Service: Fake SSH Server
Client IP: {address[0]}
Client Port: {address[1]}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Likely Cause: Someone tried to use the fake SSH key
                        """
                        
                        self.alert_logger.log_alert("HIGH", alert_message, alert_details)
                        print(f"\n[!] SSH CANARY TRIGGERED from {address[0]}:{address[1]}")
                        
                        # Send fake SSH banner and close
                        try:
                            client_socket.send(b"SSH-2.0-OpenSSH_8.9\r\n")
                            time.sleep(2)
                            client_socket.close()
                        except:
                            pass
                            
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.is_running:
                            self.alert_logger.log_error(f"SSH honeypot error: {e}")
                        break
                        
                sock.close()
                
            except Exception as e:
                self.alert_logger.log_error(f"Failed to start SSH honeypot: {e}")
        
        ssh_thread = threading.Thread(target=ssh_honeypot, daemon=True)
        ssh_thread.start()
        self.monitors.append(ssh_thread)
        
    def _start_dns_monitor(self):
        """Monitor for DNS queries to canary domains"""
        def dns_monitor():
            # This is a placeholder for DNS monitoring
            # In a full implementation, you might:
            # 1. Set up a DNS server to catch queries to canary domains
            # 2. Monitor network traffic for specific domain queries
            # 3. Use external services like Canary Tokens for DNS monitoring
            
            self.alert_logger.log_info("DNS monitoring placeholder started")
            
            # Example: Monitor for specific outbound connections
            # This would require more sophisticated network monitoring
            while self.is_running:
                time.sleep(10)  # Check every 10 seconds
                # Placeholder for actual DNS monitoring logic
                
        dns_thread = threading.Thread(target=dns_monitor, daemon=True)
        dns_thread.start()
        self.monitors.append(dns_thread)
