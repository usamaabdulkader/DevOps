# Bandit Level 0

## Goal
Log into the Bandit server using SSH.

- Host: bandit.labs.overthewire.org
- Port: 2220
- Username: bandit0

## Command Used

```bash
ssh bandit0@bandit.labs.overthewire.org -p 2220
```

## Command Breakdown

- `ssh` → Secure Shell client
- `username@host` → Remote login format
- `-p 2220` → Connect to non-default port

## What I Learned
- How to connect to a remote server
- How SSH works with custom ports
- Basics of secure remote access