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

from pyasm.common import *
from pyasm.web import *
from pyasm.prod.biz import *

class ProdContext(Base):
    '''container that manages global production context data'''

    KEY = "ProductionContainer"

    def set_shot(shot):
        Container.put_dict(ProdContext.KEY, "shot", shot)
    set_shot = staticmethod(set_shot)

    def get_shot():
        shot = Container.get_dict(ProdContext.KEY, "shot")

        # try getting from the web form
        if shot == None:
            web = WebContainer.get_web()
            shot_id = web.get_form_value("shot_id")
            if not shot_id:
                shot_id = web.get_form_value("shot_id_nav")
            if shot_id != "":
                shot = Shot.get_by_id(shot_id)

        return shot

    get_shot = staticmethod(get_shot)










