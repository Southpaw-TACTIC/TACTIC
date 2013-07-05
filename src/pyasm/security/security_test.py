#!/usr/bin/env python
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

__all__ = ["SecurityTest"]

import tacticenv

import md5

from pyasm.common import Environment, SecurityException, Xml
from pyasm.search import *
from pyasm.unittest import *
from pyasm.biz import Project

from security import *
from access_manager import *
from batch import *
from crypto_key import *


import unittest

class SecurityTest(unittest.TestCase):

    def _setup(my):

        # intialiaze the framework as a batch process
        batch = Batch()
        security = Environment.get_security()
        from pyasm.biz import Project
        Project.set_project("unittest")
        my.security = Environment.get_security()
        my.user = 'unittest_guy'
        my.password = 'cow'
        my.encrypted = md5.new(my.password).hexdigest()
        my.person = None

        # start a transaction
        my.transaction = Transaction.get(create=True)
        #my.transaction.start()

        # create the user
        login = SObjectFactory.create("sthpw/login")
        login.set_value("login", my.user)
        login.set_value("password", my.encrypted)
        login.set_value("login_groups", "test")
        login.commit()
        
        s = Search('sthpw/login_in_group')
        s.add_filter('login',my.user)
        s.add_filter('login_group', 'user')
        lng = s.get_sobject()
        if lng:
            lng.delete()


        # create the user2
        login = SObjectFactory.create("sthpw/login")
        login.set_value("login", 'unittest_gal')
        login.set_value("password", my.encrypted)
        login.set_value("login_groups", "test")
        login.commit()


        # create the user3 and add to a group
        login = SObjectFactory.create("sthpw/login")
        login.set_value("login", 'unittest_dan')
        login.set_value("password", my.encrypted)
        login.commit()

        login = SObjectFactory.create("sthpw/login_group")
        login.set_value("login_group", 'unittest_med')
        login.commit()

        login = SObjectFactory.create("sthpw/login_group")
        login.set_value("login_group", 'test')
        login.commit()

        l_in_g = SObjectFactory.create("sthpw/login_in_group")
        l_in_g.set_value("login", 'unittest_dan')
        l_in_g.set_value("login_group", 'unittest_med')
        l_in_g.commit()

        l_in_g = SObjectFactory.create("sthpw/login_in_group")
        l_in_g.set_value("login", my.user)
        l_in_g.set_value("login_group", 'test')
        l_in_g.commit()

    def _tear_down(my):
        #transaction = Transaction.get()
        my.transaction.rollback()
        # this is necessary cuz the set_value() was caught in a security exception possibly, needs investigation
        if my.person:
            my.person.delete()


    def test_all(my):

        try:
            my._setup()
            my._test_crypto()

            my._test_security_fail()
            my._test_security_pass()

            my._test_sobject_access_manager()

            my._test_access_manager()
            my._test_search_filter()
            my._test_access_level()
        except Exception, e:
            print "Error: ", e
            raise

        finally:
            my._tear_down()



    def _test_security_fail(my):

        # should fail
        password = 'test'

        fail = False
        try:
            my.security.login_user(my.user,password)
        except SecurityException, e:
            fail = True

        my.assertEquals( True, fail )


    def _test_security_pass(my):

        fail = False
        try:
            my.security.login_user(my.user,my.password)
        except SecurityException, e:
            fail = True

        # set this user as admin
        my.security.set_admin(True)


        my.assertEquals( False, fail )

    def count(my, it):
        from collections import defaultdict
        d = defaultdict(int)
        for j in it:
            d[j] += 1
        return d
    
    def _test_search_filter(my):
        my.security.set_admin(False)

        # exclude sample3d tasks and include unittest tasks only
        rules = """
        <rules>
        <rule value='sample3d' search_type='sthpw/task' column='project_code' op='!=' group='search_filter'/>
        <rule value='unittest' search_type='sthpw/task' column='project_code' group='search_filter'/>
        </rules>
        """

        xml = Xml()
        xml.read_string(rules)
        access_manager = Environment.get_security().get_access_manager()
        access_manager.add_xml_rules(xml)

        search = Search('sthpw/task')
        tasks = search.get_sobjects()
        project_codes = SObject.get_values(tasks,'project_code', unique=True)
        my.assertEquals(False, 'sample3d' in project_codes)
        my.assertEquals(True, 'unittest' in project_codes)

        # test list-based expression
        rules = """
        <rules>
        <rule value='$PROJECT' search_type='sthpw/task' column='project_code' group='search_filter'/>
        <rule value="@GET(sthpw/login['login','EQ','unittest'].login)" search_type='sthpw/task' op='in' column='assigned' group='search_filter' project='*'/>
        </rules>
        """
        xml = Xml()
        xml.read_string(rules)
        # reset it
        Environment.get_security().reset_access_manager()

        access_manager = Environment.get_security().get_access_manager()
        access_manager.add_xml_rules(xml)

        search = Search('sthpw/task')
        tasks = search.get_sobjects()
        # 3 tasks were created above for a person
        my.assertEquals(3, len(tasks))
        assigned_codes = SObject.get_values(tasks,'assigned', unique=True)
        project_codes = SObject.get_values(tasks,'project_code', unique=True)
        my.assertEquals({'unittest_guy': 1,'unittest_gal': 1}, my.count(assigned_codes))
        my.assertEquals(True, ['unittest'] == project_codes)

        rules = """
        <rules>
        <rule group="project" code='sample3d' access='allow'/>
        <rule group="project" code='unittest' access='allow'/>
        <rule group="project" code='art' access='allow'/>
        <rule value='$PROJECT' search_type='sthpw/task' column='project_code' group='search_filter'/>
        <rule value='@GET(login.login)' search_type='sthpw/task' column='assigned' group='search_filter' project='*'/>
        </rules>
        """
        xml = Xml()
        xml.read_string(rules)
        # reset it
        security = Environment.get_security()
        security.reset_access_manager()

        access_manager = security.get_access_manager()
        access_manager.add_xml_rules(xml)

        search = Search('sthpw/task')
        tasks = search.get_sobjects()

        # 2 tasks were created above for unittest_guy
        my.assertEquals(2, len(tasks))
        assigned_codes = SObject.get_values(tasks,'assigned', unique=True)
        project_codes = SObject.get_values(tasks,'project_code', unique=True)
        my.assertEquals(True, ['unittest_guy'] == assigned_codes)
        my.assertEquals(True, ['unittest'] == project_codes)

        Project.set_project('sample3d')
        search = Search('sthpw/task')
        tasks = search.get_sobjects()

        my.assertEquals(1, len(tasks))
        assigned_codes = SObject.get_values(tasks,'assigned', unique=True)
        project_codes = SObject.get_values(tasks,'project_code', unique=True)
        my.assertEquals(True, ['unittest_guy'] == assigned_codes)
        my.assertEquals(True, ['sample3d'] == project_codes)
        
        Project.set_project('unittest')


        # project specific rule
        proj_rules = """
        <rules>
        <rule group="project" code='art' access='allow'/>
        <rule group="project" code='unittest' access='allow'/>
        <rule value='$PROJECT' search_type='sthpw/task' column='project_code' group='search_filter'/>
        <rule value='@GET(login.login)' search_type='sthpw/task' column='assigned' group='search_filter' project='unittest'/>
        </rules>
        """
        xml = Xml()
        xml.read_string(proj_rules)
        # reset it
        Environment.get_security().reset_access_manager()

        access_manager = Environment.get_security().get_access_manager()
        access_manager.add_xml_rules(xml)

        project = Project.get_by_code('art')
        if project:
            Project.set_project('art')
            search = Search('sthpw/task')
            tasks = search.get_sobjects()

            assigned_codes = SObject.get_values(tasks,'assigned', unique=True)
            project_codes = SObject.get_values(tasks,'project_code', unique=True)
            # should fail since project is switched to sample3d.. and it should have more than just unittest
            my.assertEquals(False, ['unittest'] == assigned_codes)
            my.assertEquals(True, ['art'] == project_codes)




            # unittest specific rule that uses negation !=, this takes care of NULL value automatically
            rules = """
            <rules>
                <rule group="project" code='art' access='allow'/>
                <rule value='5' search_type='sthpw/task' column='priority' op='!=' group='search_filter' project='art'/>
            </rules>
            """
            xml = Xml()
            xml.read_string(rules)
            # reset it
            Environment.get_security().reset_access_manager()

            access_manager = Environment.get_security().get_access_manager()
            access_manager.add_xml_rules(xml)

            Project.set_project('art')
            search = Search('sthpw/task')
            tasks = search.get_sobjects()

            priorities = SObject.get_values(tasks,'priority', unique=True)
            #project_codes = SObject.get_values(tasks,'project_code', unique=True)
            
            for p in priorities:
                my.assertEquals(True, p != 5)
      
        try: 
            Project.set_project('unittest')
        except SecurityException, e:
            my.assertEquals('User [unittest_guy] is not permitted to view project [unittest]', e.__str__())
            xml = Xml()
            xml.read_string(proj_rules)
            # reset it
            Environment.get_security().reset_access_manager()


            access_manager = Environment.get_security().get_access_manager()
            access_manager.add_xml_rules(xml)
        except Exception, e:
            print "Error : %s", str(e)
        else:
            access_manager = Environment.get_security().get_access_manager()
            print "Allowed projects in dict form: ", access_manager.groups.get('project')
            raise Exception('unittest_guy should not be allowed to use Project unittest here.')

        # One should be able to insert a task that is outside the query restriction of the above rule
        task = SearchType.create('sthpw/task')
        task.set_sobject_value(my.person)
        task.set_value('assigned', 'made_up_login')
        task.set_value('project_code', 'sample3d')
        task.set_value('description', 'a new task')
        task.set_value('process', 'unittest')
        task.set_value('context', 'unittest')
        task.commit()

        my.assertEquals('made_up_login', task.get_value('assigned'))

    # DEPRECATED: column level security has been disabled for now (for
    # performance reasons)
    def _test_sobject_access_manager(my):
        '''test a more realistic example'''

        # create a test person
        person = Person.create("Donald", "Duck", "DisneyLand", "A duck!!!")
        my.person = person

        for project_code in ['unittest','unittest','sample3d']:
            task = SearchType.create('sthpw/task')
            task.set_sobject_value(person)
            task.set_value('assigned', 'unittest_guy')
            task.set_value('project_code', project_code)
            task.set_value('description', 'do something good')
            task.set_value('process', 'unittest')
            task.set_value('context', 'unittest')
            task.commit()

        # an extra task for list-based search_filter test
        task = SearchType.create('sthpw/task')
        task.set_sobject_value(person)
        task.set_value('assigned', 'unittest_gal')
        task.set_value('project_code', 'unittest')
        task.set_value('description', 'do something good')
        task.set_value('process', 'unittest2')
        task.set_value('context', 'unittest2')
        task.commit()
        # add these rules to the current user
        rules = """
        <rules>
          <rule group="sobject_column" default="edit"/>
          <rule group="sobject_column" search_type="unittest/person" column="name_first" access="edit"/>
          <rule group="sobject_column" search_type="unittest/person" column="name_last" access="deny"/>
          <rule group="sobject_column" search_type="unittest/person" column="nationality" access="deny"/>
        </rules>
        """

        xml = Xml()
        xml.read_string(rules)
        access_manager = Environment.get_security().get_access_manager()
        access_manager.add_xml_rules(xml)

        # disable admin for this test
        access_manager.set_admin(False)


        # should succeed
        person.set_value("name_first", "Donny")
        # should fail
        try:
            person.set_value("name_last", "Ducky")
        except SecurityException, e:
            pass
        else:
            my.fail("Expected a SecurityException")

        # should succeed
        name_last = person.get_value("name_last")
        my.assertEquals("Duck", name_last)

        # should fail
        # DISABLED for now since Search._check_value_security() is commented out
        """
        try:
            nationality = person.get_value("nationality")
        except SecurityException, e:
            pass
        else:
            my.fail("Expected a SecurityException")
        """
        # disable admin for this test
        access_manager.set_admin(True)


    def _test_access_manager(my):

        access_manager = AccessManager()

        xml = Xml()
        xml.read_string('''
        <rules>
          <group type='sobject' default='edit'>
            <rule key='corporate/budget' access='deny'/>
            <rule key='corporate/salary' access='deny'/>
          </group>

          <group type='sobject_column' default='view'>
            <rule key='prod/asset|director_notes' access='deny'/>
            <rule key='prod/asset|sensitive_data' access='deny'/>
          </group>

          <group type='url' default='deny'>
            <rule key='/tactic/bar/Partner' access='view'/>
            <rule key='/tactic/bar/External' access='view'/>
          </group>

            <rule group='sobject' search_type='sthpw/note'  project='sample3d' access='deny'/>
            <rule group='sobject' search_type='prod/layer'  project='sample3d' access='view'/>
            <rule column='description'  search_type='prod/shot' access='view' group='sobject_column'/>
           </rules>
        ''')

        access_manager.add_xml_rules(xml)

        # test sensitive sobject
        test = access_manager.get_access('sobject', 'corporate/budget')
        my.assertEquals(test, "deny")

        # test allowed sobject
        test = access_manager.get_access('sobject', 'prod/asset')
        my.assertEquals(test, "edit")

        test = access_manager.get_access('sobject', 'sthpw/note')
        my.assertEquals(test, "edit")
        # test url
        test = access_manager.get_access('url', '/tactic/bar/Partner')
        my.assertEquals(test, "view")

        # test with access values ... a more typical usage
        test = access_manager.check_access('sobject','prod/asset','view')
        my.assertEquals(test, True)

        test = access_manager.check_access('sobject','corporate/budget','edit')
        my.assertEquals(test, False)

        test = access_manager.check_access('sobject_column', 'prod/asset|director_notes','deny')
        my.assertEquals(test, True)

        test = access_manager.check_access('sobject_column',{'search_type':'prod/shot','column':'description'},'edit')
        my.assertEquals(test, False)

        test = access_manager.check_access('sobject_column',{'search_type':'prod/shot','column':'description'},'view')
        my.assertEquals(test, True)


        test = access_manager.get_access('sobject', 'sthpw/note')
        my.assertEquals(test, "edit")
        test = access_manager.get_access('sobject', {'search_type':'sthpw/note', 'project':'sample3d'} )
        my.assertEquals(test, "deny")

        test = access_manager.get_access('sobject', {'search_type':'prod/layer', 'project':'sample3d'} )
        my.assertEquals(test, "view")
        test = access_manager.get_access('sobject', 'prod/layer' )
        my.assertEquals(test, "edit")


    def _test_crypto(my):
       
        key = CryptoKey()
        key.generate()
        

        # test verifying a string
        test_string = "Holy Moly"
        signature = key.get_signature(test_string)
        check = key.verify(test_string, signature)
        my.assertEquals(True, check)

        # verify an incorrect string
        check = key.verify("whatever", signature)
        my.assertEquals(False, check)


        # encrypt and decrypt a string
        test_string = "This is crazy"
        coded = key.encrypt(test_string)

        # create a new key
        private_key = key.get_private_key()
        key2 = CryptoKey()
        key2.set_private_key(private_key)
        test_string2 = key2.decrypt(coded)

        my.assertEquals(test_string, test_string2)

    def _test_access_level(my):
        security = Environment.get_security()
        from pyasm.security import get_security_version
        security_version = get_security_version()


        projects = Search.eval('@SOBJECT(sthpw/project)')
        if security_version >= 2:
            for project in projects:
                key = { "code": project.get_code() }
                key2 = { "code": "*" }
                keys = [key, key2]
                default = "deny"
                # other than art, unittest as allowed above, a default low access level user 
                # should not see other projects
                access = security.check_access("project", keys, "allow", default=default)
                if project.get_code() in ['art','unittest']:
                    my.assertEquals(access, True)
                else:
                    my.assertEquals(access, False)
        else:
            raise SecurityException('Please test with security version 2. Set it in your config file')


      

if __name__ == "__main__":
    unittest.main()

