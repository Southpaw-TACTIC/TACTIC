// -----------------------------------------------------------------------------
//
//  Copyright (c) 2012, Southpaw Technology Inc., All Rights Reserved
//
//  PROPRIETARY INFORMATION.  This software is proprietary to
//  Southpaw Technology Inc., and is not to be reproduced, transmitted,
//  or disclosed in any way without written permission.
//
// -----------------------------------------------------------------------------
//
//

package tactic;

import java.util.*;
import java.io.*;

 
public class TacticTest {

    public static void main (String[] args) throws IOException {

        TacticServerStub server = new TacticServerStub();
        server.set_project("project");

        // test server version
        System.out.println( "Test server version" );
        System.out.println( server.get_server_version() );
        System.out.println( server.get_server_api_version() );
        System.out.println( "----" );

        // test ping
        System.out.println( "Test ping" );
        System.out.println( server.ping() );
        System.out.println( "----" );


        // test connection
        //System.out.println( "Test connection" );
        //System.out.println( server.get_connection_info() );
        //System.out.println( "----" );



        // test simple query
        System.out.println( "Test query" );

        Map<String,Object> kwargs = new HashMap<String,Object>();
        kwargs.put("limit", 3);

        ArrayList result = server.query("sthpw/login", kwargs);
        Iterator<Map> itr = result.iterator();
        while( itr.hasNext() ) {
            Map sobject = (Map) itr.next();
            System.out.println(sobject.get("login") + ": " + sobject.get("email"));
        }
        System.out.println( "----" );

        // test simple query
        System.out.println( "Test query" );

        kwargs = new HashMap<String,Object>();
        kwargs.put("limit", 6);
        kwargs.put("order_bys", "email desc");

        result = server.query("sthpw/login", kwargs);
        itr = result.iterator();
        while( itr.hasNext() ) {
            Map sobject = (Map) itr.next();
            System.out.println(sobject.get("login") + ": " + sobject.get("email"));
        }
        System.out.println( "----" );


        // test simple insert
        System.out.println( "Test insert" );
        Map insert_data = new HashMap();
        insert_data.put("code", "xxx998");
        insert_data.put("title", "Joe");
        insert_data.put("description", "This is joe");
        Map insert_sobject = server.insert("project/asset", insert_data);
        System.out.println(insert_sobject.get("code") + ": " + insert_sobject.get("title") );
        System.out.println( "----" );


        // test simple update
        System.out.println( "Test update" );

        Map update_data = new HashMap();
        update_data.put("title", "Bob");
        update_data.put("description", "This is bob");

        String search_key = "project/asset?project=project&code=xxx998";
        Map sobject = server.update(search_key, update_data);
        System.out.println(sobject.get("code") + ": " + sobject.get("title") );
        System.out.println( "----" );



        // test simple upload
        System.out.println( "Test upload" );
        String path = "./donuts.jpg";
        server.upload_file(path);
        System.out.println( "----" );


        // test simple checkin
        System.out.println( "Test checkin" );
        String context = "test";
        path = "./donuts.jpg";
        server.simple_checkin(search_key, context, path);
        System.out.println( "----" );


        // test delete sobject
        System.out.println( "Test delete" );
        Map delete_kwargs = new HashMap();
        delete_kwargs.put("include_depndencies", true);
        Map deleted_sobject = server.delete_sobject(search_key, kwargs);
        System.out.println( "----" );

    }
}


