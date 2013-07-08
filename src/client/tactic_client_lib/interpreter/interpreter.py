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


__all__ = ['PipelineInterpreter']

from xml.dom.minidom import parseString

from tactic_client_lib.common import Common

from handler import Handler


class PipelineInterpreter(object):

    def __init__(my, pipeline_xml, first_process=None):
        my.pipeline_xml = pipeline_xml

        my.first_process = first_process

        my.handlers = []
        my.handlers_dict = {}

        my.package = {}

    def set_server(my, server):
        my.server = server

    def set_package(my, package):
        my.package = package


    def get_handler(my, process_name):
        return my.handlers_dict.get(process_name)

    def get_handlers(my):
        return my.handlers


    def execute(my):
        from pipeline import Pipeline
        my.pipeline = Pipeline(my.pipeline_xml)

        try:
            # if an initial process is not specified, use an implicit one
            if not my.first_process:
                my.first_process = my.pipeline.get_first_process_name()
            my.handle_process(my.first_process)
        except Exception, e:
            if not my.handlers:
                raise
            print("Failed at handler: ", my.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = my.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception, e:
                print("Could not undo:", str(e) )
                raise

            raise


    def handle_process(my, process, input_process=None):
        '''handle the individual process

        @params
        process - the name of the process to be handled
        input_process - the name of the input process that called
            this process
        '''

        # get the handler and instantiate it
        handler_class = my.pipeline.get_handler_class(process)
        if handler_class:
            try:
                handler = Common.create_from_class_path(handler_class)
            except ImportError:
                raise ImportError("Could not import handler class [%s]" % handler_class)

        else:
            handler = Handler()

        # pass the options to the handler
        options = my.pipeline.get_action_options(process)
        handler.set_options(options)
        
        # pass relevant information to the handler
        handler.set_process_name(process)
        handler.set_server(my.server)
        handler.set_pipeline(my.pipeline)
        handler.set_package(my.package)

        # if this is the first process (no input process, then the package
        # is the input 
        if not input_process:
            output = my.package.copy()
        else:
            # get input processes and hand over the delivery
            input_handler = my.handlers_dict.get(input_process)
            if input_handler:
                output = input_handler.get_output()
            else:
                output = {}

        # By default, inputs travel through
        handler.set_input( output )
        handler.set_output( output )


        # store the handler and execute
        my.handlers.append(handler)
        my.handlers_dict[process] = handler
        handler.execute()

        # process all of the output handlers.  First ask the current handler
        # for the next process
        output_processes = handler.get_next_processes()

        # if output processes is None, then stop this branch completely
        if output_processes == None:
            return

        # otherwise, use the pipeline
        if not output_processes:
            output_processes = my.pipeline.get_output_process_names(process)

        for output_process in output_processes:
            my.handle_process(output_process, process)








    """ 
    def execute(my):

        dom = parseString(my.pipeline_xml)
        root = dom.documentElement
        nodes = root.childNodes

        try:
            for node in nodes:
                node_name = node.nodeName

                if node_name == "process":
                    my.handle_process(node)
                elif node_name == "pipeline":
                    my.handle_process(node)
                elif node_name == "package":
                    my.handle_package(node)
        except Exception, e:
            if not my.handlers:
                raise
            print("Failed at handler: ", my.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = my.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception, e:
                print("Could not undo:", e.__str())
                raise

            raise




    def handle_process(my, process_node):

        # intantiate the package to be delivered to this handler
        package = my.package

        nodes = process_node.childNodes
        for node in nodes:
            node_name = node.nodeName
            if node_name == "action":
                my.handle_action(node, package)
            elif node_name == "#text":
                continue
            else:
                attrs = {}
                for attr, value in node.attributes.items():
                    attrs[attr] = value
                package[node_name] = attrs
                

    def handle_package(my, package_node):

        # intantiate the package to be delivered to this handler
        package = my.package

        nodes = package_node.childNodes
        for node in nodes:
            node_name = node.nodeName
            if node_name == "#text":
                continue
            else:
                # handle the attributes
                attrs = {}
                for attr, value in node.attributes.items():
                    attrs[attr] = value

                # handle the vale
                if node.firstChild:
                    value = node.firstChild.nodeValue
                    attrs["__VALUE__"] = value

                package[node_name] = attrs
               


    def handle_action(my, action_node, package):
        handler_cls = action_node.getAttribute("class")
        try:
            handler = Common.create_from_class_path(handler_cls)
        except ImportError:
            raise ImportError("Could not import handler class [%s]" % handler_cls)
            
        handler.set_server(my.server)
        handler.set_package(package)

        # hand over the delivery
        if my.handlers:
            handler.set_input( my.handlers[-1].get_output() )

        my.handlers.append(handler)
        handler.execute()
    """



