# Bandit Level 0 → Level 1

## Objective

Log into the Bandit game server using SSH.

---

## Problem

The first step was establishing a remote SSH connection using the provided credentials:

- Host: bandit.labs.overthewire.org  
- Port: 2220  
- Username: bandit0  

The server runs SSH on a non-default port.

---

## Solution

Connect using the `-p` flag to specify the custom port:

```bash
ssh bandit0@bandit.labs.overthewire.org -p 2220
```

After authenticating with the provided password, access to the remote environment was established.

---

## Key Takeaways

- SSH enables secure remote shell access.
- The `-p` flag specifies a non-standard port.
- Accurate interpretation of connection parameters is essential.
- Remote access forms the foundation for system-level interaction.

---

## Practical Relevance

SSH is fundamental to:

- Cloud infrastructure management  
- DevOps workflows  
- Secure production server access  
- Automation and CI/CD operations  

This level establishes the baseline skill of securely accessing remote Linux systems.