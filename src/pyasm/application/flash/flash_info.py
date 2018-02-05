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

    def __init__(self, app_name):

        super(FlashInfo,self).__init__(app_name)

        # read from a file a parse
        self.ticket = "2b6754788b90877f0240e4b1d8e620b3"
        self.xmlrpc_url = "http://fugu/tactic/flash/XMLRPC"
        self.upload_server = "http://fugu/tactic/default/UploadServer/"
        self.tactic_user = "boris"
        self.tmpdir = "D:/tactic_temp"
        self.trash_dir = '%s/temp' %self.tmpdir
        self.sandbox_dir = "D:/tactic_temp/sandbox"
        self.publish_dir = "D:/tactic_temp/publish/%s" %self.tactic_user
        self.check_dirs()

    def check_dirs(self):
        
        if not os.path.exists(self.trash_dir):
            os.makedirs(dir)
        if not os.path.exists(self.publish_dir):
            os.makedirs(self.publish_dir)

    def get_ticket(self):
        assert self.ticket
        return self.ticket

    def get_xmlrpc_server(self):
        assert self.xmlrpc_url
        if not self.xmlrpc_server:
            self.xmlrpc_server = xmlrpclib.Server(self.xmlrpc_url)
        return self.xmlrpc_server

    def get_upload_server(self):
        assert self.upload_server
        return self.upload_server

    def get_user(self):
        assert self.user
        return self.user

    def get_tmp_dir(self):
        assert self.tmpdir
        return self.tmpdir

    def get_sandbox_dir(self):
        assert self.sandbox_dir
        return self.sandbox_dir

    def get_log_path(self):
        
        to_path = '%s/actionLog.txt' %self.trash_dir
        if not os.path.exists(to_path):
            file = open(to_path, "wb")
        return to_path

    def get_publish_dir(self):
        return self.publish_dir

    def report_error(self, exception):
        print "Error: ", exception

    def report_warning(self, exception):
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
