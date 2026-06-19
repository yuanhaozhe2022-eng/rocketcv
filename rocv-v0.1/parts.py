class Body:
    def __init__(self):
        self.length=None
        self.diameter=None
        self.geometry=None


class Fin:
    def __init__(self):
        self.width=None
        self.height=None
        self.thickness=None
        self.count=1
        self.geometry=None


class Rocket:
    def __init__(self):
        self.body=None
        self.fin=None

    def set_fin(self,fin):
        self.fin=fin