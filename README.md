# Workday Calendar

A simple way to calculate where you end up in time when moving back or forth a
number of working days from a given point in time. A *working day* excludes
weekends, one-off ("unique") holidays and yearly ("recurring") holidays, and
time is only counted inside a configurable working window.

The library uses only the Python standard library.

## Quick start

```python
from workday_calendar import Calendar

calendar = Calendar("08:00", "16:00")        # working window, HH:MM
calendar.addHoliday("27/5/2004")             # unique holiday, dd/mm/yyyy
calendar.addRecurringHoliday("17/5")         # recurring holiday, dd/mm

result = calendar.addWorkDays("24/5/2004 18:03", -6.7470217)
print(result)  # 2004-05-13 10:02:00
```

`addWorkDays` accepts a start datetime (`dd/mm/yyyy HH:MM`) and a number of
working days that may be fractional and negative.

## Command line

```bash
python workday_calendar.py "24/5/2004 18:03" -6.7470217 \
  --holiday "27/5/2004" --recurring-holiday "17/5"
# -> 13/05/2004 10:02
```

Run `python workday_calendar.py --help` for all options (custom working hours
and repeatable holiday flags). Invalid input is reported with a clear message
instead of a stack trace.

## Date / time formats

| Input | Format |
| --- | --- |
| Start datetime | `dd/mm/yyyy HH:MM` |
| Unique holiday | `dd/mm/yyyy` |
| Recurring holiday | `dd/mm` |
| Working hours | `HH:MM` |

## Development

```bash
python -m pip install -r requirements-dev.txt

python -m pytest                      # run tests
python -m pytest --cov=.              # with coverage
flake8 .                              # lint
```

Tests also run in CI on every push and pull request (see
`.github/workflows/python-package.yml`). See `AGENTS.md` for contributor and
AI-agent guidance.
