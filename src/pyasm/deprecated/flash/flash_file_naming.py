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

__all__ = ['FlashFileNaming']

import os, re

from pyasm.biz import FileNaming, Project, Snapshot, File
from pyasm.common import TacticException

class FlashFileNaming(FileNaming):

    def add_ending(my, parts, auto_version=False):

        context = my.snapshot.get_value("context")
        version = my.snapshot.get_value("version")
        version = "v%0.3d" % version

        ext = my.get_ext()

        # it is only unique if we use both context and version
        parts.append(context)
        parts.append(version)

        filename = "_".join(parts)
        filename = "%s%s" % (filename, ext)
        # should I check if this filename is unique again?

        return filename

    # custom filename processing per sobject begins 

    def _get_unique_filename(my):
        filename = my.file_object.get_full_file_name()
        # find if this filename has been used for this project
        file = File.get_by_filename(filename, skip_id=my.file_object.get_id())
        if file:
            root, ext = os.path.splitext(filename)
            parts = [root]
            filename = my.add_ending(parts, auto_version=True)
            return filename
        else:
            return None

    def flash_nat_pause(my):
        return my._get_unique_filename()

    def flash_final_wave(my):
        return my._get_unique_filename()


