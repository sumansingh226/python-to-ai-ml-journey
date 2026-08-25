# Temperature in Agentic AI

In the realm of Artificial Intelligence, particularly Large Language Models (LLMs) and Agentic AI, **Temperature** is a critical hyperparameter that dictates the randomness, creativity, and determinism of the model's output. Understanding how to manipulate temperature is essential for building effective, reliable, and purpose-driven AI agents.


## 1. What is Temperature?

At its core, temperature is a setting that controls how an AI model selects the next word (or "token") in a sequence. 

When an LLM processes a prompt, it doesn't just produce a single guaranteed word. Instead, it generates a list of possible next words, each with an associated probability. 
*   **Low Temperature (e.g., 0.0 - 0.2):** Makes the model strictly choose the most probable next word. The output becomes highly deterministic, predictable, and focused.
*   **High Temperature (e.g., 0.8 - 1.0+):** Flattens the probability distribution. The model is more likely to choose less probable words, resulting in more creative, varied, and sometimes unpredictable or hallucinatory outputs.


## 2. How Does It Work? (The Technical Mechanism)

To understand temperature, we have to look at the **Softmax function**, which neural networks use to turn raw output scores (called *logits*) into probabilities that sum to 1.0.

The temperature parameter ($T$) is introduced into the Softmax equation by dividing the logits by $T$ before applying the exponential function.

*   **When $T = 1$:** The probabilities are unchanged. The model samples naturally based on its training.
*   **When $T < 1$ (e.g., 0.1):** Dividing by a small fraction dramatically amplifies the differences between the logits. The highest-scoring word gets a probability very close to 100%, crushing the chances of all other words. This leads to greedy, deterministic selection.
*   **When $T > 1$ (e.g., 1.5):** Dividing by a larger number reduces the differences between the logits. The probabilities become more evenly distributed, giving lower-ranked words a higher chance of being selected.
