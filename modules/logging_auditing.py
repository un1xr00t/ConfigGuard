import os

def configure_centralized_logging():
    result = os.system('grep -q "@@" /etc/rsyslog.conf')
    return result == 0

def configure_auditd():
    auditd_status = os.system('systemctl is-active auditd > /dev/null 2>&1')
    return auditd_status == 0
