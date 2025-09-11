# quota

Display disk usage quotas and limits.

## Synopsis

```
quota [-h] [-g] [user_or_group...]
```

## Description

The `quota` command displays disk usage and limits for users and groups. It shows current usage against configured quotas and hard limits, along with grace periods if quotas are exceeded.

## Options

- `-h, --human-readable` - Print sizes in human readable format (e.g., 1K, 234M, 2.1G)
- `-g, --group` - Display group quotas rather than user quotas

## Arguments

- `user_or_group...` - Users or groups to display quotas for (default: current user)

## Examples

**Display current user's quota:**
```bash
quota
# Output:
# Disk quotas for users:
# Filesystem  blocks   quota   limit   grace   files   quota   limit   grace
# vfs         1024     10240   12288   -       25      100     120     -
```

**Human-readable format:**
```bash
quota -h
# Output:
# Disk quotas for users:
# Filesystem  blocks   quota   limit   grace   files   quota   limit   grace
# vfs         1.0K     10K     12K     -       25      100     120     -
```

**Display group quotas:**
```bash
quota -g developers
```

**Multiple users:**
```bash
quota user1 user2 user3
```

## Output Format

The output shows a table with these columns:

**Block Usage:**
- **Filesystem** - Name of the filesystem
- **blocks** - Current disk usage in KB (or human-readable)
- **quota** - Soft quota limit
- **limit** - Hard quota limit  
- **grace** - Grace period if quota exceeded (e.g., "7days")

**File Usage:**
- **files** - Number of files owned
- **quota** - Maximum files allowed (soft limit)
- **limit** - Maximum files allowed (hard limit)
- **grace** - Grace period if file quota exceeded

## Quota Types

**Soft Quota:** Warning threshold - can be exceeded temporarily
**Hard Quota:** Absolute limit - cannot be exceeded
**Grace Period:** Time allowed to stay above soft quota before it becomes enforced as hard quota

## Implementation Notes

- Integrates with security wrapper for quota enforcement
- Calculates actual usage by traversing user directories
- Uses filesystem storage statistics for quota information
- Handles both user and group quota scenarios
- Sets hard limits to 120% of soft quotas by default
- Grace periods default to 7 days when quotas exceeded

## Error Handling

- "quota: no user quotas for username" - No quota configured for user
- "quota: no group quotas for groupname" - No quota configured for group
- Silently handles users/groups that don't exist

## Security Integration

The command works with security-wrapped filesystems that provide:
- `get_storage_stats()` with quota information
- `max_total_size` and `max_files` limits
- Provider identification for filesystem naming

## Usage Calculation

User/group usage is calculated by:
1. Finding user's home directory or group directory
2. Recursively scanning all files in that tree
3. Summing file sizes and counts
4. Converting to appropriate units (KB blocks for disk usage)

## See Also

- [`df`](df.md) - Display filesystem disk space usage
- [`du`](du.md) - Display directory space usage
- [`whoami`](../system/whoami.md) - Display current user
- [Security features](../../README.md#security) - Filesystem security integration