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

__all__ = ["CommandTest", "TestTrigger", "TestTaskTrigger", "TestApiHandler", "TestInsertHandler", "SampleCmd","SampleCmd2" ]

import os, shutil

import tacticenv
from pyasm.common import *
from pyasm.biz import Project, Task
from pyasm.search import *
from pyasm.security import *

from command import *
from trigger import *
from pyasm.unittest import UnittestEnvironment

import unittest



class SampleCmdException(Exception):
    pass


class SampleCopyCmd(Command):
    '''copies a file to directory'''

    def __init__(self, from_file, to_file):
        super(SampleCopyCmd,self).__init__()
        self.from_file = from_file
        self.to_file = to_file


    def preprocess(self):
        '''check that everything is ok'''

        # make sure the file exists
        if not os.path.exists(self.from_file):
            raise SampleCmdException("File [%s] does not exist" % self.from_file)

        to_dir = os.path.dirname(self.to_file)
        if not os.path.exists(to_dir):
            raise SampleCmdException("Directory [%s] does not exist" % to_dir)


    def execute(self):
        shutil.copy( self.from_file, self.to_file )


    def rollback(self):
        if os.path.exists(self.to_file):
            os.unlink(self.to_file)


    def get_undo(self):
        return "Test"

    def undo(data):
        print data.get_xml()

        search_type = data.get_value("sobject/@search_type")
        search_id = data.get_value("sobject/@search_id")

        search = Search(search_type)
        search.add_id_filter(search_id)
        sobject = search.get_sobject()

        column = data.get_value("sobject/column/@name")
        value = data.get_value("sobject/column/@value")

        sobject.set_value(column, value)
        sobject.commit()

    undo = staticmethod(undo) 



class SampleCmd(Command):
    '''does nothing'''

    def execute(self):
        Container.put(Trigger.KEY,  None)
        Trigger.call(self, "test_trigger")
        Trigger.call(self, "test_api_handler")

class SampleTaskCmd(Command):
    '''create a task for a person'''

    def execute(self):
        person = SearchType.create('unittest/person')
        person.set_value('name_first', 'john')
        person.commit(triggers=False)
        person2 = SearchType.create('unittest/person')
        person2.set_value('name_first', 'zoe')
        person2.commit(triggers=False)
        task = Task.create(person, "unittest_person", "hello")
        task = Task.create(person2, "unittest_person", "hello")


class TestTrigger(Trigger):

    def execute(self):
        Container.put("TestTrigger", "test_trigger")

        # this ensure non ASCII string can be used in trigger
        server = TacticServerStub.get()
        note = u'\xe2\x80\x9cHELLO"'.encode('utf-8')
        data = {'process': 'unittest', 'context': 'unittest', 'note' : note}
        server.insert('sthpw/note', data)

class TestTaskTrigger(Trigger):

    def execute(self):
       
        Container.put("TestTaskTrigger", "done")

from tactic_client_lib import TacticServerStub
from tactic_client_lib.interpreter import Handler
class TestApiHandler(Handler):

    def execute(self):
        Container.put("TestApiHandler", "test_api_handler")
        
        # test that you can run the client api from here
        server = TacticServerStub.get()
        server.start("Api Trigger test")
        try:
            test = server.ping()
            Container.put("TestApiHandler/ping", test)

            # do some more tests
            search_type = "unittest/person"
            code = "jack"
            search_key = server.build_search_key(search_type, code)

            Container.put("TestApiHandler/search_key", search_key)
            # insert
            data = { 'code': code }
            server.insert(search_type, data)
            # query
            sobject = server.get_by_search_key(search_key)
            Container.put("TestApiHandler/code", sobject.get('code'))

        finally:
            server.abort()



class TestInsertHandler(Handler):
    '''This actually runs on the server'''

    def execute(self):
        # ensure that the protocol is "local"
        server = TacticServerStub.get()
        if server.get_protocol() != "local":
            raise Exception("TacticServerStub protocol is not 'local'")

        # test some inputs
        is_insert = self.get_input_value("is_insert")
        if is_insert != True:
            raise Exception("is_insert != True")

        is_insert = self.get_input_value("is_insert")
        if is_insert != True:
            raise Exception("is_insert != True")

        search_key = self.get_input_value('search_key')
        if search_key != 'unittest/person?project=unittest&code=fred':
            raise Exception("search_key != 'unittest/person?project=unittest&code=fred'")

        prev_data = self.get_input_value('prev_data')
        if prev_data.get('code') != None:
            raise Exception("prev_data['code'] != None")

        prev_data = self.get_input_value('update_data')
        if prev_data.get('code') != 'fred':
            raise Exception("update_data['code'] != 'fred'")

