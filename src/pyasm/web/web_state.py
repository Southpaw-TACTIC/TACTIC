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

__all__ = ['WebState']


'''Class that stores the global environmental state that a given widget lives
in.  This state can be stacked

Usage:

    # a widget will want to define a state and pass it through the hierarchy
    web_state = WebState.get()
    state = {
        'search_key': search_key,
        'process': process
    }
    web_state.push(state)

    # later a widget will be able to retrieve the state as such
    web_state = WebState.get()
    search_key = web_state.get_value("search_key")


    # common usage would be for a widget to only define states in the
    # get_display method.  This ensures proper hierarchical propogation of
    # the state
    def get_display(my):
        state = {}
        web_state.push(state)

        div = DivWdg() 

        # need to pass through add
        xx = Whatever()
        div.add(xx, use_state=True)

        web_state.pop()


        return div
'''

from pyasm.common import Container



class WebState(object):

    def __init__(my):
        my.states = []
        my.push()


    def push(my, state=None):
        if state:
            my.current_state = state
        else:
            my.current_state = {}
        my.states.append( my.current_state )


    def get_current(my):
        return my.current_state


    def pop(my):
        my.current_state = my.states.pop()
        return my.states.pop()


    def set_value(my, name, value):
        my.current_state[name] = value


    def get_value(my, name):
        return my.current_state.get(name)


    # DEPRECATED
    def add_state(my, name, value):
        my.current_state[name] = value


    # DEPRECATED
    def get_state(my, name):
        if my.current_state.has_key(name):
            return my.current_state[name]
        else:
            return ""
            
    # DEPRECATED
    def add_state_to_url(my, url):
        # add all of the states to a link
        for name, value in my.current_state.items():
            url.set_option(name, value)




    def get():
        # try getting from the web from
        state = Container.get("WebState")
        if not state:
            state = WebState()
            Container.put("WebState", state)
        return state
    get = staticmethod(get)




