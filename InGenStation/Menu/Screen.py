
import logging

from . import Menu, Action, Reading

class Screen:
    """Main GUI object. Takes input from user, and displays information from
    the system. 
    """
    pass
    def __init__(self, hab_obj):
        # Define our menus
        self.log = logging.getLogger('DragonHab')
        self.log.debug("Init the screen")
        self.objs = {}
        
        # To make this easier, we define things form the bottom up
        t1 = Reading(title="t1")
        t2 = Reading(title="t2")
        t3 = Reading(title="t3")

        temperature_menu = Menu(
            title="Temperature",
            options=[t1,t2,t3])

        self.main_menu = Menu(
            title="Main Menu",
            options=[temperature_menu])

        self.active_object = self.main_menu
        self.active_menu = self.main_menu
  
        
    def __str__(self):
        return self.active_object.__str__()


    def home(self):
        """Reset screen to home position
        """
        self.active_menu = self.main_menu
        self.active_object = self.active_menu


    def up(self):
        """Process the "up" button
        """
        self.active_object = self.active_object.up()
        self._menu_correct()
        return self


    def down(self):
        """Process the "down" button
        """
        self.active_object = self.active_object.down()
        self._menu_correct()
        return self


    def right(self):
        """Process the "right" button
        """
        self.active_object = self.active_object.right()
        self._menu_correct()
        return self


    def left(self):
        """Process the "left" button
        """
        self.active_object = self.active_object.left()
        self._menu_correct()
        return self


    def enter(self):
        """Process the "enter" button
        """
        self.active_object = self.active_object.enter()
        self._menu_correct()
        return self


    def cancel(self):
        """Process the "cancel" button
        """
        self.active_object = self.active_object.cancel()
        self._menu_correct()
        return self


    def _menu_correct(self):
        """Restore menus after odd actions. 
        If active object is None, just return to the last menu we had
        If active object is a menu, make sure the active menu agrees
        """
        if self.active_object == None:
            self.active_object = self.active_menu
        elif type(self.active_object) == Menu:
            self.active_menu = self.active_object

