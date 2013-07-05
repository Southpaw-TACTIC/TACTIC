###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import tacticenv

from pyasm.security import Batch
from pyasm.command import Command
from pyasm.common import TacticException
from client.tactic_client_lib import TacticServerStub

from tactic.command import ProjectTemplateCreatorCmd, ProjectTemplateInstallerCmd

import sys

def create(project_code):
    cmd = ProjectTemplateCreatorCmd(project_code=project_code)
    Command.execute_cmd(cmd)


def install(project_code, path=None, template_code=None):
    cmd = ProjectTemplateInstallerCmd(project_code=project_code, path=path, template_code=template_code)
    Command.execute_cmd(cmd)


#def check(project_code):
#    cmd = ProjectTemplateCheckCmd(project_code=project_code, prefix=project_code)
#    Command.execute_cmd(cmd)




if __name__ == '__main__':
    Batch(project_code='admin')

    from optparse import OptionParser

    parser = OptionParser(usage= "\n python create_template.py -m create <project_code>\n python create_template.py -m install -f /tmp/some_template-1.0.0.zip <project_code>\n python create_template.py -m install -t <template_project_code> <project_code>")
    parser.add_option("-f", "--file_path", dest="file_path", help="Zip file containing project template")
    parser.add_option("-m", "--mode", dest="mode", help="create or install")
    parser.add_option("-t", "--template", dest="template", help="template project to copy from")

    (options, args) = parser.parse_args()


    if len(args) == 0:
        print "Must supply a project code. Usually it's the name of the file before the version number."
        print "python create_template.py -m create -t template <project_code>"
        print "python create_template.py -m install -f /tmp/some_template-1.0.0.zip <project_code>"
        print "python create_template.py -m install -t <template_project_code> <project_code>"
        sys.exit(0)


    project_code = args[0]


    try:
        if options.mode == 'create':
            create(project_code)
        elif options.mode == 'install':
            path = options.file_path
            if path:
                server = TacticServerStub.get()
                server.upload_file(path)
            template_code = options.template
            install(project_code, path=path, template_code=template_code)
        else :
            print "Mode [%s] not support.  Must be either create or install" % options.get("mode")
            sys.exit(0)
    except TacticException, e:
        print
        print e.__str__()
        sys.exit(2)


