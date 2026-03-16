# weighted keyword patterns
# (phrase, score) — longer phrases score higher (more specific)
SEVERITY_KEYWORDS = {
    "Critical": [
        ("not breathing", 5),
        ("cardiac arrest", 5),
        ("heart attack", 5),
        ("no pulse", 5),
        ("unconscious", 4),
        ("drowning", 4),
        ("explosion", 5),
        ("collapsing", 4),
        ("cannot escape", 3),
        ("trapped", 3),
        ("rising fast", 3),
        ("spreading fast", 3),
        ("elderly", 3),
        ("infant", 4),
        ("pregnant", 3),
        ("child", 3),
        ("seizure", 3),
    ],
    "High": [
        ("fire", 3),
        ("flood", 2),
        ("accident", 2),
        ("injured", 3),
        ("bleeding", 3),
        ("water rising", 2),
        ("multiple people", 2),
        ("urgently", 3),
        ("serious", 2),
        ("severe", 2),
        ("cannot move", 3),
        ("broken", 2),
    ],
    "Medium": [
        ("medical", 1),
        ("help needed", 1),
        ("emergency", 1),
        ("hurt", 2),
        ("pain", 1),
        ("fell", 1),
        ("stuck", 1),
        ("sick", 1),
        ("dizzy", 1),
    ],
    "Low": [
        ("minor", 3),
        ("small", 2),
        ("contained", 3),
        ("no injuries", 4),
        ("no one hurt", 4),
        ("waterlogging", 1),
        ("slow", 1),
        ("stable", 2),
    ]
}

def classify_severity(text: str, incident_type: str = "other") -> dict:
    """
    Rule-based severity classification.
    Used when circuit breaker is OPEN or LLM call fails.

    Returns same structure as triage agent output:
    {severity, confidence, reasoning, rag_used}
    """
    text_lower = text.lower()
    scores = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    matched_keywords = []

    # score each severity level
    for severity, keywords in SEVERITY_KEYWORDS.items():
        for phrase, weight in keywords:
            if phrase in text_lower:
                scores[severity] += weight
                matched_keywords.append(f"{phrase}({severity}+{weight})")

    # boost based on incident type
    type_boosts = {
        "medical": ("Critical", 2),
        "fire":    ("High", 2),
        "flood":   ("High", 1),
        "accident":("High", 1),
    }
    if incident_type in type_boosts:
        boost_severity, boost_score = type_boosts[incident_type]
        scores[boost_severity] += boost_score

    # pick highest scoring severity
    best_severity = max(scores, key=scores.get)
    best_score = scores[best_severity]

    # if no keywords matched — default to High (safe default)
    if best_score == 0:
        return {
            "severity": "High",
            "confidence": 0.0,
            "reasoning": (
                "No keywords matched. Defaulting to High for safety. "
                "Human review recommended."
            ),
            "rag_used": False,
            "fallback_used": True
        }

    # confidence based on score — capped at 0.75
    # fallback is never as confident as LLM
    confidence = min(best_score / 10, 0.75)

    return {
        "severity": best_severity,
        "confidence": round(confidence, 2),
        "reasoning": (
            f"Rule-based classification. "
            f"Matched: {', '.join(matched_keywords[:5])}. "
            f"Score: {best_score}."
        ),
        "rag_used": False,
        "fallback_used": True
    }