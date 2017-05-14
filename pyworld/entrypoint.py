from pyworld import config
from pyworld.lib import windows


class Default(windows.Window):
    pass


default_window = Default(**config['windows']['default'])
default_window.loop()
