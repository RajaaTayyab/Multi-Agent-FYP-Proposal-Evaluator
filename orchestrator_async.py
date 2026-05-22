"""
orchestrator_async.py — Parallel orchestration (Part B).
Only THREE things change from orchestrator.py:
  1. Function signature: async def
  2. Three agent calls replaced by asyncio.gather()
  3. Each agent wrapped in run_agent_async() for sync→async bridge
Everything else is imported from orchestrator.py and reused unchanged.
"""

import asyncio, time
from concurrent.futures import ThreadPoolExecutor
from agents import (
    run_technical_reviewer,
    run_novelty_assessor,
    run_feasibility_analyst,
    run_ethics_reviewer,
)
from orchestrator import (
    extract_proposal_sections,
    detect_conflicts,
    synthesise_reports,
)

_executor = ThreadPoolExecutor(max_workers=4)


async def run_agent_async(func, *args):
    """
    Bridge synchronous agent functions into async context.
    Runs each agent in a thread pool so they execute concurrently.
    Necessary because the Groq SDK uses blocking HTTP calls.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args)


async def run_parallel_evaluation(proposal: dict) -> dict:
    """
    Run all four specialists in parallel using asyncio.gather().
    Total time ≈ slowest agent (not sum of all agents).
    """
    start_time = time.time()
    sections   = extract_proposal_sections(proposal)

    # All four start simultaneously
    tech_report, novelty_report, feasibility_report, ethics_report = await asyncio.gather(
        run_agent_async(run_technical_reviewer, sections['technical']),
        run_agent_async(run_novelty_assessor,   sections['novelty_title'], sections['novelty_problem']),
        run_agent_async(run_feasibility_analyst,
                        sections['feasibility_months'],
                        sections['feasibility_team'],
                        sections['feasibility_deliverables'],
                        sections['feasibility_scope']),
        run_agent_async(run_ethics_reviewer, sections['ethics']),
    )

    conflicts        = detect_conflicts(tech_report, novelty_report, feasibility_report, ethics_report)
    final_evaluation = synthesise_reports(tech_report, novelty_report, feasibility_report, ethics_report, conflicts)
    execution_time   = round(time.time() - start_time, 2)

    return {
        'execution_mode':   'parallel',
        'execution_time_s': execution_time,
        'specialist_reports': {
            'technical_reviewer':  tech_report,
            'novelty_assessor':    novelty_report,
            'feasibility_analyst': feasibility_report,
            'ethics_reviewer':     ethics_report,
        },
        'conflicts_detected': conflicts,
        'final_evaluation':   final_evaluation,
    }
