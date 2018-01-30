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

__all__ = ['SubmissionCheckin']

import os, shutil, re

from pyasm.common import *
from pyasm.checkin import *
from pyasm.biz import *
from pyasm.prod.biz import *
from pyasm.command import CommandException, Command
from pyasm.search import SearchType, Search
from pyasm.application.maya import *


class SubmissionCheckin(FileCheckin):

    def __init__(self, sobject, file_paths, file_types, context='publish', snapshot_type='submission',
             column='snapshot',description="", is_current=True, source_paths=[],
            level_type=None, level_id=None, mode=None, keep_file_name=False,
            base_dir=None, is_revision=False, md5s=[], file_sizes=[],
            dir_naming=None, file_naming=None, context_index_padding=None,
            checkin_type='strict', version=None):
        BaseCheckin.__init__(self, sobject)
        #context = "publish"

        super(SubmissionCheckin,self).__init__(sobject, file_paths, file_types, context=context, snapshot_type=snapshot_type,\
                column=column, description=description, is_current=is_current, source_paths=source_paths,
            level_type=level_type, level_id=level_id, mode=mode, keep_file_name=keep_file_name,
            base_dir=base_dir, is_revision=is_revision, md5s=md5s, file_sizes=file_sizes, dir_naming=dir_naming, 
            file_naming=file_naming, context_index_padding=context_index_padding, checkin_type=checkin_type, version=version)



    def add_dependencies(self, snapshot_xml):
        '''link to the referenced versions'''
        search_type = self.sobject.get_value("search_type")
        search_id = self.sobject.get_value("search_id")
        context = self.sobject.get_value("context")
        version = self.sobject.get_value("version")

        # Insert directly in the Review or Dailies tab
        if not search_type and not search_id:
            return
        snapshot = Snapshot.get_by_version(search_type, search_id, context, version)

        # for now, do not link up to an unknown snapshot
        if not snapshot:
            return


        xml = Xml()
        xml.read_string(snapshot_xml)
        builder = SnapshotBuilder(xml)
        builder.add_ref_by_snapshot(snapshot, type='input_ref')

        # commit it to the snapshot
        self.snapshot.set_value("snapshot", builder.to_string())       
        self.snapshot.commit()


        

