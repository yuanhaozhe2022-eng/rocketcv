class Body:
    def __init__(self):
        self.length = None
        self.diameter = None
        self.geometry = None


class Fin:
    def __init__(self):
        self.width = None
        self.height = None        # span (canonical y-extent)
        self.thickness = None
        self.count = 1
        self.area = None
        self.root_chord = None
        self.tip_chord = None
        self.sweep_length = None
        self.sweep_angle = None
        self.distance_from_bottom = 0
        self.geometry = None
        self.canonical_geometry = None   # lines in (chordwise, spanwise) coords


class Rocket:
    def __init__(self):
        self.body = None
        self.fin = None

    def set_fin(self, fin):
        self.fin = fin
