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

import types, string, urllib, cStringIO, urlparse, random

from pyasm.common import *
from pyasm.security import *
from pyasm.search import *

from web_container import *
from web_state import *
from pyasm.biz import Project


class WidgetException(Exception):
    pass


class Widget(object):
    '''Base class for all display widgets'''

    def _get_my_widgets(my):
        if my._widgets == None:
            my._widgets = []
        return my._widgets
    def _set_my_widgets(my, widgets):
        my._widgets = widgets
    widgets = property(_get_my_widgets, _set_my_widgets)

    def _get_my_named_widgets(my):
        if my._named_widgets == None:
            my._named_widgets = {}
        return my._named_widgets
    def _set_my_named_widgets(my, named_widgets):
        my._named_widgets = named_widgets
    named_widgets = property(_get_my_named_widgets, _set_my_named_widgets)

    def _get_my_sobjects(my):
        if my._sobjects == None:
            my._sobjects = []
        return my._sobjects
    def _set_my_sobjects(my, sobjects):
        my._sobjects = sobjects
    sobjects = property(_get_my_sobjects, _set_my_sobjects)

    def _get_my_options(my):
        if my._options == None:
            my._options = {}
        return my._options
    def _set_my_options(my, options):
        my._options = options
    options = property(_get_my_options, _set_my_options)


    # This is said to reduce memory, but it doesn't seem to
    #__slots__ = ['name', 'title', 'search','_sobjects','current_index','_widgets','named_widgets','typed_widgets','is_top','security_denied','_options','state']


    def __init__(my, name=""):
        my.name = name
        my.title = ''
        my.search = None
        #my.sobjects = []
        my._sobjects = None
        my.current_index = -1
        #my.widgets = []
        my._widgets = None
        my._named_widgets = None
        my.typed_widgets = None
        my.is_top = False

        my.security_denied = False

        #my.options = {}
        my._options = None
        my.state = None

        # make sure the init function catches security exceptions
        try:
            # quick test to see if the class_init function exists
            """
            if hasattr(my, "class_init"):
                # do a class initialization if necessary
                inits = Container.get("Widget:class_init")
                if inits == None:
                    inits = {}
                    Container.put("Widget:class_init", inits )

                class_name = Common.get_full_class_name(my)
                if not inits.has_key(class_name):
                    inits[class_name] = ""
                    my.class_init()
            """

            # call the main initialization function
            my.init()

        except SecurityException as e:
            my.__cripple_widget(e)


    # DEPRECATED
    """
    DO NOT REMOVE
    def class_init(my):
        '''this function is called once per class.  It is used initialize
        global features of this class as opposed to a particular instance
        of a widget'''
        # Note: this is should not be uncommented.  The code above uses
        # the existence of this function to optimize
        pass
    """
    
    def init_dynamic(arg_dict):
        '''it returns a dynamically instantiated widget'''
        raise WidgetException("must override [init_dynamic] method")
    
    init_dynamic = staticmethod(init_dynamic)


    def init(my):
        '''initialize all of the widgets.  Classes override this method
        for initialization'''
        pass


    def __cripple_widget(my, e):
        '''function that basically makes this widget useless for display
        purposes.  This ensures that even if a function is overridden,
        it will not display correctly'''

        def do_search():
            pass
        my.do_search = do_search

        def get_display():
            widget = StringWdg("Security Denied: '%s' with error: '%s'<br/>" \
                % (my.__class__.__name__, str(e)) )
            return widget
        my.get_display = get_display;


    def set_state(my, state):
        my.state = state

    def get_state(my):
        return my.state



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

    def get_top(my):
        '''return the top element.  In the case of widget, this is the instance
        itself'''
        return my


    def get_name(my):
        '''returns the name of the widget'''
        return my.name

    def get_class_name(my):
        '''returns the class that this sobject is an instance of'''
        return Common.get_full_class_name(my)
  
    def set_title(my, title):
        my.title = title

    def set_name(my, name):
        my.name = name

    def set_as_top(my):
        my.is_top = True


    def add_widget(my,widget,name=None,wdgtype=None,index=None,use_state=False):
        '''add a child widget to this widget'''
        if not widget:
            return
        my._add_widget(widget,name,wdgtype,index=index)


    def add(my,widget,name=None,wdgtype=None,index=None,use_state=False):
        '''Convenience function to add a child widget. Does the same
        as add widget'''
        if not widget:
            return
        my._add_widget(widget,name,wdgtype,index=index)



    def _add_widget(my,widget,name=None,wdgtype=None,index=None,use_state=False):
        '''actually adds the child widget.  This is a protected member
        and allows the adding of widgets internally.  Subclasses can
        override add_widget to add to an internal widget instead'''

        assert widget != None

        if type(widget) in types.StringTypes:
            widget = StringWdg(widget)
        elif type(widget)==types.IntType or type(widget)==types.FloatType:
            widget = StringWdg(str(widget))
        elif not isinstance(widget,Widget):
            widget = StringWdg(str(widget))


        if name:
            # find if the old widget is in the dictionary
            if my.named_widgets == None:
                my.named_widgets = {}


            if my.named_widgets.has_key(name):

                # replace the old widget with the new one
                my.__replace_widget(widget, name)
            else:
                # or just append a new on if it is not in the dictionary
                if index == None:
                    my.widgets.append(widget)
                else:
                    my.widgets.insert(index, widget)


            my.named_widgets[name] = widget
    

        # if there is no name, just append
        else:
            if index == None:
                my.widgets.append(widget)
            else:
                my.widgets.insert(index, widget)



        if wdgtype != None and wdgtype != "":

            if my.typed_widgets == None:
                my.typed_widgets = {}

            if not my.typed_widgets.has_key(wdgtype):
                my.typed_widgets[wdgtype] = []
            my.typed_widgets[wdgtype].append(widget)


        if use_state:
            my.state = WebState.get().get_current()


    def __replace_widget(my, widget, name):
        try:
            old_widget = my.named_widgets[name]
            index = my.widgets.index(old_widget)
        except ValueError:
            pass
        else:
            my.widgets[index] = widget

    def set_widget(my, widget, name):
        assert name != None and name.strip() != ''
        my.__replace_widget(widget, name) 
        my.named_widgets[name] = widget

    def get_widget(my, name):
        return my.named_widgets.get(name)


    def get_widgets_by_type(my,wdgtype):
        if my.typed_widgets.has_key(wdgtype):
            return my.typed_widgets[wdgtype]
        else:
            return []


    def get_widgets(my):
        return my.widgets


    def set_parent(my, parent):
        return parent.add(my)



    """
    def add_command(my, command):
        '''deprecated: use CommandDelegator'''
        my.commands.append(command)
    """

    def set_search(my, search):
        '''sets the search that will be performed in the search phase'''
        my.search = search

    def set_sobjects(my,sobjects,search=None):
        '''store the sobjects that this widget will act upon'''
        #print("set_sobjects")
        if search:
            my.search = search
        my.sobjects = sobjects
        my.current_index = 0

        # DEPRECATED: is this really necessary???
        # set all of the sobjects to all of the child widgets
        for widget in (my.widgets):
            widget.set_sobjects(sobjects,search)


    def set_sobject(my,sobject,search=None):
        '''convenience function to set only one sobject'''
        if sobject:
            my.set_sobjects([sobject],search)

    def is_sobjects_explicitly_set(my):
        return my.current_index != -1

    def get_sobjects(my):
        return my.sobjects


    def set_current_index(my, index):
        '''sets the index of the current sobject'''
        my.current_index = index

        for widget in (my.widgets):
            widget.set_current_index(index)
    
    def get_current_index(my):
        return my.current_index

    def get_current_sobject(my):
        if my.current_index == -1 or len(my.sobjects) == 0:
            return None
        else:
            return my.sobjects[my.current_index]



    def alter_search(my, search):
        '''Alter any search that comes through this widget'''
        for widget in my.widgets:
            widget.alter_search( search )

    def do_search(my):
        '''Perform any searches that were created in the init function.
        Returns a list of SObjects'''
        # if no search is defined in this class, then skip this
        if my.search != None:
            # give the opportunity for each of the lower widgets to alter the
            # search
            my.alter_search( my.search )

            # actually do the search and notify all of the children
            my.sobjects = my.search.get_sobjects()

        # go through each widget and perform their searches
        for widget in my.widgets:
            widget.do_search()


        # set the sobjects from this search
        # FIXME: this has the effect of overriding any lower searches
        # that may exist.  This is probably not desired behaviour
        # and should be fixed
        if my.search != None:
            my.set_sobjects( my.sobjects, my.search )



    def check_security(my):
        '''give the widget a callback that allows it to check security.
        This function will return if the widget is in a state that
        is acceptable to the security manager'''
        # execute all of the security checks of the lower widgets.  If
        # any fail with a security exception
        for widget in my.widgets:
            try:
                widget.check_security()
            except SecurityException as e:
                my.__cripple_widget(e)


    def explicit_display(my, cls=None):
        if not cls:
            child = my.get_display()
        else:
            child = cls.get_display(my)
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


    def get_display(my):
        '''Draw all of the contents'''
        for widget in my.widgets:
            #try:
            #    widget.explicit_display()
            #except SecurityException:
            #    # do nothing for now
            #    pass
            widget.explicit_display()

   


    def get_buffer(my, cls=None):
        '''create a new buffer and execute the get_display of this widget.
        This is useful for caching the display of a widget for multiple
        reuse'''
        # have to bake the widget in a new buffer
        WebContainer.push_buffer()
        try:
            my.explicit_display(cls)
        finally:
            buffer = WebContainer.pop_buffer()
        return buffer

    def get_buffer_display(my, cls=None):
        '''get a new buffer's value and execute the get_display of this widget.
        This is useful for caching the display of a widget for multiple
        reuse'''
        buffer = my.get_buffer(cls)
        value = buffer.getvalue()
        buffer.clear()

        return value

    def render(my, cls=None):
        '''get a new buffer's value and execute the get_display of this widget.
        This is useful for caching the display of a widget for multiple
        reuse'''
        return my.get_buffer(cls).getvalue()




    def get_class_display(cls, my):
        '''Explicitly use the get_display function of a provided class for a
        particular instance.  This is rarely used and should only be used
        carefully.  It is intended to break infinite loops when trying to
        build a composite widget while maintaining an internal widget's
        interface.  For example see: pyasm.wdget.FilterCheckboxWdg where
        a span is wrapped around a checkbox, but the widget needs to have the
        internal checkbox's interface.
        '''
        return my.get_buffer(cls).getvalue()
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

    def dump(my):
        print(my)
        for widget in my.widgets:
            print("child: \t", widget)

        for widget in my.widgets:
            widget.dump()


    def generate_unique_id(base='', wdg='HtmlWdg', is_random=False):
        ref_count = Container.get("%s:ref_count" %wdg)
        unique_code = Container.get("%s:unique_code" %wdg)
        if ref_count == None:
            ref_count = 0
            unique_code = ''.join([ random.choice('abcdefghijklmno') for i in xrange(0, 6)])
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

    def get_value_by_key(key, auto_create=True):
        if not DATABASE:
            return ""

        settings = WidgetSettings.get_by_key(key, auto_create=auto_create)
        if not settings:
            return ""
        value_str = settings.get_value("data")
        return value_str
    get_value_by_key = staticmethod(get_value_by_key)


    def set_value_by_key(key, value):
        '''set and commit the value'''
        if not DATABASE:
            return ""

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



    def get_by_key(key, auto_create=True):
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
    def execute(my):
        data = my.kwargs.get('data')
        key = my.kwargs.get('key')
        value = WidgetSettings.set_value_by_key(key, data)
        my.info['data'] = value

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


