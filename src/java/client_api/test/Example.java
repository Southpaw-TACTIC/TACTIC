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

import tactic.TacticServerStub;

import java.io.*;
import java.util.*;

public class Example {

    public static void main (String[] args) throws IOException {

        TacticServerStub server = new TacticServerStub();
        server.set_project("project");
        //server.set_protocol("xmlrpc");

        // test server version
        System.out.println( "Test server version" );
        System.out.println( server.get_server_version() );
        System.out.println( server.get_server_api_version() );
        System.out.println( "----" );

        // test ping
        System.out.println( "Test ping" );
        System.out.println( server.ping() );
        System.out.println( "----" );

    }
}



