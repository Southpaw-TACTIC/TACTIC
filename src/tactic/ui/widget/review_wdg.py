###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ReviewWdg']


from tactic_client_lib import TacticServerStub
from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg, Table
from pyasm.search import Search

from pyasm.widget import IconWdg, IconButtonWdg
from visual_notes_wdg import VisualNotesWdg


class ReviewWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'search_key': 'search key of sobject this widget is working on',
    'context': 'the context of the notes'
    }

    def get_display(self):

        self.search_key = self.kwargs.get("search_key") 
        self.context = self.kwargs.get("context") 

        assert self.search_key
        assert self.context

        top = DivWdg()
        self.set_as_panel(top)
        top.add_class("spt_review_top")

        table = Table()
        top.add(table)
        table.add_row()
        left = table.add_cell()
        left.add_style("vertical-align: top")



        button = IconButtonWdg("Visual Notes", IconWdg.EDIT)
        button.add_behavior( {
        'type': 'click_up',
        'kwargs': {
            'search_key': self.search_key,
            'context': self.context,
        },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_review_top");
        var content = top.getElement(".spt_review_content");
        spt.panel.load(content, "tactic.ui.widget.visual_notes_wdg.VisualNotesWdg", bvr.kwargs);
        '''
        } )
        left.add(button)


        # add a refresh button and a gear menu
        button = IconButtonWdg("Refresh", IconWdg.REFRESH)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var panel = bvr.src_el.getParent(".spt_review_top");
        spt.panel.refresh(panel);
        '''
        } )
        left.add(button)






        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add("Image Area")


        content_div = DivWdg()
        content_div.add_class("spt_review_content")
        content_div.add_style("padding: 5px")
        content_div.add_style("margin: 5px")
        content_div.add_style("border: solid 1px #999")
        content_div.add_style("min-width: 500px")
        content_div.add_style("min-height: 400px")
        content_div.add_style("height: 100%")

        right.add(content_div)



        sobject = Search.get_by_search_key(self.search_key)

        note_context = "%s|note" % self.context
        snapshots = Search.eval("@SOBJECT(sthpw/snapshot['context','=','%s'])" % note_context, [sobject])

        vnotes_div = DivWdg()
        vnotes_div.add_style("overflow: auto")
        vnotes_div.add_style("width: 200px")
        vnotes_div.add_style("min-height: 400px")
        vnotes_div.add_style("max-height: 600px")
        vnotes_div.add_style("border: solid 1px #999")
        vnotes_div.add_style("padding: 5px")
        vnotes_div.add_style("margin: 5px")

        left.add(vnotes_div)

        if not snapshots:
            vnotes_div.add("<b>No review notes available</b>")

            notes_wdg = VisualNotesWdg(search_key=self.search_key,context=self.context)
            content_div.add(notes_wdg)



        for snapshot in snapshots:
            vnote_div = DivWdg()
            vnotes_div.add(vnote_div)

            file_obj = snapshot.get_file_by_type('main')
            if not file_obj:
                vnote_div.add("None found")
                continue

            rel_path = file_obj.get_value("relative_dir")
            file_name = file_obj.get_value("file_name")
            image_url = "/assets/%s/%s" % (rel_path, file_name)


            login = snapshot.get_value("login")
            date = snapshot.get_value("timestamp")
            import dateutil
            date_str = dateutil.parser.parse(date).strftime("%b %m %Y - %H:%M")


            login_div = DivWdg()
            login_div.add_style("padding: 2px")
            login_div.add("User: ")
            login_div.add( "<b>%s</b><br/>" % login )
            login_div.add("Date: ")
            login_div.add( "<b>%s</b><br/>" % date_str )
            vnote_div.add(login_div)



            from pyasm.widget import ThumbWdg
            thumb_div = DivWdg()
            thumb_div.add_style("margin-left: 10px")
            thumb = ThumbWdg()
            thumb_div.add(thumb)
            thumb.set_has_img_link(False)
            thumb.set_option("detail", "false")
            thumb.set_option("icon_size", "80")
            thumb.set_sobject(snapshot)
            vnote_div.add(thumb_div)
            #file_obj = snapshot.get_file_by_type('icon')
            #rel_path = file_obj.get_value("relative_dir")
            #file_name = file_obj.get_value("file_name")
            #icon_url = "/assets/%s/%s" % (rel_path, file_name)
            #vnote_div.add("<img src='%s'/>" % icon_url )

            #vnote_div.add(snapshot.get_code() )
            vnote_div.add_attr("spt_image_url", image_url )
            vnote_div.add_class('hand')

            vnote_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var value = bvr.src_el.innerHTML;
            var image_url = bvr.src_el.getAttribute("spt_image_url");

            var top = bvr.src_el.getParent(".spt_review_top");
            var content = top.getElement(".spt_review_content");
            content.innerHTML = "<img src='"+image_url+"'/>";
            '''
            } )




            # get the related note to this vnote
            #notes = vnotes_div.get_related_notes()
            search = Search("sthpw/note")
            search.add_parent_filter(sobject)
            notes = search.get_sobjects()

            #for note in notes:
            #    vnote_div.add(note.get_value("note"))

            from pyasm.biz import SObjectConnection 
            connections, related_notes = SObjectConnection.get_connected_sobjects(snapshot, direction='src')
            for related_note in related_notes:
                vnote_div.add(related_note.get_value("note") )
                
            print "related_notes: ", related_notes


            vnote_div.add("<hr/>")




        return top








