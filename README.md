# ConfigGuard

![ConfigGuard](https://github.com/user-attachments/assets/07ad333e-c5c0-471d-9629-a1d05d4393c5)

## Overview

**ConfigGuard** is a comprehensive security configuration checker designed to help organizations ensure their systems are securely configured and hardened against attacks. The tool performs a wide range of security checks across various domains, providing detailed remediation steps for any issues detected.

## Features

### User and Access Management

- **Disable SSH Root Login:** Verifies that root login via SSH is disabled, encouraging the use of `sudo` for privileged operations.
- **Password Policy Enforcement:** Checks for compliance with password policies, including maximum password age and minimum password length.
- **Review Unused User Accounts:** Identifies and reports any unused or inactive user accounts.
- **Restrict `sudo` Access:** Ensures that `sudo` privileges are restricted to authorized users only.

### SSH Hardening

- **Disable SSH Password Authentication:** Ensures that SSH password authentication is disabled, enforcing SSH key-based authentication for enhanced security.
- **Fail2Ban Configuration:** Verifies that Fail2Ban is installed and configured to protect against brute force attacks.

### System Configuration

- **Firewall Status:** Checks if a firewall (e.g., UFW) is active and properly configured.
- **Package Updates:** Ensures that all system packages are up-to-date to mitigate vulnerabilities.
- **Kernel Hardening:** Verifies that critical kernel parameters (e.g., `kernel.randomize_va_space`, `kernel.exec-shield`, `net.ipv4.tcp_syncookies`) are configured for enhanced security.
- **SELinux/AppArmor Status:** Ensures that SELinux or AppArmor is enabled and configured for Mandatory Access Control (MAC).
- **Disable Unnecessary Services:** Identifies and reports unnecessary services that should be disabled to reduce the system's attack surface.
- **Open Ports Check:** Ensures that the number of open ports is minimized, reducing potential entry points for attackers.

### File System and Permissions

- **No World-Writable Files:** Ensures that no files are world-writable, which could allow unauthorized modifications.
- **No SUID/SGID Executables:** Verifies that there are no unnecessary SUID/SGID executables that could be exploited for privilege escalation.
- **Critical Files Immutable:** Ensures that critical system files (e.g., `/etc/passwd`, `/etc/shadow`) are set as immutable to prevent unauthorized changes.
- **File Integrity Monitoring Implemented:** Checks if file integrity monitoring tools (e.g., AIDE) are in place to detect unauthorized file changes.

### Logging and Auditing

- **File Integrity Monitoring:** Confirms that file integrity monitoring tools like AIDE are actively monitoring critical files.
- **Auditd Configuration:** Ensures that auditd is enabled and configured to monitor critical system events.

## Security Check Results

ConfigGuard generates a comprehensive report with the results of each security check:

- **PASS:** The check has passed, indicating that the configuration meets security requirements.
- **FAIL:** The check has failed, highlighting areas that need attention.
- **INFO:** Provides additional information or recommendations for further action.

## Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/un1xr00t/ConfigGuard.git
   cd ConfigGuard
