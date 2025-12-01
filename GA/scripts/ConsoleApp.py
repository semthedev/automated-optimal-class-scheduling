from utils.HtmlOutput import HtmlOutput
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from model.Configuration import Configuration
import sys
import os
import pathlib
import time
import tempfile
import codecs
import traceback
import webbrowser
import subprocess
import matplotlib.pyplot as plt

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# from algorithm.APNsgaIII import APNsgaIII
# from algorithm.Cso import Cso
# from algorithm.GaQpso import GaQpso
# from algorithm.Amga2 import Amga2


def main(config_path: str):
    start_time = time.time()

    cfg_file = pathlib.Path(config_path).expanduser().resolve()
    if not cfg_file.exists():
        print(f"Конфигурационный файл не найден: {cfg_file}")
        sys.exit(1)

    configuration = Configuration()
    configuration.parseFile(str(cfg_file))

    # best_overall = None
    # for attempt in range(3):
    #     alg = GeneticAlgorithm(configuration,
    #                         elitism_size=5,
    #                         crossoverProbability=90,
    #                         mutationProbability=5)
    #     alg.run(maxRepeat=2000, minFitness=1.0)
    #     if best_overall is None or alg.result.fitness > best_overall.fitness:
    #         best_overall = alg.result
    # # работаем с best_overall

    alg = GeneticAlgorithm(configuration)
    alg.run()

    gens = list(range(len(alg.fitness_history)))
    plt.plot(
        gens,
        alg.fitness_history,
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

    html_fragment = HtmlOutput.getResult(alg.result)
    full_html = "\n".join([
        "<!DOCTYPE html>",
        "<html lang='ru'>",
        "<head><meta charset='UTF-8'><title>Расписание</title></head>",
        "<body>",
        html_fragment,
        "</body></html>"
    ])

    tmp_dir = tempfile.gettempdir()
    out_name = cfg_file.stem + ".html"
    out_path = os.path.join(tmp_dir, out_name)
    with codecs.open(out_path, "w", "utf-8") as f:
        f.write(full_html)

    if sys.platform.startswith("win"):
        os.startfile(out_path)
    elif sys.platform == "darwin":
        subprocess.call(["open", out_path])
    else:
        webbrowser.open(f"file://{out_path}")

    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f} secs. → {out_path}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cfg = sys.argv[1]
    else:
        cfg = "config/GaSchedule.json"
    try:
        main(cfg)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
