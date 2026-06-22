from parts import Body, Fin
from fin_geometry import trace_loops, shoelace, extract_fin_dimensions


def _xy(p):
    """Accept both ezdxf Vec3 objects and plain tuples."""
    if hasattr(p, "x") and hasattr(p, "y"):
        return (float(p.x), float(p.y))
    return (float(p[0]), float(p[1]))


def analyze(data, part):

    xs = []
    ys = []
    for line in data["lines"]:
        for pt in (line["start"], line["end"]):
            x, y = _xy(pt)
            xs.append(x)
            ys.append(y)

    # ---- BODY ----
    if isinstance(part, Body):
        if xs:
            part.diameter = max(xs) - min(xs)
        if ys:
            part.length   = max(ys) - min(ys)

    # ---- FIN ----
    if isinstance(part, Fin):
        if xs:
            part.width  = max(xs) - min(xs)
        if ys:
            part.height = max(ys) - min(ys)

        part.area = _polygon_area(data["lines"])

        dims = extract_fin_dimensions(data["lines"])

        if dims:
            part.root_chord   = dims["root_chord"]
            part.tip_chord    = dims["tip_chord"]
            part.height       = dims["height"]       # span; overrides bbox estimate
            part.sweep_length = dims["sweep_length"]
            part.sweep_angle  = dims["sweep_angle_deg"]

            # Pre-transform every line point into canonical (chordwise, spanwise)
            # so the preview never has to know how the DXF was oriented.
            tf = dims["transform"]
            part.canonical_geometry = [
                {
                    "start": tf(_xy(line["start"])),
                    "end":   tf(_xy(line["end"]))
                }
                for line in data["lines"]
            ]
        else:
            part.root_chord        = None
            part.tip_chord         = None
            part.sweep_length      = None
            part.sweep_angle       = None
            part.canonical_geometry = None

    part.geometry = data["lines"]
    return part


def _polygon_area(lines):
    """Exact area via shoelace on the traced outline."""
    loops = trace_loops(lines)
    if not loops:
        return None
    return sum(shoelace(loop) for loop in loops)
