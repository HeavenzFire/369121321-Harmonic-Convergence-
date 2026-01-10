# NSGA-II Optimization Loop Documentation

## Overview
The NSGA-II (Non-dominated Sorting Genetic Algorithm II) optimization loop implements multi-objective optimization for sector allocation problems. It uses evolutionary algorithms to find Pareto-optimal solutions balancing four objectives: health balance, infrastructure smoothness, education diversity, and equity.

## Algorithm Structure

### Core Components
- **Population**: Set of candidate solutions (individuals)
- **Objectives**: Four fitness functions evaluated for each individual
- **Selection**: Tournament selection based on non-domination rank and crowding distance
- **Crossover**: Simulated binary crossover (SBX) for variable recombination
- **Mutation**: Polynomial mutation for solution diversity
- **Elitism**: Preservation of best solutions across generations

### Key Parameters
- `population_size`: Number of individuals (default: 100)
- `n_variables`: Number of decision variables (sectors to optimize)
- `n_objectives`: Number of objectives (fixed at 4)
- `n_generations`: Maximum iterations (default: 100)
- `crossover_prob`: Probability of crossover (default: 0.9)
- `mutation_prob`: Probability of mutation (default: 0.1)

## Input/Output Specification

### Inputs
```python
def sector_optimization(
    n_sectors: int = 10,           # Number of sectors (decision variables)
    population_size: int = 100,    # Population size
    n_generations: int = 100       # Maximum generations
) -> List[Individual]
```

**Input Data Structure:**
- `n_sectors`: Integer, number of sectors to allocate resources to
- `population_size`: Integer, size of solution population
- `n_generations`: Integer, maximum algorithm iterations

### Outputs
Returns `List[Individual]` where each `Individual` contains:
- `variables`: np.ndarray of shape (n_sectors,) with values in [0,1]
- `objectives`: np.ndarray of shape (4,) with objective values
- `rank`: Integer non-domination rank (0 = Pareto front)
- `crowding_distance`: Float diversity metric

**Output Interpretation:**
- Lower objective values are better (minimization problems)
- Rank 0 individuals form the Pareto front (non-dominated solutions)
- Solutions represent trade-offs between the four objectives

## Objective Functions

### 1. Health Balance (f₁)
```
f₁ = Σ|x_i - 0.5|  (minimize)
```
- Measures deviation from equal allocation (0.5)
- Lower values indicate better balance across sectors

### 2. Infrastructure Smoothness (f₂)
```
f₂ = Σ(Δx_i)²  (minimize)
```
- Measures allocation gradient changes
- Lower values indicate smoother resource distribution

### 3. Education Diversity (f₃)
```
f₃ = -σ(x)  (minimize)
```
- Negative of standard deviation
- Lower values indicate higher diversity (less uniform)

### 4. Equity (f₄)
```
f₄ = max|x_i|  (minimize)
```
- Maximum allocation value
- Lower values indicate no sector dominates others

## Algorithm Flow

1. **Initialization**: Random population generation
2. **Evaluation**: Compute objective values for all individuals
3. **Non-dominated Sort**: Rank individuals by domination
4. **Crowding Distance**: Calculate diversity within ranks
5. **Selection**: Tournament selection for reproduction
6. **Crossover**: SBX recombination of parent solutions
7. **Mutation**: Polynomial mutation for exploration
8. **Elitism**: Combine and select next generation
9. **Termination**: Check convergence or max generations

## Convergence Criteria
- Maximum generations reached, OR
- Average crowding distance < 10^-4 (convergence threshold)

## Usage Example
```python
from nsga2_sector_optimization import sector_optimization

# Optimize 10 sectors
pareto_front = sector_optimization(n_sectors=10, population_size=100, n_generations=50)

# Access best solutions
for solution in pareto_front:
    allocations = solution.variables
    objective_scores = solution.objectives
    print(f"Allocation: {allocations}, Objectives: {objective_scores}")
```

## Performance Characteristics
- Time complexity: O(n_generations × population_size × n_objectives × n_variables)
- Space complexity: O(population_size × n_variables)
- Convergence: Typically 50-100 generations for most problems
- Parallelizable: Evaluation and sorting can be distributed

## Validation
The algorithm is validated against known multi-objective benchmarks and produces Pareto fronts that correctly balance the four sector objectives without dominated solutions.