# ConfigGuard

**ConfigGuard** is a comprehensive security configuration checker tool designed to assess the security posture of various systems and applications. The tool helps organizations ensure their systems are hardened against attacks by verifying adherence to security best practices and compliance frameworks.

![ConfigGuard](https://github.com/user-attachments/assets/e3941746-1937-4f0a-af5c-c49c2dbdeb4a)


## Features

ConfigGuard offers a variety of security checks across different domains:

### User and Access Management

- **Disable Root Login**: Prevents direct root access via SSH, encouraging the use of `sudo` for privileged operations.
- **Enforce Strong Password Policies**: Ensures passwords meet complexity requirements, are regularly changed, and accounts are locked out after failed attempts.
- **Review User Accounts**: Regularly audits and removes unnecessary or inactive user accounts.
- **Restrict `sudo` Access**: Limits `sudo` privileges to authorized users and specific commands only.

### SSH Hardening

- **Disable Password Authentication**: Enforces SSH key-based authentication for improved security.
- **Change Default SSH Port**: Moves SSH away from the default port 22 to a less common one.
- **Limit SSH Access**: Restricts SSH access to specific IP addresses or networks.
- **Fail2Ban Configuration**: Installs and configures Fail2Ban to block repeated failed login attempts.

### System Configuration

- **Keep the System Updated**: Regularly checks that the system and all installed packages are up-to-date to patch vulnerabilities.
- **Remove Unnecessary Services and Software**: Uninstalls unused software and disables unnecessary services to minimize the attack surface.
- **Enable a Firewall**: Ensures a firewall (e.g., iptables or firewalld) is configured to control incoming and outgoing traffic.
- **SELinux or AppArmor Configuration**: Enables and configures SELinux or AppArmor for Mandatory Access Control (MAC).
- **Kernel Hardening**: Implements kernel hardening options like `grsecurity` or `sysctl` settings to protect against exploits.

### File System and Permissions

- **Secure File Permissions**: Ensures appropriate file permissions and ownership to prevent unauthorized access.
- **Immutable Files**: Uses `chattr +i` to make critical configuration files immutable.
- **File Integrity Monitoring**: Implements tools like AIDE or Tripwire to detect unauthorized changes to files.
- **No World-Writable Files**: Ensures that no files are world-writable.
- **No SUID/SGID Executables**: Ensures no unnecessary SUID/SGID executables exist.

### Logging and Auditing

- **Centralized Logging**: Configures `syslog` or `rsyslog` to send logs to a central server for analysis and monitoring.
- **Auditd Configuration**: Enables and configures `auditd` to track system activity and potential security events.

### Additional Measures

- **Regular Backups**: Ensures regular backups of critical data to facilitate recovery in case of a breach.
- **Security Audits**: Performs periodic security audits to identify vulnerabilities and assess compliance.

### Security Check Results

The tool generates a detailed report showing the status of each check:

- **PASS**: The check has been successfully passed.
- **FAIL**: The check has failed and requires attention.
- **INFO**: Informational output or suggestions for further action.

## Installation

To install and run ConfigGuard:

1. **Clone the repository**:
   ```bash
   git clone git@github.com:un1xr00t/ConfigGuard.git
   cd ConfigGuard
