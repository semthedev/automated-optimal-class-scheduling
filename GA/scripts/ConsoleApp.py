import argparse
import codecs
import os
import pathlib
import subprocess
import sys
import time
import traceback
import webbrowser

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from algorithm.GeneticAlgorithm import GeneticAlgorithm  # noqa: E402
from model.Configuration import Configuration  # noqa: E402
from utils.HtmlOutput import HtmlOutput  # noqa: E402

DEFAULT_CONFIG = PROJECT_ROOT.parent / "config" / "GaSchedule.json"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Solve the university class-scheduling problem with a genetic algorithm."
    )
    parser.add_argument("config", nargs="?", default=str(DEFAULT_CONFIG),
                        help="path to the JSON configuration file")
    parser.add_argument("--out-dir", default="output",
                        help="directory for the generated schedule and fitness plot")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for a reproducible run")
    parser.add_argument("--max-repeat", type=int, default=9999,
                        help="stop after this many generations without improvement")
    parser.add_argument("--min-fitness", type=float, default=1.0,
                        help="stop as soon as this fitness is reached")
    parser.add_argument("--headless", action="store_true",
                        help="write files only: no plot window, no browser (use in CI)")
    return parser.parse_args(argv)


def main(args):
    start_time = time.time()

    if args.headless:
        matplotlib.use("Agg")

    if args.seed is not None:
        import random
        random.seed(args.seed)

    cfg_file = pathlib.Path(args.config).expanduser().resolve()
    if not cfg_file.exists():
        print(f"Configuration file not found: {cfg_file}", file=sys.stderr)
        return 1

    configuration = Configuration()
    configuration.parseFile(str(cfg_file))
    print(f"Loaded {configuration.numberOfCourseClasses} classes, "
          f"{configuration.numberOfRooms} rooms, "
          f"{configuration.numberOfProfessors} professors, "
          f"{configuration.numberOfStudentGroups} student groups.")

    alg = GeneticAlgorithm(configuration)
    alg.run(maxRepeat=args.max_repeat, minFitness=args.min_fitness)

    out_dir = pathlib.Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_path = out_dir / f"{cfg_file.stem}_fitness.png"
    plt.figure()
    plt.plot(range(len(alg.fitness_history)), alg.fitness_history,
             marker="o", linestyle="-", label="best fitness")
    plt.xlabel("Generation")
    plt.ylabel("Best fitness")
    plt.title("Fitness evolution")
    plt.grid(True)
    plt.legend(loc="lower right")
    plt.savefig(plot_path, dpi=120, bbox_inches="tight")
    if not args.headless:
        plt.show()
    plt.close()

    html_path = out_dir / f"{cfg_file.stem}.html"
    full_html = "\n".join([
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head><meta charset='UTF-8'><title>Schedule</title></head>",
        "<body>",
        HtmlOutput.getResult(alg.result),
        "</body></html>",
    ])
    with codecs.open(str(html_path), "w", "utf-8") as f:
        f.write(full_html)

    if not args.headless:
        if sys.platform.startswith("win"):
            os.startfile(html_path)
        elif sys.platform == "darwin":
            subprocess.call(["open", str(html_path)])
        else:
            webbrowser.open(html_path.as_uri())

    print(f"Best fitness: {alg.result.fitness:.4f}")
    print(f"Schedule:     {html_path}")
    print(f"Fitness plot: {plot_path}")
    print(f"Completed in {time.time() - start_time:.2f}s")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(parse_args()))
    except Exception:
        traceback.print_exc()
        sys.exit(1)
