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

    def init(my):

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
        my.add(main_menu)

class MenuBar(HtmlElement):
    def __init__(my, title, link="", name=None):
        # init
        super(MenuBar, my).__init__()
        #
        my.set_type("div")
        my.set_attr("class","menuBar")
        # name of the js object 
        if name == None:
            my.name = "MenuBar%s" % (my.generate_unique_id())
        else:
            my.name = name
        my.set_id( my.name )
        my.add("&nbsp;")
   
    def add_item(my, MenuButton):
        my.add(MenuButton) 
        

class MenuButton(HtmlElement):
    def __init__(my, title, link="", name=None, active=False, menu=None):
        # init  
        super(MenuButton, my).__init__()
        # title is used as the text tile
        my.title = title 
        # name of the js object 
        if name == None:
            my.name = "MenuButton%s" % (my.generate_unique_id())
        else:
            my.name = name
        my.set_id( my.name )
            
        #link of the object
        my.link = link
        #is object active?  Boolean 1 or 0
        my.active = active
        
        if my.active:
            activestr="menuButton menuButtonActive"
        else:
            activestr="menuButton"
        # check to see if there is a submenu
        if menu != None:
           my.set_attr("OnClick","javascript:return buttonClick(event, '%s');" % menu.get_name())
           my.set_attr("OnMouseOver","javascript:buttonMouseover(event, '%s');" % menu.get_name())
        my.set_type("a")
        my.set_class(activestr)
        my.set_attr("href", link )
        my.add(title)
    def get_title(my):
        return my.title

    def get_link(my):
        return my.link

    def set_name(my, name):
        my.name = name


class Menu(HtmlElement):

    def __init__(my, name=None):
        super(Menu, my).__init__()
        my.set_type("div")
        my.set_class( "menu")
        my.set_attr("OnMouseOver","menuMouseover(event)")
        if name == None:
            my.name = "Menu%s" % (my.generate_unique_id()) 
        else:
            my.name = name
        my.set_id(my.name)
    
    def get_name(my):
        return my.name

    def set_name(my, name):
        my.name = name

    def get_display(my):

        for widget in my.widgets:
            if isinstance(widget, Menu):
                me.add("<span class=\"menuItemText\">Menu 3 Item 4</span>")
        return super(Menu, my).get_display()
        
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
    def __init__(my, title, link=None, name="", menu=None):
        super(MenuItem, my).__init__()
        my.set_type("a")

        my.title = title
        my.link = link
        if name == "":
            my.name = "MenuItem%s" % (my.generate_unique_id()) 
        else:
            my.name = name
        my.set_id(my.name)
        if link != None:
            my.set_attr("href",my.link)
        if menu != None:
            my.set_attr("OnClick","javascript:return false;")
            my.set_attr("OnMouseOver","javascript:menuItemMouseover(event, '%s');" % menu.get_name())
            textSpan=HtmlElement()
            textSpan.set_type("span")
            textSpan.set_class("menuItemText")
            textSpan.add(my.title)
            arrowSpan=HtmlElement()
            arrowSpan.set_type("span")
            textSpan.set_class("menuItemArrow")
            arrowSpan.add("&#9654;")
            
            my.add(textSpan)
            my.add(arrowSpan)
        else:
            my.add(title)

        my.set_class("menuItem" )
        if my.link == "":
            my.set_attr("href", link )

    def get_title(my):
        return my.title

    def get_link(my):
        return my.link

    def set_name(my, name):
        my.name=name

    def get_name(my):
        return my.name



class MenuSeparator(HtmlElement):
    def __init__(my):
        super(MenuSeparator, my).__init__()
        my.set_type("div")
        my.set_class( "menuItemSep")
