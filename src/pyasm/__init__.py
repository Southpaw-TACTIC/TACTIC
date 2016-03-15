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

import tacticenv
import sys
tactic_install_dir = tacticenv.get_install_dir()

sys.path.insert(0, "%s/3rd_party/site-packages" %tactic_install_dir)
