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
# Description: Generic script to checkout files from a snapshot
#
# usage: checkout.py <search_type> <code> [context] <to_dir>
# example: python checkin.py beat Sc01.Bt01 .\test



import sys

from tactic_client_lib import TacticServerStub


def main(args):

    search_type = args[0]
    code = args[1]
    if len(args) == 2:
        context = "publish"
        to_dir = "."
    elif len(args) == 3:
        context = "publish"
        to_dir = args[2]
    else:
        context = args[2]
        to_dir = args[3]

    server = TacticServerStub()

    # do the actual work
    server.start("Checked out file/s to [%s]" % to_dir)
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

        # checkin the uploaded file
        version = -1
        result = server.checkout(search_key, context, version=version, to_dir=to_dir)
        print result
    except:
        server.abort()
        raise
    else:
        server.finish()


if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    main(args)

