import numpy as np
import random
from typing import List, Dict, Any, Callable
from utils.logger import save_json, save_csv, timestamp
from utils.checkpoint import save_checkpoint
from utils.visualization import generate_population_data, generate_fitness_history

class Agent:
    """Individual agent in multi-agent system"""

    def __init__(self, agent_id: int, strategy: str = "random"):
        self.id = agent_id
        self.strategy = strategy
        self.score = 0
        self.history = []
        self.neighbors = []

    def make_decision(self, game_state: Dict[str, Any]) -> str:
        """Make decision based on strategy"""
        if self.strategy == "cooperate":
            return "cooperate"
        elif self.strategy == "defect":
            return "defect"
        elif self.strategy == "random":
            return random.choice(["cooperate", "defect"])
        elif self.strategy == "tit_for_tat":
            if not self.history:
                return "cooperate"
            return self.history[-1]['opponent_move']
        elif self.strategy == "grim_trigger":
            if "defect" in [h['opponent_move'] for h in self.history]:
                return "defect"
            return "cooperate"
        else:
            return "cooperate"

    def update_score(self, payoff: float):
        """Update agent score"""
        self.score += payoff

    def add_interaction(self, opponent_move: str, my_move: str, payoff: float):
        """Record interaction"""
        self.history.append({
            'opponent_move': opponent_move,
            'my_move': my_move,
            'payoff': payoff
        })

