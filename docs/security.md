# Security Configuration Guide

This guide provides comprehensive security hardening recommendations for Chuk Virtual Shell in production environments.

## Table of Contents

- [Overview](#overview)
- [Threat Model](#threat-model)
- [Security Architecture](#security-architecture)
- [Configuration Hardening](#configuration-hardening)
- [Monitoring and Auditing](#monitoring-and-auditing)
- [Best Practices](#best-practices)
- [Incident Response](#incident-response)

## Overview

Chuk Virtual Shell is designed as a secure virtual environment for AI agent execution. This document outlines security controls and configuration options to ensure safe operation in production environments.

### Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal necessary permissions and access
3. **Fail Secure**: Default to secure configuration when in doubt
4. **Audit Everything**: Comprehensive logging for security monitoring
5. **Deterministic Execution**: Predictable behavior for security analysis

## Threat Model

### Primary Threats

| Threat Category | Description | Risk Level | Mitigations |
|----------------|-------------|------------|-------------|
| **Path Traversal** | Attempts to access files outside allowed directories using `../` or symlinks | High | Path restrictions, symlink controls |
| **Resource Exhaustion** | Memory bombs, infinite loops, excessive file creation | High | Resource quotas, timeouts |
| **Command Injection** | Malicious shell commands or code execution | Medium | Input validation, command parsing |
| **Data Exfiltration** | Unauthorized access to sensitive information | Medium | Sandboxing, network isolation |
| **Privilege Escalation** | Attempts to gain elevated system access | Low | Virtual environment isolation |
| **Persistence** | Malware attempting to survive session restarts | Low | Ephemeral execution environment |

### Attack Vectors

1. **Malicious Input**: Crafted commands designed to exploit parsing vulnerabilities
2. **Path Manipulation**: Directory traversal and symlink-based attacks
3. **Resource Abuse**: Commands that consume excessive CPU, memory, or storage
4. **Social Engineering**: Tricking users into executing dangerous commands
5. **Supply Chain**: Compromised scripts or configuration files

## Security Architecture

### Isolation Layers

```
┌─────────────────────────────────────────────┐
│                 AI Agent                    │
└─────────────────┬───────────────────────────┘
                  │ MCP/API Calls
┌─────────────────┼───────────────────────────┐
│                 │ Session Manager           │
│  ┌──────────────┼──────────────────────────┐ │
│  │              │ Command Parser           │ │
│  │  ┌───────────┼─────────────────────────┐ │ │
│  │  │           │ Virtual Shell           │ │ │
│  │  │  ┌────────┼────────────────────────┐ │ │ │
│  │  │  │        │ Virtual Filesystem     │ │ │ │
│  │  │  │  ┌─────┼───────────────────────┐ │ │ │ │
│  │  │  │  │     │ Storage Backend       │ │ │ │ │
│  │  │  │  │     │ (Memory/SQLite/S3)    │ │ │ │ │
│  │  │  │  └─────────────────────────────┘ │ │ │ │
│  │  │  └─────────────────────────────────┘ │ │ │
│  │  └───────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

### Security Boundaries

- **Process Isolation**: Each session runs in isolated virtual environment
- **Filesystem Isolation**: Complete separation from host filesystem
- **Network Isolation**: No network access by default
- **Resource Isolation**: Configurable limits on CPU, memory, and storage

## Configuration Hardening

### 1. Sandbox Configuration

#### High Security Profile (Recommended for AI Agents)

```python
high_security_config = {
    "sandbox": {
        "name": "high_security",
        "filesystem": {
            "root_restrictions": ["/sandbox", "/tmp"],
            "blocked_paths": ["/etc", "/proc", "/sys"],
            "max_files": 500,
            "max_storage_mb": 50,
            "readonly_paths": ["/sandbox/templates"]
        },
        "execution": {
            "timeout_seconds": 120,
            "max_memory_mb": 256,
            "allowed_commands": [
                "cat", "ls", "pwd", "cd", "mkdir", "touch", "rm",
                "echo", "grep", "sed", "awk", "sort", "head", "tail",
                "wc", "cut", "find", "python"
            ],
            "blocked_commands": [
                "curl", "wget", "ssh", "scp", "nc", "telnet",
                "exec", "eval", "source", "bash", "sh"
            ],
            "blocked_patterns": [
                r".*\b(curl|wget|ssh|nc)\b.*",
                r".*>/dev/(tcp|udp)/.*",
                r".*\$\(.*\).*" # Disable command substitution
            ]
        },
        "environment": {
            "allowed_env_vars": [
                "HOME", "USER", "PWD", "PATH", "SHELL",
                "PYTHONPATH", "VIRTUAL_ENV"
            ],
            "blocked_env_vars": [
                "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
                "SSH_AUTH_SOCK", "SSH_AGENT_PID"
            ]
        },
        "logging": {
            "audit_all_commands": true,
            "log_file_access": true,
            "log_env_changes": true,
            "retention_days": 90
        }
    }
}
```

#### Medium Security Profile (Development)

```python
medium_security_config = {
    "sandbox": {
        "name": "development",
        "filesystem": {
            "root_restrictions": ["/workspace", "/tmp", "/home"],
            "max_files": 5000,
            "max_storage_mb": 500
        },
        "execution": {
            "timeout_seconds": 600,
            "max_memory_mb": 1024,
            "blocked_commands": ["curl", "wget", "ssh"],
            "blocked_patterns": [r".*>/dev/(tcp|udp)/.*"]
        },
        "logging": {
            "audit_commands": ["rm", "cp", "mv", "python"],
            "log_file_access": false
        }
    }
}
```

### 2. Resource Limits

```python
resource_limits = {
    "memory": {
        "max_mb": 512,              # Maximum memory usage
        "warning_threshold": 0.8    # Warn at 80% usage
    },
    "storage": {
        "max_files": 1000,          # Maximum number of files
        "max_total_mb": 100,        # Maximum total storage
        "max_file_mb": 10           # Maximum individual file size
    },
    "execution": {
        "max_runtime_seconds": 300, # 5 minute maximum
        "max_processes": 1,         # Single process execution
        "cpu_limit_percent": 50     # Limit CPU usage
    }
}
```

### 3. Command Whitelisting

```python
command_security = {
    "whitelist_mode": True,         # Only allow explicitly listed commands
    "allowed_commands": [
        # File operations
        "ls", "cat", "head", "tail", "more", "find",
        "mkdir", "touch", "cp", "mv", "rm", "pwd", "cd",
        
        # Text processing
        "grep", "sed", "awk", "sort", "uniq", "wc", "cut", "tr",
        
        # System info (safe subset)
        "date", "whoami", "which", "history",
        
        # Environment (controlled)
        "export", "env", "alias",
        
        # Scripting (limited)
        "python", "echo", "test"
    ],
    "command_restrictions": {
        "python": {
            "blocked_modules": ["subprocess", "os", "socket", "urllib"],
            "blocked_imports": ["requests", "urllib3", "httpx"]
        },
        "find": {
            "max_depth": 5,
            "blocked_paths": ["/proc", "/sys", "/dev"]
        }
    }
}
```

### 4. Input Validation

```python
input_validation = {
    "max_command_length": 2048,     # Prevent buffer overflow attacks
    "blocked_characters": [
        "\x00",                     # Null bytes
        "\x01-\x08",               # Control characters
        "\x0e-\x1f",               # More control characters
    ],
    "pattern_filters": [
        r".*\$\{.*\}.*",           # Parameter expansion
        r".*`.*`.*",               # Command substitution
        r".*/dev/(tcp|udp)/.*",    # Network redirection
        r".*>&.*",                 # File descriptor manipulation
        r".*\|\|.*rm.*",           # Dangerous command chaining
    ],
    "quote_handling": {
        "max_nesting_depth": 3,
        "validate_balanced": True,
        "escape_sequences": "limited"
    }
}
```

## Monitoring and Auditing

### 1. Audit Logging

Enable comprehensive logging for security monitoring:

```python
audit_config = {
    "enabled": True,
    "format": "json",
    "fields": [
        "timestamp",
        "session_id", 
        "user_id",
        "command",
        "arguments", 
        "working_directory",
        "exit_code",
        "execution_time",
        "memory_used",
        "files_accessed",
        "files_created",
        "files_modified",
        "env_changes"
    ],
    "destinations": [
        {
            "type": "file",
            "path": "/var/log/chuk-shell/audit.log",
            "rotation": "daily",
            "retention": "90d"
        },
        {
            "type": "syslog",
            "facility": "auth",
            "severity": "info"
        },
        {
            "type": "webhook",
            "url": "https://siem.company.com/api/logs",
            "auth": "bearer_token"
        }
    ]
}
```

### 2. Security Metrics

Monitor these key security metrics:

- **Command Execution Rate**: Detect unusual activity spikes
- **Failed Command Rate**: Monitor for brute force or reconnaissance
- **Resource Usage Patterns**: Identify resource exhaustion attempts
- **Path Access Patterns**: Detect directory traversal attempts
- **Session Duration**: Monitor for unusually long sessions

### 3. Alerting Rules

```python
alert_rules = [
    {
        "name": "suspicious_commands",
        "condition": "command matches '^(curl|wget|nc|bash).*'",
        "severity": "high",
        "action": "terminate_session"
    },
    {
        "name": "path_traversal_attempt", 
        "condition": "arguments contains '../../../'",
        "severity": "high",
        "action": "block_command"
    },
    {
        "name": "resource_exhaustion",
        "condition": "memory_mb > 90% of limit OR files_created > 90% of limit",
        "severity": "medium",
        "action": "warn_and_limit"
    },
    {
        "name": "rapid_commands",
        "condition": "commands_per_minute > 60",
        "severity": "low", 
        "action": "rate_limit"
    }
]
```

## Best Practices

### 1. Deployment Security

- **Use TLS**: Always encrypt communication with the shell API
- **Authentication**: Implement strong authentication for API access  
- **Authorization**: Use role-based access control (RBAC)
- **Network Segmentation**: Isolate shell environments from sensitive systems
- **Regular Updates**: Keep the shell and dependencies updated

### 2. Configuration Management

- **Version Control**: Store configurations in version control
- **Environment Separation**: Use different configs for dev/staging/prod
- **Secrets Management**: Use dedicated secret management systems
- **Configuration Validation**: Validate configs before deployment
- **Backup and Recovery**: Maintain configuration backups

### 3. Operational Security

- **Principle of Least Privilege**: Grant minimal necessary permissions
- **Regular Security Reviews**: Periodic assessment of configurations
- **Incident Response Plan**: Prepared procedures for security incidents
- **Security Training**: Educate users on secure usage practices
- **Vulnerability Management**: Regular security scanning and updates

## Incident Response

### 1. Detection

Monitor for these security indicators:

- Multiple failed authentication attempts
- Suspicious command patterns (network tools, system reconnaissance)
- Unusual resource consumption patterns
- Path traversal attempts
- Attempts to access blocked files or commands

### 2. Response Procedures

#### Immediate Response

1. **Isolate**: Terminate affected sessions
2. **Preserve**: Save logs and forensic data
3. **Assess**: Determine scope and impact
4. **Contain**: Prevent further damage

#### Investigation

1. **Log Analysis**: Review audit logs for attack timeline
2. **Forensics**: Analyze session state and file changes
3. **Impact Assessment**: Determine what data/systems were affected
4. **Root Cause**: Identify vulnerability or misconfiguration

#### Recovery

1. **Cleanup**: Remove malicious files or changes
2. **Patch**: Fix identified vulnerabilities
3. **Restore**: Restore from clean backups if needed
4. **Monitor**: Enhanced monitoring for similar attacks

### 3. Post-Incident

- Document lessons learned
- Update security configurations
- Improve detection rules
- Conduct security training if needed
- Review and update incident response procedures

## Security Checklist

### Pre-Deployment

- [ ] Security configuration reviewed and approved
- [ ] Resource limits configured appropriately
- [ ] Command whitelisting enabled and tested
- [ ] Audit logging configured and tested
- [ ] Network isolation verified
- [ ] Authentication and authorization implemented
- [ ] TLS encryption enabled
- [ ] Security scanning completed
- [ ] Incident response procedures documented
- [ ] Security team trained on the system

### Post-Deployment

- [ ] Monitoring dashboards configured
- [ ] Alert rules tested and tuned
- [ ] Regular security reviews scheduled
- [ ] Log retention and archival configured
- [ ] Backup and recovery procedures tested
- [ ] Documentation updated
- [ ] User training completed
- [ ] Vulnerability scanning automated

### Ongoing Operations

- [ ] Regular security assessments
- [ ] Log analysis and review
- [ ] Configuration drift detection
- [ ] Security patch management
- [ ] Incident response drills
- [ ] Threat intelligence updates
- [ ] Performance and capacity monitoring
- [ ] User access reviews

## Additional Resources

- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)

For questions or security concerns, contact the security team at security@example.com.