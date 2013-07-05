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
import re

from tactic_client_lib import TacticServerStub, TacticApiException


def main(args):
    # USAGE: create_project.py <project_code> <project_title> <project_type> 
    project_code = args[0]
    project_title = args[1]
    project_type = args[2]

    assert project_type in ['prod','flash','simple','unittest']
    assert project_title

    regexs = '^\d|\W'
    m = re.search(r'%s' % regexs, project_code) 
    if m:
        raise TacticApiException('<project_code> cannot contain special characters or start with a number.')

    server = TacticServerStub.get();
    # do the actual work
    server.start("Create Project", "Project creation for [%s] of type [%s]" % (project_code, project_type))
    try:
        args = {
        'project_code': project_code,
        'project_title': project_title,
        'project_type': project_type}
    
    
        
        class_name = "tactic.command.CreateProjectCmd";
        ret_val = server.execute_cmd(class_name, args=args);
        print ret_val
    except:
        server.abort()
        raise
    else:
        server.finish()



if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    if len(args) != 3:
        print "python create_project.py <project_code> <project_title> <project_type>"
        sys.exit(0)
    main(args)


