#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alibaba Cloud ECS Integration Setup Script
自动配置阿里云 ECS 接入
"""

import json
import os
import sys
from pathlib import Path

# Configuration
WORKSPACE_DIR = Path(__file__).parent.parent
SSH_DIR = Path.home() / ".ssh"
ENV_FILE = WORKSPACE_DIR / ".env"

def print_banner():
    print("=" * 60)
    print("  Alibaba Cloud ECS Integration Setup")
    print("  阿里云 ECS 接入配置工具")
    print("=" * 60)
    print()

def get_ecs_info():
    """Get ECS information from user"""
    print("📋 Please provide your ECS information:")
    print("   请提供您的 ECS 信息:\n")
    
    ecs_ip = input("ECS Public IP (公网 IP): ").strip()
    ecs_user = input("SSH Username [root]: ").strip() or "root"
    ecs_port = input("SSH Port [22]: ").strip() or "22"
    ecs_region = input("Region (e.g., cn-shanghai): ").strip()
    
    return {
        "ip": ecs_ip,
        "user": ecs_user,
        "port": ecs_port,
        "region": ecs_region
    }

def check_ssh_key():
    """Check if SSH key exists"""
    ssh_key = SSH_DIR / "id_ed25519"
    ssh_pub_key = SSH_DIR / "id_ed25519.pub"
    
    if ssh_key.exists() and ssh_pub_key.exists():
        print(f"✅ SSH key found: {ssh_key}")
        return True
    else:
        print(f"⚠️  SSH key not found: {ssh_key}")
        return False

def generate_ssh_key():
    """Generate SSH key pair"""
    print("\n🔑 Generating SSH key pair...")
    
    import subprocess
    try:
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-C", "alibaba-cloud-ecs", "-f", str(SSH_DIR / "id_ed25519")],
            check=True
        )
        print("✅ SSH key generated successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to generate SSH key: {e}")
        return False

def update_ssh_config(ecs_info):
    """Update SSH config file"""
    ssh_config = SSH_DIR / "config"
    
    config_content = f"""# Alibaba Cloud ECS Configuration
# Generated: 2026-03-14

Host aliyun-ecs
    HostName {ecs_info['ip']}
    User {ecs_info['user']}
    Port {ecs_info['port']}
    IdentityFile C:/Users/华为/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes

Host ecs
    HostName {ecs_info['ip']}
    User {ecs_info['user']}
    Port {ecs_info['port']}
"""
    
    # Backup existing config
    if ssh_config.exists():
        backup = ssh_config.with_suffix(".bak")
        ssh_config.rename(backup)
        print(f"✅ Backed up existing SSH config to {backup}")
    
    # Write new config
    with open(ssh_config, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ SSH config updated: {ssh_config}")
    return True

def update_env_file(ecs_info):
    """Update .env file"""
    env_content = f"""# OpenClaw Workspace Configuration
# Created: 2026-03-14

# -----------------------------------------------------------------------------
# Gateway Configuration
# -----------------------------------------------------------------------------
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_GATEWAY_HOST=127.0.0.1

# -----------------------------------------------------------------------------
# Alibaba Cloud ECS Configuration
# -----------------------------------------------------------------------------
ALIYUN_ECS_HOST={ecs_info['ip']}
ALIYUN_ECS_USER={ecs_info['user']}
ALIYUN_ECS_PORT={ecs_info['port']}
ALIYUN_ECS_REGION={ecs_info['region']}
ALIYUN_ECS_SSH_KEY=C:/Users/华为/.ssh/id_ed25519

# Remote Gateway
ALIYUN_GATEWAY_URL=http://{ecs_info['ip']}:18789

# Sync Configuration
SYNC_ENABLED=true
SYNC_INTERVAL=300

# -----------------------------------------------------------------------------
# Feishu (Lark) Configuration
# -----------------------------------------------------------------------------
FEISHU_APP_ID=cli_xxxxxxxxxxxxx
FEISHU_APP_SECRET=YOUR_APP_SECRET_HERE
FEISHU_USER_ID=ou_72a847b95fc25870dcdd8ce56d929252
FEISHU_ENABLED=true
"""
    
    # Backup existing .env
    if ENV_FILE.exists():
        backup = ENV_FILE.with_suffix(".bak")
        ENV_FILE.rename(backup)
        print(f"✅ Backed up existing .env to {backup}")
    
    # Write new .env
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ .env file updated: {ENV_FILE}")
    return True

def print_next_steps(ecs_info):
    """Print next steps"""
    print("\n" + "=" * 60)
    print("  ✅ Configuration Complete!")
    print("  配置完成!")
    print("=" * 60)
    print(f"""
📋 Next Steps / 下一步:

1. Test SSH Connection / 测试 SSH 连接:
   ssh aliyun-ecs

2. Upload SSH Public Key / 上传 SSH 公钥到 ECS:
   Type the following command on ECS:
   mkdir -p ~/.ssh && echo "YOUR_PUBLIC_KEY" >> ~/.ssh/authorized_keys

3. Install OpenClaw on ECS / 在 ECS 上安装 OpenClaw:
   ssh aliyun-ecs
   npm install -g openclaw
   openclaw gateway --port 18789

4. Configure Security Group / 配置安全组:
   - Allow port 22 (SSH)
   - Allow port 18789 (Gateway)
   - Allow port 80/443 (optional)

5. Test Gateway Connection / 测试 Gateway 连接:
   curl http://{ecs_info['ip']}:18789/health

6. Start File Sync / 启动文件同步:
   rsync -avz -e ssh /d/OpenClaw/workspace/ aliyun-ecs:/root/openclaw-workspace/

📖 Documentation / 文档:
   str(Path(__file__).parent.parent)\\30-scripts-tools\\01-SETUP\\ALINYUN-ECS-INTEGRATION.md

""")

def main():
    print_banner()
    
    # Check SSH directory
    SSH_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get ECS info
    ecs_info = get_ecs_info()
    
    # Check/generate SSH key
    if not check_ssh_key():
        if input("\nGenerate SSH key? (y/n): ").lower() == 'y':
            generate_ssh_key()
    
    # Update configurations
    update_ssh_config(ecs_info)
    update_env_file(ecs_info)
    
    # Print next steps
    print_next_steps(ecs_info)
    
    print("✅ Setup complete! Press Enter to exit...")
    input()

if __name__ == '__main__':
    main()
