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

import sys, getopt

from tactic_client_lib import TacticServerStub

SEARCH_TYPE = "prod/shot"

def main(args, login=None):
    # USAGE: checkin_shot.py <shot_code> <context> <path>
    shot_code = args[0]
    context = args[1]
    file_path = args[2]

    server = TacticServerStub(login)
    search_key = server.build_search_key(SEARCH_TYPE, shot_code)

    # do the actual work
    server.start("Checked in file [%s]" % file_path)
    try:
        # upload the file
        #server.upload_file(file_path)

        # checkin the uploaded file
        result = server.simple_checkin(search_key, context, file_path, mode='upload')
    except:
        server.abort()
        raise
    else:
        server.finish()



if __name__ == '__main__':
    
    executable = sys.argv[0]
    login = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:h", ["login=","help"])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-l", "--login"):
            login = a
            print 
        if o in ("-h", "--help"):
            print "python checkin_shot.py -l <tactic_login> <code> <context> <file_path>"
            print "python checkin_shot.py -l admin S0001 anim C:/shot_S0001.ma"
   
    if len(args) != 3:
        print "python checkin_shot.py -l <tactic_login> <code> <context> <file_path>"
        print "python checkin_shot.py -l admin S0001 anim C:/shot_S0001.ma"
        sys.exit(2)
    main(args, login=login)

