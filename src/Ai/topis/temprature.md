# Temperature in Agentic AI

In the realm of Artificial Intelligence, particularly Large Language Models (LLMs) and Agentic AI, **Temperature** is a critical hyperparameter that dictates the randomness, creativity, and determinism of the model's output. Understanding how to manipulate temperature is essential for building effective, reliable, and purpose-driven AI agents.


## 1. What is Temperature?

At its core, temperature is a setting that controls how an AI model selects the next word (or "token") in a sequence. 

When an LLM processes a prompt, it doesn't just produce a single guaranteed word. Instead, it generates a list of possible next words, each with an associated probability. 
*   **Low Temperature (e.g., 0.0 - 0.2):** Makes the model strictly choose the most probable next word. The output becomes highly deterministic, predictable, and focused.
*   **High Temperature (e.g., 0.8 - 1.0+):** Flattens the probability distribution. The model is more likely to choose less probable words, resulting in more creative, varied, and sometimes unpredictable or hallucinatory outputs.
