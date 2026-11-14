# Claude Skills: What They Are, How to Make One, How to Use It

## 1. What is a Claude skill?

A **skill** is a folder of instructions that Claude loads only when a task needs it.
Think of it as a recipe card: "when you're asked to do X, follow these steps."

- It's just files: a `SKILL.md`, plus any scripts, templates or reference docs it needs.
- Claude reads every skill's **name + description** up front, which is cheap.
- It reads the **full instructions** only when your request matches the description, so many skills can be installed without filling up Claude's context.
- Skills work in Claude Code, the Claude apps and the Claude API (Agent SDK).

**Skill vs CLAUDE.md**

| | CLAUDE.md | Skill |
|---|---|---|
| Loaded | Every session, always | Only when the task matches |
| Good for | Rules that always apply ("stay inside this folder") | Workflows for one kind of task ("how to render a video") |
| Size | Keep short | Can be long, with extra files |

---

## 2. Where skills live

| Location | Who gets it |
|---|---|
| `.claude/skills/<skill-name>/SKILL.md` (inside a project) | Only this project. Can be committed to git and shared. |
| `~/.claude/skills/<skill-name>/SKILL.md` (home folder) | All of your projects |
| Plugins | Anyone who installs the plugin |

This project uses **project skills only**, for example
`.claude/skills/tutorial-video-playbook/SKILL.md`.

---

## 3. Anatomy of a skill

```
.claude/skills/
└── my-skill/
    ├── SKILL.md          ← required: frontmatter + instructions
    ├── references/       ← optional: longer docs Claude opens when needed
    │   └── checklist.md
    └── scripts/          ← optional: helper scripts Claude can run
        └── check.mjs
```

### SKILL.md

```markdown
---
name: my-skill
description: What it does AND when to use it. Use when the user asks to "X", "Y" or "Z".
---

# My Skill

## Steps
1. First do this.
2. Then do this. For details, read `references/checklist.md`.
3. Run `node .claude/skills/my-skill/scripts/check.mjs` to verify.

## Rules
- Always ...
- Never ...
```

**Frontmatter fields**

- `name`: lowercase-with-dashes, matching the folder name.
- `description`: **the most important line.** Claude decides whether to use the skill from this alone, so say what the skill does *and* the trigger phrases a user would actually type.
- Optional: `metadata` (version, source) and `allowed-tools` (limits which tools the skill may use).

---

## 4. How to make a skill (step by step)

1. **Pick one job.** A good skill does one thing well ("write YouTube titles"), not "everything about YouTube".
2. **Create the folder:** `.claude/skills/<name>/`.
3. **Write `SKILL.md`:**
   - frontmatter with `name` + a trigger-rich `description`
   - numbered steps Claude should follow
   - hard rules / don'ts
   - an example of good output
4. **Move long material out** into `references/*.md` and link to it from `SKILL.md`. Claude opens it only when needed (this is called *progressive disclosure*).
5. **Add scripts** for anything that must be exact every time (validation, file conversion). Scripts run the same way every time; prose doesn't.
6. **Test it:** start a new Claude session, ask something that should trigger it, and check that Claude says it's using the skill. If it doesn't trigger, improve the `description`.

### Example: a tiny real skill

`.claude/skills/shorts-checklist/SKILL.md`

```markdown
---
name: shorts-checklist
description: Pre-upload checklist for a YouTube Short in this project. Use when the user says "check my short", "is the short ready" or "before I upload the short".
---

# Shorts Checklist

1. Composition is 1080x1920 at 30 fps.
2. No text in the bottom 25% or the right 15% (YouTube UI covers it).
3. Length is under 60 s.
4. Title is under 100 characters, with keywords in the first 40.
5. "Related video" is set to the long-form video.

Report each item as ✅ or ❌ with the reason. Don't fix anything until the user says so.
```

---

## 5. How to use a skill

**Automatically.** Ask normally ("give me a title for the Excel short"). If it matches a skill's description, Claude loads that skill by itself.

**By name.** Type a slash command with the skill name:

```
/yt-title-optimizer
/remotion-render
```

**Routed by CLAUDE.md.** In this project, `CLAUDE.md` has a routing table ("request is about X → use skill Y"). Claude checks it on every message and says which skill it's using, e.g. *"Using yt-seo + yt-title-optimizer."*

---

## 6. Installing someone else's skill

In this project, install skills project-only so they go straight into `.claude/skills`:

```bash
npx skills add <repo> --skill <name> -a claude-code --copy -y
```

Before you rely on it:

1. **Read the whole `SKILL.md` and every script.** A skill is instructions plus code that Claude will follow and run.
2. **Scan it for API keys, logins, tokens and paid services.** This project only allows skills that need none.
3. **Add it to the routing table** in `CLAUDE.md`.

---

## 7. Tips for skills that work well

- **The description is the trigger.** Use the user's real words, e.g. "make it smoother" rather than "motion refinement".
- **Write instructions, not essays.** Numbered steps and short rules.
- **Keep SKILL.md focused**, and push detail into `references/`.
- **Script anything that must be exact.**
- **One skill, one job.** Split it if it grows into two.
- **Rules beat skills.** If a skill disagrees with `CLAUDE.md`'s hard rules, the hard rules win.
