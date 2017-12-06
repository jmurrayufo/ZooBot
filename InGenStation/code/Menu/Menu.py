
import logging
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


    def __init__(self, screen, **kwargs):
        self.log = logging.getLogger('DragonHab')
        self.screen = screen
        self.id = kwargs['id'] # We need this, throw error if we don't have it
        self.parent = kwargs.get("parent",None)
        self.title = kwargs.get("title","NO TITLE")
        self.options = kwargs.get("options",None)
        self.index = 0


    def __str__(self):
        ret_val = f"<< {self.title} >>"

        if self.options:
            ret_val += f"\n{self.index+1} "
            display_object = self.screen.objs[self.options[self.index]]
            if type(display_object) == Menu:
                ret_val += display_object.title
            elif hasattr(display_object,'title'):
                ret_val += display_object.title
            else:
                ret_val += "???"

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
        return self.screen.objs[self.options[self.index]]


    def cancel(self):
        """Process the "cancel" button
        """
        if self.parent is not None:
            return self.screen.objs[self.parent]
        else:
            return self

