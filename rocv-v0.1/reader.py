import ezdxf
import math

def read_dxf(path):

    doc=ezdxf.readfile(path)
    model=doc.modelspace()

    data={
        "lines":[],
        "arcs":[],
        "splines":[],
        "circles":[]
    }

    for e in model:

        if e.dxftype()=="LINE":

            a=e.dxf.start
            b=e.dxf.end

            data["lines"].append({
                "start":a,
                "end":b,
                "length":distance(a,b)
            })

        elif e.dxftype()=="ARC":
            data["arcs"].append(e)

        elif e.dxftype()=="SPLINE":
            data["splines"].append(e)

        elif e.dxftype()=="CIRCLE":
            data["circles"].append(e)

    return data


def distance(a,b):

    return math.sqrt(
        (b.x-a.x)**2+
        (b.y-a.y)**2
    )