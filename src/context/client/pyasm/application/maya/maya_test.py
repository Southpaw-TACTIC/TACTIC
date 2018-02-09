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

    def test_all(self):

        # start up maya session
        self.maya = Maya70()
        MayaEnvironment.get().set_maya(self.maya)


        self._test_basic()
        self._test_namespace()

        self.maya.cleanup()


    def _test_basic(self):

        # create a few spheres
        node1, shape1 = mel("sphere")
        node2, shape2 = mel("sphere")

        self.assertEquals("nurbsSphere1", node1)
        self.assertEquals("nurbsSphere2", node2)

        # test set_attr
        self.maya.set_attr(node1, "translateX", 1)
        tx = self.maya.get_attr(node1, "translateX")
        self.assertEquals(1, tx)



        # test top nodes
        nodes = self.maya.get_top_nodes()
        self.assertEquals(nodes, ['front', 'nurbsSphere1', 'nurbsSphere2', 'persp', 'side', 'top'] )

        # test select node
        self.maya.select("nurbsSphere1")
        selected = self.maya.get_selected_node()
        self.assertEquals(selected, "nurbsSphere1")


    def _test_namespace(self):
        # test namespaces
        self.maya.add_namespace("cow")
        self.maya.set_namespace("cow")
        mel("sphere")
        namespace_nodes = self.maya.get_namespace_contents()
        self.assertEquals(namespace_nodes, \
            ('cow:makeNurbSphere1','cow:nurbsSphere1','cow:nurbsSphereShape1'))

        # set back to main namespace
        self.maya.set_namespace()

        namespaces = self.maya.get_all_namespaces()
        self.assertEquals(namespaces, ('UI', 'cow') )

        







if __name__ == "__main__":
    unittest.main()

