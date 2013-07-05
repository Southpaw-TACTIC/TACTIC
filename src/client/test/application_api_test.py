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


__all__ = ['ApplicationApiTest']



import unittest
import xmlrpclib, sys, os, shutil

class ApplicationApiTest(unittest.TestCase):

    def setUp(my):
        pass

    def test_all(my):
        print "Running Client Application API Test"

        from tactic_client_lib import TacticServerStub

        # set the server to test... assume it is run on the server
        server = "localhost"
        url = "http://%s/tactic/default/Api/" % server


        my.server = TacticServerStub.get()
        project_code = "unittest"
        my.server.set_project(project_code)

        my.server.start("Client API Unittest")

        from tactic_client_lib.application.common import TacticNodeUtil
        my.util = TacticNodeUtil()
        from tactic_client_lib.application.maya import Maya
        my.app = Maya()

        try:
            data = {
                'code': 'joe'
            }
            my.person = my.server.insert("unittest/person", data)

            data = {
                'code': 'mary'
            }
            my.person2 = my.server.insert("unittest/person", data)


            my._test_load_template()
            my._test_checkin()
            my._test_load()
            my._test_introspect()

        except Exception:
            my.server.abort()
            raise
        else:
            my.server.abort()



    def _test_load_template(my):
        '''load in asset (one with no snapshots)'''

        search_key = my.person.get("__search_key__")
        code = my.person.get("code")
        context = 'model'

        # create a new default entity
        node_name = code
        tactic_node = my.util.create_default_node(node_name, search_key, context)
        my.assertEquals( "tactic_joe", tactic_node)

        # check that it exists in Maya
        exists = my.app.mel("ls %s" % tactic_node)
        my.assertEquals( True, exists != None )


        # create a second one
        search_key = my.person2.get("__search_key__")
        code = my.person2.get("code")
        context = 'model'

        # create a new default entity
        node_name = code
        tactic_node = my.util.create_default_node(node_name, search_key, context)
        my.assertEquals( "tactic_mary", tactic_node)





        # now that it is created, find all of the tactic nodes
        tactic_nodes = my.util.get_all_tactic_nodes()
        my.assertEquals( 2, len(tactic_nodes) )




    def _test_checkin(my):

        # checkin a tactic node
        tactic_node = 'tactic_joe'

        # get the entity to check into (assume same as last one)
        search_key = my.util.get_search_key(tactic_node)
        my.assertEquals("unittest/person?project=unittest&code=joe", search_key)

        context = my.util.get_context(tactic_node)
        my.assertEquals("model", context)

        # create a new snapshot
        snapshot = my.server.create_snapshot(search_key, context=context)

        # add the snapshot to the node
        my.util.add_snapshot_to_node(tactic_node, snapshot)

        # save the file and check it in
        path = "blah.ma"
        path = my.app.save(path)

        # check in the file
        snapshot_code = snapshot.get('code')
        snapshot = my.server.add_file(snapshot_code, file_path=path, mode='upload')
        # extract the path
        path = my.server.get_path_from_snapshot(snapshot.get('code'))
        exists = os.path.exists(path)
        my.assertEquals(True, exists)


        # get the path from the latest snapshot
        context = 'model'
        snapshot = my.server.get_snapshot(search_key, context)

        snapshot_code = snapshot.get('code')
        path = my.server.get_path_from_snapshot(snapshot_code)

        my.app.load(path)

        # get all of the tactic nodes
        tactic_nodes = my.util.get_all_tactic_nodes()
        my.assertEquals(['tactic_joe', 'tactic_mary'], tactic_nodes)




    def _test_load(my):
        '''a more realistic loading example'''
        return

        # find all of the Tactic nodes
        search_type = my.person.get('__search_type__')
        code = my.person.get('code')
        search_key = my.server.build_search_key(search_type, code)

        # first checkin in a dummy model file
        path = "whatever_model.ma"
        file = open(path, 'w')
        file.write("whatever_model.ma")
        file.close()
        my.server.upload_file(path)
        model_snapshot = my.server.simple_checkin(search_key, file_path=path, context="model")

        # then checkin a dummy rig file with a reference to the model snapshot
        path = "whatever_rig.ma"
        file = open(path, 'w')
        file.write("whatever_rig.ma")
        file.close()
        my.server.upload_file(path)
        rig_snapshot = my.server.simple_checkin(search_key, file_path=path, context="rig")
        rig_snapshot = my.server.add_dependency_by_code(
            rig_snapshot.get('code'),
            model_snapshot.get('code')
        )

        
        # the the latest full snapshot
        context = "rig"
        snapshot = my.server.get_snapshot(search_key, context)
        snapshot_type = snapshot.get("snapshot_type")
        snapshot_code = snapshot.get('code')
        snapshot_xml = my.server.get_full_snapshot_xml(snapshot_code)

        # we know based on the snapshot type that there is a rig and a
        # reference to a model
        print snapshot_xml





        

    def _test_introspect(my):

        # introspect the session
        from tactic_client_lib.application.common import Session
        session = Session()
        xml = session.introspect()

        # commit this session to the database
        session.commit()

        # get snapshots from the session
        snapshots = session.get_snapshots()

        # only one tactic node has a checkin
        my.assertEquals( 1, len(snapshots) )


        # get the last session
        session.get_last()

        # get snapshots from the session
        snapshots = session.get_snapshots()
        my.assertEquals( 1, len(snapshots) )



    def test_explorer(my):
        pass



    def main():
        #sys.path.insert(0, "C:/Program Files/Southpaw/Tactic1.9/src/client")
        sys.path.insert(0, "..")
        try:
            unittest.main()
        except SystemExit:
            pass
    main = staticmethod(main)



if __name__ == "__main__":
    ApplicationApiTest.main()




