# #!/usr/bin/env python3
# # scripts/ConsoleAppDEAP.py
#!/usr/bin/env python3
from utils.HtmlOutput import HtmlOutput
from ga.operators import mut_schedule_factory
from ga.representation import decode
from ga.toolbox import toolbox, init_seed
from ga.config import get_config
from deap import tools, algorithms
import multiprocessing
import traceback
import subprocess
import webbrowser
import codecs
import tempfile
import numpy as np
import random
import time
import os
import pathlib
import sys
from pathlib import Path
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main(config_path: str,
         pop_size: int = 100,
         ngen: int = 10000,
         cx_pb: float = 0.6,
         mut_pb: float = 0.2,
         seed: int = 42):
    start_time = time.time()

    config = get_config(path=pathlib.Path(config_path))

    toolbox.unregister("mutate")
    toolbox.register("mutate",
                     mut_schedule_factory(config),
                     indpb=mut_pb)

    init_seed(seed)
    random.seed(seed)
    np.random.seed(seed)

    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    population = toolbox.population(n=pop_size)
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    hof = tools.HallOfFame(1)
    hof.update(population)

    fitness_history = []
    fitness_history.append(hof[0].fitness.values[0])
    print(f"Generation:   0\tBest fitness: {hof[0].fitness.values[0]:.6f}")

    for gen in range(1, ngen + 1):
        # селекция + вариация
        offspring = tools.selTournament(
            population, len(population), tournsize=3)
        offspring = algorithms.varAnd(offspring, toolbox, cx_pb, mut_pb)

        # оценка потомков
        fits = map(toolbox.evaluate, offspring)
        for ind, fit in zip(offspring, fits):
            ind.fitness.values = fit

        # новое поколение
        population[:] = offspring
        hof.update(population)
        best = hof[0]

        # записываем историю
        best = hof[0]
        fitness_history.append(best.fitness.values[0])

        # печать прогресса
        print(
            f"Generation: {gen:3d}\tBest fitness: {best.fitness.values[0]:.6f}", end="\r")

        # досрочный выход при идеальном расписании
        if best.fitness.values[0] >= 1.0:
            print()  # перевод строки после прогресса
            break

    schedule = decode(best)

    gens = list(range(len(fitness_history)))
    plt.plot(
        gens,
        fitness_history,
        marker='o',
        linestyle='-',
        label='Лучший фитнес'
    )
    plt.xlabel("Поколение")
    plt.ylabel("Лучший фитнес")
    plt.title("Эволюция фитнеса")
    plt.grid(True)
    plt.legend(title='Обозначения', loc='lower right')
    plt.show()

    html_fragment = HtmlOutput.getResult(schedule)
    full_html = "\n".join([
        "<!DOCTYPE html>",
        "<html lang='ru'>",
        "<head><meta charset='UTF-8'><title>Расписание</title></head>",
        "<body>",
        html_fragment,
        "</body></html>"
    ])

    tmp_file = pathlib.Path(tempfile.gettempdir()) / \
        (pathlib.Path(config_path).stem + ".html")
    with codecs.open(str(tmp_file), "w", "utf-8") as f:
        f.write(full_html)

    if sys.platform.startswith("win"):
        os.startfile(str(tmp_file))
    elif sys.platform == "darwin":
        subprocess.call(["open", str(tmp_file)])
    else:
        webbrowser.open(f"file://{tmp_file}")

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f} seconds. Result: {tmp_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ConsoleAppDEAP.py path/to/GaSchedule.json")
        sys.exit(1)
    try:
        main(sys.argv[1])
    except Exception:
        traceback.print_exc()
        sys.exit(2)