class StringWdg(Widget):
    def __init__(my,string=""):
        my.widgets = []
        my.string = string
        my.name = None

    def do_search(my):
        pass
    
    def check_security(my):
        pass
    
    def get_display(my):
        html = WebContainer.get_buffer()

        # write directly to the StringIO
        if type(my.string) == types.UnicodeType:
            my.string = Common.process_unicode_string(my.string)
        html.get_buffer().write(my.string)
    
class ClassWdg(Widget):
    def __init__(my, class_type=None):
        my.widgets = []
        assert type(class_type) == types.TypeType
        my.class_type = class_type
    
    def do_search(my):
        pass
    
    def check_security(my):
        pass
    
    def get_display(my):    
        return my.class_type()
        
    def get_class_name(my):
        return '%s.%s'%(my.class_type.__module__, my.class_type.__name__)
    
class MethodWdg(Widget):
    def __init__(my, method =''):
        my.widgets = []
        assert type(method) == types.MethodType
        my.method = method
    def do_search(my):
        pass
    
    def check_security(my):
        pass
    
    def get_display(my):    
        return my.method()
        
    def get_class_name(my):
        return '%s.%s'%(my.method.im_class.__module__, \
            my.method.im_class.__name__)

    def get_function_name(my):
        return my.method.im_func.func_name

