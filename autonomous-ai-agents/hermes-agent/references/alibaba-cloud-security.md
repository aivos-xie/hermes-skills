# Alibaba Cloud ECS Security Hardening

## Quick Checklist

### 1. Firewall (firewalld)
```bash
systemctl start firewalld
systemctl enable firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

### 2. SSH Hardening
```bash
# Disable root login
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
```
**Prerequisite:** Ensure you have a non-root user with sudo access before disabling root login.

### 3. SELinux
Alibaba Cloud Linux 3 ships with SELinux disabled by default. Consider enabling if security requirements demand it.

### 4. Security Updates
```bash
yum check-update --security
yum update -y --security
```

### 5. AliYunDun (Alibaba Cloud Security Agent)
Pre-installed on Alibaba Cloud ECS. Process: `AliYunDun` / `AliYunDunMonitor`. This is normal — do not kill these processes.
