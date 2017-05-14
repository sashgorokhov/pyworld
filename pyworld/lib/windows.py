import logging

import pygame

from pyworld import config
from pyworld.lib import dispatch

logger = logging.getLogger(__name__)


class Window:
    """
    :param pyworld.lib.scene.Scene scene:
    """
    stop_loop = False
    surface = None
    scene = None

    init_display_signal = dispatch.Signal(providing_args=['window', 'surface'])

    def __init__(self, width, height, caption):
        self.width = width
        self.height = height
        self.caption = caption
        self.init_display(width, height, caption)

        self.clock = pygame.time.Clock()

    def init_display(self, width, height, caption):
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.init_display_signal.send(window=self, surface=self.surface)

    def loop(self):
        while not self.stop_loop:
            self.handle_events()
            try:
                self.tick()
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                logger.exception('Error on tick of %s', self)
            pygame.display.flip()
            self.clock.tick(config['windows']['fps_limit'])

    def tick(self):
        pass

    def handle_event(self, event):
        pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_loop = True
                return
            self.handle_event(event)
