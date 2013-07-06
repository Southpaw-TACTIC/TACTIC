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
    def __init__(my):
        super(SnapshotAction, my).__init__()
        my.snap_code = None
        my.attr_name = None
        my.sobject = None
        my.value = None
        
    def get_title(my):
        return "SnapshotAction"


    def check(my):
        from pyasm.web import WebContainer
        my.web = WebContainer.get_web()
        
        # snap_code has a bunch of snapshot info delimited by |
        my.snap_codes = my.web.get_form_values('snapshot_code')
        if not my.snap_codes or my.snap_codes == ['']:
            return False
        
        my.attr_name = my.web.get_form_value('snapshot_attr')
        my.value = my.web.get_form_value('snapshot_value')
        return True

    def execute(my):
        # NONE option is used for clearing the labels
        from pyasm.widget import SelectWdg
        if my.value == SelectWdg.NONE_MODE:
            my.value = ''
        for snap_code in my.snap_codes:
            snap_code = snap_code.split('|')[0]
            snapshot = Snapshot.get_by_code(snap_code)
            
            if snapshot:
                snapshot.set_value(my.attr_name, my.value)
                snapshot.commit()
