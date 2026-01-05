import numpy as np
import random
from typing import List, Dict, Any, Callable
from utils.logger import save_json, save_csv, timestamp
from utils.checkpoint import save_checkpoint
from utils.visualization import generate_population_data, generate_fitness_history

class MetaEvolutionaryAlgorithm:
    """Algorithm that evolves its own parameters"""

    def __init__(self, base_algorithm: Callable, fitness_func: Callable):
        self.base_algorithm = base_algorithm
        self.fitness_func = fitness_func

        # Meta-parameters to evolve
        self.meta_params = {
            'population_size': 50,
            'mutation_rate': 0.1,
            'crossover_rate': 0.8,
            'tournament_size': 3,
            'elitism_rate': 0.1
        }

    def evaluate_meta_params(self, meta_params: Dict[str, float], test_generations: int = 20) -> float:
        """Evaluate how well a set of meta-parameters performs"""
        # Run base algorithm with these parameters
        try:
            results = self.base_algorithm(
                fitness_func=self.fitness_func,
                population_size=int(meta_params['population_size']),
                mutation_rate=meta_params['mutation_rate'],
                crossover_rate=meta_params['crossover_rate'],
                tournament_size=int(meta_params['tournament_size']),
                elitism_rate=meta_params['elitism_rate'],
                generations=test_generations
            )

            # Meta-fitness: combination of convergence speed and final fitness
            final_fitness = results.get('final_best_fitness', 0)
            convergence_speed = len(results.get('fitness_history', {}).get('fitness', []))
            if convergence_speed > 0:
                improvement_rate = (final_fitness - results['fitness_history']['fitness'][0]) / convergence_speed
            else:
                improvement_rate = 0

            return final_fitness + improvement_rate  # Meta-fitness

        except Exception as e:
            return -1000  # Penalize failed runs

    def mutate_meta_params(self, params: Dict[str, float]) -> Dict[str, float]:
        """Mutate meta-parameters"""
        mutated = params.copy()

        # Mutate each parameter with bounds
        param_bounds = {
            'population_size': (10, 200),
            'mutation_rate': (0.01, 0.5),
            'crossover_rate': (0.1, 1.0),
            'tournament_size': (2, 10),
            'elitism_rate': (0.0, 0.5)
        }

        for param, bounds in param_bounds.items():
            if random.random() < 0.2:  # 20% mutation rate for meta-params
                if param == 'population_size' or param == 'tournament_size':
                    mutated[param] = int(np.clip(
                        mutated[param] + random.randint(-5, 5),
                        bounds[0], bounds[1]
                    ))
                else:
                    mutated[param] += random.gauss(0, 0.05)
                    mutated[param] = np.clip(mutated[param], bounds[0], bounds[1])

        return mutated

def run_meta_evolution(base_algorithm: Callable,
                      fitness_func: Callable,
                      meta_population_size: int = 10,
                      meta_generations: int = 20) -> Dict[str, Any]:
    """Run meta-evolution to optimize evolutionary algorithm parameters"""

    run_id = f"meta_evolution_{timestamp()}"

    meta_ea = MetaEvolutionaryAlgorithm(base_algorithm, fitness_func)

    # Initialize meta-population
    meta_population = []
    for _ in range(meta_population_size):
        params = {
            'population_size': random.randint(20, 100),
            'mutation_rate': random.uniform(0.05, 0.3),
            'crossover_rate': random.uniform(0.5, 0.9),
            'tournament_size': random.randint(2, 5),
            'elitism_rate': random.uniform(0.0, 0.2)
        }
        fitness = meta_ea.evaluate_meta_params(params)
        meta_population.append({
            'params': params,
            'fitness': fitness
        })

    best_meta_fitness_history = []

    for gen in range(meta_generations):
        # Evaluate all meta-individuals
        for individual in meta_population:
            individual['fitness'] = meta_ea.evaluate_meta_params(individual['params'])

        # Sort by meta-fitness
        meta_population.sort(key=lambda x: x['fitness'], reverse=True)

        # Track history
        best_meta_fitness = meta_population[0]['fitness']
        best_meta_fitness_history.append(best_meta_fitness)

        # Create next meta-generation
        new_meta_population = meta_population[:meta_population_size//2]  # Elitism

        while len(new_meta_population) < meta_population_size:
            # Select parents
            parent1 = random.choice(meta_population[:meta_population_size//2])
            parent2 = random.choice(meta_population[:meta_population_size//2])

            # Crossover (blend)
            child_params = {}
            for key in parent1['params']:
                child_params[key] = (parent1['params'][key] + parent2['params'][key]) / 2

            # Mutate
            child_params = meta_ea.mutate_meta_params(child_params)

            # Evaluate
            fitness = meta_ea.evaluate_meta_params(child_params)
            new_meta_population.append({
                'params': child_params,
                'fitness': fitness
            })

        meta_population = new_meta_population

        # Checkpoint every 5 generations
        if gen % 5 == 0:
            save_checkpoint(meta_population, f"{run_id}_meta_gen_{gen}")

    # Get best meta-parameters
    best_meta_params = meta_population[0]['params']

    # Run final evaluation with best parameters
    final_results = base_algorithm(
        fitness_func=fitness_func,
        population_size=int(best_meta_params['population_size']),
        mutation_rate=best_meta_params['mutation_rate'],
        crossover_rate=best_meta_params['crossover_rate'],
        tournament_size=int(best_meta_params['tournament_size']),
        elitism_rate=best_meta_params['elitism_rate'],
        generations=100  # Full run
    )

    # Save artifacts
    artifacts = {
        "run_id": run_id,
        "algorithm": "meta_evolution",
        "meta_generations": meta_generations,
        "meta_population_size": meta_population_size,
        "best_meta_params": best_meta_params,
        "best_meta_fitness": best_meta_fitness_history[-1],
        "meta_fitness_history": generate_fitness_history(best_meta_fitness_history),
        "final_algorithm_results": final_results
    }

    save_json(artifacts, f"{run_id}_results.json")

    # CSV for meta-parameter evolution
    csv_data = []
    for i, p in enumerate(meta_population):
        csv_data.append({
            "individual": i,
            "meta_fitness": p['fitness'],
            "population_size": p['params']['population_size'],
            "mutation_rate": p['params']['mutation_rate'],
            "crossover_rate": p['params']['crossover_rate'],
            "tournament_size": p['params']['tournament_size'],
            "elitism_rate": p['params']['elitism_rate']
        })
    save_csv(csv_data, f"{run_id}_meta_population.csv",
             ["individual", "meta_fitness", "population_size", "mutation_rate",
              "crossover_rate", "tournament_size", "elitism_rate"])

    return artifacts