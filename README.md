# skia-harfbuzz
![PyPI - Version](https://img.shields.io/pypi/v/skia-harfbuzz?link=https%3A%2F%2Fpypi.org%2Fproject%2Fskia-harfbuzz)

A Python library that helps to draw text in [skia-python](https://github.com/kyamagu/skia-python) with [harfbuzz](https://harfbuzz.github.io/) shaping engine.
## Features Preview
The library integrates with [uharfbuzz](https://github.com/harfbuzz/uharfbuzz) to support font features like kerning and ligatures. 
Here are some showcases for harfbuzz-integrated text shaping. 

For more information about font features, see [this](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_fonts/OpenType_fonts_guide#the_font_features).
### Kerning
Kerning refers to the spacing between specific glyph pairings.
![Kerning: GeosansLight](/images/kerning.png)
### Ligatures
Ligatures are glyphs that replace two or more separate glyphs in order to represent them more smoothly (from a spacing or aesthetic perspective).
Ligatures are necessary in certain language scripts.
![Ligatures: JetBrainsMono](/images/ligatures.png)
## Usage
### Install
The Python package is available on PyPI.
```bash
pip install skia-harfbuzz
```
If you are using Linux, make sure you have correctly configured the environment for skia-python.
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
#### Draw and Measure
`SkiaHarfbuzzFont` provides the following functions to measure and draw text:
* `measure_text(text, bounding_box)`: returns the advance width of text, and optionally a bounding box relative to origin (0, 0)
* `draw_text(canvas, text, x, y, paint, anchor_x, anchor_y)`: draws text with given options

The value of `anchor_x` and `anchor_y` indicates the position type of input `x` and `y`. By default,
`x` is considered the left coordinate and `y` is considered the baseline coordinate (same as skia API).

AnchorTypeX: `left`, `center`, `right`

AnchorTypeY: `baseline`, `top`, `center`, `bottom`
### Patch Skia
Patch skia to override typeface loading and basic text rendering. Then you can continue with you old code.
```python
from skia_harfbuzz import patch_skia

patch_skia()
```
After patching, skia typeface created by `Typeface.MakeFromPath` or `Typeface.MakeFromData` will manage its companion harfbuzz typeface.
The companion harfbuzz typeface is deleted when the typeface is garbage collected.

The following APIs are patched to work with harfbuzz:
* `Canvas.drawString`
* `Canvas.drawSimpleText`
* `Font.measureText`
## Limitations
There are some limitations that you may need to take care when using:
* `Paint` argument in patched `Font.measureText` is not supported. This ignores stroke width and path effect, etc. 
* Minor font settings (e.g. embolden) not considered.