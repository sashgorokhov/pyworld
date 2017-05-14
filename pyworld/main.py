import argparse

import pygame

from pyworld.core import signals


class Main:
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--config', action='store', help='Path to custom pyworld config')
        signals.argparse_populate_arguments.send(parser=parser, suppress=False)

    def parse_args(self):
        parser = argparse.ArgumentParser(description='pyworld game simulation')
        self.add_arguments(parser)
        args = parser.parse_args()
        signals.argparse_post_parse.send(args=args, suppress=False)
        return args

    def load_config(self):
        import pyworld.utils.config
        import pyworld
        config = pyworld.utils.config.read_config(self.args.config)
        signals.post_config_load.send(config=config, suppress=False)
        pyworld.config = config

    def main(self):
        signals.early_init.send(suppress=False)
        self.args = self.parse_args()
        self.load_config()
        self.pygame_init()
        self.pygame_quit()

    def pygame_init(self):
        signals.pre_pygame_init.send()
        pygame.init()
        signals.post_pygame_init.send()

    def pygame_quit(self):
        signals.pre_pygame_quit.send()
        pygame.quit()
        signals.post_pygame_quit.send()


def main():
    return Main().main()

if __name__ == '__main__':
    exit(main())


