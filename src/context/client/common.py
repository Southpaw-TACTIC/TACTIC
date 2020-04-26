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
__all__ = ['TacticException', 'TacticInfo']

import cStringIO, os, sys, urllib, xmlrpclib, re, string
from xml.dom.minidom import parseString


from pyasm.application.common import BaseAppInfo


class TacticException(Exception):
    pass


class TacticInfo(BaseAppInfo):
    '''Holds data in application session that is fed by the tactic server.
    For this implementation, the information is retrieved by get
    variables from application.  This information is generally fed into
    the environment class'''

    def get_ticket(self):
        return self.app.get_var("tactic_ticket")


    def get_tactic_server(self):
        tactic_server = self.app.get_var("tactic_server")
        return tactic_server
        


    def get_xmlrpc_server(self):
        xmlrpc_url = self.app.get_var("tactic_xmlrpc")
        # Applications can't take https 
        #xmlrpc_url = xmlrpc_url.replace('https:', 'http:')
        
        # can't check for None here because this fires and __eq__ function
        # to the server
        if not isinstance(self.xmlrpc_server, xmlrpclib.Server):
            self.xmlrpc_server = xmlrpclib.Server(xmlrpc_url, allow_none=True)
            
            # WARNING: this is changing code in the xmlrpclib library.  This
            # library is not sending a proper user agent.  Hacking it in
            # that it is a little better
            if os.name == "nt":
                user_agent = 'xmlrpclib.py (Windows)'
            else:
                user_agent = 'xmlrpclib.py (Linux)'
            xmlrpclib.Transport.user_agent = user_agent

        # this will be removed. as project_code should be set per call.
        project_code = self.get_project_code()
        if project_code:
            self.xmlrpc_server.set_project(project_code)
        return self.xmlrpc_server

    def get_upload_server(self):
        upload_url = self.app.get_var("tactic_upload")
        return upload_url

    def get_user(self):
        user = self.app.get_var("tactic_user")
        return user

    def get_tmpdir(self):
        tmpdir = self.app.get_var("tactic_tmpdir")
        return tmpdir

    def get_sandbox_dir(self):
        sandbox_dir = self.app.get_var("tactic_sandbox_dir")
        return sandbox_dir

    def get_project_code(self):
        project_code = self.app.get_var("tactic_project_code")
        return project_code

    def get_server(self):
        base_url = self.app.get_var("tactic_base_url")
        base_url = re.sub('http://|https://', '', base_url)
        return base_url

# general common functions
def upload_warning():
    info = TacticInfo.get()
    info.report_warning('','', upload=True)

    #remove the file afterwards
    path = "%s/warning.txt" % info.get_tmpdir()
    if os.path.exists(path):
        os.unlink(path)

def explore(dir):
    '''create path and open explorer'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    if os.name=='nt':
        program = 'explorer'
        for path in string.split(os.environ["PATH"], os.pathsep):
            file = os.path.join(path, program) + ".exe"
            try:
                return os.spawnv(os.P_WAIT, file, (file,) + tuple(['file://%s' %dir]))
            except os.error:
                pass
        raise os.error, "cannot find executable"
        
    else: # mac OSX
        program = '/usr/bin/open'
        os.system('%s %s' %(program, dir))

