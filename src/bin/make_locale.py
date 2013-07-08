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

import os, sys

from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.common import Environment
from pyasm.search import Search, SearchType
from pyasm.command import Command


class AddTranslationCmd(Command):

    def set_path(my, path):
        my.path = path

    def set_language(my, language):
        my.language = language


    def execute(my):

        keys = ["#:", "msgid", "msgstr"]

        code_line = ""
        msgid = ""
        msgstr = ""

        file = open(my.path, 'r')
        for line in file.readlines():
            line = line.rstrip()
            if line.startswith("#:") and line != "#:":
                tmp, code_line = line.split(" ", 1)
                continue

            elif line.startswith("msgid"):
                tmp, msgid = line.split("msgid", 1)
                msgid = msgid.lstrip(' "')
                msgid = msgid.rstrip('"')

                if not msgid:
                    continue

                # look up the string first
                search = Search("sthpw/translation")
                search.add_filter("msgid", msgid)
                search.add_filter("language", my.language)
                translation = search.get_sobject()

                if not translation:
                    print "New: ", msgid
                    translation = SearchType.create("sthpw/translation")
                    translation.set_value("msgid", msgid)
                    translation.set_value("language", my.language)

                code_line = code_line.replace('\\','/')
                translation.set_value("line", code_line)
                translation.commit()






if __name__ == '__main__':

    args = sys.argv[1:]
    

    if len(args) != 1:
        print "Please supply a language code i.e. (ja, fr, or zh-CN)" 
        sys.exit(0)
    language = args[0]
    version_info = sys.version_info
    python_dir = "C:/Python%s%s" %(version_info[0], version_info[1])
    if os.name =='posix':
        python_dir = '/usr/lib/python%s.%s' %(version_info[0], version_info[1])
    tools_dir = "%s/Tools/i18n" % python_dir

    install_dir = Environment.get_install_dir()
    pyasm_dir = "%s/src/pyasm" % install_dir
    locale_dir = "%s/src/locale" % install_dir


    # generate the pot
    cmd = 'python %s/pygettext.py -p "%s" "%s"' % (tools_dir,locale_dir,pyasm_dir)
    print cmd
    os.system(cmd)

    # put the results into a database
    path = "%s/%s" % (locale_dir, "messages.pot")

    Batch(login_code='admin')
    Project.set_project("admin")

    cmd = AddTranslationCmd()
    cmd.set_path(path)
    cmd.set_language(language)
    Command.execute_cmd(cmd)

