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
__all__ = ['CopyConfigCmd']

import tacticenv

from pyasm.common import Common, Xml
from pyasm.web import Widget, WebContainer, WidgetException
from pyasm.command import Command, CommandException

from pyasm.search import WidgetDbConfig


test_xml = '''
<config>
<cow>

  <element name="Test">
    <display class="SideBarSectionLinkWdg">
        <view>test</view>
    </display>
  </element>


  <element name="My TACTIC">
    <display class="SideBarSectionLinkWdg">
        <view>my_tactic</view>
    </display>
  </element>


  <element name="Preproduction">
    <display class="SideBarSectionLinkWdg">
        <view>preproduction</view>
    </display>
  </element>


  <element name="Tasks">
    <display class="SideBarSectionLinkWdg">
        <view>tasks</view>
    </display>
  </element>

</cow>
</config>
'''



class CopyConfigCmd(Command):
    #def __init__(my, **kwargs):
    #    pass


    def execute(my):
        project_type = "prod"

        # copy all of the widget configs from the prod definition and put
        # them into the database
        xml = Xml(string=test_xml)

        search_type = "SideBarWdg"
        view = "cow"
        config = WidgetDbConfig.create(search_type, view, data=xml.to_string())

        '''
        How to do this?

        We need a way of copying a view ... easy enough

        If a template is specified, start with that.  No copying.
        If changes are made, a copy is made and stored in the database.  The
            database version is now used
        What to do when upgrading and new tabs are available or have changed?
            - need some kind of diff, but we can deal with that later.


        '''



if __name__ == '__main__':
    from pyasm.security import Batch
    from pyasm.biz import Project
    Batch()
    Project.set_project("sample3d")
    cmd = CopyConfigCmd()
    Command.execute_cmd(cmd)




