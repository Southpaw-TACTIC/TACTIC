############################################################
#
#    Copyright (c) 2012, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


__all__ = ['DeleteElementWdg']

from pyasm.widget import IconWdg

from button_wdg import ButtonElementWdg
class DeleteElementWdg(ButtonElementWdg):
    ARGS_KEYS = {
    }

    def is_editable(my):
        return False

    def preprocess(my):

        my.set_option( "icon", "DELETE" )

        # NOTE: not sure why this needs to be in kwargs and not option
        my.kwargs["cbjs_action"] = '''
        var layout = bvr.src_el.getParent(".spt_layout");
        spt.table.set_layout(layout);

        var row = bvr.src_el.getParent(".spt_table_row");
        spt.table.unselect_all_rows();
        spt.table.select_row(row);
        spt.table.delete_selected();
        '''


    def get_display(my):

        return super(DeleteElementWdg, my).get_display()


