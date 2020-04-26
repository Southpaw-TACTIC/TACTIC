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

__all__ = ['SessionVersionWdg', 'LatestVersionWdg', 'LatestVersionContextWdg','VersionWdg']

from pyasm.common import Xml
from pyasm.search import Search
from pyasm.biz import Snapshot
from pyasm.web import *
from pyasm.prod.biz import Render
from pyasm.widget import *


class SessionVersionWdg(AuxDataWdg):

    def preprocess(self):
        self.show_context = FilterCheckboxWdg("show_loaded_context", \
            "show loaded context", css="small smaller" )

    def get_prefs(self):
        return self.show_context

    def get_display(self):
        aux_data = self.get_current_aux_data()
        # latest actually means current here
        session_version = aux_data.get('session_version')
        latest_version =  aux_data.get('latest_version')
        session_context = aux_data.get('session_context')

        latest_context = aux_data.get('latest_context')
        session_revision = aux_data.get('session_revision')
        latest_revision = aux_data.get('latest_revision')
        
        
        session_display = ''
        is_loaded = False
        if session_version == 0:
                session_display = "----"
        else:
            session_display = "v%0.3d" % int(session_version)
            if session_revision:
                session_display = "%s r%0.3d" % (session_display, int(session_revision) )

            if self.show_context.get_value():
                session_display = '%s (%s)' %(session_display, session_context)
            is_loaded = True
        
        widget = Widget()
        if is_loaded:    
            if session_context != latest_context:
                span = SpanWdg('*')
                span.add_style('color', 'red')
                
                widget.add(IconWdg(icon=IconWdg.DOT_RED))
                widget.add(span)
                widget.add(session_display)
            elif latest_version == None:
                widget.add(session_display)

            elif session_version == latest_version:
                widget.add(IconWdg(icon=IconWdg.DOT_GREEN))
                widget.add(session_display)
           
            elif session_version < latest_version:
                widget.add(IconWdg(icon=IconWdg.DOT_RED))
                widget.add(session_display)

            elif session_version > latest_version:
                # this shouldn't happen unless the latest got retired
                # just now
                widget.add(IconWdg(icon=IconWdg.DOT_YELLOW))
                widget.add(session_display)
                widget.add(SpanWdg("(not current)", css='small'))
             
        
        else:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))
            widget.add(session_display)
        
        return widget

    def get_simple_display(self):
        return self.get_display()

class LatestVersionWdg(AuxDataWdg):
    '''This is used in the Latest Version column in Set items table'''
    
    def get_prefs(self):
        self.show_context = FilterCheckboxWdg("show_published_context",\
             "show published context", css="small smaller" )
        return self.show_context

   
    def get_data(self):
        aux_data = self.get_current_aux_data()
        self.session_version = aux_data.get('session_version')
        self.latest_version =  aux_data.get('latest_version')
        self.latest_revision =  aux_data.get('latest_revision')
        self.latest_context = aux_data.get('latest_context')
        
    def get_display(self):
        
        self.get_data()
        display = "v%0.3d" % int(self.latest_version)
        if self.latest_revision:
            display = '%s r0.3d' % (display, int(self.latest_version))

        if self.show_context.get_value():
            display = '%s (%s)' %(display, self.latest_context)
        is_loaded = False
        if self.session_version:
            is_loaded = True
            
        widget = Widget() 
        if is_loaded:    
            if self.session_version == self.latest_version:
                # do not show it if it matches
                pass
            else:
                #widget.add(IconWdg(icon=IconWdg.DOT_RED))
                widget.add(display)
             
        
        else:
            #widget.add(IconWdg(icon=IconWdg.DOT_GREY))
            widget.add(display)
        
        return widget

class LatestVersionContextWdg(BaseTableElementWdg):
    
    def init(self):
        self.has_data = False
        self.is_loaded = None

    def get_data(self):
        self.is_loaded = True
        self.session_version = self.get_option('session_version')
        self.latest_version =  self.get_option('latest_version')
        self.session_context = self.get_option('session_context')
        self.latest_context = self.get_option('latest_context')
        self.session_revision = self.get_option('session_revision')
        self.latest_revision =  self.get_option('latest_revision')

        if not self.latest_version:
            self.latest_version = 0
        
        if self.session_version in ['', None]:
            self.session_version = 0
            self.is_loaded = False
                
        if not self.session_revision:
            self.session_revision = 0
        else:
            self.session_revision = int(self.session_revision)
        if not self.latest_revision:
            self.latest_revision = 0
        else:
            self.latest_revision = int(self.latest_revision)
        self.has_data = True
  
    def get_status(self):
        if not self.has_data:
            self.get_data()
        '''
        is_loaded = False
        if self.session_version:
            is_loaded = True
        '''
        is_loaded = self.is_loaded
        if is_loaded:    
            if self.session_context != self.latest_context:
                return VersionWdg.MISMATCHED_CONTEXT
            elif self.session_version == self.latest_version:
                if self.session_revision == self.latest_revision:
                    return VersionWdg.UPDATED 
                elif self.session_revision < self.latest_revision:
                    return VersionWdg.OUTDATED
                else:
                    return VersionWdg.NOT_CURRENT

            elif self.session_version < self.latest_version:
                return VersionWdg.OUTDATED
            else: # session has a version not found in db
                return VersionWdg.NOT_CURRENT
        else:
             return VersionWdg.NOT_LOADED

    def get_display(self):
        
        self.get_data()
        display = "v%0.3d" % int(self.latest_version)
        if self.latest_revision:
            display = "%s r%0.3d" % (display, int(self.latest_revision))
        
        status = self.get_status()
        widget = VersionWdg.get(status)
        widget.add(display)
        
        return widget

class VersionWdg(Widget):
    '''Widget that displays the status/currency of a loaded object in the UI'''
    MISMATCHED_CONTEXT, UPDATED, OUTDATED, NOT_CURRENT, NOT_LOADED = xrange(5)
    def get(cls, status):
        widget = Widget()
        if status == cls.MISMATCHED_CONTEXT:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))
            widget.add("*")
        elif status == cls.UPDATED:
            widget.add(IconWdg(icon=IconWdg.DOT_GREEN))
        elif status == cls.NOT_CURRENT:
            widget.add(IconWdg(name='not current', icon=IconWdg.DOT_YELLOW))
        elif status == cls.OUTDATED:
            widget.add(IconWdg(name='outdated', icon=IconWdg.DOT_RED))
        elif status == cls.NOT_LOADED:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))
        else:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))

        return widget

    get = classmethod(get)

