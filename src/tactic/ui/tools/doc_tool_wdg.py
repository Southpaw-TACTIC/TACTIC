###########################################################
#
# Copyright (c) 2013, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['DocToolWdg']

from pyasm.common import Xml, Environment
from pyasm.web import DivWdg, Table, HtmlElement, SpanWdg
from pyasm.search import Search, SearchType

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import ViewPanelWdg
from tactic.ui.container import ResizableTableWdg

from tactic.ui.container import Menu, MenuItem, SmartMenu, DialogWdg

import os


class DocToolWdg(BaseRefreshWdg):


    def get_diff(my, lines, lines2):
        import difflib
        d = difflib.Differ()
        result = list(d.compare(lines, lines2) )

        diff = []
        for line in result:
            if line.startswith("-"):
                line = line[2:]
                line = "<span style='background: #FCC'>%s</span>" % line
            elif line.startswith("+"):
                line = line[2:]
                line = "<span style='background: #CFC'>%s</span>" % line
            elif line.startswith("?"):
                continue
                line = line[2:]
                line = "<span style='background: #CFC'>%s</span>" % line
            else:
                line = line[2:]

            diff.append(line)


        return diff





    def get_text(my, path):


        tmp_dir = Environment.get_tmp_dir()
        last_path = "%s/last" % tmp_dir


        if path.startswith("http"):
            # NOTE: this is very specific to google docs
            if not path.endswith("?embedded=true"):
                path = "%s?embedded=true" % path

            import urllib2
            response = urllib2.urlopen(path)
            html = response.read()

            html = html.replace("&", "&amp;")
            xml = Xml()
            xml.read_string(html)

            node = xml.get_node("html/body")
            text = xml.to_string(node)
            text = text.replace("<body", "<div style='margin: 0px'")
            text = text.replace("</body>", "</div>")

            text = text.replace("&amp;", "&")


            lines2 = []
            lines = text.split("\n")
            for line in lines:
                tmp_line = line.strip()
                if tmp_line.startswith("<span"):
                    tmp_line = tmp_line.replace("<span>", "")
                    tmp_line = tmp_line.replace("</span>", "")
                    tmp_line = tmp_line.replace("<span/>", "")
                elif tmp_line.startswith("<p "):
                    continue
                elif tmp_line.startswith("</p>"):
                    continue

                tmp_line = tmp_line.replace("&nbsp;", "")
                lines2.append(tmp_line)

            text = "\n".join(lines2)


            #print 'text', text
            #import html2text
            #text = html2text.html2text(html)

            # clear out any remaining html tags
            import re
            text = re.sub('<[^<]+?>', '', text)

            #out = open(last_path, 'w')
            #out.write(text)
            #out.close()


        else:
            f = open(path)
            lines = f.readlines()
            f.close()



            #f = open(path)
            #lines2 = f.readlines()
            #f.close()

            #diff = my.get_diff(lines, lines2)
            #text = "".join(diff)

            text = "".join(lines)



        # read last text if it exists
        if os.path.exists(last_path):
            last_file = open(last_path, 'r')
            last_text = last_file.read()
            last_file.close()
        else:
            last_text = None

        if last_text != None:
            lines = text.split("\n")
            lines2 = last_text.split("\n")
            diff = my.get_diff(lines2, lines)
            diff_text = "\n".join(diff)
            text = diff_text

        search_type_obj = SearchType.get(my.search_type)
        color = search_type_obj.get_value("color")
        if not color:
            color = '#0F0'

        search = Search(my.search_type)
        sobjects = search.get_sobjects()
        for sobject in sobjects:
            search_key = sobject.get_search_key()
            value = sobject.get_value(my.column)
            if value:
                text = text.replace(value, "<i style='color: %s; font-weight: bold; opacity: 1.0;' spt_search_key='%s' class='spt_document_item hand'>%s</i>" % (color, search_key, value))



        return text


    def get_display(my):

        my.search_types = ["test3/shot", 'test3/asset']
        my.search_type = "test3/shot"
        my.column = "description"

        top = my.top
        top.add_class("spt_document_top")

        #table = Table()
        table = ResizableTableWdg()

        top.add(table)
        table.add_row()
        table.set_max_width()

        left_td = table.add_cell()
        left_td.add_style("vertical-align: top")


        title = DivWdg()
        left_td.add(title)
        title.add_style("padding: 5px")
        title.add_color("background", "background3")


        #path = "/home/apache/pdf/mongodb.txt"
        #path = "/home/apache/assets/google_docs.html"
        #path = "/home/apache/pdf/star_wars.txt"
        path = "https://docs.google.com/document/d/1AC_YR8X8wbKsshkJ1h8EjZuFIr41guvqXq3_PXgaqJ0/pub?embedded=true"

        path = "https://docs.google.com/document/d/1WPUmXYoSkR2cz0NcyM2vqQYO6OGZW8BAiDL31YEj--M/pub"

        #path = "https://docs.google.com/spreadsheet/pub?key=0Al0xl-XktnaNdExraEE4QkxVQXhaOFh1SHIxZmZMQ0E&single=true&gid=0&output=html"
        title.add(path)


        text_wdg = DivWdg()
        text_wdg.add_class("spt_document_content")
        left_td.add(text_wdg)

        if path.startswith("https://docs.google.com/spreadsheet"):
            #path = "http://www.southpawtech.com.com"
            text_wdg.add('''
            <iframe class="spt_document_iframe" style="width: 100%%; height: auto; min-height: 600px; font-size: 1.0em" src="%s"></iframe>
            ''' % path)
            text_wdg.add_style("overflow-x: hidden")
        else:
            text = my.get_text(path)

            pre = HtmlElement.pre()
            #pre = DivWdg()
            pre.add_style("width: 600x")
            pre.add_style("white-space: pre-wrap")
            pre.add(text)
            text_wdg.add(pre)
            text_wdg.add_style("padding: 20px")
            text_wdg.add_style("max-height: 600px")
            text_wdg.add_style("overflow-y: auto")

            #from tactic.ui.app import AceEditorWdg
            #editor = AceEditorWdg(code=text, show_options=False, readonly=True, height="600px")
             #text_wdg.add(editor)



        # add a click on spt_item
        text_wdg.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_document_item',
            'search_type': my.search_type,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_document_top");
            var data_el = top.getElement(".spt_document_data");

            var search_key = bvr.src_el.getAttribute("spt_search_key");

            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var kwargs = {
                'search_type': bvr.search_type,
                'search_key': search_key,
            }
            spt.panel.load(data_el, class_name, kwargs);
            '''
        } )


        # add a double click on spt_item
        bgcolor = text_wdg.get_color("background", -10)
        text_wdg.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_document_item',
            'search_type': my.search_type,
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            //bvr.src_el.setStyle("font-weight", "normal");
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )

        # add a double click on spt_item
        text_wdg.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_document_item',
            'search_type': my.search_type,
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            //bvr.src_el.setStyle("font-weight", "bold");
            bvr.src_el.setStyle("background", "");
            '''
        } )






        # add a context menu
        ctx_menu = my.get_text_context_menu()
        menus_in = {
            'TEXT_CTX': ctx_menu,
        }
        SmartMenu.attach_smart_context_menu( text_wdg, menus_in, False )

        SmartMenu.assign_as_local_activator( text_wdg, 'TEXT_CTX' )


        panel = ViewPanelWdg(
                search_type=my.search_type,
                layout="blah"
        )


        right_td = table.add_cell()
        right_td.add_style("vertical-align: top")

        panel_div = DivWdg()
        panel_div.add_class("spt_document_data")
        right_td.add(panel_div)
        panel_div.add(panel)


        text_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': r'''

