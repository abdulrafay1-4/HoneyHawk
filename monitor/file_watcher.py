"""
File Watcher Module
Monitors file access to canary tokens using watchdog
"""

import time
import platform
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CanaryFileHandler(FileSystemEventHandler):
    def __init__(self, alert_logger):
        super().__init__()
        self.alert_logger = alert_logger
        
    def on_any_event(self, event):
        """Handle any file system event"""
        if event.is_directory:
            return
            
        # Get additional system info
        system_info = self._get_system_info()
        
        event_details = {
            "event_type": event.event_type,
            "file_path": event.src_path,
            "timestamp": time.time(),
            "system_info": system_info
        }
        
        # Log different types of events
        if event.event_type in ['opened', 'accessed']:
            self._handle_file_access(event_details)
        elif event.event_type in ['modified', 'moved', 'deleted']:
            self._handle_file_modification(event_details)
            
    def on_opened(self, event):
        """Handle file open events (Linux/macOS)"""
        if not event.is_directory:
            self._handle_file_access({
                "event_type": "opened",
                "file_path": event.src_path,
                "timestamp": time.time(),
                "system_info": self._get_system_info()
            })
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self._handle_file_modification({
                "event_type": "modified",
                "file_path": event.src_path,
                "timestamp": time.time(),
                "system_info": self._get_system_info()
            })
    
    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            self._handle_file_modification({
                "event_type": "moved",
                "file_path": f"{event.src_path} -> {event.dest_path}",
                "timestamp": time.time(),
                "system_info": self._get_system_info()
            })
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory:
            self._handle_file_modification({
                "event_type": "deleted",
                "file_path": event.src_path,
                "timestamp": time.time(),
                "system_info": self._get_system_info()
            })
            
    def _handle_file_access(self, event_details):
        """Handle file access events with high priority alerting"""
        file_path = Path(event_details["file_path"])
        
        alert_message = "CANARY TRIGGERED - File Access Detected!"
        alert_details = f"""
File: {file_path.name}
Full Path: {file_path}
Event: {event_details['event_type']}
Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event_details['timestamp']))}
System: {event_details['system_info']['hostname']}
OS: {event_details['system_info']['os']}
User: {event_details['system_info']['user']}
        """
        
        # Log with high severity
        self.alert_logger.log_alert("HIGH", alert_message, alert_details)
        
        # Print to console for immediate visibility
        print(f"\n[!] ALERT: {alert_message}")
        print(alert_details)
        
    def _handle_file_modification(self, event_details):
        """Handle file modification events"""
        file_path = Path(event_details["file_path"])
        
        alert_message = f"Canary File Modified - {event_details['event_type']}"
        alert_details = f"""
File: {file_path.name if '->' not in str(file_path) else file_path}
Event: {event_details['event_type']}
Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event_details['timestamp']))}
System: {event_details['system_info']['hostname']}
        """
        
        # Log with medium severity
        self.alert_logger.log_alert("MEDIUM", alert_message, alert_details)
        print(f"\n[!] WARNING: {alert_message}")
        
    def _get_system_info(self):
        """Get system information for the alert"""
        import os
        import socket
        
        try:
            return {
                "hostname": socket.gethostname(),
                "os": f"{platform.system()} {platform.release()}",
                "user": os.getenv("USER") or os.getenv("USERNAME") or "unknown",
                "platform": platform.platform()
            }
        except Exception as e:
            return {
                "hostname": "unknown",
                "os": "unknown", 
                "user": "unknown",
                "platform": "unknown",
                "error": str(e)
            }


class FileWatcher:
    def __init__(self, watch_directory: Path, alert_logger):
        self.watch_directory = watch_directory
        self.alert_logger = alert_logger
        self.observer = Observer()
        self.handler = CanaryFileHandler(alert_logger)
        self.is_running = False
        
    def start(self):
        """Start watching the directory"""
        if not self.watch_directory.exists():
            self.watch_directory.mkdir(parents=True, exist_ok=True)
            
        # Schedule the observer to watch the directory recursively
        self.observer.schedule(
            self.handler, 
            str(self.watch_directory), 
            recursive=True
        )
        
        self.observer.start()
        self.is_running = True
        
        self.alert_logger.log_info(f"File watcher started monitoring: {self.watch_directory}")
        print(f"File watcher active on: {self.watch_directory}")
        
    def stop(self):
        """Stop watching the directory"""
        if self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            self.alert_logger.log_info("File watcher stopped")
            
    def is_alive(self):
        """Check if the watcher is still running"""
        return self.observer.is_alive() if self.is_running else False
