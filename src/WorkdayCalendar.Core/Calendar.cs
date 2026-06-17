using System.Globalization;

namespace WorkdayCalendar.Core;

/// <summary>
/// Calculates a <see cref="DateTime"/> a number of <em>workdays</em> away from a
/// starting point. A workday excludes weekends, unique (one-off) holidays and
/// recurring (yearly) holidays. Time is only counted inside the configured
/// working window (<see cref="WorkdayStart"/>..<see cref="WorkdayEnd"/>).
/// </summary>
public class Calendar
{
    private const string DateFormat = "dd/MM/yyyy";
    private const string RecurringFormat = "dd/MM";

    private readonly List<string> _uniqueHolidays = new();
    private readonly List<string> _recurringHolidays = new();

    /// <summary>Start of the working window.</summary>
    public TimeOnly WorkdayStart { get; }

    /// <summary>End of the working window.</summary>
    public TimeOnly WorkdayEnd { get; }

    /// <summary>Registered unique holidays, formatted <c>dd/MM/yyyy</c>.</summary>
    public IReadOnlyList<string> UniqueHolidays => _uniqueHolidays;

    /// <summary>Registered recurring holidays, formatted <c>dd/MM</c>.</summary>
    public IReadOnlyList<string> RecurringHolidays => _recurringHolidays;

    /// <summary>Creates a calendar from explicit working hours.</summary>
    public Calendar(TimeOnly workdayStart, TimeOnly workdayEnd)
    {
        if (workdayStart >= workdayEnd)
        {
            throw new ArgumentException("workday start must be earlier than workday end.");
        }

        WorkdayStart = workdayStart;
        WorkdayEnd = workdayEnd;
    }

    /// <summary>Creates a calendar from <c>HH:mm</c> strings.</summary>
    public Calendar(string workdayStart, string workdayEnd)
        : this(
            InputFormats.ParseTime(workdayStart, "workday start"),
            InputFormats.ParseTime(workdayEnd, "workday end"))
    {
    }

    /// <summary>Registers a unique holiday given as <c>dd/MM/yyyy</c>.</summary>
    public void AddHoliday(string date)
    {
        DateOnly parsed = InputFormats.ParseDate(date, "holiday date");
        _uniqueHolidays.Add(parsed.ToString(DateFormat, CultureInfo.InvariantCulture));
    }

    /// <summary>Registers a recurring holiday given as <c>dd/MM</c>.</summary>
    public void AddRecurringHoliday(string date)
    {
        DateOnly parsed = InputFormats.ParseRecurring(date, "recurring holiday date");
        _recurringHolidays.Add(parsed.ToString(RecurringFormat, CultureInfo.InvariantCulture));
    }

    /// <summary>
    /// Returns the datetime <paramref name="workdays"/> working days from
    /// <paramref name="start"/> (parsed from <c>dd/MM/yyyy HH:mm</c>).
    /// </summary>
    public DateTime AddWorkDays(string start, double workdays)
        => AddWorkDays(InputFormats.ParseDateTime(start, "start datetime"), workdays);

    /// <summary>
    /// Returns the datetime <paramref name="workdays"/> working days from
    /// <paramref name="start"/>. <paramref name="workdays"/> may be fractional
    /// and negative, but not zero.
    /// </summary>
    public DateTime AddWorkDays(DateTime start, double workdays)
    {
        if (double.IsNaN(workdays) || double.IsInfinity(workdays))
        {
            throw new ArgumentException("workdays must be a finite number.", nameof(workdays));
        }

        if (workdays == 0)
        {
            throw new ArgumentException("workdays must not be 0.", nameof(workdays));
        }

        (int minutes, int days) = NumberToTime(workdays);
        return workdays > 0
            ? AddDays(start, minutes, days)
            : SubtractDays(start, minutes, days);
    }

    /// <summary>
    /// Advances <paramref name="date"/> until it lands on a real workday,
    /// handling adjacent weekends and holidays.
    /// </summary>
    public DateTime AdvanceToWorkday(DateTime date, int direction)
    {
        var checks = new int[3];
        while (checks[0] + checks[1] + checks[2] < 3)
        {
            (date, checks[2]) = SkipWeekend(date, direction);
            (date, checks[0]) = SkipUniqueHoliday(date, direction);
            (date, checks[1]) = SkipRecurringHoliday(date, direction);
        }

        return date;
    }

