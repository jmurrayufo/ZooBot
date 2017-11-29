
class Reading:


    def __init__(self, **kwargs):
        self.title = kwargs.get("title","NO TITLE")


    def __str__(self):
        return self.title


    def up(self):
        """Process the "up" button
        """
        # NOOP
        return self


    def down(self):
        """Process the "down" button
        """
        # NOOP
        return self


    def right(self):
        """Process the "right" button
        """
        # NOOP
        return self


    def left(self):
        """Process the "left" button
        """
        # NOOP
        return self


    def enter(self):
        """Process the "enter" button
        """
        return self


    def cancel(self):
        """Process the "cancel" button
        """
        return None