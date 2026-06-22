import ezdxf
import math


def read_dxf(path):

    doc = ezdxf.readfile(path)
    model = doc.modelspace()

    data = {
        "lines": [],
        "arcs": [],
        "splines": [],
        "circles": []
    }

    for e in model:

        t = e.dxftype()

        if t == "LINE":

            a = e.dxf.start
            b = e.dxf.end

            data["lines"].append({
                "start": a,
                "end": b,
                "length": distance(a, b)
            })

        elif t == "ARC":
            data["lines"] += arc_to_lines(e)

        elif t == "CIRCLE":
            data["lines"] += circle_to_lines(e)

        elif t == "SPLINE":
            data["lines"] += spline_to_lines(e)

    return data


# ---------------- CURVE CONVERSION ----------------

def arc_to_lines(arc, steps=12):

    lines = []

    cx = arc.dxf.center.x
    cy = arc.dxf.center.y
    r = arc.dxf.radius

    start = math.radians(arc.dxf.start_angle)
    end = math.radians(arc.dxf.end_angle)

    for i in range(steps):

        a1 = start + (end - start) * i / steps
        a2 = start + (end - start) * (i + 1) / steps

        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)

        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)

        lines.append({
            "start": (x1, y1),
            "end": (x2, y2)
        })

    return lines


def circle_to_lines(circle, steps=24):

    lines = []

    cx = circle.dxf.center.x
    cy = circle.dxf.center.y
    r = circle.dxf.radius

    for i in range(steps):

        a1 = 2 * math.pi * i / steps
        a2 = 2 * math.pi * (i + 1) / steps

        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)

        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)

        lines.append({
            "start": (x1, y1),
            "end": (x2, y2)
        })

    return lines


def spline_to_lines(spline, steps=20):

    pts = spline.approximate(steps)

    lines = []

    for i in range(len(pts) - 1):

        p1 = pts[i]
        p2 = pts[i + 1]

        lines.append({
            "start": (p1.x, p1.y),
            "end": (p2.x, p2.y)
        })

    return lines


# ---------------- DISTANCE ----------------

def distance(a, b):

    return math.sqrt(
        (b.x - a.x) ** 2 +
        (b.y - a.y) ** 2
    )