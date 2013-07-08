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

    def __init__(my, sobject, code):
        my.sobject = sobject
        my.code = code

        my.matches = None

        search_type = my.sobject.get_search_type_obj().get_base_key()
        func_name = search_type.replace("/", "_")

        try:
            func = "my.%s(my.code)" % func_name
            my.matches = eval( func )
        except AttributeError, e:
            print "WARNING: ", e.__str__()
            my.matches = {}



    def get_match(my, name):
        match = my.matches.get(name)
        if not match:
            raise TacticException('Failed to process this portion [%s] of the code name ' %name)

        return match


    def _match(my, pattern, code, keys):
        # get the groups
        p = re.compile(pattern)
        m = p.search(my.code)
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


    def get_related_index(my):
        related = my.matches['related']
        if related:
            return int(my.matches["related"])
        else:
            return 1





