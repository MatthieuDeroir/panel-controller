class Instructions:
    def __init__(self, instJson):
        self.table = [{}, {}, {}]
        for index, p in enumerate(instJson):
            for key, value in p.items():
                if key in ['index', 'instruction']:
                    self.table[index][key] = value


