# Claude Skills: What They Are, How to Make One, How to Use It

## 1. What is a Claude skill?

A **skill** is a folder of instructions that Claude loads only when a task needs it.
Think of it as a recipe card: "when you're asked to do X, follow these steps."

- It's just files: a `SKILL.md`, plus any scripts, templates or reference docs it needs.
- Claude reads every skill's **name + description** up front, which is cheap.
- It reads the **full instructions** only when your request matches the description, so many skills can be installed without filling up Claude's context.
- Skills work in Claude Code, the Claude apps and the Claude API (Agent SDK).
