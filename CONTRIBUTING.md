# Contributing to ReproPack

Thanks for taking the time to improve ReproPack.

## Before opening a pull request

1. Create a focused branch from `main`.
2. Keep changes small and include tests for changed behavior.
3. Use English for code, documentation, messages, and comments.
4. Do not add real secrets, `.env` files, generated reports, or personal data.
5. Run the complete check suite. On macOS, Linux, or WSL:

   ```bash
   .venv/bin/python -m pytest -q
   .venv/bin/python -m ruff check .
   .venv/bin/python -m ruff format --check .
   .venv/bin/python -m mypy src
   ```

   On Windows PowerShell:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q
   .\.venv\Scripts\python.exe -m ruff check .
   .\.venv\Scripts\python.exe -m ruff format --check .
   .\.venv\Scripts\python.exe -m mypy src
   ```

## Design principles

- Privacy comes before diagnostic detail.
- ReproPack must not read project file contents.
- Reports must not contain Git remotes, diffs, or environment variables.
- New collectors must have deterministic tests and document their data source.
- New secret patterns should be covered by redaction tests.

## Reporting bugs

Use the bug-report form on GitHub. If it is safe to do so, attach a freshly
generated ReproPack archive after reviewing its contents. Never attach secrets
or private source files.
