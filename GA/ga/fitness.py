from typing import Tuple
from ga.representation import decode


def evaluate(indiv) -> Tuple[float]:
    sched = decode(indiv)
    return (sched.fitness,)
