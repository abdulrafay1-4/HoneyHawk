"""
Alert Logger Module
Handles logging and alerting for canary token events
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class AlertLogger:
    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create log files
        self.alerts_log = self.logs_dir / "alerts.log"
        self.activity_log = self.logs_dir / "activity.log"
        self.error_log = self.logs_dir / "errors.log"
        
        # Initialize log files if they don't exist
        for log_file in [self.alerts_log, self.activity_log, self.error_log]:
            if not log_file.exists():
                log_file.touch()
                
        # Log startup
        self.log_info("AlertLogger initialized")
        
    def log_alert(self, severity: str, message: str, details: str = ""):
        """Log a security alert"""
        timestamp = datetime.now()
        
        alert_entry = {
            "timestamp": timestamp.isoformat(),
            "severity": severity,
            "type": "SECURITY_ALERT",
            "message": message,
            "details": details,
            "epoch": time.time()
        }
        
        # Write to alerts log
        self._write_to_log(self.alerts_log, alert_entry)
        
        # Also write to activity log for complete audit trail
        self._write_to_log(self.activity_log, alert_entry)
        
        # Send additional notifications based on severity
        if severity == "HIGH":
            self._send_high_priority_alert(alert_entry)
            
    def log_info(self, message: str, details: Dict[str, Any] = None):
        """Log informational messages"""
        timestamp = datetime.now()
        
        info_entry = {
            "timestamp": timestamp.isoformat(),
            "type": "INFO",
            "message": message,
            "details": details or {},
            "epoch": time.time()
        }
        
        self._write_to_log(self.activity_log, info_entry)
        
    def log_error(self, message: str, error_details: str = ""):
        """Log error messages"""
        timestamp = datetime.now()
        
        error_entry = {
            "timestamp": timestamp.isoformat(),
            "type": "ERROR",
            "message": message,
            "details": error_details,
            "epoch": time.time()
        }
        
        self._write_to_log(self.error_log, error_entry)
        
    def get_recent_alerts(self, hours: int = 24) -> list:
        """Get alerts from the last N hours"""
        cutoff_time = time.time() - (hours * 3600)
        recent_alerts = []
        
        try:
            with open(self.alerts_log, 'r') as f:
                for line in f:
                    try:
                        alert = json.loads(line.strip())
                        if alert.get('epoch', 0) > cutoff_time:
                            recent_alerts.append(alert)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
            
        return recent_alerts
        
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get a summary of all alerts"""
        summary = {
            "total_alerts": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "last_24h": 0,
            "last_alert": None
        }
        
        cutoff_24h = time.time() - (24 * 3600)
        
        try:
            with open(self.alerts_log, 'r') as f:
                for line in f:
                    try:
                        alert = json.loads(line.strip())
                        summary["total_alerts"] += 1
                        
                        severity = alert.get('severity', '').upper()
                        if severity == 'HIGH':
                            summary["high_severity"] += 1
                        elif severity == 'MEDIUM':
                            summary["medium_severity"] += 1
                        elif severity == 'LOW':
                            summary["low_severity"] += 1
                            
                        if alert.get('epoch', 0) > cutoff_24h:
                            summary["last_24h"] += 1
                            
                        # Keep track of most recent alert
                        if (summary["last_alert"] is None or 
                            alert.get('epoch', 0) > summary["last_alert"].get('epoch', 0)):
                            summary["last_alert"] = alert
                            
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
            
        return summary
        
    def _write_to_log(self, log_file: Path, entry: Dict[str, Any]):
        """Write a log entry to the specified file"""
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Error writing to log {log_file}: {e}")
            
    def _send_high_priority_alert(self, alert: Dict[str, Any]):
        """Send high priority alerts via multiple channels"""
        # Terminal notification
        print(f"\n{'='*60}")
        print(f"[!] HIGH PRIORITY ALERT [!]")
        print(f"Time: {alert['timestamp']}")
        print(f"Message: {alert['message']}")
        if alert.get('details'):
            print(f"Details: {alert['details']}")
        print(f"{'='*60}\n")
        
        # System notification (cross-platform)
        self._send_system_notification(alert)
        
        # Could add email, Discord, Slack notifications here
        
    def _send_system_notification(self, alert: Dict[str, Any]):
        """Send system notification (cross-platform)"""
        import platform
        
        title = "HoneyHawk Security Alert"
        message = alert['message']
        
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
            elif system == "Linux":
                os.system(f'notify-send "{title}" "{message}"')
            elif system == "Windows":
                # Windows notification would require additional packages
                pass
        except Exception as e:
            self.log_error(f"Failed to send system notification: {e}")
            
    def export_logs(self, output_file: Path, hours: int = 24):
        """Export logs to a file for analysis"""
        cutoff_time = time.time() - (hours * 3600)
        exported_data = {
            "export_timestamp": datetime.now().isoformat(),
            "hours_exported": hours,
            "alerts": [],
            "activities": [],
            "errors": []
        }
        
        # Export alerts
        try:
            with open(self.alerts_log, 'r') as f:
                for line in f:
                    try:
                        alert = json.loads(line.strip())
                        if alert.get('epoch', 0) > cutoff_time:
                            exported_data["alerts"].append(alert)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
            
        # Export activities
        try:
            with open(self.activity_log, 'r') as f:
                for line in f:
                    try:
                        activity = json.loads(line.strip())
                        if activity.get('epoch', 0) > cutoff_time:
                            exported_data["activities"].append(activity)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
            
        # Write export file
        with open(output_file, 'w') as f:
            json.dump(exported_data, f, indent=2)
            
        self.log_info(f"Exported logs to {output_file}")
