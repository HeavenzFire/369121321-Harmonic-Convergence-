import numpy as np
import random
from typing import List, Dict, Any, Tuple
from utils.logger import save_json, save_csv, timestamp
from utils.checkpoint import save_checkpoint
from utils.visualization import generate_population_data, generate_fitness_history

class SimpleNeuralNetwork:
    """Simple feedforward neural network"""

    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int):
        self.layers = []
        self.input_size = input_size
        self.output_size = output_size

        # Build layers
        layer_sizes = [input_size] + hidden_sizes + [output_size]
        for i in range(len(layer_sizes) - 1):
            self.layers.append({
                'weights': np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.1,
                'biases': np.zeros(layer_sizes[i+1])
            })

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        for layer in self.layers:
            x = np.tanh(np.dot(x, layer['weights']) + layer['biases'])
        return x

    def get_params(self) -> np.ndarray:
        """Get flattened parameters"""
        params = []
        for layer in self.layers:
            params.extend(layer['weights'].flatten())
            params.extend(layer['biases'].flatten())
        return np.array(params)

    def set_params(self, params: np.ndarray) -> None:
        """Set parameters from flattened array"""
        idx = 0
        for layer in self.layers:
            w_shape = layer['weights'].shape
            w_size = np.prod(w_shape)
            layer['weights'] = params[idx:idx+w_size].reshape(w_shape)
            idx += w_size

            b_size = len(layer['biases'])
            layer['biases'] = params[idx:idx+b_size]
            idx += b_size

    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.1) -> None:
        """Mutate network parameters"""
        params = self.get_params()
        mask = np.random.rand(len(params)) < mutation_rate
        params[mask] += np.random.randn(np.sum(mask)) * mutation_strength
        self.set_params(params)

def xor_fitness(network: SimpleNeuralNetwork) -> float:
    """XOR fitness function"""
    inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    targets = np.array([[0], [1], [1], [0]])

    total_error = 0
    for x, target in zip(inputs, targets):
        output = network.forward(x)
        total_error += np.sum((output - target) ** 2)

    return -total_error  # Negative for maximization

def run_neuroevolution(population_size: int = 50, generations: int = 100,
                      mutation_rate: float = 0.1, hidden_sizes: List[int] = [2]) -> Dict[str, Any]:
    """Run neuroevolution"""

    run_id = f"neuro_{timestamp()}"

    # Initialize population
    population = []
    for _ in range(population_size):
        network = SimpleNeuralNetwork(2, hidden_sizes, 1)
        fitness = xor_fitness(network)
        population.append({
            'network': network,
            'fitness': fitness,
            'params': network.get_params()
        })

    best_fitness_history = []
    avg_fitness_history = []

    for gen in range(generations):
        # Evaluate fitness
        for individual in population:
            individual['fitness'] = xor_fitness(individual['network'])

        # Sort by fitness (descending)
        population.sort(key=lambda x: x['fitness'], reverse=True)

        # Track history
        best_fitness = population[0]['fitness']
        avg_fitness = np.mean([p['fitness'] for p in population])
        best_fitness_history.append(best_fitness)
        avg_fitness_history.append(avg_fitness)

        # Create next generation
        new_population = population[:population_size//2]  # Elitism

        while len(new_population) < population_size:
            # Select parents
            parent1 = random.choice(population[:population_size//2])
            parent2 = random.choice(population[:population_size//2])

            # Crossover
            child_params = (parent1['params'] + parent2['params']) / 2

            # Create child
            child_network = SimpleNeuralNetwork(2, hidden_sizes, 1)
            child_network.set_params(child_params)
            child_network.mutate(mutation_rate)

            child_fitness = xor_fitness(child_network)
            new_population.append({
                'network': child_network,
                'fitness': child_fitness,
                'params': child_network.get_params()
            })

        population = new_population

        # Checkpoint every 10 generations
        if gen % 10 == 0:
            save_checkpoint(population, f"{run_id}_gen_{gen}")

    # Save artifacts
    final_population_data = generate_population_data(population)
    fitness_history_data = generate_fitness_history(best_fitness_history)

    artifacts = {
        "run_id": run_id,
        "algorithm": "neuroevolution",
        "generations": generations,
        "population_size": population_size,
        "mutation_rate": mutation_rate,
        "hidden_sizes": hidden_sizes,
        "final_best_fitness": best_fitness_history[-1],
        "final_avg_fitness": avg_fitness_history[-1],
        "population_data": final_population_data,
        "fitness_history": fitness_history_data
    }

    save_json(artifacts, f"{run_id}_results.json")

    # CSV for analysis
    csv_data = []
    for i, p in enumerate(population):
        csv_data.append({
            "individual": i,
            "fitness": p['fitness'],
            "params_count": len(p['params'])
        })
    save_csv(csv_data, f"{run_id}_population.csv", ["individual", "fitness", "params_count"])

    return artifacts