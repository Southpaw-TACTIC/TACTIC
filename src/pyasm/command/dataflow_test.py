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


    def __init__(my, **kwargs):
        my.kwargs = kwargs


    def get_state_key(my, sobject, process):
        key = "%s|%s|state" % (sobject.get_search_key(), process)
        return key


    def get_input_state(my, sobject, process):

        pipeline = Pipeline.get_by_sobject(sobject)

        # use the first input process
        input_processes = pipeline.get_input_processes(process)
        if not input_processes:
            return {}

        p = input_processes[0]

        process_name = p.get_name()

        key = my.get_state_key(sobject, process_name)

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



    def get_input_path(my, sobject, process):

        state = my.get_input_state(sobject, process)
        if not state:
            return ""

        path = state.get("path")
        return path








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
 
            search = Search("sthpw/message")
            search.add_filter("project_code", "unittest")
            sobjects = search.get_sobjects()
            for sobject in sobjects:
                sobject.delete()

           
 
 
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
            #my._test_file()
            #my._test_checkin()
            my._test_manual()
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




    def setup(my):

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



    def _test_file(my):

        # create a dummy sobject
        sobject = my.setup()

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
        pipeline, processes = my.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()


        process = processes.get("a")
        process.set_json_value("workflow", {
            'output': {
                'type': 'file',
                'path': '/tmp/whatever2.txt',
            },
            'on_action': r'''
            print "a"
            data = input.get("data")
            path = data.get("path")
            print "path: ", path

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
            print "b"
            data = input.get("data")
            path = data.get("path")
            print "path: ", path

            my.output = {
                'type': 'file',
                'path': '/tmp/whatever3.txt',
            }

            '''
        } )
        process.commit()

        process = processes.get("c")
        process.set_json_value("workflow", {
            'on_action': r'''
            print "c"
            data = input.get("data")
            path = data.get("path")
            print "path: ", path

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
        for i in range(0, 10):
            start = time.time()
            Trigger.call(my, "process|pending", output)
            print time.time() - start





    def _test_checkin(my):

        # create a dummy sobject
        sobject = my.setup()

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
        pipeline, processes = my.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()


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
            print "a: "
            print

            server.simple_checkin(search_key, "test", path, mode="move")
            '''
        } )
        process.commit()


        process = processes.get("b")
        process.set_json_value("workflow", {
            'output': {
                'context': 'test2',
            },
            'on_action': r'''
            data = input.get("data")
            path = data.get("path")

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

            print "b: "
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
            print "path: ", path
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
        Trigger.call(my, "process|pending", output)


    def _test_manual(my):

        # create a dummy sobject
        sobject = my.setup()

        # create a pipeline
        pipeline_xml = '''
        <pipeline>
          <process type="auto" name="a"/>
          <process type="manual" name="b"/>
          <connect from="a" to="b"/>
        </pipeline>
        '''
        pipeline, processes = my.get_pipeline(pipeline_xml)

        sobject.set_value("pipeline_code", pipeline.get_code())
        sobject.commit()




        process = processes.get("a")
        process.set_json_value("workflow", {
            'output': {
                'context': 'test',
            },
            'on_action': r'''

            path = "/tmp/test.txt"
            f = open(path, 'w')
            f.write("OMG\n")
            f.close()

            sobject = input.get("sobject")
            search_key = sobject.get("__search_key__")
            print "running process: a"

            server.simple_checkin(search_key, "test", path, mode="move")



            '''
        } )
        process.commit()



        # create a task for b
        task = Task.create(sobject, process="b")


        dataflow = Dataflow()
        path = dataflow.get_input_path(sobject, "b")
        my.assertEquals("", path)


        # Run the pipeline
        process = "a"
        output = {
            "pipeline": pipeline,
            "sobject": sobject,
            "process": process,
        }
        Trigger.call(my, "process|pending", output)


        dataflow = Dataflow()
        path = dataflow.get_input_path(sobject, "b")
        print "path: ", path


        task.set_value("status", "complete")
        task.commit()


        return






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





