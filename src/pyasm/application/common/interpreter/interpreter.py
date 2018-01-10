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

from pyasm.application.common import AppEnvironment


class PipelineInterpreter(object):

    def __init__(my, pipeline_xml):
        my.pipeline_xml = pipeline_xml

        my.env = AppEnvironment.get()
        my.app = my.env.get_app()
        my.handlers = []
        my.package = {}

    def set_server(my, server):
        my.server = server

    def set_package(my, package):
        my.package = package


    def execute2(my):
        from pipeline import Pipeline
        my.pipeline = Pipeline(my.pipeline_xml)

        try:
            process = my.pipeline.get_first_process_name()
            my.handle_process2(process)
        except Exception as e:
            if not my.handlers:
                raise
            print("Failed at handler: ", my.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = my.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception as e:
                print("Could not undo:", e.__str())
                raise

            raise


    def handle_process2(my, process):

        my.pipeline.get_process_info(process)

        # get the handler and instantiate it
        handler_class = my.pipeline.get_handler_class(process)
        if not handler_class:
            return

        try:
            handler = AppEnvironment.create_from_class_path(handler_class)
        except ImportError:
            raise ImportError("Could not import handler class [%s]" % handler_class)
        
        # pass relevant information to the handler
        handler.set_server(my.server)
        handler.set_package(my.package)

        # get input processes and hand over the delivery
        input_processes = my.pipeline.get_input_process_names(process)
        for input_process in input_processes:
            print "input: ", input_process
        #if my.handlers:
        #    handler.set_input( my.handlers[-1].get_output() )


        # store the handler and execute
        my.handlers.append(handler)
        handler.execute()

        # process all of the output handlers
        output_processes = my.pipeline.get_output_process_names(process)
        for output_process in output_processes:
            my.handle_process2(output_process)








   

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
        except Exception as e:
            if not my.handlers:
                raise
            print("Failed at handler: ", my.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = my.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception as e:
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
            handler = AppEnvironment.create_from_class_path(handler_cls)
        except ImportError:
            raise ImportError("Could not import handler class [%s]" % handler_cls)
            
        handler.set_server(my.server)
        handler.set_package(package)

        # hand over the delivery
        if my.handlers:
            handler.set_input( my.handlers[-1].get_output() )

        my.handlers.append(handler)
        handler.execute()



