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

__all__ = ["NotificationTest"]

import tacticenv
import unittest
import time

from pyasm.common import *
from pyasm.security import *
from pyasm.search import Transaction, SearchType, Search
from pyasm.unittest import Person
from pyasm.checkin import FileCheckin

from pyasm.unittest import UnittestEnvironment
from pyasm.biz import Notification, Project, Note, Task
from pyasm.command import Trigger


class NotificationTest(unittest.TestCase):

    def test_all(self):
        
        self.mail_to = Config.get_value("services", "notify_user")

        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()

        test_env = UnittestEnvironment()
        test_env.create()
        self.transaction = Transaction.get(create=True)
        Project.set_project('unittest')
        try:
            self.person = Person.create( "Unit", "Test",
                        "ComputerWorld", "Fake Unittest Person")
            self._test_notification()
            self._test_result()
        finally:
            self.transaction.rollback()
            test_env.delete()



    def _test_notification(self):
        
        
        sobject = SearchType.create("sthpw/notification")
        sobject.set_value('subject', 'TACTIC Unittest 001: a new item has been added.')
        sobject.set_value("event",'insert|unittest/country')
        sobject.set_value("mail_to", self.mail_to)
        sobject.commit()

        sobject = SearchType.create("sthpw/notification")
        sobject.set_value('subject', 'TACTIC Unittest 002: an item has been updated.')
        sobject.set_value("event",'update|unittest/country')
        sobject.set_value("mail_to", self.mail_to)
        sobject.commit()

        sobject = SearchType.create("sthpw/notification")
        sobject.set_value('subject', 'TACTIC Unittest 003: New notes added.')
        sobject.set_value("event",'insert|sthpw/note')
        sobject.set_value("mail_to", self.mail_to)
        sobject.commit()      

        sobject = SearchType.create("sthpw/notification")
        sobject.set_value('subject', 'TACTIC Unittest 004: Task status has been updated.')
        sobject.set_value("event",'update|sthpw/task|status')
        sobject.set_value("mail_to", self.mail_to)
        sobject.commit()

        sobject = SearchType.create("sthpw/notification")
        sobject.set_value('subject', 'TACTIC Unittest 005: Task has been assigned.')
        sobject.set_value("event",'change|sthpw/task|assigned')
        sobject.set_value("mail_to", self.mail_to)
        sobject.commit()

        sobject = SearchType.create("sthpw/notification")
        sobject.set_value('subject', 'TACTIC Unittest 006: Files are checked in.')
        sobject.set_value("event",'checkin|unittest/country')
        sobject.set_value("mail_to", self.mail_to)
        sobject.commit()

        self.clear_notification()
        
        # Item added
        sobject1 = SearchType.create("unittest/country")
        sobject1.set_value('code', 'test_update_trigger')
        sobject1.commit()
        

        # Updated item
        sobject1.set_value('code','success') 
        sobject1.commit()  
        

        # Note added
        Note.create(self.person, "test note2", context='default2')

        # Task assigned
        sobject = Task.create(self.person,'hi','hellotest',assigned="test assigned")

        # Task status changed
        tasks = Task.get_by_sobject(self.person)
        tasks[0].set_value('status','Pending')
        tasks[0].commit()

        # Files are checked in
        file_path = "./notification_test_check.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(sobject1, file_path, "main", context='test', checkin_type='auto')
        checkin.execute()
        import os

        if os.path.exists(file_path):
            os.remove(file_path)
        
        Trigger.call_all_triggers()
    
    def _test_result(self):
        """ 
        Tests that notifications have been created correctly. 
        """


        search = Search('sthpw/notification_log')
        search.add_order_by('timestamp desc')
        search.set_limit(6)
        notes = search.get_sobjects()
        message=[]

        for note in notes:
            temp_value = note.get_value('subject')
            message.append(temp_value)

        self.assertEqual("TACTIC Unittest 006: Files are checked in.", message[0])
        self.assertEqual("TACTIC Unittest 002: an item has been updated.", message[1])
        self.assertEqual("TACTIC Unittest 003: New notes added.", message[2])
        self.assertEqual("TACTIC Unittest 005: Task has been assigned.", message[3])
        self.assertEqual("TACTIC Unittest 004: Task status has been updated.", message[4])
        self.assertEqual("TACTIC Unittest 001: a new item has been added.", message[5])

    def clear_notification(self):
        Notification.clear_cache()
        Container.put("Trigger:notifications", None)
        Container.put("triggers:cache", None)
        Container.put("notifications:cache", None)

if __name__ == '__main__':
    unittest.main()



