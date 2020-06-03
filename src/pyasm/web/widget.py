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

__all__ = [ 'WidgetException', 'Widget', 'WidgetSettings', 'StringWdg', 'Html', 'Url', 'ClassWdg', 'MethodWdg', 'WidgetSettingSaveCbk' ]

import types, string, urllib, random

try:
    import urlparse
except:
    from urllib import parse as urlparse

try:
    from cStringIO import StringIO as Buffer
except:
    from io import StringIO as Buffer

import six
basestring = six.string_types


from pyasm.common import *
from pyasm.biz import Project
from pyasm.security import *
from pyasm.search import *

from .web_container import *
from .web_state import *

import sys

if sys.version_info[0] < 3:
    IS_Pv3 = False
else:
    IS_Pv3 = True


class WidgetException(Exception):
    pass


class Widget(object):
    '''Base class for all display widgets'''

    def _get_my_widgets(self):
        if self._widgets == None:
            self._widgets = []
        return self._widgets
    def _set_my_widgets(self, widgets):
        self._widgets = widgets
    widgets = property(_get_my_widgets, _set_my_widgets)

    def _get_my_named_widgets(self):
        if self._named_widgets == None:
            self._named_widgets = {}
        return self._named_widgets
    def _set_my_named_widgets(self, named_widgets):
        self._named_widgets = named_widgets
    named_widgets = property(_get_my_named_widgets, _set_my_named_widgets)

    def _get_my_sobjects(self):
        if self._sobjects == None:
            self._sobjects = []
        return self._sobjects
    def _set_my_sobjects(self, sobjects):
        self._sobjects = sobjects
    sobjects = property(_get_my_sobjects, _set_my_sobjects)

    def _get_my_options(self):
        if self._options == None:
            self._options = {}
        return self._options
    def _set_my_options(self, options):
        self._options = options
    options = property(_get_my_options, _set_my_options)


    # This is said to reduce memory, but it doesn't seem to
    #__slots__ = ['name', 'title', 'search','_sobjects','current_index','_widgets','named_widgets','typed_widgets','is_top','security_denied','_options','state']


    def __init__(self, name=""):
        self.name = name
        self.title = ''
        self.search = None
        #self.sobjects = []
        self._sobjects = None
        self.current_index = -1
        #self.widgets = []
        self._widgets = None
        self._named_widgets = None
        self.typed_widgets = None
        self.is_top = False

        self.security_denied = False

        #self.options = {}
        self._options = None
        self.state = None

        # make sure the init function catches security exceptions
        try:
            # quick test to see if the class_init function exists
            """
            if hasattr(self, "class_init"):
                # do a class initialization if necessary
                inits = Container.get("Widget:class_init")
                if inits == None:
                    inits = {}
                    Container.put("Widget:class_init", inits )

                class_name = Common.get_full_class_name(self)
                if class_name not in inits:
                    inits[class_name] = ""
                    self.class_init()
            """

            # call the main initialization function
            self.init()

        except SecurityException as e:
            self.__cripple_widget(e)


    # DEPRECATED
    """
    DO NOT REMOVE
    def class_init(self):
        '''this function is called once per class.  It is used initialize
        global features of this class as opposed to a particular instance
        of a widget'''
        # Note: this is should not be uncommented.  The code above uses
        # the existence of this function to optimize
        pass
    """

    def _use_bootstrap(self):
        return True
        from pyasm.biz import ProjectSetting
        ui_library = ProjectSetting.get_value_by_key("feature/ui_library") or "bootstrap_material"
        if ui_library not in ['bootstrap', 'bootstrap_material']:
            return False
        
    
    def init_dynamic(arg_dict):
        '''it returns a dynamically instantiated widget'''
        raise WidgetException("must override [init_dynamic] method")
    
    init_dynamic = staticmethod(init_dynamic)


    def init(self):
        '''initialize all of the widgets.  Classes override this method
        for initialization'''
        pass


    def __cripple_widget(self, e):
        '''function that basically makes this widget useless for display
        purposes.  This ensures that even if a function is overridden,
        it will not display correctly'''

        def do_search():
            pass
        self.do_search = do_search

        def get_display():
            widget = StringWdg("Security Denied: '%s' with error: '%s'<br/>" \
                % (self.__class__.__name__, str(e)) )
            return widget
        self.get_display = get_display;


    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state



    def check_access(cls, group, key, access, value=None, is_match=False, default="edit"):
        '''convenience function to check the security level to the access
        manager'''
        security = Environment.get_security()
        return security.check_access(group, key, access, value, is_match, default=default)
    check_access = classmethod(check_access)


    def get_access(cls, group, key, default=None):
        security = Environment.get_security()
        return security.get_access(group, key, default=None)
    get_access = classmethod(get_access)

    def get_top(self):
        '''return the top element.  In the case of widget, this is the instance
        itself'''
        return self


    def get_name(self):
        '''returns the name of the widget'''
        return self.name

    def get_class_name(self):
        '''returns the class that this sobject is an instance of'''
        return Common.get_full_class_name(self)
  
    def set_title(self, title):
        self.title = title

    def set_name(self, name):
        self.name = name

    def set_as_top(self):
        self.is_top = True


    def add_widget(self,widget,name=None,wdgtype=None,index=None,use_state=False):
        '''add a child widget to this widget'''
        if not widget:
            return
        self._add_widget(widget,name,wdgtype,index=index)


    def add(self,widget,name=None,wdgtype=None,index=None,use_state=False):
        '''Convenience function to add a child widget. Does the same
        as add widget'''
        if not widget:
            return
        self._add_widget(widget,name,wdgtype,index=index)



    def _add_widget(self,widget,name=None,wdgtype=None,index=None,use_state=False):
        '''actually adds the child widget.  This is a protected member
        and allows the adding of widgets internally.  Subclasses can
        override add_widget to add to an internal widget instead'''

        assert widget != None

        if isinstance(widget, basestring):
            widget = StringWdg(widget)
        elif isinstance(widget, (int, float)):
            widget = StringWdg(str(widget))
        elif not isinstance(widget,Widget):
            widget = StringWdg(str(widget))


        if name:
            # find if the old widget is in the dictionary
            if self.named_widgets == None:
                self.named_widgets = {}


            if name in self.named_widgets:

                # replace the old widget with the new one
                self.__replace_widget(widget, name)
            else:
                # or just append a new on if it is not in the dictionary
                if index == None:
                    self.widgets.append(widget)
                else:
                    self.widgets.insert(index, widget)


            self.named_widgets[name] = widget
    

        # if there is no name, just append
        else:
            if index == None:
                self.widgets.append(widget)
            else:
                self.widgets.insert(index, widget)



        if wdgtype != None and wdgtype != "":

            if self.typed_widgets == None:
                self.typed_widgets = {}

            if wdgtype not in self.typed_widgets:
                self.typed_widgets[wdgtype] = []
            self.typed_widgets[wdgtype].append(widget)


        if use_state:
            self.state = WebState.get().get_current()


    def __replace_widget(self, widget, name):
        try:
            old_widget = self.named_widgets[name]
            index = self.widgets.index(old_widget)
        except ValueError:
            pass
        else:
            self.widgets[index] = widget

    def set_widget(self, widget, name):
        assert name != None and name.strip() != ''
        self.__replace_widget(widget, name) 
        self.named_widgets[name] = widget

    def get_widget(self, name):
        return self.named_widgets.get(name)


    def get_widgets_by_type(self,wdgtype):
        if wdgtype in self.typed_widgets:
            return self.typed_widgets[wdgtype]
        else:
            return []


    def get_widgets(self):
        return self.widgets


    def set_parent(self, parent):
        return parent.add(self)



    """
    def add_command(self, command):
        '''deprecated: use CommandDelegator'''
        self.commands.append(command)
    """

    def set_search(self, search):
        '''sets the search that will be performed in the search phase'''
        self.search = search

    def set_sobjects(self,sobjects,search=None):
        '''store the sobjects that this widget will act upon'''
        #print("set_sobjects")
        if search:
            self.search = search
        self.sobjects = sobjects
        self.current_index = 0

        # DEPRECATED: is this really necessary???
        # set all of the sobjects to all of the child widgets
        for widget in (self.widgets):
            widget.set_sobjects(sobjects,search)


    def set_sobject(self,sobject,search=None):
        '''convenience function to set only one sobject'''
        if sobject:
            self.set_sobjects([sobject],search)

    def is_sobjects_explicitly_set(self):
        return self.current_index != -1

    def get_sobjects(self):
        return self.sobjects


    def set_current_index(self, index):
        '''sets the index of the current sobject'''
        self.current_index = index

        for widget in (self.widgets):
            widget.set_current_index(index)
    
    def get_current_index(self):
        return self.current_index

    def get_current_sobject(self):
        if self.current_index == -1 or len(self.sobjects) == 0:
            return None
        else:
            return self.sobjects[self.current_index]



    def alter_search(self, search):
        '''Alter any search that comes through this widget'''
        for widget in self.widgets:
            widget.alter_search( search )

    def do_search(self):
        '''Perform any searches that were created in the init function.
        Returns a list of SObjects'''
        # if no search is defined in this class, then skip this
        if self.search != None:
            # give the opportunity for each of the lower widgets to alter the
            # search
            self.alter_search( self.search )

            # actually do the search and notify all of the children
            self.sobjects = self.search.get_sobjects()

        # go through each widget and perform their searches
        for widget in self.widgets:
            widget.do_search()


        # set the sobjects from this search
        # FIXME: this has the effect of overriding any lower searches
        # that may exist.  This is probably not desired behaviour
        # and should be fixed
        if self.search != None:
            self.set_sobjects( self.sobjects, self.search )



    def check_security(self):
        '''give the widget a callback that allows it to check security.
        This function will return if the widget is in a state that
        is acceptable to the security manager'''
        # execute all of the security checks of the lower widgets.  If
        # any fail with a security exception
        for widget in self.widgets:
            try:
                widget.check_security()
            except SecurityException as e:
                self.__cripple_widget(e)


    def explicit_display(self, cls=None):
        if not cls:
            child = self.get_display()
        else:
            child = cls.get_display(self)
        if child:
            widget = None
            if isinstance(child,basestring):
                widget = StringWdg(child)
                widget.explicit_display()
            elif isinstance(child,Widget):
                widget = child.get_display()
                if widget:
                    if isinstance(widget,basestring):
                        widget = StringWdg(widget)
                    widget.explicit_display()
            elif isinstance(child,Html):
                widget = StringWdg(child.getvalue())
                widget.explicit_display()
            
            del(child)
            del(widget)


    def get_display(self):
        '''Draw all of the contents'''
        for widget in self.widgets:
            #try:
            #    widget.explicit_display()
            #except SecurityException:
            #    # do nothing for now
            #    pass
            widget.explicit_display()

   


    def get_buffer(self, cls=None):
        '''create a new buffer and execute the get_display of this widget.
        This is useful for caching the display of a widget for multiple
        reuse'''
        # have to bake the widget in a new buffer
        WebContainer.push_buffer()
        try:
            self.explicit_display(cls)
        finally:
            buffer = WebContainer.pop_buffer()
        return buffer

    def get_buffer_display(self, cls=None):
        '''get a new buffer's value and execute the get_display of this widget.
        This is useful for caching the display of a widget for multiple
        reuse'''
        buffer = self.get_buffer(cls)
        value = buffer.getvalue()
        buffer.clear()

        return value

    def render(self, cls=None):
        '''get a new buffer's value and execute the get_display of this widget.
        This is useful for caching the display of a widget for multiple
        reuse'''
        return self.get_buffer(cls).getvalue()




    def get_class_display(cls, self):
        '''Explicitly use the get_display function of a provided class for a
        particular instance.  This is rarely used and should only be used
        carefully.  It is intended to break infinite loops when trying to
        build a composite widget while maintaining an internal widget's
        interface.  For example see: pyasm.wdget.FilterCheckboxWdg where
        a span is wrapped around a checkbox, but the widget needs to have the
        internal checkbox's interface.
        '''
        return self.get_buffer(cls).getvalue()
    get_class_display = classmethod(get_class_display)

    def get_buffer_on_exception(cls, last_buffer=1):
        '''resets everything currently in the stack of buffers.  This is mainly
        used when an exception occurs to retrieve all of the widgets that
        has been assembled so far, but was not returned because
        of the exception'''
        widget = Widget()
        num_buffers = WebContainer.get_num_buffers()

        # NOTE: this is weird ... last buffer is dependent on something.
        # Not sure what.  For example, it depends on the level of TabWdg
        # However, this appears to be working

        for i in range(num_buffers, last_buffer, -1):
            buffer = WebContainer.pop_buffer()
            widget.add(buffer)
        return widget




    def is_ajax(cls, check_name=True):
        ''' return True if it is an Ajax wdg on construction
        NOTE: there is a is_from_ajax() in AjaxWdg'''
        # Since TACTIC is 99.9% ajax now, this is probably not relevant
        web = WebContainer.get_web()
        ajax_class = web.get_form_value("widget")
        is_ajax = False
        if web.get_form_value("ajax") == "true":
            if check_name:
                module, class_name = Common.breakup_class_path(ajax_class)
                if class_name == cls.__name__:
                    is_ajax = True
            else:
                is_ajax = True

        return is_ajax

    is_ajax = classmethod(is_ajax)
    
    def has_restriction(cls):
        ''' check if the user is restricted to see this secure wdg based on class name '''
        security = Environment.get_security()
        key = cls.__name__
        if security.check_access("public_wdg", key, access='deny', is_match=True):
            return True
        return False
    has_restriction = classmethod(has_restriction)

    def has_access(cls):
        ''' check if the user has access to this secure wdg based on class name '''
        security = Environment.get_security()
        key = cls.__name__
        if security.check_access("secure_wdg", key, access='view'):
            return True
        return False

    has_access = classmethod(has_access)

    def dump(self):
        print(self)
        for widget in self.widgets:
            print("child: \t", widget)

        for widget in self.widgets:
            widget.dump()


    def generate_unique_id(base='', wdg='HtmlWdg', is_random=False):
        ref_count = Container.get("%s:ref_count" %wdg)
        unique_code = Container.get("%s:unique_code" %wdg)
        if ref_count == None:
            ref_count = 0
            unique_code = ''.join([ Common.randchoice('abcdefghijklmno') for i in range(0, 6)])
            Container.put("%s:unique_code" %wdg, unique_code)
      
        Container.put("%s:ref_count" %wdg, ref_count+1)
        if is_random:
            base = '%s_%s' %(base, unique_code) 
       
        if not base:
            base = "unique"
        
            
        return "%s_%s" % (base, ref_count)
    generate_unique_id = staticmethod(generate_unique_id)

    
