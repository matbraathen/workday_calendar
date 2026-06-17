using System.Globalization;

namespace WorkdayCalendar.Core;

/// <summary>
/// Parsing helpers shared by <see cref="Calendar"/> and the UI. Each helper
/// raises an <see cref="ArgumentException"/> with a clear, format-aware message
/// rather than leaking a raw <see cref="FormatException"/>.
/// </summary>
public static class InputFormats
{
    /// <summary>Format for a start datetime, e.g. <c>24/5/2004 19:03</c>.</summary>
    public const string DateTimeFormat = "d/M/yyyy H:mm";

    /// <summary>Format for a unique holiday, e.g. <c>27/5/2004</c>.</summary>
    public const string DateFormat = "d/M/yyyy";

    /// <summary>Format for a recurring holiday, e.g. <c>17/5</c>.</summary>
    public const string RecurringFormat = "d/M";

    /// <summary>Format for working hours, e.g. <c>08:00</c>.</summary>
    public const string TimeFormat = "H:mm";

    public static DateTime ParseDateTime(string value, string description)
    {
        if (DateTime.TryParseExact(
                value, DateTimeFormat, CultureInfo.InvariantCulture,
                DateTimeStyles.None, out DateTime result))
        {
            return result;
        }

        throw Invalid(value, description, DateTimeFormat);
    }

    public static DateOnly ParseDate(string value, string description)
    {
        if (DateTime.TryParseExact(
                value, DateFormat, CultureInfo.InvariantCulture,
                DateTimeStyles.None, out DateTime result))
        {
            return DateOnly.FromDateTime(result);
        }

        throw Invalid(value, description, DateFormat);
    }

    public static DateOnly ParseRecurring(string value, string description)
    {
        if (DateTime.TryParseExact(
                value, RecurringFormat, CultureInfo.InvariantCulture,
                DateTimeStyles.None, out DateTime result))
        {
            return DateOnly.FromDateTime(result);
        }

        throw Invalid(value, description, RecurringFormat);
    }

    public static TimeOnly ParseTime(string value, string description)
    {
        if (TimeOnly.TryParseExact(
                value, TimeFormat, CultureInfo.InvariantCulture,
                DateTimeStyles.None, out TimeOnly result))
        {
            return result;
        }

        throw Invalid(value, description, TimeFormat);
    }

    private static ArgumentException Invalid(string? value, string description, string format)
        => new($"Invalid {description}: '{value}'. Expected format '{format}'.");
}
