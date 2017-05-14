import logging.config

from pyworld.core import signals


@signals.post_config_load.register()
def setup_logging(config: dict):
    logging.config.dictConfig(config['logging']['config'])
