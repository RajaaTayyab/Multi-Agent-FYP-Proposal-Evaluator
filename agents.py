"""
agents.py — Four specialist agents. Each uses a different internal pattern.
  Technical Reviewer  → Reflection Pattern  (Lab 07)
  Novelty Assessor    → Tool Use Pattern    (Lab 08)
  Feasibility Analyst → ReAct Pattern       (Lab 06)
  Ethics Reviewer     → Reflection Pattern  (Graded Task 1)
"""

import os, json, re
from groq import Groq
from dotenv import load_dotenv
from tools import (
    search_literature, check_existing_systems,
    check_timeline_realism, check_team_scope_fit,
)

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL  = 'llama-3.1-8b-instant'


def _llm(system: str, user: str, max_tokens: int = 1024) -> str:
    """Single LLM call — shared by all agents."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': user},
        ],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


# ── Agent 1: Technical Reviewer (Reflection Pattern) ─────────────────────────

TECH_GENERATOR_SYSTEM = """
You are an expert software engineering professor reviewing an FYP technical proposal.
Evaluate the technical merit, architecture choices, technology stack appropriateness,
and implementation feasibility.
Write a structured technical assessment covering:
- Architecture and design quality
- Technology stack suitability
- Technical risks and challenges
- Implementation complexity
Be specific and technical. Return your assessment in plain text.
"""

TECH_CRITIC_SYSTEM = """
You are a senior technical reviewer checking a technical assessment of an FYP proposal.
Check whether the assessment:
1. Addresses architecture and design concretely
2. Justifies the technology stack with reasoning
3. Identifies specific technical risks (not vague ones)
4. Evaluates implementation complexity realistically

If all four criteria are fully addressed, respond with exactly:
ASSESSMENT APPROVED

Otherwise, write specific improvements needed. Be concise.
"""


def run_technical_reviewer(proposal_text: str) -> dict:
    """
    Technical Reviewer using Reflection Pattern.
    Generator writes assessment → Critic reviews → Generator revises (max 2 rounds).
    Receives: title + technical_description + technology_stack ONLY (isolation).
    """
    assessment = _llm(TECH_GENERATOR_SYSTEM, f'Review this FYP technical proposal:\n\n{proposal_text}')
    reflection_rounds = 0
    critic_approved   = False

    for _ in range(2):
        critique = _llm(
            TECH_CRITIC_SYSTEM,
            f'Proposal:\n{proposal_text}\n\nAssessment to review:\n{assessment}',
            max_tokens=512,
        )
        reflection_rounds += 1

        if 'ASSESSMENT APPROVED' in critique:
            critic_approved = True
            break

        # Revise based on critique
        assessment = _llm(
            TECH_GENERATOR_SYSTEM,
            f'Original proposal:\n{proposal_text}\n\nYour previous assessment:\n{assessment}\n\nCritique:\n{critique}\n\nRevise your assessment to address the critique.',
        )

    return {
        'assessment':        assessment,
        'reflection_rounds': reflection_rounds,
        'critic_approved':   critic_approved,
        'pattern':           'Reflection (Lab 07)',
    }


# ── Agent 2: Novelty Assessor (Tool Use Pattern) ─────────────────────────────

NOVELTY_TOOL_SCHEMAS = [
    {
        'type': 'function',
        'function': {
            'name': 'search_literature',
            'description': 'Search academic literature database for papers related to the FYP topic. Call this first to assess research novelty.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'keywords': {'type': 'string', 'description': 'Search keywords from the problem statement'},
                },
                'required': ['keywords'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'check_existing_systems',
            'description': 'Check existing production systems and solutions in the domain. Call after literature search to assess market novelty.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'domain': {'type': 'string', 'description': 'The application domain, e.g. chatbot, early warning, machine learning'},
                },
                'required': ['domain'],
            },
        },
    },
]

NOVELTY_TOOL_FUNCTIONS = {
    'search_literature':    search_literature,
    'check_existing_systems': check_existing_systems,
}

NOVELTY_SYSTEM = """
You are a research novelty assessor evaluating FYP proposals.
Use your tools to assess novelty:
1. Call search_literature to find relevant academic papers
2. Call check_existing_systems to find existing solutions
3. Synthesise both results into a novelty verdict

