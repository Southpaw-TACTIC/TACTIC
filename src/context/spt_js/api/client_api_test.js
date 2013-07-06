// -----------------------------------------------------------------------------
/
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//
//   PROPRIETARY INFORMATION.  This software is proprietary to
//   Southpaw Technology Inc., and is not to be reproduced, transmitted,
//   or disclosed in any way without written permission.
//
//
// -----------------------------------------------------------------------------
//
//
//

spt.ClientApiTest = new Class( {

    initialize: function() {
        this.server = TacticServerStub.get()
    },

    _test_version: function() {
        var server_version = this.server.get_server_version();
        var client_api_version = this.server.get_client_api_version();
        this.assertEqual(server_version, client_api_version);
    },

    _test_checkin: function() {
        var file_path = "C:/New Folder/test.txt";

        var search_type = "unittest/person";
        var code = "joe";
        var context = "test_context";
        var search_key = this.server.build_search_key(search_type, code);

        // simple checkin of a file. No dependencies
        var desc = 'A Simple Checkin';
        var result = my.server.simple_checkin(search_key, context, file_path, { description: desc});
        spt.js_log.debug(result);

        this.assertNotEquals(result, null);

        var snapshot_code = result['code'];
        this.assertEquals("1", result['version']);

        var snapshot_description = result['description'];
        my.assertEquals(snapshot_description, desc);

        var path = this.server.get_path_from_snapshot(snapshot_code,file_type);
        // FIXME: need to go through applet for this
        //exists = os.path.exists(path)
        this.assertEquals(true, exists);

        // check that the file name is correct
        



    },


} )


