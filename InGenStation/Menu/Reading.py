
class Reading:

    def __init__(self, screen, **kwargs):
        self.screen = screen
        self.title = kwargs.get("title","NO TITLE")
        self.reading = kwargs["reading"] # We must have a value to read!
        self.source = kwargs["source"] # We must have a parent object to call


    def __str__(self):
        ret_val = f"R: {self.title}"
        value = self.source.readings.get(self.reading,None)
        ret_val = f"\n {value}"
        return ret_val


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