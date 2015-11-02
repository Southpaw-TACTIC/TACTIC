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


__all__ = ['Pipeline']

IMPORT_ERROR = None
try:
    from xml.dom.ext.reader import Sax2
    from xml import xpath
except ImportError:
    IMPORT_ERROR =  "WARNING: pipeline.py in client api requires PyXML'"


class Pipeline(object):
    '''class that stores the data structure of the a pipeline.  Internally,
    this is stored as a linked list'''

    def __init__(my, pipeline_xml):
        if IMPORT_ERROR:
            print IMPORT_ERROR
            return
        my.doc = Sax2.FromXml(pipeline_xml)


    def get_first_process_name(my):
        # for now, just assume the first process
        nodes = xpath.Evaluate("/pipeline/process", my.doc)
        node = nodes[0]
        return node.getAttribute('name')


    def get_process_info(my, process_name):
        processes = xpath.Evaluate("/pipeline/process[@name='%s']" % process_name, my.doc)
        if not processes:
            return {}
        process = processes[0]

        #print "get_process_info: ", process_name
        return process_name

        



    def get_output_process_names(my, process_name):
        attrs = xpath.Evaluate("/pipeline/connect[@from='%s']/@to" % process_name, my.doc)
        return [x.value for x in attrs]


    def get_input_process_names(my, process_name):

        attrs = xpath.Evaluate("/pipeline/connect[@to='%s']/@from" % process_name, my.doc)
        return [x.value for x in attrs]


    def get_handler_class(my, process_name):
        nodes = xpath.Evaluate("/pipeline/process[@name='%s']/action" % process_name, my.doc)
        if not nodes:
            return ""

        action = nodes[0]
        action_class = action.getAttribute("class")
        return action_class


    def get_action_options(my, process_name):
        options = {}
        nodes = xpath.Evaluate("/pipeline/process[@name='%s']/action" % process_name, my.doc)
        if not nodes:
            return options

        action_node = nodes[0]
        nodes = action_node.childNodes
        for node in nodes:
            name = node.nodeName
            if name == "#text":
                continue
            value = my._get_node_value(node)
            options[name] = value

        return options



    def _get_node_value(cls, node):
        '''Gets the value of a node.  This value is often the first child
        of the node'''
        value = node.nodeValue
        if value == None:
            if node.firstChild == None:
                value = ""
            else:
                value = node.firstChild.nodeValue

        return value
    _get_node_value = classmethod(_get_node_value)

