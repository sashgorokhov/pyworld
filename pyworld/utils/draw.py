import random

import noise

from pyworld.utils import color


def polygon_fill(draw, rect, color):
    """
    :param PIL.ImageDraw.ImageDraw draw:
    :param pyworld.utils.position.Rect rect:
    :param world.utils.color.RGBA color:
    """
    draw.polygon(rect.flat(), (*color,))


def simple_noise(point, divider=5, **kwargs):
    """
    
    :param pyworld.utils.position.Point point: 
    :param divider: for the result of noise function
    :param kwargs: passed to `noise.snoise3`
    :return: 
    """
    abs_coords = (abs(point.x), abs(point.y))
    return noise.snoise3(point.x, point.y, random.randint(min(abs_coords), max(abs_coords)), **kwargs) / divider


def apply_noise(image, rect, noise_func=simple_noise, noise_settings=None):
    """
    :param PIL.Image.Image image:
    :param pyworld.utils.position.Rect rect:
    :param noise_func:
    :param dict noise_settings:
    """
    noise_settings = noise_settings or {}

    for point in rect.walk():
        pixel = image.getpixel(point.tuple())
        pixel_color = color.RGBA(*pixel)
        noise_value = noise_func(point, **noise_settings)
        modified_color = pixel_color * (1 + noise_value)
        image.putpixel(point.tuple(), (*modified_color,))
