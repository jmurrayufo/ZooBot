
from . import Action, Reading
class Menu:
    """Menu Class
    """

    """
    Menus need to allow the following:
        Information Display
        Action
        User Input
            Bool
            Int
            Float?
            Char?
            String?
    """


    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent",None)
        self.title = kwargs.get("title","NO TITLE")
        self.options = kwargs.get("options",None)
        self.index = 0
        for option in self.options:
            if type(option) == Menu:
                option.parent = self
        pass


    def __str__(self):
        ret_val = f"<< {self.title} >>"
        if self.options:
            ret_val += f"\n{self.index+1} "
            if type(self.options[self.index]) == Menu:
                ret_val += self.options[self.index].title
            elif hasattr(self.options[self.index],'title'):
                ret_val += self.options[self.index].title
                
        return ret_val


    def up(self):
        """Process the "up" button
        """
        self.index += 1
        self.index %= len(self.options)
        return self


    def down(self):
        """Process the "down" button
        """
        self.index -= 1
        self.index %= len(self.options)
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
        return self.options[self.index]


    def cancel(self):
        """Process the "cancel" button
        """
        if self.parent:
            return self.parent
        else:
            return self