# Determine if there is a TACTIC database in this AppServer
DATABASE = Environment.has_tactic_database()

class WidgetSettings(SObject):
    '''sobject for all storing settings for a widget.  Note that this class
    respects whether there is a tactic database.  If not, widget settings will
    fail gracefully.  This is used in SimpleAppServer'''

    SEARCH_TYPE = "sthpw/wdg_settings"


    #
    # Simple explicit functions with no manipulation of data
    #

    def get_value_by_key(key, auto_create=True, default="", is_json=False):
        if not DATABASE:
            return default

        settings = WidgetSettings.get_by_key(key)
        if not settings:
            return default

        value_str = settings.get_value("data")



        if is_json:
            if not value_str:
                value_str = default
            else:
                try:
                    value_str = jsonloads(value_str)
                except Exception as e:
                    print("WARNING: ", e)
                    return default


        return value_str
    get_value_by_key = staticmethod(get_value_by_key)


    def set_value_by_key(key, value, default=""):
        '''set and commit the value'''
        if not DATABASE:
            return default

        if isinstance(value, list) or isinstance(value, dict):
            value = jsondumps(value)

        settings = WidgetSettings.get_by_key(key, auto_create=True)
        settings.set_value("data", value)
        settings.commit(triggers=False)
        return value
    set_value_by_key = staticmethod(set_value_by_key)




    #
    # older methods ... need to clean up ... to many assumptions
    #

    def get_key_values(key, auto_create=True):
        '''return the values as an array: WARNING: this will split on ||
        to get an array value'''
        if not DATABASE:
            return []

        settings = WidgetSettings.get_by_key(key, auto_create=auto_create)
        if not settings:
            return []
        value_str = settings.get_value("data")
        if not value_str:
            return []
        else:
            return value_str.split("||")
    get_key_values = staticmethod(get_key_values)




    def set_key_values(key, values):
        if not DATABASE:
            return

        assert(key)
        settings = WidgetSettings.get_by_key(key)
        if not settings:
            return 

        tmp_array = []
        for x in values:
            if not x:
                continue
            if not isinstance(x, basestring):
                x = str(x)
            tmp_array.append(x)
            
        values_str = "||".join(tmp_array)
        
        # if the current value is different from stored value, then update
        if values_str == settings.get_value('data'):
            return
        
        settings.set_value("data", values_str)
        settings.commit(triggers=False)
    set_key_values = staticmethod(set_key_values)



    def get_wdg_value(widget, widget_name):
        '''boilerplate function which gets the value of a widget'''
        # ensure uniqueness of a key for the settings
        class_name = Common.get_full_class_name(widget)
        value = WidgetSettings.get_key_value(class_name, widget_name)
        return value

    get_wdg_value = staticmethod(get_wdg_value)



    # DEPRECATED
    def get_key_value(key, widget_name):

        #print('DEPRECATED: WidgetSettings.get_key_value()')

        # web form value overrides all others
        web = WebContainer.get_web()
        value = web.get_form_value(widget_name,raw=True)

        # make it so the database doesn't need to be present
        if not DATABASE:
            return value

        settings_key = "%s|%s" % (key,widget_name)
        settings = WidgetSettings.get_by_key(settings_key)
        if not settings:
            return value

        # if value is empty then get it from the database
        if value == None:
            # get the widget settings object for this filter
            value = settings.get_value("data")
        # if the value is different from the settings then replace in
        # the database
        elif settings.get_value("data") != value:
            settings.set_value("data",value)
            settings.commit()

        return value
    get_key_value = staticmethod(get_key_value)



    def get_by_key(key, auto_create=False):
        login = WebContainer.get_user_name()
        dict_key = '%s:%s' %(WidgetSettings.SEARCH_TYPE, login) 
        settings_dict = Container.get(dict_key)
        setting = None
        if not settings_dict:
            
            settings_dict = {}
            Container.put(dict_key, settings_dict)
                   
            search = Search(WidgetSettings.SEARCH_TYPE)
            search.add_filter("project_code", Project.get_project_code())
            search.add_filter("login", login)
            settings = search.get_sobjects()
            for setting in settings:
                settings_dict[setting.get_value('key')] = setting
                
        setting = settings_dict.get(key)
            
        # autocreate if it does not exist
        if auto_create and setting == None:
            setting = WidgetSettings.create(key)
            
            settings_dict[setting.get_value('key')] = setting

        return setting
    get_by_key = staticmethod(get_by_key)



    def create(key):
        login = WebContainer.get_login().get_login() 

        settings = SObjectFactory.create(WidgetSettings.SEARCH_TYPE)
        settings.set_value("key",key)
        settings.set_value("login",login)
        settings.set_value("data","")
        settings.set_value("project_code", Project.get_project_code())
        settings.commit(triggers=False) 

        return settings
    create = staticmethod(create)


