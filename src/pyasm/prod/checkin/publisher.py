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

__all__ = ["PublisherException", "PublisherCmd", 'FlashAssetPublisherCmd',
]

from pyasm.common import *
from pyasm.search import *
from pyasm.command import Command
from pyasm.biz import *
from pyasm.checkin import *
from pyasm.prod.biz import *
from pyasm.prod.load import LoaderCmd


import os


class PublisherException(Exception):
    pass


class PublisherCmd(LoaderCmd):
    '''This defines that base publisher class, which will publish
    an instance of an asset in to a session.  These classes will
    essentially use a low level xml command language which a
    SessionBuilder class will handle'''

    def __init__(self):
        self.asset_code = None
        super(PublisherCmd, self).__init__()

    def set_asset_code(self, code):
        self.asset_code = code

    def execute(self):

        # get the current execute parser.  Note this assume that there
        # can only be one at a time.
        key = "PublisherCmd:top_publisher"
        top_publisher = Container.get(key)
        if top_publisher == None:
            self.execute_xml = Xml()
            self.execute_xml.create_doc("execute")
            top_publisher = self
            #self.is_top_loader_flag = True
            Container.put(key, top_publisher)
        else:
            self.execute_xml = top_publisher.execute_xml

        # decipher the XML
        self.handle_xml()

        # clean up the execute xml
        if top_publisher == self:

            print "*"*20
            self.execute_xml.dump()
            print "*"*20

            Container.remove(key)

class FlashAssetPublisherCmd(PublisherCmd):
    ''' this can handle both asset and shot publish'''

    def handle_xml(self):
        root = self.execute_xml.get_root_node()
        doc = self.execute_xml.get_doc()
        publish_node = doc.createElement("publish")
        Xml.set_attribute(publish_node, "node", self.asset_code)
        Xml.set_attribute(publish_node, "asset_code", self.asset_code)
        root.appendChild(publish_node)


   
