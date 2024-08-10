import os

def disable_password_authentication():
    with open('/etc/ssh/sshd_config', 'r') as file:
        for line in file:
            if 'PasswordAuthentication' in line:
                return 'no' in line
    return False

def change_default_ssh_port():
    with open('/etc/ssh/sshd_config', 'r') as file:
        for line in file:
            if line.startswith('Port'):
                return line.strip().split()[-1] != '22'
    return False

def limit_ssh_access():
    with open('/etc/hosts.allow', 'r') as file:
        allow_list = [line.strip() for line in file if not line.startswith('#')]
    return allow_list

def configure_fail2ban():
    fail2ban_status = os.system('systemctl is-active fail2ban')
    return fail2ban_status == 0
