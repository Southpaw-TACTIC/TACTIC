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

    def init(self):
        web = WebContainer.get_web()
        widget_class = web.get_form_value("dynamic_widget")
        widget_args = web.get_form_values("args")

        if widget_class == "":
            raise DynamicLoaderException("Widget class [%s] is not defined" % widget_class)

        widget = Common.create_from_class_path( widget_class, widget_args )

        self.add_widget(widget)




class DynamicLoaderWdg(Widget):
    '''the widget used to send a dyanmic link'''

    def __init__(self, buffer_id=None, display_id=None):
        super(DynamicLoaderWdg,self).__init__()

        ref_count = Container.get("DyanmicLoaderWdg:ref_count")
        if ref_count is None:
            ref_count = 0

        if display_id is None:
            self.display_id = "dynamic_display_%s" % ref_count
        else:
            self.display_id = display_id

        if buffer_id is None:
            self.buffer_id = "dynamic_buffer_%s" % ref_count
        else:
            self.buffer_id = buffer_id

        self.loader_id = "dynamic_loader_%s" % ref_count


        Container.put("DyanmicLoaderWdg:ref_count", ref_count + 1 )


        self.load_class = None
        self.load_args = None

        web = WebContainer.get_web()
        self.loader_url = web.get_dynamic_loader_url()


    def get_loader_url(self):
        return self.loader_url



    def set_display_widget(self, widget):
        """set the widget to initially display"""
        self.display_widget = widget




    def set_load_class(self, load_class, load_args=None):
        self.load_class = load_class
        self.load_args = load_args


    def _get_display_html(self):

        standin_content = None
        if len(self.widgets) != 0:
            # take the first one
            standin_content = self.widgets[0]
        else:
            standin_content = StringWdg("")

        div = HtmlElement.div( standin_content )
        div.set_id(self.display_id)
        div.add_style("display", "block")
        return div


    def get_on_script(self):
        self.loader_url.set_option("dynamic_widget", self.load_class)
        if self.load_args != None:
            self.loader_url.set_option("args", self.load_args)

        self.loader_url.set_option("dynamic_loader_id", self.loader_id)

        url = self.loader_url.get_url()

        return "%s.load_content('%s');set_display_on('%s')" % (self.loader_id, url , self.display_id )



    def get_off_script(self):
        return "set_display_off(\'%s\')" % self.display_id




    def get_display(self):

        widget = Widget()
        widget.add('<script>%s = new DynamicLoader("%s","%s")</script>\n' \
            % (self.loader_id, self.display_id, self.buffer_id)
        )

        widget.add( self._get_display_html() )

        widget.add('''
        <iframe id="%s" name="%s" style="border: none; display: none">
        WARNING: iframes are not supported
        </iframe>
        ''' % (self.buffer_id, self.buffer_id) )

        return widget



