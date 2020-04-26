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


__all__ = ['SnapshotAction']


from pyasm.command import Command
from pyasm.biz import Snapshot


class SnapshotAction(Command):
    ''' a command to set values on any column in Snapshot'''
    def __init__(self):
        super(SnapshotAction, self).__init__()
        self.snap_code = None
        self.attr_name = None
        self.sobject = None
        self.value = None
        
    def get_title(self):
        return "SnapshotAction"


    def check(self):
        from pyasm.web import WebContainer
        self.web = WebContainer.get_web()
        
        # snap_code has a bunch of snapshot info delimited by |
        self.snap_codes = self.web.get_form_values('snapshot_code')
        if not self.snap_codes or self.snap_codes == ['']:
            return False
        
        self.attr_name = self.web.get_form_value('snapshot_attr')
        self.value = self.web.get_form_value('snapshot_value')
        return True

    def execute(self):
        # NONE option is used for clearing the labels
        from pyasm.widget import SelectWdg
        if self.value == SelectWdg.NONE_MODE:
            self.value = ''
        for snap_code in self.snap_codes:
            snap_code = snap_code.split('|')[0]
            snapshot = Snapshot.get_by_code(snap_code)
            
            if snapshot:
                snapshot.set_value(self.attr_name, self.value)
                snapshot.commit()
