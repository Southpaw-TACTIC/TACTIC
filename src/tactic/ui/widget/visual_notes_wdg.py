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


__all__ = ['VisualNotesWdg']


from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg, Table
from pyasm.biz import Snapshot
from pyasm.widget import TextAreaWdg
from pyasm.search import Search


class VisualNotesWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'search_key': 'search key of the sobject to operate on',
    'context': 'context of the snapshot to operate on'
    }

    def get_display(self):
        top = DivWdg()
        top.add_class("spt_visual_notes_top")

        self.search_key = self.kwargs.get("search_key")
        self.context = self.kwargs.get("context")
        assert self.search_key
        assert self.context


        sobject = Search.get_by_search_key(self.search_key)
        sobj_search_type = sobject.get_search_type()
        sobj_id = sobject.get_id()
        assert sobject

        snapshot = Snapshot.get_latest(sobj_search_type, sobj_id, self.context)
        if not snapshot:
            self.path = ''
            top.add("<b>No snapshot found</b>")
            return top
        else:
            files = snapshot.get_files_by_type("main")
            
            file = files[0]
            self.path = "/assets/%s/%s" % (file.get_value("relative_dir"), file.get_value("file_name") )

            #self.path = "/assets/cg/asset/chr/chr001/icon/hawaii01_web_icon_v001.jpg"


        self.note_context = self.context + '|note'


        # put in a title
        title_div = DivWdg()
        title_div.add_class("maq_search_bar")
        title_div.add("Visual Notes Editor")
        top.add(title_div)


        # add in the buttons bar
        buttons_wdg = self.get_buttons_wdg()
        top.add(buttons_wdg)




        flash_vars = "file=" + self.path;

        #'swf_url': '/assets/sthpw/widget/visual_notes_wdg/VisualNotesWdg.swf',
        kwargs = {
              'swf_url': '/context/visual_notes_wdg.swf',
              'title': 'Flash Test',
              'flash_vars': flash_vars,
              'width': '800',
              'height': '600'
        }
        #spt.panel.load('spt_flash', 'tactic.ui.panel.SwfWdg', kwargs);

        from tactic.ui.panel import SwfWdg
        swf = SwfWdg(**kwargs)
        top.add(swf)


        return top


    def get_buttons_wdg(self):
        buttons_div = DivWdg()
        buttons_div.add_style("margin-left: 20px")
        buttons_div.add_style("margin-right: 20px")


        # add brush size

        text_note_wdg = DivWdg()
        text_note_wdg.add("<b>Text Note</b>")
        buttons_div.add(text_note_wdg)


        text_note = TextAreaWdg("spt_text_note")
        text_note.add_style("width: 400px")
        text_note.add_class("spt_text_note")
        buttons_div.add(text_note)
        

        from pyasm.widget import IconButtonWdg, IconWdg
        save_button = IconButtonWdg("Export", IconWdg.SAVE)
        save_button.add_style("float: right")
        buttons_div.add(save_button)


        script = '''
        try {
          function getFlashMovie(movieName) {
              var isIE = navigator.appName.indexOf("Microsoft") != -1;
              return (isIE) ? window[movieName] : document[movieName];
          }


          spt.app_busy.show("Exporting Visual Note", " ")
         
          var data = getFlashMovie("visual_notes_wdg").visual_notes_export();

          var applet = spt.Applet.get();
          var server = TacticServerStub.get();
          //server.start();
          var search_key = bvr.kwargs.search_key;

          var txt_path = "c:/sthpw/sandbox/temp/visual_notes/visual_notes_temp.txt" 
          var jpg_path = "c:/sthpw/sandbox/temp/visual_notes/visual_notes_temp.jpg" 

          applet.create_file(txt_path, data);
          applet.decodeFileToFile(txt_path, jpg_path);

          var top_el = bvr.src_el.getParent(".spt_visual_notes_top");
          var context = bvr.kwargs.context;
          var snapshot = server.simple_checkin(search_key, context, jpg_path);

          //var note_context = context + "|note";
          var note_context = context;
          var note = top_el.getElement(".spt_text_note").value;
          var note_sobj = server.insert("sthpw/note", { note: note, context: note_context}, {parent_key: search_key} );
          server.connect_sobjects( snapshot, note_sobj);

          //server.finish("Visual Notes");      


          spt.app_busy.hide();
          alert("Visual note added for [" + context + "]");
        }
        catch(err) {
            spt.app_busy.hide();
            alert(err);
        }
        '''
        save_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': script,
        'kwargs': {
            'search_key': self.search_key,
            'context': self.note_context
        }
        })
   

        return buttons_div








