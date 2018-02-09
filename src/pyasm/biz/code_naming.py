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

__all__ = ["CodeNaming"]

import re
from pyasm.common import TacticException

class CodeNaming:

    def __init__(self, sobject, code):
        self.sobject = sobject
        self.code = code

        self.matches = None

        search_type = self.sobject.get_search_type_obj().get_base_key()
        func_name = search_type.replace("/", "_")

        try:
            func = "self.%s(self.code)" % func_name
            self.matches = eval( func )
        except AttributeError, e:
            print "WARNING: ", e.__str__()
            self.matches = {}



    def get_match(self, name):
        match = self.matches.get(name)
        if not match:
            raise TacticException('Failed to process this portion [%s] of the code name ' %name)

        return match


    def _match(self, pattern, code, keys):
        # get the groups
        p = re.compile(pattern)
        m = p.search(self.code)
        if not m:
            raise Exception( "Code '%s' does not match pattern" % code )
        groups = m.groups()

        # match the groups to the keys
        matches = {}
        count = 0
        for key in keys:
            matches[key] = groups[count]
            count += 1

        return matches


    def get_related_index(self):
        related = self.matches['related']
        if related:
            return int(self.matches["related"])
        else:
            return 1





