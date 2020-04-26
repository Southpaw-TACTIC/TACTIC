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


from houdini import Houdini, hscript, HoudiniException
from houdini_environment import HoudiniEnvironment

import unittest, os

class HoudiniTest(unittest.TestCase):

    def test_all(self):
        env = HoudiniEnvironment.get()
        self.app = Houdini()
        env.set_app(self.app)

        self.instance = "cow"

        self._test_hscript()
        self._test_attr()
        self._test_select()
        self._test_file()


    def _test_hscript(self):
        # test basic hscript connection
        hscript("opcf /obj")
        hscript("opadd -n subnet %s" % self.instance)
        nodes = hscript("opls").split()
        self.assertEquals(True, self.instance in nodes)


    def _test_attr(self):

        # test the basic commands
        self.app.set_attr(self.instance, "rx", 5.5)
        value = self.app.get_attr(self.instance, "rx")
        self.assertEquals( value, 5.5)

        # try to set a string
        try:
            self.app.set_attr(self.instance, "rx", "cow")
        except HoudiniException, e:
            pass
        else:
            self.fail()


    def _test_select(self):

        self.app.select(self.instance)
        selected = self.app.get_selected_nodes()
        self.assertEquals(True, self.instance in selected)


    def _test_file(self):

        instance = self.app.import_reference("C:/chr001.otl", "horse")

        # check if it is a reference
        is_reference = self.app.is_reference(instance)
        self.assertEquals( True, is_reference )
        
        # create a subnet
        hscript("opadd -n subnet subnet_test")
        is_reference = self.app.is_reference("subnet_test")
        self.assertEquals( False, is_reference )
        hscript("oprm subnet_test")


        # export the animation
        self.app.set_attr(instance, "tx", 3.154)
        tmp_file = "C:/sthpw/temp/%s.cmd" % instance
        self.app.export_anim(tmp_file, instance)

        # remove the instance and recreate
        hscript("oprm %s" % instance)
        instance = self.app.import_reference("C:/chr001.otl", "horse")
        self.app.import_anim(tmp_file, instance)

        value = self.app.get_attr(instance, "tx")
        self.assertEquals(3.154, value)
        hscript("oprm %s" % instance)
        os.unlink(tmp_file)


        # save out the file
        save_file = "C:/sthpw/temp/whatever.hip"
        self.app.save(save_file)
        self.assertEquals( True, os.path.exists(save_file) )
        os.unlink(save_file)


        # find ops of a certain type
        nodes = self.app.get_nodes_by_type("xxxxyyxx")
        self.assertEquals( True, not nodes )

        nodes = self.app.get_nodes_by_type("chr001")
        self.assertEquals( False, not nodes )
        


        # remove the test node
        #hscript("oprm %s" % self.instance)


        


if __name__ == "__main__":
    unittest.main()

