---
name: cloud-security
description: 云安全 — AWS/Azure/GCP渗透、容器安全、Kubernetes安全
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cloud, aws, azure, gcp, kubernetes, container, docker, trivy, prowler]
---

# 云安全工具链

## 核心工具

| 工具 | 用途 | Stars |
|------|------|-------|
| **Prowler** | 多云安全审计 | 12K+ |
| **ScoutSuite** | 多云攻击面报告 | 3K+ |
| **Pacu** | AWS漏洞利用框架 | 5K+ |
| **Stratus Red Team** | 云对手模拟 | 2.3K |
| **Trivy** | 容器/K8s安全扫描 | 36K |
| **kube-bench** | K8s CIS基准检查 | 7K+ |
| **KubeArmor** | K8s运行时安全 | 2K+ |
| **amicontained** | 容器安全检测 | 3K+ |

---

## 1. Prowler — 多云安全审计

### 安装
```bash
pip install prowler
```

### 用法
```bash
# AWS
prowler aws

# Azure
prowler azure

# GCP
prowler gcp

# Web UI
prowler dashboard

# 指定检查
prowler aws --checks check11 check12

# 指定合规标准
prowler aws --compliance cis_2.0_aws
prowler aws --compliance pci_dss_4.0
prowler aws --compliance hipaa

# 输出格式
prowler aws -M json -o output/
prowler aws -M html -o output/
```

---

## 2. Pacu — AWS漏洞利用

### 安装
```bash
pip install pacu
```

### 用法
```bash
pacu

# 设置AWS密钥
set_keys

# 列出模块
list

# 常用模块
run iam_privesc_by_rollback
run iam_backdoor_users_keys
run iam_backdoor_users_password
run lambda_backdoor
run ec2_ami_snapshot
run secrets
```

---

## 3. Stratus Red Team — 云对手模拟

### 安装
```bash
curl -sL https://github.com/DataDog/stratus-red-team/releases/latest/download/stratus-red-team_Linux_x86_64.tar.gz | tar xz
sudo mv stratus-red-team /usr/local/bin/
```

### 用法
```bash
# 列出可用攻击
stratus list

# 预热(准备攻击条件)
stratus warmup aws.persistence.iam-create-admin-user

# 执行攻击
stratus detonate aws.persistence.iam-create-admin-user

# 清理
stratus cleanup aws.persistence.iam-create-admin-user

# 按平台过滤
stratus list --platform aws
stratus list --platform azure
stratus list --platform k8s
```

---

## 4. Trivy — 容器安全扫描

### 安装
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

### 用法
```bash
# 扫描容器镜像
trivy image python:3.4-alpine

# 扫描文件系统
trivy fs --scanners vuln,secret,misconfig ./

# 扫描Git仓库
trivy repo https://github.com/org/repo

# 扫描K8s集群
trivy k8s --report summary cluster

# 扫描IaC
trivy config ./terraform/

# 输出格式
trivy image -o report.json -f json python:3.4
trivy image -o report.html -f template --template '@contrib/html.tpl' python:3.4
```

---

## 5. kube-bench — K8s CIS基准

### 安装
```bash
# Docker运行
docker run --pid=host -v /etc:/node/etc:ro -v /var:/node/var:ro \
  aquasec/kube-bench:latest run --targets node

# K8s Job
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs kube-bench
```

---

## 6. KubeArmor — K8s运行时安全

### 安装
```bash
helm repo add kubearmor https://kubearmor.github.io/charts
helm install kubearmor kubearmor/kubearmor
```

### 安全策略示例
```yaml
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: deny-curl
spec:
  selector:
    matchLabels:
      app: my-app
  process:
    matchPaths:
    - path: /usr/bin/curl
      action: Block
```

---

## Pitfalls

1. **云渗透需要授权** — 未授权访问云环境是违法的
2. **Prowler需要云凭据** — 需要配置AWS/Azure/GCP认证
3. **Trivy扫描镜像需要网络** — 离线环境需提前下载漏洞库
4. **kube-bench只检查不修复** — 需要手动修复发现的问题
5. **Stratus Red Team会产生真实攻击** — 只在测试环境使用
6. **KubeArmor需要内核支持** — 需要AppArmor或SELinux
