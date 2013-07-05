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

import re, sys, cStringIO, xmlrpclib

from common import *
import checkin, load


def create(set_name, cat_name, context):
    '''update a node in the session'''
    info = TacticInfo.get()
    ticket = info.get_ticket()
    server = info.get_xmlrpc_server()
   
    app = info.get_app()
    # get all of the top level assets
    selected = app.mel("ls -sl -as")
   
    if not selected:
        raise TacticException('At least 1 asset (top node) needs to be selected in the session!')
    xml, asset_code = server.create_set(ticket, set_name, cat_name, selected)
    builder = info.get_builder()
    builder.execute(xml)

    if asset_code:
        # checkin_set and upload the files 
        checkin.checkin_set(set_name, asset_code)
        
        # publish the set
        snapshot_code = server.checkin_set(ticket, asset_code, context)

        # update tacticNodeInfo
        #context = "publish"
        load.update(snapshot_code, asset_code, set_name, context) 
    
    
'''
#OLD CODE   
class CreateSetAsset:

    def __init__(my, set_code):
        my.set_code = set_code
        my.info = TacticInfo.get()
        my.ticket = my.info.get_ticket()
        
    def execute(my):

        # get all of the top level assets
        selected = mel("ls -sl -as")

        for instance in selected:
            print instance

            # export the node
            mel("select %s" % instance)
            path = mel("file -rename %s" % instance )
            mel("file -f -es -type mayaAscii")

            # for some reason file -rename always returns .mb extension?!?
            p = re.compile(r'\.mb$')
            path = p.sub('.ma', path)

            my.upload(path)
        
        mel("select %s" % " ".join(selected) )

        # now create all of the assets through xmlrpc
        server = my.info.get_xmlrpc_server()
        asset_codes = server.create_assets(my.ticket, my.set_code, selected)

        # rename nodes
        count = 0
        for instance in selected:
            mel("rename %s %s" % (instance, asset_codes[count]) )
            count += 1


    def upload(my, from_path):
        my.info.upload(from_path)



if __name__ == '__main__':
    executable = sys.argv[0]
    args = sys.argv[1:]

    set_code = args[0]

    cmd = CreateSetAsset(set_code)
    cmd.execute()

'''

