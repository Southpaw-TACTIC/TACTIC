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

from .handler import Handler


class PipelineInterpreter(object):

    def __init__(self, pipeline_xml, first_process=None):
        self.pipeline_xml = pipeline_xml

        self.first_process = first_process

        self.handlers = []
        self.handlers_dict = {}

        self.package = {}

    def set_server(self, server):
        self.server = server

    def set_package(self, package):
        self.package = package


    def get_handler(self, process_name):
        return self.handlers_dict.get(process_name)

    def get_handlers(self):
        return self.handlers


    def execute(self):
        from pipeline import Pipeline
        self.pipeline = Pipeline(self.pipeline_xml)

        try:
            # if an initial process is not specified, use an implicit one
            if not self.first_process:
                self.first_process = self.pipeline.get_first_process_name()
            self.handle_process(self.first_process)
        except Exception as e:
            if not self.handlers:
                raise
            print("Failed at handler: ", self.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = self.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception as e:
                print("Could not undo:", str(e) )
                raise

            raise


    def handle_process(self, process, input_process=None):
        '''handle the individual process

        @params
        process - the name of the process to be handled
        input_process - the name of the input process that called
            this process
        '''

        # get the handler and instantiate it
        handler_class = self.pipeline.get_handler_class(process)
        if handler_class:
            try:
                handler = Common.create_from_class_path(handler_class)
            except ImportError:
                raise ImportError("Could not import handler class [%s]" % handler_class)

        else:
            handler = Handler()

        # pass the options to the handler
        options = self.pipeline.get_action_options(process)
        handler.set_options(options)
        
        # pass relevant information to the handler
        handler.set_process_name(process)
        handler.set_server(self.server)
        handler.set_pipeline(self.pipeline)
        handler.set_package(self.package)

        # if this is the first process (no input process, then the package
        # is the input 
        if not input_process:
            output = self.package.copy()
        else:
            # get input processes and hand over the delivery
            input_handler = self.handlers_dict.get(input_process)
            if input_handler:
                output = input_handler.get_output()
            else:
                output = {}

        # By default, inputs travel through
        handler.set_input( output )
        handler.set_output( output )


        # store the handler and execute
        self.handlers.append(handler)
        self.handlers_dict[process] = handler
        handler.execute()

        # process all of the output handlers.  First ask the current handler
        # for the next process
        output_processes = handler.get_next_processes()

        # if output processes is None, then stop this branch completely
        if output_processes == None:
            return

        # otherwise, use the pipeline
        if not output_processes:
            output_processes = self.pipeline.get_output_process_names(process)

        for output_process in output_processes:
            self.handle_process(output_process, process)








    """ 
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
        except Exception as e:
            if not self.handlers:
                raise
            print("Failed at handler: ", self.handlers[-1])
            try:
                # make a copy and reverse the handlers
                handlers = self.handlers[:]
                handlers.reverse()
                for handler in handlers:
                    handler.undo()
            except Exception as e:
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
            handler = Common.create_from_class_path(handler_cls)
        except ImportError:
            raise ImportError("Could not import handler class [%s]" % handler_cls)
            
        handler.set_server(self.server)
        handler.set_package(package)

        # hand over the delivery
        if self.handlers:
            handler.set_input( self.handlers[-1].get_output() )

        self.handlers.append(handler)
        handler.execute()
    """



