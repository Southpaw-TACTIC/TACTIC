###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['MenuTest', 'MenuBar', 'MenuButton', 'MenuItem', 'MenuSeparator']


from pyasm.web import *
from pyasm.widget import *


class MenuTest(Widget):

    def init(self):

        # create the main menu widget.  This may need to be a MainMenuWdg class
        main_menu = MenuWdg("Main")

        # create a simple link menu
        site_menu = MenuWdg("Sites")
        site_menu.add( MenuItem("Yahoo", "http://www.yahoo.com") )
        site_menu.add( MenuItem("Ebay", "http://www.ebay.com") )
        site_menu.add( MenuItem("Amazon", "http://www.amazon.com") )

        # add a separator
        site_menu.add( MenuSeparator() )

        # add an arbitrary widget - not sure about this one
        #widget = HtmlElement.href("Google", "http://www.google.com")
        #site_menu.add( MenuItem(widget) )

        # add a submenu
        sub_menu = MenuWdg("Work")
        sub_menu.add( MenuItem("Alias", "http://www.alias.com") )
        sub_menu.add( MenuItem("Nelvana", "http://www.nelvana.com") )

        core_menu = MenuItem("Core", "http://www.corefa.com") 
        sub_menu.add( core_menu )

        # add the menu to the main menu
        main_menu.add(site_menu)

        # add another widget to the main menu
        help_menu = MenuWdg("Help")
        help_menu.add( MenuItem("About Southpaw", "httpd//www.bankrupt.com") )
        main_menu.add(help_menu)


        # add it to this widget
        self.add(main_menu)

class MenuBar(HtmlElement):
    def __init__(self, title, link="", name=None):
        # init
        super(MenuBar, self).__init__()
        #
        self.set_type("div")
        self.set_attr("class","menuBar")
        # name of the js object 
        if name == None:
            self.name = "MenuBar%s" % (self.generate_unique_id())
        else:
            self.name = name
        self.set_id( self.name )
        self.add("&nbsp;")
   
    def add_item(self, MenuButton):
        self.add(MenuButton) 
        

class MenuButton(HtmlElement):
    def __init__(self, title, link="", name=None, active=False, menu=None):
        # init  
        super(MenuButton, self).__init__()
        # title is used as the text tile
        self.title = title 
        # name of the js object 
        if name == None:
            self.name = "MenuButton%s" % (self.generate_unique_id())
        else:
            self.name = name
        self.set_id( self.name )
            
        #link of the object
        self.link = link
        #is object active?  Boolean 1 or 0
        self.active = active
        
        if self.active:
            activestr="menuButton menuButtonActive"
        else:
            activestr="menuButton"
        # check to see if there is a submenu
        if menu != None:
           self.set_attr("OnClick","javascript:return buttonClick(event, '%s');" % menu.get_name())
           self.set_attr("OnMouseOver","javascript:buttonMouseover(event, '%s');" % menu.get_name())
        self.set_type("a")
        self.set_class(activestr)
        self.set_attr("href", link )
        self.add(title)
    def get_title(self):
        return self.title

    def get_link(self):
        return self.link

    def set_name(self, name):
        self.name = name


class Menu(HtmlElement):

    def __init__(self, name=None):
        super(Menu, self).__init__()
        self.set_type("div")
        self.set_class( "menu")
        self.set_attr("OnMouseOver","menuMouseover(event)")
        if name == None:
            self.name = "Menu%s" % (self.generate_unique_id()) 
        else:
            self.name = name
        self.set_id(self.name)
    
    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_display(self):

        for widget in self.widgets:
            if isinstance(widget, Menu):
                me.add("<span class=\"menuItemText\">Menu 3 Item 4</span>")
        return super(Menu, self).get_display()
        
class MenuItem(HtmlElement):
    ''' A MenuItem is added to a Menu Object to create individual items in
    the menu (duh!)  

    usage: MenuItem(title, link, name, menu)

    where:  title = Display name of the menu Item
            link = (optional) href link of the item 
            name = (optional) javascript name of the item (Can be left blank,
            name will be created automatically
            menu = put a submenu in place of a menuitem
   ''' 
    def __init__(self, title, link=None, name="", menu=None):
        super(MenuItem, self).__init__()
        self.set_type("a")

        self.title = title
        self.link = link
        if name == "":
            self.name = "MenuItem%s" % (self.generate_unique_id()) 
        else:
            self.name = name
        self.set_id(self.name)
        if link != None:
            self.set_attr("href",self.link)
        if menu != None:
            self.set_attr("OnClick","javascript:return false;")
            self.set_attr("OnMouseOver","javascript:menuItemMouseover(event, '%s');" % menu.get_name())
            textSpan=HtmlElement()
            textSpan.set_type("span")
            textSpan.set_class("menuItemText")
            textSpan.add(self.title)
            arrowSpan=HtmlElement()
            arrowSpan.set_type("span")
            textSpan.set_class("menuItemArrow")
            arrowSpan.add("&#9654;")
            
            self.add(textSpan)
            self.add(arrowSpan)
        else:
            self.add(title)

        self.set_class("menuItem" )
        if self.link == "":
            self.set_attr("href", link )

    def get_title(self):
        return self.title

    def get_link(self):
        return self.link

    def set_name(self, name):
        self.name=name

    def get_name(self):
        return self.name



class MenuSeparator(HtmlElement):
    def __init__(self):
        super(MenuSeparator, self).__init__()
        self.set_type("div")
        self.set_class( "menuItemSep")
