# AI Agent Skill

In an AI agent, a **skill** is a reusable capability that teaches the agent how to perform a specific type of task.

For example, an agent might have these skills:

- **web-search** → Search and summarize information
- **email** → Read and send emails
- **database** → Query a database
- **customer-support** → Handle customer questions
- **invoice-processing** → Extract information from invoices

A skill is often described in a `.md` file so the agent can understand:

- What the skill does
- When to use it
- What inputs it needs
- How to perform the task
- What rules to follow
- What output to produce

---

# Example: Weather Search Skill

## Description

This skill allows the agent to find the current weather and forecast for a specified location.

## When to Use

Use this skill when the user asks about:

- Current weather
- Temperature
- Weather forecast
- Rain or snow predictions
- Weather conditions in a city

## Inputs

The skill requires:

- `location`: City or geographic location
- `date`: Optional date for the forecast

## Process

1. Identify the location from the user's request.
2. Get the latest weather information.
3. Check the temperature and weather conditions.
4. Return the information in a simple format.

## Example

### User

> What is the weather in Delhi today?

### Agent

> The weather in Delhi today is 32°C with partly cloudy conditions.

## Rules

- Always use the latest available weather information.
- Do not guess the weather.
- Ask for the location if it is not provided.
- Clearly mention the temperature and conditions.

## Output Format

Return:

- Location
- Temperature
- Weather condition
- Forecast, if requested

---

# Simple Way to Think About It

**Agent = Brain + Tools + Skills**

```text
Agent
 │
 ├── Skill: Weather
 │     └── skill.md
 │
 ├── Skill: Email
 │     └── skill.md
 │
 ├── Skill: Database
 │     └── skill.md
 │
 └── Skill: Customer Support
       └── skill.md

What Does a Skill Do?

A skill gives the agent a specific capability.


User
  │
  │ "What's the weather in Delhi?"
  ▼
AI Agent
  │
  │ Identifies that Weather Skill is required
  ▼
Weather Skill
  │
  │ Gets weather information
  ▼
AI Agent
  │
  │ Formats the result
  ▼
User
  │
  └── "Delhi: 32°C, Partly Cloudy"

Typical Skill Structure

A skill can contain:

skill-name/
│
└── skill.md

For example:

weather/
│
└── skill.md


email/
│
└── skill.md


database/
│
└── skill.md


customer-support/
│
└── skill.md



Each skill.md acts as an instruction manual for that particular capability.

In Short

A skill is a reusable set of instructions that gives an AI agent the knowledge and procedure needed to perform a particular task.

Agent = The system that decides what to do

Skill = Instructions for how to perform a specific task

Tool = The actual external capability used to perform the task

For example:

Agent
 │
 ├── Decides: "I need weather information"
 │
 ├── Uses: Weather Skill
 │
 └── Calls: Weather Tool/API