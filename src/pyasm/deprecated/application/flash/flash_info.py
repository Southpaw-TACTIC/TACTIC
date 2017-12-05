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
__all__ = ['FlashInfo']

import cStringIO, os, sys, urllib, xmlrpclib
from xml.dom.minidom import parseString


from pyasm.application.common import BaseAppInfo


class FlashInfo(BaseAppInfo):
    '''Gets data fed by the TACTIC server in a well know location'''

    def __init__(my, app_name):

        super(FlashInfo,my).__init__(app_name)

        # read from a file a parse
        my.ticket = "2b6754788b90877f0240e4b1d8e620b3"
        my.xmlrpc_url = "http://fugu/tactic/flash/XMLRPC"
        my.upload_server = "http://fugu/tactic/default/UploadServer/"
        my.tactic_user = "boris"
        my.tmpdir = "D:/tactic_temp"
        my.trash_dir = '%s/temp' %my.tmpdir
        my.sandbox_dir = "D:/tactic_temp/sandbox"
        my.publish_dir = "D:/tactic_temp/publish/%s" %my.tactic_user
        my.check_dirs()

    def check_dirs(my):
        
        if not os.path.exists(my.trash_dir):
            os.makedirs(dir)
        if not os.path.exists(my.publish_dir):
            os.makedirs(my.publish_dir)

    def get_ticket(my):
        assert my.ticket
        return my.ticket

    def get_xmlrpc_server(my):
        assert my.xmlrpc_url
        if not my.xmlrpc_server:
            my.xmlrpc_server = xmlrpclib.Server(my.xmlrpc_url)
        return my.xmlrpc_server

    def get_upload_server(my):
        assert my.upload_server
        return my.upload_server

    def get_user(my):
        assert my.user
        return my.user

    def get_tmp_dir(my):
        assert my.tmpdir
        return my.tmpdir

    def get_sandbox_dir(my):
        assert my.sandbox_dir
        return my.sandbox_dir

    def get_log_path(my):
        
        to_path = '%s/actionLog.txt' %my.trash_dir
        if not os.path.exists(to_path):
            file = open(to_path, "wb")
        return to_path

    def get_publish_dir(my):
        return my.publish_dir

    def report_error(my, exception):
        print "Error: ", exception

    def report_warning(my, exception):
        print "Warning: ", exception

"""
def upload_warning():
    info = TacticInfo.get()
    info.report_warning('','', upload=True)

    #remove the file afterwards
    path = "%s/warning.txt" % info.get_tmpdir()
    if os.path.exists(path):
        os.unlink(path)

"""