spt.document = {};

spt.document.selected_text = null;

spt.document.get_selected_text = function(frame)
{

    var t = '';

    if (frame) {
        var rng = frame.contentWindow.getSelection().getRangeAt(0);
        spt.document.expandtoword(rng);
        t = rng.toString();
    }

    else if (window.getSelection) // FF4 with one tab open?
    {
        var rng = window.getSelection().getRangeAt(0);
        spt.document.expandtoword(rng);
        t = rng.toString();
    }
    else if (document.getSelection) // FF4 with multiple tabs open?
    {
        var rng = document.getSelection().getRangeAt(0);
        spt.document.expandtoword(rng);
        t = rng.toString();
    }
    else if (document.selection) // IE8
    {
        var rng = document.selection.createRange();
        // expand range to enclose any word partially enclosed in it
        rng.expand("word");
        t = rng.text;
    }

    // convert newline chars to spaces, collapse whitespace, and trim non-word chars
    return t.replace(/^\W+|\W+$/g, '');
    //return t.replace(/\r?\n/g, " ").replace(/\s+/g, " ").replace(/^\W+|\W+$/g, '');
}

// expand FF range to enclose any word partially enclosed in it
spt.document.expandtoword = function(range)
{
    if (range.collapsed)
    {
        return;
    }

    while (range.startOffset > 0 && range.toString()[0].match(/\w/))
    {
        range.setStart(range.startContainer, range.startOffset - 1);
    }

    while (range.endOffset < range.endContainer.length && range.toString()[range.toString().length - 1].match(/\w/))
    {
        range.setEnd(range.endContainer, range.endOffset + 1);
    }
}
            '''
        } )

        top.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_document_content',
            'cbjs_action': r'''
            //spt.ace_editor.set_editor_top(bvr.src_el);
            //var text = spt.ace_editor.get_selection();
            var text = spt.document.get_selected_text();
            spt.document.selected_text = text + "";
            '''
        } )




        return top


    def get_text_context_menu(my):

        search_type_obj = SearchType.get(my.search_type)
        title = search_type_obj.get_title()


        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)



        label = 'Create New "%s"' % title
        menu_item = MenuItem(type='action', label=label)
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'search_type': my.search_type,
            'column': my.column,
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);

            var selection = spt.document.selected_text;
            if (!selection) {
                alert("Nothing selected");
                return;
            }

            spt.app_busy.show("Adding " + bvr.search_type);


            var data = {}
            data[bvr.column] = selection;

            var server = TacticServerStub.get();
            server.insert(bvr.search_type, data);

            spt.app_busy.hide();
            '''
        } )


        label = '%s (Detail)' % label
        menu_item = MenuItem(type='action', label=label)
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'search_type': my.search_type,
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);

            var selection = spt.document.selected_text;
            if (!selection) {
                alert("Nothing selected");
                return;
            }

            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_type: bvr.search_type,
                default: {
                  description: selection
                }
            }


            spt.panel.load_popup("Add", class_name, kwargs);
            '''
        } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Search')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'search_type': my.search_type,
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var selection = spt.document.selected_text;
            if (!selection) {
                alert("Nothing selected");
                return;
            }

            var top = activator.getParent(".spt_document_top");
            var data_el = top.getElement(".spt_document_data");

            spt.app_busy.show("Searching " + selection);

            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var kwargs = {
                'search_type': bvr.search_type,
                'keywords': selection,
                'simple_search_view': 'simple_filter',
            }
            spt.panel.load(data_el, class_name, kwargs);



            spt.app_busy.hide();
            '''
        } )



        return menu


