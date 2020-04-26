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

    def setUp(self):
        pass

    def test_all(self):
        print "Running Client Application API Test"

        from tactic_client_lib import TacticServerStub

        # set the server to test... assume it is run on the server
        server = "localhost"
        url = "http://%s/tactic/default/Api/" % server


        self.server = TacticServerStub.get()
        project_code = "unittest"
        self.server.set_project(project_code)

        self.server.start("Client API Unittest")

        from tactic_client_lib.application.common import TacticNodeUtil
        self.util = TacticNodeUtil()
        from tactic_client_lib.application.maya import Maya
        self.app = Maya()

        try:
            data = {
                'code': 'joe'
            }
            self.person = self.server.insert("unittest/person", data)

            data = {
                'code': 'mary'
            }
            self.person2 = self.server.insert("unittest/person", data)


            self._test_load_template()
            self._test_checkin()
            self._test_load()
            self._test_introspect()

        except Exception:
            self.server.abort()
            raise
        else:
            self.server.abort()



    def _test_load_template(self):
        '''load in asset (one with no snapshots)'''

        search_key = self.person.get("__search_key__")
        code = self.person.get("code")
        context = 'model'

        # create a new default entity
        node_name = code
        tactic_node = self.util.create_default_node(node_name, search_key, context)
        self.assertEquals( "tactic_joe", tactic_node)

        # check that it exists in Maya
        exists = self.app.mel("ls %s" % tactic_node)
        self.assertEquals( True, exists != None )


        # create a second one
        search_key = self.person2.get("__search_key__")
        code = self.person2.get("code")
        context = 'model'

        # create a new default entity
        node_name = code
        tactic_node = self.util.create_default_node(node_name, search_key, context)
        self.assertEquals( "tactic_mary", tactic_node)





        # now that it is created, find all of the tactic nodes
        tactic_nodes = self.util.get_all_tactic_nodes()
        self.assertEquals( 2, len(tactic_nodes) )




    def _test_checkin(self):

        # checkin a tactic node
        tactic_node = 'tactic_joe'

        # get the entity to check into (assume same as last one)
        search_key = self.util.get_search_key(tactic_node)
        self.assertEquals("unittest/person?project=unittest&code=joe", search_key)

        context = self.util.get_context(tactic_node)
        self.assertEquals("model", context)

        # create a new snapshot
        snapshot = self.server.create_snapshot(search_key, context=context)

        # add the snapshot to the node
        self.util.add_snapshot_to_node(tactic_node, snapshot)

        # save the file and check it in
        path = "blah.ma"
        path = self.app.save(path)

        # check in the file
        snapshot_code = snapshot.get('code')
        snapshot = self.server.add_file(snapshot_code, file_path=path, mode='upload')
        # extract the path
        path = self.server.get_path_from_snapshot(snapshot.get('code'))
        exists = os.path.exists(path)
        self.assertEquals(True, exists)


        # get the path from the latest snapshot
        context = 'model'
        snapshot = self.server.get_snapshot(search_key, context)

        snapshot_code = snapshot.get('code')
        path = self.server.get_path_from_snapshot(snapshot_code)

        self.app.load(path)

        # get all of the tactic nodes
        tactic_nodes = self.util.get_all_tactic_nodes()
        self.assertEquals(['tactic_joe', 'tactic_mary'], tactic_nodes)




    def _test_load(self):
        '''a more realistic loading example'''
        return

        # find all of the Tactic nodes
        search_type = self.person.get('__search_type__')
        code = self.person.get('code')
        search_key = self.server.build_search_key(search_type, code)

        # first checkin in a dummy model file
        path = "whatever_model.ma"
        file = open(path, 'w')
        file.write("whatever_model.ma")
        file.close()
        self.server.upload_file(path)
        model_snapshot = self.server.simple_checkin(search_key, file_path=path, context="model")

        # then checkin a dummy rig file with a reference to the model snapshot
        path = "whatever_rig.ma"
        file = open(path, 'w')
        file.write("whatever_rig.ma")
        file.close()
        self.server.upload_file(path)
        rig_snapshot = self.server.simple_checkin(search_key, file_path=path, context="rig")
        rig_snapshot = self.server.add_dependency_by_code(
            rig_snapshot.get('code'),
            model_snapshot.get('code')
        )

        
        # the the latest full snapshot
        context = "rig"
        snapshot = self.server.get_snapshot(search_key, context)
        snapshot_type = snapshot.get("snapshot_type")
        snapshot_code = snapshot.get('code')
        snapshot_xml = self.server.get_full_snapshot_xml(snapshot_code)

        # we know based on the snapshot type that there is a rig and a
        # reference to a model
        print snapshot_xml





        

    def _test_introspect(self):

        # introspect the session
        from tactic_client_lib.application.common import Session
        session = Session()
        xml = session.introspect()

        # commit this session to the database
        session.commit()

        # get snapshots from the session
        snapshots = session.get_snapshots()

        # only one tactic node has a checkin
        self.assertEquals( 1, len(snapshots) )


        # get the last session
        session.get_last()

        # get snapshots from the session
        snapshots = session.get_snapshots()
        self.assertEquals( 1, len(snapshots) )



    def test_explorer(self):
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




