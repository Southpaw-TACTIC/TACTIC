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

import tacticenv

from pyasm.security import Batch
from pyasm.search import Search, SearchType, Transaction
from pyasm.biz import Project

from pipeline import *

from pyasm.unittest import UnittestEnvironment


import unittest

class ProcessTest(unittest.TestCase):



    def test_all(self):

        Batch()

        test_env = UnittestEnvironment()
        test_env.create()

        Project.set_project("unittest")


        self.transaction = Transaction.get(create=True)
        try:

            self._test_process()
            self._test_version()

        finally:
            self.transaction.rollback()
            Project.set_project('unittest')

            test_env.delete()

 

    def _test_process(self):


        pipeline_xml = '''
        <pipeline>
          <process type="process" name="a"/>
          <process type="condition" name="b"/>
          <process type="process" name="c"/>
          <process type="process" name="d"/>
          <process type="process" name="e"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c" from_attr="success"/>
          <connect from="b" to="d" from_attr="fail"/>
          <connect from="b" to="e" from_attr="fail" to_attr="revise"/>
        </pipeline>

        '''

        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_pipeline(pipeline_xml)
        pipeline.set_value("code", "test")

        # outputs
        processes = pipeline.get_output_processes("a")
        self.assertEquals(1, len(processes))

        processes = pipeline.get_output_processes("b")
        self.assertEquals(3, len(processes))
        self.assertEquals("c", processes[0].get_name())
        self.assertEquals("d", processes[1].get_name())

        # inputs
        processes = pipeline.get_input_processes("b")
        self.assertEquals("a", processes[0].get_name())


        # output with attr
        processes = pipeline.get_output_processes("b", from_attr="success")
        self.assertEquals(1, len(processes))
        self.assertEquals("c", processes[0].get_name())

        processes = pipeline.get_output_processes("b", from_attr="fail")
        self.assertEquals(2, len(processes))
        self.assertEquals("d", processes[0].get_name())


        # input with attr
        processes = pipeline.get_input_processes("e", to_attr="revise")
        self.assertEquals("b", processes[0].get_name())




    def _test_pipeline(self):

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
            print(process)

        from_processes = pipeline.get_from_processes("supervisor")
        for process in from_processes:
            print(process)




    def _test_version(self):
        """
        Tests that overwriting pipeline definition with/without versions produces consistent results.
        """

        return

        city = SearchType.create("unittest/city")
        city.set_value("code", "los_angeles")
        city.set_value("name", "LA")
        city.set_value("country_code", "USA")
        city.commit()


        pipeline_xml = '''
        <pipeline>
          <process type="process" name="a"/>
          <process type="process" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''


        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_value("name", "my_pipeline")
        pipeline.set_pipeline(pipeline_xml)
        pipeline.commit()

        pipeline_code = pipeline.get_code()
        city.set_value("pipeline_code", pipeline_code)
        city.commit()


        # When a pipeline is saved, it overrites the current definition.  Most often, the
        # versionless will be saved. All sobjects pointing to a pipeline will have te newly
        # saved version
        pipeline_xml = '''
        <pipeline>
          <process type="process" name="a"/>
          <process type="process" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''
        pipeline.set_pipeline(pipeline_xml)
        pipeline.commit()


        # However, if an sobject is pointing to a versioned pipeline, then since that definition
        # will likely never change, the sobject will point to a locked version



        pipeline1 = pipeline.save_version()
        version1 = pipeline1.get_value("version")
        self.assertEquals(version1, 1)

        pipeline2 = pipeline.save_version()
        version2 = pipeline2.get_value("version")
        self.assertEquals(version2, 2)

        """
        # an sobject can point to the latest version
        pipeline.set_sobject_to_latest(city)

        # or it can point to the versionless (which can change definition)
        pipeline.set_sobject_to_versionless(city)

        # or point to a specific version
        pipeline.set_sobject_to_version(city, 2)


        # the versionless pipeline can revert back to an older version
        pipeline.revert_to_version(1)
        """














if __name__ == "__main__":
    unittest.main()

