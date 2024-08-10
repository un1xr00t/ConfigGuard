import os
import subprocess

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

def check_unused_user_accounts(days=90):
    threshold = subprocess.run(['sudo', 'lastlog', '-b', str(days)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    unused_accounts = [line.split()[0] for line in threshold.stdout.splitlines() if line.split()[0] != 'Username']
    return unused_accounts

def check_world_writable_files():
    result = subprocess.run(['sudo', 'find', '/', '-xdev', '-type', 'f', '-perm', '-0002', '-print'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return len(result.stdout.strip()) == 0

def check_suid_sgid_executables():
    result = subprocess.run(['sudo', 'find', '/', '-xdev', '-perm', '-4000', '-o', '-perm', '-2000', '-type', 'f', '-print'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return len(result.stdout.strip()) == 0

def check_package_updates():
    result = subprocess.run(['sudo', 'apt-get', '-s', 'upgrade'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return "0 upgraded" in result.stdout

def check_sudo_restrictions():
    try:
        with open('/etc/sudoers', 'r') as file:
            sudo_restrictions = file.readlines()
        return sudo_restrictions
    except FileNotFoundError:
        return []

def check_fail2ban_configured():
    status = subprocess.run(['sudo', 'systemctl', 'is-enabled', 'fail2ban'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return 'enabled' in status.stdout.lower()

def check_critical_files_immutable():
    result = subprocess.run(['lsattr', '/etc/passwd', '/etc/shadow', '/etc/gshadow', '/etc/group'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return all('i' in line for line in result.stdout.splitlines())

def check_file_integrity_monitoring():
    result = subprocess.run(['sudo', 'systemctl', 'is-active', 'aide'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return 'active' in result.stdout.lower()

def check_inactive_services():
    result = subprocess.run(['sudo', 'systemctl', 'list-units', '--type=service', '--state=inactive'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    inactive_services = [line.split()[0] for line in result.stdout.splitlines() if '.service' in line]
    return inactive_services

def check_unnecessary_active_services():
    unnecessary_services = [
        "snap-bare-5.mount",
        "accounts-daemon.service",
        "apparmor.service",
        "bluetooth.service"
    ]
    active_services = []
    for service in unnecessary_services:
        result = subprocess.run(['sudo', 'systemctl', 'is-active', service], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if 'active' in result.stdout.lower():
            active_services.append(service)
    return active_services

def generate_report(issues):
    with open("security_report.txt", "w") as report_file:
        report_file.write("Security Configuration Checker - Remediation Report\n")
        report_file.write("="*50 + "\n\n")
        for issue, remediation in issues.items():
            report_file.write(f"Issue: {issue}\n")
            report_file.write(f"Remediation: {remediation}\n\n")
        report_file.write("="*50 + "\n")
        report_file.write("End of Report\n")
    print("\nDetailed remediation steps have been written to 'security_report.txt'")

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
    }

    # Dictionary to store remediation steps for failed checks
    issues = {}

    print("Security Check Results:\n")
    for check, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{check}: {status}")
        
        if not result:  # If the check failed
            if check == "SSH Root Login Disabled":
                issues[check] = "Edit /etc/ssh/sshd_config and set 'PermitRootLogin no'. Then restart the SSH service."
            elif check == "SSH Password Authentication Disabled":
                issues[check] = "Edit /etc/ssh/sshd_config and set 'PasswordAuthentication no'. Then restart the SSH service."
            elif check == "Firewall Active":
                issues[check] = "Enable the firewall using 'sudo ufw enable' and ensure it is active."
            elif check == "Password Policy Max Days":
                issues[check] = "Edit /etc/login.defs and set 'PASS_MAX_DAYS' to 90 or fewer days."
            elif check == "Password Policy Min Length":
                issues[check] = "Edit /etc/login.defs and set 'PASS_MIN_LEN' to 8 or more characters."
            elif check == "No World-Writable Files":
                issues[check] = "Identify and secure world-writable files using 'sudo find / -xdev -type f -perm -0002 -exec chmod o-w {} \;'."
            elif check == "No SUID/SGID Executables":
                issues[check] = "Identify and secure SUID/SGID files using 'sudo find / -xdev -perm -4000 -o -perm -2000 -exec chmod u-s,g-s {} \;'."
            elif check == "All Packages Up-to-Date":
                issues[check] = "Update all packages using 'sudo apt-get update && sudo apt-get upgrade'."
            elif check == "Fail2Ban Not Configured":
                issues[check] = "Install and configure Fail2Ban using 'sudo apt-get install fail2ban' and enable the service."
            elif check == "Critical Files Immutable":
                issues[check] = "Set critical files as immutable using 'sudo chattr +i /etc/passwd /etc/shadow /etc/gshadow /etc/group'."
            elif check == "File Integrity Monitoring Implemented":
                issues[check] = "Install and configure AIDE or another file integrity monitoring tool to protect critical files."

    # Generate report for failed checks only
    if issues:
        generate_report(issues)
    else:
        print("\nAll security checks passed. No issues to report.")

    # Print summary of issues
    if issues:
        print("\nSummary of Issues Detected:")
        for issue in issues.keys():
            print(f"  - {issue}")
        print("\nPlease review the detailed remediation steps in 'security_report.txt'.")
    else:
        print("\nNo security issues detected. The system appears secure.")

if __name__ == "__main__":
    main()
