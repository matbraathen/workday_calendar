using WorkdayCalendar.Core;

namespace WorkdayCalendar.Tests;

public class CalendarTests
{
    private static Calendar NewCalendar() => new("08:00", "16:00");

    private static Calendar NewCalendarWithHolidays()
    {
        var calendar = NewCalendar();
        calendar.AddHoliday("27/5/2004");
        calendar.AddRecurringHoliday("17/5");
        return calendar;
    }

    // --- configuration -----------------------------------------------------

    [Fact]
    public void Constructor_SetsWorkingHours()
    {
        var calendar = NewCalendar();
        Assert.Equal(new TimeOnly(8, 0), calendar.WorkdayStart);
        Assert.Equal(new TimeOnly(16, 0), calendar.WorkdayEnd);
    }

    [Theory]
    [InlineData("27/02/2022")]
    [InlineData("14/7/2022")]
    public void AddHoliday_NormalisesAndStores(string holiday)
    {
        var calendar = NewCalendar();
        calendar.AddHoliday(holiday);
        Assert.Single(calendar.UniqueHolidays);
    }

    [Theory]
    [InlineData("21/11", "21/11")]
    [InlineData("3/1", "03/01")]
    public void AddRecurringHoliday_NormalisesAndStores(string input, string stored)
    {
        var calendar = NewCalendar();
        calendar.AddRecurringHoliday(input);
        Assert.Contains(stored, calendar.RecurringHolidays);
    }

    // --- core calculation --------------------------------------------------

    [Theory]
    [InlineData("24/5/2004 19:03", 44.723656, 2004, 7, 27, 13, 47)]
    [InlineData("24/5/2004 18:03", -6.7470217, 2004, 5, 13, 10, 2)]
    public void AddWorkDays_MatchesReferenceCases(
        string start, double workdays, int y, int mo, int d, int h, int mi)
    {
        var calendar = NewCalendarWithHolidays();
        Assert.Equal(new DateTime(y, mo, d, h, mi, 0), calendar.AddWorkDays(start, workdays));
    }

    [Theory]
    // 12 May 2004 is a Wednesday inside the working window.
    [InlineData("12/05/2004 08:00", 1.0, 2004, 5, 13, 8, 0)]
    [InlineData("12/05/2004 08:00", -1.0, 2004, 5, 11, 8, 0)]
    [InlineData("12/05/2004 08:00", 0.5, 2004, 5, 12, 12, 0)]
    public void AddWorkDays_SimpleCases(
        string start, double workdays, int y, int mo, int d, int h, int mi)
    {
        var calendar = NewCalendar();
        Assert.Equal(new DateTime(y, mo, d, h, mi, 0), calendar.AddWorkDays(start, workdays));
    }

    // --- workday / skip logic ---------------------------------------------

    [Fact]
    public void AdvanceToWorkday_SkipsRecurringHoliday()
    {
        var calendar = NewCalendarWithHolidays();
        var result = calendar.AdvanceToWorkday(new DateTime(2004, 5, 17, 8, 0, 0), 1);
        Assert.Equal(new DateTime(2004, 5, 18, 8, 0, 0), result);
    }

    [Fact]
    public void AdvanceToWorkday_SkipsUniqueHoliday()
    {
        var calendar = NewCalendarWithHolidays();
        var result = calendar.AdvanceToWorkday(new DateTime(2004, 5, 27, 8, 0, 0), 1);
        Assert.Equal(new DateTime(2004, 5, 28, 8, 0, 0), result);
    }

    [Fact]
    public void AdvanceToWorkday_SkipsWeekendForward()
    {
        var calendar = NewCalendar();
        var result = calendar.AdvanceToWorkday(new DateTime(2004, 5, 15, 8, 0, 0), 1);
        Assert.Equal(new DateTime(2004, 5, 17, 8, 0, 0), result);
    }

    [Fact]
    public void AdvanceToWorkday_SkipsWeekendBackward()
    {
        var calendar = NewCalendar();
        var result = calendar.AdvanceToWorkday(new DateTime(2004, 5, 15, 8, 0, 0), -1);
        Assert.Equal(new DateTime(2004, 5, 14, 8, 0, 0), result);
    }

    [Fact]
    public void AdvanceToWorkday_SkipsAdjacentWeekendAndHoliday()
    {
        var calendar = NewCalendar();
        calendar.AddRecurringHoliday("17/5");
        var result = calendar.AdvanceToWorkday(new DateTime(2004, 5, 15, 8, 0, 0), 1);
        Assert.Equal(new DateTime(2004, 5, 18, 8, 0, 0), result);
    }

    // --- validation --------------------------------------------------------

    [Fact]
    public void AddWorkDays_ZeroWorkdays_Throws()
    {
        var calendar = NewCalendar();
        Assert.Throws<ArgumentException>(() => calendar.AddWorkDays("12/05/2004 08:00", 0));
    }

    [Theory]
    [InlineData(double.NaN)]
    [InlineData(double.PositiveInfinity)]
    public void AddWorkDays_NonFiniteWorkdays_Throws(double workdays)
    {
        var calendar = NewCalendar();
        Assert.Throws<ArgumentException>(() => calendar.AddWorkDays("12/05/2004 08:00", workdays));
    }

    [Fact]
    public void AddWorkDays_InvalidStartDateTime_Throws()
    {
        var calendar = NewCalendar();
        Assert.Throws<ArgumentException>(() => calendar.AddWorkDays("not a date", 1));
    }

    [Fact]
    public void AddHoliday_Invalid_Throws()
    {
        var calendar = NewCalendar();
        Assert.Throws<ArgumentException>(() => calendar.AddHoliday("31/31/2004"));
    }

    [Fact]
    public void AddRecurringHoliday_Invalid_Throws()
    {
        var calendar = NewCalendar();
        Assert.Throws<ArgumentException>(() => calendar.AddRecurringHoliday("nope"));
    }

    [Theory]
    [InlineData("08:00", "08:00")]
    [InlineData("16:00", "08:00")]
    public void Constructor_StartNotBeforeEnd_Throws(string start, string end)
    {
        Assert.Throws<ArgumentException>(() => new Calendar(start, end));
    }

    [Fact]
    public void Constructor_InvalidHours_Throws()
    {
        Assert.Throws<ArgumentException>(() => new Calendar("8 oclock", "16:00"));
    }
}
