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

    def test_all(my):
        env = HoudiniEnvironment.get()
        my.app = Houdini()
        env.set_app(my.app)

        my.instance = "cow"

        my._test_hscript()
        my._test_attr()
        my._test_select()
        my._test_file()


    def _test_hscript(my):
        # test basic hscript connection
        hscript("opcf /obj")
        hscript("opadd -n subnet %s" % my.instance)
        nodes = hscript("opls").split()
        my.assertEquals(True, my.instance in nodes)


    def _test_attr(my):

        # test the basic commands
        my.app.set_attr(my.instance, "rx", 5.5)
        value = my.app.get_attr(my.instance, "rx")
        my.assertEquals( value, 5.5)

        # try to set a string
        try:
            my.app.set_attr(my.instance, "rx", "cow")
        except HoudiniException, e:
            pass
        else:
            my.fail()


    def _test_select(my):

        my.app.select(my.instance)
        selected = my.app.get_selected_nodes()
        my.assertEquals(True, my.instance in selected)


    def _test_file(my):

        instance = my.app.import_reference("C:/chr001.otl", "horse")

        # check if it is a reference
        is_reference = my.app.is_reference(instance)
        my.assertEquals( True, is_reference )
        
        # create a subnet
        hscript("opadd -n subnet subnet_test")
        is_reference = my.app.is_reference("subnet_test")
        my.assertEquals( False, is_reference )
        hscript("oprm subnet_test")


        # export the animation
        my.app.set_attr(instance, "tx", 3.154)
        tmp_file = "C:/sthpw/temp/%s.cmd" % instance
        my.app.export_anim(tmp_file, instance)

        # remove the instance and recreate
        hscript("oprm %s" % instance)
        instance = my.app.import_reference("C:/chr001.otl", "horse")
        my.app.import_anim(tmp_file, instance)

        value = my.app.get_attr(instance, "tx")
        my.assertEquals(3.154, value)
        hscript("oprm %s" % instance)
        os.unlink(tmp_file)


        # save out the file
        save_file = "C:/sthpw/temp/whatever.hip"
        my.app.save(save_file)
        my.assertEquals( True, os.path.exists(save_file) )
        os.unlink(save_file)


        # find ops of a certain type
        nodes = my.app.get_nodes_by_type("xxxxyyxx")
        my.assertEquals( True, not nodes )

        nodes = my.app.get_nodes_by_type("chr001")
        my.assertEquals( False, not nodes )
        


        # remove the test node
        #hscript("oprm %s" % my.instance)


        


if __name__ == "__main__":
    unittest.main()

