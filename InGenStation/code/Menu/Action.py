
class Action:


    def __init__(self, **kwargs):
        self.title = kwargs.get("title","NO TITLE")
        self.callback = kwargs.get("callback",None)


    def __str__(self):
        return self.title