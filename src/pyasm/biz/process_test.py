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

__all__ = ["ProcessTest"]


from pyasm.security import *

from pipeline import *

import unittest

class ProcessTest(unittest.TestCase):


    def setUp(my):

        # start batch environment
        Batch()

        transaction = Transaction.get().start()

    def tearDown(my):

        transaction = Transaction.get().rollback()



    def test_process(my):

        pipeline = Pipeline()

        pipeline_xml = """
        <pipeline>
            <process name="artist"/>
            <process name="supervisor"/>
            <process name="director"/>
            <process name="render"/>

            <connect from="artist" to="supervisor" type="normal"/>
            <connect from="artist" to="render" type="normal"/>
            <connect from="supervisor" to="render" type="normal"/>
            <connect from="supervisor" to="director" type="normal"/>
            <connect from="supervisor" to="artist" type="normal"/>
            <connect from="director" to="supervisor" type="normal"/>
            <connect from="director" to="artist" type="normal"/>
        </pipeline>
        """
        pipeline.set_pipeline(pipeline_xml)



        to_processes = pipeline.get_to_processes("supervisor")
        for process in to_processes:
            print process

        from_processes = pipeline.get_from_processes("supervisor")
        for process in from_processes:
            print process


        





if __name__ == "__main__":
    unittest.main()

