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


from maya_environment import *
from maya import *

import unittest

class MayaTest(unittest.TestCase):
    '''Unit test that tests all of the interactions of Tactic with Maya'''

    def test_all(my):

        # start up maya session
        my.maya = Maya70()
        MayaEnvironment.get().set_maya(my.maya)


        my._test_basic()
        my._test_namespace()

        my.maya.cleanup()


    def _test_basic(my):

        # create a few spheres
        node1, shape1 = mel("sphere")
        node2, shape2 = mel("sphere")

        my.assertEquals("nurbsSphere1", node1)
        my.assertEquals("nurbsSphere2", node2)

        # test set_attr
        my.maya.set_attr(node1, "translateX", 1)
        tx = my.maya.get_attr(node1, "translateX")
        my.assertEquals(1, tx)



        # test top nodes
        nodes = my.maya.get_top_nodes()
        my.assertEquals(nodes, ['front', 'nurbsSphere1', 'nurbsSphere2', 'persp', 'side', 'top'] )

        # test select node
        my.maya.select("nurbsSphere1")
        selected = my.maya.get_selected_node()
        my.assertEquals(selected, "nurbsSphere1")


    def _test_namespace(my):
        # test namespaces
        my.maya.add_namespace("cow")
        my.maya.set_namespace("cow")
        mel("sphere")
        namespace_nodes = my.maya.get_namespace_contents()
        my.assertEquals(namespace_nodes, \
            ('cow:makeNurbSphere1','cow:nurbsSphere1','cow:nurbsSphereShape1'))

        # set back to main namespace
        my.maya.set_namespace()

        namespaces = my.maya.get_all_namespaces()
        my.assertEquals(namespaces, ('UI', 'cow') )

        







if __name__ == "__main__":
    unittest.main()

