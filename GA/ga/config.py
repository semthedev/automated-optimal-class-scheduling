import pathlib
from model.Configuration import Configuration

_config = None


def get_config(path: pathlib.Path = None) -> Configuration:
    global _config
    if _config is None:
        if path is None:
            path = pathlib.Path.cwd() / "config" / "GaSchedule.json"
        _config = Configuration()
        _config.parseFile(str(path))
    return _config
