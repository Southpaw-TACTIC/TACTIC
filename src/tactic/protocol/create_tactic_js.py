

import tacticenv

import os

install_dir = tacticenv.get_install_dir()

js_dir = "%s/src/context/spt_js" % install_dir
files = ["environment.js", "xmlrpc.js", "client_api.js"]


o = open("%s/tactic.js" % js_dir, "w")


# add bootstrap
o.write('''// -----------------------------------------------------------------------------
//
//  Copyright (c) 2017, Southpaw Technology Inc., All Rights Reserved
//   
//  PROPRIETARY INFORMATION.  This software is proprietary to
//  Southpaw Technology Inc., and is not to be reproduced, transmitted,
//  or disclosed in any way without written permission.
//   
// 





/* Bootstrap TACTIC API */

var spt = {};

// Fixes
spt.browser = {};
spt.browser.is_IE = function() { return false; }


// simple exception class to just rethrow exception
spt.exception = {};

spt.exception.handle_fault_response = function( response_text ) {
    throw( response_text )
}

spt.exception.handler = function( ex ) {
    throw( ex )
}

''')



for filename in files:
    path = "%s/%s" % (js_dir, filename)
    print 'path: ', path

    if not os.path.exists(path):
        raise Exception("Cannot find file [%s]" % filename)


    o.write("\n/* START: %s */\n\n" % filename)

    f = open(path, "r")
    o.write( f.read() )
    f.close()

    o.write("\n/* END: %s */\n\n" % filename)

o.close()


"""
from jsmin import jsmin
with open("./test.js") as js_file:
    minified = jsmin(js_file.read())

    f = open("./test2.js", "w")
    f.write(minified)
    f.close()
"""




