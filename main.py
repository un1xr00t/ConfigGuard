import os
import subprocess
from reports.report_generator import generate_report 

# Function to print the banner
def print_banner():
    banner = """
\033[34m   ______            _____       ______                     __
  / ____/___  ____  / __(_)___ _/ ____/_  ______ __________/ /
 / /   / __ \/ __ \/ /_/ / __ `/ / __/ / / / __ `/ ___/ __  / 
/ /___/ /_/ / / / / __/ / /_/ / /_/ / /_/ / /_/ / /  / /_/ /  
\____/\____/_/ /_/_/ /_/\__, /\____/\__,_/\__,_/_/   \__,_/   
                       /____/                                 \033[0m
    """
    print(banner)

# Call the function at the start of your script
print_banner()

# Security check functions
def check_ssh_root_login():
    try:
        with open('/etc/ssh/sshd_config', 'r') as file:
            for line in file:
                if line.startswith('PermitRootLogin'):
                    return 'no' in line.split()[1].lower()
    except FileNotFoundError:
        return False
    return False

def check_ssh_password_authentication():
    try:
        with open('/etc/ssh/sshd_config', 'r') as file:
            for line in file:
                if line.startswith('PasswordAuthentication'):
                    return 'no' in line.split()[1].lower()
    except FileNotFoundError:
        return False
    return False

