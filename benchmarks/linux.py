import os
import pwd
import datetime

def check_ssh_security_settings():
    required_settings = {
        'PermitRootLogin': ['no', 'prohibit-password'],
        'PasswordAuthentication': ['no'],
        'PermitEmptyPasswords': ['no'],
        'ChallengeResponseAuthentication': ['no'],
        'X11Forwarding': ['no'],
    }
    
    results = {}
    
    with open('/etc/ssh/sshd_config', 'r') as file:
        lines = file.readlines()
    
    for setting, valid_values in required_settings.items():
        setting_found = False
        
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if line.startswith('#'):
                continue  # Skip commented lines
            if line.startswith(setting):
                setting_found = True
                parts = line.split()
                if len(parts) == 2 and parts[1] in valid_values:
                    results[setting] = (True, None)
                else:
                    results[setting] = (False, (
                        f"The {setting} setting is not securely configured. "
                        f"To fix this, edit the /etc/ssh/sshd_config file and set "
                        f"'{setting} {valid_values[0]}'. Then, restart the SSH service: "
                        "'sudo systemctl restart sshd'."
                    ))
                break
        
        if not setting_found:
            results[setting] = (False, (
                f"The {setting} setting is missing, commented out, or not found in the SSH config file. "
                f"To fix this, add '{setting} {valid_values[0]}' to the /etc/ssh/sshd_config file "
                "and restart the SSH service."
            ))

    return results

def check_firewall_status():
    status = os.system('sudo ufw status | grep -i active > /dev/null 2>&1')
    if status == 0:
        return True, None
    else:
        return False, (
            "The firewall is not active. "
            "To enable the firewall, use the following commands: "
            "'sudo ufw enable' to activate, and 'sudo ufw status' to verify."
        )

def check_password_policy_max_days():
    with open('/etc/login.defs', 'r') as file:
        for line in file:
            if line.strip().startswith('#') or not line.strip():
                continue
            
            parts = line.split()
            
            if len(parts) == 2 and parts[0] == 'PASS_MAX_DAYS':
                try:
                    max_days = int(parts[1])
                    if max_days <= 90:
                        return True, None
                    else:
                        return False, (
                            "The maximum password age is set too high. "
                            "To fix this, edit the /etc/login.defs file and set "
                            "'PASS_MAX_DAYS 90'. This will enforce password changes every 90 days."
                        )
                except ValueError:
                    return False, (
                        "The value for 'PASS_MAX_DAYS' is not a valid number. "
                        "Please ensure it is an integer, e.g., 'PASS_MAX_DAYS 90'."
                    )
    
    return False, (
        "Could not find the 'PASS_MAX_DAYS' setting in the /etc/login.defs file. "
        "To fix this, add 'PASS_MAX_DAYS 90' to enforce password changes every 90 days."
    )

def check_password_policy_min_length():
    with open('/etc/login.defs', 'r') as file:
        for line in file:
            if line.strip().startswith('#') or not line.strip():
                continue

            parts = line.split()

            if len(parts) == 2 and parts[0] == 'PASS_MIN_LEN':
                try:
                    min_len = int(parts[1])
                    if min_len >= 8:
                        return True, None
                    else:
                        return False, (
                            "The minimum password length is set too low. "
                            "To fix this, edit the /etc/login.defs file and set "
                            "'PASS_MIN_LEN 8'. This will enforce a minimum password length of 8 characters."
                        )
                except ValueError:
                    return False, (
                        "The value for 'PASS_MIN_LEN' is not a valid number. "
                        "Please ensure it is an integer, e.g., 'PASS_MIN_LEN 8'."
                    )
    
    return False, (
        "Could not find the 'PASS_MIN_LEN' setting in the /etc/login.defs file. "
        "To fix this, add 'PASS_MIN_LEN 8' to enforce a minimum password length of 8 characters."
    )

def check_unused_user_accounts(days=90):
    threshold = datetime.datetime.now() - datetime.timedelta(days=days)
    for user in pwd.getpwall():
        if user.pw_uid >= 1000 and user.pw_shell != '/usr/sbin/nologin':
            last_login = os.popen(f"lastlog -u {user.pw_name} | tail -n 1 | awk '{{print $4,$5,$9}}'").read().strip()
            
            if not last_login or 'Never' in last_login or '**' in last_login:
                continue 
            
            try:
                last_login_date = datetime.datetime.strptime(last_login, "%b %d %Y")
                if last_login_date < threshold:
                    return False, (
                        f"User '{user.pw_name}' has not logged in for more than {days} days. "
                        "Consider disabling or removing this account if it is no longer needed. "
                        "To disable the account, use: 'sudo usermod -L {user.pw_name}'."
                    )
            except ValueError:
                return False, (
                    f"User '{user.pw_name}' has an invalid last login date format: '{last_login}'. "
                    "Please verify the last login date manually."
                )
    
    return True, None

def check_world_writable_files():
    result = os.system('find / -xdev -type f -perm -0002 -print > /dev/null 2>&1')
    if result == 0:
        return False, (
            "There are world-writable files on the system. "
            "To fix this, find and review these files using: "
            "'sudo find / -xdev -type f -perm -0002 -print'. "
            "If needed, change the permissions using: 'chmod o-w <file>'."
        )
    return True, None

def check_suid_sgid_executables():
    result = os.system('find / -xdev \( -perm -4000 -o -perm -2000 \) -type f -print > /dev/null 2>&1')
    if result == 0:
        return False, (
            "There are SUID/SGID executables on the system. "
            "To fix this, find and review these files using: "
            "'sudo find / -xdev \\( -perm -4000 -o -perm -2000 \\) -type f -print'. "
            "If appropriate, remove the SUID/SGID permissions using: 'chmod u-s <file>' or 'chmod g-s <file>'."
        )
    return True, None

def check_for_package_updates():
    result = os.system('sudo apt-get -s upgrade | grep -P "^\d+ upgraded, \d+ newly installed, \d+ to remove and \d+ not upgraded." | awk \'{print $1}\'')
    if int(result) > 0:
        return False, (
            "There are packages that need to be updated. "
            "To fix this, run: 'sudo apt-get update' followed by 'sudo apt-get upgrade'. "
            "This will update all installed packages to their latest versions."
        )
    return True, None

def check_unusual_processes():
    result = os.system("ps aux | awk '{print $11}' | grep -vE '^/usr|^/bin|^/sbin|^/lib' > /dev/null 2>&1")
    if result == 0:
        return False, (
            "There are processes running from unusual locations. "
            "To investigate, use: 'ps aux | awk \'{print $11}\' | grep -vE \'^[^/]+$\' '. "
            "Identify and terminate any suspicious processes."
        )
    return True, None

def run_linux_checks():
    checks = {
        **check_ssh_security_settings(),
        'Firewall Active': check_firewall_status(),
        'Password Policy Max Days': check_password_policy_max_days(),
        'Password Policy Min Length': check_password_policy_min_length(),
        'No Unused User Accounts': check_unused_user_accounts(),
        'No World-Writable Files': check_world_writable_files(),
        'No SUID/SGID Executables': check_suid_sgid_executables(),
        'All Packages Up-to-Date': check_for_package_updates(),
        'No Unusual Processes': check_unusual_processes(),
    }
    return checks
