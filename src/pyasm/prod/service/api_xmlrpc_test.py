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


__all__ = ['ApiTest']


import unittest
import xmlrpclib

class ApiTest(unittest.TestCase):

    def setUp(my):
        pass

    def test_all(my):

        url = "http://saba/tactic/default/Api/"
        login_ticket = "9246c9d636c1331c418a9c8ef4356e95"
        my.project_code = "bar"


        my.server = xmlrpclib.Server(url)

        # do a simple insert using a fixed ticket and then undo it
        my.ticket = login_ticket
        my.server.set_state(my.ticket, "project", my.project_code)
        my._test_insert()

        my.server.undo(my.ticket)

        # test basic functionality in a transaction.  A new ticket is
        # generated which is used to append to the transaction.
        my.ticket = my.server.start(login_ticket, my.project_code, "Client Api test suite")
        try:
            my._test_simple()
            my._test_query()
            my._test_insert()
            my._test_update()
            my._test_checkin()
        finally:
            # make sure that no matter what happens transaction is undone
            my.server.finish(my.ticket)

        my.server.undo(my.ticket)


        # test with an error
        my.ticket = my.server.start(login_ticket, my.project_code, "Client Api Error Test")
        try:
            my._test_insert()
            my.server.test_error()
        except:
            print "Error Caught"
            my.server.undo(my.ticket)
 
        return




    def _test_simple(my):
        result = my.server.test(my.ticket)
        my.assertEquals("test", result)


    def _test_query(my):
        print "Testing Api Query"

        search_type = "prod/shot"
        filters = []
        filters.append( ("code", "XG007") )

        columns = ['id', 'code', 'tc_frame_start', 'tc_frame_end']


        result = my.server.query(my.ticket, search_type, filters, columns)
        code = result[0]['code']
        my.assertEquals('XG007', code)



    def _test_insert(my):
        '''Test an individual insert of a shot and undo'''
        print "Testing Api Insert"

        search_type = "prod/shot"

        # create a dictionary with data for the shot
        data = {
            'code': 'XG999',
            'sequence_code': 'XG',
            'description': 'A dynamically created shot'
        }

        result = my.server.insert(my.ticket, search_type, data)
        my.assertEquals('XG999', result.get('code'))



    def _test_update(my):
        '''update the shot'''
        print "Testing Api Update"

        search_key = "prod/shot?project=%s&code=XG999" % my.project_code

        data = {'description': 'A new description'}

        result = my.server.update(my.ticket, search_key, data)
        my.assertEquals("A new description", result.get("description") )




    def _test_checkin(my):
        # upload a file
        file_path = "./test/test.jpg"

        #upload_file(my.ticket, upload_url, file_path)
        file = open(file_path, 'rb')
        data = xmlrpclib.Binary( file.read() )
        file.close()
        my.server.upload_file(my.ticket, "test.jpg", data)

        # now check in the file
        search_key = "prod/shot?project=bar&code=XG999"

        # simple checkin of a file.  No dependencies
        context = "publish"
        result = my.server.simple_checkin(my.ticket, search_key, context, file_path)
        # No real test needed here.  If it failed, it will stack trace
        my.assertNotEquals(result, None)


    # NOT IMPLEMENTED YET
    def _test_checkin_with_dependency(my):

        # checkin an -ref.xml file
        # assumes files are already uploaded
        ref_xml = '''
        <session>
          <ref path="D:/tactic_temp/temp/shot_XG002.ma">
            <ref path="D:/tactic_temp/repo/bar/asset/cam/cam002/scenes/cam002_model_v002_BAR.ma"/>
            <ref path="D:/tactic_temp/repo/bar/asset/furn/furn002/scenes/furn002_0000387BAR.ma"/>
            <ref path="D:/tactic_temp/repo/bar/asset/furn/furn001/scenes/furn001_model_v007_BAR.ma"/>
          </ref>
        </session>
        '''
        #my.server.checkin(my.ticket, search_key, ref_xml)


    # NOT IMPLEMENTED
    def _test_multicall(my):
        '''NOTE: Not support by cherrypy yet!!'''

        # start a multicall transaction

        search_type = "prod/shot"

        multicall = xmlrpclib.MultiCall(my.server)

        for i in range(0, 3):
            sequence_code = "FG"
            code = "%s%0.3d" % (sequence_code, i)
            data = {
                'code': code,
                'sequence_code': sequence_code,
                'description': 'Dynamic Shot'
            }

            #multicall.insert(my.ticket, search_type, data)
            multicall.test()

        result = multicall()

        #my.server.commit()




if __name__ == "__main__":
    unittest.main()


