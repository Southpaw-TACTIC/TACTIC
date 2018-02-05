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

    def __init__(self, pipeline_xml):
        self.pipeline_xml = pipeline_xml

        self.env = AppEnvironment.get()
        self.app = self.env.get_app()
        self.handlers = []
        self.package = {}

    def set_server(self, server):
        self.server = server

    def set_package(self, package):
        self.package = package


    def execute2(self):
        from pipeline import Pipeline
        self.pipeline = Pipeline(self.pipeline_xml)

        try:
            process = self.pipeline.get_first_process_name()
            self.handle_process2(process)
        except Exception, e:
            if not self.handlers:
                raise
            print("Failed at handler: ", self.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = self.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception, e:
                print("Could not undo:", e.__str())
                raise

            raise


    def handle_process2(self, process):

        self.pipeline.get_process_info(process)

        # get the handler and instantiate it
        handler_class = self.pipeline.get_handler_class(process)
        if not handler_class:
            return

        try:
            handler = AppEnvironment.create_from_class_path(handler_class)
        except ImportError:
            raise ImportError("Could not import handler class [%s]" % handler_class)
        
        # pass relevant information to the handler
        handler.set_server(self.server)
        handler.set_package(self.package)

        # get input processes and hand over the delivery
        input_processes = self.pipeline.get_input_process_names(process)
        for input_process in input_processes:
            print "input: ", input_process
        #if self.handlers:
        #    handler.set_input( self.handlers[-1].get_output() )


        # store the handler and execute
        self.handlers.append(handler)
        handler.execute()

        # process all of the output handlers
        output_processes = self.pipeline.get_output_process_names(process)
        for output_process in output_processes:
            self.handle_process2(output_process)








   

    def execute(self):

        dom = parseString(self.pipeline_xml)
        root = dom.documentElement
        nodes = root.childNodes

        try:
            for node in nodes:
                node_name = node.nodeName

                if node_name == "process":
                    self.handle_process(node)
                elif node_name == "pipeline":
                    self.handle_process(node)
                elif node_name == "package":
                    self.handle_package(node)
        except Exception, e:
            if not self.handlers:
                raise
            print("Failed at handler: ", self.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = self.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception, e:
                print("Could not undo:", e.__str())
                raise

            raise




    def handle_process(self, process_node):

        # intantiate the package to be delivered to this handler
        package = self.package

        nodes = process_node.childNodes
        for node in nodes:
            node_name = node.nodeName
            if node_name == "action":
                self.handle_action(node, package)
            elif node_name == "#text":
                continue
            else:
                attrs = {}
                for attr, value in node.attributes.items():
                    attrs[attr] = value
                package[node_name] = attrs
                

    def handle_package(self, package_node):

        # intantiate the package to be delivered to this handler
        package = self.package

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
               


    def handle_action(self, action_node, package):
        handler_cls = action_node.getAttribute("class")
        try:
            handler = AppEnvironment.create_from_class_path(handler_cls)
        except ImportError:
            raise ImportError("Could not import handler class [%s]" % handler_cls)
            
        handler.set_server(self.server)
        handler.set_package(package)

        # hand over the delivery
        if self.handlers:
            handler.set_input( self.handlers[-1].get_output() )

        self.handlers.append(handler)
        handler.execute()



