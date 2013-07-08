###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
# AUTHOR:
#     Remko Noteboom
#
#

__all__ = ['DynamicLoaderException', 'DynamicLoaderReceiverWdg', 'DynamicLoaderWdg']


from pyasm.common import Container, Common
from pyasm.web import *
from web_wdg import *
from layout_wdg import *


class DynamicLoaderException(Exception):
    pass


class DynamicLoaderReceiverWdg(Widget):
    '''the recieving widget that actually displays the content'''

    def init(my):
        web = WebContainer.get_web()
        widget_class = web.get_form_value("dynamic_widget")
        widget_args = web.get_form_values("args")

        if widget_class == "":
            raise DynamicLoaderException("Widget class [%s] is not defined" % widget_class)

        widget = Common.create_from_class_path( widget_class, widget_args )

        my.add_widget(widget)




class DynamicLoaderWdg(Widget):
    '''the widget used to send a dyanmic link'''

    def __init__(my, buffer_id=None, display_id=None):
        super(DynamicLoaderWdg,my).__init__()

        ref_count = Container.get("DyanmicLoaderWdg:ref_count")
        if ref_count is None:
            ref_count = 0

        if display_id is None:
            my.display_id = "dynamic_display_%s" % ref_count
        else:
            my.display_id = display_id

        if buffer_id is None:
            my.buffer_id = "dynamic_buffer_%s" % ref_count
        else:
            my.buffer_id = buffer_id

        my.loader_id = "dynamic_loader_%s" % ref_count


        Container.put("DyanmicLoaderWdg:ref_count", ref_count + 1 )


        my.load_class = None
        my.load_args = None

        web = WebContainer.get_web()
        my.loader_url = web.get_dynamic_loader_url()


    def get_loader_url(my):
        return my.loader_url



    def set_display_widget(my, widget):
        """set the widget to initially display"""
        my.display_widget = widget




    def set_load_class(my, load_class, load_args=None):
        my.load_class = load_class
        my.load_args = load_args


    def _get_display_html(my):

        standin_content = None
        if len(my.widgets) != 0:
            # take the first one
            standin_content = my.widgets[0]
        else:
            standin_content = StringWdg("")

        div = HtmlElement.div( standin_content )
        div.set_id(my.display_id)
        div.add_style("display", "block")
        return div


    def get_on_script(my):
        my.loader_url.set_option("dynamic_widget", my.load_class)
        if my.load_args != None:
            my.loader_url.set_option("args", my.load_args)

        my.loader_url.set_option("dynamic_loader_id", my.loader_id)

        url = my.loader_url.get_url()

        return "%s.load_content('%s');set_display_on('%s')" % (my.loader_id, url , my.display_id )



    def get_off_script(my):
        return "set_display_off(\'%s\')" % my.display_id




    def get_display(my):

        widget = Widget()
        widget.add('<script>%s = new DynamicLoader("%s","%s")</script>\n' \
            % (my.loader_id, my.display_id, my.buffer_id)
        )

        widget.add( my._get_display_html() )

        widget.add('''
        <iframe id="%s" name="%s" style="border: none; display: none">
        WARNING: iframes are not supported
        </iframe>
        ''' % (my.buffer_id, my.buffer_id) )

        return widget



