# Minimal MapData port (stubbed for now)

class MapData:
    def __init__(self):
        self.data = {}

    def load_from_json(self, js):
        self.data = dict(js)

    def to_json(self):
        return dict(self.data)
