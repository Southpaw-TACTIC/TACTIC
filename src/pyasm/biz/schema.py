##########################################################
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

__all__ = ["Schema"]

from pyasm.common import Xml, Container, TacticException
from pyasm.search import Search, SObject, SearchType


SCHEMA_XML = {}

SCHEMA_XML['simple'] = '''<?xml version='1.0' encoding='UTF-8'?>
<schema parent="__NONE__">
</schema>
'''

SCHEMA_XML['admin'] = '''<?xml version='1.0' encoding='UTF-8'?>
<schema parent="__NONE__">
    <search_type name="sthpw/project"/>
    <search_type name="sthpw/project_type"/>
    <search_type name="sthpw/schema"/>
    <search_type name="sthpw/db_resource"/>

    <search_type name="sthpw/search_object"/>
    <search_type name="sthpw/snapshot"/>
    <search_type name="sthpw/file"/>


   
    <search_type name="sthpw/custom_script"/>
    <search_type name="sthpw/task"/>
    <search_type name="sthpw/milestone"/>
    <search_type name="sthpw/work_hour"/>
    <search_type name="sthpw/note" access="view"/>

    <search_type name="sthpw/login" display="@GET(sthpw/login.login)"/>
    <search_type name="sthpw/login_group" display="@GET(sthpw/login_group.login_group)"/>
    <search_type name="sthpw/login_in_group" display="@GET(sthpw/login_in_group.login)"/>
    <search_type name="sthpw/connection"/>
    <search_type name='sthpw/pref_list'/>

    <search_type name='sthpw/wdg_settings'/>
    <search_type name='sthpw/ticket'/>
    <search_type name="sthpw/doc"/>

    <search_type name="sthpw/pipeline"/>
    <search_type name="sthpw/trigger"/>
    <search_type name="sthpw/notification"/>
    <search_type name="sthpw/sobject_list"/>

    <search_type name="sthpw/transaction_log"/>
    <search_type name="sthpw/exception_log"/>
    <search_type name="sthpw/status_log"/>
    <search_type name="sthpw/sobject_log"/>
    <search_type name="sthpw/retire_log"/>
    <search_type name="sthpw/notification_log"/>
    <search_type name="sthpw/group_notification" display="@GET(sthpw/group_notification.login_group)"/>
    <search_type name="sthpw/cache"/>
    <search_type name="sthpw/queue"/>



<!--
    <search_type name='sthpw/template'/>
-->


    <connect to="sthpw/project_type" from="sthpw/project" type='hierarchy'/>


    <connect from="sthpw/file" to="sthpw/snapshot"
                relationship='code' type='hierarchy'/>

    <connect from="sthpw/file" to="*"
                relationship='search_type'/>




    <connect from="sthpw/snapshot" to="sthpw/login"
        relationship='code'
        from_col='login' to_col='login' path='login'/>
    

    <connect from="sthpw/snapshot" to="*"
                type='hierarchy' relationship='search_type'/>



    <connect from="sthpw/task" to="*"
                type='hierarchy' relationship='search_type'/>

    <connect from="sthpw/task" to="sthpw/project"
        relationship="code" from_col="project_code" to_col="code"
        path="project"/>
    <connect from="sthpw/task" to="sthpw/pipeline"
        relationship="code" from_col="pipeline_code" to_col="code"/>

    <connect from="sthpw/task" to="sthpw/milestone" relationship='code'/>

    <!-- <connect from="sthpw/task" to="config/process" relationship='code' from_col='process' to_col='process'/> -->


    <connect from="sthpw/note" to="*"
                type='hierarchy' relationship='search_type'/>
    <connect from="sthpw/work_hour" to="*"
                type='hierarchy' relationship='search_type'/>
    <connect from="sthpw/work_hour" to="sthpw/task"
                relationship='code' from_col='task_code' to_col='code'/>
    <connect from="sthpw/pipeline" to="*" from_col='code' to_col='pipeline_code' type='hierarchy' relationship='code'/>


    <connect from="sthpw/pipeline" to="sthpw/search_object"
        relationship='code' from_col='search_type' to_col='search_type'/>

    <connect from="sthpw/clipboard" to="*"
                type='hierarchy' relationship='search_type'/>

    <connect from="sthpw/sobject_list" to="*"
                type='hierarchy' relationship='search_type'/>


    <connect from="sthpw/sobject_log" to="*"
             type='hierarchy' relationship='search_type'/>
    <connect from="sthpw/sobject_log" to="sthpw/transaction_log"
             relationship='id' from_col='transaction_log_id'/>

    <connect from="sthpw/login_in_group" to="sthpw/login"
            relationship='code' from_col='login' to_col='login'/>
    <connect from="sthpw/login_in_group" to="sthpw/login_group"
            relationship='code' from_col='login_group' to_col='login_group'/>

    <connect from="sthpw/task" to="sthpw/login"
            relationship='code' from_col='assigned' to_col='login'/>
    <connect from="sthpw/task" to="sthpw/login" path='supervisor'
            relationship='code' from_col='supervisor' to_col='login'/>
    <connect from="sthpw/note" to="sthpw/login"
            relationship='code' from_col='login' to_col='login'/>
    <connect from="sthpw/work_hour" to="sthpw/login"
            relationship='code' from_col='login' to_col='login'/>


    <connect to='*' from ='sthpw/connection'
            relationship='search_type' type='hierarchy'
            prefix='src'
    />
    <connect to='*' from ='sthpw/connection'
            relationship='search_type' type='hierarchy'
            prefix='src' path='src'
    />

    <connect to='*' from ='sthpw/connection'
            relationship='search_type'
            prefix='dst' path='dst'
    />




    <connect from="sthpw/group_notification" to="sthpw/login_group" relationship='code' from_col='login_group' to_col='login_group'/>
    <connect from="sthpw/group_notification" to="sthpw/notification" relationship='id' from_col='notification_id'/>

    <connect from="sthpw/ticket" to="sthpw/login" relationship='code' from_col='login' to_col='login'/>
    <connect from="sthpw/status_log" to="sthpw/task" type='hierarchy' relationship='search_type'/>

 

    
    <!-- FIXME -->
    <!-- put in the config relationships here for now.  It does not yet
    read the config xml for dependencies
    -->
    <connect from="config/ingest_rule" to="config/ingest_session" relationship="code" from_col="spt_ingest_session_code" to_col="code"/>

    <connect from="config/plugin_content" to="config/plugin"
                from_col="plugin_code" to_col="code"
                relationship='code' type='hierarchy'/>

    <connect from="config/plugin_content" to="*"
                relationship='search_type'/>


   <search_type name="sthpw/sync_job"/>
   <search_type name="sthpw/sync_server"/>
   <connect from="sthpw/sync_job" to="sthpw/sync_server" relationship="code" from_col="server_code" to_col="code"/>


   <connect from="sthpw/message_log" to="sthpw/message" relationship="code" from_col="message_code" to_col="code"/>

   <connect from="sthpw/subscription" to="sthpw/message" relationship="code" from_col="message_code" to_col="code"/>

   <connect from="sthpw/subscription" to="sthpw/message" relationship="code" from_col="message_code" to_col="code"/>

   <connect from="sthpw/subscription" to="sthpw/login" relationship="code" from_col="login" to_col="login"/>



</schema>
'''


