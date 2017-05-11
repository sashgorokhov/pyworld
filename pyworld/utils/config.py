import os
import metayaml


CONFIG_ENV_NAME = 'PYWORLD_CONFIG'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def read(path: str, defaults: dict=None) -> dict:
    defaults = defaults or dict()
    defaults['join'] = os.path.join
    defaults['BASE_DIR'] = BASE_DIR
    return metayaml.read(path, defaults=defaults, disable_order_dict=True)


def read_config(path: str=None) -> dict:
    path = path or os.environ.get(CONFIG_ENV_NAME, None) or os.path.join(BASE_DIR, 'pyworld', 'config', 'config.yaml')
    return read(path)

