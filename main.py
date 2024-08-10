import os
import subprocess

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

def generate_report(issues):
    with open("security_report.txt", "w") as report_file:
        report_file.write("Security Configuration Checker - Remediation Report\n")
        report_file.write("="*50 + "\n\n")
        for issue, remediation in issues.items():
            report_file.write(f"Issue: {issue}\n")
            report_file.write(f"Remediation: {remediation}\n\n")
        report_file.write("="*50 + "\n")
        report_file.write("End of Report\n")

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

    print("\033[34mSecurity Check Results:\033[0m")  # Blue title for the results section
    for check, result in results.items():
        check_title = f"\033[34m{check}\033[0m"  # Blue color for titles
        if result:
            status = "\033[32mPASS\033[0m"  # Green color for PASS
            print(f"{check_title}: {status}")
        else:
            status = "\033[31mFAIL\033[0m"  # Red color for FAIL
            print(f"{check_title}: {status}")
            # Add to issues with remediation
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
            elif check == "Fail2Ban Configured":
                issues[check] = "Install and configure Fail2Ban using 'sudo apt-get install fail2ban' and enable the service."
            elif check == "Critical Files Immutable":
                issues[check] = "Set critical files as immutable using 'sudo chattr +i /etc/passwd /etc/shadow /etc/gshadow /etc/group'."
            elif check == "File Integrity Monitoring Implemented":
                issues[check] = "Install and configure AIDE or another file integrity monitoring tool to protect critical files."

    # Generate report for failed checks only if there are any
    if issues:
        generate_report(issues)
        print("\n\033[31mSummary of Issues Detected:\033[0m")  # Red title for summary
        for issue in issues.keys():
            print(f"  - \033[31m{issue}\033[0m")  # Red color for issues in summary
        print("\nPlease review the detailed remediation steps in 'security_report.txt'.")
    else:
        print("\nAll security checks passed. The system appears secure.")

if __name__ == "__main__":
    main()
