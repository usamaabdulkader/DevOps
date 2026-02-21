# OverTheWire Bandit – Linux Fundamentals & Systems Thinking

This repository documents my structured progression through the OverTheWire Bandit wargame.

Rather than focusing only on solutions, this project emphasizes:

- Diagnostic reasoning
- Shell behavior understanding
- Filesystem metadata analysis
- Stream processing
- Encoding and compression workflows
- Network communication models
- TLS protocol awareness
- Secure authentication mechanisms

The goal was not to “complete levels,” but to build and document core Linux and systems-level skills relevant to DevOps and infrastructure engineering.

---

## What This Project Demonstrates

### 1. Command-Line Precision

- Argument parsing and shell interpretation
- Handling special characters and edge-case filenames
- Understanding stdin, stdout, and stderr behavior
- Stream redirection and piping

### 2. Filesystem & Metadata Awareness

- File type inspection (`file`)
- Metadata-driven searches (`find`)
- Ownership and permission filtering
- Byte-level size constraints

### 3. Stream Processing & Text Manipulation

- Pattern matching (`grep`)
- Deduplication (`sort | uniq`)
- Character translation (`tr`)
- Extracting strings from binary (`strings`)

### 4. Encoding & Compression Analysis

- Base64 decoding
- Hexdump reconstruction (`xxd -r`)
- Iterative decompression workflows
- Identifying file formats via magic numbers

### 5. Networking Fundamentals

- Raw TCP communication (`nc`)
- Client vs server roles
- Protocol layering (TCP vs TLS)
- TLS negotiation with `openssl s_client`
- CRLF vs LF behavior
- Input timing and EOF semantics

### 6. Secure Authentication

- SSH key-based authentication
- Permission constraints on private keys
- Client execution context awareness

---

## Why This Matters

Bandit progressively shifts from:

- Basic command usage  
to  
- Structured filesystem querying  
to  
- Stream composition  
to  
- Binary inspection  
to  
- Protocol-level debugging  

This mirrors real-world infrastructure troubleshooting:

- Investigating unexpected system behavior
- Debugging service communication issues
- Identifying data format mismatches
- Handling layered compression or encoding
- Diagnosing TLS-related failures
- Understanding authentication context

The progression demonstrates increasing systems-level awareness rather than isolated command knowledge.

---

## Repository Structure

Each level contains:

- Objective
- Problem analysis
- Key concepts
- Solution approach
- Technical explanation
- Practical relevance

The emphasis is on reasoning and tool selection, not just command execution.

---

## Core Tools Practiced

- `ssh`
- `find`
- `file`
- `grep`
- `sort`
- `uniq`
- `tr`
- `strings`
- `xxd`
- `tar`
- `gzip` / `bzip2`
- `nc`
- `openssl s_client`

---

## Takeaway

This project strengthened:

- Linux command-line fluency
- Diagnostic methodology
- Tool chaining and composition
- Protocol awareness
- Secure remote access practices

It reflects deliberate practice in foundational Linux and networking concepts essential for DevOps, cloud engineering, and systems troubleshooting.
