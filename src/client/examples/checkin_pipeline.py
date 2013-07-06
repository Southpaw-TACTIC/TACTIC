###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import sys

from tactic_client_lib import TacticServerStub


def main(args):
    usage = "USAGE: checkin.py <search_type> <code> [context] <path>\n"
    usage += "example: python checkin.py beat Sc01.Bt01 .\\test\\image.png"

    context = "publish"

    # TODO: lots of assumptions here
    if len(args) == 2:
        # assume code and file path are equivalent
        code = args[1]
        file_path = args[1]
    elif len(args) == 3:
        code = args[1]
        file_path = args[2]
    elif len(args) == 4:
        code = args[1]
        context = args[2]
        file_path = args[3]
    else:
        print usage
        return

    search_type = args[0]

    server = TacticServerStub()

    # do the actual work
    server.start("Checked in file [%s] to [%s] - [%s]" % (file_path, search_type, code) )
    try:
        # query all of the search_types to simplify argument
        if search_type.find("/") == -1:
            columns = ["search_type"]
            results = server.query("sthpw/search_object", columns=columns)
            for result in results:
                test = result.get("search_type")
                if test.endswith("/%s" % search_type):
                    search_type = test
                    break
            else:
                raise Exception("Search type [%s] not found" % search_type)

        search_key = server.build_search_key(search_type, code)

        # upload the file
        server.upload_file(file_path)

        # checkin the uploaded file
        result = server.simple_checkin(search_key, context, file_path)
    except Exception, e:
        server.abort()
        print "ERROR: ", e.__str__()
    else:
        server.finish()


if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    main(args)

