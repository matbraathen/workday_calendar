# Workday Calendar

A small .NET / C# application that calculates where you end up in time when
moving back or forth a number of **working days** from a given point in time. A
*working day* excludes weekends, one-off ("unique") holidays and yearly
("recurring") holidays, and time is only counted inside a configurable working
window.

It ships as a reusable core library plus a Blazor web UI.

## Projects

| Project | Description |
| --- | --- |
| `src/WorkdayCalendar.Core` | The `Calendar` engine and input parsing (no UI). |
| `src/WorkdayCalendar.Web` | Blazor (interactive server) web UI. |
| `tests/WorkdayCalendar.Tests` | xUnit test suite. |

## Requirements

- [.NET SDK 8.0+](https://dotnet.microsoft.com/download)

## Run the web app

```bash
dotnet run --project src/WorkdayCalendar.Web
```

Then open the printed `http://localhost:<port>` URL. Enter the working hours,
start date/time, number of workdays (may be fractional and negative) and any
holidays, then press **Calculate**. Invalid input is reported inline instead of
throwing.

## Use the library

```csharp
using WorkdayCalendar.Core;

var calendar = new Calendar("08:00", "16:00");
calendar.AddHoliday("27/5/2004");        // unique holiday, dd/MM/yyyy
calendar.AddRecurringHoliday("17/5");    // recurring holiday, dd/MM

DateTime result = calendar.AddWorkDays("24/5/2004 18:03", -6.7470217);
// 2004-05-13 10:02
```

## Date / time formats

| Input | Format |
| --- | --- |
| Start datetime | `d/M/yyyy H:mm` |
| Unique holiday | `d/M/yyyy` |
| Recurring holiday | `d/M` |
| Working hours | `H:mm` |

## Build & test

```bash
dotnet build WorkdayCalendar.sln
dotnet test WorkdayCalendar.sln
```

Tests also run in CI on every push and pull request (see
`.github/workflows/dotnet.yml`). See `AGENTS.md` for contributor and AI-agent
guidance.
