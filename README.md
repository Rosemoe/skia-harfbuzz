# skia-harfbuzz
A Python library that helps to draw text in skia-python with harfbuzz shaping engine.
## Usage
### Use Library API
#### Create Typeface and Font
```python
from skia_harfbuzz import SkiaHarfbuzzTypeface, SkiaHarfbuzzFont

font_path = '/path/to/your_font.ttf'
typeface = SkiaHarfbuzzTypeface.create_from_file(font_path)
# Or use font data
# with open(font_path, 'r') as f:
#     typeface = SkiaHarfbuzzTypeface.create_from_data(f.read())

font: SkiaHarfbuzzFont = typeface.create_font(size=20.0)
# Optionally, set scaleX, skewX and font features
# font = typeface.create_font(size=20.0, scale_x=1.1, skew_x=-0.10, features={ 'calt': False })
```
For more information about font features, see [this](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_fonts/OpenType_fonts_guide#the_font_features).
#### Draw and Measure
`SkiaHarfbuzzFont` provides the following functions to measure and draw text:
* `measure_text(text, bounding_box)`: returns the advance width of text, and optionally a bounding box relative to origin (0, 0)
* `draw_text(canvas, text, x, y, paint, anchor_x, anchor_y)`: draws text with given options

The value of `anchor_x` and `anchor_y` indicates the position type of input `x` and `y`. By default,
`x` is considered the left coordinate and `y` is considered the baseline coordinate (same as skia API).

AnchorTypeX: `left`, `center`, `right`

AnchorTypeY: `baseline`, `top`, `center`, `bottom`
### Patch Skia
Patch skia to override typeface loading and basic text rendering. And you can continue with you old code.
```python
from skia_harfbuzz import patch_skia

patch_skia()
```
After patching, skia typefaces created by `Typeface.MakeFromPath` or `Typeface.MakeFromData` will manage its companion harfbuzz typeface.
The companion harfbuzz typeface is deleted when the typeface is garbage collected.

The following APIs are patched to work with harfbuzz:
* `Canvas.drawString`
* `Canvas.drawSimpleText`
* `Font.measureText`

Note that measuring with paint is not supported, the given paint is ignored. Minor font settings (e.g. embolden) not supported.