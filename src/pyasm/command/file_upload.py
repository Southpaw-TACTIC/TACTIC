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

__all__ = ["FileUpload", "FileUploadException"]

import os

from pyasm.common import *
from pyasm.biz import *

 
class FileUploadException(TacticException):
    pass


class FileUpload(Base):
    '''utility class that handles a single file upload'''
    def __init__(my):
        my.field_storage = None
        my.file_name = None
        my.file_path = None
        my.file_dir = None

        # full paths to all of the files
        my.files = []

        my.file_types = []
        #my.tmp_dir = "%s/%s" % (Environment.get_tmp_dir(), "upload")
        my.tmp_dir = Environment.get_upload_dir()

        my.write_mode = "wb"
        my.create_icon = True
        my.default_type = 'main'
   
    def set_append_mode(my, flag):
        if flag:
            my.write_mode = "ab"
        else:
            my.write_mode = "wb"

    # DEPRECATED: use set_create_icon
    def set_create_icon_flag(my, flag):
        my.create_icon = flag

    def set_create_icon(my, flag):
        my.create_icon = flag


    def set_field_storage(my, field_storage, file_name=None):
        '''set the field storage taken from the web adapter'''
        my.field_storage = field_storage
        # if a particular file_name is given with the field_storage
        my.file_name = file_name

    def set_file_path(my, file_path):
        my.file_path = file_path

    def set_file_dir(my, file_dir):
        my.file_dir = file_dir

    def set_default_type(my, type):
        my.default_type = type

    def get_file_path(my):
        if my.file_path:
            return File.process_file_path(my.file_path)

        elif my.file_dir:
            if my.file_name:
                filename = my.file_name
            else:
                filename = my.field_storage.filename
            
            # depending how the file is uploaded. If it's uploaded thru Python,
            # it has been JSON dumped as unicode code points, so this decode
            # step would be necessary
            try:
                filename = filename.decode('unicode-escape')
            except UnicodeEncodeError, e:
                pass
            except UnicodeError,e:
                pass
            if filename == "":
                return None
            filename = filename.replace("\\", "/")
            
            basename = os.path.basename(filename)

            # File.process_file_path() should be deprecated
            return "%s/%s" % (my.file_dir, Common.get_filesystem_name(basename))
            #return "%s/%s" % (my.file_dir, File.process_file_path(basename) )

        elif my.field_storage != None:
            if my.file_name:
                filename = my.file_name
            else:
                filename = my.field_storage.filename
            if filename == "":
                return None
            filename = filename.replace("\\", "/")
            basename = os.path.basename(filename)
            # File.process_file_path() should be deprecated
            return "%s/%s" % (my.tmp_dir,  Common.get_filesystem_name(basename))
            #return "%s/%s" % (my.tmp_dir, File.process_file_path(basename) )
        else:
            raise FileUploadException("No file defined")



    def get_files(my):
        '''gets all of the resulting files'''
        return my.files

    def get_file_types(my):
        return my.file_types



    def execute(my):
        '''main function that does all the work based on the set
        parameters'''
        if my.field_storage == None:
            raise FileUploadException("Field storage is None")


        my._dump_file_to_temp()

        file_path = my.get_file_path()

        if not file_path:
            return

        my._add_file(my.default_type, file_path)

        # create icons
        if my.create_icon:
            icon_creator = IconCreator(file_path)
            icon_creator.create_icons()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()

            if web_path:
                my._add_file("web", web_path)

            if icon_path:
                my._add_file("icon", icon_path)



    def _add_file(my, type, file_path):
        my.file_types.append( type )
        my.files.append( file_path )



    def _dump_file_to_temp(my):

        # Create the temporary file name
        tmp_file_path = my.get_file_path()
        if not tmp_file_path:
            return

        dirname = os.path.dirname(tmp_file_path)
        if not dirname:
            return

        System().makedirs(dirname)
   
        # Get temporary file path to read from
        # Linux uses mkstemp, while Windows uses TemporaryFile
        if os.name == 'nt':
            data = my.field_storage.file
        else:
            path = my.field_storage.get_path()
            data = open(path, 'rb')

        # Write file to tmp directory
        f = open("%s" % tmp_file_path, my.write_mode)
       
        # Use base 64 decode if necessary.
        import base64
        base_decode = False
        header = data.read(22)
        if header.startswith("data:image/png;base64,"):
            base_decode = True
        else:
            data.seek(0)

        f_progress = None
        file_progress_path = "%s_progress" % tmp_file_path

        while 1:
            buffer = data.read(1024*64)
            if not buffer:
                break
            
            if base_decode: 
                buffer = base64.b64decode(buffer)
            
            f.write( buffer )
            f_progress = open(file_progress_path, 'w')
            f_progress.write(str(f.tell()))
            f_progress.flush()
        f.close()

        try:
            data.close()
        except Exception, e:
            print str(e)

        # when upload is running in append mode f_progress could be None
        if f_progress:
            f_progress.close()
            os.unlink(file_progress_path)
        elif not os.path.exists(tmp_file_path):
            raise FileUploadException('The supplied file [%s] is empty or does not exist.' %tmp_file_path)
        elif os.path.getsize(tmp_file_path) == 0:
            pass




