"""A small calculator for moving a point in time by a number of *workdays*.

A workday is any day that is not a weekend, a unique (one-off) holiday or a
recurring (yearly) holiday. Time is only ever counted inside the configured
working window (``workday_start``..``workday_end``).
"""

import argparse
import datetime

import utils

DATETIME_FORMAT = "%d/%m/%Y %H:%M"
DATE_FORMAT = "%d/%m/%Y"
RECURRING_FORMAT = "%d/%m"
TIME_FORMAT = "%H:%M"


def _parse(value, fmt, description):
    """Parse ``value`` with ``fmt`` raising a friendly ``ValueError``."""
    try:
        return datetime.datetime.strptime(value, fmt)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Invalid {description}: {value!r}. Expected format '{fmt}'."
        ) from exc


class Calendar:
    """Computes workday offsets relative to a configured working window."""

    def __init__(self, workday_start, workday_end):
        self.workday_start = _parse(workday_start, TIME_FORMAT, "workday start").time()
        self.workday_end = _parse(workday_end, TIME_FORMAT, "workday end").time()
        if self.workday_start >= self.workday_end:
            raise ValueError("workday_start must be earlier than workday_end.")
        self.recurring_holidays = []
        self.unique_holidays = []

    def addWorkDays(self, datetime_start, workdays):
        """Return the datetime ``workdays`` working days from ``datetime_start``.

        ``workdays`` may be fractional and negative. A value of ``0`` is
        rejected because it has no meaningful workday offset.
        """
        if not isinstance(workdays, (int, float)) or isinstance(workdays, bool):
            raise TypeError("workdays must be a number.")
        if workdays == 0:
            raise ValueError("workdays must not be 0.")

        datetime_start = _parse(datetime_start, DATETIME_FORMAT, "start datetime")
        minutes, days = utils.numberToTime(self, workdays)
        if workdays > 0:
            return utils.addDays(self, datetime_start, minutes, days)
        return utils.subtractDays(self, datetime_start, minutes, days)

    def isWorkday(self, date, operator):
        """Advance ``date`` until it lands on a real workday.

        Repeatedly applies the weekend / unique-holiday / recurring-holiday
        checks (in the direction given by ``operator``) until all three pass,
        which also handles adjacent weekends and holidays.
        """
        checks = [0, 0, 0]
        while sum(checks) < 3:
            date, checks[2] = utils.isWeekend(self, date, operator)
            date, checks[0] = utils.isUniqueHoliday(self, date, operator)
            date, checks[1] = utils.isRecurringHoliday(self, date, operator)
        return date

    def addHoliday(self, date):
        """Register a unique holiday given as ``dd/mm/yyyy``."""
        parsed = _parse(date, DATE_FORMAT, "holiday date").date()
        self.unique_holidays.append(parsed.strftime(DATE_FORMAT))

    def addRecurringHoliday(self, date):
        """Register a yearly recurring holiday given as ``dd/mm``."""
        parsed = _parse(date, RECURRING_FORMAT, "recurring holiday date").date()
        self.recurring_holidays.append(parsed.strftime(RECURRING_FORMAT))

    def setStart(self, start):
        self.workday_start = _parse(start, TIME_FORMAT, "workday start").time()

    def getStart(self):
        return self.workday_start

    def setEnd(self, end):
        self.workday_end = _parse(end, TIME_FORMAT, "workday end").time()

    def getEnd(self):
        return self.workday_end


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Calculate a datetime a number of workdays away from a start."
    )
    parser.add_argument(
        "start", help="Start datetime, format 'dd/mm/yyyy HH:MM' (quote it)."
    )
    parser.add_argument(
        "workdays", type=float, help="Workdays to add (may be fractional/negative)."
    )
    parser.add_argument(
        "--start-hour", default="08:00", help="Workday start, format 'HH:MM'."
    )
    parser.add_argument(
        "--end-hour", default="16:00", help="Workday end, format 'HH:MM'."
    )
    parser.add_argument(
        "--holiday",
        action="append",
        default=[],
        metavar="dd/mm/yyyy",
        help="A unique holiday (repeatable).",
    )
    parser.add_argument(
        "--recurring-holiday",
        action="append",
        default=[],
        metavar="dd/mm",
        help="A yearly recurring holiday (repeatable).",
    )
    return parser


def main(argv=None):
    """CLI entry point. Returns the resulting datetime string."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        calendar = Calendar(args.start_hour, args.end_hour)
        for holiday in args.holiday:
            calendar.addHoliday(holiday)
        for recurring in args.recurring_holiday:
            calendar.addRecurringHoliday(recurring)
        result = calendar.addWorkDays(args.start, args.workdays)
    except (ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(result.strftime(DATETIME_FORMAT))
    return result


if __name__ == "__main__":
    main()
