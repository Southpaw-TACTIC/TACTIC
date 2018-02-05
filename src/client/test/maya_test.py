#!/usr/bin/python 
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


__all__ = ['MayaTest']



import unittest
import xmlrpclib, sys, os, shutil

class MayaTest(unittest.TestCase):
    '''Test the basic level interaction to Maya'''

    def test_all(self):

        from tactic_client_lib.application.common import TacticNodeUtil
        self.util = TacticNodeUtil()
        from tactic_client_lib.application.maya import Maya
        self.app = Maya()

        self._test_nodes()
        self._test_attributes()
        self._test_file()



    def _test_nodes(self):

        # create a test node
        node_name = "test_node"
        created_name = self.app.add_node(node_name)
        self.assertEquals(node_name, created_name)

        # test to see whether it exists
        exists = self.app.node_exists(created_name)
        self.assertEquals(True, exists)

        # create a node of the same name
        created_name2 = self.app.add_node(node_name)
        self.assertEquals("test_node1", created_name2)

        # create a node that should be unique
        created_name3 = self.app.add_node(node_name, unique=True)
        self.assertEquals("test_node", created_name3)

        # get the nodes by name pattern
        pattern = "test_*"
        nodes = self.app.get_nodes_by_name(pattern)
        self.assertEquals(['test_node','test_node1'], nodes)
        





    def _test_attributes(self):
        '''tests various attribute functionality'''



    def _test_file(self):
        if os.name == "nt":
            dir = "C:/sthpw/temp"
        else:
            dir = "/tmp/sthpw/temp"
        if not os.path.exists(dir):
            os.makedirs(dir)

        path = '%s/test' % dir
        if os.path.exists(path):
            os.unlink(path)

        path = self.app.save(path)            
        self.assertEquals(True, os.path.exists(path))

        # remove the file
        if os.path.exists(path):
            os.unlink(path)



    def main():        
        import sys
        sys.path.insert(0, "C:/Program Files/Southpaw/Tactic1.9/src/client")
        try:
            unittest.main()
        except SystemExit:
            pass
    main = staticmethod(main)



if __name__ == "__main__":
    MayaTest.main()

