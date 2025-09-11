# date

Display the current date and time.

## Usage

```bash
date [OPTIONS]
date +FORMAT
```

## Description

The `date` command displays the current date and time. When called without arguments, it displays the date in the default format. You can also specify a custom format string.

## Options

- No options: Display current date and time in default format
- `+FORMAT`: Display date using the specified format string

## Format Specifiers

- `%Y` - Year (4 digits)
- `%m` - Month (01-12)
- `%d` - Day of month (01-31)
- `%H` - Hour (00-23)
- `%M` - Minute (00-59)
- `%S` - Second (00-59)
- `%a` - Weekday abbreviated (Mon, Tue, etc.)
- `%A` - Weekday full (Monday, Tuesday, etc.)
- `%b` - Month abbreviated (Jan, Feb, etc.)
- `%B` - Month full (January, February, etc.)

## Examples

### Display current date and time
```bash
$ date
Thu Sep 11 13:45:00  2025
```

### Display date in YYYY-MM-DD format
```bash
$ date +%Y-%m-%d
2025-09-11
```

### Display time only
```bash
$ date +%H:%M:%S
13:45:00
```

### Custom format with text
```bash
$ date +"Today is %A, %B %d, %Y"
Today is Thursday, September 11, 2025
```

## Implementation Notes

The date command in the virtual shell provides basic date/time display functionality. It supports a subset of the standard Unix date command format specifiers.

## See Also

- [time](time.md) - Time command execution
- [uptime](uptime.md) - Show system uptime