Always call BOTH tools before giving your final assessment.
Your final assessment must include: novelty level (HIGH/MEDIUM/LOW), justification, and key gaps identified.
"""


def run_novelty_assessor(title: str, problem_statement: str) -> dict:
    """
    Novelty Assessor using Tool Use Pattern.
    Receives: title + problem_statement ONLY (isolation).
    """
    messages = [
        {'role': 'system', 'content': NOVELTY_SYSTEM},
        {'role': 'user',   'content': f'Assess the novelty of this FYP:\nTitle: {title}\nProblem: {problem_statement}'},
    ]
    tools_called  = []
    tool_results  = []

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=NOVELTY_TOOL_SCHEMAS,
            tool_choice='auto',
            temperature=0.2,
            max_tokens=1024,
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return {
                'assessment':   message.content,
                'tools_called': tools_called,
                'tool_results': tool_results,
                'pattern':      'Tool Use (Lab 08)',
            }

        messages.append({'role': 'assistant', 'content': None, 'tool_calls': message.tool_calls})

        for tc in message.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            func = NOVELTY_TOOL_FUNCTIONS.get(name)
            result = func(**args) if func else {'error': f'Unknown tool: {name}'}

            tools_called.append(name)
            tool_results.append({'tool': name, 'args': args, 'result': result})

            messages.append({
                'role':         'tool',
                'tool_call_id': tc.id,
                'content':      json.dumps(result),
            })

    return {
        'assessment':   'Max turns reached without final assessment.',
        'tools_called': tools_called,
        'tool_results': tool_results,
        'pattern':      'Tool Use (Lab 08)',
    }


# ── Agent 3: Feasibility Analyst (ReAct Pattern) ─────────────────────────────

FEASIBILITY_REACT_SYSTEM = """
You are a project feasibility analyst for FYP proposals.
Use THOUGHT/ACTION/OBSERVATION format to reason step by step.

Available actions (call exactly as shown):
- check_timeline_realism(proposed_months=N, deliverables_count=N, scope_description="text")
- check_team_scope_fit(team_size=N, scope_description="text")

Format:
THOUGHT: What should I check first?
ACTION: check_timeline_realism(proposed_months=8, deliverables_count=5, scope_description="ML web app")
OBSERVATION: {paste tool result here}
THOUGHT: What does this tell me?
ACTION: check_team_scope_fit(team_size=3, scope_description="ML web app")
OBSERVATION: {paste tool result here}
THOUGHT: I have both results. Here is my conclusion.
FINAL ANSWER: <your feasibility verdict>

You MUST call both tools. You MUST end with FINAL ANSWER.
"""


def _parse_react_actions(text: str) -> list[dict]:
    """Extract ACTION calls from ReAct trace."""
    actions = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('ACTION:'):
            actions.append({'action': line.replace('ACTION:', '').strip()})
    return actions


def _execute_react_tool(action_text: str, months: int, team: int, deliverables: int, scope: str) -> str:
    """Execute tool referenced in ReAct ACTION line."""
    if 'check_timeline_realism' in action_text:
        result = check_timeline_realism(months, deliverables, scope)
    elif 'check_team_scope_fit' in action_text:
        result = check_team_scope_fit(team, scope)
    else:
        result = {'error': 'Unknown tool'}
    return json.dumps(result)


def run_feasibility_analyst(proposed_months: int, team_size: int,
                             deliverables_count: int, scope_description: str) -> dict:
    """
    Feasibility Analyst using ReAct Pattern.
    Receives: timeline + team numbers + scope ONLY (isolation).
    """
    user_query = (
        f'Assess feasibility:\n'
        f'Proposed months: {proposed_months}\n'
        f'Team size: {team_size}\n'
        f'Deliverables: {deliverables_count}\n'
        f'Scope: {scope_description}'
    )

    messages = [
        {'role': 'system', 'content': FEASIBILITY_REACT_SYSTEM},
        {'role': 'user',   'content': user_query},
    ]

    reasoning_trace = []
    react_turns     = 0
    final_answer    = ''

    for _ in range(6):
        response  = _llm(FEASIBILITY_REACT_SYSTEM, '\n'.join(
            [m['content'] for m in messages if m.get('content')]
        ))
        react_turns += 1
        reasoning_trace.append(response)

        if 'FINAL ANSWER' in response:
            # Extract final answer
            parts = response.split('FINAL ANSWER:')
            final_answer = parts[-1].strip() if len(parts) > 1 else response
            break

        # Execute any tool calls found in response
        actions = _parse_react_actions(response)
        observations = []
        for act in actions:
            obs = _execute_react_tool(
                act['action'], proposed_months, team_size, deliverables_count, scope_description
            )
            observations.append(f'OBSERVATION: {obs}')

        # Append response + observations to continue loop
        messages.append({'role': 'assistant', 'content': response})
        if observations:
            messages.append({'role': 'user', 'content': '\n'.join(observations) + '\nContinue your reasoning.'})

    return {
        'feasibility_verdict': final_answer or 'See reasoning trace.',
        'reasoning_trace':     '\n\n---\n\n'.join(reasoning_trace),
        'react_turns':         react_turns,
        'pattern':             'ReAct (Lab 06)',
    }


# ── Agent 4: Ethics Reviewer (Reflection Pattern) — Graded Task 1 ────────────

ETHICS_GENERATOR_SYSTEM = """
You are an AI ethics expert reviewing FYP proposals for responsible AI concerns.
Evaluate the proposal across these five dimensions:
1. Data Privacy — What personal data is collected? How is it protected? GDPR/PDPA compliance?
2. Potential Misuse or Harm — Could this system be weaponised, abused, or cause unintended harm?
3. Fairness and Bias Risks — Does training data or system design risk discriminating against groups?
4. Pakistan-Specific Ethical Considerations — Local legal context, cultural sensitivities, vulnerable communities?
5. Responsible AI Compliance — Transparency, explainability, human oversight, right to appeal?

