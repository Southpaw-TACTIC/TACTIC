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

    def setUp(self):
        pass

    def test_all(self):

        url = "http://saba/tactic/default/Api/"
        login_ticket = "9246c9d636c1331c418a9c8ef4356e95"
        self.project_code = "bar"


        self.server = xmlrpclib.Server(url)

        # do a simple insert using a fixed ticket and then undo it
        self.ticket = login_ticket
        self.server.set_state(self.ticket, "project", self.project_code)
        self._test_insert()

        self.server.undo(self.ticket)

        # test basic functionality in a transaction.  A new ticket is
        # generated which is used to append to the transaction.
        self.ticket = self.server.start(login_ticket, self.project_code, "Client Api test suite")
        try:
            self._test_simple()
            self._test_query()
            self._test_insert()
            self._test_update()
            self._test_checkin()
        finally:
            # make sure that no matter what happens transaction is undone
            self.server.finish(self.ticket)

        self.server.undo(self.ticket)


        # test with an error
        self.ticket = self.server.start(login_ticket, self.project_code, "Client Api Error Test")
        try:
            self._test_insert()
            self.server.test_error()
        except:
            print "Error Caught"
            self.server.undo(self.ticket)
 
        return




    def _test_simple(self):
        result = self.server.test(self.ticket)
        self.assertEquals("test", result)


    def _test_query(self):
        print "Testing Api Query"

        search_type = "prod/shot"
        filters = []
        filters.append( ("code", "XG007") )

        columns = ['id', 'code', 'tc_frame_start', 'tc_frame_end']


        result = self.server.query(self.ticket, search_type, filters, columns)
        code = result[0]['code']
        self.assertEquals('XG007', code)



    def _test_insert(self):
        '''Test an individual insert of a shot and undo'''
        print "Testing Api Insert"

        search_type = "prod/shot"

        # create a dictionary with data for the shot
        data = {
            'code': 'XG999',
            'sequence_code': 'XG',
            'description': 'A dynamically created shot'
        }

        result = self.server.insert(self.ticket, search_type, data)
        self.assertEquals('XG999', result.get('code'))



    def _test_update(self):
        '''update the shot'''
        print "Testing Api Update"

        search_key = "prod/shot?project=%s&code=XG999" % self.project_code

        data = {'description': 'A new description'}

        result = self.server.update(self.ticket, search_key, data)
        self.assertEquals("A new description", result.get("description") )




    def _test_checkin(self):
        # upload a file
        file_path = "./test/test.jpg"

        #upload_file(self.ticket, upload_url, file_path)
        file = open(file_path, 'rb')
        data = xmlrpclib.Binary( file.read() )
        file.close()
        self.server.upload_file(self.ticket, "test.jpg", data)

        # now check in the file
        search_key = "prod/shot?project=bar&code=XG999"

        # simple checkin of a file.  No dependencies
        context = "publish"
        result = self.server.simple_checkin(self.ticket, search_key, context, file_path)
        # No real test needed here.  If it failed, it will stack trace
        self.assertNotEquals(result, None)


    # NOT IMPLEMENTED YET
    def _test_checkin_with_dependency(self):

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
        #self.server.checkin(self.ticket, search_key, ref_xml)


    # NOT IMPLEMENTED
    def _test_multicall(self):
        '''NOTE: Not support by cherrypy yet!!'''

        # start a multicall transaction

        search_type = "prod/shot"

        multicall = xmlrpclib.MultiCall(self.server)

        for i in range(0, 3):
            sequence_code = "FG"
            code = "%s%0.3d" % (sequence_code, i)
            data = {
                'code': code,
                'sequence_code': sequence_code,
                'description': 'Dynamic Shot'
            }

            #multicall.insert(self.ticket, search_type, data)
            multicall.test()

        result = multicall()

        #self.server.commit()




if __name__ == "__main__":
    unittest.main()


