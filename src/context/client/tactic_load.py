###########################################################
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

import os, sys, urllib, xmlrpclib
from xml.dom.minidom import parseString


from common import *



def load(snapshot_code, context, options):
    '''load a snapshot into a session'''
    info = TacticInfo.get()
    ticket = info.get_ticket()
    server = info.get_xmlrpc_server()
    project_code = info.get_project_code()
    xml = server.get_loader_xml(ticket, project_code, snapshot_code, context, options)

    builder = info.get_builder()
    builder.execute(xml)


def update(snapshot_code, asset_code, instance, context):
    '''update a node in the session'''
    info = TacticInfo.get()
    ticket = info.get_ticket()
    server = info.get_xmlrpc_server()

    project_code = info.get_project_code()
    xml = server.get_update_xml(ticket, project_code, snapshot_code, asset_code, \
        instance, context)

    builder = info.get_builder()
    builder.execute(xml)


def replace_reference(snapshot_code, asset_code, instance, context):
    '''update a node in the session'''
    info = TacticInfo.get()
    ticket = info.get_ticket()
    server = info.get_xmlrpc_server()

    project_code = info.get_project_code()
    # set the load mode to replace, which will replace the references
    options = "load_mode=replace"
    xml = server.get_update_xml(ticket, project_code, snapshot_code, asset_code, \
        instance, context, options)

    builder = info.get_builder()
    builder.execute(xml)




def load_anim(snapshot_code, shot_code, instance, context, options):
    '''load an animated instance into a session'''

    info = TacticInfo.get()
    ticket = info.get_ticket()
    server = info.get_xmlrpc_server()

    project_code = info.get_project_code()
    xml = server.get_shot_loader_xml(ticket, project_code, snapshot_code, shot_code, instance, context, options)

    builder = info.get_builder()
    builder.execute(xml)




if __name__ == '__main__':

    '''usage: load.py <snapshot_code> <context> <options>'''
    executable = sys.argv[0]
    args = sys.argv[1:]

    snapshot_code = args[0]
    context = args[1]

    # get some options if they exists
    options = ""
    if len(args) == 3:
        options = args[2]
    load(snapshot_code, context, options)


