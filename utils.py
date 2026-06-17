"""Helper functions backing :class:`workday_calendar.Calendar`.

These functions operate on a ``calendar`` instance (the :class:`Calendar`
that owns the configured work hours and holidays). They are kept as module
level helpers so the public :class:`Calendar` API stays small and focused.
"""

import math
import datetime


def numberToTime(calendar, number):
    """Split a (possibly fractional) number of workdays into days and minutes.

    The integer part is a count of whole workdays. The fractional part is
    converted to a number of minutes relative to the length of a single
    workday. Minutes are floored to match the reference results.

    Returns a ``(minutes, days)`` tuple of non-negative integers.
    """
    decimal, integer = math.modf(number)
    workday_minutes = (
        (calendar.workday_end.hour * 60 + calendar.workday_end.minute)
        - (calendar.workday_start.hour * 60 + calendar.workday_start.minute)
    )
    returned_minutes = workday_minutes * abs(decimal)
    return math.floor(abs(returned_minutes)), int(integer)


def isRecurringHoliday(calendar, date, operator):
    """Skip past any recurring holiday on ``date``.

    Moves ``date`` forward (``operator > 0``) or backward until it no longer
    lands on a recurring holiday. Returns ``(new_date, passed_check)`` where
    ``passed_check`` is ``1`` when no move was needed.
    """
    new_date = date
    holiday = True
    passed_check = 1
    while holiday:
        date_string = new_date.strftime("%d/%m")
        if date_string not in calendar.recurring_holidays:
            holiday = False
        else:
            passed_check = 0
            if operator > 0:
                new_date += datetime.timedelta(days=1)
            else:
                new_date -= datetime.timedelta(days=1)
    return new_date, passed_check


def isUniqueHoliday(calendar, date, operator):
    """Skip past any unique (single date) holiday on ``date``.

    Behaves like :func:`isRecurringHoliday` but matches against the calendar's
    one-off holidays.
    """
    new_date = date
    holiday = True
    passed_check = 1
    while holiday:
        date_string = new_date.strftime("%d/%m/%Y")
        if date_string not in calendar.unique_holidays:
            holiday = False
        else:
            passed_check = 0
            if operator > 0:
                new_date += datetime.timedelta(days=1)
            else:
                new_date -= datetime.timedelta(days=1)
    return new_date, passed_check


def isWeekend(calendar, date, operator):
    """Skip past weekend days starting at ``date``.

    Moves ``date`` off Saturday/Sunday in the direction given by ``operator``.
    Returns ``(new_date, passed_check)`` where ``passed_check`` is ``1`` when
    ``date`` already fell on a weekday.
    """
    new_date = date
    weekend = True
    passed_check = 1
    while weekend:
        if operator > 0:
            if new_date.weekday() == 5:
                passed_check = 0
                new_date += datetime.timedelta(days=2)
            elif new_date.weekday() == 6:
                passed_check = 0
                new_date += datetime.timedelta(days=1)
            else:
                weekend = False
        else:
            if new_date.weekday() == 5:
                passed_check = 0
                new_date -= datetime.timedelta(days=1)
            elif new_date.weekday() == 6:
                passed_check = 0
                new_date -= datetime.timedelta(days=2)
            else:
                weekend = False
    return new_date, passed_check


def addDays(calendar, datetime_start, minutes, days):
    """Add ``days`` workdays and ``minutes`` to ``datetime_start``.

    The start time is first normalised into the working window, then the
    minutes are applied (rolling over to the next workday if they overflow),
    and finally whole workdays are added one at a time, skipping weekends and
    holidays.
    """
    returned_date = datetime_start
    returned_date_time = datetime.time(returned_date.hour, returned_date.minute)
    # Normalise a start time that falls outside the working window.
    if returned_date_time < calendar.workday_start:
        returned_date = returned_date.replace(
            hour=calendar.workday_start.hour, minute=calendar.workday_start.minute
        )
    elif returned_date_time > calendar.workday_end:
        returned_date = returned_date.replace(
            hour=calendar.workday_start.hour, minute=calendar.workday_start.minute
        )
        returned_date += datetime.timedelta(days=1)

    # Apply the leftover minutes, rolling into the next workday on overflow.
    returned_date_time = datetime.time(returned_date.hour, returned_date.minute)
    minutes_left = (
        (calendar.workday_end.hour * 60 + calendar.workday_end.minute)
        - (returned_date_time.hour * 60 + returned_date_time.minute)
    )
    if minutes_left < minutes:
        returned_date = returned_date.replace(
            hour=calendar.workday_start.hour, minute=calendar.workday_start.minute
        )
        returned_date += datetime.timedelta(days=1)
        returned_date += datetime.timedelta(minutes=(minutes - minutes_left))
    else:
        returned_date += datetime.timedelta(minutes=minutes)

    # Add the whole workdays, skipping non-working days.
    for _ in range(abs(days)):
        returned_date = calendar.isWorkday(returned_date, 1)
        returned_date += datetime.timedelta(days=1)
    return returned_date


def subtractDays(calendar, datetime_start, minutes, days):
    """Subtract ``days`` workdays and ``minutes`` from ``datetime_start``.

    The mirror image of :func:`addDays`, moving backwards through time.
    """
    returned_date = datetime_start
    returned_date_time = datetime.time(returned_date.hour, returned_date.minute)
    # Normalise a start time that falls outside the working window.
    if returned_date_time < calendar.workday_start:
        returned_date = returned_date.replace(
            hour=calendar.workday_end.hour, minute=calendar.workday_end.minute
        )
        returned_date -= datetime.timedelta(days=1)
    elif returned_date_time > calendar.workday_end:
        returned_date = returned_date.replace(
            hour=calendar.workday_end.hour, minute=calendar.workday_end.minute
        )

    # Apply the leftover minutes, rolling into the previous workday on overflow.
    returned_date_time = datetime.time(returned_date.hour, returned_date.minute)
    minutes_left = (
        (returned_date_time.hour * 60 + returned_date_time.minute)
        - (calendar.workday_start.hour * 60 + calendar.workday_start.minute)
    )
    if minutes_left < minutes:
        returned_date = returned_date.replace(
            hour=calendar.workday_end.hour, minute=calendar.workday_end.minute
        )
        returned_date -= datetime.timedelta(days=1)
        returned_date -= datetime.timedelta(minutes=(minutes - minutes_left))
    else:
        returned_date -= datetime.timedelta(minutes=minutes)

    # Subtract the whole workdays, skipping non-working days.
    for _ in range(abs(days)):
        returned_date -= datetime.timedelta(days=1)
        returned_date = calendar.isWorkday(returned_date, -1)
    return returned_date
