import uharfbuzz as hb
import skia as sk


def shape_text_skhf(text: str | hb.Buffer, skia_font: sk.Font, harfbuzz_font: hb.Font,
                    size_precision: int, features: dict[str, bool] | None = None,
                    build_blob: bool = False, bounding_box: sk.Rect | None = None) -> tuple[sk.TextBlob | None, float]:
    if features is None:
        features = {}
    if isinstance(text, hb.Buffer):
        buf = text
    else:
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()

    hb.shape(harfbuzz_font, buf, features)

    if bounding_box:
        bounding_box.setEmpty()

    l, t, r, b = 0, 0, 0, 0
    # Assuming Y = 0 -> Top, X = 0 -> Left
    curr_advance_x = 0.0
    curr_advance_y = 0.0
    multiplier = 1 / size_precision
    glyphs, positions = [], []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gid = info.codepoint
        x_advance = pos.x_advance * multiplier
        y_advance = pos.y_advance * multiplier
        if build_blob:
            x_offset = pos.x_offset * multiplier
            y_offset = pos.y_offset * multiplier
            glyphs.append(gid)
            positions.append(sk.Point(curr_advance_x + x_offset, curr_advance_y + y_offset))
        if bounding_box:
            extents = harfbuzz_font.get_glyph_extents(gid)
            gl, gt = curr_advance_x + extents.x_bearing / size_precision, curr_advance_y - extents.y_bearing / size_precision
            gr, gb = gl + extents.width / size_precision, gt - extents.height / size_precision
            print(gl, gt)
            l, t = min(l, gl), min(t, gt)
            r, b = max(r, gr), max(b, gb)
        curr_advance_x += x_advance
        curr_advance_y += y_advance

    if bounding_box:
        bounding_box.setLTRB(l, t, r, b)
    if not build_blob:
        return None, curr_advance_x

    builder = sk.TextBlobBuilder()
    builder.allocRunPos(skia_font, glyphs, positions)
    blob: sk.TextBlob = builder.make()
    return blob, curr_advance_x