# DEPRECATED
SCHEMA_XML['prod'] = '''<?xml version='1.0' encoding='UTF-8'?>
 <schema parent="__NONE__">
   <search_type name='prod/art_reference'/>
   <search_type name='prod/script'/>
   <search_type name='prod/storyboard'/>
   <search_type name='prod/asset_library'/>
   <search_type name='prod/asset' display="@GET(prod/asset.code)"/>
   <search_type name='prod/texture'/>
   <search_type name='prod/episode'/>
   <search_type name='prod/sequence'/>
   <search_type name='prod/sequence_instance'/>
   <search_type name='prod/shot'/>
   <search_type name='prod/shot_instance' display="{@GET(prod/shot_instance.asset_code)} ({@GET(prod/shot_instance.name)})"/>
   <search_type name='prod/shot_texture'/>
   <search_type name='prod/layer'/>
   <search_type name='prod/composite'/>
   <search_type name='prod/plate'/>
   <search_type name='prod/bin'/>
   <search_type name='prod/submission_in_bin'/>
   <search_type name='prod/submission'/>
   <search_type name='prod/render'/>

   <connect to='*' type='connection' from='prod/art_reference' relationship='general'/>

   <connect from='prod/asset' relationship='code' to='prod/asset_library' from_col='asset_library' to_col='code' type='hierarchy'/>
   <connect from='prod/texture' to='prod/asset' relationship='code' type='hierarchy'/>

    <connect from='prod/shot' to='prod/sequence'
        relationship='code' type='hierarchy'/>
    <connect from='prod/sequence' to='prod/episode'
        relationship='code' type='hierarchy'/>
    <connect from='prod/sequence' to='prod/sequence_instance'
        relationship='code'/>

    <connect from='prod/shot_texture' to='prod/shot'
        relationship='search_type' type='hierarchy'/>

    <connect from='prod/layer' to='prod/shot'
        relationship='code' type='hierarchy'/>
    <connect from='prod/composite' to='prod/shot'
        relationship='code' type='hierarchy'/>
    <connect from='prod/plate' to='prod/shot'
        relationship='code' type='hierarchy'/>


    <connect from="prod/submission_in_bin" to="prod/submission" relationship='id' from_col='submission_id' to_col='id'/>
    <connect from="prod/submission_in_bin" to="prod/bin" relationship='id' from_col='bin_id' to_col='id'/>

    <connect to="prod/submission" from="sthpw/note" type='hierarchy' relationship='search_type'/>
    <connect to="*" from="prod/submission" type='hierarchy' relationship='search_type'/>
    <connect to="*" from="prod/render" type='hierarchy' relationship='search_type'/>

    <!-- TODO: short cuts for instances -->
    <!--
    <connect from="prod/asset" to="prod/shot" relationship='instance' path='prod/shot_instance'/>
    -->

    <connect from="prod/shot_instance" to="prod/shot" relationship='code' from_col='shot_code' to_col='code'/>
    <connect from="prod/shot_instance" to="prod/asset" relationship='code' from_col='asset_code' to_col='code'/>



 </schema>
'''

