# Claude Skills Collection

A personal library of Claude Code skills for easy installation and use.

## Skills Catalog

| Skill | Description | Install |
|-------|-------------|---------|
| [skill-seekers](skills/skill-seekers/) | Convert documentation websites, GitHub repos, and PDFs into Claude skills | `cp -r skills/skill-seekers ~/.claude/skills/` |
| [shot-list](skills/shot-list/) | Generate professional shot lists from screenplays and scripts | `cp -r skills/shot-list ~/.claude/skills/` |

## Installation

### Method 1: Direct Copy (Recommended)

```bash
# Clone this repository
git clone https://github.com/jakerains/claude-skills-collection.git
cd claude-skills-collection

# Copy a skill to Claude's skills directory
cp -r skills/skill-seekers ~/.claude/skills/
cp -r skills/shot-list ~/.claude/skills/
```

### Method 2: Symlink (Auto-updates with git pull)

```bash
# Symlink so changes sync automatically
ln -s $(pwd)/skills/skill-seekers ~/.claude/skills/skill-seekers
ln -s $(pwd)/skills/shot-list ~/.claude/skills/shot-list
```

### Method 3: Plugin Marketplace

```bash
# Add this repo as a marketplace
/plugin marketplace add jakerains/claude-skills-collection

# Install skills from it
/plugin install skill-seekers@claude-skills-collection
```

## Skill Details

### skill-seekers

Converts documentation websites, GitHub repositories, and PDFs into Claude AI skills.

**Use when:**
- Creating Claude skills from documentation
- Scraping docs, GitHub repos, or PDFs for Claude
- Packaging documentation into `.zip` for Claude

**Files:**
- `SKILL.md` - Main skill definition
- `references/` - Detailed documentation

### shot-list

Generate professional shot lists from screenplays and scripts.

**Use when:**
- User uploads a screenplay (`.fountain`, `.fdx`, `.txt`, `.pdf`, `.docx`)
- Planning shots for production
- Breaking down scripts for filming

**Files:**
- `SKILL.md` - Main skill definition
- `scripts/` - Python utilities for parsing and PDF generation
- `references/` - Shot terminology and coverage patterns

## Adding New Skills

```bash
# Create new skill directory
mkdir -p skills/my-new-skill

# Add SKILL.md with required frontmatter
cat > skills/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: What it does and when to use it. Include trigger keywords.
---

# My New Skill

## Instructions
...
EOF

# Commit and push
git add skills/my-new-skill
git commit -m "Add my-new-skill"
git push
```

## SKILL.md Format

Each skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: skill-name          # Lowercase, hyphens only
description: Description  # Include trigger keywords for activation
---

# Skill Name

## When to Activate
- Trigger condition 1
- Trigger condition 2

## Instructions
...
```

## License

MIT
