import random

from PIL import ImageDraw, Image, ImageFont, ImageFilter
from pygame import image

group = lambda sequence, group_by: zip(*[sequence[i::group_by] for i in range(group_by)])


def from_pil_to_pygame(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tostring()
    return image.fromstring(data, size, mode)


def ground_bounds(x, y, tile_height, border=2):
    return y >= x / 2 - tile_height / 4 + border and y - tile_height / 4 + border <= x / 2 and y - tile_height / 4 - border >= -x / 2 and y - tile_height / 4 <= -x / 2 + tile_height / 2


def hex2rgba(hex, alpha=None):
    """
    :param str hex: FF or #FF or tuple(str, alpha)
    :return tuple:
    """
    if isinstance(hex, tuple):
        hex, alpha = hex
    if hex.startswith('#'):
        hex = hex[1:]
    result = tuple(map(lambda x: int(''.join(x), 16), group(list(hex), 2)))
    if alpha is not None:
        result += (alpha,)
    return result


create_blank_image = lambda width, height, fill_color=(0, 0, 0, 0): Image.new("RGBA", (width, height), fill_color)


class TempImage:
    def __init__(self, passed_image, merge=False):
        """
        :param image: get from width & height from it
        :param merge: merge to image
        """
        self.passed_image = passed_image
        self.merge = merge

    def __enter__(self):
        self.image = create_blank_image(*self.passed_image.size)
        return self.image

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.merge:
            self.passed_image.paste(self.image, (0, 0), self.image)


def fix_colors(*args):
    result = list()
    for color in args:
        if isinstance(color, str):
            if not color.startswith('#'):
                color = '#' + color
            result.append(color)
        elif isinstance(color, tuple):
            result.append(hex2rgba(color[0]) + (color[1],))
    return result


def update_dict(d, **kwargs):
    """
    :param dict d:
    :param kwargs:
    :return dict:
    """
    d = d.copy()
    d.update(kwargs)
    return d


def mix_colors(color1, color2):
    """
    :param tuple color1:
    :param tuple color2:
    :return tuple:
    """
    result = tuple()
    for v1, v2 in zip(color1[:-1], color2[:-1]):
        result += ((v1 + v2) / 2,)
    return result + (color1[-1],)


def convert_line_to_coords(top_left, right_bottom):
    width = right_bottom[0] - top_left[0]
    height = right_bottom[1] - top_left[1]
    image = create_blank_image(width + 1, height + 1)
    draw = ImageDraw.Draw(image)
    draw.line((0, 0, width, height), '#FFFFFF', 1)
    pixels = image.load()
    for y in range(0, height + 1):
        for x in range(0, width + 1):
            current_color = pixels[x, y][:-1]
            if current_color != (0, 0, 0):
                yield (top_left[0] + x, top_left[1] + y)


def convert_polygon_to_coords(top, right, bottom, left):
    """
    :return tuple:
    """
    height = bottom[1] - top[1]
    width = right[0] - left[0]
    offset_x = left[0]
    offset_y = top[1]
    image = create_blank_image(width, height + 1)
    draw = ImageDraw.Draw(image)
    fill_color = '#FFFFFF'
    borders_color = '#AAAAAA'
    draw.polygon((width / 2 - 1, 0, width, height / 2, width / 2 - 1, height, 0, height / 2), fill=fill_color,
                 outline=borders_color)
    draw.line((width / 2 - 1, -1, -1, height / 2 - 1), (0, 0, 0, 0), 1)
    draw.line((width / 2 - 1, -1, width, height / 2 - 1), (0, 0, 0, 0), 1)
    pixels = image.load()
    fill = list()
    borders = list()
    fill_color = hex2rgba(fill_color)
    borders_color = hex2rgba(borders_color)
    for y in range(0, height + 1):
        for x in range(0, width):
            current_color = pixels[x, y][:-1]
            if current_color == fill_color:
                fill.append((offset_x + x, offset_y + y))
            elif current_color == borders_color:
                borders.append((offset_x + x, offset_y + y))
    return fill, borders


def iterate_cross(value_x, value_y, radius=1):
    yield value_x + radius, value_y
    yield value_x, value_y + radius
    yield value_x - radius, value_y
    yield value_x, value_y - radius


def iterate_circle(value_x, value_y, radius=1, bounds=None):
    top_border = value_y - radius
    left_border = value_x - radius
    right_border = value_x + radius
    bottom_border = value_y + radius

    for y in range(top_border, bottom_border + 1):
        for x in range(left_border, right_border + 1):
            if y == top_border or x == left_border or x == right_border or y == bottom_border:
                if bounds is None or (bounds is not None and 0 <= x < bounds[0] and 0 <= y < bounds[1]):
                    yield x, y


def text_surface(text, size, font, color, outline_color=None):
    """
    :return pygame.Surface, tuple(width, height):
    """
    image_font = ImageFont.truetype(font, size)
    image_width, image_height = image_font.getsize(text)
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)
    if outline_color:
        draw.text((0, 0), text, hex2rgba(outline_color), font=image_font)
        image = image.filter(ImageFilter.GaussianBlur(1))
        draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, hex2rgba(color), font=image_font)
    return from_pil_to_pygame(image), (image_width, image_height)


