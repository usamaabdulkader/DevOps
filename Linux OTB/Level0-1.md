# Bandit Level 1 → Level 2

## Objective

Retrieve the password stored in a file named `-`.

---

## Problem

Running:

```bash
cat -
```

did not display the file contents. Instead, the command waited for input.

This occurs because many Unix tools interpret `-` as standard input (stdin), not as a literal filename.

---

## Key Concepts

- Special argument handling in Unix commands  
- Standard input (stdin)  
- Command-line argument parsing  
- Filename disambiguation  

---

## Solution

To treat `-` as a filename rather than stdin, it must be referenced explicitly:

```bash
cat ./-
```

or

```bash
cat -- -
```

---

## Explanation

- `./-` specifies a file named `-` in the current directory.
- `--` marks the end of command options, forcing the following argument to be interpreted strictly as a filename.

The issue was not file access, but argument interpretation.

---

## Key Takeaways

- The shell parses arguments before command execution.
- Many Unix tools reserve `-` to represent stdin.
- Explicit disambiguation prevents unintended behavior.
- Accurate command construction avoids subtle errors.

---

## Practical Relevance

This pattern applies directly to:

- Writing reliable shell scripts  
- Handling edge-case filenames  
- Automating system tasks  
- Preventing parsing-related bugs in production  

Understanding how commands interpret arguments improves reliability and debugging efficiency.