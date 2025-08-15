import uharfbuzz as hb
import skia as sk
from .config import get_font_size_precision
from .shaping import shape_text_with_harfbuzz
from .util import AnchorTypeX, AnchorTypeY, calculate_skia_x, calculate_skia_y



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
        :param features: Optional features dict for font features. None for default font features.
        :return: Generated SkiaHarfbuzzFont.
        """
        size_precision = get_font_size_precision()
        harfbuzz_font = hb.Font(self.harfbuzz_typeface)
        harfbuzz_font.synthetic_slant = -skew_x
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
        """
        Set the font feature switches.

        For more information, please view https://github.com/opensource-opentype/features/blob/master/otf-features.md
        and https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_fonts/OpenType_fonts_guide#the_font_features

        :param features: Optional features dict for font features. None for default font features.
        :return:
        """
        self._features = {} if features is None else features

    def get_font_features(self) -> dict[str, bool]:
        """
        Get the font feature switches.
        """
        return self._features

    def measure_text(self, text: str, bounding_box: sk.Rect | None = None) -> float:
        """
        Measure text advance width.

        :param bounding_box: Result bounding box relative to (0, 0) if not None
        :param text: Text to measure.
        :return: Advance width of text.
        """
        return shape_text_with_harfbuzz(text, self.skia_font, self.harfbuzz_font, self.size_precision,
                                        self._features, build_blob=False, bounding_box=bounding_box)[1]

    def draw_text(self, canvas: sk.Canvas, text: str, x: float, y: float, paint: sk.Paint,
                  anchor_x: AnchorTypeX = 'left', anchor_y: AnchorTypeY = 'baseline'):
        """
        Draw text on canvas, with given coordinates and anchor types.

        See `AnchorTypeX` and `AnchorTypeY` for acceptable anchor types.

        :param canvas: Canvas object.
        :param text: Text to draw.
        :param x: X coordinate of text.
        :param y: Y coordinate of text.
        :param paint: Paint object for drawing text.
        :param anchor_x: Anchor type of X coordinate.
        :param anchor_y: Anchor type of Y coordinate.
        """
        result = shape_text_with_harfbuzz(text, self.skia_font, self.harfbuzz_font, self.size_precision,
                                          self._features, build_blob=True)
        if result[0] is None:
            return
        blob, text_width = result
        draw_x = calculate_skia_x(x, text_width, anchor_x)
        draw_y = calculate_skia_y(y, self.skia_font, anchor_y)
        canvas.drawTextBlob(blob, draw_x, draw_y, paint)