class get_ground_corners:
    def __init__(self, image_width, image_height, offset=0):
        self.top = (image_width / 2, image_height / 4 - offset)
        self.bottom = (image_width / 2, image_height - image_height / 4 - offset)
        self.left = (0, image_height / 2 - offset)
        self.right = (image_width - 1, image_height / 2 - offset)
        if image_width % 2 == 0:
            self.bottom = self.bottom[0] - 1, self.bottom[1]


def ground_raw(image_width, image_height, fill_color, border_color=None, offset=0):
    if border_color is None:
        border_color = fill_color
    fill_color, border_color = fix_colors(fill_color, border_color)
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)
    corners = get_ground_corners(image_width, image_height, offset)
    draw.polygon([corners.top, corners.right, corners.bottom, corners.left], outline=border_color, fill=fill_color)

    # fix draw.polygon bug
    top = corners.top[0], corners.top[1] - 1
    right = corners.right[0], corners.right[1] - 1
    draw.line(top + right, (0, 0, 0, 0), 1)
    return image


def ground(image, fill_color, border_color=None, offset=0):
    result = ground_raw(image.size[0], image.size[1], fill_color, border_color, offset)
    image.paste(result, (0, 0), result)


def left_side_raw(image_width, image_height, tall, fill_color, border_color=None, offset=0):
    if border_color is None:
        border_color = fill_color
    fill_color, border_color = fix_colors(fill_color, border_color)
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)
    corners = get_ground_corners(image_width, image_height, offset)
    top_right = corners.bottom[0], corners.bottom[1] + 1
    top_left = corners.left[0] - 1, corners.left[1] + 1
    bottom_right = top_right[0] + 1, top_right[1] + tall
    bottom_left = top_left[0] + 1, top_left[1] + tall
    draw.polygon([top_left, top_right, bottom_right, bottom_left], fill=fill_color)
    draw.line(top_left + (corners.bottom[0] + 1, corners.bottom[1] + 1), fill=border_color, width=1)

    # fix middle pixels
    pixels = image.load()
    for y in range(0, image_height):
        for x in range(image_width // 2, image_width):
            pixels[x, y] = (0, 0, 0, 0)
    return image


def left_side(image, tall, fill_color, border_color=None, offset=0):
    result = left_side_raw(image.size[0], image.size[1], tall, fill_color, border_color, offset)
    image.paste(result, (0, 0), result)


def right_side_raw(image_width, image_height, tall, fill_color, border_color=None, offset=0):
    if border_color is None:
        border_color = fill_color
    fill_color, border_color = fix_colors(fill_color, border_color)
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)
    corners = get_ground_corners(image_width, image_height, offset)
    top_left = corners.bottom[0] - 1, corners.bottom[1] + 2
    top_right = corners.right[0] + 1, corners.right[1] + 1
    bottom_left = top_left[0] - 1, top_left[1] + tall
    bottom_right = top_right[0] - 1, top_right[1] + tall
    draw.polygon([top_left, top_right, bottom_right, bottom_left], fill=fill_color)
    draw.line(top_right + (corners.bottom[0], corners.bottom[1] + 1), fill=border_color, width=1)

    # fix middle pixels
    pixels = image.load()
    for y in range(0, image_height):
        for x in range(image_width // 4, image_width // 2):
            pixels[x, y] = (0, 0, 0, 0)
    return image


def right_side(image, tall, fill_color, border_color=None, offset=0):
    result = right_side_raw(image.size[0], image.size[1], tall, fill_color, border_color, offset)
    image.paste(result, (0, 0), result)


def dots_raw(image_width, image_height, color, frequency=10, offset=0):
    color = fix_colors(color)[0]
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)
    wait = False
    for y in range(0, image_height):
        for x in range(2, image_width - 3):
            if wait:
                wait = False
                continue
            if random.randint(0, 200) < frequency:
                wait = True
                # if y > 0 and pixels[x, y-1] != (0, 0, 0, 0):
                #    continue
                if ground_bounds(x, y, image_height, 3):
                    draw.point((x, y + image_height / 4 - offset), fill=color)
    return image


def dots(image, color, frequency=10, offset=0):
    result = dots_raw(image.size[0], image.size[1], color, frequency, offset)
    image.paste(result, (0, 0), result)


