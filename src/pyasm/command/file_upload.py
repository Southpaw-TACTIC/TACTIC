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
    def __init__(self):
        self.field_storage = None
        self.file_name = None
        self.file_path = None
        self.file_dir = None

        # full paths to all of the files
        self.files = []

        self.file_types = []
        #self.tmp_dir = "%s/%s" % (Environment.get_tmp_dir(), "upload")
        self.tmp_dir = Environment.get_upload_dir()

        self.write_mode = "wb"
        self.create_icon = True
        self.default_type = 'main'
  
        self.base_decode = None

    def set_append_mode(self, flag):
        if flag:
            self.write_mode = "ab"
        else:
            self.write_mode = "wb"

    # DEPRECATED: use set_create_icon
    def set_create_icon_flag(self, flag):
        self.create_icon = flag

    def set_create_icon(self, flag):
        self.create_icon = flag


    def set_field_storage(self, field_storage, file_name=None):
        '''set the field storage taken from the web adapter'''
        self.field_storage = field_storage
        # if a particular file_name is given with the field_storage
        self.file_name = file_name

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_file_dir(self, file_dir):
        self.file_dir = file_dir

    def set_default_type(self, type):
        self.default_type = type

    def set_decode(self, decode):
        self.base_decode = decode
    
    def get_file_path(self):
        if self.file_path:
            return File.process_file_path(self.file_path)

        elif self.file_dir:
            if self.file_name:
                filename = self.file_name
            else:
                filename = self.field_storage.filename
            
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
            return "%s/%s" % (self.file_dir, Common.get_filesystem_name(basename))
            #return "%s/%s" % (self.file_dir, File.process_file_path(basename) )

        elif self.field_storage != None:
            if self.file_name:
                filename = self.file_name
            else:
                filename = self.field_storage.filename
            if filename == "":
                return None
            filename = filename.replace("\\", "/")
            basename = os.path.basename(filename)
            # File.process_file_path() should be deprecated
            return "%s/%s" % (self.tmp_dir,  Common.get_filesystem_name(basename))
            #return "%s/%s" % (self.tmp_dir, File.process_file_path(basename) )
        else:
            raise FileUploadException("No file defined")



    def get_files(self):
        '''gets all of the resulting files'''
        return self.files

    def get_file_types(self):
        return self.file_types



    def execute(self):
        '''main function that does all the work based on the set
        parameters'''
        if self.field_storage == None:
            raise FileUploadException("Field storage is None")


        self._dump_file_to_temp()

        file_path = self.get_file_path()

        if not file_path:
            return

        self._add_file(self.default_type, file_path)

        # create icons
        if self.create_icon:
            icon_creator = IconCreator(file_path)
            icon_creator.create_icons()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()

            if web_path:
                self._add_file("web", web_path)

            if icon_path:
                self._add_file("icon", icon_path)



    def _add_file(self, type, file_path):
        self.file_types.append( type )
        self.files.append( file_path )



    def _dump_file_to_temp(self):

        # Create the temporary file name
        tmp_file_path = self.get_file_path()
        if not tmp_file_path:
            return

        dirname = os.path.dirname(tmp_file_path)
        if not dirname:
            return

        System().makedirs(dirname)
   
        '''
        Determine if base_decode is necessary. Either base_decode
        is set self upload_server_page on create mode, or 
        an action file has been created to indicate decode is necessary.
        example decode_action_path
            /home/tactic/tactic_temp/upload/
            XX-dev-2924f964921857bf239acef4f9bcf3bf/miso_ramen.jpg.action
        '''
        decode_action_path = "%s.action" % tmp_file_path
        
        # Clear action file from previous any previous base64 upload
        if self.write_mode == "wb" and os.path.exists(decode_action_path):
            os.remove(decode_action_path)
        
        base_decode = self.base_decode
        if self.write_mode == "ab":
            # Check for base_decode indicator file
            if os.path.exists(decode_action_path):
                base_decode = True
        elif base_decode:
            # Create indicator file if base_decode is necessary
            f_action = open(decode_action_path, 'w')
            f_action.write("base64decode")
            f_action.close()

        # Get temporary file path to read from
        # Linux uses mkstemp, while Windows uses TemporaryFile
        if os.name == 'nt':
            data = self.field_storage.file
        else:
            path = self.field_storage.get_path()
            data = open(path, 'rb')

        # Write file to tmp directory
        f = open("%s" % tmp_file_path, self.write_mode)
       
        # Use base 64 decode if necessary.
        import base64
        if base_decode and self.write_mode == "wb":
            header = data.read(10)
            while 1:
                char = data.read(1)
                header = "%s%s" % (header, char)
                if header.endswith(";base64,"):
                    break
                if len(header) > 100:
                    raise Exception("This is not a Base64 encoded file")

        # Write progress file
        f_progress = None
        file_progress_path = "%s_progress" % tmp_file_path

        if base_decode and not tmp_file_path.endswith(".png"):
            buffer = data.read()
            length = len(buffer)
            buffer = base64.b64decode(buffer)
            f.write( buffer )

            #f_progress = open(file_progress_path, 'w')
            #f_progress.write(str(length))
            #f_progress.flush()

        else:

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




