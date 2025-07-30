# HoneyHawk - Cross-Platform Canary Credential Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/abdulrafay1-4/honeyhawk)

> **A sophisticated Blue Team deception tool that proactively detects unauthorized access by planting fake credentials (canary tokens) and monitoring for their use.**

HoneyHawk is a cross-platform security monitoring tool designed for threat detection, malware discovery, insider threat identification, and security lab simulation. It generates realistic fake credentials and monitors for any access attempts, providing immediate alerts when potential threats interact with the canary tokens.

## Features

### Token Generation
- **AWS Credentials**: Fake access keys and secrets in multiple formats
- **SSH Keys**: Realistic private keys in various locations
- **Database Configs**: Connection strings, environment files, and config files
- **API Tokens**: GitHub, Slack, Discord, Stripe, SendGrid tokens
- **Auto-regeneration**: Configurable token refresh intervals

### Cross-Platform Monitoring
- **File System Monitoring**: Real-time detection using `watchdog` library
- **Network Traps**: SSH honeypot and DNS monitoring
- **Process Detection**: System-level access monitoring
- **Multi-OS Support**: Windows, macOS, and Linux compatibility

### Advanced Alerting
- **Real-time Alerts**: Immediate console notifications
- **Structured Logging**: JSON-formatted logs for analysis
- **System Notifications**: Native OS notifications
- **Severity Levels**: HIGH, MEDIUM, LOW priority classification
- **Export Capabilities**: Log export for forensic analysis

### Configuration Management
- **YAML Configuration**: Easy customization via `config.yaml`
- **Flexible Token Types**: Enable/disable specific credential types
- **Monitoring Options**: Configurable file and network monitoring
- **Alert Channels**: Multiple notification methods

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abdulrafay1-4/honeyhawk.git
   cd honeyhawk
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run setup script**
   ```bash
   python setup.py
   ```
   This will:
   - Create the configuration file from template
   - Set up necessary directories
   - Verify dependencies

4. **Run HoneyHawk**
   ```bash
   python main.py
   ```

### First Run
On first execution, HoneyHawk will:
- Create necessary directories (`tokens/`, `logs/`, `config/`)
- Generate a complete set of canary credentials
- Start file system monitoring
- Begin network monitoring (SSH honeypot on port 2222)
- Display real-time status in the terminal

**Note**: Generated tokens and logs are automatically excluded from git tracking via `.gitignore` for security.

## 📋 Usage

### Basic Commands

```bash
# Start monitoring (default)
python main.py

# Generate new tokens only
python main.py generate

# Clean up all tokens
python main.py clean
```

### Monitoring Output
```
Starting HoneyHawk - Canary Credential Monitor
Project root: /path/to/honeyhawk
Generating canary tokens...
Starting file monitoring...
Starting network monitoring...
HoneyHawk is now active and monitoring for threats!
Check logs/ directory for activity logs
Press Ctrl+C to stop
```

### Alert Example
```
ALERT: CANARY TRIGGERED - File Access Detected!

File: credentials
Full Path: /path/to/honeyhawk/tokens/.aws/credentials
Event: opened
Time: 2025-01-30 14:23:15
System: hostname.local
OS: Darwin 21.6.0
User: username
```

## Project Structure

```
honeyhawk/
├── tokens/                 # Generated canary credentials
│   ├── .aws/              # AWS credential files
│   ├── .ssh/              # SSH key files
│   ├── config/            # Database and API configs
│   └── manifest.json      # Generation metadata
├── monitor/               # Monitoring modules
│   ├── file_watcher.py    # File system monitoring
│   └── network_monitor.py # Network activity monitoring
├── alerts/                # Alerting system
│   └── logger.py          # Alert logging and notifications
├── utils/                 # Utility modules
│   └── config_manager.py  # Configuration management
├── config/                # Configuration files
│   └── config.yaml        # Main configuration
├── logs/                  # Log files
│   ├── alerts.log         # Security alerts
│   ├── activity.log       # General activity
│   └── errors.log         # Error messages
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize HoneyHawk behavior:

```yaml
honeyhawk:
  version: "1.0.0"
  name: "HoneyHawk Canary Monitor"

