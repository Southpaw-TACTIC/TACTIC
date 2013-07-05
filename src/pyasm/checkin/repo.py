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

__all__ = ["BaseRepo", "TacticRepo"]

import os, sys, re

from pyasm.common import Environment, System
from pyasm.biz import File
from pyasm.search import FileUndo
from checkin import CheckinException

class BaseRepo(object):
    '''abstract class defining repositories'''
    def has_file_codes(my):
        return True

    def handle_system_commands(my, snapshot, files, file_objects, mode, md5s, source_paths=[]):
        pass




class TacticRepo(BaseRepo):

    def handle_system_commands(my, snapshot, files, file_objects, mode, md5s, source_paths=[], file_sizes=[]):
        '''move the tmp files in the appropriate directory'''

        # if mode is local then nothing happens here
        if mode == 'local':
            return

        sobject = snapshot.get_sobject()

        # inplace mode does not move the file.  It just registers the file
        # object
        if mode == 'inplace':
            for i, file in enumerate(files):
                file_object = file_objects[i]
                to_name = file_object.get_full_file_name()
                file_type = snapshot.get_type_by_file_name(to_name)
                to_path = file

                file_object.set_value('type', file_type)
                if not os.path.isdir(to_path):
                    md5_checksum = None
                    if md5s:
                        md5_checksum = md5s[i]
                    if not md5_checksum:
                        md5_checksum = File.get_md5(to_path)

                    if md5_checksum:
                        file_object.set_value("md5", md5_checksum)

                file_object.commit(triggers=False)
                return
            
   
        for i, file in enumerate(files):

            file_object = file_objects[i]
            to_name = file_object.get_full_file_name()
            file_type = snapshot.get_type_by_file_name(to_name)

            lib_dir = snapshot.get_lib_dir(file_type=file_type, file_object=file_object)
            # it should have been created in postprocess_snapshot
            System().makedirs(lib_dir)

            to_path = "%s/%s" % (lib_dir, to_name )

            #print "path: ", i, files[i]
            #print to_path, os.path.exists(to_path)

            # first make sure that the to path does not exist, if so, just skip
            if os.path.exists(to_path) and mode not in ['inplace','preallocate']:
                raise CheckinException('This path [%s] already exists'%to_path) 


            # add the file
            try:

                # inplace undo used to not touch the file, 
                # now it will be moved to cache on undo
                io_action = True
                if mode in ['preallocate']:
                    io_action = False

                # make it look like the files was created in the repository
                if mode == 'free_move':
                    FileUndo.move( source_paths[i], to_path )
                elif mode == 'free_copy':
                    # check for directory within FileUndo.copy
                    FileUndo.copy( source_paths[i], to_path )
                else:
                    FileUndo.create( files[i], to_path, io_action=io_action )


            except IOError, e:
                raise CheckinException('IO Error occurred. %s' %e.__str__())

            # check to see that the file exists.
            if not os.path.exists( to_path ):
                if mode in ["inplace", "preallocate"]:
                    raise CheckinException("File not found in repo at [%s]" % to_path )
                else:
                    raise CheckinException("Failed move [%s] to [%s]" % \
                (files[i], to_path) )

            file_object.set_value('type', file_type)
            if not os.path.isdir(to_path):
                md5_checksum = None
                if md5s:
                    md5_checksum = md5s[i]
                if not md5_checksum:
                    md5_checksum = File.get_md5(to_path)

                if md5_checksum:
                    file_object.set_value("md5", md5_checksum)

            file_object.commit(triggers=False)
            

