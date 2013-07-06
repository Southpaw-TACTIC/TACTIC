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


__all__= ['SnapshotCheckin','SnapshotAppendCheckin']

from file_checkin import *
from pyasm.search import Search
from checkin import CheckinException

class SnapshotCheckin(FileCheckin):
    '''simple class to checkin a snapshot without files'''
    def __init__(my, sobject, snapshot_xml, \
            context="publish", column="snapshot", snapshot_type="file", \
            description=""):

        if isinstance(sobject, basestring):
            sobject = Search.get_by_search_key(sobject)
            
        super(SnapshotCheckin,my).__init__(sobject, [], [], \
            context=context, column=column, snapshot_type=snapshot_type,\
            description=description)

        my.snapshot_xml = snapshot_xml


    def create_snapshot(my, file_paths):
        return my.snapshot_xml



    def handle_system_commands(my, files, file_objects):
        '''do nothing'''
        pass

class SnapshotAppendCheckin(FileAppendCheckin):
    '''Append a file to an existing snapshot. The first arg is the snapshot sobject instead of snapshot_code'''
    def __init__(my, sobject, file_paths, file_types, **kwargs):

        snapshot = sobject
        existing_types = snapshot.get_all_file_types()
        for file_type in file_types:
            if file_type in existing_types:
                raise CheckinException('This file type [%s] already exists'%file_type)
        snapshot_code = snapshot.get_code()

        mode = kwargs.get('mode')
        keep_file_name = kwargs.get('keep_file_name')
        if keep_file_name != True:
            keep_file_name = False

        super(SnapshotAppendCheckin,my).__init__(snapshot_code, file_paths, file_types, \
                mode=mode, keep_file_name=keep_file_name)
