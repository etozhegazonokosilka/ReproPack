# ReproPack

Create a safe diagnostic archive for reproducible bug reports.

ReproPack collects the technical context that maintainers and teammates usually
need to investigate a problem: operating-system metadata, Python environment,
safe Git state, and a bounded project tree. It writes the result as a ZIP
archive containing a machine-readable JSON report and a readable HTML report.

It is designed to help explain *where* a bug happened without copying source
files, environment files, Git remotes, diffs, or common credentials.

## Installation

ReproPack currently installs from source and requires Python 3.12 or newer.

```bash
git clone https://github.com/etozhegazonokosilka/ReproPack.git
cd ReproPack
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
```

## Usage

Run ReproPack from the project that has the problem:

```bash
.venv/bin/repropack .
```

The command creates `repropack-report.zip` in the current directory. To choose
another location or replace an existing archive:

```bash
.venv/bin/repropack /path/to/project --output /path/to/repropack-report.zip
.venv/bin/repropack . --output repropack-report.zip --overwrite
```

Inspect the archive with Python if `unzip` is unavailable:

```bash
python -m zipfile -l repropack-report.zip
```

The archive always contains:

```text
report.json
report.html
```

Open `report.html` in a browser for a readable overview. Use `report.json` for
automation or structured issue-processing tools.

## What ReproPack collects

- operating system name, version, and architecture;
- Python version, implementation, virtual-environment status, and installed
  package versions;
- safe Git metadata: branch, commit, dirty state, modified paths, and
  untracked paths;
- a relative, sorted project file tree with a maximum depth of four levels;
- ReproPack and report schema versions.

Git is optional. A report is still generated when Git is unavailable or the
target directory is not a Git repository.

## Privacy and safety

ReproPack is intentionally conservative. It does not collect:

- file contents, including `.env` files;
- environment variables;
- Git remotes, diffs, or commit messages;
- usernames, hostnames, IP addresses, or MAC addresses.

Common secret formats found in collected strings are replaced with
`[REDACTED]`, including API keys, GitHub tokens, OpenAI keys, Telegram tokens,
authorization values, database passwords, and private keys.

Always inspect a report before sharing it. Project and Git path names can still
contain information that is meaningful in your context, even though file
contents are never read.

## Development

Install development tools and run the checks:

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and
[SECURITY.md](SECURITY.md) for responsible security reporting.

## Scope of version 0.1.0

This first version supports local Python projects and Git metadata only. It
does not inspect Node.js, Docker, cloud accounts, authentication providers, or
external services. ReproPack has no telemetry and never sends reports anywhere
automatically.

## License

ReproPack is available under the [MIT License](LICENSE).
