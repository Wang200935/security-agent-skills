# Directory Rename — 2026-07-08 Cleanup Session

## Change
Directory renamed from `flipper-zero-backupup/` → `flipper-zero-backup/` to match frontmatter `name: flipper-zero-backup`.

## Reason
Skill-organizer audit flagged name mismatch: `dir='flipper-zero-backupup'` vs `fm='flipper-zero-backup'`. Fixed by renaming directory to match frontmatter (since `skill_view` and `skills_list` already used the frontmatter name).

## Lesson
When `skill_view(name="...")` returns a skill but the directory name differs from frontmatter `name:`, rename the **directory** to match frontmatter. The frontmatter name is the canonical identifier.