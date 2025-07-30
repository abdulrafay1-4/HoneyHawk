#!/usr/bin/env python3
"""
HoneyHawk - Cross-Platform Canary Credential Monitor
Author: Abdul Rafay
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path

from tokens.generator import TokenGenerator
from monitor.file_watcher import FileWatcher
from monitor.network_monitor import NetworkMonitor
from alerts.logger import AlertLogger
from utils.config_manager import ConfigManager


class HoneyHawk:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_manager = ConfigManager(self.project_root / "config" / "config.yaml")
        self.alert_logger = AlertLogger(self.project_root / "logs")
        self.token_generator = TokenGenerator(
            self.project_root / "tokens", 
            self.alert_logger
        )
        self.file_watcher = FileWatcher(
            self.project_root / "tokens", 
            self.alert_logger
        )
        self.network_monitor = NetworkMonitor(self.alert_logger)
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n[!] Shutting down HoneyHawk...")
        self.stop()
        
    def start(self):
        """Start the HoneyHawk monitoring system"""
        print("Starting HoneyHawk - Canary Credential Monitor")
        print(f"Project root: {self.project_root}")
        
        # Create necessary directories
        self._create_directories()
        
        # Generate initial tokens
        print("Generating canary tokens...")
        self.token_generator.generate_all_tokens()
        
        # Start monitoring
        print("Starting file monitoring...")
        self.file_watcher.start()
        
        print("Starting network monitoring...")
        self.network_monitor.start()
        
        self.running = True
        print("HoneyHawk is now active and monitoring for threats!")
        print("Check logs/ directory for activity logs")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Stop all monitoring components"""
        self.running = False
        print("Stopping file watcher...")
        self.file_watcher.stop()
        print("Stopping network monitor...")
        self.network_monitor.stop()
        print("HoneyHawk stopped successfully")
        
    def _create_directories(self):
        """Create necessary project directories"""
        directories = [
            self.project_root / "tokens",
            self.project_root / "logs",
            self.project_root / "config"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)


def main():
    """Main entry point"""
    honeyhawk = HoneyHawk()
    honeyhawk.setup_signal_handlers()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "generate":
            print("Generating new canary tokens...")
            honeyhawk.token_generator.generate_all_tokens()
            print("Tokens generated successfully!")
        elif command == "clean":
            print("Cleaning up old tokens...")
            honeyhawk.token_generator.clean_tokens()
            print("Cleanup completed!")
        else:
            print("Usage: python main.py [generate|clean]")
    else:
        honeyhawk.start()


if __name__ == "__main__":
    main()
