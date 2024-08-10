import os

def check_world_writable_files():
    """
    Check for world-writable files on the system.
    World-writable files can be a security risk as they can be modified by any user.
    """
    result = os.system('sudo find / -type f -perm -0002 -print > /dev/null 2>&1')
    return result != 0

def check_suid_sgid_executables():
    """
    Check for files with SUID/SGID permissions.
    SUID/SGID files can be a security risk as they allow users to run the file with the permissions of the file's owner or group.
    """
    result = os.system('sudo find / -perm /6000 -type f -exec ls -ld {} \; > /dev/null 2>&1')
    return result != 0

def make_critical_files_immutable():
    """
    Ensure critical system files are immutable.
    Making files immutable prevents them from being altered or deleted.
    """
    critical_files = ['/etc/passwd', '/etc/shadow']
    immutable = True
    for file in critical_files:
        result = os.system(f'lsattr {file} | grep -q "\-i\-"')
        if result != 0:
            immutable = False
            break
    return immutable

def implement_file_integrity_monitoring():
    """
    Check if a file integrity monitoring tool (like AIDE) is installed.
    File integrity monitoring helps detect unauthorized changes to critical files.
    """
    result = os.system('dpkg -s aide > /dev/null 2>&1')
    return result == 0
