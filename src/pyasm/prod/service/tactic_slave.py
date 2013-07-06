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


# DEPRECATED


import cherrypy

import os
from pyasm.common import Common
from pyasm.command import Command
from pyasm.web import WebContainer
from pyasm.security import XmlRpcInit
from pyasm.security import Security
from pyasm.search import Search
from pyasm.search import SearchType
from pyasm.prod.render import *


class Root:
    pass

class SlaveXmlRpcServer:
    '''This class assumes the availiablilty of all of the Tactic installation
    and the an nfs link to the asset library.  It will run as an low
    load xmlrpc server enabling distribution of Tactic commands to other
    computers'''

    def __init__(my):
        my.ticket = None
        my.is_busy = False


    def _cpOnError(self):
        import traceback, StringIO
        bodyFile = StringIO.StringIO()
        traceback.print_exc(file = bodyFile)
        errorBody = bodyFile.getvalue()        
        print "Error: ", errorBody
        if cherrypy.request.isRPC: 
            ## isRPC boolean is set on xml-rpc requests by the filter
            ## convert the traceback to a dumped Fault object: 
            ## the XML-RPC exception
            import xmlrpclib
            cherrpy.response.body = xmlrpclib.dumps(xmlrpclib.Fault(1,errorBody))
        else:
            ## handle regular web errors
            cherrpy.response.body = '<pre>%s</pre>' % errorBody




    @cherrypy.expose()
    def do_login(my, ticket, tactic_install_path=None):
        os.environ["TACTIC_CONFIG_PATH"] = "/home/apache/tactic_sites/config/tactic_linux-conf.xml"
        # initialize the framework and login
        xmlrpc = XmlRpcInit(ticket)
        security = xmlrpc.get_security()
        ticket = security.get_ticket().get_key()
        return "ticket: %s" % ticket



    @cherrypy.expose()
    def do_command(my, pickled):
        import pickle
        # launch pickled command
        command = pickle.loads(pickled)
        Command.execute_cmd(command)
        return "OK"



cherrypy.root = Root()
cherrypy.root.xmlrpc = SlaveXmlRpcServer()
cherrypy.config.update(
    {
     'global': { 'server.socketPort': 8081, 'server.environment': 'production' },
     '/xmlrpc': { 'xmlRpcFilter.on': True, 'xmlRpcFilter.encoding': 'latin-1',}
    }
)

cherrypy.server.start()
