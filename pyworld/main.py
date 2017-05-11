

def main():
    import argparse

    parser = argparse.ArgumentParser(description='pyworld game simulation')
    parser.add_argument('--config', action='store', help='Path to custom pyworld config')
    args = parser.parse_args()

    import pyworld.config
    pyworld.config.read_config(args.config)

    from pyworld.core import signals
    signals.post_config_load.send()

    import pygame
    signals.pre_pygame_init.send()
    pygame.init()
    signals.post_pygame_init.send()

    signals.pre_pygame_quit.send()
    pygame.quit()
    signals.post_pygame_quit.send()
    return 0


if __name__ == '__main__':
    exit(main())


