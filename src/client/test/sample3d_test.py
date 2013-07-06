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


__all__ = ['Sample3dTest']

import tacticenv
from tactic_client_lib import TacticServerStub

import unittest
import xmlrpclib, sys, os, shutil

class Sample3dTest(unittest.TestCase):

    def setUp(my):
        pass

    def test_all(my):
        print "Running Sample3d Test"

        from pyasm.security import Batch
        from pyasm.biz import Project
        Batch()
        Project.set_project("sample3d")


        #my.server = TacticServerStub(protocol="local")
        my.server = TacticServerStub(protocol="xmlrpc")
        project_code = "sample3d"
        my.server.set_project(project_code)


        my.server.start("Sample3d Test")
        try:
            my._test_create_search_type()
            my._test_create_submission()
            my._test_get_submission()
            my._test_shot_sequence_hierarchy()
            my._test_query_snapshots()
            #my._test_performance()
        except Exception:
            my.server.abort()
            raise
        my.server.abort()


        #try:
        #    my.server.query("prod/asset")
        #except Exception:
        #    my.server.abort()
        #    raise
        #my.server.abort()



    def _test_query_snapshots(my):
        filters = []
        filters.append( ['context', 'model'] )
        filters.append( ['search_type', 'prod/asset?project=sample3d'] )
        snapshots = my.server.query_snapshots(filters=filters, include_paths=True)

        import time
        start = time.time()
        for snapshot in snapshots:
            print snapshot.get('__search_key__')
            print snapshot.get('__paths__')
            print "parent: ", snapshot.get('__parent__')
        print time.time() - start




    def _test_create_search_type(my):
        search_type = 'test'
        search_type_obj = my.server.create_search_type(search_type)
        print search_type_obj




    def _test_performance(my):

        for i in range(0,1):
            assets = my.server.query("prod/asset")
            for asset in assets:
                asset_key = asset.get("__search_key__")
                snapshots = my.server.get_all_children(asset_key,'sthpw/snapshot')
                #snapshot = my.server.get_snapshot(asset_key,context='model', include_paths=True)
                #print snapshot.get('__paths__')


        




    def _test_get_submission(my):

        server = TacticServerStub()
        server.set_project("sample3d")

        # choose some arbitrary bin
        bin_id = 4
        filters = []
        filters.append( ['bin_id', bin_id] )
        connectors = server.query("prod/submission_in_bin", filters)

        # get all of the submissions from the bin
        submission_ids = [x.get('submission_id') for x in connectors]
        filters = [ ['id', submission_ids] ]
        submissions = server.query("prod/submission", filters)


        # get all of the snapshots from the submissions
        for submission in submissions:
            search_key = submission.get('__search_key__')

            print "-"*20
            snapshot = server.get_snapshot(search_key, include_paths=True)

            paths = snapshot.get('__paths__')
            for path in paths:
                print path



    def _test_create_submission(my):

        server = TacticServerStub()
        server.set_project("sample3d")

        # choose some arbitrary bin
        bin_id = 4
        filters = []


        # asset
        parent_type = "prod/asset"
        parent_code = "chr001"
        parent_key = server.build_search_key(parent_type, parent_code)
        parent = server.get_by_search_key(parent_key)
        parent_id = parent.get('id')

        # create a submission
        data = {
            'description': 'A test submission',
            'artist': 'joe',
            'context': 'model'
        }
        submission = server.insert("prod/submission", data, parent_key=parent_key)
        submission_key = submission.get('__search_key__')
        submission_id = submission.get('id')

        file_path = './miso_ramen.jpg'
        context = "publish"
        snapshot = server.simple_checkin(submission_key, context, file_path, mode="upload")

        # no connect to the bin with a connector
        data = {
            "bin_id": bin_id,
            'submission_id': submission_id
        }
        server.insert("prod/submission_in_bin", data)




    def _test_shot_sequence_hierarchy(my):
        shot_key = "prod/shot?project=sample3d&code=RC_001_001"
        shot = my.server.get_by_search_key(shot_key)
        
        parent = my.server.get_parent(shot_key)
        my.assertEquals("RC_001", parent.get("code") )



if __name__ == "__main__":
    unittest.main()


