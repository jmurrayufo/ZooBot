


class Image:
    """Track data and progress of an image as an object.
    """


    def __init__(self, name, destination):
        self.name = name
        self.destination = destination
        self.current_location = None
        self.manifest = None
        self.captured = False
        self.writen = False
        self.copied = False