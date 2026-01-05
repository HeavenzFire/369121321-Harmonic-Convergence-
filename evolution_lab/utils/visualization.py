import numpy as np
from typing import List, Dict, Any

def generate_population_data(population: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate visualization data from population"""
    if not population:
        return {"x": [], "y": [], "fitness": [], "colors": []}

    x_vals = [p.get("x", 0) for p in population]
    y_vals = [p.get("y", 0) for p in population]
    fitness_vals = [p.get("fitness", 0) for p in population]

    # Color by fitness (blue=low, red=high)
    min_fit, max_fit = min(fitness_vals), max(fitness_vals)
    if max_fit == min_fit:
        colors = ["blue"] * len(population)
    else:
        colors = []
        for f in fitness_vals:
            intensity = (f - min_fit) / (max_fit - min_fit)
            colors.append(f"rgb({int(255*intensity)},0,{int(255*(1-intensity))})")

    return {
        "x": x_vals,
        "y": y_vals,
        "fitness": fitness_vals,
        "colors": colors,
        "best_fitness": max(fitness_vals) if fitness_vals else 0,
        "avg_fitness": np.mean(fitness_vals) if fitness_vals else 0
    }

def generate_fitness_history(history: List[float]) -> Dict[str, Any]:
    """Generate fitness history data"""
    return {
        "generations": list(range(len(history))),
        "fitness": history,
        "best_so_far": [max(history[:i+1]) for i in range(len(history))]
    }