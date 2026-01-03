# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a personal Claude Code skills library. Skills are stored in `skills/` and can be installed to `~/.claude/skills/` for use across projects.

## Repository Structure

```
skills/
├── skill-name/
│   ├── SKILL.md           # Required - main skill definition with frontmatter
│   ├── references/        # Optional - detailed documentation
│   └── scripts/           # Optional - utility scripts
```

## SKILL.md Requirements

Every skill must have a `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name
description: Clear description with trigger keywords for activation
---
```

- `name`: Lowercase letters, numbers, hyphens only (max 64 chars)
- `description`: Include keywords users would naturally say (max 1024 chars)

## Processing Dropped .skill Files

When a user drops a `.skill` file (ZIP archive) into the repository root and asks to add it:

1. **Extract to skills directory:**
   ```bash
   mkdir -p skills/skill-name
   unzip dropped-file.skill -d skills/skill-name
   ```

2. **Fix nested directories** (common issue - ZIPs often contain a folder inside):
   ```bash
   # If extraction created skills/skill-name/skill-name/, move contents up
   mv skills/skill-name/skill-name/* skills/skill-name/
   rmdir skills/skill-name/skill-name
   ```

3. **Verify SKILL.md has frontmatter** - if missing, add:
   ```yaml
   ---
   name: skill-name
   description: [Extract from content or ask user]
   ---
   ```

4. **Delete the original .skill file** from root after extraction

5. **Update README.md** - add the new skill to the Skills Catalog table

## Installation Commands

```bash
# Copy skill to Claude
cp -r skills/skill-name ~/.claude/skills/

# Or symlink for auto-updates
ln -s $(pwd)/skills/skill-name ~/.claude/skills/skill-name
```

## Adding New Skills Manually

```bash
mkdir -p skills/new-skill
# Create SKILL.md with frontmatter
# Add optional references/ and scripts/ directories
```
