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

    def test_all(my):
        
        my.test_handler = 'tactic_client_lib.test.TestHandler'
        my.pipeline_xml = '''
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
        ''' % (my.test_handler, my.test_handler)

        my.pipeline = Pipeline(my.pipeline_xml)

        my._test_pipeline()
        my._test_interpreter()


    def _test_pipeline(my):
        # get the output names
        output_names = my.pipeline.get_output_process_names('model')
        my.assertEquals( ['texture', 'rig'], output_names )

        # get the input names
        input_names = my.pipeline.get_input_process_names('texture')
        my.assertEquals( ['model'], input_names)

        # get the handler class of model
        handler_class = my.pipeline.get_handler_class('model')
        my.assertEquals( my.test_handler, handler_class)


        # small test running through pipeline
        process = my.pipeline.get_first_process_name()
        my.assertEquals( 'model', process)


    def _test_interpreter(my):

        # create a package to be delivered to each handler
        package = {
            'company': 'Acme',
            'city': 'Toronto',
            'context': 'whatever'
        }

        # use client api
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub()

        interpreter = PipelineInterpreter(my.pipeline_xml)
        interpreter.set_server(server)
        interpreter.set_package(package)
        interpreter.execute()

        # introspect the interpreter to see if everything ran well
        handlers = interpreter.get_handlers()
        process_names = [x.get_process_name() for x in handlers]
        expected = ['model', 'texture', 'rig', 'extra1', 'extra2']
        my.assertEquals( expected, process_names )

        # make sure all the handlers completed
        my.assertEquals( 5, len(handlers) )
        for handler in handlers:
            my.assertEquals( "complete", handler.get_status() )

            # check that the package is delivered to the input
            my.assertEquals("Acme", handler.get_input_value('company') )
            my.assertEquals("Toronto", handler.get_input_value('city') )

            process_name = handler.get_process_name()
            if process_name == 'model':
                my.assertEquals("Acme", handler.company)

                my.assertEquals("pig", handler.get_option_value('test') )
                my.assertEquals("cow", handler.get_option_value('test2') )

            # ensure input settings propogate
            if process_name == 'extra1':
                my.assertEquals("test.txt", handler.get_output_value('file'))
                my.assertEquals("Acme", handler.get_package_value('company'))





if __name__ == "__main__":
    unittest.main()

