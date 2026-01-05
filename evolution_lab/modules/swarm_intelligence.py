import numpy as np
import os
from utils.logger import save_json, save_csv, timestamp
from utils.checkpoint import save_checkpoint

def fitness_function(x, y):
    # Ackley function
    return -20 * np.exp(-0.2 * np.sqrt(0.5 * (x**2 + y**2))) - np.exp(0.5 * (np.cos(2*np.pi*x) + np.cos(2*np.pi*y))) + np.e + 20

def run_cli(agents=50, iterations=1000):
    # PSO parameters
    w = 0.7  # inertia
    c1 = 1.4  # personal
    c2 = 1.4  # global
    swarm = []
    for i in range(agents):
        x = np.random.uniform(-5, 5)
        y = np.random.uniform(-5, 5)
        vx = np.random.uniform(-1, 1)
        vy = np.random.uniform(-1, 1)
        fitness = fitness_function(x, y)
        swarm.append({
            "x": x, "y": y, "vx": vx, "vy": vy,
            "pbest_x": x, "pbest_y": y, "pbest_fitness": fitness,
            "fitness": fitness
        })
    gbest_x = min(swarm, key=lambda p: p["fitness"])["x"]
    gbest_y = min(swarm, key=lambda p: p["fitness"])["y"]
    gbest_fitness = min(swarm, key=lambda p: p["fitness"])["fitness"]
    trajectory = []
    for i in range(iterations):
        for p in swarm:
            # Update velocity
            r1 = np.random.rand()
            r2 = np.random.rand()
            p["vx"] = w * p["vx"] + c1 * r1 * (p["pbest_x"] - p["x"]) + c2 * r2 * (gbest_x - p["x"])
            p["vy"] = w * p["vy"] + c1 * r1 * (p["pbest_y"] - p["y"]) + c2 * r2 * (gbest_y - p["y"])
            # Update position
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            # Clip to bounds
            p["x"] = np.clip(p["x"], -5, 5)
            p["y"] = np.clip(p["y"], -5, 5)
            # Update fitness
            p["fitness"] = fitness_function(p["x"], p["y"])
            # Update personal best
            if p["fitness"] < p["pbest_fitness"]:
                p["pbest_x"] = p["x"]
                p["pbest_y"] = p["y"]
                p["pbest_fitness"] = p["fitness"]
        # Update global best
        current_gbest = min(swarm, key=lambda p: p["fitness"])
        if current_gbest["fitness"] < gbest_fitness:
            gbest_x = current_gbest["x"]
            gbest_y = current_gbest["y"]
            gbest_fitness = current_gbest["fitness"]
        trajectory.append([{"x": p["x"], "y": p["y"], "fitness": p["fitness"]} for p in swarm])
        if i % 100 == 0:
            save_checkpoint(swarm, f"swarm_iter_{i}")
    # Save artifacts
    run_id = f"swarm_{timestamp()}"
    save_json({"trajectory": trajectory, "gbest": {"x": gbest_x, "y": gbest_y, "fitness": gbest_fitness}}, f"{run_id}.json")
    flat_data = [{"x": p["x"], "y": p["y"], "fitness": p["fitness"]} for p in swarm]
    save_csv(flat_data, f"{run_id}.csv", fieldnames=["x","y","fitness"])