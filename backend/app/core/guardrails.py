VALID_SEVERITIES = {"Critical", "High", "Medium", "Low"}

def validate_triage_output(result: dict) -> tuple[bool, str]:
    """
    Validates triage agent output before writing to DB.
    Returns (is_valid, reason).
    """
    # severity must be one of 4 valid values
    severity = result.get("severity")
    if not severity or severity not in VALID_SEVERITIES:
        return False, f"Invalid severity: {severity}"

    # confidence must be 0.0 - 1.0
    confidence = result.get("confidence")
    if confidence is None:
        return False, "Missing confidence"
    try:
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            return False, f"Confidence out of range: {confidence}"
    except (TypeError, ValueError):
        return False, f"Invalid confidence type: {confidence}"

    # reasoning must exist and be non-empty
    reasoning = result.get("reasoning")
    if not reasoning or not str(reasoning).strip():
        return False, "Missing reasoning"

    return True, "valid"

def safe_default(reason: str) -> dict:
    """
    Returns safe default triage result when validation fails.
    Always High — never Low or Medium on failure.
    Always routes to human review (confidence=0.0).
    """
    return {
        "severity": "High",
        "confidence": 0.0,
        "reasoning": f"Guardrail triggered: {reason}. Defaulting to High.",
        "rag_used": False,
        "fallback_used": True,
        "guardrail_triggered": True
    }