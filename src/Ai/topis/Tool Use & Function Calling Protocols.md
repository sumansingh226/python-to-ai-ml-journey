### Tool Use & Function Calling Protocols

## 1. What is Tool Use in Agentic AI?
While Large Language Models (LLMs) are powerful reasoning engines, their native capabilities are restricted to generating text based on static training data. **Tool Use** (or Function Calling) bridges this gap, allowing agents to interact with the external world. Instead of just answering a question, the LLM generates a structured payload (usually JSON) that an application uses to execute an external function, such as querying a database, hitting an API, or executing code.

---

## 2. The Mechanics of Function Calling
Function calling operates on a strict request-response cycle:
* **Definition:** The developer provides the LLM with a schema (often defined via Pydantic or JSON Schema) detailing the available tools, their expected parameters, and whether those parameters are required.
* **Intent Recognition:** The LLM analyzes the user's prompt and determines if a tool is needed.
* **Generation:** The model outputs a structured JSON object containing the function name and the necessary arguments.
* **Execution:** The application (not the LLM) executes the API call using the generated parameters and returns the raw result back to the LLM to synthesize a final answer.
