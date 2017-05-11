
def read_config(path=None):
    import sys
    from pyworld.utils import config

    sys.modules['pyworld.config'] = config.read_config()  # Ha ha, classic
