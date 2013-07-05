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

__all__ = ['SnapshotWdg']

from pyasm.command import Command, DatabaseAction, FileUpload
from pyasm.checkin import FileAppendCheckin
from pyasm.search import Search
from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebContainer
from pyasm.widget import SimpleUploadWdg, TextWdg, SelectWdg


class SnapshotWdg(Widget):

    def get_display(my):

        web = WebContainer.get_web()

        args = web.get_form_args()
        search_type = args.get("search_type")
        search_id = args.get("search_id")
        snapshot = Search.get_by_id(search_type, search_id)
        print "snapshot: ", snapshot, snapshot.get_code()



        div = DivWdg()
        div.add_style("padding: 20px")

        from pyasm.widget import DebugWdg
        div.add(DebugWdg())

        div.add("%s, %s" % (search_type, search_id) )

        div.add("<b>Add an files: </b>")

        # upload a single file
        upload = SimpleUploadWdg("upload")
        upload.set_option("upload_type", "arbitrary")
        upload.set_option("context", "icon")
        div.add(upload)

        # handle option for multiload (drag and drop)
        pass




        text = TextWdg("type")
        div.add(text)


        return div




   





