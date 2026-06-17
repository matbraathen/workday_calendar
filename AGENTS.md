# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository.

## Project overview

A .NET / C# application that calculates where you land in time when moving a
number of **workdays** forward or backward from a starting point. A workday
excludes weekends, one-off ("unique") holidays and yearly ("recurring")
holidays. Time is only counted inside a configured working window.

The calculation engine lives in a UI-agnostic core library; a Blazor web app
provides the front end.

## Layout

| Path | Purpose |
| --- | --- |
| `src/WorkdayCalendar.Core/Calendar.cs` | The `Calendar` engine (public API). |
| `src/WorkdayCalendar.Core/InputFormats.cs` | Shared string parsing + validation. |
| `src/WorkdayCalendar.Web/` | Blazor interactive-server UI (`Components/Pages/Home.razor`). |
| `tests/WorkdayCalendar.Tests/` | xUnit test suite. |
| `.github/workflows/dotnet.yml` | CI: restore, build, test. |

## Target framework

All projects target **net8.0** (LTS). Keep it that way unless there is a clear
reason to change, and update CI (`dotnet.yml`) accordingly.

## Common commands

```bash
dotnet restore WorkdayCalendar.sln
dotnet build WorkdayCalendar.sln
dotnet test WorkdayCalendar.sln

# Run the web UI locally
dotnet run --project src/WorkdayCalendar.Web
```

## Date / time formats

- Start datetime: `d/M/yyyy H:mm`
- Unique holiday: `d/M/yyyy`
- Recurring holiday: `d/M`
- Working hours: `H:mm`

## Conventions

- Keep `WorkdayCalendar.Core` free of any UI / web dependencies so it stays
  reusable and unit-testable.
- Validate input and throw `ArgumentException` with a clear, format-aware
  message rather than leaking a raw `FormatException` or returning a sentinel.
- The reference cases in `CalendarTests.cs` (`AddWorkDays_MatchesReferenceCases`)
  encode the intended arithmetic. If you change the core algorithm, update those
  cases deliberately and explain why.

## Definition of done

Before finishing a change, make sure both of these are green:

1. `dotnet build WorkdayCalendar.sln`
2. `dotnet test WorkdayCalendar.sln`
