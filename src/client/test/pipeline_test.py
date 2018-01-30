#!/usr/bin/python 
###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import unittest, sys

# import the client lib
sys.path.insert( 0, ".." )
from tactic_client_lib.interpreter import *



class PipelineTest(unittest.TestCase):

    def test_all(self):
        
        self.test_handler = 'tactic_client_lib.test.TestHandler'
        self.pipeline_xml = '''
        <pipeline>
          <process name='model'>
            <action class='%s'>
                <test>pig</test>
                <test2>cow</test2>
            </action>
          </process>
          <process name='texture'>
            <action class='%s'/>
          </process>
          <process name='rig'>
            <action class='tactic_client_lib.test.TestNextProcessHandler'/>
          </process>
          <process name='extra'/>
          <process name='extra2'/>
          <connect from='model' to='texture'/>
          <connect from='model' to='rig'/>
          <connect from='rig' to='publish'/>
        </pipeline>
        ''' % (self.test_handler, self.test_handler)

        self.pipeline = Pipeline(self.pipeline_xml)

        self._test_pipeline()
        self._test_interpreter()


    def _test_pipeline(self):
        # get the output names
        output_names = self.pipeline.get_output_process_names('model')
        self.assertEquals( ['texture', 'rig'], output_names )

        # get the input names
        input_names = self.pipeline.get_input_process_names('texture')
        self.assertEquals( ['model'], input_names)

        # get the handler class of model
        handler_class = self.pipeline.get_handler_class('model')
        self.assertEquals( self.test_handler, handler_class)


        # small test running through pipeline
        process = self.pipeline.get_first_process_name()
        self.assertEquals( 'model', process)


    def _test_interpreter(self):

        # create a package to be delivered to each handler
        package = {
            'company': 'Acme',
            'city': 'Toronto',
            'context': 'whatever'
        }

        # use client api
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub()

        interpreter = PipelineInterpreter(self.pipeline_xml)
        interpreter.set_server(server)
        interpreter.set_package(package)
        interpreter.execute()

        # introspect the interpreter to see if everything ran well
        handlers = interpreter.get_handlers()
        process_names = [x.get_process_name() for x in handlers]
        expected = ['model', 'texture', 'rig', 'extra1', 'extra2']
        self.assertEquals( expected, process_names )

        # make sure all the handlers completed
        self.assertEquals( 5, len(handlers) )
        for handler in handlers:
            self.assertEquals( "complete", handler.get_status() )

            # check that the package is delivered to the input
            self.assertEquals("Acme", handler.get_input_value('company') )
            self.assertEquals("Toronto", handler.get_input_value('city') )

            process_name = handler.get_process_name()
            if process_name == 'model':
                self.assertEquals("Acme", handler.company)

                self.assertEquals("pig", handler.get_option_value('test') )
                self.assertEquals("cow", handler.get_option_value('test2') )

            # ensure input settings propogate
            if process_name == 'extra1':
                self.assertEquals("test.txt", handler.get_output_value('file'))
                self.assertEquals("Acme", handler.get_package_value('company'))





if __name__ == "__main__":
    unittest.main()