SCHEMA_XML['flash'] = '''<?xml version='1.0' encoding='UTF-8'?>
 <schema parent="__NONE__">
   <search_type name='prod/art_reference'/>
   <search_type name='prod/script'/>
   <search_type name='prod/storyboard'/>
   <search_type name='prod/asset_library'/>
   <search_type name='flash/asset'/>
   <search_type name='prod/episode'/>
   <search_type name='prod/episode_instance'/>
   <search_type name='flash/shot'/>
   <search_type name='prod/shot_instance'/>
   <search_type name='prod/layer'/>
   <search_type name='prod/composite'/>
   <search_type name='prod/bin'/>
   <search_type name='prod/submission_in_bin'/>
   <search_type name='prod/submission'/>
   <search_type name='prod/naming'/>
   <connect to='*' type='connection' from='prod/art_reference' relationship='general'/>

   <connect to='flash/asset' type='hierarchy' from='flash/asset_library'/>
   <connect to='flash/shot' type='hierarchy' from='prod/episode'/>
   <connect to='prod/episode_instance' type='hierarchy' from='prod/episode'/>
   <connect to='prod/shot_instance' type='hierarchy' from='flash/shot'/>
   <connect to='prod/layer' type='hierarchy' from='flash/shot'/>
   <connect to='prod/composite' type='hierarchy' from='flash/shot'/>

   <!-- TODO: need a special relationship here -->
   <connect to='prod/submission_in_bin' type='hierarchy' from='prod/bin'/>

   <connect to="*" from="prod/submission" type='hierarchy' relationship='search_type'/>
 </schema>
'''


SCHEMA_XML['unittest'] = '''<?xml version='1.0' encoding='UTF-8'?>
 <schema parent="__NONE__">
     <search_type name="unittest/country"/>
     <search_type name="unittest/city"/>
     <search_type name="unittest/person"/>
     <search_type name="unittest/car"/>

     <connect from="unittest/city" to="unittest/country"
            relationship="code" type="hierarchy" from_col='country_code' to_col='code'/>
     <connect from="unittest/person" to="unittest/city"
            relationship="code" type="hierarchy"/>

     <connect from="unittest/person_car_instance" to="unittest/person"
            relationship="code" type="hierarchy"/>
     <connect from="unittest/person_car_instance" to="unittest/car"
            relationship="code"/>



     <!-- COMMENTED OUT: Are instances even necessary any more
     <connect from="unittest/person" to="unittest/car" type="many_to_many" instance_type="unittest/person_car_instance"/>-->

 </schema>
'''


SCHEMA_XML['config'] = '''<?xml version='1.0' encoding='UTF-8'?>
<schema parent="__NONE__">
   <search_type name='config/plugin'/>
   <search_type name='config/naming'/>
   <search_type name='config/widget_config'/>
   <search_type name='config/custom_script'/>
   <search_type name='config/trigger'/>
   <search_type name='config/client_trigger'/>
   <search_type name='config/process'/>
   <search_type name='prod/custom_property'/>
   <search_type name='sthpw/pref_setting'/>
   <search_type name='config/url'/>
   <search_type name='config/ingest_session'/>
   <search_type name='config/ingest_rule'/>
   <search_type name='config/plugin'/>
   <search_type name='config/plugin_content'/>

   <connect from="config/ingest_rule" to="config/ingest_session" type="code" from_col="spt_ingest_session_code" to_col="code"/>

</schema>
'''


