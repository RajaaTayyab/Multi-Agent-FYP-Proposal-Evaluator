"""
orchestrator.py — Sequential orchestration (Part A).
Coordinates four specialists: Technical, Novelty, Feasibility, Ethics.
The orchestrator NEVER does domain work — only extracts, dispatches, detects, synthesises.
"""

import os, time
from groq import Groq
from dotenv import load_dotenv
from agents import (
    run_technical_reviewer,
    run_novelty_assessor,
    run_feasibility_analyst,
    run_ethics_reviewer,
)

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL  = 'llama-3.1-8b-instant'

# ── Section Extraction — Agent Isolation ─────────────────────────────────────

def extract_proposal_sections(proposal: dict) -> dict:
    """
    Extract isolated sections for each specialist.
    Each agent gets ONLY what it needs — no cross-contamination.
    """
    title       = proposal.get('title', '')
    problem     = proposal.get('problem_statement', '')
    tech_desc   = proposal.get('technical_description', '')
    tech_stack  = proposal.get('technology_stack', '')
    months      = proposal.get('proposed_months', 6)
    team        = proposal.get('team_size', 2)
    deliverables= proposal.get('deliverables_count', 3)

    return {
        # Technical Reviewer — technical fields only, no timeline/team/problem
        'technical': (
            f'Title: {title}\n'
            f'Technical Description: {tech_desc}\n'
            f'Technology Stack: {tech_stack}'
        ),

        # Novelty Assessor — title + problem ONLY (no tech details)
        'novelty_title':   title,
        'novelty_problem': problem,

        # Feasibility Analyst — numbers + scope, no tech or literature
        'feasibility_months':      months,
        'feasibility_team':        team,
        'feasibility_deliverables': deliverables,
        'feasibility_scope':       f'{title}. {tech_desc[:200]}',

        # Ethics Reviewer — problem + technical description (full ethical context)
        'ethics': (
            f'Title: {title}\n'
            f'Problem Statement: {problem}\n'
            f'Technical Description: {tech_desc}'
        ),
    }


# ── Conflict Detection ────────────────────────────────────────────────────────

def detect_conflicts(tech_report: dict, novelty_report: dict,
                     feasibility_report: dict, ethics_report: dict) -> list[str]:
    """
    Detect disagreements between specialist reports.
    Returns list of conflict descriptions. Empty list = no conflicts.
    """
    conflicts = []

    tech_text        = tech_report.get('assessment', '').lower()
    feasibility_text = feasibility_report.get('feasibility_verdict', '').lower()
    novelty_text     = novelty_report.get('assessment', '').lower()
    ethics_text      = ethics_report.get('assessment', '').lower()
    ethics_flagged   = ethics_report.get('ethics_flagged', False)

    # Conflict 1: Technical enthusiasm vs Feasibility concern
    tech_positive = any(w in tech_text for w in ['excellent', 'strong', 'impressive', 'well-designed', 'robust'])
    feas_negative = any(w in feasibility_text for w in ['unrealistic', 'risky', 'tight', 'insufficient', 'understaffed'])
    if tech_positive and feas_negative:
        conflicts.append(
            'CONFLICT: Technical Reviewer is enthusiastic about the design, '
            'but Feasibility Analyst flags delivery risks. Strong technical '
            'vision may not be achievable within proposed constraints.'
        )

    # Conflict 2: High novelty claim vs Many existing systems found
    novelty_high = any(w in novelty_text for w in ['highly novel', 'significant gap', 'no existing', 'unique'])
    novelty_low_tools = any(r.get('result', {}).get('novelty_score', 10) <= 3
                            for r in novelty_report.get('tool_results', []))
    if novelty_high and novelty_low_tools:
        conflicts.append(
            'CONFLICT: Novelty Assessor claims high novelty in final assessment, '
            'but tool results found multiple existing solutions. Review novelty claims carefully.'
        )

    # Conflict 3 (Graded Task 1): Technical enthusiasm vs Ethics flag
    if tech_positive and ethics_flagged:
        conflicts.append(
            'CONFLICT: Technical Reviewer is enthusiastic about a system that the '
            'Ethics Reviewer has flagged as HIGH RISK. Strong technical implementation '
            'does not mitigate ethical concerns — deployment may face regulatory or '
            'societal barriers despite technical merit.'
        )

    # Conflict 4: Ethics flag vs Novelty high (high-risk novel systems)
    ethics_high_risk = 'ETHICS FLAGGED' in ethics_report.get('ethics_verdict', '')
    novelty_score_high = any(r.get('result', {}).get('novelty_score', 0) >= 7
                             for r in novelty_report.get('tool_results', []))
    if ethics_high_risk and novelty_score_high:
        conflicts.append(
            'CONFLICT: System is novel but also ethically high-risk. '
            'Novelty alone does not justify deployment — ethics review must be resolved first.'
        )

    return conflicts


