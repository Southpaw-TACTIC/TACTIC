###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import sys
import os

import tacticenv
from pyasm.security import Batch, Login
from pyasm.search import Search, SearchType

Batch()

search = Search("sthpw/login")
search.add_filter("login", "admin")
admin = search.get_sobject()

password = Login.get_default_encrypted_password()

if not admin:
    search.set_show_retired(True)
    admin = search.get_sobject(redo=True)

if not admin:
    # create missing admin entry
    admin = SearchType.create('sthpw/login')
    admin.set_value('login','admin')

admin.set_value("password", password)
admin.commit()

print "Successfully reset admin password.  You will be prompted to change it on startup of TACTIC."
raw_input()

