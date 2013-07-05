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

__all__ = ['FlashContext']

from pyasm.common import *
from pyasm.web import *
from pyasm.flash import *

class FlashContext(Base):
    '''container that manages global production context data'''

    KEY = "FlashContainer"

    def set_shot(shot):
        Container.put_dict(FlashContext.KEY, "shot", shot)
    set_shot = staticmethod(set_shot)

    def get_shot():
        shot = Container.get_dict(FlashContext.KEY, "shot")

        # try getting from the web from
        if shot == None:
            web = WebContainer.get_web()
            shot_id = web.get_form_value("shot_id")
            if shot_id != "":
                shot = FlashShot.get_by_id(shot_id)
            else:
                shot_code = web.get_form_value("shot_code")
                shot = FlashShot.get_by_code(shot_code)

        return shot

    get_shot = staticmethod(get_shot)










