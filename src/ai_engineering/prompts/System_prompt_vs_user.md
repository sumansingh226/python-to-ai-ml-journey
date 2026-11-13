# System Prompt vs. User Prompt

A quick guide to the two kinds of instructions you give a language model, what each is for, and when to use which.

---

## 1. What is a System Prompt?

A **system prompt** is a set of standing instructions given to the model *before* the conversation starts. It defines **who the model is and how it should behave** for the whole session.

- Written by the developer / app builder (or by you, in a custom setup)
- Persists across every turn of the conversation
- Usually hidden from the end user
- Sets role, tone, rules, format, constraints, and background knowledge

**Think of it as:** the job description and company handbook handed to a new employee.

### Typical contents
- Role / persona ("You are a senior support agent for Acme Inc.")
- Tone and style ("Be concise, friendly, no jargon.")
- Rules and guardrails ("Never give legal advice.")
- Output format ("Always reply in JSON with keys `answer` and `sources`.")
- Reference material (product docs, glossary, policies)

---

## 2. What is a User Prompt?

A **user prompt** is the message you send *during* the conversation. It describes **the specific task or question right now**.

- Written by the end user, one turn at a time
- Changes every message
- Visible in the chat
- Carries the actual request, plus any data to work on

**Think of it as:** the specific assignment you hand that employee today.

### Typical contents
- A question ("How do I reset my password?")
- A task ("Summarize this article.")
- Input data (text, code, a table, a file)
- Follow-ups and corrections ("Make it shorter.")

---

## 3. Side-by-Side Comparison

| | System Prompt | User Prompt |
|---|---|---|
| **Purpose** | Define role, rules, style | Make a specific request |
| **Scope** | Whole conversation | One turn |
| **Who writes it** | Developer / app owner | End user |
| **How often it changes** | Rarely | Every message |
| **Visibility** | Usually hidden | Visible |
| **Analogy** | Job description | Today's task |
| **Example** | "You are a French tutor. Correct every mistake." | "Check this sentence: *Je suis allé au marché hier.*" |

---

## 4. When to Use Which

### Put it in the **system prompt** when it is...
- **Permanent:** should apply to every reply (tone, persona, language)
- **A rule or guardrail:** safety limits, things to never do
- **A format requirement:** JSON schema, markdown style, length limits
- **Shared background:** company info, documentation, definitions
- **Something the user shouldn't have to repeat** every time

### Put it in the **user prompt** when it is...
- **Specific to this request:** the question or task at hand
- **Changing input:** the document, code, or data to process
- **A one-off preference:** "just this once, explain it like I'm five"
- **A follow-up or correction** to the previous answer

### Rule of thumb
> If you'd have to type it again in every message, it belongs in the **system prompt**.
> If it only matters for this one request, it belongs in the **user prompt**.

---

## 5. Best Practices

**System prompt**
- Be clear and specific; vague roles give vague behavior
- State priorities when rules could conflict
- Include examples of ideal output when format matters
- Keep it focused; long, contradictory prompts get partly ignored
- Don't put secrets (API keys, passwords) in it

**User prompt**
- State the goal and the desired output format
- Provide the context the model needs; it can't read your mind
- Separate instructions from data (use headings or tags like `<document>…</document>`)
- Iterate with follow-ups instead of rewriting everything

---

## 6. Example

### Example system prompt

```text
You are "Penny", a friendly customer-support assistant for BrightBank,
a retail bank.

Rules:
- Answer only questions about BrightBank accounts, cards, and fees.
- Never ask for or repeat full card numbers, PINs, or passwords.
- If you are unsure, say so and offer to connect the customer to a human agent.
- Do not give investment, tax, or legal advice.

Style:
- Warm, clear, and brief (max 120 words unless asked for more).
- Use plain language, no banking jargon.
- End every reply with: "Is there anything else I can help with?"
```

### Example user prompts (sent one at a time)

```text
Turn 1: What's the monthly fee on the Silver checking account?
Turn 2: Can you explain that more simply?
Turn 3: My card was stolen, what do I do?
```

### What happens

1. The model reads the **system prompt** first, so it knows it is "Penny", knows its rules, and knows the style.
2. For each **user prompt**, it answers that specific question while still following the system prompt.
3. On Turn 3, the guardrails matter: Penny gives urgent, safe guidance without asking for card numbers, and offers a human agent if needed.

### Example of a good reply to Turn 1

```text
The Silver checking account has a $5 monthly fee, which is waived if you
keep a balance of $1,500 or more. Is there anything else I can help with?
```

---

## 7. Common Mistakes

| Mistake | Fix |
|---|---|
| Putting a one-time task in the system prompt | Move it to the user prompt |
| Repeating the same rules in every user message | Move them to the system prompt |
| Writing a very long, contradictory system prompt | Trim it; keep rules consistent and prioritized |
| Mixing instructions and data with no separation | Use delimiters or tags |
| Assuming the system prompt is a secure secret | Treat it as potentially extractable; keep secrets out |

---

## 8. TL;DR

- **System prompt** = *who the model is and the rules it follows* (set once, always on).
- **User prompt** = *what you want right now* (changes every turn).
- Use the **system prompt** for anything permanent; use the **user prompt** for anything specific to the current request.
