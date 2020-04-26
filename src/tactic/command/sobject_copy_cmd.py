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
__all__ = ['SObjectCopyCmd']

import tacticenv

from pyasm.common import Common, Xml
from pyasm.web import Widget, WebContainer, WidgetException
from pyasm.command import Command, CommandException
from pyasm.search import Search, SearchType
from pyasm.biz import Snapshot, Clipboard, Project
from pyasm.checkin import FileCheckin, CheckinException

from pyasm.search import WidgetDbConfig

import os

class SObjectCopyCmd(Command):

    def execute(self):
        sobject = self.kwargs.get("sobject")
        if sobject:
            sobjects = [sobject]

        else:

            search_key = self.kwargs.get("search_key")
            if search_key:
                search_keys = [search_key]
            else:
                search_keys = self.kwargs.get("search_keys")

            if search_keys:
                sobjects = []
                for search_key in search_keys:
                    sobject = Search.get_by_search_key(search_key)
                    sobjects.append(sobject)
            else:
                source = self.kwargs.get("source")
                if source == 'clipboard':
                    sobjects = Clipboard.get_selected()


        dst_search_type = self.kwargs.get("dst_search_type")
        if not dst_search_type:
            dst_search_type = sobjects[0].get_base_search_type()



        context = self.kwargs.get("context")
        #if not context:
        #    context = "publish"

        for sobject in sobjects:
            self.copy_sobject(sobject, dst_search_type, context)


    def copy_sobject(self, sobject, dst_search_type, context=None, checkin_mode='inplace'):

        new_sobject = SearchType.create(dst_search_type)
        search_type = SearchType.get(dst_search_type)
        columns = SearchType.get_columns(dst_search_type)

        data = sobject.get_data()
        for name, value in data.items():
            if name in ['id','pipeline_code']:
                continue

            if name not in columns:
                continue

            if not value:
                continue

            if name == "code":
                value = Common.get_next_sobject_code(sobject, 'code')
                if not value:
                    continue
            new_sobject.set_value(name, value)
        if SearchType.column_exists(dst_search_type, "project_code"):
            project_code = Project.get_project_code()
            new_sobject.set_value("project_code", project_code)
        new_sobject.commit()



        # get all of the current snapshots and file paths associated
        if not context:
            snapshots = Snapshot.get_all_current_by_sobject(sobject)
        else:
            snapshots = [Snapshot.get_current_by_sobject(sobject, context)]

        if not snapshots:
            return

        msgs = []
        for snapshot in snapshots:
            #file_paths = snapshot.get_all_lib_paths()
            file_paths_dict = snapshot.get_all_paths_dict()
            file_types = file_paths_dict.keys()
            if not file_types:
                continue

            # make sure the paths match the file_types
            file_paths = [file_paths_dict.get(x)[0] for x in file_types]

            mode = checkin_mode

            # checkin the files (inplace)
            try:
                context = snapshot.get_value('context')
                checkin = FileCheckin(new_sobject, context=context, file_paths=file_paths, file_types=file_types, mode=mode)
                checkin.execute()

                #print "done: ", context, new_sobject.get_related_sobjects("sthpw/snapshot")
            except CheckinException, e:
                msgs.append('Post-process Check-in Error for %s: %s ' %(context, e.__str__()))

        if msgs:
            self.info['error'] = msgs

        return new_sobject



class SObjectReferenceCmd(Command):

    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        if search_keys:
            sobjects = []
            for search_key in search_keys:
                sobject = Search.get_by_search_key(search_key)
                sobjects.append(sobject)
        else:
            source = self.kwargs.get("source")
            if source == 'clipboard':
                sobjects = Clipboard.get_selected()


        dst_search_type = self.kwargs.get("dst_search_type")








if __name__ == '__main__':
    from pyasm.security import Batch
    from pyasm.biz import Project
    Batch(project_code='simulation')
    cmd = SObjectCopyCmd()
    Command.execute_cmd(cmd)




