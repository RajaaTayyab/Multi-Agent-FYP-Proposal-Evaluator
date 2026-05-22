# Multi-Agent-FYP-Proposal-Evaluator

# Agentic AI: Composed Multi-Agent Hub-and-Spoke System

[cite_start]An enterprise-grade implementation of the **Multi-Agent Design Pattern** featuring a FastAPI backend orchestration framework utilizing the Groq SDK (`llama-3.1-8b-instant`)[cite: 3]. [cite_start]This system serves as an automated **FYP Proposal Evaluator** [cite: 4][cite_start], delegating subtasks to heavily isolated specialist agents executing distinct internal cognitive patterns[cite: 4, 9].

## 🏗️ Architecture Blueprint

                        +----------------------+
                        |  Client / API Layer  |
                        +-----------+----------+
                                    |
                                    v
                        +----------------------+
                        |     Orchestrator     |
                        | (Isolation/Synthesis)|
                        +-----+---+---+---+----+
                              |   |   |   |
         +--------------------+   |   |   +--------------------+
         |                        |   +-----------------+      |
         v                        v                     v      v
+-----------------+      +-----------------+      +----------+ +----------+
| Technical Rev.  |      | Novelty Assessor|      |Feasibility| |  Ethics  |
|  (Reflection)   |      |   (Tool Use)    |      | (ReAct)  | |(Reflection)|
+-----------------+      +--------+--------+      +----+-----+ +----------+
                                  |                    |
                                  v                    v
                         +-----------------+  +-----------------+
                         | Literature &    |  | Timeline &      |
                         | Systems Tools   |  | Scope Tools     |
                         +-----------------+  +-----------------+

## ⚙️ Core Architectural Principles
* **Multi-Pattern Composition:** Integrates Reflection, Tool Use, and ReAct paradigms into one multi-agent ecosystem[cite: 11, 19].
* **Strict Agent Isolation:** Enforces unbiased domain evaluations by passing only the contextually relevant payload fields to each specialized agent[cite: 10, 53].
* **Asynchronous Concurrency:** Bridges the synchronous Groq SDK with a non-blocking `asyncio.gather()` and `ThreadPoolExecutor` pipeline, achieving a ~2.5x performance execution speedup[cite: 6, 244, 245, 258].
* **Conflict Surface Detection:** The Orchestrator monitors and catches contradictory agent claims—such as a technical greenlight alongside a severe ethical or timeline bottleneck[cite: 47, 271].

---


python -m pip install -r requirements.txt
