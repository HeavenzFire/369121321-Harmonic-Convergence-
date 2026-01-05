import argparse
import sys
import os
sys.path.append('/vercel/sandbox/evolution_lab')

from modules.neuroevolution import run_cli as neuro_run
from modules.quantum_ga import run_cli as quantum_run
from modules.swarm_intelligence import run_cli as swarm_run
from modules.moea_nsga2 import run_cli as moea_run
from modules.evolutionary_game import run_cli as game_run
from modules.meta_evolution import run_cli as meta_run

parser = argparse.ArgumentParser()
parser.add_argument("--target", required=True)
parser.add_argument("--algo", required=True)
parser.add_argument("--iters", type=int, default=1000)
parser.add_argument("--agents", type=int, default=50)
parser.add_argument("--population", type=int, default=50)
parser.add_argument("--objectives", type=int, default=2)
args = parser.parse_args()

if args.algo == "neuroevolution":
    neuro_run(iterations=args.iters, population=args.population)
elif args.algo == "quantum_ga":
    quantum_run(iterations=args.iters, population=args.population)
elif args.algo == "swarm_intelligence":
    swarm_run(agents=args.agents, iterations=args.iters)
elif args.algo == "moea_nsga2":
    moea_run(iterations=args.iters, population=args.population, objectives=args.objectives)
elif args.algo == "evolutionary_game":
    game_run(agents=args.agents, iterations=args.iters)
elif args.algo == "meta_evolution":
    meta_run(iterations=args.iters)
else:
    print(f"Algorithm '{args.algo}' not recognized.")