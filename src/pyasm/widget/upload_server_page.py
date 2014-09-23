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
from pyasm.biz import File
from pyasm.search import SearchType
from pyasm.web import *
from pyasm.command import FileUpload

import shutil


class UploadServerWdg(Widget):

    def get_display(my):
        web = WebContainer.get_web()

        num_files = web.get_form_value("num_files")
        files = []

        # HTML5 upload
        if num_files:
            num_files = int(num_files)
            files = []
            for i in range(0, num_files):
                field_storage = web.get_form_value("file%s" % i)
                if not field_storage:
                    continue

                file_name = web.get_form_value("file_name%s"% i)
                if not file_name:
                    file_name = my.get_file_name(field_storage)
                items = my.dump(field_storage, file_name)
                files.extend(items)


        else:
            field_storage = web.get_form_value("file")
            if field_storage:
                file_name = web.get_form_value("file_name0")
                if not file_name:
                    file_name = my.get_file_name(field_storage)

                files = my.dump(field_storage, file_name)

        if files:
            print "files: ", files
            return "file_name=%s\n" % ','.join(files)
        else:
            return "NO FILES"



    def get_file_name(my, field_storage):

        file_name = field_storage.filename

        # depending how the file is uploaded. If it's uploaded thru Python,
        # it has been JSON dumped as unicode code points, so this decode
        # step would be necessary
        try:
            file_name = file_name.decode('unicode-escape')
        except UnicodeEncodeError, e:
            pass
        except UnicodeError,e:
            pass
        file_name = file_name.replace("\\", "/")
        file_name = os.path.basename(file_name)

        # Not sure if this is really needed anymore
        #file_name = File.get_filesystem_name(file_name)

        return file_name



    def dump(my, field_storage, file_name):

        web = WebContainer.get_web()

        ticket = web.get_form_value("transaction_ticket")
        if not ticket:
            security = Environment.get_security()
            ticket = security.get_ticket_key()


        tmpdir = Environment.get_tmp_dir()
        subdir = web.get_form_value("subdir")
        if subdir:
            file_dir = "%s/%s/%s/%s" % (tmpdir, "upload", ticket, subdir)
        else:
            file_dir = "%s/%s/%s" % (tmpdir, "upload", ticket)



        # With some recent change done in cherrypy._cpreqbody line 294
        # we can use the field storage directly and just move the file
        # without using FileUpload
        path = field_storage.get_path()
        if path and file_name:
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            basename = os.path.basename(path)
            to_path = "%s/%s" % (file_dir, file_name)
            
            if os.name == 'nt':
                # windows does not do anything.. and it shouldn't even get to 
                # this point for windows.
                pass
            else:
                shutil.move(path, to_path)
                    
            # Because _cpreqbody makes use of mkstemp, the file permissions
            # are set to 600.  This switches to the permissions as defined
            # by the TACTIC users umask
            try:
                current_umask = os.umask(0)
                os.umask(current_umask)
                os.chmod(to_path, 0o666 - current_umask)
            except Exception, e:
                print "WARNING: ", e

            return [to_path]



        # This may be DEPRECATED
        #raise Exception("Upload method is DEPRECATED")



        #file_name = ''
        if field_storage == "":
            # for swfupload
            field_storage = web.get_form_value("Filedata")

            if not field_storage:
                file_name = web.get_form_value("Filename")




        # set a default for now
        action = web.get_form_value("action")
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
            upload.set_field_storage(field_storage, file_name)

        upload.set_file_dir(file_dir)

        upload.execute()
        files = upload.get_files()
        return files






