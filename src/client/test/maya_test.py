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

    def test_all(my):

        from tactic_client_lib.application.common import TacticNodeUtil
        my.util = TacticNodeUtil()
        from tactic_client_lib.application.maya import Maya
        my.app = Maya()

        my._test_nodes()
        my._test_attributes()
        my._test_file()



    def _test_nodes(my):

        # create a test node
        node_name = "test_node"
        created_name = my.app.add_node(node_name)
        my.assertEquals(node_name, created_name)

        # test to see whether it exists
        exists = my.app.node_exists(created_name)
        my.assertEquals(True, exists)

        # create a node of the same name
        created_name2 = my.app.add_node(node_name)
        my.assertEquals("test_node1", created_name2)

        # create a node that should be unique
        created_name3 = my.app.add_node(node_name, unique=True)
        my.assertEquals("test_node", created_name3)

        # get the nodes by name pattern
        pattern = "test_*"
        nodes = my.app.get_nodes_by_name(pattern)
        my.assertEquals(['test_node','test_node1'], nodes)
        





    def _test_attributes(my):
        '''tests various attribute functionality'''



    def _test_file(my):
        if os.name == "nt":
            dir = "C:/sthpw/temp"
        else:
            dir = "/tmp/sthpw/temp"
        if not os.path.exists(dir):
            os.makedirs(dir)

        path = '%s/test' % dir
        if os.path.exists(path):
            os.unlink(path)

        path = my.app.save(path)            
        my.assertEquals(True, os.path.exists(path))

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

