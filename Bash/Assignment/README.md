# Bash Scripting Assignments

This repository contains foundational Bash scripting exercises focused on core Linux command-line skills and automation patterns.

The scripts demonstrate structured scripting, input handling, file operations, conditional logic, and basic automation workflows.

---

## Scripts Included

### 1. calculator.sh
Performs basic arithmetic operations (addition, subtraction, multiplication, division) on two user-provided integers.

**Concepts demonstrated:**
- Arithmetic expansion `$(( ))`
- Conditional logic
- Division-by-zero handling
- User input handling

---

### 2. file_operations.sh
Creates a directory and file, writes a message including the current date, and displays the file contents.

**Concepts demonstrated:**
- Directory creation (`mkdir -p`)
- Command substitution `$(date +%F)`
- Variable usage and quoting
- File I/O operations

---

### 3. file_checker.sh
Checks whether a file exists and reports its read, write, and execute permissions.

**Concepts demonstrated:**
- File test operators (`-e`, `-r`, `-w`, `-x`)
- Conditional branching
- Structured output formatting

---

### 4. backup_txt.sh
Backs up all `.txt` files from a source directory into a timestamped backup directory and reports the number of files copied.

**Concepts demonstrated:**
- Looping over file patterns
- Timestamp generation
- Defensive scripting
- File copying and counting logic

---

## How to Run

Make a script executable:

```bash
chmod +x script_name.sh
```

Run the script:

```bash
./script_name.sh
```

---

## Purpose

These exercises reinforce core Bash fundamentals including:

- Input validation
- Conditional statements
- File and directory manipulation
- Looping constructs
- Defensive scripting practices

This repository reflects structured practice in Linux shell scripting and foundational automation concepts.
