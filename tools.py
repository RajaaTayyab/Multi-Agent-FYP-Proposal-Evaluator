"""
tools.py — Simulated tools for Novelty Assessor and Feasibility Analyst.
Pure functions — no knowledge of agents, orchestrator, or main.
"""

# ── Novelty Assessor Tools (Tool Use Pattern) ────────────────────────────────

LITERATURE_DB = {
    'machine learning': [
        {'title': 'Deep Learning for Predictive Analytics', 'year': 2022, 'relevance': 'high'},
        {'title': 'Neural Networks in Production Systems',  'year': 2023, 'relevance': 'medium'},
    ],
    'natural language processing': [
        {'title': 'Transformers for Low-Resource Languages', 'year': 2023, 'relevance': 'high'},
        {'title': 'BERT Fine-tuning Survey',                 'year': 2022, 'relevance': 'medium'},
    ],
    'computer vision': [
        {'title': 'Real-Time Object Detection Survey', 'year': 2023, 'relevance': 'high'},
        {'title': 'Vision Transformers in Practice',   'year': 2022, 'relevance': 'medium'},
    ],
    'chatbot': [
        {'title': 'Conversational AI: A Survey',        'year': 2021, 'relevance': 'high'},
        {'title': 'Rule-Based vs Neural Chatbots',      'year': 2020, 'relevance': 'high'},
        {'title': 'University FAQ Chatbot Design',      'year': 2022, 'relevance': 'very high'},
    ],
    'early warning': [
        {'title': 'ML-Based Flood Early Warning Systems', 'year': 2023, 'relevance': 'medium'},
        {'title': 'Satellite Data for Disaster Prediction','year': 2022, 'relevance': 'low'},
    ],
    'facial recognition': [
        {'title': 'Face Recognition Bias Study',          'year': 2023, 'relevance': 'high'},
        {'title': 'Privacy-Preserving Face Recognition',  'year': 2022, 'relevance': 'high'},
    ],
    'surveillance': [
        {'title': 'AI Surveillance Ethics Review',        'year': 2023, 'relevance': 'high'},
        {'title': 'Smart City Monitoring Systems',        'year': 2022, 'relevance': 'medium'},
    ],
    'default': [
        {'title': 'Survey of AI Applications in Software Engineering', 'year': 2023, 'relevance': 'low'},
    ],
}

EXISTING_SYSTEMS = {
    'chatbot': {
        'known_solutions': ['ChatGPT', 'Dialogflow', 'Rasa', 'Microsoft Bot Framework'],
        'gap_analysis': 'Market is saturated. Differentiation requires very specific domain focus.',
        'novelty_score': 2,
    },
    'early warning': {
        'known_solutions': ['GDACS', 'PMD Manual System', 'USGS Flood Early Warning'],
        'gap_analysis': 'Pakistan-specific AI-based cloudburst warning is a genuine research gap.',
        'novelty_score': 8,
    },
    'machine learning': {
        'known_solutions': ['Scikit-learn pipelines', 'AutoML platforms', 'MLflow'],
        'gap_analysis': 'Generic ML systems are mature. Domain-specific application may be novel.',
        'novelty_score': 5,
    },
    'facial recognition': {
        'known_solutions': ['AWS Rekognition', 'Azure Face API', 'DeepFace', 'FaceNet'],
        'gap_analysis': 'Market is highly saturated. Ethical concerns limit deployment.',
        'novelty_score': 2,
    },
    'surveillance': {
        'known_solutions': ['Milestone XProtect', 'Genetec Security Center', 'Hikvision AI'],
        'gap_analysis': 'Commercial systems well-established. Ethics and privacy concerns are primary barriers.',
        'novelty_score': 2,
    },
    'default': {
        'known_solutions': ['Various open-source alternatives'],
        'gap_analysis': 'Insufficient information to assess existing systems comprehensively.',
        'novelty_score': 5,
    },
}