class MultiAgentSystem:
    """Multi-agent evolutionary system"""

    def __init__(self, num_agents: int = 50, game_type: str = "prisoner_dilemma"):
        self.num_agents = num_agents
        self.game_type = game_type
        self.agents = self.initialize_agents()
        self.payoff_matrix = self.get_payoff_matrix()
        self.interaction_history = []

    def initialize_agents(self) -> List[Agent]:
        """Initialize agents with different strategies"""
        strategies = ["cooperate", "defect", "random", "tit_for_tat", "grim_trigger"]
        agents = []

        for i in range(self.num_agents):
            strategy = random.choice(strategies)
            agents.append(Agent(i, strategy))

        return agents

    def get_payoff_matrix(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Get payoff matrix for the game"""
        if self.game_type == "prisoner_dilemma":
            return {
                ("cooperate", "cooperate"): (3, 3),  # Mutual cooperation
                ("cooperate", "defect"): (0, 5),     # Sucker payoff
                ("defect", "cooperate"): (5, 0),     # Temptation
                ("defect", "defect"): (1, 1)         # Mutual defection
            }
        elif self.game_type == "stag_hunt":
            return {
                ("cooperate", "cooperate"): (4, 4),  # Successful hunt
                ("cooperate", "defect"): (1, 2),     # Failed hunt
                ("defect", "cooperate"): (2, 1),     # Hare hunting
                ("defect", "defect"): (2, 2)         # Both hunt hare
            }
        else:
            # Default to prisoner's dilemma
            return self.get_payoff_matrix()

    def play_game(self, agent1: Agent, agent2: Agent) -> None:
        """Play one round of the game between two agents"""
        move1 = agent1.make_decision({})
        move2 = agent2.make_decision({})

        payoff1, payoff2 = self.payoff_matrix[(move1, move2)]

        agent1.update_score(payoff1)
        agent2.update_score(payoff2)

        agent1.add_interaction(move2, move1, payoff1)
        agent2.add_interaction(move1, move2, payoff2)

        self.interaction_history.append({
            'agent1_id': agent1.id,
            'agent2_id': agent2.id,
            'agent1_move': move1,
            'agent2_move': move2,
            'agent1_payoff': payoff1,
            'agent2_payoff': payoff2
        })

    def evolve_strategies(self) -> None:
        """Evolve agent strategies based on performance"""
        # Sort agents by score
        self.agents.sort(key=lambda a: a.score, reverse=True)

        # Replace bottom half with mutated versions of top performers
        num_to_replace = self.num_agents // 2
        top_performers = self.agents[:num_to_replace]

        new_agents = self.agents[:num_to_replace]  # Keep top performers

        while len(new_agents) < self.num_agents:
            # Select parent from top performers
            parent = random.choice(top_performers)

            # Create child with possible mutation
            child = Agent(len(new_agents), parent.strategy)

            # Strategy mutation
            if random.random() < 0.1:  # 10% mutation rate
                strategies = ["cooperate", "defect", "random", "tit_for_tat", "grim_trigger"]
                child.strategy = random.choice(strategies)

            new_agents.append(child)

        self.agents = new_agents

    def run_simulation(self, rounds_per_generation: int = 10, generations: int = 50) -> Dict[str, Any]:
        """Run multi-agent simulation"""
        strategy_distribution_history = []

        for gen in range(generations):
            # Reset scores for new generation
            for agent in self.agents:
                agent.score = 0

            # Play games within generation
            for _ in range(rounds_per_generation):
                # Random pairing for interactions
                agents_copy = self.agents.copy()
                random.shuffle(agents_copy)

                for i in range(0, len(agents_copy) - 1, 2):
                    self.play_game(agents_copy[i], agents_copy[i+1])

            # Track strategy distribution
            strategy_counts = {}
            for agent in self.agents:
                strategy_counts[agent.strategy] = strategy_counts.get(agent.strategy, 0) + 1

            strategy_distribution_history.append(strategy_counts)

            # Evolve strategies
            self.evolve_strategies()

            # Checkpoint every 10 generations
            if gen % 10 == 0:
                save_checkpoint(self.agents, f"multi_agent_gen_{gen}")

        # Calculate final statistics
        final_scores = [agent.score for agent in self.agents]
        strategy_counts = {}
        for agent in self.agents:
            strategy_counts[agent.strategy] = strategy_counts.get(agent.strategy, 0) + 1

        return {
            'final_agents': self.agents,
            'final_scores': final_scores,
            'strategy_distribution_history': strategy_distribution_history,
            'interaction_history': self.interaction_history[-1000:],  # Last 1000 interactions
            'final_strategy_counts': strategy_counts,
            'avg_final_score': np.mean(final_scores),
            'max_final_score': max(final_scores)
        }

def run_multi_agent_simulation(num_agents: int = 50, game_type: str = "prisoner_dilemma",
                              rounds_per_generation: int = 10, generations: int = 50) -> Dict[str, Any]:
    """Run multi-agent evolutionary simulation"""

    run_id = f"multi_agent_{timestamp()}"

    system = MultiAgentSystem(num_agents, game_type)
    results = system.run_simulation(rounds_per_generation, generations)

    # Generate visualization data
    # Convert agents to population data format
    population_data = []
    for agent in results['final_agents']:
        population_data.append({
            'x': agent.id,  # Use agent ID as x coordinate
            'y': agent.score,  # Score as y coordinate
            'fitness': agent.score,
            'strategy': agent.strategy
        })

    viz_data = generate_population_data(population_data)

    # Save artifacts
    artifacts = {
        "run_id": run_id,
        "algorithm": "multi_agent",
        "game_type": game_type,
        "num_agents": num_agents,
        "rounds_per_generation": rounds_per_generation,
        "generations": generations,
        "avg_final_score": results['avg_final_score'],
        "max_final_score": results['max_final_score'],
        "final_strategy_counts": results['final_strategy_counts'],
        "strategy_distribution_history": results['strategy_distribution_history'],
        "population_data": viz_data
    }

    save_json(artifacts, f"{run_id}_results.json")

    # CSV for agent analysis
    csv_data = []
    for agent in results['final_agents']:
        csv_data.append({
            "agent_id": agent.id,
            "strategy": agent.strategy,
            "final_score": agent.score,
            "history_length": len(agent.history)
        })
    save_csv(csv_data, f"{run_id}_agents.csv",
             ["agent_id", "strategy", "final_score", "history_length"])

    # CSV for interactions
    interaction_csv = []
    for interaction in results['interaction_history'][-500:]:  # Last 500 interactions
        interaction_csv.append(interaction)
    save_csv(interaction_csv, f"{run_id}_interactions.csv",
             ["agent1_id", "agent2_id", "agent1_move", "agent2_move", "agent1_payoff", "agent2_payoff"])

    return artifacts