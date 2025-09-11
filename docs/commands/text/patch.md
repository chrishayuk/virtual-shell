# patch

Apply diff patches to files.

## Synopsis

```
patch [OPTIONS] [ORIGINAL] < PATCHFILE
patch [OPTIONS] -i PATCHFILE [ORIGINAL]
```

## Description

The `patch` command applies changes from a diff file (patch) to the original file(s). It can handle unified diff, context diff, and normal diff formats.

## Options

- `-i FILE` - Read patch from FILE instead of stdin
- `-p NUM` - Strip NUM leading path components (default: 0)
- `-R, --reverse` - Reverse the patch (undo changes)
- `-b` - Make backup files (.orig)
- `-o FILE` - Output to FILE instead of modifying in place
- `--dry-run` - Show what would be changed without modifying files

## Arguments

- `ORIGINAL` - File to patch (optional if patch contains filenames)
- `PATCHFILE` - Diff file containing changes

## Examples

**Apply patch from stdin:**
```bash
patch < changes.patch                        # Apply patch to files mentioned in patch
patch file.txt < changes.patch               # Apply patch to specific file
```

**Apply patch from file:**
```bash
patch -i changes.patch                       # Apply patch from file
patch -i changes.patch file.txt              # Apply to specific file
```

**Reverse a patch:**
```bash
patch -R < changes.patch                     # Undo previously applied patch
patch -R -i changes.patch file.txt           # Reverse specific patch
```

**Create backup and test:**
```bash
patch -b < changes.patch                     # Create .orig backup files
patch --dry-run < changes.patch              # Test without modifying
```

**Handle path differences:**
```bash
patch -p1 < kernel.patch                     # Strip 1 path component
patch -p0 < local.patch                      # Use full paths (default)
```

**Output to different file:**
```bash
patch -o result.txt file.txt < changes.patch # Save result to new file
```

## Path Stripping (`-p` Option)

When patches contain paths that don't match your directory structure:

**Example patch header:**
```diff
--- a/src/main.c
+++ b/src/main.c
```

**Path stripping options:**
- `-p0`: Use `a/src/main.c` (no stripping)
- `-p1`: Use `src/main.c` (strip `a/`)
- `-p2`: Use `main.c` (strip `a/src/`)

## Supported Patch Formats

### Unified Diff
```diff
--- original.txt
+++ modified.txt
@@ -1,3 +1,3 @@
 line1
-old text
+new text
 line3
```

### Context Diff  
```diff
*** original.txt
--- modified.txt
***************
*** 1,3 ****
  line1
! old text
  line3
--- 1,3 ----
  line1
! new text
  line3
```

### Normal Diff
```diff
2c2
< old text
---
> new text
```

## Workflow Examples

**Create and apply patch:**
```bash
# Create patch
diff -u original.txt modified.txt > changes.patch

# Apply patch
patch < changes.patch

# Later, reverse if needed
patch -R < changes.patch
```

**Safe patching with backup:**
```bash
# Test first
patch --dry-run < risky.patch

# Apply with backup
patch -b < risky.patch

# If problems occur, restore from .orig files
```

**Patch from version control:**
```bash
# Git-style patch (often needs -p1)
patch -p1 < feature.patch

# Local diff (usually -p0)  
patch -p0 < local_changes.patch
```

## Error Handling

- "patch: no patch input" - No stdin and no `-i` file specified
- "patch: filename: No such file or directory" - Target file or patch file missing  
- "patch: no valid patches found" - Patch format not recognized
- "patch: failed to apply patch to filename" - Patch doesn't match file content

## Implementation Notes

- Supports unified, context, and normal diff formats
- Handles new file creation (from `/dev/null`)
- Processes multiple patches in sequence
- Path stripping helps with directory structure differences
- Dry run mode allows safe testing

## Special Cases

**New file creation:**
Patches can create new files when old file is `/dev/null`:
```diff
--- /dev/null
+++ newfile.txt
@@ -0,0 +1,3 @@
+line1
+line2  
+line3
```

**File deletion:**
Patches can remove files when new file is `/dev/null`:
```diff
--- oldfile.txt
+++ /dev/null
@@ -1,3 +0,0 @@
-line1
-line2
-line3
```

## Use Cases

**Software updates:**
```bash
patch -p1 < security-fix.patch              # Apply security patches
```

**Configuration management:**
```bash
patch -b config.conf < config.patch         # Update config with backup
```

**Code review:**
```bash
patch --dry-run < proposed-changes.patch    # Review before applying
```

## See Also

- [`diff`](diff.md) - Compare files and create patches
- [`cp`](../filesystem/cp.md) - Copy files (for manual backups)
- [`mv`](../filesystem/mv.md) - Rename files
- [Version control](../../README.md#version-control) - Managing code changes