import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import random
from matplotlib.patches import Circle

# Harmonic constants
phi = (1 + 5**0.5) / 2  # Golden ratio
pi = math.pi
e = math.e

class FractalGenome:
    def __init__(self, depth=None, angle_variation=None, branch_scaling=None,
                 color_hue=None, energy_level=None):
        self.depth = depth if depth is not None else random.randint(8, 12)
        self.angle_variation = angle_variation if angle_variation is not None else random.uniform(pi/8, pi/4)
        self.branch_scaling = branch_scaling if branch_scaling is not None else random.uniform(0.6, 0.8)
        self.color_hue = color_hue if color_hue is not None else random.uniform(0, 1)
        self.energy_level = energy_level if energy_level is not None else random.uniform(0.5, 2.0)

    def mutate(self, mutation_rate=0.1):
        if random.random() < mutation_rate:
            self.depth = max(5, min(15, self.depth + random.randint(-2, 2)))
        if random.random() < mutation_rate:
            self.angle_variation += random.uniform(-pi/16, pi/16)
            self.angle_variation = max(pi/16, min(pi/3, self.angle_variation))
        if random.random() < mutation_rate:
            self.branch_scaling += random.uniform(-0.1, 0.1)
            self.branch_scaling = max(0.4, min(0.9, self.branch_scaling))
        if random.random() < mutation_rate:
            self.color_hue = (self.color_hue + random.uniform(-0.2, 0.2)) % 1
        if random.random() < mutation_rate:
            self.energy_level += random.uniform(-0.3, 0.3)
            self.energy_level = max(0.2, min(3.0, self.energy_level))

    @classmethod
    def crossover(cls, parent1, parent2):
        child = cls()
        child.depth = random.choice([parent1.depth, parent2.depth])
        child.angle_variation = random.choice([parent1.angle_variation, parent2.angle_variation])
        child.branch_scaling = random.choice([parent1.branch_scaling, parent2.branch_scaling])
        child.color_hue = random.choice([parent1.color_hue, parent2.color_hue])
        child.energy_level = random.choice([parent1.energy_level, parent2.energy_level])
        return child

def calculate_quantum_resonance(genome):
    # Quantum resonance based on harmonic constants
    resonance = (genome.energy_level * phi**2 +
                math.sin(genome.angle_variation * pi) +
                math.cos(genome.depth * e))
    return resonance

def calculate_fitness(genome):
    # Fitness based on complexity, symmetry, and quantum resonance
    complexity = genome.depth * genome.energy_level
    symmetry = 1 / (1 + abs(genome.angle_variation - pi/6))
    resonance = calculate_quantum_resonance(genome)
    fitness = complexity * symmetry * resonance
    return fitness

def draw_fractal(ax, genome, x=0, y=-100, angle=pi/2, depth=None, max_depth=None):
    if depth is None:
        depth = genome.depth
    if max_depth is None:
        max_depth = genome.depth

    if depth == 0:
        return

    # Quantum harmonic scaling
    branch_length = 50 * genome.branch_scaling ** (max_depth - depth) * genome.energy_level

    x2 = x + branch_length * math.cos(angle)
    y2 = y + branch_length * math.sin(angle)

    # Energy-based coloring
    hue = (genome.color_hue + depth/max_depth * 0.3) % 1
    saturation = 0.8 - depth/max_depth * 0.3
    value = 0.9 - depth/max_depth * 0.4
    color = plt.cm.hsv(hue)

    ax.plot([x, x2], [y, y2], color=color, linewidth=depth+1, alpha=0.8)

    # Add quantum particles at branch ends
    if depth == 1:
        particle_color = plt.cm.plasma(genome.energy_level / 3.0)
        ax.add_patch(Circle((x2, y2), 2, color=particle_color, alpha=0.6))

    # Recursive branches with quantum angle variations
    angle_var = genome.angle_variation * (1 + 0.1 * math.sin(depth * pi / max_depth))
    draw_fractal(ax, genome, x2, y2, angle - angle_var, depth - 1, max_depth)
    draw_fractal(ax, genome, x2, y2, angle + angle_var, depth - 1, max_depth)

def evolve_population(population, generations=50, population_size=20):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(-300, 300)
    ax.set_ylim(-200, 300)
    ax.axis('off')
    ax.set_title("Awakened Fractal Evolution", fontsize=16, fontweight='bold')

    best_fitness_history = []
    best_genome = None

    def animate(frame):
        nonlocal best_genome
        ax.clear()
        ax.set_xlim(-300, 300)
        ax.set_ylim(-200, 300)
        ax.axis('off')

        generation = frame // 2  # 2 frames per generation for smoother animation

        if generation < generations:
            # Evaluate fitness
            fitness_scores = [(genome, calculate_fitness(genome)) for genome in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)

            best_genome = fitness_scores[0][0]
            best_fitness = fitness_scores[0][1]
            best_fitness_history.append(best_fitness)

            # Display current best
            draw_fractal(ax, best_genome)

            # Evolution info
            ax.text(-280, 250, f'Generation: {generation + 1}/{generations}', fontsize=12)
            ax.text(-280, 230, f'Best Fitness: {best_fitness:.2f}', fontsize=12)
            ax.text(-280, 210, f'Depth: {best_genome.depth}', fontsize=10)
            ax.text(-280, 190, f'Energy: {best_genome.energy_level:.2f}', fontsize=10)

            # Create next generation
            if generation < generations - 1:
                elite = fitness_scores[:population_size//4]  # Keep top 25%
                new_population = [genome for genome, _ in elite]

                # Breed and mutate
                while len(new_population) < population_size:
                    parent1 = random.choice(elite)[0]
                    parent2 = random.choice(elite)[0]
                    child = FractalGenome.crossover(parent1, parent2)
                    child.mutate()
                    new_population.append(child)

                population[:] = new_population

        else:
            # Final evolved fractal
            if best_genome:
                draw_fractal(ax, best_genome)
                ax.set_title("Final Awakened Fractal", fontsize=16, fontweight='bold')

    anim = animation.FuncAnimation(fig, animate, frames=generations*2,
                                interval=500, repeat=False)

    # Save final frame
    plt.savefig('/vercel/sandbox/awakened_fractal_final.png', dpi=300, bbox_inches='tight')
    plt.close()

    return best_genome, best_fitness_history

# Initialize population
population = [FractalGenome() for _ in range(20)]

# Run evolution
final_genome, fitness_history = evolve_population(population, generations=30)

print("Evolution complete!")
print(f"Final genome - Depth: {final_genome.depth}, Energy: {final_genome.energy_level:.2f}")
print(f"Peak fitness: {max(fitness_history):.2f}")

# Save fitness evolution plot
plt.figure(figsize=(10, 6))
plt.plot(fitness_history)
plt.title('Fractal Consciousness Evolution')
plt.xlabel('Generation')
plt.ylabel('Fitness Score')
plt.grid(True, alpha=0.3)
plt.savefig('/vercel/sandbox/awakened_fitness_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

print("Awakened fractal evolution saved as 'awakened_fractal_final.png'")
print("Fitness evolution saved as 'awakened_fitness_evolution.png'")