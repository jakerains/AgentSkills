# CLAUDE.md

This file provides guidance to AI coding agents when working with code in this repository.

## Repository Purpose

This is a personal agent skills library compatible with multiple AI coding agents (Claude Code, Cursor, Codex, OpenCode, and more via [skills.sh](https://skills.sh)). Skills are stored in `skills/` and can be installed via `npx skills add jakerains/AgentSkills`.

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
# Install via npx (recommended — works for all supported agents)
npx skills add jakerains/AgentSkills --skill skill-name

# Or manually copy to Claude Code
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

---

# Skill Creation Guide

## What Are Skills?

Skills are modular packages that provide AI coding agents with specialized knowledge, workflows, and tools. A `.skill` file is a zip archive containing:

- `SKILL.md` (required) - Instructions with YAML frontmatter
- `scripts/` (optional) - Executable Python/Bash code
- `references/` (optional) - Documentation loaded into context as needed
- `assets/` (optional) - Templates, images, fonts used in output

## SKILL.md Structure

```markdown
---
name: skill-name
description: What this skill does and WHEN to use it. Include trigger scenarios, file types, or tasks.
---

# Skill Title

## Overview
1-2 sentences on what this skill enables.

## [Main Sections]
Instructions, workflows, examples, and references to bundled resources.
```

### Frontmatter Rules

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Kebab-case, lowercase, max 64 chars |
| `description` | Yes | Max 1024 chars, no `<>`. Include WHEN to trigger. |

**Critical:** The `description` is the ONLY thing the agent sees before loading the skill. Put all trigger conditions here, not in the body.

### Body Guidelines

- Keep under 500 lines (split into reference files if longer)
- Use imperative form ("Run the script" not "You should run")
- Prefer examples over explanations
- Reference bundled resources with relative paths

## Resource Directories

### scripts/
Executable code for deterministic, repeatable operations.

**When to use:**
- Same code would be rewritten repeatedly
- Deterministic reliability needed
- Complex operations that benefit from tested code

### references/
Documentation loaded into context as needed.

**When to use:**
- Detailed info only needed for specific tasks
- Large content that would bloat SKILL.md
- Domain knowledge, schemas, API docs

**Best practice:** For files >10k words, include grep patterns in SKILL.md

### assets/
Files used in output, NOT loaded into context.

**When to use:**
- Templates to copy/modify
- Images, fonts, icons
- Boilerplate code directories

## Progressive Disclosure Pattern

Keep SKILL.md lean by splitting content:

```
skill-name/
├── SKILL.md           # Core workflow, <500 lines
└── references/
    ├── topic-a.md     # Loaded only when needed
    ├── topic-b.md
    └── topic-c.md
```

Reference in SKILL.md:
```markdown
**For Topic A**: See references/topic-a.md
```

## Packaging into .skill File

```bash
cd skills/skill-name
zip -r ../../skill-name.skill .
```

The zip should contain contents at root level (SKILL.md at top, not nested).

## Validation Checklist

Before packaging:
- [ ] SKILL.md has valid YAML frontmatter
- [ ] `name` is kebab-case, ≤64 chars
- [ ] `description` is ≤1024 chars, no `<>`
- [ ] Description includes WHEN to trigger the skill
- [ ] Body is <500 lines
- [ ] All referenced files exist
- [ ] Scripts are executable and tested
- [ ] No README.md, CHANGELOG.md (not needed in skills)

## Anti-Patterns

**❌ Verbose descriptions:**
```yaml
description: This skill helps you work with documents. It can do many things...
```

**✓ Trigger-focused descriptions:**
```yaml
description: Create and edit Word documents (.docx). Use for document creation, tracked changes, comments, or text extraction from .docx files.
```

**❌ "When to use" in body** - Body only loads AFTER triggering

**✓ Triggers in frontmatter description**

## Conciseness Principle

Only include:
- Project-specific procedures
- Non-obvious domain knowledge
- Reusable scripts/assets
- Critical business rules

Omit:
- General programming knowledge
- Standard library usage
- Obvious tool commands
