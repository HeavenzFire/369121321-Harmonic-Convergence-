def node_score(uptime: float, storage: float, energy: float,
               alpha: float = 0.5, beta: float = 0.4, gamma: float = 0.3) -> float:
    """
    Calculate node score for mesh routing.
    Score = α·Uptime + β·Storage - γ·EnergyCost
    """
    return alpha * uptime + beta * storage - gamma * energy