def check_firewall_status():
    status = subprocess.run(['sudo', 'ufw', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return 'active' in status.stdout.lower()

def check_password_policy_max_days():
    try:
        with open('/etc/login.defs', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('PASS_MAX_DAYS') and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            max_days = int(parts[1])
                            return max_days <= 90
                        except ValueError:
                            return False
    except FileNotFoundError:
        return False
    return False

def check_password_policy_min_length():
    try:
        with open('/etc/login.defs', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('PASS_MIN_LEN') and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            min_length = int(parts[1])
                            return min_length >= 8
                        except ValueError:
                            return False
    except FileNotFoundError:
        return False
    return False

def check_world_writable_files():
    result = subprocess.run(['sudo', 'find', '/', '-xdev', '-type', 'f', '-perm', '-0002', '-print'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return len(result.stdout.strip()) == 0

def check_suid_sgid_executables():
    result = subprocess.run(['sudo', 'find', '/', '-xdev', '-perm', '-4000', '-o', '-perm', '-2000', '-type', 'f', '-print'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return len(result.stdout.strip()) == 0

def check_package_updates():
    result = subprocess.run(['sudo', 'apt-get', '-s', 'upgrade'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return "0 upgraded" in result.stdout

def check_fail2ban_configured():
    status = subprocess.run(['sudo', 'systemctl', 'is-enabled', 'fail2ban'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return 'enabled' in status.stdout.lower()

def check_critical_files_immutable():
    result = subprocess.run(['lsattr', '/etc/passwd', '/etc/shadow', '/etc/gshadow', '/etc/group'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return all('i' in line for line in result.stdout.splitlines())

def check_file_integrity_monitoring():
    result = subprocess.run(['sudo', 'systemctl', 'is-active', 'aide'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return 'active' in result.stdout.lower()

def check_kernel_hardening():
    required_settings = {
        'kernel.randomize_va_space': '2', 
        'kernel.exec-shield': '1',         
        'net.ipv4.tcp_syncookies': '1'     
    }

    try:
        with open('/etc/sysctl.conf', 'r') as f:
            lines = f.readlines()
            for setting, value in list(required_settings.items()):
                for line in lines:
                    if line.startswith(setting) and value in line.split('=')[1].strip():
                        required_settings.pop(setting)
                        break
            return not required_settings
    except FileNotFoundError:
        return False

def check_selinux_apparmor():
    selinux_status = subprocess.run(['getenforce'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    apparmor_status = subprocess.run(['sudo', 'aa-status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    selinux_enabled = 'Enforcing' in selinux_status.stdout
    apparmor_enabled = 'active' in apparmor_status.stdout and 'complain' not in apparmor_status.stdout

    return selinux_enabled or apparmor_enabled

def check_unnecessary_services():
    services_to_check = ['inetd', 'rsh', 'rlogin', 'telnet', 'ftp'] 
    for service in services_to_check:
        status = subprocess.run(['sudo', 'systemctl', 'is-active', service], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if 'active' in status.stdout.lower():
            return False
    return True

def check_open_ports():
    result = subprocess.run(['sudo', 'netstat', '-tulpn'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    num_open_ports = len(result.stdout.splitlines()) - 2  # Adjust for headers
    return num_open_ports <= 30 

def main():
    results = {
        "SSH Root Login Disabled": check_ssh_root_login(),
        "SSH Password Authentication Disabled": check_ssh_password_authentication(),
        "Firewall Active": check_firewall_status(),
        "Password Policy Max Days": check_password_policy_max_days(),
        "Password Policy Min Length": check_password_policy_min_length(),
        "No World-Writable Files": check_world_writable_files(),
        "No SUID/SGID Executables": check_suid_sgid_executables(),
        "All Packages Up-to-Date": check_package_updates(),
        "Fail2Ban Configured": check_fail2ban_configured(),
        "Critical Files Immutable": check_critical_files_immutable(),
        "File Integrity Monitoring Implemented": check_file_integrity_monitoring(),
        "Kernel Hardening Configured": check_kernel_hardening(),
        "SELinux or AppArmor Enabled": check_selinux_apparmor(),
        "Unnecessary Services Disabled": check_unnecessary_services(),
        "Limited Number of Open Ports": check_open_ports(),
    }

    # Dictionary to store remediation steps for failed checks
    issues = {}

    print("\033[34mSecurity Check Results:\n\033[0m") 
    for check, result in results.items():
        check_title = f"\033[34m{check}\033[0m" 
        if result:
            status = "\033[32mPASS\033[0m" 
            print(f"{check_title}: {status}")
        else:
            status = "\033[31mFAIL\033[0m" 
            print(f"{check_title}: {status}")
            # Add to issues with remediation
            if check == "SSH Root Login Disabled":
                issues[check] = {"fix": "Edit /etc/ssh/sshd_config and set 'PermitRootLogin no'.", "service_restart": "ssh"}
            elif check == "SSH Password Authentication Disabled":
                issues[check] = {"fix": "Edit /etc/ssh/sshd_config and set 'PasswordAuthentication no'.", "service_restart": "ssh"}
            elif check == "Firewall Active":
                issues[check] = {"fix": "Enable the firewall using 'sudo ufw enable' and ensure it is active."}
            elif check == "Password Policy Max Days":
                issues[check] = {"fix": "Edit /etc/login.defs and set 'PASS_MAX_DAYS' to 90 or fewer days."}
            elif check == "Password Policy Min Length":
                issues[check] = {"fix": "Edit /etc/login.defs and set 'PASS_MIN_LEN' to 8 or more characters."}
            elif check == "No World-Writable Files":
                issues[check] = {"fix": "Identify and secure world-writable files using 'sudo find / -xdev -type f -perm -0002 -exec chmod o-w {} \;'."}
            elif check == "No SUID/SGID Executables":
                issues[check] = {"fix": "Identify and secure SUID/SGID files using 'sudo find / -xdev -perm -4000 -o -perm -2000 -exec chmod u-s,g-s {} \;'."}
            elif check == "All Packages Up-to-Date":
                issues[check] = {"fix": "Update all packages using 'sudo apt-get update && sudo apt-get upgrade'."}
            elif check == "Fail2Ban Configured":
                issues[check] = {"fix": "Install and configure Fail2Ban using 'sudo apt-get install fail2ban' and enable the service.", "service_restart": "fail2ban"}
            elif check == "Critical Files Immutable":
                issues[check] = {"fix": "Set critical files as immutable using 'sudo chattr +i /etc/passwd /etc/shadow /etc/gshadow /etc/group'."}
            elif check == "File Integrity Monitoring Implemented":
                issues[check] = {"fix": "Install and configure AIDE or another file integrity monitoring tool to protect critical files.", "service_restart": "aide"}
            elif check == "Kernel Hardening Configured":
                issues[check] = {"fix": "Edit /etc/sysctl.conf and add/modify the required kernel hardening settings. Then run 'sudo sysctl -p' to apply changes."}
            elif check == "SELinux or AppArmor Enabled":
                issues[check] = {"fix": "Enable and configure either SELinux or AppArmor. Refer to your distribution's documentation for specific instructions."}
            elif check == "Limited Number of Open Ports":
                issues[check] = {"fix": "Identify and close unnecessary open ports. Use firewall rules to restrict access as needed."}

    # Generate report for failed checks only if there are any
    if issues:
        generate_report(results, issues)  # Pass both 'results' and 'issues'
        print("\n\033[31mSummary of Issues Detected:\033[0m") 
        for issue in issues.keys():
            print(f"  - \033[31m{issue}\033[0m") 
        print("\nPlease review the detailed remediation steps in 'security_report.txt'.")
    else:
        generate_report(results, issues)
        print("\nAll security checks passed. The system appears secure.")

if __name__ == "__main__":
    main()