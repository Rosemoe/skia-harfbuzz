__all__ = ['get_font_size_precision', 'set_font_size_precision']

_font_size_precision = 64


def get_font_size_precision() -> int:
    """
    Get font size precision. The minimum pixel delta will be 1/precision.
    """
    return _font_size_precision


def set_font_size_precision(precision: int):
    """
    Set font size precision. The minimum pixel delta will be 1/precision.
    :param precision: Font size precision.
    """
    global _font_size_precision
    if not isinstance(precision, int):
        raise TypeError("font size precision must be an integer")
    if precision <= 0:
        raise ValueError("font size precision must be positive")
    _font_size_precision = precision
