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

import sys

from tactic_client_lib import TacticServerStub

SEARCH_TYPE = "prod/shot"

def main(args):
    # USAGE: query_shot.py <shot_code>
    shot_code = args[0]

    server = TacticServerStub()
    search_key = server.build_search_type(SEARCH_TYPE)

    # do the actual work
    server.start("Queried shot [%s]" % shot_code)
    try:
        filters = [
            ('code', shot_code)
        ]
        print server.query(search_key, filters)

    except:
        server.abort()
        raise
    else:
        server.finish()



if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    main(args)

