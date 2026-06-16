# Multi-Agent FYP Proposal Evaluator


An enterprise-grade hub-and-spoke multi-agent system that automates the evaluation of Final Year Project proposals. A central orchestrator delegates to four isolated specialist agents  each running a distinct cognitive pattern  and synthesizes their outputs into a structured assessment report.

---

## Architecture

```
Client / API Layer
        │
        ▼
   Orchestrator  ──  Isolation · Conflict Detection · Synthesis
   ┌─────┬─────┬─────┬─────┐
   ▼     ▼     ▼     ▼
Technical  Novelty   Feasibility  Ethics
Reviewer   Assessor  Analyst      Reviewer
(Reflect)  (Tools)   (ReAct)      (Reflect)
              │           │
          Literature   Timeline &
          & Systems    Scope Tools
```

---

## Key Design Decisions

### Multi-pattern composition
Reflection, Tool Use, and ReAct patterns coexist in one ecosystem. Each agent uses the pattern best suited to its evaluation domain rather than a one-size-fits-all approach.

### Strict agent isolation
Only contextually scoped payload fields are passed to each specialist agent. This eliminates cross-agent bias and ensures independent, uncontaminated domain evaluations.

### Async concurrency
The synchronous Groq SDK is bridged to a non-blocking pipeline using `asyncio.gather()` and `ThreadPoolExecutor`, achieving a **~2.5× speedup** over sequential agent execution.

### Conflict surface detection
The orchestrator monitors for contradictory agent signals — for example, a technical greenlight alongside a critical ethics or timeline bottleneck — and surfaces these discrepancies before final report generation.

---

## Specialist Agents

| Agent | Pattern | Responsibility |
|---|---|---|
| Technical Reviewer | Reflection | Critiques implementation soundness, technology choices, and system design |
| Novelty Assessor | Tool Use | Queries literature and prior-art tools to ground originality claims |
| Feasibility Analyst | ReAct | Reasons over timeline and scope tools to validate delivery plans |
| Ethics Reviewer | Reflection | Flags data privacy, bias, and research ethics concerns |

---

## Quickstart

```bash
git clone https://github.com/your-org/fyp-evaluator
cd fyp-evaluator
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

POST a proposal JSON to `/evaluate`. The orchestrator runs all four agents concurrently and returns a structured report with per-domain scores and a synthesis section highlighting any inter-agent conflicts.

### Example request

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Federated Learning for Medical Image Segmentation",
    "abstract": "This project proposes ...",
    "methodology": "...",
    "timeline": "..."
  }'
```

### Example response structure

```json
{
  "scores": {
    "technical": 8.2,
    "novelty": 7.5,
    "feasibility": 6.8,
    "ethics": 9.0
  },
  "conflicts": [
    "Feasibility agent flagged timeline risk; Technical agent rated implementation complexity as high."
  ],
  "synthesis": "The proposal demonstrates strong technical merit and ethical grounding...",
  "recommendation": "CONDITIONAL_PASS"
}
```

---

## Project Structure

```
fyp-evaluator/
├── main.py                  # FastAPI entry point
├── orchestrator.py          # Hub: dispatches agents, detects conflicts, synthesizes
├── agents/
│   ├── technical.py         # Reflection pattern
│   ├── novelty.py           # Tool Use pattern
│   ├── feasibility.py       # ReAct pattern
│   └── ethics.py            # Reflection pattern
├── tools/
│   ├── literature_search.py
│   └── timeline_scope.py
├── models.py                # Pydantic schemas
├── requirements.txt
└── README.md
```

---

## Requirements

```
fastapi
uvicorn
groq
pydantic
python-dotenv
```

---

## Environment Variables

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

