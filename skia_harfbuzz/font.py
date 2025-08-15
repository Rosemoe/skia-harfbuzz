import uharfbuzz as hb
import skia as sk
from typing import Literal
from .config import get_font_size_precision
from .shaping import shape_text_skhf


AnchorTypeX = Literal['left', 'center', 'right']
AnchorTypeY = Literal['baseline', 'top', 'center', 'bottom']


class SkiaHarfbuzzTypeface:
    """
    Typeface object maintaining both Skia and Harfbuzz typeface object.
    """
    def __init__(self, skia_typeface: sk.Typeface, harfbuzz_typeface: hb.Face):
        self.skia_typeface = skia_typeface
        self.harfbuzz_typeface = harfbuzz_typeface

    @classmethod
    def create_from_data(cls, font_data: bytes, index: int = 0):
        """
        Create typeface from font data in bytes.
        :param font_data: Font data in bytes.
        :param index: Font index to use.
        :return: Generated SkiaHarfbuzzTypeface.
        """
        skia_typeface = sk.Typeface.MakeFromData(font_data, index)
        harfbuzz_typeface = hb.Face(font_data, index)
        return cls(skia_typeface, harfbuzz_typeface)

    @classmethod
    def create_from_file(cls, file_path: str, index: int = 0):
        """
        Create typeface from file path.
        :param file_path: Font file path.
        :param index: Font index to use.
        :return: Generated SkiaHarfbuzzTypeface.
        """
        skia_typeface = sk.Typeface.MakeFromFile(file_path, index)
        harfbuzz_blob = hb.Blob.from_file_path(file_path)
        harfbuzz_typeface = hb.Face(harfbuzz_blob, index)
        return cls(skia_typeface, harfbuzz_typeface)

    def create_font(self, size: float = 12.0, scale_x: float = 1.0, skew_x: float = 0.0,
                    features: dict[str, bool] | None = None) -> "SkiaHarfbuzzFont":
        """
        Create font with given size, scale X and skew X.

        :param size: Font size in pixels (typographic height of text).
        :param scale_x: Text horizontal scale.
        :param skew_x: Additional shear on x-axis relative to y-axis.
        :param features: Optional features dict for font features. By default, kerning and ligatures are enabled.
        :return: Generated SkiaHarfbuzzFont.
        """
        size_precision = get_font_size_precision()
        harfbuzz_font = hb.Font(self.harfbuzz_typeface)
        harfbuzz_font.synthetic_slant = skew_x
        harfbuzz_font.scale = (int(size * size_precision * scale_x), int(size * size_precision))
        return SkiaHarfbuzzFont(sk.Font(self.skia_typeface, size, scale_x, skew_x),
                                harfbuzz_font, size_precision, features)


class SkiaHarfbuzzFont:
    """
    Font object maintaining both Skia and Harfbuzz font object.

    Note that the inner font object in this class must not be mutated.
    """

    def __init__(self, skia_font: sk.Font, harfbuzz_font: hb.Font, size_precision: int,
                 features: dict[str, bool] | None = None):
        """
        Create font with given size, scale X and skew X.

        Note that the given :skia_font: and :harfbuzz_font: must not be mutated.
        """
        self.skia_font = skia_font
        self.harfbuzz_font = harfbuzz_font
        self.size_precision = size_precision
        self._features = features if features is not None else {}

    def set_font_features(self, features: dict[str, bool] | None = None):
        self._features = {} if features is None else features

    def get_font_features(self) -> dict[str, bool]:
        return self._features

    def measure_text(self, text: str) -> float:
        return shape_text_skhf(text, self.skia_font, self.harfbuzz_font, self.size_precision,
                               self._features, build_blob=False)[1]

    def draw_text(self, canvas: sk.Canvas, text: str, x: float, y: float, paint: sk.Paint,
                  anchor_x: AnchorTypeX = 'left', anchor_y: AnchorTypeY = 'baseline'):
        result = shape_text_skhf(text, self.skia_font, self.harfbuzz_font, self.size_precision,
                                 self._features, build_blob=True)
        if result[0] is None:
            return
        blob, text_width = result
        draw_x = x
        draw_y = y
        # Compute X
        if anchor_x != 'left':
            if anchor_x == 'center':
                draw_x = x - text_width / 2
            elif anchor_x == 'right':
                draw_x = x - text_width
            else:
                raise ValueError(f'anchor_x {anchor_x} not supported')
        # Compute Y
        if anchor_y != 'baseline':
            font = self.skia_font
            if anchor_y == 'top':
                draw_y = y - font.getMetrics().fAscent
            elif anchor_y == 'center':
                draw_y = y - font.getSpacing() / 2 - font.getMetrics().fAscent
            elif anchor_y == 'bottom':
                draw_y = y - font.getSpacing() - font.getMetrics().fAscent
            else:
                raise ValueError(f'anchor_y {anchor_y} not supported')
        canvas.drawTextBlob(blob, draw_x, draw_y, paint)
