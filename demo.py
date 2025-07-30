#!/usr/bin/env python3
"""
HoneyHawk Demo Script
Demonstrates the canary token monitoring system
"""

import time
import threading
from pathlib import Path
from main import HoneyHawk


def demo_attack_simulation():
    """Simulate an attacker accessing canary files"""
    print("\nDEMO: Simulating attacker behavior...")
    time.sleep(3)
    
    # Simulate reading AWS credentials
    print("Attacker: Reading AWS credentials...")
    aws_creds = Path("tokens/.aws/credentials")
    if aws_creds.exists():
        with open(aws_creds, 'r') as f:
            content = f.read()
            print(f"   Found: {content.split()[2]}")  # Show access key
    
    time.sleep(2)
    
    # Simulate reading SSH key
    print("Attacker: Accessing SSH private key...")
    ssh_key = Path("tokens/.ssh/id_rsa")
    if ssh_key.exists():
        with open(ssh_key, 'r') as f:
            lines = f.readlines()
            print(f"   Found: {lines[0].strip()}")
    
    time.sleep(2)
    
    # Simulate reading API tokens
    print("Attacker: Looking for API tokens...")
    env_file = Path("tokens/.env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if "GITHUB_TOKEN" in line:
                    print(f"   Found: {line.strip()}")
                    break


def main():
    """Run the HoneyHawk demo"""
    print("HoneyHawk Demo - Canary Credential Detection")
    print("=" * 50)
    
    # Initialize HoneyHawk
    honeyhawk = HoneyHawk()
    
    # Generate tokens if they don't exist
    print("Setting up canary tokens...")
    honeyhawk.token_generator.generate_all_tokens()
    
    # Start monitoring
    print("Starting monitoring systems...")
    honeyhawk.file_watcher.start()
    
    print("HoneyHawk is now monitoring for threats!")
    print("Watch for alerts as the demo progresses...\n")
    
    # Run attack simulation in a separate thread
    attack_thread = threading.Thread(target=demo_attack_simulation)
    attack_thread.start()
    
    # Monitor for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10:
        time.sleep(0.5)
    
    # Stop monitoring
    print("\nDemo complete - stopping monitoring...")
    honeyhawk.file_watcher.stop()
    
    # Show results
    print("\nDEMO RESULTS:")
    summary = honeyhawk.alert_logger.get_alert_summary()
    print(f"   Total Alerts: {summary['total_alerts']}")
    print(f"   High Severity: {summary['high_severity']}")
    print(f"   Medium Severity: {summary['medium_severity']}")
    print(f"   Last 24h: {summary['last_24h']}")
    
    if summary['last_alert']:
        print(f"\n   Most Recent Alert:")
        print(f"   Message: {summary['last_alert']['message']}")
        print(f"   Time: {summary['last_alert']['timestamp']}")
    
    print(f"\nCheck logs/ directory for detailed alert information")
    print("Demo completed successfully!")


if __name__ == "__main__":
    main()