from pyasm.command import Command
class WidgetSettingSaveCbk(Command):
    '''Callback to save a WidgetSetting'''
    def execute(self):
        data = self.kwargs.get('data')
        key = self.kwargs.get('key')
        value = WidgetSettings.set_value_by_key(key, data)
        self.info['data'] = value

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


class StringWdg(Widget):
    def __init__(self,string=""):
        self.widgets = []
        self.string = string
        self.name = None

    def do_search(self):
        pass
    
    def check_security(self):
        pass
    
    def get_display(self):
        html = WebContainer.get_buffer()

        # write directly to the StringIO
        if not IS_Pv3:
            if isinstance(self.string, unicode):
                self.string = Common.process_unicode_string(self.string)
        html.get_buffer().write(self.string)
    
class ClassWdg(Widget):
    def __init__(self, class_type=None):
        self.widgets = []
        if IS_Pv3:
            assert isinstance(class_type, type)
        else:
            assert isinstance(class_type, types.TypeType)

        self.class_type = class_type
    
    def do_search(self):
        pass
    
    def check_security(self):
        pass
    
    def get_display(self):    
        return self.class_type()
        
    def get_class_name(self):
        return '%s.%s'%(self.class_type.__module__, self.class_type.__name__)
    
class MethodWdg(Widget):
    def __init__(self, method =''):
        self.widgets = []
        assert isinstance(method, types.MethodType)
        self.method = method
    def do_search(self):
        pass
    
    def check_security(self):
        pass
    
    def get_display(self):    
        return self.method()
        
    def get_class_name(self):
        return '%s.%s'%(self.method.im_class.__module__, \
            self.method.im_class.__name__)

    def get_function_name(self):
        return self.method.im_func.func_name

