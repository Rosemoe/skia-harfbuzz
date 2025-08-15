__all__ = [
    'patch_skia', 'unpatch_skia',
    'set_default_anchor_type_x', 'get_default_anchor_type_x',
    'set_default_anchor_type_y', 'get_default_anchor_type_y',
]

import contextvars
import weakref
import skia as sk
import uharfbuzz as hb
from threading import Lock
from .font import SkiaHarfbuzzTypeface, SkiaHarfbuzzFont, AnchorTypeX, AnchorTypeY


_is_patched = False
_patch_list = []
_anchor_type_x: AnchorTypeX = 'left'
_anchor_type_y: AnchorTypeY = 'baseline'


def register_patch(clazz, function_name: str):
    # Backup the original function
    original_function = getattr(clazz, function_name)
    setattr(clazz, '_real_' + function_name, original_function)
    def decorator(func):
        # Prevent nested calling
        executing_context = contextvars.ContextVar('executing_context', default=False)
        def wrapper(*args, **kwargs):
            nonlocal executing_context
            if executing_context.get():
                return original_function(*args, **kwargs)
            executing_context.set(True)
            try:
                return func(*args, **kwargs)
            finally:
                executing_context.set(False)
        _patch_list.append((clazz, function_name, wrapper, original_function))
        return func
    return decorator


class ExtraDataManager[TargetType, DataType]:
    def __init__(self):
        self.references: dict[int, weakref.ReferenceType[TargetType]] = {}
        self.extra_data: dict[int, TargetType] = {}
        self.lock = Lock()

    def _handle_object_delete(self, obj_id: int):
        with self.lock:
            self.references.pop(obj_id, None)
            self.extra_data.pop(obj_id, None)

    def set_extra_data(self, obj: TargetType, data: DataType):
        if obj is None:
            return
        obj_id = id(obj)
        if data is None:
            self._handle_object_delete(obj_id)
            return
        with self.lock:
            if obj_id not in self.references:
                self.references[obj_id] = weakref.ref(obj, lambda _: self._handle_object_delete(obj_id))
            self.extra_data[obj_id] = data

    def get_extra_data(self, obj: TargetType) -> DataType | None:
        if obj is None:
            return None
        obj_id = id(obj)
        with self.lock:
            return self.extra_data.get(obj_id, None)

    def __setitem__(self, key: TargetType, value: DataType):
        self.set_extra_data(key, value)

    def __getitem__(self, key: TargetType) -> DataType | None:
        return self.get_extra_data(key)


_typeface_extra_data = ExtraDataManager[sk.Typeface, hb.Face]()


def _get_skhb_font_for(font: sk.Font) -> SkiaHarfbuzzFont | None:
    skia_typeface: sk.Typeface = font.getTypeface()
    harfbuzz_typeface = _typeface_extra_data[skia_typeface]
    if harfbuzz_typeface is None:
        return None
    typeface = SkiaHarfbuzzTypeface(skia_typeface, harfbuzz_typeface)
    skhb_font = typeface.create_font(font.getSize(), font.getScaleX(), font.getSkewX())
    return skhb_font


@register_patch(sk.Typeface, 'MakeFromData')
def make_typeface_from_data(data: bytes, index: int = 0):
    typeface = SkiaHarfbuzzTypeface.create_from_data(data, index)
    _typeface_extra_data[typeface.skia_typeface] = typeface.harfbuzz_typeface
    return typeface.skia_typeface


@register_patch(sk.Typeface, 'MakeFromFile')
def make_typeface_from_file(path: str, index: int = 0):
    typeface = SkiaHarfbuzzTypeface.create_from_file(path, index)
    _typeface_extra_data[typeface.skia_typeface] = typeface.harfbuzz_typeface
    return typeface.skia_typeface


@register_patch(sk.Canvas, 'drawString')
@register_patch(sk.Canvas, 'drawSimpleText')
def canvas_draw_string(canvas: sk.Canvas, text: str, x: float, y: float, font: sk.Font, paint: sk.Paint):
    skhb_font = _get_skhb_font_for(font)
    if skhb_font is None:
        # must call the real drawString/drawSimpleText here to avoid recursion
        draw_string_func = getattr(sk.Canvas, '_real_drawString', None)
        if draw_string_func is None:
            canvas.drawString(text, x, y, font, paint)
        else:
            draw_string_func(canvas, text, x, y, font, paint)
        return
    skhb_font.draw_text(canvas, text, x, y, paint, anchor_x=_anchor_type_x, anchor_y=_anchor_type_y)


@register_patch(sk.Font, 'measureText')
def font_measure_text(font: sk.Font, text: str, encoding: sk.TextEncoding = sk.kUTF8, bounds: sk.Rect | None = None, paint: sk.Paint = None) -> float:
    skhb_font = _get_skhb_font_for(font)
    if skhb_font is None:
        return font.measureText(text, encoding, bounds, paint)
    return skhb_font.measure_text(text=text, bounding_box=bounds)


def patch_skia():
    for patch in _patch_list:
        setattr(patch[0], patch[1], patch[2])


def unpatch_skia():
    for patch in _patch_list:
        setattr(patch[0], patch[1], patch[3])


def set_default_anchor_type_x(typ: AnchorTypeX):
    global _anchor_type_x
    _anchor_type_x = typ


def get_default_anchor_type_x() -> AnchorTypeX:
    return _anchor_type_x


def set_default_anchor_type_y(typ: AnchorTypeY):
    global _anchor_type_y
    _anchor_type_y = typ


def get_default_anchor_type_y() -> AnchorTypeY:
    return _anchor_type_y
