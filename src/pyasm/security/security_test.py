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
from pyasm.biz import Project, ExpressionParser

from security import *
from access_manager import *
from batch import *
from crypto_key import *

import unittest

class SecurityTest(unittest.TestCase):

    def _setup(my):

        # intialiaze the framework as a batch process
        Site.set_site('default')
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
       
        s = Search('sthpw/login_group')
        s.add_filter('login_group','user')
        group = s.get_sobject()
        if not group:
            group = SObjectFactory.create("sthpw/login_group")
            group.set_value("login_group", 'user')
            group.set_value('access_level','min')
            group.commit()

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
        #my.transaction = Transaction.get()
        my.transaction.rollback()
        # this is necessary cuz the set_value() was caught in a security exception possibly, needs investigation
        #if my.person:
        #    my.person.delete()
        tasks = Search.eval("@SOBJECT(sthpw/task['project_code','in','unittest|sample3d'])")
        for task in tasks:
            task.delete(triggers=False)

    def test_all(my):
        batch = Batch()
        Environment.get_security().set_admin(True)

        from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment
        test_env = UnittestEnvironment()
        test_env.create()

        sample3d_env = Sample3dEnvironment(project_code='sample3d')
        sample3d_env.create()

        Project.set_project("unittest")
        try:
            my.access_manager = Environment.get_security().get_access_manager()   
            my._test_all()

        finally:
            # Reset access manager for tear down 
            Environment.get_security()._access_manager =  my.access_manager
            Environment.get_security().reset_access_manager() 
            my._tear_down()
            Environment.get_security().set_admin(True)
            test_env.delete()
            Environment.get_security().set_admin(True)
            sample3d_env.delete()
            Site.pop_site()

    def _test_initial_access_level(my):
        # before adding process unittest_guy in user group is in MIN access_level
        # so no access to process, but access to search_types
        my.security.set_admin(False)
        security = Environment.get_security()


        process_keys = [{'process': 'anim'}]
        proc_access = security.check_access("process", process_keys, "allow") 
        my.assertEquals(proc_access, False)

        stype_keys = [{'code':'*'}, {'code':'unittest/city'}]
        stype_access = security.check_access("search_type", stype_keys, "allow") 
        a = security.get_access_manager()
        my.assertEquals(stype_access, True)

        # we don't have this sType specified explicitly, should be False
        stype_keys = [{'code':'unittest/city'}]
        stype_access = security.check_access("search_type", stype_keys, "allow") 
        a = security.get_access_manager()
        my.assertEquals(stype_access, False)



    def _test_all(my):

        try:
            my._setup()
            my._test_crypto()

            my._test_security_fail()
            my._test_security_pass()
            my._test_initial_access_level()
            my._test_sobject_access_manager()
    
            # order matters here
            my._test_search_filter()
            my._test_access_level()
            my._test_access_manager()
        
            my._test_guest_allow()
        except Exception, e:
            print "Error: ", e
            raise




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

        my.assertEquals('unittest_guy',  Environment.get_user_name())
        my.assertEquals( False, fail )

    def count(my, it):
        from collections import defaultdict
        d = defaultdict(int)
        for j in it:
            d[j] += 1
        return d
    
    def _test_search_filter(my):

        # NOTE: this unittest is flawed because it relies on project
        # that may not exist

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

        my.security.set_admin(False)
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
        try:
            search = Search('sthpw/task')
            tasks = search.get_sobjects()

            my.assertEquals(1, len(tasks))
            assigned_codes = SObject.get_values(tasks,'assigned', unique=True)
            project_codes = SObject.get_values(tasks,'project_code', unique=True)
            my.assertEquals(True, ['unittest_guy'] == assigned_codes)
            my.assertEquals(True, ['sample3d'] == project_codes)
        finally:
            Project.set_project('unittest')


      

        # project specific rule
        proj_rules = """
        <rules>
        <rule group="project" code='sample3d' access='allow'/>
        <rule group="project" code='unittest' access='allow'/>
        <rule value='$PROJECT' search_type='sthpw/task' column='project_code' group='search_filter'/>
        <rule value='@GET(login.login)' search_type='sthpw/task' column='assigned' group='search_filter' project='unittest'/>
        <rule group="process" process="anim" access="allow"/>
        <rule group="process" process="comp" access="allow"/>
        </rules>
        """
        xml = Xml()
        xml.read_string(proj_rules)
        # reset it
        Environment.get_security().reset_access_manager()

        access_manager = Environment.get_security().get_access_manager()
        access_manager.add_xml_rules(xml)

        project = Project.get_by_code('sample3d')
        if project:
            Project.set_project('sample3d')
            search = Search('sthpw/task')
            tasks = search.get_sobjects()

            assigned_codes = SObject.get_values(tasks,'assigned', unique=True)
            project_codes = SObject.get_values(tasks,'project_code', unique=True)
            # should fail since project is switched to sample3d.. and it should have more than just unittest
            my.assertEquals(False, ['unittest'] == assigned_codes)
            my.assertEquals(True, ['sample3d'] == project_codes)




            # unittest specific rule that uses negation !=, this takes care of NULL value automatically
            rules = """
            <rules>
                <rule group="project" code='sample3d' access='allow'/>
                <rule value='5' search_type='sthpw/task' column='priority' op='!=' group='search_filter' project='sample3d'/>
                 <rule group="process" process="anim" access="allow"/>
                <rule group="process" process="comp" access="allow"/>
            </rules>
            """
            xml = Xml()
            xml.read_string(rules)
            # reset it
            Environment.get_security().reset_access_manager()

            access_manager = Environment.get_security().get_access_manager()
            access_manager.add_xml_rules(xml)

            Project.set_project('sample3d')
            search = Search('sthpw/task')
            tasks = search.get_sobjects()

            priorities = SObject.get_values(tasks,'priority', unique=True)
            #project_codes = SObject.get_values(tasks,'project_code', unique=True)
            
            for p in priorities:
                my.assertEquals(True, p != 5)
      
        try: 
            Project.set_project('unittest')
        except SecurityException, e:
            # should get an SecurityException
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
            # this should not happen
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
        # reset it
        Environment.get_security().reset_access_manager()

        access_manager = Environment.get_security().get_access_manager()

        xml = Xml()
        xml.read_string('''
        <rules>
          
       
          <rule group='sobject' key='corporate/budget' access='allow'/>
          <rule group='sobject'  key='corporate/salary' access='allow'/>
          <rule group='sobject'  key='prod/asset' access='edit'/>
          <rule group='sobject' search_type='sthpw/note'  project='sample3d' access='edit'/>
          <group type='url' default='deny'>
            <rule key='/tactic/bar/Partner' access='view'/>
            <rule key='/tactic/bar/External' access='view'/>
          </group>


          
            <rule group='sobject' search_type='prod/layer'  project='sample3d' access='view'/>
            <rule column='description'  search_type='prod/shot' access='view' group='sobject_column'/>
           
          <group type='sobject_column' default='edit'>
            <rule key='prod/asset|director_notes' access='deny'/>
            <rule key='prod/asset|sensitive_data' access='deny'/>
          </group>

      
          <rule group='search_type' code='prod/asset'   access='allow'/>

          <rule group='search_type' code='sthpw/note' project='unittest' access='edit'/>
          
           
          <rule group='search_type' code='unittest/person'  project='unittest' access='allow'/>
          <rule group='builtin' key='view_site_admin' access='allow'/>
          <rule group='builtin' key='export_all_csv' project='unittest' access='allow'/>
          <rule group='builtin' key='import_csv' access='allow'/>

          <rule group='builtin' key='retire_delete' project='*' access='allow'/>
          <rule group='builtin' key='view_side_bar' access='allow'/>
                  
           </rules>
        ''')
        access_manager.add_xml_rules(xml)

        

        # try mixing in a 2nd login_group rule with a project override, mimmicking a 
        # login_group with project_code. but project group is special it doesn't get the usual
        # project_override treatment
        xml2 = Xml()
        xml2.read_string('''
        <rules>
          <rule group="project" code="sample3d" access="allow"/>
          <rule group="project" code="unittest" access="allow"/>

          <rule group='builtin' key='view_side_bar' project='sample3d' access='allow'/>
        </rules>
        ''')
 
        access_manager.add_xml_rules(xml2)

        access_manager.print_rules('project')
        
        test = access_manager.check_access('builtin', 'view_site_admin','allow')
        my.assertEquals(test, True)

        
        Project.set_project('sample3d')
        test = access_manager.check_access('builtin', 'export_all_csv','allow')
        my.assertEquals(test, False)

        # old way of checking project
        test = access_manager.check_access('project', 'sample3d','allow')
        my.assertEquals(test, True)

        Project.set_project('unittest')
        # old way should work as well
        test = access_manager.check_access('builtin', 'export_all_csv','allow')
        my.assertEquals(test, True)
        
        # default to the system's hardcoded deny for builtin
        test = access_manager.check_access('builtin', 'export_all_csv','allow', default='deny')
        my.assertEquals(test, True)



        # this is the new way to control per project csv export
        keys = [{'key':'export_all_csv', 'project': 'unittest'}, {'key':'export_all_csv','project': '*'}]
        test = access_manager.check_access('builtin', keys ,'allow')
        my.assertEquals(test, True)
        keys = [{'key':'import_csv', 'project': '*'}, {'key':'import_csv','project': Project.get_project_code()}]
        test = access_manager.check_access('builtin', keys ,'allow')
        my.assertEquals(test, True)


        test = access_manager.check_access('builtin', 'view_side_bar','allow')
        my.assertEquals(test, True)
        key = { "project": 'unittest', 'key':'view_side_bar' }
        key1 = { "project": 'sample3d', 'key':'view_side_bar' }
        key2 = { "project": "*",'key': 'view_side_bar' }
        keys = [key, key2]
        test = access_manager.check_access('builtin', keys,'allow')
        my.assertEquals(test, True)
        keys = [key1, key2]
        test = access_manager.check_access('builtin', keys,'allow')
        my.assertEquals(test, True)

        test = access_manager.check_access('builtin', 'retire_delete','allow')

        my.assertEquals(test, True)

        # test sensitive sobject
        test = access_manager.get_access('sobject', 'corporate/budget')
        my.assertEquals(test, "allow")

        # test allowed sobject
        test = access_manager.get_access('sobject', 'prod/asset')
        my.assertEquals(test, "edit")

        test = access_manager.get_access('sobject', [{'search_type':'sthpw/note', 'project':'sample3d'}])
        my.assertEquals(test, "edit")
        # test url
        test = access_manager.get_access('url', '/tactic/bar/Partner')
        my.assertEquals(test, "view")

        # test with access values ... a more typical usage
        test = access_manager.check_access('sobject','prod/asset','view')
        my.assertEquals(test, True)

        test = access_manager.check_access('sobject','corporate/budget','edit')
        my.assertEquals(test, True)

        test = access_manager.check_access('sobject_column', 'prod/asset|director_notes','deny')
        my.assertEquals(test, True)

        test = access_manager.check_access('sobject_column',{'search_type':'prod/shot','column':'description'},'edit')
        my.assertEquals(test, False)

        test = access_manager.check_access('sobject_column',{'search_type':'prod/shot','column':'description'},'view')
        my.assertEquals(test, True)


        test = access_manager.get_access('sobject',  {'search_type':'sthpw/note', 'project':'sample3d'} )
        my.assertEquals(test, "edit")
        test = access_manager.get_access('sobject', {'search_type':'sthpw/note'} )
        my.assertEquals(test, None)

        test = access_manager.get_access('sobject', {'search_type':'prod/layer', 'project':'sample3d'} )
        my.assertEquals(test, "view")
        test = access_manager.get_access('sobject', 'prod/layer' )
        my.assertEquals(test, None)

        Project.set_project('sample3d')
        # security version 2 uses group = search_type
        asset = SearchType.create('prod/asset')
        asset.set_value('name','unit test obj')
        asset.commit(triggers=False)
        # replace the access manager with this 
        Environment.get_security()._access_manager = access_manager
        
        test = access_manager.check_access('search_type',{'search_type':'prod/asset','project':'sample3d'},'delete')
        my.assertEquals(test, False)

        asset.delete()

        note = SearchType.create('sthpw/note')
        note.set_value('note','unit test note obj')
        note.set_value('project_code','unittest')
        note.commit(triggers=False)
        

        test = access_manager.get_access('search_type', [{'code':'sthpw/note', 'project':'unittest'}] )
        my.assertEquals(test, 'edit')
        msg = ''
        # delete of unittest note should fail
        try:
            note.delete()
        except SObjectException, e:
            msg = 'delete error'
        my.assertEquals(msg, 'delete error')
            
        note = SearchType.create('sthpw/note')
        note.set_value('note','unit test sample3d note obj')
        note.set_value('project_code','sample3d')
        note.commit(triggers=False)
        
        # this should pass since it's a sthpw/ prefix
        note.delete()

        test = access_manager.check_access('search_type',{'search_type':'sthpw/note','project':'unittest'},'delete')
        my.assertEquals(test, False)
        
        my.assertEquals('unittest_guy',  Environment.get_user_name())


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
                # other than sample3d, unittest as allowed above, a default low access level user 
                # should not see other projects
                access = security.check_access("project", keys, "allow", default=default)
                process_keys = [{'process': 'anim'}]
                proc_access = security.check_access("process", process_keys, "allow")
                my.assertEquals(proc_access, True)
                if project.get_code() in ['sample3d','unittest']:
                    my.assertEquals(access, True)
                else:
                    my.assertEquals(access, False)
        else:
            raise SecurityException('Please test with security version 2. Set it in your config file')



    def _test_guest_allow(my):
        '''test Config tag allow_guest in security tag.
        Note: Since it is hard to emulate AppServer class, 
        this is based on logic which handles in _get_display 
        of BaseAppServer.
        
        1. If allow_guest is false, then it is necessary that 
        Sudo is instantiated.

        2. If allow_guest is true, then it is necessary that 
        guest login rules are added and login_as_guest is
        executed.
        '''

        security = Security()
        Environment.set_security(security)
        
        #1. allow_guest is false
        fail = False
        try:
            sudo = Sudo()
        except Exception as e:
            fail = True
        my.assertEquals( False, fail ) 
        sudo.exit()
        
        key = [{'code': "*"}]
        project_access = security.check_access("project", key, "allow")
        my.assertEquals(project_access, False)
        
        #2. allow_guest is true
        Site.set_site("default")
        try:
            security.login_as_guest()
            ticket_key = security.get_ticket_key()
            access_manager = security.get_access_manager()
            xml = Xml()
            xml.read_string('''
            <rules>
              <rule column="login" value="{$LOGIN}" search_type="sthpw/login" access="deny" op="!=" group="search_filter"/>
              <rule group="project" code="default" access="allow"/>
            </rules>
            ''')
            access_manager.add_xml_rules(xml)
        finally:
            Site.pop_site()
       
        
        default_key = [{'code': "default"}]
        project_access = security.check_access("project", default_key, "allow")
        my.assertEquals(project_access, True)  
        
        unittest_key = [{'code', "sample3d"}]
        project_access = security.check_access("project", unittest_key, "allow")
        my.assertEquals(project_access, False)  
        

       
         

if __name__ == "__main__":
    unittest.main()

