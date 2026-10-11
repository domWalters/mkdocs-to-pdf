---
name: check-modified-files
description: Runs pre-commit checks against modified files that aren't yet committed
---

## What I do

Run the pre-commit hooks (formatting, linting, typing, security, lockfile
sync, ...) against the files changed relative to `HEAD`.

## How to use

```bash
make check
```
