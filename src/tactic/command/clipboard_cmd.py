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
__all__ = ['ClipboardAddCmd', 'ClipboardCopyCmd', 'ClipboardConnectCmd']

import tacticenv

from pyasm.common import Common, Xml
from pyasm.command import Command, CommandException
from pyasm.search import Search, SearchType
from pyasm.biz import Snapshot, Clipboard
from pyasm.checkin import FileCheckin

class ClipboardAddCmd(Command):

    def execute(self):
        search_keys = self.kwargs.get("search_keys")
        Clipboard.add_to_selected(search_keys)



class ClipboardCopyCmd(Command):

    def execute(self):
        search_keys = self.kwargs.get("search_keys")
        Clipboard.clear_selected()
        Clipboard.add_to_selected(search_keys)


class ClipboardConnectCmd(Command):

    def execute(self):
        search_keys = self.kwargs.get("search_keys")
        print "search_keys: ", search_keys
        for search_key in search_keys:
            sobject = Search.get_by_search_key(search_key)
            Clipboard.reference_selected(sobject)