def search_literature(keywords: str) -> dict:
    """Search simulated academic literature database for relevant papers."""
    keywords_lower = keywords.lower()
    found_papers = LITERATURE_DB.get('default', [])
    matched_domain = 'default'

    for domain, papers in LITERATURE_DB.items():
        if domain in keywords_lower:
            found_papers = papers
            matched_domain = domain
            break

    high_relevance = [p for p in found_papers if p['relevance'] in ('high', 'very high')]
    novelty_indicator = 'LOW' if len(high_relevance) >= 2 else 'MEDIUM' if len(high_relevance) == 1 else 'HIGH'

    return {
        'keywords_searched': keywords,
        'domain_matched':    matched_domain,
        'papers_found':      len(found_papers),
        'papers':            found_papers,
        'high_relevance_count': len(high_relevance),
        'novelty_indicator': novelty_indicator,
        'note': 'Simulated literature database — representative results only.',
    }


def check_existing_systems(domain: str) -> dict:
    """Check simulated production systems database for existing solutions."""
    domain_lower = domain.lower()
    result = EXISTING_SYSTEMS.get('default')

    for key in EXISTING_SYSTEMS:
        if key in domain_lower:
            result = EXISTING_SYSTEMS[key]
            break

    score = result['novelty_score']
    novelty_level = 'HIGH' if score >= 7 else 'MEDIUM' if score >= 4 else 'LOW'

    return {
        'domain_checked':   domain,
        'known_solutions':  result['known_solutions'],
        'gap_analysis':     result['gap_analysis'],
        'novelty_score':    score,
        'novelty_level':    novelty_level,
        'note': 'Simulated systems database — representative results only.',
    }


# ── Feasibility Analyst Tools (ReAct Pattern) ────────────────────────────────

def check_timeline_realism(proposed_months: int, deliverables_count: int, scope_description: str) -> dict:
    """Assess whether the proposed timeline is realistic for the project scope."""
    scope_lower = scope_description.lower()
    complexity_score = 3  # base

    # Adjust for tech complexity
    if any(t in scope_lower for t in ['machine learning', 'deep learning', 'neural', 'ai model']):
        complexity_score += 3
    if any(t in scope_lower for t in ['real-time', 'streaming', 'distributed']):
        complexity_score += 2
    if any(t in scope_lower for t in ['mobile', 'web', 'dashboard', 'api']):
        complexity_score += 1

    min_months_needed = max(4, deliverables_count * 1.5 + complexity_score * 0.5)
    min_months_needed = round(min_months_needed)

    if proposed_months >= min_months_needed * 1.2:
        verdict = 'COMFORTABLE'
    elif proposed_months >= min_months_needed:
        verdict = 'TIGHT'
    elif proposed_months >= min_months_needed * 0.7:
        verdict = 'RISKY'
    else:
        verdict = 'UNREALISTIC'

    return {
        'proposed_months':    proposed_months,
        'deliverables_count': deliverables_count,
        'complexity_score':   complexity_score,
        'min_months_needed':  min_months_needed,
        'verdict':            verdict,
        'explanation': f'Complexity score {complexity_score}/10. Minimum {min_months_needed} months needed for {deliverables_count} deliverables.',
    }


def check_team_scope_fit(team_size: int, scope_description: str) -> dict:
    """Assess whether the team size is appropriate for the project scope."""
    scope_lower = scope_description.lower()
    complexity_score = 3

    if any(t in scope_lower for t in ['machine learning', 'deep learning', 'neural']):
        complexity_score += 3
    if any(t in scope_lower for t in ['real-time', 'distributed', 'microservices']):
        complexity_score += 2
    if any(t in scope_lower for t in ['web', 'mobile', 'dashboard']):
        complexity_score += 1
    if any(t in scope_lower for t in ['database', 'api', 'backend']):
        complexity_score += 1

    team_capacity = team_size * 2  # simplified capacity metric

    if team_capacity >= complexity_score * 1.2:
        verdict = 'WELL_STAFFED'
    elif team_capacity >= complexity_score:
        verdict = 'ADEQUATE'
    elif team_capacity >= complexity_score * 0.7:
        verdict = 'UNDERSTAFFED'
    else:
        verdict = 'CRITICALLY_UNDERSTAFFED'

    return {
        'team_size':        team_size,
        'team_capacity':    team_capacity,
        'complexity_score': complexity_score,
        'verdict':          verdict,
        'explanation': f'Team capacity {team_capacity} vs complexity {complexity_score}. {verdict}.',
    }