# ── Orchestrator Synthesis ────────────────────────────────────────────────────

ORCHESTRATOR_SYNTHESIS_PROMPT = """
You are an FYP evaluation orchestrator. You have received reports from four specialist agents.
Your job is coordination and synthesis ONLY — do not add new domain judgments.

Synthesise a unified evaluation that includes:
1. OVERALL VERDICT: STRONG / ACCEPTABLE / NEEDS REVISION / REJECTED
2. TOP 3 STRENGTHS (cite which specialist identified each)
3. TOP 3 CONCERNS (include ethics concerns if ethics agent flagged them — these take priority)
4. FINAL RECOMMENDATIONS (3 concrete action items for the student team)

Ethics concerns, if flagged, MUST appear in TOP 3 CONCERNS regardless of other findings.
Base your synthesis ONLY on the specialist reports provided. Do not invent new assessments.
"""


def synthesise_reports(tech: dict, novelty: dict, feasibility: dict,
                        ethics: dict, conflicts: list[str]) -> str:
    """Call LLM to synthesise all four specialist reports into unified evaluation."""
    summary = (
        f'TECHNICAL REVIEWER REPORT:\n{tech.get("assessment", "")}\n\n'
        f'NOVELTY ASSESSOR REPORT:\n{novelty.get("assessment", "")}\n\n'
        f'FEASIBILITY ANALYST REPORT:\n{feasibility.get("feasibility_verdict", "")}\n\n'
        f'ETHICS REVIEWER REPORT:\n{ethics.get("assessment", "")}\n'
        f'Ethics Verdict: {ethics.get("ethics_verdict", "UNKNOWN")}\n\n'
        f'CONFLICTS DETECTED:\n' + ('\n'.join(conflicts) if conflicts else 'None') + '\n\n'
        f'Synthesise a unified evaluation following the format in your instructions.'
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': ORCHESTRATOR_SYNTHESIS_PROMPT},
            {'role': 'user',   'content': summary},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


# ── Sequential Orchestration (Part A) ────────────────────────────────────────

def run_sequential_evaluation(proposal: dict) -> dict:
    """
    Run all four specialists sequentially then synthesise.
    Total time ≈ sum of all agent times.
    """
    start_time = time.time()
    sections   = extract_proposal_sections(proposal)

    # Sequential dispatch — one by one
    tech_report        = run_technical_reviewer(sections['technical'])
    novelty_report     = run_novelty_assessor(sections['novelty_title'], sections['novelty_problem'])
    feasibility_report = run_feasibility_analyst(
        sections['feasibility_months'],
        sections['feasibility_team'],
        sections['feasibility_deliverables'],
        sections['feasibility_scope'],
    )
    ethics_report      = run_ethics_reviewer(sections['ethics'])

    conflicts         = detect_conflicts(tech_report, novelty_report, feasibility_report, ethics_report)
    final_evaluation  = synthesise_reports(tech_report, novelty_report, feasibility_report, ethics_report, conflicts)
    execution_time    = round(time.time() - start_time, 2)

    return {
        'execution_mode':   'sequential',
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
