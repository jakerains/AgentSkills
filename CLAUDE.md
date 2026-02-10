# CLAUDE.md

This file provides guidance to AI coding agents when working with code in this repository.

## Repository Purpose

This is a personal agent skills library compatible with 18+ AI coding agents including AMP, Antigravity, Claude Code, ClawdBot, Cline, Codex, Cursor, Droid, Gemini, GitHub Copilot, Goose, Kilo, Kiro CLI, OpenCode, Roo, Trae, VSCode, and Windsurf (via [skills.sh](https://skills.sh)). Skills are stored in `skills/` and can be installed via `npx skills add jakerains/AgentSkills`.

## Repository Structure

```
skills/
├── skill-name/
│   ├── SKILL.md           # Required - main skill definition with frontmatter
│   ├── references/        # Optional - detailed documentation loaded on-demand
│   ├── scripts/           # Optional - executable code for deterministic tasks
│   └── assets/            # Optional - templates, images, fonts used in output
```

## Skills CLI

```bash
npx skills init <name>        # Scaffold a new skill (creates SKILL.md template)
npx skills add <repo>         # Install skills from a repo
npx skills add <repo> -g      # Install globally
npx skills add <repo> -s <n>  # Install specific skill by name
npx skills find [query]       # Search for skills interactively
npx skills check              # Check for skill updates
npx skills update             # Update all installed skills
```

---

# Skill Creation Guide

This repo's primary purpose is creating skills. When asked to create a new skill, follow this guide. For additional patterns and advanced techniques, the `/skill-creator` skill is also available — but always use `npx skills init` as the starting point.

## Step 1: Understand the Skill

Before building, clarify with the user:
- What does the skill do? Get concrete usage examples.
- What would a user say to trigger it?
- What resources (docs, scripts, assets) would help?

Skip this if the user has already provided clear requirements.

## Step 2: Initialize with npx

Always start new skills with the CLI:

```bash
cd skills/
npx skills init <skill-name>
```

This creates `skills/<skill-name>/SKILL.md` with a template. Then add optional directories as needed:

```bash
mkdir -p skills/<skill-name>/references  # For detailed docs
mkdir -p skills/<skill-name>/scripts     # For executable code
mkdir -p skills/<skill-name>/assets      # For templates, images, etc.
```

## Step 3: Write the SKILL.md

### Frontmatter (Required)

```yaml
---
name: skill-name
description: What this skill does and WHEN to use it. Include trigger keywords, file types, or task descriptions.
---
```

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Kebab-case, lowercase, max 64 chars |
| `description` | Yes | Max 1024 chars, no `<>`. Include WHEN to trigger. |

**Critical:** The `description` is the ONLY thing the agent sees before deciding to load the skill. All trigger conditions must go here, not in the body.

### Frontmatter Examples

**Bad — vague:**
```yaml
description: This skill helps you work with documents. It can do many things...
```

**Good — trigger-focused:**
```yaml
description: Create and edit Word documents (.docx). Use for document creation, tracked changes, comments, or text extraction from .docx files.
```

### Body (Required)

The body contains instructions the agent follows after the skill is activated.

- Keep under **500 lines** (split into reference files if longer)
- Use **imperative form** ("Run the script" not "You should run")
- Prefer **examples over explanations**
- Reference bundled resources with **relative paths**
- Do NOT put "When to use" sections in the body — that belongs in the description

### Body Structure

```markdown
# Skill Title

## Overview
1-2 sentences on what this skill enables.

## Workflow / Instructions
Step-by-step procedures, commands, code examples.

## References
Links to reference files for detailed content:
- **Topic A details**: See references/topic-a.md
- **Topic B details**: See references/topic-b.md
```

## Step 4: Add Resources (Optional)

### references/
Documentation loaded into context only when needed. Use for:
- Detailed info only needed for specific sub-tasks
- Large content that would bloat SKILL.md
- Domain knowledge, schemas, API docs

**Best practice:** For large files (>10k words), include grep patterns in SKILL.md so the agent can search efficiently.

### scripts/
Executable code (Python/Bash) for deterministic, repeatable operations. Use when:
- The same code would be rewritten every time
- Deterministic reliability is needed
- Complex operations benefit from tested code

**Always test scripts** by running them before finalizing.

### assets/
Files used in output (NOT loaded into context). Use for:
- Templates to copy/modify
- Images, fonts, icons
- Boilerplate code directories

## Step 5: Progressive Disclosure

Keep SKILL.md lean. Split heavy content into reference files:

```
skill-name/
├── SKILL.md              # Core workflow, <500 lines
└── references/
    ├── setup.md          # Loaded only when needed
    ├── advanced.md       # Loaded only when needed
    └── troubleshooting.md
```

Reference from SKILL.md:
```markdown
**For setup details**: See references/setup.md
**For advanced usage**: See references/advanced.md
```

**Keep references one level deep** — all reference files should link directly from SKILL.md, not from other reference files.

For reference files over 100 lines, include a **table of contents** at the top.

## Step 6: Update README.md

After creating a skill, add it to the Available Skills section in README.md:

```markdown
### skill-name
> One-line description

**Use for:** Comma-separated use cases

\```bash
npx skills add jakerains/AgentSkills --skill skill-name
\```
```

## Step 7: Packaging (Optional)

To create a distributable `.skill` file:

```bash
cd skills/skill-name
zip -r ../../skill-name.skill .
```

The zip should contain contents at root level (SKILL.md at top, not nested in a subfolder).

## Validation Checklist

Before finalizing any skill:
- [ ] SKILL.md has valid YAML frontmatter with `name` and `description`
- [ ] `name` is kebab-case, ≤64 chars
- [ ] `description` is ≤1024 chars, no `<>`, includes trigger keywords
- [ ] Body is <500 lines
- [ ] All referenced files actually exist
- [ ] Scripts are executable and tested
- [ ] No extraneous files (README.md, CHANGELOG.md, etc. inside the skill)
- [ ] README.md updated with new skill entry

## Conciseness Principle

Only include in a skill:
- Project-specific procedures and workflows
- Non-obvious domain knowledge
- Reusable scripts and assets
- Critical business rules or gotchas

Omit:
- General programming knowledge the agent already has
- Standard library usage
- Obvious tool commands

---

## Processing Dropped .skill Files

When a user drops a `.skill` file (ZIP archive) into the repository root:

1. **Extract:** `mkdir -p skills/skill-name && unzip dropped-file.skill -d skills/skill-name`
2. **Fix nesting:** If extraction created `skills/skill-name/skill-name/`, move contents up one level
3. **Verify frontmatter:** Ensure SKILL.md has valid `name` and `description` in YAML frontmatter
4. **Delete** the original `.skill` file from root
5. **Update README.md** with the new skill entry
