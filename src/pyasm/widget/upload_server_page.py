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

__all__ = ['UploadServerWdg']


import os, string, sys

from pyasm.common import Environment, TacticException
from pyasm.search import SearchType
from pyasm.web import *
from pyasm.command import FileUpload


class UploadServerWdg(Widget):


    def get_display(my):
        web = WebContainer.get_web()
        ticket = web.get_form_value("transaction_ticket")
        if not ticket:
            security = Environment.get_security()
            ticket = security.get_ticket_key()

        subdir = web.get_form_value("subdir")
        #print "subdir: ", subdir

        action = web.get_form_value("action")
        field_storage = web.get_form_value("file")
        #field_storage = web.get_form_value("fileToUpload")
        file_name = ''
        if field_storage == "":
            # for swfupload
            field_storage = web.get_form_value("Filedata")

            if not field_storage:
                file_name = web.get_form_value("Filename")

        # set a default for now
        if not action:
            action = "create"


        # process and get the uploaded files
        upload = FileUpload()
        if action == "append":
            upload.set_append_mode(True)
            upload.set_create_icon(False)
        elif action == "create":
            upload.set_create_icon(False)
        elif not action:
            # this means that we are accessing from browser.
            return "Upload server"
        else:
            print("WARNING: Upload action '%s' not supported" % action)
            raise TacticException("Upload action '%s' not supported" % action)

        # set the field storage
        if field_storage:
            upload.set_field_storage(field_storage)

        # set the directory
        tmpdir = Environment.get_tmp_dir()

        if subdir:
            file_dir = "%s/%s/%s/%s" % (tmpdir, "upload", ticket, subdir)
        else:
            file_dir = "%s/%s/%s" % (tmpdir, "upload", ticket)

        #if file_name:
        #    file_path = "%s/%s" % (file_dir, file_name)
        #    upload.set_file_path(file_path)
        #else:
        #    upload.set_file_dir(file_dir)
        #print "file_dir: ", file_dir
        upload.set_file_dir(file_dir)

        upload.execute()
        files = upload.get_files()
        print "files: ", files
        return "file_name=%s\n" % ','.join(files)






