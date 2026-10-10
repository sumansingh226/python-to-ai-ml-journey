# Tokens in AI Models: Complete Guide (Basic to Advanced)

---

## Table of Contents

1. [What Is a Token?](#1-what-is-a-token)
2. [Why Models Use Tokens](#2-why-models-use-tokens)
3. [Tokens vs Words vs Characters](#3-tokens-vs-words-vs-characters)
4. [What Is Tokenization?](#4-what-is-tokenization)
5. [Tokenization Algorithms](#5-tokenization-algorithms)
6. [Vocabulary and Token IDs](#6-vocabulary-and-token-ids)
7. [Special Tokens](#7-special-tokens)
8. [From Tokens to Embeddings](#8-from-tokens-to-embeddings)
9. [How a Model Generates Tokens](#9-how-a-model-generates-tokens)
10. [Context Window](#10-context-window)
11. [Input, Output, and Reasoning Tokens](#11-input-output-and-reasoning-tokens)
12. [Tokens and Cost](#12-tokens-and-cost)
13. [Tokens and Speed](#13-tokens-and-speed)
14. [Multilingual Tokenization](#14-multilingual-tokenization)
15. [Code, Numbers, and Whitespace](#15-code-numbers-and-whitespace)
16. [Multimodal Tokens (Images, Audio, Video)](#16-multimodal-tokens-images-audio-video)
17. [Tokenizer Quirks and Failure Modes](#17-tokenizer-quirks-and-failure-modes)
18. [Advanced Topics](#18-advanced-topics)
19. [Practical Tips for Saving Tokens](#19-practical-tips-for-saving-tokens)
20. [Hands-On Code Examples](#20-hands-on-code-examples)
21. [Glossary](#21-glossary)
22. [Quick Summary](#22-quick-summary)

---

# PART 1: BASICS

## 1. What Is a Token?

A **token** is the basic unit of text (or other data) that an AI language model reads and writes. Models do not see letters or words directly. They see a sequence of tokens, each of which is just an integer ID.

A token can be:

- A whole word: `"apple"`
- Part of a word: `"un"`, `"believ"`, `"able"`
- A single character: `"a"`, `"?"`
- A space plus a word: `" the"`
- Punctuation or symbols: `"."`, `"</"`
- A byte or a piece of an emoji or rare character

**Example**

```
Text:    "Tokenization is fun!"
Tokens:  ["Token", "ization", " is", " fun", "!"]
IDs:     [4421, 2065, 318, 1257, 0]      (illustrative numbers only)
```

The exact split depends on the tokenizer of the specific model.

---

## 2. Why Models Use Tokens

Neural networks work with numbers, not text. Tokens are the bridge:

```
Text  →  Tokens  →  Token IDs  →  Embeddings (vectors)  →  Model  →  Next-token probabilities  →  Text
```

Why not use plain characters or whole words?

| Approach | Advantage | Problem |
|---|---|---|
| **Characters** | Tiny vocabulary, no unknown words | Sequences become very long; hard to learn meaning |
| **Whole words** | Short sequences, meaningful units | Huge vocabulary; cannot handle new, misspelled, or rare words (out-of-vocabulary problem) |
| **Subword tokens** | Balanced: moderate vocabulary, handles new words by splitting them | Splits can be odd for some languages and inputs |

Modern models use **subword tokens** because they are a good compromise.

---

## 3. Tokens vs Words vs Characters

Rough rules of thumb for **English** text with common modern tokenizers:

- 1 token ≈ 4 characters
- 1 token ≈ ¾ of a word
- 100 tokens ≈ 75 words
- 1,000 tokens ≈ 750 words (about 1.5 pages of text)

These are approximations. They vary by:

- **Language** (non-English text often needs more tokens)
- **Content type** (code, numbers, and special characters usually need more)
- **Tokenizer** (different models count differently)

> Always use the model provider's official token counter when accuracy matters.

---

## 4. What Is Tokenization?

**Tokenization** is the process of converting raw text into tokens. **Detokenization** is the reverse.

Typical pipeline:

1. **Normalization**: clean text (Unicode normalization, optional lowercasing, etc.)
2. **Pre-tokenization**: split roughly on spaces, punctuation, or regex patterns
3. **Subword splitting**: apply the learned algorithm (BPE, WordPiece, etc.)
4. **Mapping to IDs**: look up each piece in the vocabulary
5. **Add special tokens**: for example start-of-sequence or role markers

The tokenizer is **trained separately** from the model, on a large text corpus, before model training. The model and its tokenizer are tied together: you must always use the matching tokenizer.

---

# PART 2: INTERMEDIATE

## 5. Tokenization Algorithms

### 5.1 Byte Pair Encoding (BPE)

Used by many GPT-style and other models.

**How the vocabulary is learned**

1. Start with a base vocabulary (characters or bytes).
2. Count all adjacent pairs of symbols in the training corpus.
3. Merge the **most frequent pair** into a new symbol.
4. Repeat until the vocabulary reaches the target size (e.g., 32k, 50k, 100k+ tokens).

**Mini example**

Corpus words: `low`, `lower`, `lowest`

```
Start:   l o w | l o w e r | l o w e s t
Merge 1: (l, o) → lo
Merge 2: (lo, w) → low
Merge 3: (e, r) → er
...
```

Frequent chunks like `low` become single tokens. Rare words get split into smaller known pieces.

### 5.2 Byte-Level BPE

BPE applied to **raw bytes (UTF-8)** instead of characters. The base vocabulary is the 256 possible byte values, so **any** text, including emojis and rare scripts, can be represented. There is no "unknown token" problem.

### 5.3 WordPiece

Used by BERT-style models. Similar to BPE, but merges are chosen by **likelihood gain** on the training data rather than raw frequency. Continuation pieces are marked, for example `##ing`.

```
"playing" → ["play", "##ing"]
```

### 5.4 Unigram Language Model

Used in SentencePiece-based models. Starts with a **large** candidate vocabulary and **removes** tokens that contribute least to the corpus likelihood until the target size is reached. It can output multiple possible segmentations with probabilities, which allows **subword regularization** (random sampling of splits during training).

### 5.5 SentencePiece

A **tool/library**, not a single algorithm. It treats text as a raw stream (including spaces, often shown as `▁`) and does not require pre-splitting by whitespace. This makes it friendly for languages without spaces (Chinese, Japanese, Thai). It supports BPE and Unigram.

### 5.6 Comparison

| Method | Core Idea | Typical Use |
|---|---|---|
| BPE | Merge most frequent pairs | GPT-style, many LLMs |
| Byte-level BPE | BPE over bytes | No unknown tokens, any script |
| WordPiece | Merge by likelihood | BERT family |
| Unigram | Prune a large vocabulary | T5, many multilingual models |
| SentencePiece | Library, whitespace-agnostic | Multilingual and many open models |

---

## 6. Vocabulary and Token IDs

- The **vocabulary** is the full list of tokens the model knows. Sizes commonly range from about 30,000 to 250,000+ entries.
- Each token has a unique **integer ID**.
- Larger vocabulary: shorter sequences (cheaper per text), but a larger embedding table and output layer.
- Smaller vocabulary: longer sequences, smaller embedding table.

**Vocabulary size tradeoff**

| Bigger vocab | Smaller vocab |
|---|---|
| Fewer tokens per text | More tokens per text |
| Bigger embedding/output matrices | Smaller matrices |
| Rare tokens may be under-trained | Better coverage per token |
| Often better for multilingual text | Often worse for multilingual text |

---

## 7. Special Tokens

Special tokens carry structure, not ordinary text. Names vary by model.

| Token (examples) | Purpose |
|---|---|
| `<BOS>` / `<s>` | Beginning of sequence |
| `<EOS>` / `</s>` | End of sequence. The model emits this to signal it is done |
| `<PAD>` | Padding so batch items have equal length |
| `<UNK>` | Unknown token (mostly in older, non-byte-level tokenizers) |
| `<MASK>` | Masked position (BERT-style training) |
| `[CLS]`, `[SEP]` | Classification and separator tokens (BERT-style) |
| Role/turn markers | Mark system, user, assistant turns in chat models |
| Tool-call tokens | Mark function/tool calls and results |

**Chat templates**: chat models wrap messages in special tokens. A conversation like "system / user / assistant" is converted into one long token sequence with role markers. These markers also **consume tokens** from your budget.

---

## 8. From Tokens to Embeddings

After tokenization, each token ID is turned into a **vector** (a list of numbers):

```
Token ID 1257  →  lookup in embedding matrix  →  [0.12, -0.84, 0.33, ... ]  (e.g., 4096 numbers)
```

- The **embedding matrix** has shape `(vocab_size × hidden_dim)`.
- Embeddings are **learned** during training. Tokens used in similar contexts end up with similar vectors.
- **Positional information** is added (for example learned positions, sinusoidal encodings, or rotary embeddings (RoPE)) so the model knows token **order**.

```
Final input to transformer = token embedding + position information
```

Then stacked **transformer layers** (attention + feed-forward) transform these vectors.

---

## 9. How a Model Generates Tokens

Language models are **autoregressive**: they predict **one token at a time**.

```
Input tokens → Transformer → logits (a score for every vocab token)
            → softmax → probability distribution
            → pick next token → append → repeat
```

### Logits and probabilities

At each step the final layer outputs a **logit** for each of the V tokens in the vocabulary. **Softmax** converts these to probabilities that sum to 1.

### Decoding / sampling strategies

| Strategy | What it does |
|---|---|
| **Greedy** | Always pick the highest-probability token. Deterministic but can be repetitive |
| **Temperature** | Rescales logits. Low (<1) = more focused; high (>1) = more random |
| **Top-k** | Sample only from the k most likely tokens |
| **Top-p (nucleus)** | Sample from the smallest set of tokens whose cumulative probability ≥ p |
| **Beam search** | Keep several candidate sequences and choose the best overall |
| **Repetition / frequency penalties** | Discourage repeating tokens |

Generation stops when the model emits an **EOS** token, hits a **max token limit**, or matches a **stop sequence**.

---

## 10. Context Window

The **context window** (or context length) is the **maximum number of tokens** the model can handle at once. It includes:

- System prompt
- Conversation history
- Your current input (and any documents/images)
- The model's output being generated
- Tool definitions and tool results
- Any hidden reasoning tokens (see next section)

```
Context window = input tokens + output tokens (+ reasoning tokens)
```

If the total exceeds the window, you must truncate, summarize, or retrieve selectively. Models can only "see" what is inside the window. They have no memory of anything outside it unless an external system adds it back.

Context windows have grown from about 512 to 2,048 tokens in early models to hundreds of thousands, and in some models over a million tokens.

> A larger window does not guarantee equally good use of all of it. Models can be weaker at using information buried in the middle of very long inputs ("lost in the middle" effect).

---

## 11. Input, Output, and Reasoning Tokens

| Type | Meaning |
|---|---|
| **Input (prompt) tokens** | Everything you send to the model |
| **Output (completion) tokens** | What the model generates |
| **Reasoning / thinking tokens** | Intermediate "thinking" tokens some models produce before the final answer. They often count as output tokens for billing and for the context window, even if not fully shown |
| **Cached tokens** | Input tokens served from a prompt cache, usually cheaper and faster |

**Max tokens parameter**: usually limits the **output** length. If the limit is hit, the response can be cut off mid-sentence.

---

## 12. Tokens and Cost

Most AI APIs bill **per token**, typically quoted per million tokens, with **different prices for input and output** (output is usually more expensive).

```
Cost = (input_tokens × input_price) + (output_tokens × output_price)
```

**Example (illustrative prices, not real)**

- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Request: 2,000 input + 500 output tokens

```
Input  cost = 2,000 / 1,000,000 × $3  = $0.006
Output cost =   500 / 1,000,000 × $15 = $0.0075
Total       = $0.0135
```

Things that raise cost: long system prompts resent every turn, long chat histories, large documents, verbose outputs, and heavy reasoning. Always check the provider's current pricing page.

---

## 13. Tokens and Speed

- **Time to first token (TTFT)**: delay before the first output token. Grows with prompt length.
- **Tokens per second**: generation speed. Each new token requires a forward pass.
- Longer outputs take proportionally longer.
- Longer contexts increase memory use and can slow generation.

---

# PART 3: ADVANCED

## 14. Multilingual Tokenization

Tokenizers trained mostly on English text are **more efficient for English**. Other languages may be split into many small pieces.

```
English:  "Hello, how are you?"   →  few tokens
Other scripts (same meaning)      →  often more tokens
```

Consequences:

- **Higher cost** for the same meaning in some languages.
- **Smaller effective context window** for those languages.
- **Potentially lower quality**, because meaning is spread over many fragments.

This metric is sometimes called **tokenizer fertility** (average tokens per word). Newer tokenizers with larger, more multilingual vocabularies reduce this gap.

---

## 15. Code, Numbers, and Whitespace

### Code
- Common keywords and syntax (`function`, `return`, `()`) are usually single tokens.
- Long identifiers, uncommon variable names, and deep indentation increase token counts.
- Many modern tokenizers merge runs of spaces or indentation into single tokens to be efficient.

### Numbers
- Numbers are often split into arbitrary chunks, e.g. `"12345"` → `["123", "45"]`.
- The same number can tokenize differently depending on surrounding text.
- This is one reason models can struggle with exact arithmetic. Some tokenizers split digits individually or in fixed groups to help.

### Whitespace and case
- `"hello"`, `" hello"`, `"Hello"`, and `" Hello"` are often **different tokens**.
- Leading spaces are usually part of the token.
- Extra whitespace, newlines, and formatting symbols all cost tokens.

---

## 16. Multimodal Tokens (Images, Audio, Video)

Models that handle more than text convert other inputs into tokens or token-like vectors.

### Images
- The image is split into **patches** (for example 14×14 or 16×16 pixels).
- Each patch becomes an **image token / embedding** through a vision encoder.
- Larger or higher-resolution images produce more tokens. Many providers publish a formula based on image size.

### Audio
- Audio is converted to a spectrogram or processed with a neural audio codec.
- It is divided into short frames, each producing a token or embedding.
- Some codecs produce **discrete audio tokens** (using residual vector quantization).

### Video
- Treated as sampled frames (image tokens) plus optional audio. Token counts can grow very quickly.

### Output modalities
- Some models can also **generate** image or audio tokens, which are then decoded back to pixels or waveforms.

---

## 17. Tokenizer Quirks and Failure Modes

| Issue | Explanation |
|---|---|
| **Letter counting errors** | The model sees tokens, not letters. Asking "how many r's in strawberry" requires reasoning over letters the model never directly sees |
| **Reversing / spelling tasks** | Same reason: characters are hidden inside multi-character tokens |
| **Arithmetic errors** | Inconsistent number splitting |
| **Glitch tokens** | Rare tokens that appeared in the tokenizer's training data but barely in the model's training data, leading to odd behaviour when used |
| **Trailing-space problems** | Prompts ending in a space can cause strange completions because the model expects spaces at the *start* of tokens |
| **Token boundary effects** | Prompts that end mid-word can distort predictions ("token healing" techniques address this) |
| **Prompt injection via odd Unicode** | Unusual characters may tokenize unexpectedly and bypass naive filters |
| **Truncation** | Hitting limits mid-output or mid-JSON breaks structured outputs |
| **Tokenizer mismatch** | Using the wrong tokenizer for a model gives wrong counts and degraded behaviour |

---

## 18. Advanced Topics

### 18.1 Attention and Quadratic Cost
In standard self-attention, every token attends to every other token, so compute and memory scale roughly with **n²** (n = number of tokens). This is why long contexts are expensive. Techniques to reduce this include:

- Sparse / sliding-window attention
- Grouped-query and multi-query attention
- Linear attention variants and state-space models
- FlashAttention-style memory-efficient kernels

### 18.2 KV Cache
During generation, the model stores the **keys and values** computed for previous tokens so it doesn't recompute them. This **KV cache** makes generation faster but uses memory that **grows linearly with context length** (and with batch size, layers, and heads). Managing the KV cache (quantization, paging, eviction) is a major part of efficient LLM serving.

### 18.3 Prompt Caching
Providers can cache the processed form of a **repeated prompt prefix** (system prompt, documents, tool definitions). Later requests reusing the same prefix are cheaper and faster. To benefit: put stable content first and variable content last.

### 18.4 Prefill vs Decode
- **Prefill**: processing all input tokens in parallel. Compute-bound and fast per token.
- **Decode**: generating output tokens one by one. Memory-bandwidth-bound and slower per token.

### 18.5 Speculative Decoding
A small, fast "draft" model proposes several tokens, and the large model verifies them in one pass. Accepted tokens are generated much faster while keeping the large model's output distribution.

### 18.6 Multi-Token Prediction
Training or decoding the model to predict **several future tokens** at once, which can improve quality and speed.

### 18.7 Constrained / Structured Decoding
At each step, **mask out** tokens that would violate a grammar or JSON schema, so the output is guaranteed valid. This operates directly on the token level and requires care with token boundaries.

### 18.8 Scaling Laws
Model quality scales predictably with **parameters, training tokens, and compute**. Training dataset size is measured in **tokens** (often trillions for modern LLMs). Research on compute-optimal training suggests balancing model size and training tokens rather than only increasing size.

### 18.9 Tokens as a Training Signal
Pretraining objective for most LLMs: **next-token prediction**, minimizing cross-entropy loss between the predicted distribution and the actual next token. Related metrics:

- **Loss** (lower is better)
- **Perplexity** = exp(loss); lower means the model is less "surprised" by the text
- **Bits per byte / bits per character**: tokenizer-independent measures, useful for comparing models with different tokenizers

### 18.10 Tokenizer Design Considerations
- Vocabulary size vs. sequence length
- Coverage of target languages, code, and math
- Digit handling strategy
- Whitespace and indentation merging
- Reserved slots for future special tokens
- Normalization (Unicode forms) and pre-tokenization regex
- Compression rate: bytes per token

### 18.11 Tokenizer-Free and Alternative Approaches
Researchers are exploring models that avoid fixed subword vocabularies:

- **Byte-level models**: operate directly on bytes (very long sequences, but no vocabulary issues)
- **Dynamic patching**: group bytes into variable-sized patches based on predictability
- **Character-aware / hierarchical models**: process characters locally and words globally
- **Latent / continuous-token approaches**: predict higher-level representations rather than discrete tokens

These aim to remove tokenization artifacts but are less widespread than subword tokenization today.

### 18.12 Reasoning Tokens and Test-Time Compute
Some models spend additional tokens "thinking" before answering. More thinking tokens can improve accuracy on hard problems (math, coding, planning) at the cost of latency and money. This is called **test-time compute scaling**. Providers typically let you set a thinking/reasoning budget.

### 18.13 Long-Context Techniques
- **Position encoding extension** (RoPE scaling, YaRN, etc.) to stretch trained context lengths
- **Retrieval-Augmented Generation (RAG)**: retrieve only relevant chunks instead of stuffing everything into context
- **Summarization / compaction** of old conversation turns
- **Hierarchical memory** or external memory stores

### 18.14 Chunking for RAG
Documents are split into chunks measured in tokens (for example 200 to 1,000 tokens each, often with overlap) before embedding and indexing. Chunk size affects retrieval precision and context cost.

---

## 19. Practical Tips for Saving Tokens

1. **Be concise** in prompts. Remove filler and repeated instructions.
2. **Reuse stable prefixes** and enable prompt caching where supported.
3. **Summarize** long conversation history instead of resending everything.
4. **Use retrieval** (RAG) rather than pasting entire documents.
5. **Set sensible max output limits** and ask for brief formats when appropriate.
6. **Choose compact formats**: for example, terse JSON keys or tables may save tokens over verbose prose.
7. **Pick the right model size**: smaller models for simple tasks.
8. **Control reasoning budgets** for models with thinking modes.
9. **Strip unneeded content**: HTML boilerplate, logs, repeated headers.
10. **Measure**: count tokens before sending large requests.

---

## 20. Hands-On Code Examples

### 20.1 Counting tokens with `tiktoken` (OpenAI-style tokenizers)

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")   # pick the encoding matching your model

text = "Tokenization is fun!"
ids = enc.encode(text)

print(ids)                       # list of token IDs
print(len(ids))                  # number of tokens
print([enc.decode([i]) for i in ids])   # the individual token strings
print(enc.decode(ids))           # back to original text
```

### 20.2 Using Hugging Face tokenizers

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("bert-base-uncased")

text = "Tokenization is fun!"
encoded = tok(text)

print(encoded["input_ids"])
print(tok.convert_ids_to_tokens(encoded["input_ids"]))
print(tok.decode(encoded["input_ids"]))
```

### 20.3 Training a tiny BPE tokenizer

```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers

tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

trainer = trainers.BpeTrainer(vocab_size=500, special_tokens=["[UNK]", "[PAD]"])
tokenizer.train(files=["my_corpus.txt"], trainer=trainer)

print(tokenizer.encode("low lower lowest").tokens)
```

### 20.4 Simple BPE merge illustration (educational)

```python
from collections import Counter

def get_pairs(tokens):
    return Counter(zip(tokens, tokens[1:]))

def merge(tokens, pair):
    out, i = [], 0
    while i < len(tokens):
        if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == pair:
            out.append(tokens[i] + tokens[i+1])
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out

tokens = list("lowerlowestlow")
for _ in range(4):
    pairs = get_pairs(tokens)
    best = max(pairs, key=pairs.get)
    tokens = merge(tokens, best)
    print(best, "->", tokens)
```

### 20.5 Token counting via an API (conceptual)

Most providers offer a token-counting endpoint or library. Use it before large requests:

```python
# Pseudocode: check your provider's SDK docs for the exact method
count = client.count_tokens(model="your-model", messages=[...])
print(count)
```

### 20.6 Cost estimator

```python
def estimate_cost(input_tokens, output_tokens, in_price_per_m, out_price_per_m):
    return (input_tokens / 1_000_000) * in_price_per_m + \
           (output_tokens / 1_000_000) * out_price_per_m

print(estimate_cost(2000, 500, 3.0, 15.0))   # illustrative prices
```

---

## 21. Glossary

| Term | Definition |
|---|---|
| **Token** | Basic unit of text/data processed by a model |
| **Tokenizer** | Component that converts text to tokens and back |
| **Vocabulary** | The set of all tokens a model knows |
| **Token ID** | Integer identifying a token in the vocabulary |
| **Subword** | A token that is part of a word |
| **BPE** | Byte Pair Encoding, merges frequent pairs |
| **Embedding** | Vector representation of a token |
| **Context window** | Max tokens the model can process at once |
| **Logits** | Raw scores over the vocabulary before softmax |
| **Softmax** | Converts logits to probabilities |
| **Temperature** | Controls randomness of sampling |
| **Top-k / Top-p** | Sampling restrictions |
| **EOS** | End-of-sequence token |
| **KV cache** | Stored attention keys/values for previous tokens |
| **Prefill / Decode** | Processing the prompt vs generating output |
| **Perplexity** | Measure of how well a model predicts text |
| **Fertility** | Average tokens per word for a tokenizer and language |
| **RAG** | Retrieval-Augmented Generation |
| **Reasoning tokens** | Tokens used for internal thinking before the answer |

---

## 22. Quick Summary

- A **token** is the unit of text a model reads and writes: usually a word, part of a word, or a symbol.
- Text is split by a **tokenizer** (BPE, WordPiece, Unigram, etc.), mapped to **IDs**, then to **embeddings**.
- Models **predict the next token** repeatedly to generate text.
- In English, **1 token ≈ 4 characters ≈ ¾ word**, but this varies by language, content, and tokenizer.
- The **context window** limits total tokens (input + output + reasoning).
- **Billing, speed, and memory** all depend on token counts.
- Tokenization causes quirks: letter counting, arithmetic, multilingual inefficiency, and boundary effects.
- Advanced efficiency ideas include **KV caching, prompt caching, speculative decoding, sparse attention, and RAG**.
- Research continues on **tokenizer-free** and more efficient representations.

---