def left_roots_raw(image_width, image_height, tall, color, full=False, frequency=4, offset=0):
    color = fix_colors(color)[0]
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)

    prev_x = 1
    for x in range(prev_x, image_width // 2):
        if x % frequency == 0:
            top_pos_x = random.randint(prev_x, x)
            bottom_pos_x = random.randint(top_pos_x - 1, top_pos_x + 1)
            top_pos_y = image_height / 2 + top_pos_x / 2 + 2 - offset
            bottom_pos_y = image_height / 2 + bottom_pos_x / 2 + tall - offset
            if not full:
                bottom_pos_y -= random.randint(0, tall // 4)
            draw.line((top_pos_x, top_pos_y, bottom_pos_x, bottom_pos_y), fill=color, width=1)
            prev_x = x

    return image


def left_roots(image, tall, color, full=False, frequency=4, offset=0):
    result = left_roots_raw(image.size[0], image.size[1], tall, color, full, frequency, offset)
    image.paste(result, (0, 0), result)


def right_roots_raw(image_width, image_height, tall, color, full=False, frequency=4, offset=0):
    color = fix_colors(color)[0]
    image = create_blank_image(image_width, image_height)
    draw = ImageDraw.Draw(image)

    prev_x = image_width // 2 + frequency
    for x in range(prev_x, image_width):
        if x % frequency == 0:
            top_pos_x = random.randint(prev_x, x)
            bottom_pos_x = random.randint(top_pos_x - 1, top_pos_x + 1)
            top_pos_y = image_height - top_pos_x / 2 + 1 - offset
            bottom_pos_y = image_height - bottom_pos_x / 2 + tall - 1 - offset
            if not full:
                bottom_pos_y -= random.randint(0, tall // 4)
            draw.line((top_pos_x, top_pos_y, bottom_pos_x, bottom_pos_y), fill=color, width=1)
            prev_x = x

    return image


def water_on_ground(image, tall, fill_color, border_color=None, offset=0):
    if border_color is None:
        border_color = fill_color
    fill_color = fix_colors(fill_color)[0]
    border_color = fix_colors(border_color)[0]
    draw = ImageDraw.Draw(image)
    pixels = image.load()
    image_width, image_height = image.size
    corners = get_ground_corners(image_width, image_height, offset)
    corners.right = corners.right[0] + 1, corners.right[1]
    fill, borders = convert_polygon_to_coords(corners.top, corners.right, corners.bottom, corners.left)
    for x, y in fill:
        current_color = pixels[x, y]
        if current_color != (0, 0, 0, 0):
            pixels[x, y] = mix_colors(current_color, fill_color)
        else:
            pixels[x, y] = fill_color
    for x, y in borders:
        current_color = pixels[x, y]
        if current_color != (0, 0, 0, 0):
            pixels[x, y] = mix_colors(current_color, border_color)
        else:
            pixels[x, y] = border_color


def right_roots(image, tall, color, full=False, frequency=4, offset=0):
    result = right_roots_raw(image.size[0], image.size[1], tall, color, full, frequency, offset)
    image.paste(result, (0, 0), result)


class ColorBase:
    pass


class Ground(ColorBase):
    ground = None
    ground_borders = None
    dots = ground_borders
    left = None
    left_borders = None
    left_roots = left_borders
    right = None
    right_borders = None
    right_roots = right_borders


class Grass(Ground):
    ground = '41a62a'
    ground_borders = '378d24'
    dots = ground_borders
    left = '925429'
    left_borders = '814622'
    left_roots = left_borders
    right = '8c4d26'
    right_borders = '7b3016'
    right_roots = right_borders


class Sand(Ground):
    ground = 'f1e0a5'
    ground_borders = 'e1ca73'
    dots = ground_borders
    left = 'e1ca73'
    left_borders = 'cdb35a'
    left_roots = left_borders
    right = 'd1b868'
    right_borders = 'bba251'
    right_roots = right_borders


class Water(Ground):
    ground = ('9dd2db', 180)
    ground_borders = ('6db6d9', 180)
    left = ground
    right = ground
    left_borders = ground
    right_borders = ground


class Blank(Ground):
    ground = '5e5e5e'
    ground_borders = '514f4f'
    left = '7b7b7b'
    right = '484747'


if __name__ == '__main__':
    color = Water()

    image = create_blank_image(64, 64)
    ground(image, color.ground, color.ground_borders)

    left_side(image, 15, color.left, color.left_borders)
    right_side(image, 15, color.right, color.right_borders)

    # dots(image, color.dots)
    # left_roots(image, 15, color.left_roots)
    # right_roots(image, 15, color.right_roots)
    #
    image.save('imae.png')
