import random
import numpy as np
from deap import base, creator, tools
from ga.representation import encode
from ga.fitness import evaluate
from ga.operators import cx_schedule, mut_schedule_factory
from ga.config import get_config

if "FitnessMax" not in creator.__dict__:
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("individual", tools.initIterate, creator.Individual, encode)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)
toolbox.register("mate",     cx_schedule)
toolbox.register("mutate",   tools.mutShuffleIndexes, indpb=0.2)
toolbox.register("select",   tools.selTournament, tournsize=3)


def init_seed(seed: int = None):
    random.seed(seed)
    np.random.seed(seed)
