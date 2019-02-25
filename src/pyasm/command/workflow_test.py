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

import unittest, random, os

from pyasm.common import Common
from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment
from pyasm.search import Search, SearchType
from pyasm.biz import Task
from pyasm.command import Command, Trigger

from workflow import Workflow

from pyasm.security import Batch



class WorkflowTest(unittest.TestCase):

    def test_all(self):
        Batch()
        from pyasm.web.web_init import WebInit

        test_env = UnittestEnvironment()
        test_env.create()

        try:
            self._test_complete_trigger()
        finally:
            test_env.delete()

            search = Search("sthpw/pipeline")
            search.add_filter("project_code", "unittest")
            pipelines = search.get_sobjects()
            for pipeline in pipelines:
                pipeline.delete()
 
            search = Search("sthpw/message")
            search.add_filter("project_code", "unittest")
            sobjects = search.get_sobjects()
            for sobject in sobjects:
                sobject.delete()

           
 
 
    def _test_complete_trigger(self):
        cmd = WorkflowCmd()
        Command.execute_cmd(cmd)


class WorkflowCmd(Command):
    def execute(self):

        #from pyasm.security import Site
        #from pyasm.biz import Project
        #print("site: " ,Site.get_site())
        #print("project: ", Project.get().get_data())

        try:
            Workflow().init()
            self._test_multi_task()



            self._test_multi_input_reject()
            self._test_progress()
            #self._test_progress_reject()
            self._test_multi_input()
            self._test_multi_input_complete()
            self._test_custom_status()
            self._test_messaging()
            self._test_hierarchy()
            self._test_js()
            self._test_manual()
            self._test_check()
            self._test_task()
            self._test_action_process()
            self._test_choice()
            self._test_input()
            self._test_trigger()
            self._test_approval()
            self._test_dependency()
        except Exception, e:
            print("Error: ", e)
            raise


    def get_pipeline(self, pipeline_xml, add_tasks=False, search_type=None):

        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_pipeline(pipeline_xml)
        pipeline_id = random.randint(0, 10000000)
        #pipeline.set_value("code", "test%s" % pipeline_id)
        #pipeline.set_id(pipeline_id)
        #pipeline.set_value("id", pipeline_id)
        pipeline.set_value("pipeline", pipeline_xml)
        if search_type:
            pipeline.set_value("search_type", search_type)
        pipeline.commit()

        # clear the cache
        from pyasm.common import Container
        Container.put("process_listeners", None)

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
                'on_pending': '''
                sobject.set_value('%s', "pending")
                ''' % process_name,
                'on_complete': '''
                sobject.set_value('%s', "complete")
                ''' % process_name,
                'on_approved': '''
                sobject.set_value('%s', "approved")
                ''' % process_name,
                'on_revise': '''
                sobject.set_value('%s', "revise")
                ''' % process_name,
                'on_reject': '''
                sobject.set_value('%s', "reject")
                ''' % process_name,
                'on_custom': '''
                sobject.set_value('%s', input.get("status"))
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



    def _test_js(self):
        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")

        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

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
            "process": process,
            "status": "pending"
        }

        import time
        start = time.time()
        Trigger.call(self, "process|pending", output)
        #self.assertEquals( "complete", sobject.get_value("a"))




    def _test_action_process(self):

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
        pipeline, processes = self.get_pipeline(pipeline_xml)


        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
            "status": "pending"
        }

        import time
        start = time.time()
        Trigger.call(self, "process|pending", output)
        #print("time: ", time.time() - start)
        self.assertEquals( "complete", sobject.get_value("a"))
        self.assertEquals( "complete", sobject.get_value("b"))
        self.assertEquals( "complete", sobject.get_value("c"))
        self.assertEquals( "complete", sobject.get_value("d"))

        # TODO: this got called twice ... not what we want : fix later
        self.assertEquals( "complete", sobject.get_value("e"))



    def _test_check(self):

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

        pipeline, processes = self.get_pipeline(pipeline_xml)

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
        Trigger.call(self, "process|pending", output)
        self.assertEquals( "revise", sobject.get_value("a"))


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
        Trigger.call(self, "process|pending", output)
        self.assertEquals( "complete", sobject.get_value("a"))
        self.assertEquals( "complete", sobject.get_value("c"))





    def _test_input(self):

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
        pipeline, processes = self.get_pipeline(pipeline_xml)


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
        Trigger.call(self, "process|pending", output)
        # make sure we have the same sobject
        self.assertEquals( "test", sobject.get_value("test") )
        self.assertEquals( "a", sobject.get_value("b_input"))
        self.assertEquals( "c,d", sobject.get_value("b_output"))




    def _test_multi_input(self):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        code = "test%s" % Common.generate_alphanum_key()
        sobject.set_value("code", code)



        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="action" name="b1"/>
          <process type="action" name="b2"/>
          <process type="action" name="b3"/>
          <process type="action" name="b4"/>
          <process type="action" name="c"/>
          <process type="action" name="d"/>
          <connect from="a" to="b1"/>
          <connect from="a" to="b2"/>
          <connect from="a" to="b3"/>
          <connect from="a" to="b4"/>
          <connect from="b1" to="c"/>
          <connect from="b2" to="c"/>
          <connect from="b3" to="c"/>
          <connect from="b4" to="c"/>
          <connect from="c" to="d"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)


        process = processes.get("c")
        process.commit()

        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|pending", output)
       
        self.assertEquals( "complete", sobject.get_value("a"))
        self.assertEquals( "complete", sobject.get_value("b1"))
        self.assertEquals( "complete", sobject.get_value("b2"))
        self.assertEquals( "complete", sobject.get_value("b3"))
        self.assertEquals( "complete", sobject.get_value("b4"))
        self.assertEquals( "complete", sobject.get_value("c"))
        self.assertEquals( "complete", sobject.get_value("d"))




    def _test_multi_input_complete(self):

        # DISABLE until check_inputs is called
        return

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        code = "test%s" % Common.generate_alphanum_key()
        sobject.set_value("code", code)



        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="manual" name="b1"/>
          <process type="manual" name="b2"/>
          <process type="manual" name="b3"/>
          <process type="action" name="c"/>
          <connect from="a" to="b1"/>
          <connect from="a" to="b2"/>
          <connect from="a" to="b3"/>
          <connect from="a" to="b4"/>
          <connect from="b1" to="c"/>
          <connect from="b2" to="c"/>
          <connect from="b3" to="c"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)


        process = processes.get("c")
        process.commit()

        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|pending", output)


        # Run the pipeline
        process = "b1"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|complete", output)

       
        self.assertEquals( "complete", sobject.get_value("a"))
        self.assertEquals( "complete", sobject.get_value("b1"))
        self.assertEquals( "pending", sobject.get_value("b2"))
        self.assertEquals( "pending", sobject.get_value("b3"))

        # THIS WILL FAIL until we implement this correctly
        self.assertEquals( "pending", sobject.get_value("c"))






    def _test_multi_input_reject(self):

        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        code = "test%s" % Common.generate_alphanum_key()
        sobject.set_value("code", code)
        sobject.set_value("a1", "complete")
        sobject.set_value("a2", "complete")
        sobject.set_value("a3", "complete")
        sobject.set_value("b", "pending")

        # simple condition
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a1"/>
          <process type="action" name="a2"/>
          <process type="action" name="a3"/>
          <process type="approval" name="b"/>
          <connect from="a1" to="b"/>
          <connect from="a2" to="b"/>
          <connect from="a3" to="b"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)


        # Run the pipeline
        process = "b"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
            "reject_process": ['a1', 'a3']
        }
        Trigger.call(self, "process|reject", output)

        self.assertEquals( "revise", sobject.get_value("a1"))
        self.assertEquals( "complete", sobject.get_value("a2"))
        self.assertEquals( "revise", sobject.get_value("a3"))




    def _test_choice(self):

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

        pipeline, processes = self.get_pipeline(pipeline_xml)

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
        Trigger.call(self, "process|pending", output)

        self.assertEquals( "complete", sobject.get_value("a"))
        self.assertEquals( "complete", sobject.get_value("b"))
        self.assertEquals( "complete", sobject.get_value("c"))
        self.assertEquals( False, sobject.get_value("d"))
        self.assertEquals( "complete", sobject.get_value("e"))



    def _test_manual(self):

        print("test manual")

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

        pipeline, processes = self.get_pipeline(pipeline_xml)

        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|pending", output)

        # nothing should have run
        self.assertEquals( "pending", sobject.get_value("a"))
        self.assertEquals( False, sobject.get_value("b"))


    def _test_task(self):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")



        pipeline_xml = '''
        <pipeline>
          <process name="a"/>
          <process type="action" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''

        pipeline, processes = self.get_pipeline(pipeline_xml)

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
        #self.assertEquals( "in_progress", sobject.get_value("name_first"))

        task.set_value("status", "complete")
        task.commit()
        self.assertEquals( "b", sobject.get_value("name_first"))




    def _test_multi_task(self):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")

        pipeline_xml = '''
        <pipeline>
          <process name="a"/>
          <process type="action" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''

        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code() )
        sobject.commit()

        for process_name, process in processes.items():
            process.set_json_value("workflow", {
                'on_complete': '''
                sobject.set_value('name_first', '%s')
                ''' % process_name,
            } )
            process.commit()
 

        task = Task.create(sobject, process="a", description="Test Task")
        task2 = Task.create(sobject, process="a", description="Test Task 2")

        task.set_value("status", "complete")
        task.commit()
        self.assertEquals( False, "b" == sobject.get_value("name_first"))

        task2.set_value("status", "complete")
        task2.commit()
        self.assertEquals( True, "b" == sobject.get_value("name_first"))









    def _test_trigger(self):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")

        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

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
        print("---")
        for key, value in input.items():
            print(key, value)
        print("---")
        print("process: ", input.get("process"))
        ''')
        script.commit()
 
        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|pending", output)



    def _test_approval(self):

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
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()

        # ensure there are not tasks
        tasks = Task.get_by_sobject(sobject, process="b")
        self.assertEquals(0, len(tasks))


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|pending", output)

        # ensure there are not tasks
        tasks = Task.get_by_sobject(sobject, process="b")
        self.assertEquals(1, len(tasks))

        task = tasks[0]
        self.assertEquals("b", task.get("process"))

        # approve the task
        task.set_value("status", "approved")
        task.commit()
        self.assertEquals( "complete", sobject.get_value("b"))
        self.assertEquals( "complete", sobject.get_value("c"))



    def _test_hierarchy(self):

        # create a dummy sobject
        sobject = SearchType.create("unittest/person")

        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="hierarchy" name="b"/>
          <process type="hierarchy" name="c"/>
          <process type="action" name="d"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
          <connect from="c" to="d"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)


        # create the sub pipeline
        subpipeline_xml = '''
        <pipeline>
          <process type="input" name="start"/>
          <process type="action" name="suba"/>
          <process type="action" name="subb"/>
          <process type="action" name="subc"/>
          <process type="output" name="end"/>
          <connect from="start" to="suba"/>
          <connect from="suba" to="subb"/>
          <connect from="subb" to="subc"/>
          <connect from="subc" to="end"/>
        </pipeline>
        '''
        subpipeline, subprocesses = self.get_pipeline(subpipeline_xml)
        #subpipeline.set_value("parent_process", parent_process.get_code())
        subpipeline.commit()
        subpipeline_code = subpipeline.get_code()

        p = processes.get("b")
        p.set_value("subpipeline_code", subpipeline_code)
        p.commit()

        p = processes.get("c")
        p.set_value("subpipeline_code", subpipeline_code)
        p.commit()



        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process
        }
        Trigger.call(self, "process|pending", output)

        self.assertEquals( "complete", sobject.get_value("a"))
        self.assertEquals( "complete", sobject.get_value("b"))
        self.assertEquals( "complete", sobject.get_value("c"))
        self.assertEquals( "complete", sobject.get_value("start"))
        self.assertEquals( "complete", sobject.get_value("suba"))
        self.assertEquals( "complete", sobject.get_value("subb"))
        self.assertEquals( "complete", sobject.get_value("subc"))
        self.assertEquals( "complete", sobject.get_value("end"))

        


    def _test_dependency(self):

        # Diabled in this version
        #return

        # create a dummy sobject
        city = SearchType.create("unittest/city")


        city_pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="dependency" name="b" search_type="unittest/person" process="x" status="pending"/>
          <process type="action" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        city_pipeline, city_processes = self.get_pipeline(city_pipeline_xml)

        city.set_value("pipeline_code", city_pipeline.get_code())
        city.commit()



        people = []

        person_pipeline_xml = '''
        <pipeline>
          <process type="action" name="x"/>
          <process type="action" name="y"/>
          <process type="dependency" name="z" search_type="unittest/city" process="b" status="complete"/>
          <connect from="x" to="y"/>
          <connect from="y" to="z"/>
        </pipeline>
        '''
        person_pipeline, person_processes = self.get_pipeline(person_pipeline_xml)

        for name in ['Beth', 'Cindy', 'John','Amy','Jack','Steve','Karen']:
            person = SearchType.create("unittest/person")
            person.set_value("name_first", name)
            person.set_value("pipeline_code", person_pipeline.get_code())
            person.set_value("city_code", city.get_code())
            person.commit()

            person.set_value("x", "null")
            person.set_value("y", "null")
            person.set_value("z", "null")

            people.append(person)



        # Run the pipeline
        process = "a"
        output = {
            "pipeline": city_pipeline,
            "sobject": city,
            "process": process
        }
        Trigger.call(self, "process|pending", output)



        #person_task = Task.create(person, process="a", description="Test Task")
        #person_task.set_value("status", "complete")
        #person_task.commit()
        for person in people:
            self.assertEquals( "complete", person.get_value("x") )
            self.assertEquals( "complete", person.get_value("y") )
            self.assertEquals( "complete", person.get_value("z") )

        self.assertEquals( "complete", city.get_value("c") )



    def _test_progress(self):

        # create a dummy sobject
        city = SearchType.create("unittest/city")

        people = []

        person_pipeline_xml = '''
        <pipeline>
          <process type="action" name="p1"/>
          <process type="action" name="p2"/>
          <process type="manual" name="p3"/>
          <connect from="p1" to="p2"/>
          <connect from="p2" to="p3"/>
        </pipeline>
        '''
        person_pipeline, person_processes = self.get_pipeline(person_pipeline_xml, search_type="unittest/person")
        person_pipeline_code = person_pipeline.get_value("code")



        city_pipeline_xml = '''
        <pipeline>
          <process type="action" name="c1"/>
          <process type="progress" name="c2" pipeline_code="%s" search_type="unittest/person" process="p1" status="complete"/>
          <process type="progress" name="c3" search_type="unittest/person" process="p3" status="complete"/>
          <process type="action" name="c4"/>
          <connect from="c1" to="c2"/>
          <connect from="c2" to="c3"/>
          <connect from="c3" to="c4"/>
        </pipeline>
        ''' % person_pipeline_code
        city_pipeline, city_processes = self.get_pipeline(city_pipeline_xml, search_type="unittest/city")

        city.set_value("pipeline_code", city_pipeline.get_code())
        city.commit()

        from pyasm.common import Container
        Container.put("process_listeners", None)

        for name in ['Beth', 'Cindy', 'John']:
            person = SearchType.create("unittest/person")
            person.set_value("name_first", name)
            person.set_value("pipeline_code", person_pipeline.get_code())
            person.set_value("city_code", city.get_code())
            person.commit()

            person.set_value("p1", "null")
            person.set_value("p2", "null")
            person.set_value("p3", "null")

            people.append(person)


        # Run the city pipeline
        process = "c1"
        output = {
            "pipeline": city_pipeline,
            "sobject": city,
            "process": process
        }
        Trigger.call(self, "process|pending", output)


        # it should have stopped at c2
        self.assertEquals( "complete", city.get_value("c1") )
        self.assertEquals( "pending", city.get_value("c2") )

        # run the people pipeline
        for person in people:
            process = "p1"
            output = {
                "pipeline": person_pipeline,
                "sobject": person,
                "process": process
            }

            Trigger.call(self, "process|pending", output)

            #self.assertEquals( "pending", city.get_value("c2") )


        # it should have stopped at p3
        for person in people:
            self.assertEquals( "complete", person.get_value("p1") )
            self.assertEquals( "complete", person.get_value("p2") )
            self.assertEquals( "pending", person.get_value("p3") )


        # however, because p1 is complete, c2 should have finished
        self.assertEquals( "complete", city.get_value("c1") )
        self.assertEquals( "complete", city.get_value("c2") )
        self.assertEquals( "pending", city.get_value("c3") )


        # run the manual p3 for all people
        for person in people:
            process = "p3"
            output = {
                "pipeline": person_pipeline,
                "sobject": person,
                "process": process
            }
            Trigger.call(self, "process|complete", output)

    
        # this should complete c3 and c4
        for person in people:
            self.assertEquals( "complete", person.get_value("p1") )
            self.assertEquals( "complete", person.get_value("p2") )
            self.assertEquals( "complete", person.get_value("p3") )

        """
        TODO: sync the progress node c3 status to match p3. 
        Now, c3 stays as complete once it switches to complete.
        # let's set p3 to revise
        for person in people:
            process = "p3"
            output = {
                "pipeline": person_pipeline,
                "sobject": person,
                "process": process
            }
            Trigger.call(self, "process|revise", output)
        
           

        self.assertEquals( "complete", city.get_value("c1") )
        self.assertEquals( "complete", city.get_value("c2") )
        self.assertEquals( "pending", city.get_value("c3") )


        # run the manual p3 for all people to complete again
        for person in people:
            process = "p3"
            output = {
                "pipeline": person_pipeline,
                "sobject": person,
                "process": process
            }
            Trigger.call(self, "process|complete", output)
        
        """
        self.assertEquals( "complete", city.get_value("c1") )
        self.assertEquals( "complete", city.get_value("c2") )
        self.assertEquals( "complete", city.get_value("c3") )
        self.assertEquals( "complete", city.get_value("c4") )



    def _test_progress_reject(self):

        # FIXME: it is not completely clear what should happen when a progress
        # node recieves a revise message.
        return

        # create a dummy sobject
        city = SearchType.create("unittest/city")

        people = []

        person_pipeline_xml = '''
        <pipeline>
          <process type="action" name="p1"/>
        </pipeline>
        '''
        person_pipeline, person_processes = self.get_pipeline(person_pipeline_xml, search_type="unittest/person")
        person_pipeline_code = person_pipeline.get_value("code")



        city_pipeline_xml = '''
        <pipeline>
          <process type="progress" name="c1" pipeline_code="%s" search_type="unittest/person" process="p1" status="complete"/>
          <process type="approval" name="c2"/>
          <connect from="c1" to="c2"/>
        </pipeline>
        ''' % person_pipeline_code
        city_pipeline, city_processes = self.get_pipeline(city_pipeline_xml, search_type="unittest/city")

        city.set_value("pipeline_code", city_pipeline.get_code())
        city.commit()


        from pyasm.common import Container
        Container.put("process_listeners", None)


        for name in ['Beth', 'Cindy', 'John']:
            person = SearchType.create("unittest/person")
            person.set_value("name_first", name)
            person.set_value("pipeline_code", person_pipeline.get_code())
            person.set_value("city_code", city.get_code())
            person.commit()

            person.set_value("p1", "complete")

            people.append(person)



        process = "c2"
        output = {
            "pipeline": city_pipeline,
            "sobject": city,
            "process": process
        }

        Trigger.call(self, "process|reject", output)

        for person in people:
            self.assertEquals( "revise", person.get_value("p1") )


 


    def _test_messaging(self):

        # create a dummy sobject
        city = SearchType.create("unittest/city")


        city_pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="action" name="b"/>
          <process type="action" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        city_pipeline, city_processes = self.get_pipeline(city_pipeline_xml)

        city.set_value("pipeline_code", city_pipeline.get_code())
        city.commit()

        # Run the pipeline
        process = "a"
        output = {
            "pipeline": city_pipeline,
            "sobject": city,
            "process": process
        }
        Trigger.call(self, "process|pending", output)


        for process in city_processes:
            key = "%s|%s|status" % (city.get_search_key(), process)
            search = Search("sthpw/message")
            search.add_filter("code", key)
            sobject = search.get_sobject()
            message = sobject.get_value("message")
            self.assertEquals("complete", message)



    def _test_custom_status(self):

        task_pipeline_xml = '''
        <pipeline>
          <process name="Pending"/>
          <process name="Do It"/>
          <process name="Fix it" mapping="revise"/>
          <process name="Push Back" mapping="reject"/>
          <process name="Revise"/>
          <process name="Go to Do It" direction="output" status="Do It"/>
          <process name="Accept" mapping="complete"/>
        </pipeline>
        '''
        task_pipeline, task_processes = self.get_pipeline(task_pipeline_xml)
        task_pipeline.set_value("code", "custom_task")
        task_pipeline.commit()



        # create a dummy sobject
        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("code", "test")

        pipeline_xml = '''
        <pipeline>
          <process task_pipeline="custom_task" type="manual" name="a"/>
          <process task_pipeline="custom_task" type="action" name="b"/>
          <process type="action" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())


        # Run the pipeline
        process = "b"
        status = "Push Back"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
            "status": status
        }
        Trigger.call(self, "process|custom", output)

        self.assertEquals("reject", sobject.get_value("b"))
        self.assertEquals("revise", sobject.get_value("a"))



        # Run the pipeline
        process = "a"
        status = "Go to Do It"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
            "status": status
        }
        Trigger.call(self, "process|custom", output)

        self.assertEquals("Do It", sobject.get_value("b"))





    def assertEquals(self, a, b):
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





