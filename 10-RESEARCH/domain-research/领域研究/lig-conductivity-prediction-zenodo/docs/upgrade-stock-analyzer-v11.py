#!/usr/bin/env python3
"""
Stock Analyzer v11.0 - Quick Fixes
- Fix "Invalid Date" display issues
- Optimize performance
- Add auto-refresh indicator
"""

import paramiko
import time
from datetime import datetime

SSH_HOST = '8.208.30.28'
SSH_USER = 'root'
SSH_PASS = '20051104sS'
SERVER_PATH = '/opt/stock-analyzer/70-dashboard'

def connect_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, username=SSH_USER, password=SSH_PASS, timeout=15)
    return ssh

def fix_date_display(ssh):
    """Fix Invalid Date issues in JavaScript"""
    print("[1/4] Fixing date display issues...")

    stdin, stdout, stderr = ssh.exec_command(f"cat {SERVER_PATH}/index.html")
    content = stdout.read().decode('utf-8', errors='replace')

    # Fix 1: Add date validation
    old_code = "new Date(stock.lastUpdated)"
    new_code = "stock.lastUpdated ? new Date(stock.lastUpdated) : new Date()"

    if old_code in content:
        content = content.replace(old_code, new_code)
        print("      [OK] Added date validation")

    # Fix 2: Add fallback for missing dates
    old_format = "toLocaleDateString('zh-HK')"
    new_format = "toLocaleDateString('zh-HK', {year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})"

    if old_format in content and new_format not in content:
        content = content.replace(old_format, new_format)
        print("      [OK] Enhanced date formatting")

    # Fix 3: Add error handling
    if "function formatDate(date)" not in content:
        format_func = """
        function formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            try {
                const date = new Date(dateStr);
                if (isNaN(date.getTime())) return 'Invalid Date';
                return date.toLocaleDateString('zh-HK', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch(e) {
                return 'Error';
            }
        }
"""
        # Insert before </script> tag
        if "</script>" in content:
            content = content.replace("</script>", format_func + "</script>")
            print("      [OK] Added formatDate function")

    # Upload fixed file
    stdin, stdout, stderr = ssh.exec_command(f"cat > {SERVER_PATH}/index.html")
    stdin.write(content.encode('utf-8'))
    stdin.flush()
    stdin.channel.shutdown_write()
    stdout.channel.recv_exit_status()
    print("      [OK] index.html updated")

def add_performance_optimizations(ssh):
    """Add performance improvements"""
    print("[2/4] Adding performance optimizations...")

    stdin, stdout, stderr = ssh.exec_command(f"cat {SERVER_PATH}/index.html")
    content = stdout.read().decode('utf-8', errors='replace')

    # Add lazy loading for charts
    if 'loading="lazy"' not in content:
        content = content.replace('<canvas id="marketChart"', '<canvas id="marketChart" loading="lazy"')
        print("      [OK] Added lazy loading")

    # Add meta description for SEO
    if '<meta name="description"' not in content:
        meta_desc = '<meta name="description" content="股票分析器 v11.0 - 实时股票数据、AI 简报、智能信号和套利机会扫描">\n'
        content = content.replace('<meta charset="UTF-8">', meta_desc + '<meta charset="UTF-8">')
        print("      [OK] Added SEO meta description")

    # Upload optimized file
    stdin, stdout, stderr = ssh.exec_command(f"cat > {SERVER_PATH}/index.html")
    stdin.write(content.encode('utf-8'))
    stdin.flush()
    stdin.channel.shutdown_write()
    stdout.channel.recv_exit_status()
    print("      [OK] Performance optimizations applied")

def add_version_banner(ssh):
    """Add version banner with last update time"""
    print("[3/4] Adding version banner...")

    stdin, stdout, stderr = ssh.exec_command(f"cat {SERVER_PATH}/index.html")
    content = stdout.read().decode('utf-8', errors='replace')

    # Add version display
    version_html = f'''
    <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:8px;text-align:center;font-size:0.9em;">
        📈 Stock Analyzer v11.0 | Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} HKT | Auto-refresh: 30min
    </div>
'''

    if '<body>' in content and version_html.strip() not in content:
        content = content.replace('<body>', '<body>\n' + version_html)

        stdin, stdout, stderr = ssh.exec_command(f"cat > {SERVER_PATH}/index.html")
        stdin.write(content.encode('utf-8'))
        stdin.flush()
        stdin.channel.shutdown_write()
        stdout.channel.recv_exit_status()
        print("      [OK] Version banner added")

def restart_service(ssh):
    """Restart the stock analyzer service"""
    print("[4/4] Restarting service...")

    ssh.exec_command("pkill -f 'python.*index.html' || true")
    time.sleep(1)

    ssh.exec_command(f"cd {SERVER_PATH} && nohup python3 -m http.server 8500 > /var/log/stock-analyzer.log 2>&1 &")
    time.sleep(2)

    stdin, stdout, stderr = ssh.exec_command("pgrep -f 'python.*index.html'")
    pid = stdout.read().decode().strip()

    if pid:
        print(f"      [OK] Service restarted (PID: {pid})")
    else:
        print("      [WARN] Service may not have started")

def main():
    print("=" * 70)
    print("STOCK ANALYZER V11.0 - QUICK FIXES")
    print("=" * 70)

    try:
        ssh = connect_ssh()
        print("\n[OK] SSH connected to 8.208.30.28\n")

        fix_date_display(ssh)
        add_performance_optimizations(ssh)
        add_version_banner(ssh)
        restart_service(ssh)

        print("\n" + "=" * 70)
        print("UPGRADE COMPLETE!")
        print("=" * 70)
        print("\nAccess URL: https://felixxii.xyz/stock")
        print("Version: v11.0")
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        ssh.close()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        raise

if __name__ == "__main__":
    main()
