"""
Token Generator Module
Generates realistic fake credentials for various services
"""

import os
import random
import string
import secrets
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class TokenGenerator:
    def __init__(self, tokens_dir: Path, alert_logger):
        self.tokens_dir = tokens_dir
        self.alert_logger = alert_logger
        self.tokens_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different credential types
        self.aws_dir = self.tokens_dir / ".aws"
        self.ssh_dir = self.tokens_dir / ".ssh"
        self.config_dir = self.tokens_dir / "config"
        
        for directory in [self.aws_dir, self.ssh_dir, self.config_dir]:
            directory.mkdir(exist_ok=True)
    
    def generate_aws_credentials(self) -> Dict[str, str]:
        """Generate fake AWS credentials"""
        access_key = f"AKIA{self._random_string(16, string.ascii_uppercase + string.digits)}"
        secret_key = self._random_string(40, string.ascii_letters + string.digits + "+/")
        
        credentials_content = f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
region = us-east-1

[honeyhawk-trap]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
region = us-west-2
"""
        
        # Write to multiple locations to increase chances of discovery
        credential_files = [
            self.aws_dir / "credentials",
            self.aws_dir / "fake_credentials",
            self.tokens_dir / "aws.txt",
            self.tokens_dir / ".env_aws"
        ]
        
        for file_path in credential_files:
            file_path.write_text(credentials_content)
            
        self.alert_logger.log_info(f"Generated AWS credentials in {len(credential_files)} files")
        return {"access_key": access_key, "secret_key": secret_key}
    
    def generate_ssh_keys(self) -> Dict[str, str]:
        """Generate fake SSH private key"""
        # Generate a fake but realistic-looking SSH private key
        fake_key = f"""-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
Nh{self._random_string(400, string.ascii_letters + string.digits + "+/=")}
{self._random_string(64, string.ascii_letters + string.digits + "+/=")}
{self._random_string(64, string.ascii_letters + string.digits + "+/=")}
{self._random_string(64, string.ascii_letters + string.digits + "+/=")}
{self._random_string(64, string.ascii_letters + string.digits + "+/=")}
{self._random_string(64, string.ascii_letters + string.digits + "+/=")}
-----END OPENSSH PRIVATE KEY-----"""
        
        ssh_files = [
            self.ssh_dir / "id_rsa",
            self.ssh_dir / "fake_id_rsa",
            self.tokens_dir / "server_key.pem",
            self.tokens_dir / "backup_key"
        ]
        
        for file_path in ssh_files:
            file_path.write_text(fake_key)
            # Set appropriate permissions (readable by owner only)
            os.chmod(file_path, 0o600)
            
        self.alert_logger.log_info(f"Generated SSH keys in {len(ssh_files)} files")
        return {"key_files": [str(f) for f in ssh_files]}
    
    def generate_database_config(self) -> Dict[str, str]:
        """Generate fake database configuration"""
        username = random.choice(["admin", "root", "dbuser", "postgres", "mysql"])
        password = self._random_string(12, string.ascii_letters + string.digits)
        host = random.choice(["localhost", "db.internal", "database.company.com"])
        
        configs = {
            "db_config.ini": f"""[database]
host = {host}
port = 5432
username = {username}
password = {password}
database = production
ssl_mode = require
""",
            ".env": f"""DB_HOST={host}
DB_PORT=5432
DB_USER={username}
DB_PASS={password}
DB_NAME=production
DATABASE_URL=postgresql://{username}:{password}@{host}:5432/production
""",
            "database.json": json.dumps({
                "host": host,
                "port": 5432,
                "username": username,
                "password": password,
                "database": "production",
                "ssl": True
            }, indent=2)
        }
        
        for filename, content in configs.items():
            file_path = self.config_dir / filename
            file_path.write_text(content)
            
        self.alert_logger.log_info(f"Generated database configs in {len(configs)} files")
        return {"username": username, "password": password, "host": host}
    
    def generate_api_tokens(self) -> Dict[str, str]:
        """Generate fake API tokens for various services"""
        tokens = {
            "github_token": f"ghp_{self._random_string(36, string.ascii_letters + string.digits)}",
            "slack_token": f"xoxb-{'-'.join([self._random_string(11, string.digits) for _ in range(3)])}",
            "discord_bot_token": f"{self._random_string(24, string.ascii_letters + string.digits)}.{self._random_string(6, string.ascii_letters + string.digits)}.{self._random_string(27, string.ascii_letters + string.digits + '-_')}",
            "stripe_key": f"sk_live_{self._random_string(24, string.ascii_letters + string.digits)}",
            "sendgrid_key": f"SG.{self._random_string(22, string.ascii_letters + string.digits + '-_')}.{self._random_string(43, string.ascii_letters + string.digits + '-_')}"
        }
        
        # Create .env file with API tokens
        env_content = f"""# API Tokens
GITHUB_TOKEN={tokens['github_token']}
SLACK_BOT_TOKEN={tokens['slack_token']}
DISCORD_BOT_TOKEN={tokens['discord_bot_token']}
STRIPE_SECRET_KEY={tokens['stripe_key']}
SENDGRID_API_KEY={tokens['sendgrid_key']}

# Other sensitive data
JWT_SECRET={self._random_string(32, string.ascii_letters + string.digits)}
ENCRYPTION_KEY={self._random_string(32, string.ascii_letters + string.digits)}
"""
        
        env_files = [
            self.tokens_dir / ".env",
            self.tokens_dir / ".env.local",
            self.tokens_dir / "api_keys.txt",
            self.config_dir / "secrets.env"
        ]
        
        for file_path in env_files:
            file_path.write_text(env_content)
            
        self.alert_logger.log_info(f"Generated API tokens in {len(env_files)} files")
        return tokens
    
    def generate_all_tokens(self):
        """Generate all types of canary tokens"""
        print("Generating AWS credentials...")
        self.generate_aws_credentials()
        
        print("Generating SSH keys...")
        self.generate_ssh_keys()
        
        print("Generating database configs...")
        self.generate_database_config()
        
        print("Generating API tokens...")
        self.generate_api_tokens()
        
        # Create a manifest file
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "total_files": len(list(self.tokens_dir.rglob("*"))),
            "description": "HoneyHawk canary credentials - DO NOT USE IN PRODUCTION"
        }
        
        manifest_path = self.tokens_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        print(f"Generated {manifest['total_files']} canary credential files")
        self.alert_logger.log_info(f"Generated complete token set: {manifest['total_files']} files")
    
    def clean_tokens(self):
        """Remove all generated tokens"""
        if self.tokens_dir.exists():
            import shutil
            shutil.rmtree(self.tokens_dir)
            self.tokens_dir.mkdir(exist_ok=True)
            self.alert_logger.log_info("Cleaned all canary tokens")
    
    def _random_string(self, length: int, charset: str = None) -> str:
        """Generate a random string of specified length"""
        if charset is None:
            charset = string.ascii_letters + string.digits
        return ''.join(secrets.choice(charset) for _ in range(length))
