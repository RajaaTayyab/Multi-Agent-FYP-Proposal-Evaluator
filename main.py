"""
main.py — FastAPI entrypoint. Do NOT modify for Graded Task 1.
Endpoints:
  GET  /health              — system status and agent list
  POST /evaluate            — sequential evaluation (Part A)
  POST /evaluate/parallel   — parallel evaluation (Part B)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator import run_sequential_evaluation
from orchestrator_async import run_parallel_evaluation

app = FastAPI(title='FYP Multi-Agent Evaluator', version='2.0')


# ── Request Schema ────────────────────────────────────────────────────────────

class FYPProposal(BaseModel):
    title:                   str
    problem_statement:       str
    technical_description:   str
    technology_stack:        str
    proposed_months:         int = 6
    team_size:               int = 2
    deliverables_count:      int = 3


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get('/health')
def health():
    return {
        'status':       'ok',
        'architecture': 'Hub and Spoke — Orchestrator + 4 Specialists',
        'agents': {
            'orchestrator':        'Coordination and synthesis only — no domain work',
            'technical_reviewer':  'Reflection pattern (Lab 07)',
            'novelty_assessor':    'Tool Use pattern (Lab 08)',
            'feasibility_analyst': 'ReAct pattern (Lab 06)',
            'ethics_reviewer':     'Reflection pattern (Graded Task 1)',
        },
    }


@app.post('/evaluate')
def evaluate(proposal: FYPProposal):
    """Sequential evaluation — Part A."""
    if not proposal.title.strip():
        raise HTTPException(status_code=400, detail='title cannot be empty')
    return run_sequential_evaluation(proposal.model_dump())


@app.post('/evaluate/parallel')
async def evaluate_parallel(proposal: FYPProposal):
    """Parallel evaluation — Part B."""
    if not proposal.title.strip():
        raise HTTPException(status_code=400, detail='title cannot be empty')
    return await run_parallel_evaluation(proposal.model_dump())
