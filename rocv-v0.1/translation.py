from parts import Body,Fin

def analyze(data,part):

    xs=[]
    ys=[]

    for line in data["lines"]:

        xs.append(line["start"].x)
        xs.append(line["end"].x)

        ys.append(line["start"].y)
        ys.append(line["end"].y)


    if isinstance(part,Body):

        if xs:
            part.length=max(xs)-min(xs)

        if ys:
            part.diameter=max(ys)-min(ys)


    if isinstance(part,Fin):

        if xs:
            part.width=max(xs)-min(xs)

        if ys:
            part.height=max(ys)-min(ys)


    part.geometry=data

    return part