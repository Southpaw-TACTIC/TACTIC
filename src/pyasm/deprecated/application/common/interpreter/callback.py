###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['callback']

from interpreter import PipelineInterpreter

import cgi

class ClientCallbackException(Exception):
    pass


class BaseClientCbk(object):
    def set_ticket(my, ticket):
        my.ticket = ticket

    def set_options(my, options):
        my.options = options

    def get_option(my, name):
        return my.options.get(name)


    def _execute(my):

        # get the server name
        server_name = my.get_option("server_name")
        if not server_name:
            raise ClientCallbackException("No [server_name] option delivered to callback")
        server_name = server_name[0]

        # get the project
        project_code = my.get_option("project_code")
        if not project_code:
            raise ClientCallbackException("No [project_code] option delivered to callback")
        project_code = project_code[0]

        # the entire pipeline is run in a TacticServer Transaction
        from tactic_client_lib import TacticServerStub
        my.server = TacticServerStub()
        my.server.set_server(server_name)
        my.server.set_ticket(my.ticket)
        my.server.set_project(project_code)


        my.server.start("Pipeline checkin")
        try:
            my.execute()

        except Exception, e:
            my.server.abort()
            raise
        else:
            my.server.finish()


    def execute_pipeline(my, pipeline_xml):
        # execute the pipeline
        interpreter = PipelineInterpreter(pipeline_xml)
        interpreter.set_server(my.server)
        interpreter.set_package(my.options)
        interpreter.execute()





class ClientCbk(BaseClientCbk):
    '''This callback executes a pipeline based on certain input parameters
    '''
    def execute(my):
        # get the snapshot type passed in
        snapshot_type_code = my.get_option("snapshot_type")
        if not snapshot_type_code:
            raise ClientCallbackException("No [snapshot_type] option delivered to callback")

        snapshot_type_code = snapshot_type[0]
        search_type = "sthpw/snapshot_type"
        search_key = my.server.build_search_type(search_type, snapshot_type_code)
        # get the pipeline
        pipeline_xml = my.server.get_pipeline_xml(search_key)

        my.execute_pipeline(pipeline_xml)





class ClientLoadCbk(BaseClientCbk):
    '''This callback executes a pipeline based on certain input parameters
    '''
    def execute(my):

        search_keys = my.get_option('search_key')
        for search_key in search_keys:
            print "search_key: ", search_key

            # get the snapshot
            snapshot = my.server.get_by_search_key(search_key)

            # get the snapshot type from the snapshot
            snapshot_type_code = snapshot.get('snapshot_type')
            search_type = "sthpw/snapshot_type"
            search_key = my.server.build_search_type(search_type, snapshot_type_code)
            pipeline_xml = my.server.get_pipeline_xml(search_key)

            # execute the pipeline
            my.execute_pipeline(pipeline_xml)





#
# entry point
#
def callback(ticket, callback_class, options):
    # NOTE: cgi.parse_qs creates arrays for *all* values
    options = cgi.parse_qs(options)
    print "options: ", options

    # get the callback, if there is one
    callback = eval("%s()" % callback_class)
    callback.set_ticket(ticket)
    callback.set_options(options)
    callback._execute()


