from .font import AnchorTypeX, AnchorTypeY
from skia import Font


__all__ = ['calculate_skia_x', 'calculate_skia_y']


def calculate_skia_x(x: float, text_width: float, anchor_x: AnchorTypeX) -> float:
    draw_x = x
    if anchor_x != 'left':
        if anchor_x == 'center':
            draw_x = x - text_width / 2
        elif anchor_x == 'right':
            draw_x = x - text_width
        else:
            raise ValueError(f'anchor_x {anchor_x} not supported')
    return draw_x


def calculate_skia_y(y: float, font: Font, anchor_y: AnchorTypeY) -> float:
    draw_y = y
    if anchor_y != 'baseline':
        if anchor_y == 'top':
            draw_y = y - font.getMetrics().fAscent
        elif anchor_y == 'center':
            draw_y = y - font.getSpacing() / 2 - font.getMetrics().fAscent
        elif anchor_y == 'bottom':
            draw_y = y - font.getSpacing() - font.getMetrics().fAscent
        else:
            raise ValueError(f'anchor_y {anchor_y} not supported')
    return draw_y
