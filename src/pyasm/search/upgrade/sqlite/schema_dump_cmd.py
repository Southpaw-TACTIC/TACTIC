###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['SchemaDumpCmd']

import tacticenv

from pyasm.common import Xml, Environment, TacticException
from pyasm.search import Search, SearchType
from pyasm.biz import Project
from tactic.command import PluginCreator, PluginInstaller

import os, shutil



class SchemaDumpCmd(object):
    '''This will dump a plugin that will contain structure of the sthpw
    and config schema. It can be used to import these using the plugin
    architecture (ie: database independent).  Only the bootstrap tables
    are needed for these to import properly (bootstrap_schema.sql).

    However, these may not be necessary as string replacement seems to work
    fine for database independence for the base schema.
    '''

    def execute(my):
        plugin_code = "sthpw_schema"
        project_code = 'sthpw'

        search_types = [
            # these are handled in bootstrap loader so do not need to be dumpted
            #"sthpw/search_object",
            #"sthpw/project",
            #"sthpw/login",
            #"sthpw/trigger",            # DEPRECATED
            #"sthpw/schema",
            #"sthpw/notification",

            "sthpw/project_type",
            "sthpw/login_in_group",
            "sthpw/login_group",
            "sthpw/ticket",
            "sthpw/pipeline",
            "sthpw/group_notification", # DEPRECATED
            "sthpw/snapshot",
            "sthpw/file",
            "sthpw/remote_repo",        # DEPRECATED
            "sthpw/milestone",
            "sthpw/task",
            "sthpw/note",
            "sthpw/pref_setting",
            "sthpw/wdg_settings",
            "sthpw/clipboard",
            "sthpw/exception_log",
            "sthpw/transaction_log",
            "sthpw/transaction_state",  # CLEANUP
            "sthpw/sobject_log",
            "sthpw/status_log",
            "sthpw/cache",
            "sthpw/sobject_list",
            "sthpw/doc"
        ]


        my.dump(plugin_code, project_code, search_types)


        plugin_code = "config_schema"
        project_code = 'project'

        search_types = [
            "config/custom_script",
            "config/widget_config",
            "config/naming",
            "config/client_trigger",
            "config/process",
            "config/trigger",
            "config/url",
            "config/prod_setting",
        ]

        my.dump(plugin_code, project_code, search_types)


        #project_code = 'project'
        #search_type_objs = Project.get_by_code(project_code).get_search_types()
        #search_types = [x.get_value("search_type") for x in search_type_objs]
        #plugin_code = "%s_schema" % project_code
        #my.dump(plugin_code, project_code, search_types)
 



    def dump(my, plugin_code, project_code, search_types):

        xml = Xml()
        my.xml = xml

        xml.create_doc("manifest")
        manifest_node = xml.get_root_node()
        xml.set_attribute(manifest_node, "code", plugin_code)

        # DUMP the data
        for search_type in search_types:

            data_node = xml.create_element("search_type")
            xml.append_child(manifest_node, data_node)
            xml.set_attribute(data_node, "code", search_type)

            # This exports the data
            """
            data_node = xml.create_element("sobject")
            xml.append_child(manifest_node, data_node)
            xml.set_attribute(data_node, "search_type", search_type)

            # find the currval 
            st_obj = SearchType.get(search_type)
            # have to call nextval() to initiate this sequence in the session in psql since Postgres 8.1
            seq_id = st_obj.sequence_nextval()
            
            seq_id = st_obj.sequence_currval()

            seq_id -= 1
            if seq_id > 0:
                st_obj.sequence_setval(seq_id)
            xml.set_attribute(data_node, "seq_max", seq_id)
            """
            


        print xml.to_string()

        # create a virtual plugin
        plugin = SearchType.create("sthpw/plugin")
        plugin.set_value("version", "1.0.0")
        plugin.set_value("code", "%s_project" % project_code)

        base_dir = "./templates"
        creator = PluginCreator( base_dir=base_dir, plugin=plugin, manifest=xml.to_string() )
        creator.execute()


if __name__ == '__main__':

    from pyasm.security import Batch
    Batch()
    cmd = SchemaDumpCmd()
    cmd.execute()


