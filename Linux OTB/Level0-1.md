# Bandit Level 0 → 1

## Level Goal

The password for the next level is stored in a file called `readme` located in the home directory.

After retrieving it, use SSH (port 2220) to log into `bandit1`.

---

##  Commands Used

- `ls`
- `cat`

---

## Solution Steps

### List files in the home directory

```bash
ls
```

Output:

```
readme
```

---

### Display the contents of the file

```bash
cat readme
```

Output:

```
<level-1-password>
```

---

### Login to the next level

```bash
ssh bandit1@bandit.labs.overthewire.org -p 2220
```

---

## 🧠 What I Learned

- How to list files in a directory using `ls`
- How to read file contents using `cat`
- Basic Linux home directory navigation
- The importance of securely storing credentials