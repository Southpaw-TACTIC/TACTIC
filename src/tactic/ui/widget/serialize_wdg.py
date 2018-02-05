###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['SObjectSerializer', 'SerializeWdg']

from pyasm.search import Search, SearchType

from pyasm.common import Xml, Common, jsonloads, jsondumps
from pyasm.command import Command
from pyasm.search import Search
from pyasm.web import DivWdg
from tactic.ui.common import BaseRefreshWdg



class SObjectSerializer(object):

    def dumps(self, sobjects):
        sobject_list = []

        for sobject in sobjects:
            data = sobject.get_data()
            sobject_list.append(data)

        sobjects_str = jsondumps(sobject_list)
        return sobjects_str


    def loads(self, search_type, sobjects_str):
        sobject_list = jsonloads(sobjects_str)

        sobjects = []
        for sobject_dict in sobject_list:
            sobject = SearchType.create(search_type)

            for name, value in sobject_dict.items():
                if value == None:
                    continue
                sobject.set_value(name, value)

            sobjects.append(sobject)

        return sobjects



    def create_config_xml(self, search_type, sobjects, element_names=[]):

        sobject_str = self.dumps(sobjects)

        serialized = []
        serialized.append('''<config><custom><element name='custom'>''')
        serialized.append('''<display class='tactic.ui.panel.TableLayoutWdg'>''')
        serialized.append('''  <search_type>%s</search_type>''' % search_type)
        if element_names:
            element_names_str = ",".join(element_names)
            serialized.append('''  <element_names>%s</element_names>''' % element_names_str)
        serialized.append('''  <view>summary</view>''')
        serialized.append('''  <sobjects><![CDATA[''')
        serialized.append(sobject_str)
        serialized.append('''  ]]></sobjects>''')
        serialized.append('''</display>''')
        serialized.append('''</element></custom></config>''')

        serialized = "\n".join(serialized)

        return serialized




class SerializeCmd(Command):

    def save_serialized(self, view, serialized):

        category = 'SerialzeWdg'
        search = Search("config/widget_config")
        search.add_filter("category", category)
        search.add_filter("view", view)
        config_sobj = search.get_sobject()
        if not config_sobj:
            config_sobj = SearchType.create("config/widget_config")
            config_sobj.set_value("category", category)
            config_sobj.set_value("view", view)

        config_sobj.set_value("config", serialized)

        config_sobj.commit()


    def execute(self):

        # FIXME: This is specific to TableLayoutWdg
        search_type = self.kwargs.get('search_type')
        view = self.kwargs.get('view')
        element_names = self.kwargs.get_element_names()
        if type(element_names) in types.StringTypes:
            element_names = element_names.split("|")




        serializer = SObjectSerializer()
        serialized = serializer.create_config_xml(search_type, sobjects, element_names)





class SerializeWdg(BaseRefreshWdg):
    def get_display(self):

        category = 'SerializeWdg'
        view = '123COW'

        sobjects = Search.eval("@SOBJECT(prod/asset)")
        element_names = ['preview', 'code', 'task_status']

        serializer = SObjectSerializer()
        serialized = serializer.create_config_xml("prod/asset", sobjects, element_names)



        search = Search("config/widget_config")
        search.add_filter("category", category)
        search.add_filter("view", view)
        config_sobj = search.get_sobject()

        serialized = config_sobj.get_xml_value("config")

        sobject_str = serialized.get_value("config/custom/element/display/sobjects")
        
        sobjects = serializer.loads("prod/asset", sobject_str)
        print sobjects

        top = DivWdg()
        self.set_as_panel(top)
        print top.attrs

        from pyasm.widget import WidgetConfig
        config = WidgetConfig.get(view='custom', xml=serialized)
        widget = config.get_display_widget("custom")
        widget.set_sobjects(sobjects[1:3])

        top.add(widget)
        return top