For each dimension, give a verdict: LOW RISK / MEDIUM RISK / HIGH RISK with justification.
End with an overall ethics verdict: ETHICS APPROVED / ETHICS CONCERNS / ETHICS FLAGGED (high risk).
"""

ETHICS_CRITIC_SYSTEM = """
You are a senior AI ethics board member reviewing an ethics assessment of an FYP proposal.
Check whether the assessment:
1. Addresses all five dimensions (data privacy, misuse, fairness, Pakistan-specific, responsible AI)
2. Gives specific risk levels (not vague) with concrete justification
3. Identifies the most serious ethical concern clearly
4. Provides actionable mitigation recommendations
5. Ends with a clear overall verdict (ETHICS APPROVED / ETHICS CONCERNS / ETHICS FLAGGED)

If all five criteria are fully addressed, respond with exactly:
ASSESSMENT APPROVED

Otherwise, write specific improvements needed.
"""


def run_ethics_reviewer(proposal_text: str) -> dict:
    """
    Ethics Reviewer using Reflection Pattern (Graded Task 1).
    Receives: problem_statement + technical_description (full ethical context).
    Uses same Generator-Critic-Revise loop as Technical Reviewer.
    """
    assessment = _llm(
        ETHICS_GENERATOR_SYSTEM,
        f'Review the ethics and responsible AI aspects of this FYP proposal:\n\n{proposal_text}',
    )
    reflection_rounds = 0
    critic_approved   = False
    ethics_flagged    = False

    for _ in range(2):
        critique = _llm(
            ETHICS_CRITIC_SYSTEM,
            f'Proposal:\n{proposal_text}\n\nEthics assessment to review:\n{assessment}',
            max_tokens=512,
        )
        reflection_rounds += 1

        if 'ASSESSMENT APPROVED' in critique:
            critic_approved = True
            break

        assessment = _llm(
            ETHICS_GENERATOR_SYSTEM,
            f'Original proposal:\n{proposal_text}\n\nYour previous ethics assessment:\n{assessment}\n\nCritique:\n{critique}\n\nRevise your assessment to address all critique points.',
        )

    # Determine risk level from final assessment
    assessment_upper = assessment.upper()
    if 'ETHICS FLAGGED' in assessment_upper:
        ethics_verdict = 'ETHICS FLAGGED'
        ethics_flagged = True
    elif 'ETHICS CONCERNS' in assessment_upper:
        ethics_verdict = 'ETHICS CONCERNS'
    else:
        ethics_verdict = 'ETHICS APPROVED'

    return {
        'assessment':        assessment,
        'ethics_verdict':    ethics_verdict,
        'ethics_flagged':    ethics_flagged,
        'reflection_rounds': reflection_rounds,
        'critic_approved':   critic_approved,
        'pattern':           'Reflection (Graded Task 1)',
    }
