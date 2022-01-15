class BPMNEdge:
    def __init__(self, src, tgt):
        self.src = src
        self.tgt = tgt

    def __key(self):
        return self.src, self.tgt

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if type(self) is type(other):
            return self.src == other.src and self.tgt == other.tgt
        else:
            return False

    def __repr__(self):
        return f"{self.src} --> {self.tgt}"
