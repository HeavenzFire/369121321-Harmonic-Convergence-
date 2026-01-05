import math
import time

def forward_probability(last_seen: float, lam: float = 0.01) -> float:
    """
    Calculate probability of forwarding content based on delay-tolerant gossip.
    P(forward) = 1 if unseen, exp(-λt) if seen
    """
    if last_seen == 0:  # unseen
        return 1.0
    t = time.time() - last_seen
    return math.exp(-lam * t)