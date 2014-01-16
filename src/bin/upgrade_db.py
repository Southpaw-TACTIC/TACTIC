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


import tacticenv
import sys, re, getopt, os

from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.command import Command
from pyasm.search import Search, DbContainer, SObject, Sql
from pyasm.search.upgrade import Upgrade
from pyasm.common import Container, Environment



if __name__ == '__main__':
    is_forced = False
    is_confirmed = False
    tacticversion = "2.5.0"
    project_code = None
    quiet = False


    if os.name != 'nt' and os.getuid() == 0:
        print 
        print "You should not run this as root. Run it as the Web server process's user. e.g. apache"
        print 
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "fyhp:q", ["force","yes","help","project=","quiet"])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    # process options
    for o, a in opts:
	if o in ("-y", "--yes"):
            is_confirmed = True
        if o in ("-f", "--force"):
            is_forced = True
        if o in ("-h", "--help"):
            print "python upgrade_db.py [-fy] [%s]" % tacticversion
            sys.exit(0)
        if o in ("-p", "--project"):
            project_code = a
        if o in ("-q", "--quiet"):
            quiet = True
   

    if len(args) == 0:
        # trace the version of TACTIC that houses this upgrade_db.py script
        dir = os.getcwd()
        file_path = sys.modules[__name__].__file__
        full_path = os.path.join(dir, file_path)
        pat = re.compile(r'\\|/')
        path_parts = pat.split(full_path)
        # get the last occurance of "src"
        path_parts.reverse()
        index = len(path_parts) - 1 - path_parts.index('src')
        path_parts.reverse()
        # used to be -3
        path_parts = path_parts[0:index]
        f = open('%s/VERSION' %'/'.join(path_parts), 'r')
        current_version =  f.readline().strip()
        msg = "Upgrading to version [%s]" % current_version
        if is_forced:
            msg = "Upgrading to version [%s] with force option" % current_version
        if not is_confirmed:
	    answer = raw_input(" %s. Continue (y/n): " %msg)
            if answer == "y":
                pass
            elif answer == 'n':
                sys.exit(0)
            else:
                print "Only y or n is accepted. Exiting..."
                sys.exit(0)
        version = current_version
    elif len(args) == 1:
        version = args[0]
    else:
        print "Either 1 or no argument can be accepted."


    if not version:
        version = tacticversion

    if version != Environment.get_release_version():
        
        answer = raw_input("[%s] does not match currently running TACTIC version [%s]. If it is a lower version number, it will probably not work. -f must be used to continue. For regular upgrade, you have not symlinked to the new TACTIC version. Continue (y/n): " \
                %(version, Environment.get_release_version()))
        if answer == "y":
            if not is_forced:
                print "-f option must be used in this situation. "
                sys.exit(0)
            pass
        elif answer == 'n':
            sys.exit(0)
        else:
            print "Only y or n is accepted. Exiting..."
            sys.exit(0)

    # check if some projects are already in newer version
    Batch()
    search = Search("sthpw/project")
    if project_code:
        search.add_filter("code", project_code)
    else:
        search.add_enum_order_by("type", ['sthpw','prod','flash','game','design','simple', 'unittest'])
    projects = search.get_sobjects()
    project_dict = {}
    for project in projects:
        last_version = project.get_value('last_version_update', no_exception=True)
        if last_version > version:
            project_dict[project.get_code()] = last_version

    if project_dict:
        data = []
        for key, value in project_dict.items():
            data.append('    %s --- %s' %(key, value))
        if is_confirmed:
            answer = 'y'
        else:
            answer = raw_input("Several projects are already in newer versions:\n%s\n"\
                    "These will not be upgraded unless their last_version_update is lowered. "\
                    "Continue (y/n): " %('\n'.join(data)))
                
        if answer == "y":
            pass
        elif answer == 'n':
            sys.exit(0)
        else:
            print "Only y or n is accepted. Exiting..."
            sys.exit(0)

    p = re.compile(r'\d+.\d+.\d+(.\w+)?$')
    if not p.match(version):
        print 
        print "Version pattern is invalid. Examples for version are 2.0.0 or 2.0.0.rc02. If you are just upgrading to the current version, just run: "
        print
        print "python upgrade_db.py"
        sys.exit(0)

    version.replace('.', '_')
    
    upgrade = Upgrade(version, is_forced, project_code=project_code, quiet=quiet, is_confirmed=is_confirmed)
    upgrade.execute()

    if not quiet:
        print "Upgrade to version [%s] finished." % version
    tmp_dir = Environment.get_tmp_dir()
    output_file = '%s/upgrade_output.txt' %tmp_dir
    if not quiet:
        print "Upgrade output file saved in [%s]" %output_file
    



