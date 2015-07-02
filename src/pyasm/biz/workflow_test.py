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

__all__ = ["WorkflowTest"]

import tacticenv

import unittest, random

from pyasm.common import Common
from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment
from pyasm.search import Search, SearchType
from pyasm.command import Command, Trigger

from workflow import Workflow
from task import Task

from pyasm.security import Batch



class WorkflowTest(unittest.TestCase):

    def test_all(my):
        Batch()
        from pyasm.web.web_init import WebInit

        test_env = UnittestEnvironment()
        test_env.create()

        try:
            my._test_complete_trigger()
        finally:
            test_env.delete()

            search = Search("sthpw/pipeline")
            search.add_filter("project_code", "unittest")
            pipelines = search.get_sobjects()
            for pipeline in pipelines:
                pipeline.delete()
            
 
 
    def _test_complete_trigger(my):
        cmd = WorkflowCmd()
        Command.execute_cmd(cmd)


class WorkflowCmd(Command):
    def execute(my):

        #from pyasm.security import Site
        #from pyasm.biz import Project
        #print "site: " ,Site.get_site()
        #print "project: ", Project.get().get_data()

        try:
            Workflow().init()
            my._test_hierarchy()
            my._test_js()
            my._test_manual()
            my._test_check()
            my._test_task()
            my._test_action_process()
            my._test_choice()
            my._test_input()
            my._test_trigger()
            my._test_approval()
        except Exception, e:
            print "Error: ", e
            raise


    def get_pipeline(my, pipeline_xml, add_tasks=False):

        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_pipeline(pipeline_xml)
        pipeline_id = random.randint(0, 10000000)
        #pipeline.set_value("code", "test%s" % pipeline_id)
        #pipeline.set_id(pipeline_id)
        #pipeline.set_value("id", pipeline_id)
        pipeline.set_value("pipeline", pipeline_xml)
        pipeline.commit()

        process_names = pipeline.get_process_names()

        # delete the processes
        search = Search("config/process")
        search.add_filters("process", process_names)
        processes = search.get_sobjects()
        for process in processes:
            process.delete()

        # create new processes
        processes_dict = {}
        for process_name in process_names:

            # define the process nodes
            process = SearchType.create("config/process")
            process.set_value("process", process_name)
            process.set_value("pipeline_code", pipeline.get_code())
            process.set_json_value("workflow", {
                'on_complete': '''
                sobject.set_value('%s', "complete")
                ''' % process_name,
                'on_approved': '''
                sobject.set_value('%s', "approved")
                ''' % process_name,
 
            } )
            process.commit()

            processes_dict[process_name] = process


            # Note: we don't have an sobject yet
            if add_tasks:
                task = SaerchType.create("sthpw/task")
                task.set_parent(sobject)
                task.set_value("process", process_name)
                task.commit()


        return pipeline, processes_dict



    def _test_js(my):
        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")

        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)

        process = processes.get("a")
        process.set_json_value("workflow", {
            'cbjs_action': '''
            console.log("This is javascript");
            console.log(input);
            return false
            '''
        } )
        process.commit()


        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }

        import time
        start = time.time()
        Trigger.call(my, "process|pending", output)
        #my.assertEquals( "complete", sobject.get_value("a"))




    def _test_action_process(my):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")
        sobject.set_value("a", False)
        sobject.set_value("b", False)
        sobject.set_value("c", False)
        sobject.set_value("d", False)
        sobject.set_value("e", False)

        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="action" name="b"/>
          <process type="action" name="c"/>
          <process type="action" name="d"/>
          <process type="action" name="e"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
          <connect from="b" to="d"/>
          <connect from="c" to="e"/>
          <connect from="d" to="e"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)


        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }

        import time
        start = time.time()
        Trigger.call(my, "process|pending", output)
        #print "time: ", time.time() - start
        my.assertEquals( "complete", sobject.get_value("a"))
        my.assertEquals( "complete", sobject.get_value("b"))
        my.assertEquals( "complete", sobject.get_value("c"))
        my.assertEquals( "complete", sobject.get_value("d"))

        # TODO: this got called twice ... not what we want : fix later
        my.assertEquals( "complete", sobject.get_value("e"))



    def _test_check(my):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")
        sobject.set_value("a", False)
        sobject.set_value("b", False)
        sobject.set_value("c", False)

        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="condition" name="b"/>
          <process type="action" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c" from_attr="success"/>
          <!--
          <connect from="b" to="a" from_attr="fail"/>
          -->
        </pipeline>

        '''

        pipeline, processes = my.get_pipeline(pipeline_xml)

        for process in processes.keys():
            a_process = processes.get(process)
            a_process.set_json_value("workflow", {
                'on_complete': '''
                sobject.set_value('%s', "complete")
                ''' % process,
                'on_revise': '''
                sobject.set_value('%s', "revise")
                ''' % process
            } )
            a_process.commit()


        process = processes.get("b")
        process.set_json_value("workflow", {
            'on_action': '''
            # ... some code to determine True or False
            return False
            '''
        } )
        process.commit()


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)
        my.assertEquals( "revise", sobject.get_value("a"))


        process = processes.get("b")
        process.set_json_value("workflow", {
            'on_action': '''
            # ... some code to determine True or False
            return True
            ''',
            'on_complete': '''
            sobject.set_value('%s', "complete")
            '''
 
        } )
        process.commit()


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)
        my.assertEquals( "complete", sobject.get_value("a"))
        my.assertEquals( "complete", sobject.get_value("c"))





    def _test_input(my):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")

        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="condition" name="b"/>
          <process type="action" name="c"/>
          <process type="action" name="d"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c" from_attr="success"/>
          <connect from="b" to="d" from_attr="success"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)


        # check input values
        process = processes.get("b")
        process.set_json_value("workflow", {
            'on_action': '''
            inputs = input.get("inputs")
            sobject.set_value("b_input", inputs[0]);
            outputs = input.get("outputs")
            sobject.set_value("b_output", ",".join(outputs))
            sobject.set_value("test", "test")
            '''
        } )
        process.commit()


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)
        # make sure we have the same sobject
        my.assertEquals( "test", sobject.get_value("test") )
        my.assertEquals( "a", sobject.get_value("b_input"))
        my.assertEquals( "c,d", sobject.get_value("b_output"))







    def _test_choice(my):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")
        sobject.set_value("a", False)
        sobject.set_value("b", False)
        sobject.set_value("c", False)
        sobject.set_value("d", False)
        sobject.set_value("e", False)


        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="condition" name="b"/>
          <process type="action" name="c"/>
          <process type="action" name="d"/>
          <process type="action" name="e"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c" from_attr="stream1"/>
          <connect from="b" to="d" from_attr="stream2"/>
          <connect from="b" to="e" from_attr="stream3"/>
        </pipeline>

        '''

        pipeline, processes = my.get_pipeline(pipeline_xml)

        process = processes.get("b")
        process.set_json_value("workflow", {
            'on_action': '''
            # ... some code to determine True or False
            return ['stream1', 'stream3']
            ''',
            'on_complete': '''
            sobject.set_value('b', "complete")
            '''
        } )
        process.commit()


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)

        my.assertEquals( "complete", sobject.get_value("a"))
        my.assertEquals( "complete", sobject.get_value("b"))
        my.assertEquals( "complete", sobject.get_value("c"))
        my.assertEquals( False, sobject.get_value("d"))
        my.assertEquals( "complete", sobject.get_value("e"))



    def _test_manual(my):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")
        sobject.set_value("a", False)
        sobject.set_value("b", False)


        pipeline_xml = '''
        <pipeline>
          <process name="a"/>
          <process type="action" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''

        pipeline, processes = my.get_pipeline(pipeline_xml)

        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)

        # nothing should have run
        my.assertEquals( False, sobject.get_value("a"))
        my.assertEquals( False, sobject.get_value("b"))


    def _test_task(my):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")



        pipeline_xml = '''
        <pipeline>
          <process name="a"/>
          <process type="action" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''

        pipeline, processes = my.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code() )
        sobject.commit()

        for process_name, process in processes.items():
            process.set_json_value("workflow", {
                #'on_in_progress': '''
                #sobject.set_value('name_first', '%s')
                #''' % process_name,
                'on_complete': '''
                sobject.set_value('name_first', '%s')
                ''' % process_name,
            } )
            process.commit()
 

        task = Task.create(sobject, process="a", description="Test Task")

        # TODO: not quite sure if this should be related to "action"
        #task.set_value("status", "in_progress")
        #task.commit()
        #my.assertEquals( "in_progress", sobject.get_value("name_first"))

        task.set_value("status", "complete")
        task.commit()
        my.assertEquals( "b", sobject.get_value("name_first"))



    def _test_trigger(my):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")

        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)

        process = processes.get("a")
        process.set_value("workflow", "")
        process.commit()


        folder = Common.generate_alphanum_key()

        Trigger.clear_db_cache()
        event = "process|action"
        trigger = SearchType.create("config/trigger")
        trigger.set_value("event", event)
        trigger.set_value("process", process.get_code())
        trigger.set_value("mode", "same process,same transaction")
        trigger.set_value("script_path", "%s/process_trigger" % folder)
        trigger.commit()

        script = SearchType.create("config/custom_script")
        script.set_value("folder", folder)
        script.set_value("title", "process_trigger")
        script.set_value("script", '''
        print "---"
        for key, value in input.items():
            print key, value
        print "---"
        print "process: ", input.get("process")
        ''')
        script.commit()
 
        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)



    def _test_approval(my):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")

        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="approval" name="b"/>
          <process type="action" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()

        # ensure there are not tasks
        tasks = Task.get_by_sobject(sobject, process="b")
        my.assertEquals(0, len(tasks))


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)

        # ensure there are not tasks
        tasks = Task.get_by_sobject(sobject, process="b")
        my.assertEquals(1, len(tasks))

        task = tasks[0]
        my.assertEquals("b", task.get("process"))

        # approve the task
        task.set_value("status", "approved")
        task.commit()
        my.assertEquals( "complete", sobject.get_value("b"))
        my.assertEquals( "complete", sobject.get_value("c"))



    def _test_hierarchy(my):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")

        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="hierarchy" name="b"/>
          <process type="action" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)
        parent_process = processes.get("b")

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()

        # create the sub pipeline
        subpipeline_xml = '''
        <pipeline>
          <process type="action" name="suba"/>
          <process type="action" name="subb"/>
          <process type="action" name="subc"/>
          <process type="output" name="end"/>
          <connect from="suba" to="subb"/>
          <connect from="subb" to="subc"/>
          <connect from="subc" to="end"/>
        </pipeline>
        '''
        subpipeline, subprocesses = my.get_pipeline(subpipeline_xml)
        subpipeline.set_value("parent_process", parent_process.get_code())
        subpipeline.commit()
        subpipeline_code = subpipeline.get_code()

        p = processes.get("b")
        p.set_value("subpipeline_code", subpipeline_code)
        p.commit()



        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(my, "process|pending", output)

        my.assertEquals( "complete", sobject.get_value("a"))
        my.assertEquals( "complete", sobject.get_value("b"))
        my.assertEquals( "complete", sobject.get_value("c"))
        my.assertEquals( "complete", sobject.get_value("suba"))
        my.assertEquals( "complete", sobject.get_value("subb"))
        my.assertEquals( "complete", sobject.get_value("subc"))
        my.assertEquals( "complete", sobject.get_value("end"))

        






    def assertEquals(my, a, b):
        if a == b:
            return
        else:
            raise Exception("%s != %s" % (a,b))


def main():
    unittest.main()
    #cmd = WorkflowCmd()
    #Command.execute_cmd(cmd)




if __name__ == '__main__':
    main()





