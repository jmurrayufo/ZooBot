
import json
import logging

from . import Menu, Action, Reading

class Screen:
    """Main GUI object. Takes input from user, and displays information from
    the system. 
    """


    def __init__(self, hab_obj, json_file):
        # Define our menus
        self.log = logging.getLogger('DragonHab')
        self.log.debug("Init the screen")
        self.objs = {}
        # self.actions = {}
        # self.alerts = {}
        # self.menus = {}
        # self.readings = {}
        # self.timers = {}

        with open(json_file,'r') as fp:
            data = json.load(fp)

        self.log.debug("Load actions")
        for item in data['actions']:
            pass

        self.log.debug("Load alerts")
        for item in data['alerts']:
            pass

        self.log.debug("Load menus")
        for item in data['menus']:
            self.objs[item['id']] = Menu(
                self,
                id = item['id'],
                title = item['title'],
                parent = item['parent'],
                options = item['options']
                )

        self.log.debug("Load readings")
        for item in data['readings']:
            self.objs[item['id']] = Reading(
                self,
                id = item['id'],
                title = item['title'],
                reading = item['reading'],
                source = hab_obj
                )

        self.log.debug("Load timers")
        for item in data['timers']:
            pass

        # assert 0


        # To make this easier, we define things form the bottom up
        self.home()
  
        
    def __str__(self):
        return self.active_object.__str__()


    def home(self):
        """Reset screen to home position
        """
        self.active_menu = self.objs[0]
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

