# AI Hallucination: A Complete Tutorial

What it is, why it happens, how to spot it, and how to fix or reduce it.

---

## Table of Contents

1. [What is AI hallucination?](#1-what-is-ai-hallucination)
2. [Simple examples](#2-simple-examples)
3. [Types of hallucination](#3-types-of-hallucination)
4. [Why it happens](#4-why-it-happens)
5. [Why it is dangerous](#5-why-it-is-dangerous)
6. [How to detect hallucinations](#6-how-to-detect-hallucinations)
7. [Fixes for users (prompting)](#7-fixes-for-users-prompting)
8. [Fixes for developers (systems)](#8-fixes-for-developers-systems)
9. [Hands-on: build a simple RAG fix](#9-hands-on-build-a-simple-rag-fix)
10. [Can hallucination be eliminated?](#10-can-hallucination-be-eliminated)
11. [Quick cheat sheet](#11-quick-cheat-sheet)
12. [Glossary](#12-glossary)

---

## 1. What is AI hallucination?

**AI hallucination** is when an AI model produces output that is **false, made up, or unsupported by any real source, but presents it confidently as if it were true.**

The word "hallucination" is a metaphor. The model is not seeing things. It is generating text that *sounds* right but has no grounding in fact.

Key points:

- The output is usually **fluent and confident**, which is what makes it dangerous.
- It affects **text models** (chatbots), **image models** (extra fingers, impossible objects), **code models** (functions that don't exist), and **speech models** (words never spoken).
- It is **not a bug in one product**. It is a property of how modern generative models work.

> **One-line definition:** A hallucination is a plausible-sounding answer that is not true.

---

## 2. Simple examples

| You ask | Hallucinated answer | Reality |
|---|---|---|
| "Summarize the 2019 paper *Quantum Gravity in Cats* by Dr. Smith." | A detailed, convincing summary | The paper does not exist |
| "Which Python function sorts a dict by value?" | `dict.sort_by_value()` | No such method exists |
| "Cite three court cases about X." | Three realistic-looking case names with citations | The cases were invented |
| "Who won the 2031 World Cup?" | A named winner | That event has not happened |
| Image prompt: "A person holding a cup" | A hand with 7 fingers | Image models don't understand anatomy |

Notice the pattern: the model **never says "I don't know."** It fills the gap with something plausible.

---

## 3. Types of hallucination

### 3.1 Intrinsic vs. extrinsic

- **Intrinsic hallucination:** The output **contradicts the source material you gave it.**
  *Example:* You paste an article that says "revenue rose 5%." The summary says "revenue fell 5%."
- **Extrinsic hallucination:** The output adds information that **can't be verified from the source** or from reality.
  *Example:* The summary adds a quote from the CEO that is not in the article.

### 3.2 Factual vs. faithfulness

- **Factuality hallucination:** Wrong about the real world (wrong date, invented person).
- **Faithfulness hallucination:** Not faithful to the user's instructions or provided context.

### 3.3 Common categories in practice

1. **Fabricated facts**: invented dates, names, statistics.
2. **Fabricated citations**: fake papers, URLs, case law, DOIs.
3. **Fabricated code**: nonexistent libraries, functions, or parameters.
4. **Reasoning errors**: confident but wrong math or logic.
5. **Outdated information**: stated as current when it is stale.
6. **Sycophancy**: agreeing with a false claim in your prompt.
7. **Fabricated tool or action results**: claiming to have run code, browsed, or saved a file when it did not.

---

## 4. Why it happens

This is the most important section. Understanding the *cause* tells you which fix to use.

### 4.1 The model predicts text, it does not look up truth

A large language model (LLM) is trained to answer one question over and over:

> *"Given the text so far, what token (word piece) most likely comes next?"*

It optimizes for **plausibility**, not **truth**. If a false sentence is statistically plausible, the model can produce it.

```
Prompt:  "The capital of Australia is"
Model:   P("Canberra") = 0.80   P("Sydney") = 0.18   P("Melbourne") = 0.02
```

Usually the right answer wins. But for rare or obscure facts, the probabilities are flat and the model picks something that merely *looks* right.

### 4.2 Training data problems

- **Gaps:** The model never saw the fact, so it guesses.
- **Errors:** The internet contains misinformation, and the model learns it.
- **Bias and imbalance:** Popular topics are well covered; niche topics are thin.
- **Knowledge cutoff:** The model knows nothing after its training date.
- **Duplicates and noise:** Repeated wrong claims get reinforced.

### 4.3 Compressed, lossy memory

The model's "knowledge" is stored as billions of numeric weights, not as a database of facts. Facts are **compressed and blurred together**. Recall is reconstruction, and reconstruction can be wrong, like remembering a face and getting details off.

### 4.4 Training rewards confident answers

- During training and evaluation, a guess can score better than "I don't know."
- Models fine-tuned with human feedback may learn that **confident, helpful-sounding answers get rewarded**, even when they are wrong.
- Result: models are pushed toward **always answering**, not toward **knowing when to abstain**.

### 4.5 No built-in fact-checking

The model has no internal step that says "let me verify this." It generates left to right, one token at a time. Once it starts a wrong claim, it tends to **keep going consistently** with it.

### 4.6 Snowballing (error compounding)

Each new token depends on the previous ones. One early mistake pushes the rest of the answer to stay consistent with the mistake, so the error grows.

### 4.7 Prompt-related causes

- **Vague or ambiguous prompts:** The model fills in the blanks.
- **Leading questions:** "Why is X true?" assumes X is true.
- **Missing context:** The model fills in what you did not provide.
- **Too much or conflicting context:** Long contexts can cause the model to miss or mix up details.
- **Requests for things that don't exist:** The model tries to be helpful and invents it.

### 4.8 Decoding settings

- **High temperature** (more randomness) makes unlikely, creative, and wrong tokens more probable.
- **Low temperature** is more stable, but it can still be confidently wrong.

### 4.9 Summary of causes

| Cause | Layer |
|---|---|
| Predicts plausible text, not truth | Model design |
| Missing / wrong / old training data | Data |
| Lossy compression of knowledge | Model design |
| Rewarded for confident answers | Training |
| No verification step | Architecture |
| Vague or leading prompt | User input |
| High temperature | Settings |

---

## 5. Why it is dangerous

- **Legal:** Lawyers have been sanctioned for submitting briefs with fake case citations.
- **Medical:** Wrong dosages, invented drug interactions, or made-up studies.
- **Academic:** Fake references that look real and waste researchers' time.
- **Software:** Imaginary APIs, insecure code, or "package hallucination" where attackers register the fake package names that models invent.
- **Business:** Wrong numbers in reports and bad decisions.
- **Trust:** Fluent errors make people over-trust AI.

The core risk: **hallucinations are not obvious.** They look exactly like correct answers.

---

## 6. How to detect hallucinations

### 6.1 Manual checks (you)

- **Verify citations.** Search the exact title, author, URL, or DOI. If it doesn't exist, it was hallucinated.
- **Cross-check key facts** with a trusted primary source.
- **Be extra suspicious of:** specific numbers, exact quotes, dates, names, URLs, and niche topics.
- **Ask the same question twice** (or rephrase it). Inconsistent answers are a red flag.
- **Ask the model to show its source or reasoning,** then check that.
- **Test the edges:** if the answer is unusually detailed about something obscure, be careful.

### 6.2 Automated checks (developers)

- **Self-consistency:** sample the answer several times; low agreement suggests a likely hallucination.
- **Groundedness / faithfulness scoring:** check whether each claim in the answer is supported by the retrieved documents.
- **Natural Language Inference (NLI) models:** classify whether the source *entails* or *contradicts* the claim.
- **Citation validators:** programmatically check that URLs resolve and cited quotes appear in the source.
- **LLM-as-judge:** a second model reviews the first model's answer against the sources.
- **Confidence / token probability:** low-probability spans can flag shaky claims (imperfect but useful).
- **Evaluation benchmarks:** TruthfulQA, HaluEval, and similar test sets measure how often a model hallucinates.

---

## 7. Fixes for users (prompting)

You cannot change the model, but you can change how you use it.

### 7.1 Give it permission to say "I don't know"

```
Answer only if you are confident. If you are unsure or don't know,
say "I don't know" instead of guessing.
```

### 7.2 Provide the source material

Paste the document and tell the model to use only that.

```
Using ONLY the text below, answer the question. If the answer is not
in the text, reply "Not found in the provided text."

<document>
...your text here...
</document>

Question: ...
```

### 7.3 Ask for quotes and evidence

```
For each claim, include the exact supporting quote from the document.
If you cannot find a quote, drop the claim.
```

### 7.4 Be specific and remove ambiguity

| Weak prompt | Better prompt |
|---|---|
| "Tell me about the Mercury project." | "Tell me about NASA's Project Mercury (1958-1963), focusing on the astronauts selected." |

### 7.5 Avoid leading questions

| Leading | Neutral |
|---|---|
| "Why is X the best framework?" | "Compare X and Y. What are the trade-offs?" |

### 7.6 Ask for step-by-step reasoning

```
Think through this step by step before giving your final answer.
```

This often catches logic and math slips (it does not guarantee correctness).

### 7.7 Ask the model to verify itself

```
Review your answer above. List any claims you are not fully sure about
and mark them as uncertain.
```

### 7.8 Break big tasks into small ones

Smaller, focused questions leave less room for invention than one huge request.

### 7.9 Lower the temperature (if you have access)

Use a low temperature (for example 0 to 0.3) for factual tasks.

### 7.10 Use tools when available

Use a model/product with **web search, file upload, or code execution**, and ask it to use them for facts, math, and data.

### 7.11 Always verify high-stakes output

For medical, legal, financial, or safety decisions, **a human must check against primary sources.**

---

## 8. Fixes for developers (systems)

Fixing hallucination at the system level is far more reliable than prompting alone.

### 8.1 Retrieval-Augmented Generation (RAG)

Instead of relying on the model's memory, **retrieve relevant documents first and make the model answer from them.**

```
User question
     |
     v
 [Retriever] --> finds relevant passages from your trusted knowledge base
     |
     v
 [Prompt] = question + retrieved passages + "answer only from these"
     |
     v
 [LLM] --> answer with citations
```

Benefits: fresher info, domain-specific knowledge, traceable sources.
Caveat: bad retrieval = bad answers. Retrieval quality matters as much as the model.

### 8.2 Grounding and citations

- Require the model to **cite the passage** for each claim.
- Validate citations in code. Reject answers whose citations do not exist or do not support the claim.

### 8.3 Use tools instead of memory

Let the model call:

- a **calculator / code interpreter** for math,
- a **database or API** for live facts,
- a **search engine** for current events.

Rule of thumb: *if the answer is checkable, make the model check it rather than recall it.*

### 8.4 Structured outputs and constraints

- Force outputs into a **JSON schema** or from a **fixed list of allowed values**.
- Constrain answers to known entities (for example, product IDs that exist in your catalog).

### 8.5 Fine-tuning for honesty

- Train or tune on examples where the correct behavior is **abstaining** when evidence is missing.
- Include "unanswerable" questions in your training/evaluation data.

### 8.6 Verification layers

- **Second-pass check:** another model or rule-based step verifies claims against sources.
- **Self-consistency voting:** generate several answers and pick the majority.
- **Chain-of-verification:** the model drafts an answer, writes verification questions, answers them independently, then revises.

### 8.7 Prompt and system design

- Clear system prompt: scope, tone, and **"say you don't know when evidence is missing."**
- Keep context focused. Do not stuff irrelevant text into the prompt.
- Put the most important instructions and documents where the model attends best (clearly labeled, not buried).

### 8.8 Human-in-the-loop

For high-stakes domains, route low-confidence or high-impact answers to a human reviewer.

### 8.9 Monitoring and evaluation

- Build a **test set** of questions with known answers and track the hallucination rate over time.
- Log real user queries and review failures.
- Re-test whenever you change the model, prompt, or retrieval setup.

### 8.10 Fix-by-cause table

| Cause | Best fix |
|---|---|
| Missing or old knowledge | RAG, web search, tools |
| Fabricated citations | Citation validation, require quotes |
| Wrong math / logic | Code interpreter, step-by-step reasoning |
| Vague prompts | Better prompt design, clarifying questions |
| Overconfidence | Abstention training, "I don't know" instructions |
| Random errors | Lower temperature, self-consistency |
| High-stakes domain | Human review |

---

## 9. Hands-on: build a simple RAG fix

A tiny Python example showing the idea. It uses simple keyword retrieval to keep the code short. In production you would use embeddings and a vector database.

```python
# rag_demo.py
# Demonstrates "answer only from retrieved context" to reduce hallucination.

KNOWLEDGE_BASE = [
    "Our refund window is 30 days from the date of purchase.",
    "Support is available Monday to Friday, 9am to 5pm IST.",
    "Premium plans include priority email support and a 99.9% uptime SLA.",
]

def retrieve(question: str, k: int = 2) -> list[str]:
    """Naive retrieval: rank passages by shared words with the question."""
    q_words = set(question.lower().split())
    scored = []
    for passage in KNOWLEDGE_BASE:
        overlap = len(q_words & set(passage.lower().split()))
        scored.append((overlap, passage))
    scored.sort(reverse=True)
    return [p for score, p in scored[:k] if score > 0]

def build_prompt(question: str) -> str:
    context = retrieve(question)
    if not context:
        # No evidence found: tell the model to abstain.
        context_text = "(no relevant documents found)"
    else:
        context_text = "\n".join(f"- {c}" for c in context)

    return f"""You are a support assistant.
Answer ONLY using the context below.
If the answer is not in the context, say: "I don't have that information."
Quote the line you used.

Context:
{context_text}

Question: {question}
Answer:"""

if __name__ == "__main__":
    for q in ["What is the refund window?", "Do you ship to Mars?"]:
        print("=" * 50)
        print(build_prompt(q))
```

**What this demonstrates**

1. The model gets **real evidence** in the prompt.
2. It is **told to refuse** when evidence is missing ("Do you ship to Mars?" gets no context, so the right answer is "I don't have that information").
3. It is asked to **quote its source**, which makes checking easy.

Send the generated prompt to any LLM API to see the effect.

---

## 10. Can hallucination be eliminated?

**Not completely, with today's technology.**

- It comes from the core design (probabilistic text generation), so it can be **reduced a lot** but not reduced to zero.
- Newer models hallucinate less than older ones, and retrieval plus verification helps further.
- The practical goal is **risk management**: lower the rate, detect the rest, and keep humans in the loop where mistakes are costly.

Think of an LLM as a **brilliant, fast, sometimes overconfident assistant**: great for drafts, ideas, and explanations, but you check the facts that matter.

---

## 11. Quick cheat sheet

**If you are a user**

- [ ] Give the model the source text when possible
- [ ] Allow "I don't know"
- [ ] Ask for quotes / sources, then verify them
- [ ] Be specific; avoid leading questions
- [ ] Double-check names, numbers, dates, citations, URLs, code
- [ ] Never rely on AI alone for medical, legal, or financial decisions

**If you are a developer**

- [ ] Use RAG with a trusted knowledge base
- [ ] Require and validate citations
- [ ] Use tools (search, calculator, database) for checkable facts
- [ ] Constrain outputs with schemas
- [ ] Add a verification pass
- [ ] Measure the hallucination rate with a test set
- [ ] Add human review for high-stakes cases

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **LLM** | Large Language Model, an AI trained to predict text |
| **Token** | A small piece of text (word or word fragment) the model works with |
| **Hallucination** | Confident output that is false or unsupported |
| **Grounding** | Tying answers to real, checkable sources |
| **RAG** | Retrieval-Augmented Generation: fetch documents, then answer from them |
| **Temperature** | A setting controlling randomness of output |
| **Knowledge cutoff** | The date after which the model has no training data |
| **Sycophancy** | Agreeing with the user even when they are wrong |
| **Faithfulness** | How well the answer stays true to the provided source |
| **Abstention** | The model declining to answer when unsure |
| **Chain-of-verification** | Draft, generate check questions, answer them, then revise |

---

### Final takeaway

> LLMs generate **plausible** text, not guaranteed **true** text.
> Reduce hallucination by **grounding** the model in real sources, **constraining** what it can say, **verifying** its output, and **keeping humans in the loop** when it matters.