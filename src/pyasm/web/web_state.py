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
    def get_display(self):
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

    def __init__(self):
        self.states = []
        self.push()


    def push(self, state=None):
        if state:
            self.current_state = state
        else:
            self.current_state = {}
        self.states.append( self.current_state )


    def get_current(self):
        return self.current_state


    def pop(self):
        self.current_state = self.states.pop()
        return self.states.pop()


    def set_value(self, name, value):
        self.current_state[name] = value


    def get_value(self, name):
        return self.current_state.get(name)


    # DEPRECATED
    def add_state(self, name, value):
        self.current_state[name] = value


    # DEPRECATED
    def get_state(self, name):
        if self.current_state.has_key(name):
            return self.current_state[name]
        else:
            return ""
            
    # DEPRECATED
    def add_state_to_url(self, url):
        # add all of the states to a link
        for name, value in self.current_state.items():
            url.set_option(name, value)




    def get():
        # try getting from the web from
        state = Container.get("WebState")
        if not state:
            state = WebState()
            Container.put("WebState", state)
        return state
    get = staticmethod(get)