class SampleCmd2(Command):

    def execute(self):
        a = "self custom command description"
        self.add_description(a)
        self.info['extra']= 'some info'
        self.info['processed'] = 10


class CommandTest(unittest.TestCase):

    def setUp(self):
        # intialiaze the framework as a batch process
        batch = Batch()
        Project.set_project("unittest")


    def test_all(self):
        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()

        test_env = UnittestEnvironment()
        test_env.create()


        self._test_command()
        self._test_trigger()
        trigger_key = "triggers:cache"
        Container.put(trigger_key, None)

        try:
            self._test_api_trigger()
            self._test_insert_trigger()

            # test copy project from template
            self._test_copy_project()
            # clear again for subsequent Client API test
            trigger_key = "triggers:cache"

            Container.put(trigger_key, None)
            trigger_key2 = Trigger.KEY
            Container.put(trigger_key2, None)
        finally:
            Project.set_project('unittest')
            test_env.delete()


    def _test_command(self):

        # create a temp file
        tmp_dir = Environment.get_tmp_dir()
        from_path = "%s/test_command.txt" % tmp_dir
        to_path = from_path + ".bak"

        if os.path.exists(from_path):
            os.unlink(from_path)
        if os.path.exists(to_path):
            os.unlink(to_path)

        file = open(from_path, 'w')
        file.write("whatever")
        file.close()

        # start a tranaction for this command
        transaction = Transaction.get(create=True)
        transaction.start()

        # execute the command
        cmd = SampleCopyCmd(from_path, to_path )
        Command.execute_cmd(cmd)

        self.assertEquals( True, os.path.exists(to_path) )

        transaction.rollback()

        # make sure the rollback worked
        self.assertEquals( False, os.path.exists(to_path) )

        os.unlink(from_path)


    def _test_trigger(self):

        # create a db trigger
        transaction = Transaction.get(create=True)
        try:
            trigger_sobj = SearchType.create("sthpw/trigger")
            trigger_sobj.set_value("event", "test_trigger")
            trigger_sobj.set_value("class_name", "pyasm.command.command_test.TestTrigger")
            trigger_sobj.set_value("description", "Unittest Test Trigger")
            trigger_sobj.commit()

            trigger_sobj = SearchType.create("sthpw/trigger")
            trigger_sobj.set_value("event", "insert|sthpw/task")
            trigger_sobj.set_value("class_name", "pyasm.command.command_test.TestTaskTrigger")
            trigger_sobj.set_value("description", "Unittest Test Task Trigger")
            trigger_sobj.set_value("mode", "same process,same transaction")
            trigger_sobj.commit()

            trigger_sobj = SearchType.create("sthpw/notification")
            trigger_sobj.set_value("event", "insert|sthpw/task")
            trigger_sobj.set_value("search_type", "unittest/person")
            trigger_sobj.set_value("subject", "Sub: Unittest a task is created for {@GET(parent.name_first)}")
            trigger_sobj.set_value("message", "Unittest a task is created. {@GET(.code)}")
            trigger_sobj.set_value("mail_to", "support@southpawtech.com")
            trigger_sobj.set_value("description", "Unittest Test Task Notification")
            trigger_sobj.commit()

            Container.put(Trigger.TRIGGER_EVENT_KEY,  None)
            Container.put(Trigger.NOTIFICATION_EVENT_KEY,  None)
            Container.put(Trigger.NOTIFICATION_KEY,  None)

            cmd = SampleCmd()
            Command.execute_cmd(cmd)
            
            cmd = SampleTaskCmd()
            Command.execute_cmd(cmd)

            #print "You should see the message: sending email!!! once"
            # confirm by notification log
            log_msgs = Search.eval("@GET(sthpw/notification_log['subject', 'NEQ', 'Note']['@ORDER_BY', 'timestamp desc']['@LIMIT','4'].subject)")
            self.assertEquals(log_msgs[0] , 'Sub: Unittest a task is created for john')
          
            self.assertEquals(log_msgs[1] , 'Sub: Unittest a task is created for zoe')
            # random check against duplicates

            self.assertEquals(log_msgs[2] != 'Sub: Unittest a task is created for zoe', True)
            value = Container.get("TestTrigger")
            self.assertEquals("test_trigger", value)
            value = Container.get("TestTaskTrigger")
            self.assertEquals("done", value)


        finally:
            transaction = Transaction.get()
            transaction.rollback()



    def _test_api_trigger(self):
        # create a db trigger

        transaction = Transaction.get(create=True)
        try:
            trigger_sobj = SearchType.create("sthpw/trigger")
            trigger_sobj.set_value("event", "test_api_handler")
            trigger_sobj.set_value("class_name", "pyasm.command.command_test.TestApiHandler")
            trigger_sobj.set_value("description", "Unittest Test Api Handler")
            trigger_sobj.commit()

            Container.put(Trigger.TRIGGER_EVENT_KEY,  None)
            Container.put(Trigger.NOTIFICATION_EVENT_KEY,  None)

            cmd = SampleCmd()
            Command.execute_cmd(cmd)

            # test that the api handler was executed
            value = Container.get("TestApiHandler")
            self.assertEquals("test_api_handler", value)

            # test that ping test worked
            value = Container.get("TestApiHandler/ping")
            self.assertEquals("OK", value)

            # test that search_key worked
            value = Container.get("TestApiHandler/search_key")
            self.assertEquals("unittest/person?project=unittest&code=jack", value)

            # test that insert/query worked
            value = Container.get("TestApiHandler/code")
            self.assertEquals("jack", value)

        finally:
            #transaction = Transaction.get()
            transaction.rollback()
            print "Ensure the unittest trigger is removed"


    def _test_insert_trigger(self):



        # create a db trigger
        sobject = Search.eval("@SOBJECT(sthpw/trigger['event','insert|unittest/person'])", single=True)
        if sobject:
            raise Exception('Please delete the insert|unittest/person trigger in sthpw first')
        trigger_sobj = SearchType.create("sthpw/trigger")
        trigger_sobj.set_value("event", "insert|unittest/person")
        trigger_sobj.set_value("class_name", "pyasm.command.command_test.TestInsertHandler")
        trigger_sobj.set_value("description", "Unittest Test Api Handler")
        trigger_sobj.commit()


        search = Search("sthpw/trigger")
        count = search.get_count()

        # use the client api to insert that trigger
        server = TacticServerStub(protocol='xmlrpc')

        server.start("insert trigger test")
        try:
            # create a new person
            search_type = "unittest/person"
            code = "fred"
            search_key = server.build_search_key(search_type, code)

            Container.put("TestApiHandler/search_key", search_key)
            # insert
            data = { 'code': code }

            # insert test: if the trigger fails then an exception should be
            # raised ...?
            server.insert(search_type, data)
        finally:
            server.abort()

        trigger_sobj.delete()

        search = Search('sthpw/trigger')
        search.add_filter('event', 'insert|unittest/person')
        trig = search.get_sobject()
        self.assertEquals(trig, None)


    def _test_copy_project(self):

        #transaction = Transaction.get(create=True)
        try:
            os.system('dropdb -U postgres "game_copy"')
            from tactic.command import ProjectTemplateInstallerCmd
            cmd =  ProjectTemplateInstallerCmd(project_code='game_copy', template_code='game', mode='copy')
            cmd.execute()
        

            schema_entry = Search.eval("@GET(sthpw/schema['code','game_copy'].code)", single=True)
            self.assertEquals(schema_entry, 'game_copy')
            project_entry = Search.eval("@GET(sthpw/project['code','game_copy'].code)", single=True)
            self.assertEquals(project_entry, 'game_copy')
            Project.set_project('game_copy')

            widget_config_st = Search.eval("@GET(config/widget_config['code','1GAME'].search_type)", single=True) 
            self.assertEquals(widget_config_st, 'game/ticket')

            widget_config_counts = Search.eval("@COUNT(config/widget_config)") 
            self.assertEquals(widget_config_counts, 133)
            Project.set_project('unittest')
        finally:
            
            sql = DbContainer.get('sthpw')
            sql.do_update("delete from project where code ='game_copy'")
            sql.do_update("delete from schema where code ='game_copy'")
            sql.commit()
            
            DbContainer.close_all()
            os.system('dropdb -U postgres "game_copy"')
            #transaction = Transaction.get()
            #transaction.rollback()





if __name__ == "__main__":
    unittest.main()
   

