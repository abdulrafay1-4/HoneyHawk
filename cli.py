#!/usr/bin/env python3
"""
HoneyHawk CLI Utility
Command-line interface for managing HoneyHawk
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

from alerts.logger import AlertLogger
from tokens.generator import TokenGenerator


def show_status():
    """Show HoneyHawk status"""
    print("HoneyHawk Status")
    print("=" * 30)
    
    # Check if tokens exist
    tokens_dir = Path("tokens")
    if tokens_dir.exists():
        token_files = list(tokens_dir.rglob("*"))
        file_count = len([f for f in token_files if f.is_file() and not f.name.startswith('__')])
        print(f"Token files: {file_count}")
        
        manifest = tokens_dir / "manifest.json"
        if manifest.exists():
            with open(manifest) as f:
                data = json.load(f)
                print(f"Last generated: {data.get('generated_at', 'Unknown')}")
    else:
        print("Token files: None (run 'generate' first)")
    
    # Check logs
    logs_dir = Path("logs")
    if logs_dir.exists():
        alert_logger = AlertLogger(logs_dir)
        summary = alert_logger.get_alert_summary()
        print(f"Total alerts: {summary['total_alerts']}")
        print(f"High severity: {summary['high_severity']}")
        print(f"Last 24h: {summary['last_24h']}")
    else:
        print("Logs: None")


def list_tokens():
    """List all generated canary tokens"""
    tokens_dir = Path("tokens")
    if not tokens_dir.exists():
        print("No tokens found. Run 'generate' first.")
        return
    
    print("Canary Token Files")
    print("=" * 30)
    
    for token_file in sorted(tokens_dir.rglob("*")):
        if token_file.is_file() and not token_file.name.startswith('__'):
            rel_path = token_file.relative_to(tokens_dir)
            size = token_file.stat().st_size
            print(f"{rel_path} ({size} bytes)")


def show_recent_alerts(hours=24):
    """Show recent alerts"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("No logs found.")
        return
    
    alert_logger = AlertLogger(logs_dir)
    alerts = alert_logger.get_recent_alerts(hours)
    
    print(f"Recent Alerts (Last {hours} hours)")
    print("=" * 40)
    
    if not alerts:
        print("No alerts in the specified time period.")
        return
    
    for alert in alerts[-10:]:  # Show last 10 alerts
        timestamp = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
        severity = alert['severity']
        message = alert['message']
        
        severity_prefix = {"HIGH": "[HIGH]", "MEDIUM": "[MED]", "LOW": "[LOW]"}.get(severity, "[UNK]")
        print(f"{timestamp} {severity_prefix} {message}")


def export_logs(output_file, hours=24):
    """Export logs to file"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("No logs found.")
        return
    
    alert_logger = AlertLogger(logs_dir)
    alert_logger.export_logs(Path(output_file), hours)
    print(f"Exported {hours} hours of logs to {output_file}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="HoneyHawk - Canary Credential Monitor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py status                 # Show system status
  python cli.py generate              # Generate new tokens
  python cli.py list                  # List all token files
  python cli.py alerts               # Show recent alerts
  python cli.py alerts --hours 48    # Show alerts from last 48 hours
  python cli.py export report.json   # Export logs to file
  python cli.py clean                # Clean all tokens
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show HoneyHawk status')
    
    # Generate command
    subparsers.add_parser('generate', help='Generate new canary tokens')
    
    # List command
    subparsers.add_parser('list', help='List all canary token files')
    
    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='Show recent alerts')
    alerts_parser.add_argument('--hours', type=int, default=24, 
                              help='Hours to look back (default: 24)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export logs to file')
    export_parser.add_argument('output', help='Output file path')
    export_parser.add_argument('--hours', type=int, default=24,
                              help='Hours to export (default: 24)')
    
    # Clean command
    subparsers.add_parser('clean', help='Clean all canary tokens')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'status':
            show_status()
        elif args.command == 'generate':
            alert_logger = AlertLogger(Path("logs"))
            generator = TokenGenerator(Path("tokens"), alert_logger)
            generator.generate_all_tokens()
        elif args.command == 'list':
            list_tokens()
        elif args.command == 'alerts':
            show_recent_alerts(args.hours)
        elif args.command == 'export':
            export_logs(args.output, args.hours)
        elif args.command == 'clean':
            alert_logger = AlertLogger(Path("logs"))
            generator = TokenGenerator(Path("tokens"), alert_logger)
            generator.clean_tokens()
            print("Cleaned all canary tokens")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