class Schema(SObject):
    SEARCH_TYPE = "sthpw/schema"

    def __init__(my, search_type, columns=None, result=None, dependencies=True, fast_data=None):
        super(Schema,my).__init__(search_type, columns, result, fast_data=fast_data)

        my.sthpw_schema = None
        my.parent_schema = None

        my.init()

        if dependencies:
            my.add_dependencies()


    def init(my):
        my.xml = my.get_xml_value("schema")



    def add_dependencies(my):
        # schemas without a code cannot have a dependency
        schema_code = my.get_value("code")
        if not schema_code:
            return


        # a schema has knowledge of it's parent
        my.parent_schema = my.get_parent_schema()

        # sthpw schema that everybody inherits from
        code = my.get_value("code")
        if code and code != "admin":
            my.sthpw_schema = Schema("sthpw/schema", dependencies=False)
            my.sthpw_schema.set_xml(SCHEMA_XML['admin'])


    def get_attrs_by_search_type(my, search_type):
        node = my.xml.get_node("schema/search_type[@name='%s']" % search_type)
        if node is not None:
            attrs = Xml.get_attributes(node)
        else:
            attrs = {}

        if not attrs and my.parent_schema:
            attrs = my.parent_schema.get_attrs_by_search_type(search_type)
        if not attrs and my.sthpw_schema:
            attrs = my.sthpw_schema.get_attrs_by_search_type(search_type)

        return attrs

    def get_attr_by_search_type(my, search_type, attr):
        node = my.xml.get_node("schema/search_type[@name='%s']" % search_type)
        if node is None:
            return {}
        return Xml.get_attributes(node).get(attr)





    def get_parent_schema(my):

        parent_schema_code = my.xml.get_value("schema/@parent")
        if parent_schema_code:
            if parent_schema_code == "__NONE__":
                return None

            parent_schema = Schema.get_by_code(parent_schema_code)
            return parent_schema
        else:

            # try the project type
            # FIXME: assume schema code == project_code
            schema_code = my.get_value("code")
            #assert schema_code and schema_code != "admin"

            from pyasm.biz import Project
            project = Project.get_by_code(schema_code)
            if not project:
                return None

            project_code = project.get_code()
            project_type = project.get_base_type()
            if not project_type:
                return None

            parent_schema = Schema.get_predefined_schema(project_type) 
            return parent_schema





    def get_xml(my):
        return my.xml

    def set_xml(my, xml):
        my.set_value("schema", xml)
        my.xml = my.get_xml_value("schema")



    def get_related_search_types(my, search_type, direction=None):
        related_types = []

        if not direction or direction == "parent":
            xpath = "schema/connect[@from='%s']" %(search_type)
            connects = my.xml.get_nodes(xpath)
            for connect in connects:
                related_type = Xml.get_attribute(connect,"to")
                related_types.append(related_type)

        if not direction or direction == "children":
            xpath = "schema/connect[@to='%s']" %(search_type)
            connects = my.xml.get_nodes(xpath)
            for connect in connects:
                related_type = Xml.get_attribute(connect,"from")
                related_types.append(related_type)


        if my.parent_schema:
            search_types = my.parent_schema.get_related_search_types(search_type, direction=direction)
            related_types.extend(search_types)

        if my.sthpw_schema:
            search_types = my.sthpw_schema.get_related_search_types(search_type, direction=direction)
            related_types.extend(search_types)

        return related_types 


    def get_relationship(my, search_type, search_type2):
        '''
        #FIXME, this should be updated to do what get_relationship_attrs behave
        @return

        general: connection through sthpw/connection search_type
        search_type: connection through search_type, search_id/code columns
        foreign_key: connection through foreign key constraint by foreign_key

        (deprecated)
        parent_code: connection through foreign key constraint by "parent_code
        project: connection through prod/connection search_type
        search_key: connection through search_key column (not used yet)


        # this one is explicit ... foreign key handles it. ... not sure
        # if this is needed
        code: connection through foreign key constraint by <table>_code
        id: connection through id <table>_id
        '''

        # use the same logic as get_relationship_attrs()
        attrs = my.get_relationship_attrs(search_type, search_type2, path=None, cache=True)
        relationship =  attrs.get('relationship')

        if relationship == 'search_type':
            relationship = my.resolve_search_type_relationship(attrs, search_type, search_type2)

        return relationship



    def resolve_search_type_relationship(my, attrs, search_type, search_type2):

        # determine the direction of the relationship
        my_is_from = attrs['from'] == search_type

        relationship = attrs.get('relationship')
        assert relationship == 'search_type'

        if my_is_from:

            has_code = SearchType.column_exists(search_type2, "code")
            if has_code:
                relationship = 'search_code'
            else:
                relationship = 'search_id'
        else:
            has_code = SearchType.column_exists(search_type, "code")
            if has_code:
                relationship = 'search_code'
            else:
                relationship = 'search_id'

        return relationship



    def resolve_relationship_attrs(my, attrs, search_type, search_type2):

        if attrs.get("relationship") != "search_type":
            return attrs


        search_type_obj = SearchType.get(search_type)
        search_type_obj2 = SearchType.get(search_type2)

        my_is_from = attrs['from'] == search_type_obj.get_base_key()

        db_resource = SearchType.get_db_resource_by_search_type(search_type)
        db_resource2 = SearchType.get_db_resource_by_search_type(search_type2)
        db_impl = db_resource.get_database_impl()
        db_impl2 = db_resource2.get_database_impl()

        # <connect from="sthpw/note" to="*"
        #    type='hierarchy' relationship='search_type'/>

        prefix = attrs.get("prefix")
        if prefix:
            prefix = "%s_" % prefix
        else:
            prefix = ""


        if my_is_from:

            if db_impl2.get_database_type() == "MongoDb":
                attrs['from_col'] = '%ssearch_code' % prefix
                attrs['to_col'] = db_impl2.get_id_col(db_resource2,search_type2)
                attrs['relationship'] = 'search_code'
            else:
                has_code = SearchType.column_exists(search_type2, "code")
                if has_code:
                    attrs['from_col'] = '%ssearch_code' % prefix
                    attrs['to_col'] = 'code'
                    attrs['relationship'] = 'search_code'
                else:
                    attrs['from_col'] = '%ssearch_id' % prefix
                    attrs['to_col'] = db_impl2.get_id_col(db_resource2,search_type2)
                    attrs['relationship'] = 'search_id'

        else:


            if db_impl.get_database_type() == "MongoDb":
                attrs['to_col'] = '%ssearch_code' % prefix
                attrs['from_col'] = db_impl.get_id_col(db_resource,search_type)
                attrs['relationship'] = 'search_code'
            else:
                has_code = SearchType.column_exists(search_type, "code")
                if has_code:
                    attrs['from_col'] = 'code'
                    attrs['to_col'] = '%ssearch_code' % prefix
                    attrs['relationship'] = 'search_code'
                else:
                    attrs['from_col'] = db_impl.get_id_col(db_resource,search_type)
                    attrs['to_col'] = '%ssearch_id' % prefix
                    attrs['relationship'] = 'search_id'

        return attrs




    def get_relationship_attrs(my, search_type, search_type2, path=None, cache=True, type=None):

        if cache:
            key = "Schema:%s|%s|%s|%s" % (search_type, search_type2, path, type)
            attrs_dict = Container.get("Schema:relationship")
            if attrs_dict == None:
                attrs_dict = {}
                Container.put("Schema:relationship", attrs_dict)

            attrs = attrs_dict.get(key)
            if attrs != None:
                return attrs

        # Need to remove ? and get the base
        if search_type.find("?") != -1:
            parts = search_type.split("?")
            search_type = parts[0]
        if search_type2.find("?") != -1:
            parts = search_type2.split("?")
            search_type2 = parts[0]


        """
        # TODO: fix this hard coding!!!!
        xx = ['sthpw/sobject_log', 'sthpw/queue']
        if search_type == 'sthpw/sobject_log' and search_type2 == 'sthpw/transaction_log':
            pass
        elif search_type2 == 'sthpw/sobject_log' and search_type == 'sthpw/transaction_log':
            pass
        elif search_type2 == 'sthpw/snapshot' and search_type == 'sthpw/file':
            pass

        elif search_type in xx:
            # these are defined backwards from the current definition
            attrs = {
                'from': search_type,
                'to': search_type2,
                'relationship': 'search_type',
                'from_col': '',
                'to_col': '',
            }
            return attrs
        elif search_type2 in xx:
            attrs = {
                'from': search_type2,
                'to': search_type,
                'relationship': 'search_type',
                'from_col': '',
                'to_col': '',
            }
            return attrs
        """



        direction = 'forward'


        # find all the connects with the first search_type
        connect = None

        # assemble all of the connects
        xpaths = []
        if type:
            xpath = "schema/connect[@from='%s' and @to='%s' and @type='%s']" %(search_type, search_type2, type)
            xpaths.append( xpath )
            xpath = "schema/connect[@from='%s' and @to='%s' and @type='%s']" %(search_type2, search_type, type)
            xpaths.append( xpath )
            xpath = "schema/connect[@from='%s' and @to='*' and @type='%s']" %(search_type, type)
            xpaths.append( xpath )
            xpath = "schema/connect[@from='%s' and @to='*' and @type='%s']" %(search_type2, type)
            xpaths.append( xpath )
        else:
            xpath = "schema/connect[@from='%s' and @to='%s']" %(search_type, search_type2)
            xpaths.append( xpath )
            xpath = "schema/connect[@from='%s' and @to='%s']" %(search_type2, search_type)
            xpaths.append( xpath )
        
            xpath = "schema/connect[@from='%s' and @to='*']" %(search_type)
            xpaths.append( xpath )
            xpath = "schema/connect[@from='%s' and @to='*']" %(search_type2)
            xpaths.append( xpath )

        try:
            if path:
                for xpath  in xpaths:
                    # if a path is specified then use that
                    connects = my.xml.get_nodes(xpath)
                    for conn in connects:
                        # at some odd times, the cached value is None
                        if conn is None:
                            continue
                        conn_path = my.xml.get_attribute(conn, "path")
                        if conn_path == path:
                            connect = conn
                            raise ExitLoop
            else:
                for xpath  in xpaths:
                    connects = my.xml.get_nodes(xpath)
                    for conn in connects:
                        # at some odd times, the cached value is None
                        if conn is None:
                            continue
                        conn_path = my.xml.get_attribute(conn, "path")
                        if conn_path:
                            continue
                        # this check is not really needed
                        #if conn is not None:
                        connect = conn
                        raise ExitLoop
        except ExitLoop:
            pass

        if connect is not None:
            if my.xml.get_attribute(connect, "from") == search_type:
                direction = 'forward'
            else:
                direction = 'backward'


        # since we are adding keys like 'disabled' below, processed is a boolean
        # to indicate if a found attrs dict has already been processed once
        # thru recursive running of the current method
        processed = False
       
        # if no explicit relationship is defined, find it in the parents
        if connect == None:
            if my.parent_schema:
                attrs = my.parent_schema.get_relationship_attrs(search_type, search_type2, path=path, cache=False, type=type)
                
                if not attrs:
                    attrs = my.sthpw_schema.get_relationship_attrs(search_type, search_type2, path=path, cache=False, type=type)
                processed = True
            else:
                if my.sthpw_schema:
                    attrs = my.sthpw_schema.get_relationship_attrs(search_type, search_type2, path=path, cache=False, type=type)
                    processed = True
                else:
                    attrs = {}

        else:
            attrs = my.xml.get_attributes(connect)
        
        if processed:
            return attrs

        relationship = attrs.get('relationship')
        # backwards compatibility mapping
        if not relationship:
            if attrs.get("type") == "hierarchy":
                attrs['relationship'] = 'code'
                relationship = 'code'


        if direction == 'forward':
            a_search_type = search_type
            b_search_type = search_type2
        else:
            a_search_type = search_type2
            b_search_type = search_type


        # fill in some defaults
        from_col = attrs.get('from_col')
        to_col = attrs.get('to_col')
        if relationship == 'id':
            a_search_type_obj = SearchType.get(a_search_type)
            b_search_type_obj = SearchType.get(b_search_type)
            
            if not from_col:
                table = b_search_type_obj.get_table()
                attrs['from_col'] = '%s_id' % table
            if not to_col:
                attrs['to_col'] = 'id'
                to_col = 'id'
            if not SearchType.column_exists(b_search_type, to_col):
                attrs['disabled'] = True
            if not SearchType.column_exists(a_search_type, from_col):
                attrs['disabled'] = True



        elif relationship == 'code':
            a_search_type_obj = SearchType.get(a_search_type)
            b_search_type_obj = SearchType.get(b_search_type)
            if not from_col:
                table = b_search_type_obj.get_table()
                from_col = '%s_code' % table
                attrs['from_col'] = from_col
            if not to_col:
                attrs['to_col'] = 'code'
                to_col = 'code'

            if not SearchType.column_exists(b_search_type, to_col):
                attrs['disabled'] = True
            if not SearchType.column_exists(a_search_type, from_col):
                attrs['disabled'] = True


        # store
        if cache:
            attrs_dict[key] = attrs


        return attrs

        
    def get_foreign_keys(my, search_type, search_type2, path=None):
        '''get the foreign keys relating these two search types'''
        attrs = my.get_relationship_attrs(search_type, search_type2, path)

        relationship = attrs.get('relationship')
        my_is_from = attrs['from'] == search_type

        from_col = attrs.get('from_col')
        to_col = attrs.get('to_col')

        if relationship in ['id', 'code']:
            if not from_col:
                from_col = 'whatever_id'
            if not to_col:
                to_col = 'id'

        elif relationship in ['search_type']:
            if not from_col:
                from_col = 'search_id'
            if not to_col:
                to_col = 'id'
                    

        else:
            raise Exception("Relationship [%s] is no supported" % relationship)
 

        if my_is_from:
            return (to_col, from_col)
        else:
            return (from_col, to_col)

    #
    # convenience functions to manipulate the schema
    #
    def add_search_type(my, search_type, parent_type=None, commit=True):
        '''adds a new search_type'''
        schema_node = my.xml.get_node("schema")

        xpath = "schema/search_type[@name='%s']" %search_type
        node = my.xml.get_node(xpath)
        if node is None:
            new_node = my.xml.create_element("search_type")
            my.xml.set_attribute(new_node, "name", search_type)
            #schema_node.appendChild(new_node)
            my.xml.append_child(schema_node, new_node)
            my.xml.set_attribute(new_node, "xpos", "0")
            my.xml.set_attribute(new_node, "ypos", "0")

        if parent_type:
            my.edit_connection(search_type, parent_type, mode='add')
    
        # clear the cache
        my.xml.clear_xpath_cache()
        if commit:
            my.set_value("schema", my.xml.to_string() )

    def edit_connection(my, from_search_type, to_search_type, mode='remove', commit=True):
        '''edit the connection im a schema'''
        xpath = "schema/connect[@from='%s' and @to='%s']" %(from_search_type, to_search_type)

        node = my.xml.get_node(xpath)
        schema_node = my.xml.get_node("schema")
        if node is not None:
            if mode == 'remove':
                #schema_node.removeChild(node)
                my.xml.remove_child(schema_node, node)
        else:
            # add only if it does not exist
            if mode == 'add':
                connect_node = my.xml.create_element("connect")
                my.xml.set_attribute(connect_node, "from", from_search_type)
                my.xml.set_attribute(connect_node, "to", to_search_type)
                my.xml.set_attribute(connect_node, "relationship", 'code')
                my.xml.set_attribute(connect_node, "type", 'hierarchy')
                #schema_node.appendChild(connect_node)
                my.xml.append_child(schema_node, connect_node)

               
        if commit:
            my.set_value("schema", my.xml.to_string() )


    #
    # information retrieval functions
    #


    def get_search_types(my, hierarchy=True):
        search_types = []
        if hierarchy:
            if my.sthpw_schema:
                sthpw_search_types = my.sthpw_schema.get_search_types()
                search_types.extend(sthpw_search_types)
            
            if my.parent_schema:
                parent_search_types = my.parent_schema.get_search_types()
                search_types.extend(parent_search_types)

        search_types.extend( my.xml.get_values("schema/search_type/@name") )

        return search_types


    def get_instance_type(my, search_type, related_search_type):
        connect = my.xml.get_node("schema/connect[@to='%s' and @from='%s']" % \
            (search_type, related_search_type) ) 
        if connect == None:
            return ""

        # ensure that the connection is "many_to_many"
        type = Xml.get_attribute(connect, "type")
        if type != "many_to_many":
            return ""

        instance_type = Xml.get_attribute(connect, "instance_type")
        if not instance_type:
            raise Exception("No instance_type defined for [%s] to [%s]" % \
                (search_type, related_search_type) )

        return instance_type


    def get_parent_type(my, search_type, relationship=None):
        # NOTE: relationship arg is deprecated!!

        if search_type.find("?") != -1:
            search_type, tmp = search_type.split("?", 1)

        # make a provision for admin search_types passed in
        if my.get_code() != "admin" and search_type.startswith("sthpw/"):
            
            parent_type = Schema.get_admin_schema().get_parent_type(search_type, relationship)
            if parent_type:
                return parent_type

        parent_type = ""
        # look at new style connections first
        connects = my.xml.get_nodes("schema/connect[@from='%s']" % search_type ) 
        for connect in connects:
            relationship_new = Xml.get_attribute(connect, "relationship")
            if relationship_new:
                type = Xml.get_attribute(connect, "type")
                if type == 'hierarchy':
                    parent_type = Xml.get_attribute(connect, "to")
                    break

        # NOTE: there could be multiple parents here.  Hierarchy type
        # should be the one to resolve this.
        # if there is no "hierarchy" type, use the first one
        if not parent_type:
            for connect in connects:
                from_type = Xml.get_attribute(connect, "from")
                if from_type == search_type:
                    parent_type = Xml.get_attribute(connect, "to")
                    break



        """
        # DEPRECATED: resort to old style
        if not parent_type:
            connects = my.xml.get_nodes("schema/connect[@to='%s']" % search_type ) 
            # FIXME: you need to assign parent_type here
            for connect in connects:
                type = Xml.get_attribute(connect, "type")
                if type != relationship:
                    continue
                parent_type = Xml.get_attribute(connect, "from") 
                # FIXME: should we call break?
        """


        if not parent_type and my.parent_schema:
            parent_type = my.parent_schema.get_parent_type(search_type, relationship)


        return parent_type



    def get_child_types(my, search_type, relationship="hierarchy", hierarchy=True):
        if search_type.find("?") != -1:
            search_type, tmp = search_type.split("?", 1)

        child_types = []
        # first get the child types defined in the admin schema
        if hierarchy and my.sthpw_schema:
            sthpw_child_types = my.sthpw_schema.get_child_types(search_type, relationship)
            child_types.extend(sthpw_child_types)


        # get the child types in the project type schema
        if hierarchy and my.parent_schema:
            parent_child_types = my.parent_schema.get_child_types(search_type, relationship)
            child_types.extend(parent_child_types)


        # add new style
        connects = my.xml.get_nodes("schema/connect[@to='%s'] | schema/connect[@to='*']" % search_type) 
        for connect in connects:
            relationship = Xml.get_attribute(connect, "relationship")
            # skip old style
            if not relationship:
                continue

            child_type = Xml.get_attribute(connect, "from")
            # skip identical type
            if child_type == search_type:
                continue
            child_types.append(child_type)

        return child_types




    def get_types_from_instance(my, search_type):
        from_type = my.xml.get_value("schema/connect[@instance_type='%s']/@from" % search_type)
        to_type = my.xml.get_value("schema/connect[@instance_type='%s']/@to" % search_type)
        return from_type, to_type


    #
    # triggers
    #

    def insert_trigger(my, sobject):

        # on creation of an instance, create a child one
        search_type = sobject.get_base_search_type()

        #
        # update based on short code
        #
        short_code = sobject.get_value("short_code", no_exception=True)
        if short_code:
            delimiter = "_"

            parent_type = my.get_parent_type(search_type)
            if parent_type:
                parent = sobject.get_parent(parent_type)
                if parent:
                    parent_code = parent.get_code()
                    short_code = sobject.get_value("short_code")

                    code = "%s%s%s" % (parent_code, delimiter, short_code)

                    sobject.set_value("code", code)
                    # this is put here to prevent and infinite loop
                    sobject.set_value("short_code", short_code)
                    sobject.commit(triggers=False)


        #
        # update code based on whether this is an instance
        #
        from_type, to_type = my.get_types_from_instance(search_type)
        if from_type and to_type:

            # update the code of the instance
            parent = sobject.get_parent(to_type)

            short_code = sobject.get_value("short_code", no_exception=True)
            if short_code:
                code = "%s_%s" % ( parent.get_code(), short_code)
            else:
                sibling = sobject.get_parent(from_type)
                code = "%s_%s" % ( parent.get_code(), sibling.get_code())

            sobject.set_value("code", code)
            sobject.commit()




    def edit_trigger(my, sobject):
        '''This gets called on every update of an sobject.  When any update is
        made, a checked through schema determines if any cascading effects
        are required'''

        search_type = sobject.get_base_search_type()
        code = sobject.get_code()

        # update based on short code
        prev_short_code = sobject.get_prev_value("short_code")
        if sobject.has_value("short_code"):
            short_code = sobject.get_value("short_code")
            if short_code and short_code != prev_short_code:
                delimiter = "_"

                parent_type = my.get_parent_type(search_type)
                if parent_type:
                    parent = sobject.get_parent(parent_type)
                    if parent:
                        parent_code = parent.get_code()
                        short_code = sobject.get_value("short_code")

                        code = "%s%s%s" % (parent_code, delimiter, short_code)

                        sobject.set_value("code", code)
                        # this is put here to prevent and infinite loop
                        sobject.set_value("short_code", short_code)
                        sobject.commit(triggers=False)

                

        # update the children
        my.update_children_code(sobject)
        

    def update_children_code(my, sobject):

        # DEPRECATED: this has only be used once and has some very specific
        # logic that is probably much better implemented as some kind of
        # external trigger
        return

        search_type = sobject.get_base_search_type()
        code = sobject.get_code()
        delimiter = "_"

        schema = Schema.get()
        # handle children's code if db foreign constraint key has not been applied
        child_search_types = my.get_child_types(search_type)
        for child_search_type in child_search_types:
            prev_code = sobject.get_prev_value("code")
            if prev_code and code != prev_code:
                # get all of the former children (little bit of a HACK here)
                sobject.set_value("code", prev_code)
                children = sobject.get_all_children( child_search_type )
                sobject.set_value("code", code)
               
                foreign_key = ''
                # determine the from_col
                attrs = schema.get_relationship_attrs(search_type, child_search_type)
                # all new schema connection should have attrs
                if attrs:
                    relationship = attrs.get('relationship')
                    if relationship in ['id', 'code']:
                        foreign_key = attrs.get('from_col')
                    elif relationship in ['search_type']:
                        continue

                        
                if not foreign_key:    
                    # backward compatible with code relationship that doesn't define from_col
                    foreign_key = sobject.get_foreign_key()

                for child in children:
                    # skip if this child does not have the foreign key
                    if not child.has_value(foreign_key):
                        continue

                    # switch the child's parent code to reflect the new code
                    child.set_value(foreign_key, code)

                    short_code = child.get_value("short_code",no_exception=True)
                    if not short_code:
                        child.commit()
                        continue

                    new_child_code = "%s%s%s" % ( code, delimiter, short_code )
                    child.set_value("code", new_child_code)
                    child.commit()



    #
    # static methods
    #
    def create(code, description, schema="<schema/>"):
        sobject = Schema("sthpw/schema", dependencies=False)
        sobject.set_value("code", code)
        sobject.set_value("description", description)
        sobject.set_value("schema", schema)
        sobject.set_user()
        sobject.commit()
        sobject.init()
        return sobject
    create = staticmethod(create)


    def get_predefined_schema(cls, code):
        assert(code)
        schema = Container.get("Schema:%s" % code)
        if not schema:
            schema = Schema("sthpw/schema", dependencies=False)
            schema.set_value("schema", SCHEMA_XML[code])
            schema.set_value("code", code)
            schema.init()
            Container.put("Schema:%s" % code, schema)

        return schema
    get_predefined_schema = classmethod(get_predefined_schema)




    def get_admin_schema(cls):
        return cls.get_predefined_schema("admin")
    get_admin_schema = classmethod(get_admin_schema)


    def get_prod_schema(cls):
        return cls.get_predefined_schema("prod")
    get_prod_schema = classmethod(get_prod_schema)


    def get_unittest_schema(cls):
        return cls.get_predefined_schema("unittest")
    get_unittest_schema = classmethod(get_unittest_schema)




    def get_by_project_code(cls, project_code):

        schema = Schema.get_by_code(project_code)

        # if the project schema does not exist, then create an empty one
        if not schema:
            if project_code=='unittest':
                return Schema.get(project_code)
            schema = Schema("sthpw/schema", dependencies=False)
            schema.set_value("schema", "<schema/>")
            schema.set_value("code", project_code)
            schema.init()
            schema.add_dependencies()

        return schema
        
    get_by_project_code = classmethod(get_by_project_code)

 

    def get_by_sobject(cls, sobject):
        # by default the code of the schema is the project code
        search_type = sobject.get_search_type()
        if search_type.startswith("sthpw/"):

            schema = Container.get("Schema:admin")
            if not schema:
                schema = Schema("sthpw/schema", dependencies=False)
                schema.set_value("code", "admin")
                schema.set_xml(SCHEMA_XML['admin'])

                Container.put("Schema:admin", schema)

            return schema


        project_code = sobject.get_project_code()
        schema = Schema.get_by_project_code(project_code)
        return schema
    get_by_sobject = classmethod(get_by_sobject)


 
    def get(cls, reset_cache=False):

        if not reset_cache:
            schema = Container.get("Schema")
            if schema:
                return schema

        from project import Project
        project_code = Project.get_project_code()

        # the predefined ones cannot be overriden
        #if project_code in ['prod', 'unittest', 'flash', 'admin']:
        if project_code in ['unittest']:
            schema = cls.get_predefined_schema(project_code)
            schema.init()
            sthpw_schema = cls.get_predefined_schema("admin")
            sthpw_schema.init()
            schema.sthpw_schema = sthpw_schema
            return schema
        elif project_code in ['sthpw','admin']:
            sthpw_schema = cls.get_predefined_schema("admin")
            sthpw_schema.init()
            return sthpw_schema



        # by default the code of the schema is the project code
        #schema = cls.get_by_project_code(project_code)
        # find using explicit search ... too much nested caching going
        # on here.  It is confusing when changing schema
        search = Search("sthpw/schema")
        #search.add_op("begin")
        search.add_filter("code", project_code)
        #search.add_filter("project_code", project_code)
        #search.add_op("or")
        schemas = search.get_sobjects()

        #if len(schemas) > 1:
        if False:
            schema = SearchType.create("sthpw/schema")
            schema.set_value("code", project_code)
            schema.set_value("project_code", project_code)

            new_xml = []
            new_xml.append("<schema>\n")

            for schema in schemas:
                xml = schema.get_xml_value("schema")
                nodes = xml.get_nodes("schema/*")
                for node in nodes:
                    new_xml.append(xml.to_string(node))

            new_xml.append("</schema>\n")

            new_xml = "".join(new_xml)
            print new_xml
            schema.set_value("schema", new_xml)

        elif schemas:
            schema = schemas[0]


        # if the project schema does not exist, then create an empty one
        if not schema:
            schema = Schema("sthpw/schema", dependencies=False)
            schema.set_value("schema", "<schema/>")
            schema.set_value("code", project_code)
            schema.init()
            schema.add_dependencies()




        # if the project schema does not exist, then create an empty one
        if not schema:
            schema = Schema("sthpw/schema", dependencies=False)
            schema.set_value("schema", "<schema/>")
            schema.set_value("code", project_code)
            schema.init()
            schema.add_dependencies()

        Container.put("Schema", schema)
        return schema
    get = classmethod(get)

class ExitLoop(Exception):
    """Just a way to exit a nested for loop"""
    pass

