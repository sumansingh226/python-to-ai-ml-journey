###AI agent skill
In an AI agent, a skill is a reusable capability that teaches the agent how to perform a specific type of task.

For example, an agent might have these skills:

web-search → search and summarize information
email → read and send emails
database → query a database
customer-support → handle customer questions
invoice-processing → extract information from invoices

A skill is often described in a .md file so the agent can understand what the skill does, when to use it, and how to use it.


# Weather Search Skill

## Description

This skill allows the agent to find the current weather
and forecast for a specified location.

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

User:

"What is the weather in Delhi today?"

Agent:

"The weather in Delhi today is 32°C with partly cloudy
conditions."

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