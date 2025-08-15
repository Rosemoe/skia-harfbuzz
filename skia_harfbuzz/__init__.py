__version__ = '0.1.0'

from .config import get_font_size_precision, set_font_size_precision
from .font import SkiaHarfbuzzTypeface, SkiaHarfbuzzFont, AnchorTypeX, AnchorTypeY
from .shaping import shape_text_with_harfbuzz
from .patching import (
    patch_skia, unpatch_skia,
    set_default_anchor_type_y, get_default_anchor_type_y,
    set_default_anchor_type_x, get_default_anchor_type_x
)
