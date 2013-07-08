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


class Root:
    @cherrypy.expose()
    def index(my):
        return "hello"

class RemoteXmlRpcServer:
    '''This server assumes that there is no connection to any Tactic softwre
    code base or access by nfs to the asset filesystem.  It is a remote
    server that tactic can use with minimal install.  All of the marshalling
    and caching of files and code is handled transparently'''

    my.is_busy = True

    #def login_user(my, name, password):
    #    os.environ["TACTIC_CONFIG_PATH"] = "/home/apache/tactic_sites/config/tactic_linux-conf.xml"
    #    security = Security()
    #    WebContainer.set_security(security)
    #    security.login_user(name,password)
    #    my.ticket = security.get_ticket()


    def do_download(my, url, to_path):
        import urllib, os
        f = urllib.urlopen(url)
        file = open(to_path, 'w')
        file.write(f.read())
        file.close()
        f.close()

    def is_busy(my):
        return my.is_busy


    @cherrypy.expose()
    def do_remote_render(my, execute_xml):
        '''This data gets an xml document and downloads the files
        and renders them.  There are no interactions with the database
        and suitable to run on a render farm or a remote machine'''

        # TODO: should have to login at some point!!!!

        local_dir = "/tmp/sthpw"
        server_url = "http://saba"

        # get the client files
        zip = local_dir+"/download/sthpw.zip"
        my.do_download(server_url+"/sthpw/context/client/sthpw.zip", zip)

        delegator = local_dir+"/download/delegator.py"
        my.do_download(server_url+"/sthpw/context/client/delegator.py", delegator )

        import sys
        sys.path.append(local_dir+"/download/sthpw.zip")

        print execute_xml

        from maya import MayaEnvironment
        from maya import Maya
        maya_env = MayaEnvironment.get()
        maya = Maya(init=True)
        maya.set_verbose()
        maya_env.set_maya(maya)
        maya_env.set_tmpdir(local_dir+"/download")

        from maya import MayaBuilder
        loader = MayaBuilder()
        loader.execute(execute_xml)

        filepath = local_dir+"/download/maya_render.ma"
        maya_env.get_maya().save(filepath)

        os.system("Render %s" % filepath)

        return "Done"






cherrypy.root = Root()
cherrypy.root.xmlrpc = RootXmlRpcServer()
cherrypy.config.update(
    {
     'global': { 'server.socketPort': 8081, },
     '/xmlrpc': { 'xmlrpc_filter.on': True, 'xmlrpc_filter.encoding': 'latin-1',}
    }
)

cherrypy.server.start()
