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

__all__ = ['WebContainer']


from pyasm.common import *
from pyasm.security import *
from palette import Palette

from thread import get_ident
buffers = {}



class WebContainer(Base):
    """global container class for web related information"""

    def __init__(my):
        pass

    def set_web(web):
        """set the web object which give access to all request/response
        functionality"""

        # register the web contaienr
        Container.put("WebContainer::web", web )

        # also register this object as the environment info
        Environment.set_env_object( web )

    set_web = staticmethod(set_web)


    # main retrieval function
    def get_web():
        return Container.get("WebContainer::web")
    get_web = staticmethod(get_web)



    # html buffers.  Do this manually here for performance reasons
    def get_buffer():
        # return the last buffer
        try:
            buffer_list = buffers[get_ident()]
            return buffer_list[0]
        except KeyError:
            # create a new buffer list for this thread and add it
            buffer_list = []
            buffers[get_ident()] = buffer_list

            # push a new buffer
            buffer = WebContainer.push_buffer()
            return buffer
        except IndexError:
            # if for some reason there is no buffer, push a new one
            buffer = WebContainer.push_buffer()
            return buffer

    get_buffer = staticmethod(get_buffer)


    def push_buffer():
        # create a new buffer
        from widget import Html
        buffer = Html()
        buffer_list = buffers[get_ident()]
        buffer_list.insert(0, buffer)
        return buffer
    push_buffer = staticmethod(push_buffer)


    def pop_buffer():
        buffer_list = buffers[get_ident()]
        buffer = buffer_list[0]
        buffer_list.remove(buffer)
        return buffer
    pop_buffer = staticmethod(pop_buffer)

    def clear_buffer():
        # explicitly clear the buffers
        buffer_list = buffers.get(get_ident())
        if buffer_list:
            for buffer in buffer_list:
                buffer.clear()
        # create a new one
        buffer_list = []
        buffers[get_ident()] = buffer_list
        WebContainer.push_buffer()
    clear_buffer = staticmethod(clear_buffer)

    def get_num_buffers():
        return len(buffers[get_ident()])
    get_num_buffers = staticmethod(get_num_buffers)






    # security accessors
    def set_security(security):
        Environment.set_security(security)
    set_security = staticmethod(set_security)


    def get_security():
        security = Environment.get_security()
        return security
    get_security = staticmethod(get_security)


    # palette access
    def get_palette():
        return Palette.get()
    get_palette = staticmethod(get_palette)


    def get_login():
        return WebContainer.get_security().get_login()
    get_login = staticmethod(get_login)

    def get_user_name():
        return WebContainer.get_security().get_user_name()
    get_user_name = staticmethod(get_user_name)



    # cache for the various configuration files parsed
    def set_config(sobject_type, config):
        Container.put("WebContainer::"+sobject_type, config)
    set_config = staticmethod(set_config)


    def get_config(sobject_type):
        return Container.get("WebContainer::"+sobject_type )
    get_config = staticmethod(get_config)


    # storage of the command delegator
    def set_cmd_delegator(cmd_delegator):
        Container.put("WebContainer::delegator", cmd_delegator)
    set_cmd_delegator = staticmethod(set_cmd_delegator)


    def get_cmd_delegator():
        return Container.get("WebContainer::delegator" )
    get_cmd_delegator = staticmethod(get_cmd_delegator)


    def register_cmd(command_class_path):
        cmd_delegator = WebContainer.get_cmd_delegator()
        marshaller = Marshaller(command_class_path)
        cmd_delegator.register_cmd( marshaller )
        return marshaller
    register_cmd = staticmethod(register_cmd)



    def set_dragdrop(dragdrop):
        Container.put("WebContainer::dragdrop",dragdrop)
    set_dragdrop = staticmethod(set_dragdrop)

    def get_dragdrop():
        return Container.get("WebContainer::dragdrop")
    get_dragdrop = staticmethod(get_dragdrop)




    # storage of the event container
    def set_event_container(event_container):
        Container.put("WebContainer::event_container", event_container)
    set_event_container = staticmethod(set_event_container)


    def get_event_container():
        return Container.get("WebContainer::event_container" )
    get_event_container = staticmethod(get_event_container)

    def get_event(event_name):
        event_container = WebContainer.get_event_container()
        return event_container.get_event(event_name)
    get_event = staticmethod(get_event)



    def is_dev_mode(cls):
        import os
        mode = os.environ.get("TACTIC_MODE")
        if mode == "development":
            return True
        else:
            return False
    is_dev_mode = classmethod(is_dev_mode)


    # enviroment variables
    def get_env(env_var):
        web = WebContainer.get_web()
        return web.get_env(env_var)
    get_env = staticmethod(get_env)

    def get_menu(name):
        return Container.get(name)
    get_menu = staticmethod(get_menu)    

    def get_float_menu():
        return Container.get('float_menu')
    get_float_menu = staticmethod(get_float_menu)    

    def get_iframe(layout='default'):
        if layout == 'default':
            return Container.get('iframe')
        elif layout == 'plain':
            return Container.get('iframe_plain')
       
    get_iframe = staticmethod(get_iframe)  

    def get_body():
        return Container.get('body')
    get_body = staticmethod(get_body) 


    def get_warning():
        return Environment.get_warning()
    get_warning = staticmethod(get_warning)

    def add_warning(label, warning):
        return Environment.add_warning( label, warning)
    add_warning = staticmethod(add_warning)
    
    
    def add_js(js_file_name):
        ''' this has to be called on instantiation of tab or page widgets''' 
        web = WebContainer.get_web()
        context_url = web.get_context_url().to_string()
        js_url = "%s/javascript" % context_url
        Container.append_seq("Page:js", "%s/%s" % ( js_url, js_file_name))
    add_js = staticmethod(add_js)





