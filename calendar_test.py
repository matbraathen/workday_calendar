import datetime

import pytest

import workday_calendar


def dt(value):
    return datetime.datetime.strptime(value, "%d-%m-%Y %H:%M")


@pytest.fixture
def calendar():
    return workday_calendar.Calendar("08:00", "16:00")


@pytest.fixture
def calendar_with_holidays(calendar):
    calendar.addHoliday("27/5/2004")
    calendar.addRecurringHoliday("17/5")
    return calendar


# --- configuration ---------------------------------------------------------

def test_initial_workday_start(calendar):
    assert calendar.workday_start == datetime.time(8, 0)


def test_initial_workday_end(calendar):
    assert calendar.workday_end == datetime.time(16, 0)


@pytest.mark.parametrize("start", ["08:00", "07:00", "09:30"])
def test_change_workday_start(calendar, start):
    calendar.setStart(start)
    assert calendar.getStart() == datetime.datetime.strptime(start, "%H:%M").time()


@pytest.mark.parametrize("end", ["16:00", "15:00", "17:45"])
def test_change_workday_end(calendar, end):
    calendar.setEnd(end)
    assert calendar.getEnd() == datetime.datetime.strptime(end, "%H:%M").time()


@pytest.mark.parametrize("holiday", ["27/02/2022", "14/07/2022"])
def test_addHoliday(calendar, holiday):
    calendar.addHoliday(holiday)
    assert holiday in calendar.unique_holidays


@pytest.mark.parametrize("recurring_holiday", ["21/11", "22/12"])
def test_addRecurringHoliday(calendar, recurring_holiday):
    calendar.addRecurringHoliday(recurring_holiday)
    assert recurring_holiday in calendar.recurring_holidays


# --- core calculation ------------------------------------------------------

@pytest.mark.parametrize("start_time, workdays, expected", [
    ("24/5/2004 19:03", 44.723656, "27-07-2004 13:47"),
    ("24/5/2004 18:03", -6.7470217, "13-05-2004 10:02"),
])
def test_add_workdays_reference_cases(calendar_with_holidays, start_time, workdays, expected):
    assert calendar_with_holidays.addWorkDays(start_time, workdays) == dt(expected)


@pytest.mark.parametrize("start_time, workdays, expected", [
    # 12 May 2004 is a Wednesday, inside the working window.
    ("12/05/2004 08:00", 1, "13-05-2004 08:00"),
    ("12/05/2004 08:00", -1, "11-05-2004 08:00"),
    ("12/05/2004 08:00", 0.5, "12-05-2004 12:00"),
])
def test_add_workdays_simple_cases(calendar, start_time, workdays, expected):
    assert calendar.addWorkDays(start_time, workdays) == dt(expected)


# --- workday / skip logic --------------------------------------------------

def test_isWorkday_skips_recurring_holiday(calendar_with_holidays):
    # 17 May 2004 (Monday) is the recurring 17/5 holiday.
    result = calendar_with_holidays.isWorkday(datetime.datetime(2004, 5, 17, 8, 0), 1)
    assert result == datetime.datetime(2004, 5, 18, 8, 0)


def test_isWorkday_skips_unique_holiday(calendar_with_holidays):
    # 27 May 2004 (Thursday) is the unique holiday.
    result = calendar_with_holidays.isWorkday(datetime.datetime(2004, 5, 27, 8, 0), 1)
    assert result == datetime.datetime(2004, 5, 28, 8, 0)


def test_isWorkday_skips_weekend_forward(calendar):
    # 15 May 2004 is a Saturday.
    result = calendar.isWorkday(datetime.datetime(2004, 5, 15, 8, 0), 1)
    assert result == datetime.datetime(2004, 5, 17, 8, 0)


def test_isWorkday_skips_weekend_backward(calendar):
    # 15 May 2004 is a Saturday; moving back lands on Friday.
    result = calendar.isWorkday(datetime.datetime(2004, 5, 15, 8, 0), -1)
    assert result == datetime.datetime(2004, 5, 14, 8, 0)


def test_isWorkday_skips_adjacent_weekend_and_holiday(calendar):
    # Sat 15 + Sun 16 May, then Mon 17 May is a recurring holiday.
    calendar.addRecurringHoliday("17/5")
    result = calendar.isWorkday(datetime.datetime(2004, 5, 15, 8, 0), 1)
    assert result == datetime.datetime(2004, 5, 18, 8, 0)


# --- validation ------------------------------------------------------------

def test_zero_workdays_raises(calendar):
    with pytest.raises(ValueError):
        calendar.addWorkDays("12/05/2004 08:00", 0)


@pytest.mark.parametrize("bad_workdays", [True, "3", None])
def test_non_numeric_workdays_raises(calendar, bad_workdays):
    with pytest.raises(TypeError):
        calendar.addWorkDays("12/05/2004 08:00", bad_workdays)


def test_invalid_start_datetime_raises(calendar):
    with pytest.raises(ValueError):
        calendar.addWorkDays("not a date", 1)


def test_invalid_holiday_raises(calendar):
    with pytest.raises(ValueError):
        calendar.addHoliday("31/31/2004")


def test_invalid_recurring_holiday_raises(calendar):
    with pytest.raises(ValueError):
        calendar.addRecurringHoliday("nope")


@pytest.mark.parametrize("start, end", [
    ("08:00", "08:00"),
    ("16:00", "08:00"),
])
def test_start_not_before_end_raises(start, end):
    with pytest.raises(ValueError):
        workday_calendar.Calendar(start, end)


def test_invalid_hours_raise():
    with pytest.raises(ValueError):
        workday_calendar.Calendar("8 oclock", "16:00")


# --- CLI -------------------------------------------------------------------

def test_cli_main_returns_and_prints(capsys):
    result = workday_calendar.main(["12/05/2004 08:00", "1"])
    assert result == datetime.datetime(2004, 5, 13, 8, 0)
    assert capsys.readouterr().out.strip() == "13/05/2004 08:00"


def test_cli_main_with_holidays(capsys):
    result = workday_calendar.main([
        "24/5/2004 18:03", "-6.7470217",
        "--holiday", "27/5/2004", "--recurring-holiday", "17/5",
    ])
    assert result == datetime.datetime(2004, 5, 13, 10, 2)


def test_cli_invalid_input_exits(capsys):
    with pytest.raises(SystemExit):
        workday_calendar.main(["bad", "1"])
