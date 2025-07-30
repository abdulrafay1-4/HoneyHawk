"""
Configuration Manager Module
Handles YAML configuration for HoneyHawk
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            # Create default config
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
            
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "honeyhawk": {
                "version": "1.0.0",
                "name": "HoneyHawk Canary Monitor"
            },
            "tokens": {
                "generate_aws": True,
                "generate_ssh": True,
                "generate_database": True,
                "generate_api": True,
                "regenerate_interval_days": 30
            },
            "monitoring": {
                "file_watch_enabled": True,
                "network_monitor_enabled": True,
                "ssh_honeypot_port": 2222
            },
            "alerting": {
                "log_to_file": True,
                "system_notifications": True,
                "email_alerts": False,
                "discord_webhook": "",
                "slack_webhook": ""
            },
            "logging": {
                "log_level": "INFO",
                "max_log_size_mb": 100,
                "rotate_logs": True
            }
        }
        
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to YAML file"""
        self.config_path.parent.mkdir(exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value
        self._save_config(self.config)
        
    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()
