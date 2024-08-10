import os

def allowed_services():
    return [
        'ssh.service',
        'cron.service',
        'networking.service',
        'ufw.service'
        # Add other essential services as needed
    ]

def remove_unnecessary_services():
    services = os.popen("systemctl list-unit-files | grep enabled").read().splitlines()
    unnecessary_services = []
    inactive_services = []
    
    for service in services:
        service_name = service.split()[0]
        
        # Skip template services with the '@' wildcard
        if '@' in service_name:
            continue

        service_status = os.popen(f"systemctl is-active {service_name}").read().strip()
        
        # Identify inactive services
        if service_status == "inactive":
            inactive_services.append(service_name)
        
        # Identify unnecessary active services
        if service_name not in allowed_services() and service_status == "active":
            unnecessary_services.append(service_name)
    
    return unnecessary_services, inactive_services

def keep_system_updated():
    result = os.system('sudo apt-get update > /dev/null && sudo apt-get -s upgrade | grep -P "^\d+ upgraded," | awk \'{print $1}\'')
    return int(result) == 0

def enable_firewall():
    firewall_status = os.system('sudo ufw status | grep -i active > /dev/null 2>&1')
    return firewall_status == 0