tokens:
  generate_aws: true
  generate_ssh: true
  generate_database: true
  generate_api: true
  regenerate_interval_days: 30

monitoring:
  file_watch_enabled: true
  network_monitor_enabled: true
  ssh_honeypot_port: 2222

alerting:
  log_to_file: true
  system_notifications: true
  email_alerts: false
  discord_webhook: ""
  slack_webhook: ""

logging:
  log_level: "INFO"
  max_log_size_mb: 100
  rotate_logs: true
```

## Security Considerations

### Safe Deployment
- **Isolated Environment**: Deploy in controlled environments only
- **Network Segmentation**: Ensure honeypot ports don't conflict with production services
- **Access Control**: Limit access to HoneyHawk directories and logs
- **Regular Updates**: Keep dependencies updated for security

### Token Safety
- **No Real Credentials**: All generated tokens are fake and non-functional
- **Clear Identification**: Tokens are marked as canary/honeypot credentials
- **Secure Storage**: Tokens are stored locally and not transmitted externally
- **Git Safety**: Comprehensive `.gitignore` prevents accidental credential exposure

### Repository Security
**IMPORTANT**: This repository uses a comprehensive `.gitignore` to prevent committing:
- Generated canary tokens and credentials
- Log files containing security alerts
- Configuration files with sensitive settings
- Runtime data and process files

Before deployment:
1. Copy `config/config.yaml.example` to `config/config.yaml`
2. Customize settings for your environment
3. Never commit actual tokens or logs to version control

## Log Analysis

### Alert Log Format
```json
{
  "timestamp": "2025-01-30T14:23:15.123456",
  "severity": "HIGH",
  "type": "SECURITY_ALERT",
  "message": "CANARY TRIGGERED - File Access Detected!",
  "details": "File: credentials\nEvent: opened\n...",
  "epoch": 1643556195.123
}
```

### Analyzing Logs
```bash
# View recent alerts
tail -f logs/alerts.log

# Count alerts by severity
grep '"severity": "HIGH"' logs/alerts.log | wc -l

# Export last 24 hours of data
python -c "
from alerts.logger import AlertLogger
from pathlib import Path
logger = AlertLogger(Path('logs'))
logger.export_logs(Path('export.json'), 24)
"
```

## Advanced Usage

### Custom Token Generation
```python
from tokens.generator import TokenGenerator
from alerts.logger import AlertLogger
from pathlib import Path

logger = AlertLogger(Path("logs"))
generator = TokenGenerator(Path("custom_tokens"), logger)

# Generate specific token types
generator.generate_aws_credentials()
generator.generate_ssh_keys()
```

### Programmatic Monitoring
```python
from monitor.file_watcher import FileWatcher
from alerts.logger import AlertLogger
from pathlib import Path

logger = AlertLogger(Path("logs"))
watcher = FileWatcher(Path("tokens"), logger)

watcher.start()
# ... your code here ...
watcher.stop()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

HoneyHawk is designed for educational purposes, security research, and authorized testing environments only. Users are responsible for complying with all applicable laws and regulations. The authors are not responsible for any misuse of this tool.

## Support

- **Issues**: [GitHub Issues](https://github.com/abdulrafay1-4/honeyhawk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/abdulrafay1-4/honeyhawk/discussions)
- **Security**: For security concerns, please email security@example.com

## Acknowledgments

- [Watchdog](https://github.com/gorakhargosh/watchdog) for cross-platform file monitoring
- [PyYAML](https://pyyaml.org/) for configuration management
- The Blue Team and threat detection community for inspiration

---

**Made with love by [Abdul Rafay](https://github.com/abdulrafay1-4)**
