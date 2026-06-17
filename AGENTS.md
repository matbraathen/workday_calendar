# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository.

## Project overview

A small, dependency-free Python library that calculates where you land in time
when moving a number of **workdays** forward or backward from a starting point.
A workday excludes weekends, one-off ("unique") holidays and yearly
("recurring") holidays. Time is only counted inside a configured working window.

## Layout

| File | Purpose |
| --- | --- |
| `workday_calendar.py` | `Calendar` class (public API) + argparse CLI (`main`). |
| `utils.py` | Pure helper functions implementing the date arithmetic. |
| `calendar_test.py` | pytest suite. |
| `.github/workflows/python-package.yml` | CI: lint (flake8) + tests (pytest). |

## Setup

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Common commands

```bash
# Run the full test suite
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=term-missing

# Lint (matches CI)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Run the CLI (note: quote the start datetime)
python workday_calendar.py "24/5/2004 18:03" -6.7470217 \
  --holiday "27/5/2004" --recurring-holiday "17/5"
```

## Date / time formats

- Start datetime: `dd/mm/yyyy HH:MM`
- Unique holiday: `dd/mm/yyyy`
- Recurring holiday: `dd/mm`
- Workday hours: `HH:MM`

## Conventions

- Pure standard library only — do **not** add runtime dependencies. Dev-only
  tooling (pytest, flake8, coverage) belongs in `requirements-dev.txt`.
- Keep `utils.py` functions pure; they take the owning `calendar` as the first
  argument and must not print.
- Raise `ValueError`/`TypeError` with a clear message for invalid input rather
  than printing or returning sentinel values.
- The parametrized expected results in `calendar_test.py` encode intended
  behavior. If you change the core arithmetic, update those cases deliberately
  and explain why.

## Definition of done

Before finishing a change, make sure both of these are green:

1. `python -m pytest`
2. `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
