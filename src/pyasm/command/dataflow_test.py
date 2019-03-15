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




from pyasm.biz import Pipeline


class Dataflow(object):


    def __init__(self, **kwargs):
        self.kwargs = kwargs


    def get_state_key(self, sobject, process):
        key = "%s|%s|state" % (sobject.get_search_key(), process)
        return key


    def get_input_state(self, sobject, process):

        pipeline = Pipeline.get_by_sobject(sobject)

        # use the first input process
        input_processes = pipeline.get_input_processes(process)
        if not input_processes:
            return {}

        # get the first process for now
        p = input_processes[0]

        process_name = p.get_name()

        key = self.get_state_key(sobject, process_name)

        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()

        from pyasm.common import jsonloads
        message = server.get_message(key)
        message = message.get("message")
        if not message:
            state = {}
        else:
            state = jsonloads(message)

        return state



    def get_input_path(self, sobject, process):
        '''Assumes a single input path'''

        state = self.get_input_state(sobject, process)
        if not state:
            return ""

        path = state.get("path")
        return path


    def get_output_path(self, sobject, process):
        pass








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
            #self._test_file()
            #self._test_checkin()
            #self._test_context_output()
            self._test_status_message()
            """
            self._test_snapshot_package()
            self._test_approval_state()
            self._test_manual_state()
            """
        except Exception, e:
            print("Error: ", e)
            raise


    def get_pipeline(self, pipeline_xml, add_tasks=False):

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




    def setup(self):

        # create a dummy sobject
        sobject = SearchType.create("unittest/city")
        sobject.commit()

        # check in a file to the city
        file_path = "./test.txt"
        file = open(file_path, 'w')
        file.write("test test test")
        file.close()

        file_paths = [file_path]
        file_types = ['main']
        context = "publish"
        from pyasm.checkin import FileCheckin
        checkin = FileCheckin(
                    sobject,
                    file_paths=file_paths,
                    file_types=file_types,
                    context="test",
                    mode="move"
            )
        checkin.execute()

        return sobject



    def _test_file(self):

        # create a dummy sobject
        sobject = self.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="auto" name="a"/>
          <process type="auto" name="b"/>
          <process type="auto" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()


        process = processes.get("a")
        process.set_json_value("workflow", {
            'output': {
                'type': 'file',
                'path': '/tmp/whatever2.txt',
            },
            'on_action': r'''
            print("a")
            data = input.get("data")
            path = data.get("path")
            print("path: ", path)

            '''
        } )
        process.commit()


        process = processes.get("b")
        process.set_json_value("workflow", {
            'output': {
                'type': 'file',
                'path': '/tmp/whatever3.txt',
            },
            'on_action': r'''
            print("b")
            data = input.get("data")
            path = data.get("path")
            print("path: ", path)

            self.output = {
                'type': 'file',
                'path': '/tmp/whatever3.txt',
            }

            '''
        } )
        process.commit()

        process = processes.get("c")
        process.set_json_value("workflow", {
            'on_action': r'''
            print("c")
            data = input.get("data")
            path = data.get("path")
            print("path: ", path)

            '''
        } )
        process.commit()


 



        data = {
            "type": "file",
            "path": "/tmp/whatever1.txt"
        }

        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
            "data": data
        }

        import time
        start = time.time()
        Trigger.call(self, "process|pending", output)
        print(time.time() - start)





    def _test_checkin(self):

        # create a dummy sobject
        jobject = self.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="auto" name="a"/>
          <process type="auto" name="b"/>
          <process type="auto" name="c"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()


        # the process checks into the "test" context and outputs this context
        process = processes.get("a")
        process.set_json_value("workflow", {
            'output': {
                'context': 'test',
            },
            'on_action': r'''
            data = input.get("data")
            path = data.get("path")
            f = open(path, 'a')
            f.write("OMG\n")
            f.close()

            sobject = input.get("sobject")
            search_key = sobject.get("__search_key__")
            print("a: ")
            print

            server.simple_checkin(search_key, "test", path, mode="move")
            '''
        } )
        process.commit()


        # the process takes the path from the previous process
        process = processes.get("b")
        process.set_json_value("workflow", {
            'output': {
                'context': 'test2',
            },
            'on_action': r'''
            data = input.get("data")
            path = data.get("path")

            print("path: ", path0

            f = open(path, "r")
            content = f.read()
            f.close()

            output_path = "/tmp/whatever2.txt"
            f = open(output_path, 'w')
            f.write(content)
            f.write("\n")
            f.write(content)
            f.write("\n")
            f.close()

            print("b: ")
            sobject = input.get("sobject")
            search_key = sobject.get("__search_key__")
            print


            server.simple_checkin(search_key, "test2", output_path, mode="move")
            '''
        } )
        process.commit()


        process = processes.get("c")
        process.set_json_value("workflow", {
            'on_action': r'''
            data = input.get("data")
            path = data.get("path")
            print
            print("path: ", path)
            print
            assert(path)
            '''
        } )
        process.commit()



        # inital data to the input
        data = {
            'snapshot': 'sthpw/snapshot?project=xyz&code=SNAPSHOT0044',
            'path': '/tmp/whatever.txt'
        }



        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
            "data": data
        }
        Trigger.call(self, "process|pending", output)


    def _test_context_output(self):

        # create a dummy sobject
        sobject = self.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="auto" name="a"/>
          <process type="manual" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()



        process = processes.get("a")
        process.set_json_value("workflow", {
            'output': {
                'context': 'test,test2',
            },
            'on_action': r'''

            path = "/tmp/test.txt"
            f = open(path, 'w')
            f.write("OMG\n")
            f.close()

            path2 = "/tmp/test2.txt"
            f = open(path2, 'w')
            f.write("OMG2\n")
            f.close()



            sobject = input.get("sobject")
            search_key = sobject.get("__search_key__")
            server.simple_checkin(search_key, "test", path, mode="move")
            server.simple_checkin(search_key, "test2", path2, mode="move")

            '''
        } )
        process.commit()



        # create a task for b
        task = Task.create(sobject, process="b")


        # Run the pipeline, this will stop at b
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
        }
        Trigger.call(self, "process|pending", output)


        # use data flow to get the input path.  Basically, this states
        # "get me whatever self input is delivering"
        dataflow = Dataflow()
        path = dataflow.get_input_path(sobject, "b")

        print("path: ", path)

        task.set_value("status", "complete")
        task.commit()


    def _test_snapshot_package(self):

        # create a dummy sobject
        sobject = self.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="action" name="b"/>
          <process type="approval" name="c"/>
          <process type="approval" name="d"/>
          <process type="action" name="e"/>
          <connect from="a" to="b"/>
          <connect from="b" to="c"/>
          <connect from="c" to="d"/>
          <connect from="d" to="e"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()


        # first process will check in 2 files
        process = processes.get("a")
        process.set_json_value("workflow", {
            'on_action': r'''

            path = "/tmp/test.txt"
            f = open(path, 'w')
            f.write("OMG\n")
            f.close()

            path2 = "/tmp/test2.txt"
            f = open(path2, 'w')
            f.write("OMG2\n")
            f.close()

            sobject = input.get("sobject")
            search_key = sobject.get("__search_key__")
            snapshot1 = server.simple_checkin(search_key, "test", path, mode="move")
            snapshot2 = server.simple_checkin(search_key, "test2", path2, mode="move")

            snapshot_codes = [snapshot1.get("code"), snapshot2.get("code")]

            # set the output packages based on the checkins
            output['packages'] = {
                'default': {
                    'type': 'snapshot',
                    'snapshot_codes': snapshot_codes
                }

            }

            '''
        } )
        process.commit()


        # second process checks the package
        process = processes.get("b")
        process.set_json_value("workflow", {
            'on_action': r'''
            '''
        } )
        process.commit()


        # create a task for b
        Task.create(sobject, process="c")
        Task.create(sobject, process="d")


        # second process checks the package
        process = processes.get("e")
        process.set_json_value("workflow", {
            'on_action': r'''

            print("---")
            print(input)

            # receive the packages
            packages = input.get("packages")

            package = packages.get("default") or {}
            if package:
                package_type = package.get("type")
                sobject.set_value('snapshot_codes', ",".join(package.get("snapshot_codes")))
            else:
                sobject.set_value('snapshot_codes', "No package found")


            '''
        } )
        process.commit()



        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
        }

        Trigger.call(self, "process|pending", output)

        # the pipeline will stop at the manual task, so we set the task to complete
        # which will continue the workflow
        task = Task.get_by_sobject(sobject, process="c")[0]
        task.set_value("status", "Complete")
        task.commit()


        # the pipeline will stop at the manual task, so we set the task to complete
        # which will continue the workflow
        task = Task.get_by_sobject(sobject, process="d")[0]
        task.set_value("status", "Complete")
        task.commit()

        #print("snapshot_codes: ", sobject.get_value("snapshot_codes", no_exception=True))




    def _test_approval_state(self):
        '''ensure the the state goes through an approval'''

        # create a dummy sobject
        sobject = self.setup()

        # create a pipeline
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

        # first process will check in 1 files
        process = processes.get("a")
        process.set_json_value("workflow", {
            'on_action': r'''
            path = "/tmp/test.txt"
            f = open(path, 'w')
            f.write("OMG\n")
            f.close()

            search_key = sobject.get_search_key()
            snapshot = server.simple_checkin(search_key, "test", path, mode="move")
            snapshot_codes = [snapshot.get("code")]

            sobject.set_value("a_snapshot_code", snapshot_codes[0])
 
            # set the output packages based on the checkins
            output['packages'] = {
                'default': {
                    'type': 'snapshot',
                    'snapshot_codes': snapshot_codes
                }

            }

            '''
        } )
        process.commit()


        task = Task.create(sobject, process="b")

        # last process checks package
        process = processes.get("c")
        process.set_json_value("workflow", {
            'on_action': r'''
            default = input.get("packages").get("default")
            snapshot_codes = default.get("snapshot_codes")
            if snapshot_codes:
                sobject.set_value("c_snapshot_code", snapshot_codes[0] )
            else:
                sobject.set_value("c_snapshot_code", "")

            '''
        } )
        process.commit()





        # Run the pipeline
        process = "a"
        input = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
        }

        import time
        start = time.time()
        Trigger.call(self, "process|pending", input)

        task.set_value("status", "Complete")
        task.commit()

        print("time: ", time.time() - start)

        self.assertEquals( sobject.get("a_snapshot_code"), sobject.get("c_snapshot_code") )





    def _test_manual_state(self):
        '''ensure the the state goes through an approval'''

        # create a dummy sobject
        sobject = self.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="action" name="a"/>
          <process type="manual" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()

        # first process will check in 1 files
        process = processes.get("a")
        process.set_json_value("workflow", {
            'on_action': r'''
            path = "/tmp/test.txt"
            f = open(path, 'w')
            f.write("OMG\n")
            f.close()

            search_key = sobject.get_search_key()
            snapshot = server.simple_checkin(search_key, "test", path, mode="move")
            snapshot_codes = [snapshot.get("code")]

            sobject.set_value("a_snapshot_code", snapshot_codes[0])
 
            # set the output packages based on the checkins
            output['packages'] = {
                'default': {
                    'type': 'snapshot',
                    'snapshot_codes': snapshot_codes
                }

            }

            '''
        } )
        process.commit()


        task = Task.create(sobject, process="b")

        # Run the pipeline
        a_process = "a"
        input = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": a_process,
        }

        import time
        start = time.time()
        Trigger.call(self, "process|pending", input)


        # query state of the task
        key = "%s|%s|state" % (task.get_search_key(), process.get_value("process"))
        print("key: ", key)
        message = Search.get_by_code("sthpw/message", key).get_json_value("message")

        print("key: ", key)
        print("message: ", message)



    def assertEquals(self, a, b):
        if a == b:
            return
        else:
            raise Exception("%s != %s" % (a,b))



    def _test_status_message(self):
        '''test for messaging information from node to another'''

        # create a dummy sobject
        sobject = self.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="auto" name="start"/>
          <process type="auto" name="test"/>
          <process type="manual" name="a"/>
          <process type="manual" name="b"/>
          <process type="manual" name="c"/>
          <process type="manual" name="d"/>
          <process type="manual" name="e"/>
          <process type="manual" name="f"/>
          <connect from="start" to="a"/>
          <connect from="start" to="test"/>
          <connect from="a" to="b"/>
          <connect from="b" to="e"/>
          <connect from="c" to="d"/>
          <connect from="d" to="e"/>
        </pipeline>
        '''
        pipeline, processes = self.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()

        task_a = Task.create(sobject, process="a")
        task_b = Task.create(sobject, process="b")
        task_c = Task.create(sobject, process="c")
        task_d = Task.create(sobject, process="d")
        task_e = Task.create(sobject, process="e")


        # second process checks the package
        process = processes.get("test")
        process.set_json_value("workflow", {
            'on_action': r'''

            # receive the packages
            packages = input.get("packages")
            print "packages: ", packages

            '''
        } )
        process.commit()



        packages = {
            "status": { "type": "status", "status": "Not Required", "scope": "stream" },
        }

        # Run the pipeline
        a_process = "start"
        input = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": a_process,
            "packages": packages,
        }
        Trigger.call(self, "process|complete", input)

        #task_a.set_value("status", "Not Required")
        #task_a.commit()

        #task_b.set_value("status", "Not Required")
        #task_b.commit()

        tasks = Task.get_by_sobject(sobject)
        for task in tasks:
            print("task: ", task.get("process"), task.get("status"))
            if task.get("process") == "a":
                self.assertEquals( task.get("status"), "Not Required")
            if task.get("process") == "b":
                self.assertEquals( task.get("status"), "Not Required")



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





