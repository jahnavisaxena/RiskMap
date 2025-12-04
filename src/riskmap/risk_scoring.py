def calculate_score(likelihood: int, impact: int) -> int:
    """
    Calculate risk score based on likelihood and impact.
    Score = Likelihood * Impact
    """
    return likelihood * impact
