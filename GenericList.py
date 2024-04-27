class GenericList:
    def __init__(self, length):
        self.length = length
        self.values = {}
        self.index = -1

    def add_value(self, value):
        self.index += 1
        if self.index == self.length:
            self.index = 0
        self.values[self.index] = value

    def get_current_value(self):
        if self.index == -1:
            return None
        value = self.values.get(self.index)
        return value