class Html(Base):
    '''String buffer class for html code'''

    def __init__(self):
        self._buffer = Buffer()

    def __del__(self):
        self.clear()

    def write(self, html):
        if isinstance(html, basestring):
            self._buffer.write(html)
        #elif isinstance(html, int):
        elif isinstance(html, (int, float)):
            self._buffer.write( str(html) )
        elif isinstance(html,Html):
            self._buffer.write(html.getvalue())
        elif not html:
            pass
        else:
            raise WidgetException("Cannot handle [%s] type" % html)


    def writeln(self, html):
        self.write(html)
        self._buffer.write("\n")


    def getvalue(self):
        '''This exists to maintain backwards compatibility when this class
        used the StringIO class directly.'''
        return self._buffer.getvalue()

    def get_display(self):
        return self._buffer.getvalue()

    def to_string(self):
        return self._buffer.getvalue()

    def get_buffer(self):
        return self._buffer

    def clear(self):
        self._buffer.close()





class Url(Base):
    '''class which builds up a url'''

    def __init__(self, base=""):
        self.base = base
        self.options = {}

    def set_base(self, base):
        self.base = base

    def append_to_base(self, extra):
        if extra.startswith("/"):
            self.base += extra
        else:
            self.base += "/%s" % extra



    def set_option(self, name, value):
        self.options[name] = value


    def get_info(self):
        url = self.to_string()
        urlparts = urlparse.urlsplit(url)
        return urlparts

    def get_protocol(self):
        return self.get_info()[0]

    def get_host(self):
        return self.get_info()[1]


    def get_selector(self):
        return self.get_info()[2]



    def to_string(self):

        options_list = []
        for name,value in self.options.items():

            if isinstance(value, list):
                for item in value:
                    if not isinstance(value, basestring):
                        value = str(value)
                    encoded = urlparse.quote_plus(value.encode('utf'))
                    options_list.append("%s=%s" % (name,encoded) )
            else:
                if not isinstance(value, basestring):
                    value = str(value)
                encoded = urlparse.quote_plus(value.encode('utf'))
                options_list.append("%s=%s" % (name,encoded) )

        options_str = "&".join(options_list)

        if options_str != "":
            url = "%s?%s" % (self.base, options_str)
        else:
            url = self.base

        return url


    def add_web_state(self):
        '''add web state paramenters to this url'''
        state = WebState.get()
        state.add_state_to_url(self)


    def get_protocol(self):
        parts = self.base.split("://")
        return parts[0]



    def get_url(self):
        return self.to_string()


    def get_base(self):
        return self.base