    private (int minutes, int days) NumberToTime(double number)
    {
        double integer = Math.Truncate(number);
        double fraction = number - integer;
        int workdayMinutes =
            (WorkdayEnd.Hour * 60 + WorkdayEnd.Minute)
            - (WorkdayStart.Hour * 60 + WorkdayStart.Minute);
        double minutes = workdayMinutes * Math.Abs(fraction);
        return ((int)Math.Floor(Math.Abs(minutes)), (int)integer);
    }

    private (DateTime, int) SkipRecurringHoliday(DateTime date, int direction)
    {
        DateTime result = date;
        int passed = 1;
        while (_recurringHolidays.Contains(result.ToString(RecurringFormat, CultureInfo.InvariantCulture)))
        {
            passed = 0;
            result = direction > 0 ? result.AddDays(1) : result.AddDays(-1);
        }

        return (result, passed);
    }

    private (DateTime, int) SkipUniqueHoliday(DateTime date, int direction)
    {
        DateTime result = date;
        int passed = 1;
        while (_uniqueHolidays.Contains(result.ToString(DateFormat, CultureInfo.InvariantCulture)))
        {
            passed = 0;
            result = direction > 0 ? result.AddDays(1) : result.AddDays(-1);
        }

        return (result, passed);
    }

    private static (DateTime, int) SkipWeekend(DateTime date, int direction)
    {
        DateTime result = date;
        int passed = 1;
        while (true)
        {
            if (direction > 0)
            {
                if (result.DayOfWeek == DayOfWeek.Saturday)
                {
                    passed = 0;
                    result = result.AddDays(2);
                }
                else if (result.DayOfWeek == DayOfWeek.Sunday)
                {
                    passed = 0;
                    result = result.AddDays(1);
                }
                else
                {
                    break;
                }
            }
            else
            {
                if (result.DayOfWeek == DayOfWeek.Saturday)
                {
                    passed = 0;
                    result = result.AddDays(-1);
                }
                else if (result.DayOfWeek == DayOfWeek.Sunday)
                {
                    passed = 0;
                    result = result.AddDays(-2);
                }
                else
                {
                    break;
                }
            }
        }

        return (result, passed);
    }

    private DateTime AddDays(DateTime start, int minutes, int days)
    {
        DateTime result = start;
        var time = new TimeOnly(result.Hour, result.Minute);

        // Normalise a start time that falls outside the working window.
        if (time < WorkdayStart)
        {
            result = WithTime(result, WorkdayStart);
        }
        else if (time > WorkdayEnd)
        {
            result = WithTime(result, WorkdayStart).AddDays(1);
        }

        // Apply the leftover minutes, rolling into the next workday on overflow.
        time = new TimeOnly(result.Hour, result.Minute);
        int minutesLeft =
            (WorkdayEnd.Hour * 60 + WorkdayEnd.Minute)
            - (time.Hour * 60 + time.Minute);
        if (minutesLeft < minutes)
        {
            result = WithTime(result, WorkdayStart)
                .AddDays(1)
                .AddMinutes(minutes - minutesLeft);
        }
        else
        {
            result = result.AddMinutes(minutes);
        }

        // Add the whole workdays, skipping non-working days.
        for (int i = 0; i < Math.Abs(days); i++)
        {
            result = AdvanceToWorkday(result, 1);
            result = result.AddDays(1);
        }

        return result;
    }

    private DateTime SubtractDays(DateTime start, int minutes, int days)
    {
        DateTime result = start;
        var time = new TimeOnly(result.Hour, result.Minute);

        // Normalise a start time that falls outside the working window.
        if (time < WorkdayStart)
        {
            result = WithTime(result, WorkdayEnd).AddDays(-1);
        }
        else if (time > WorkdayEnd)
        {
            result = WithTime(result, WorkdayEnd);
        }

        // Apply the leftover minutes, rolling into the previous workday on overflow.
        time = new TimeOnly(result.Hour, result.Minute);
        int minutesLeft =
            (time.Hour * 60 + time.Minute)
            - (WorkdayStart.Hour * 60 + WorkdayStart.Minute);
        if (minutesLeft < minutes)
        {
            result = WithTime(result, WorkdayEnd)
                .AddDays(-1)
                .AddMinutes(-(minutes - minutesLeft));
        }
        else
        {
            result = result.AddMinutes(-minutes);
        }

        // Subtract the whole workdays, skipping non-working days.
        for (int i = 0; i < Math.Abs(days); i++)
        {
            result = result.AddDays(-1);
            result = AdvanceToWorkday(result, -1);
        }

        return result;
    }

    private static DateTime WithTime(DateTime date, TimeOnly time)
        => new(date.Year, date.Month, date.Day, time.Hour, time.Minute, 0);
}
