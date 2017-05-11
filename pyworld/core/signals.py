from pyworld.lib import dispatch

post_config_load = dispatch.Signal()

pre_pygame_init = dispatch.Signal()
post_pygame_init = dispatch.Signal()

pre_pygame_quit = dispatch.Signal()
post_pygame_quit = dispatch.Signal()