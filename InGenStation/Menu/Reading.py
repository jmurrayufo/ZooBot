
class Reading:


    def __init__(self, **kwargs):
        self.title = kwargs.get("title","NO TITLE")


    def __str__(self):
        return self.title