class Html(Base):
    '''String buffer class for html code'''

    def __init__(my):
        my._buffer = cStringIO.StringIO()

    def __del__(my):
        my.clear()

    def write(my, html):
        if isinstance(html, basestring):
            my._buffer.write(html)
        elif type(html) == types.IntType:
            my._buffer.write( str(html) )
        elif isinstance(html,Html):
            my._buffer.write(html.getvalue())
        elif not html:
            pass
        else:
            raise WidgetException("Cannot handle [%s] type" % html)


    def writeln(my, html):
        my.write(html)
        my._buffer.write("\n")


    def getvalue(my):
        '''This exists to maintain backwards compatibility when this class
        used the StringIO class directly.'''
        return my._buffer.getvalue()

    def get_display(my):
        return my._buffer.getvalue()

    def to_string(my):
        return my._buffer.getvalue()

    def get_buffer(my):
        return my._buffer

    def clear(my):
        my._buffer.close()





class Url(Base):
    '''class which builds up a url'''

    def __init__(my, base=""):
        my.base = base
        my.options = {}

    def set_base(my, base):
        my.base = base

    def append_to_base(my, extra):
        if extra.startswith("/"):
            my.base += extra
        else:
            my.base += "/%s" % extra



    def set_option(my, name, value):
        my.options[name] = value


    def get_info(my):
        url = my.to_string()
        urlparts = urlparse.urlsplit(url)
        return urlparts

    def get_protocol(my):
        return my.get_info()[0]

    def get_host(my):
        return my.get_info()[1]


    def get_selector(my):
        return my.get_info()[2]



    def to_string(my):

        options_list = []
        for name,value in my.options.items():

            if type(value) == types.ListType:
                for item in value:
                    if not isinstance(value, basestring):
                        value = str(value)
                    encoded = urllib.quote_plus(value.encode('utf'))
                    options_list.append("%s=%s" % (name,encoded) )
            else:
                if not isinstance(value, basestring):
                    value = str(value)
                encoded = urllib.quote_plus(value.encode('utf'))
                options_list.append("%s=%s" % (name,encoded) )

        options_str = string.join( options_list, "&" )

        if options_str != "":
            url = "%s?%s" % (my.base, options_str)
        else:
            url = my.base

        return url


    def add_web_state(my):
        '''add web state paramenters to this url'''
        state = WebState.get()
        state.add_state_to_url(my)


    def get_protocol(my):
        parts = my.base.split("://")
        return parts[0]



    def get_url(my):
        return my.to_string()


    def get_base(my):
        return my.base




