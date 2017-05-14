from pyworld.lib import dispatch

early_init = dispatch.Signal()

argparse_populate_arguments = dispatch.Signal(providing_args=['parser'])
argparse_post_parse = dispatch.Signal(providing_args=['args'])

post_config_load = dispatch.Signal(providing_args=['config'])

pre_pygame_init = dispatch.Signal()
post_pygame_init = dispatch.Signal()

pre_pygame_quit = dispatch.Signal()
post_pygame_quit = dispatch.Signal()
