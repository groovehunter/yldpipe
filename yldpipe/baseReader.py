from AbstractBase import AbstractReader


class BaseReader(AbstractReader):
    def __init__(self):
        self.buffer = {}
    def get_buffer(self, fn):
        return self.buffer[fn]

