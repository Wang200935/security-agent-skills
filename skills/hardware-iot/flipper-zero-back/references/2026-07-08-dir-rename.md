# Directory Rename — 2026-07-08 Cleanup Session

## Change
Directory renamed from `flipper-zero-backup/` → `flipper-zero-back/` to match frontmatter `name: flipper-zero-back`.

## Reason
Skill-organizer audit flagged name mismatch: `dir='flipper-zero-backup'` vs `fm='flipper-zero-back'`. Fixed by renaming directory to match frontmatter (since `skill_view` and `skills_list` already used the frontmatter name).

## Lesson
When `skill_view(name="...")` returns a skill but the directory name differs from frontmatter `name:`, rename the **directory** to match frontmatter. The frontmatter name is the canonical identifier.