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
from pyasm.widget import IconWdg, SelectWdg, TextWdg
from pyasm.command import Command
from pyasm.biz import Snapshot
from pyasm.checkin import FileCheckin

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import ViewPanelWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg

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





    def get_text(my, path, last_path=None, highlight=True):


        if path.startswith("http"):
            if path.startswith("https://docs.google.com/document"):
                # NOTE: this is very specific to google docs
                if not path.endswith("?embedded=true"):
                    path = "%s?embedded=true" % path
                is_html = True
            else:
                is_html = False

            import urllib2
            response = urllib2.urlopen(path)
            html = response.read()


            fix = '''<meta content="text/html; charset=UTF-8" http-equiv="content-type">'''
            html = html.replace(fix, "")
            html = html.replace("&", "&amp;")

            if is_html:

                xml = Xml()
                try:
                    xml.read_string(html)
                except:
                    my.doc_mode = "formatted"
                    html = html.replace("&amp;", "&")
                    print
                    print "WARNING: cannot parse as XML"
                    print
                    return html


                if my.doc_mode == "formatted":
                    return xml.to_string().replace("&amp;", "&")


                node = xml.get_node("html/body")
                text = xml.to_string(node)
                text = text.replace("<body", "<div style='margin: 0px'")
                text = text.replace("</body>", "</div>")

                text = text.replace("&amp;", "&")

            else:
                text = html


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

                # FIXME: there has to be a function to do this
                tmp_line = tmp_line.replace("&nbsp;", "")
                tmp_line = tmp_line.replace("&quot;", '"')
                tmp_line = tmp_line.replace("&#39;", "'")
                lines2.append(tmp_line)

            text = "\n".join(lines2)


            #print 'text', text
            #import html2text
            #text = html2text.html2text(html)

            # clear out any remaining html tags
            import re
            text = re.sub('<[^<]+?>', '', text)


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
        if last_path and os.path.exists(last_path):
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


        if highlight:
            search_type_obj = SearchType.get(my.search_type)
            color = search_type_obj.get_value("color")
            if not color:
                color = '#0F0'

            # assemble all the lines
            data = []

            search = Search(my.search_type)
            sobjects = search.get_sobjects()
            for sobject in sobjects:
                search_key = sobject.get_search_key()

                value = sobject.get_value(my.column)
                lines = value.split("\n")
                for line in lines:
                    line = line.strip()
                    data.append( [line, search_key] )
                

            for line, search_key in data:
                if not line:
                    continue

                line = line.strip()

                text = text.replace(line, "<i style='color: %s; font-weight: bold; opacity: 1.0;' spt_search_key='%s' class='spt_document_item hand'>%s</i>" % (color, search_key, line))



        return text


    def get_display(my):

        my.doc_mode = my.kwargs.get("doc_mode")
        path = my.kwargs.get("path")
        my.search_type = my.kwargs.get("search_type")

        my.last_path = None

        doc_key = my.kwargs.get("doc_key")
        if doc_key:
            my.doc = Search.get_by_search_key(doc_key)
            snapshot = Snapshot.get_latest_by_sobject(my.doc)
            if snapshot:
                my.last_path = snapshot.get_lib_path_by_type('main')

            path = my.doc.get_value("link")


        # TEST TEST TEST
        if not path:
            #path = "/home/apache/pdf/mongodb.txt"
            #path = "/home/apache/assets/google_docs.html"
            #path = "/home/apache/pdf/star_wars.txt"
            path = "https://docs.google.com/document/d/1AC_YR8X8wbKsshkJ1h8EjZuFIr41guvqXq3_PXgaqJ0/pub?embedded=true"

            path = "https://docs.google.com/document/d/1WPUmXYoSkR2cz0NcyM2vqQYO6OGZW8BAiDL31YEj--M/pub"

            #path = "https://docs.google.com/spreadsheet/pub?key=0Al0xl-XktnaNdExraEE4QkxVQXhaOFh1SHIxZmZMQ0E&single=true&gid=0&output=html"
            path = "/home/apache/tactic/doc/alias.json"

        if not my.search_type:
            my.search_type = "test3/shot"


        my.column = "description"

        top = my.top
        top.add_class("spt_document_top")
        my.set_as_panel(top)

        #table = Table()
        table = ResizableTableWdg()

        top.add(table)
        table.add_row()
        table.set_max_width()

        left_td = table.add_cell()
        left_td.add_style("vertical-align: top")


        title = DivWdg()
        left_td.add(title)
        title.add_style("padding: 10px")
        title.add_color("background", "background3")

        button = IconButtonWdg(title="Refresh", icon=IconWdg.REFRESH)
        title.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Reloading Document");
            var top = bvr.src_el.getParent(".spt_document_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )
        button.add_style("float: left")


        button = IconButtonWdg(title="Save", icon=IconWdg.SAVE)
        title.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            '''
        } )
        button.add_style("float: left")


        if not my.doc_mode:
            my.doc_mode = "text"
        select = SelectWdg("doc_mode")
        select.set_option("values", "text|formatted")
        title.add(select)
        select.set_value(my.doc_mode)
        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            spt.app_busy.show("Reloading Document");
            var top = bvr.src_el.getParent(".spt_document_top");
            var value = bvr.src_el.value;
            top.setAttribute("spt_doc_mode", value);
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )


        title.add("<br clear='all'/>")

        #title.add(path)


        text_wdg = DivWdg()
        text_wdg.add_class("spt_document_content")
        left_td.add(text_wdg)

        #if path.startswith("https://docs.google.com/spreadsheet"):
        #    #path = "http://www.southpawtech.com.com"
        #    text_wdg.add('''
        #    <iframe class="spt_document_iframe" style="width: 100%%; height: auto; min-height: 600px; font-size: 1.0em" src="%s"></iframe>
        #    ''' % path)
        #    text_wdg.add_style("overflow-x: hidden")
        if True:

            if not my.last_path and my.doc:
                tmp_dir = Environment.get_tmp_dir()
                tmp_path = '%s/last_path.txt' % tmp_dir
                f = open(tmp_path, 'w')

                text = my.get_text(path, highlight=False)

                f.write(text)
                f.close()

                cmd = FileCheckin(my.doc, tmp_path)
                Command.execute_cmd(cmd)

            else:
                save = False
                if save:
                    # open up the last path
                    f = open(my.last_path, 'r')
                    last_text = f.read()
                    text = my.get_text(path, None, highlight=False)

                    if last_text != text:

                        tmp_dir = Environment.get_tmp_dir()
                        tmp_path = '%s/last_path.txt' % tmp_dir
                        f = open(tmp_path, 'w')
                        f.write(text)
                        f.write(text)
                        f.close()

                        cmd = FileCheckin(my.doc, tmp_path)
                        Command.execute_cmd(cmd)

                text = my.get_text(path, my.last_path)


            lines = text.split("\n") 

            if my.doc_mode == "text":

                num_lines = len(lines)

                """
                line_div = HtmlElement.pre()
                text_wdg.add(line_div)
                line_div.add_style("width: 20px")
                line_div.add_style("float: left")
                line_div.add_style("text-align: right")
                line_div.add_style("opacity: 0.3")
                line_div.add_style("padding-right: 10px")
                for i in range(0, num_lines*2):
                    line_div.add(i+1)
                    line_div.add("<br/>")
                """



            if my.doc_mode == "text":
                pre = HtmlElement.pre()
                pre.add_style("white-space: pre-wrap")
            else:
                pre = DivWdg()
            pre = DivWdg()
            text_wdg.add(pre)

            text_wdg.add_style("padding: 10px 5px")
            text_wdg.add_style("max-height: 600px")
            text_wdg.add_style("overflow-y: auto")
            text_wdg.add_style("width: 600px")
            text_wdg.add_class("spt_resizable")


            pre.add_style("font-family: courier")


            if my.doc_mode == "formatted":
                pre.add(text)

            else:
                line_table = Table()
                pre.add(line_table)
                line_table.add_style("width: 100%")
                count = 1
                for line in lines:
                    #line = line.replace(" ", "&nbsp;")
                    tr = line_table.add_row()
                    if count % 2 == 0:
                        tr.add_color("background", "background", -2)

                    td = line_table.add_cell()

                    # FIXME: hacky
                    if line.startswith('''<span style='background: #CFC'>'''):
                        is_new = True
                    else:
                        td.add_style("vertical-align: top")
                        text = TextWdg()
                        text.add_style("border", "none")
                        text.add_style("text-align", "right")
                        text.add_style("width", "25px")
                        text.add_style("margin", "0 10 0 0")
                        text.add_style("opacity", "0.5")
                        text.set_value(count)
                        td.add(text)
                        count += 1
                        is_new = False

                    td = line_table.add_cell()
                    if not is_new:
                        SmartMenu.assign_as_local_activator( td,'TEXT_CTX' )
                        tr.add_class("spt_line");
                    else:
                        SmartMenu.assign_as_local_activator( td,'TEXT_NEW_CTX' )
                        tr.add_class("spt_new_line");

                    td.add_class("spt_line_content");
                    td.add(line)




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
        ctx_new_menu = my.get_text_new_context_menu()
        menus_in = {
            'TEXT_CTX': ctx_menu,
            'TEXT_NEW_CTX': ctx_new_menu,
        }
        SmartMenu.attach_smart_context_menu( text_wdg, menus_in, False )



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
    if (range.collapsed) {
        return;
    }

    while (range.startOffset > 0 && range.toString()[0].match(/\w/)) {
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
            text = text.replace(/\n\n/mg, "\n");
            text = text.replace(/\n\n/mg, "\n");
            spt.document.selected_text = text + "";
            '''
        } )




        return top


    def get_text_new_context_menu(my):

        search_type_obj = SearchType.get(my.search_type)
        title = search_type_obj.get_title()


        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label="Update line")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var line_el = activator.getParent(".spt_new_line");
            var prev_line_el = line_el.getPrevious(".spt_line");
            prev_line_el.setStyle("border", "solid 1px red");

            var content = prev_line_el.getElement(".spt_line_content");
            alert(content.innerHTML);



            var prev_line_el = prev_line_el.getPrevious(".spt_line");
            prev_line_el.setStyle("border", "solid 1px red");

            var next_line_el = line_el.getNext(".spt_line");
            next_line_el.setStyle("border", "solid 1px red");

            var next_line_el = next_line_el.getNext(".spt_line");
            next_line_el.setStyle("border", "solid 1px red");
            '''
        } )

        return menu


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


