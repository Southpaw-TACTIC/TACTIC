###########################################################
#
# Copyright (c) 2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ['HelpWdg', 'HelpContentWdg', 'HelpEditWdg', 'HelpEditCbk', 'HelpEditContentWdg','HelpDocFilterWdg']

import tacticenv

from pyasm.common import Environment, Xml, TacticException, Config, Common, Container
from pyasm.web import DivWdg, Table, SpanWdg, WebContainer
from pyasm.widget import TextAreaWdg, SelectWdg, HiddenWdg, IconWdg
from pyasm.search import Search, SearchType
from pyasm.command import Command

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, SingleButtonWdg, IconButtonWdg

import types, os

__all__.append("HelpButtonWdg")
class HelpButtonWdg(BaseRefreshWdg):

    def init(my):
        my.cbjs_action = my.kwargs.get("cbjs_action")


    def add_style(my, key, value=None):
        my.top.add_style(key, value=value)

    def add_behavior(my, cbjs_action):
        my.cbjs_action = cbjs_action


    def exists():
        return Container.get("HelpWdg::exists") == True
    exists = staticmethod(exists)



    def get_display(my):

        top = my.top

        if not HelpWdg.exists():
            return top

        alias = my.kwargs.get("alias")
        description = my.kwargs.get("description")
        if not description:
            description = "Show Help"

        if my.kwargs.get("use_icon"):
            #help_button = SingleButtonWdg(title='Help', icon=IconWdg.HELP_BUTTON, show_arrow=False)
            help_button = IconButtonWdg(title='Help', icon=IconWdg.HELP_BUTTON, show_arrow=False)
        else:
            help_button = ActionButtonWdg(title="?", tip=description, size='small')
        top.add(help_button)

        if not my.cbjs_action:
            my.cbjs_action = '''
            spt.help.set_top();
            spt.help.load_alias(bvr.alias);
            '''

            help_button.add_behavior( {
                'type': 'click_up',
                'alias': alias,
                'cbjs_action': my.cbjs_action
            } )


        return top



class HelpDocFilterWdg(BaseRefreshWdg):

    def get_display(my):

        alias = my.kwargs.get("alias")

        my.rel_path = my.kwargs.get("rel_path")
        if not my.rel_path:
            from tactic_client_lib import TacticServerStub
            server = TacticServerStub.get(protocol='local')
            my.rel_path = server.get_doc_link(alias)

        if not my.rel_path or my.rel_path == 'none_found':
            #raise TacticException("Help alias [%s] does not exist" % alias)
            layout = DivWdg()
            layout.add(HelpCreateWdg(alias=alias))
            layout.add(HelpDocFilterWdg(alias='main'))
            return layout 

        # special condition for plugins path
        if my.rel_path.startswith("/plugins/"):
            plugin_dir = Environment.get_plugin_dir()
            rel_path = my.rel_path.replace("/plugins/", "")
            path = "%s/%s" % (plugin_dir,rel_path)
        elif my.rel_path.startswith("/builtin_plugins/"):
            plugin_dir = Environment.get_builtin_plugin_dir()
            rel_path = my.rel_path.replace("/builtin_plugins/", "")
            path = "%s/%s" % (plugin_dir,rel_path)
        elif my.rel_path.startswith("/assets/"):
            asset_dir = Environment.get_asset_dir()
            rel_path = my.rel_path.replace("/assets/", "")
            path = "%s/%s" % (asset_dir,rel_path)
        else:

            # see if there is an override
            doc_dir = os.environ.get("TACTIC_DOC_DIR") 
            if not doc_dir:
                doc_dir = Config.get_value("install", "doc_dir")
            if not doc_dir:
                install_dir = Environment.get_install_dir()
                doc_dir = "%s/doc" % install_dir

            path = "%s/%s" % (doc_dir, my.rel_path)

        html = []
        try:
            paths = path.split('#')
            anchor = ''
            if len(paths) > 1:
                anchor = paths[-1]
                path = paths[0]
                read = False
            else:
                read = True

            
            f = open(path, 'r')
            count = 0
            idx = 0 
            anchor_str = '<a id="%s"></a>'%anchor
            div_str = '<div class="titlepage">'
            strip_count = 0
            for line in f:
                if anchor and not read:
                    tmp_line = line.decode('utf-8','ignore')
                    div_idx = tmp_line.find(div_str)
                    idx = tmp_line.find(anchor_str)
                    if idx != -1:
                        # use the div above the anchor
                        line = line[div_idx:-1]
                        
                        # in case it doesn't get it right on
                        while strip_count < 30 and not line.startswith('<div class="titlepage">'):
                            line = line[1:-1]
                            strip_count +=  1

                        read = True
                
                if read:
                    line = my.filter_line(line, count)
                    html.append(line)
                    count += 1
            f.close()
        except Exception, e:
            print "Error processing: ", e
            html.append("Error processing document: %s<br/><br/>" % str(e))
        
        html = "\n".join(html)
        if not html:
            html = "<div/>"


        # let custom layout parse this first
        from tactic.ui.panel import CustomLayoutWdg
        rel_dir = os.path.dirname(my.rel_path)

        # TODO: this is only used to try to get images into plugin dogs
        # It breaks a lot of docs that have Mako examples
        #layout = CustomLayoutWdg(html=html, base_dir=rel_dir)
        #html = layout.get_buffer_display()

        
        tree = Xml.parse_html(html)
        
        xml = Xml(doc=tree)

        elements = my.filter_xml(xml)


        # generate the html
        top = my.top
        top.add_class("spt_help_top")
        top.add_style("min-width: 300px")
        top.add_style("min-height: 100px")
        top.add_color("background", "background")
        top.add_style("padding: 10px")
        top.add_style("font-size: 12px")
        top.add_class("spt_resizable")




        inner = DivWdg()
        top.add(inner)


        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var els = bvr.src_el.getElements(".spt_replace_element");
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                var replace_id = el.getAttribute("spt_replace_id");
                var el_old = $(replace_id);
                if (el_old) {
                    el.replaces(el_old);

                    var children = el_old.getChildren();
                    for (var j = 0; j < children.length; j++) {
                        el.appendChild(children[j]);
                    }
                }

            }
            '''
        } )

        inner.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_link',
            'cbjs_action': 'spt.mouse.table_layout_hover_over({}, {src_el: bvr.src_el, add_color_modifier: -5})'
        } )
        inner.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_link',
            'cbjs_action': 'spt.mouse.table_layout_hover_out({}, {src_el: bvr.src_el})'
        } )




        #node = xml.get_node("//body")
        #html = xml.to_string(node)
        ##print html
        #inner.add(html)

        nodes = xml.get_nodes("//body/*")
        for node in nodes:
            html = xml.to_string(node)
            html = html.replace("&lt;", "&spt_lt;")
            html = html.replace("&gt;", "&spt_gt;")
            inner.add(html)

        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var text = bvr.src_el.innerHTML;
            text = text.replace(/amp\;/g, "");
            spt.behavior.replace_inner_html(bvr.src_el, text);
            '''
        } )

        # add replacement html
        div = DivWdg()
        inner.add(div)
        div.add_class("spt_replacement")
        for element in elements:
            div.add(element)

        rel_path_div = DivWdg()
        rel_path_div.add("<i>Source: %s</i>" % my.rel_path)
        inner.add(rel_path_div)
        rel_path_div.add_style("opacity: 0.3")
        rel_path_div.add_style("margin-top: 10")


        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return top



    def filter_line(my, line, count):

        line = line.strip()
        if line.startswith("<meta"):
            line = line.replace(">", "/>")
        elif line.startswith("<link"):
            line = line.replace(">", "/>")
        elif line.find("<a ") != -1:
            import re
            p = re.compile("<a name.*?></>")
            p2 = re.compile("<a id.*?></a>")
            line = re.sub(p, "", line)
            line = re.sub(p2, "", line)

        line = line.replace("&nbsp;", " ")
        line = line.replace("<hr>", "<hr/>")
        line = line.replace("<br>", "<br/>")

        return line


    def add_shadow(my, styles, value, color):
        browser = WebContainer.get_web().get_browser()
        if browser == 'Mozilla':
            styles.append("-moz-box-shadow: %s %s" % (value, color))
            styles.append("box-shadow: %s %s" % (value, color))
        elif browser == 'Webkit':
            styles.append("-webkit-box-shadow: %s %s" % (value, color))
            styles.append("box-shadow: %s %s" % (value, color))
        else:
            styles.append("box-shadow: %s %s" % (value, color))



    def filter_xml(my, xml):
        dirname = os.path.dirname(my.rel_path)


        # filter images
        img_nodes = xml.get_nodes("//img")
        install_dir = Environment.get_install_dir()
        for node in img_nodes:
            src = xml.get_attribute(node, "src")

            if src.startswith("/tactic/plugins/"):
                plugin_dir = Environment.get_plugin_dir()
                path = "%s/%s" % (plugin_dir, src.replace("/tactic/plugins/", "") )
            elif src.startswith("/tactic/builtin_plugins/"):
                plugin_dir = Environment.get_builtin_plugin_dir()
                path = "%s/%s" % (plugin_dir, src.replace("/tactic/builtin_plugins/", "") )



            elif src.startswith("/"):
                path = "%s/src%s" % (install_dir, src)
            else:
                path = "%s/doc/%s/%s" % (install_dir, dirname, src)

            size = (0,0)
            try:
                from PIL import Image 
                im = Image.open(path)
                size = im.size
            except IOError, e:
                print "Error importing Image: ", e
                
            except:
                print "Error in opening image path:", path
                #continue
                size = [0,0]

            style = xml.get_attribute(node, "style")
            if style:
                styles = style.split(";")
            else:
                styles = []

            shadow = "rgba(0,0,0,0.4)"
            if size[0] > 500:
                styles.append("width: 75%")
                styles.append("margin-left: 50px")
                styles.append("margin-bottom: 20px")
                styles.append("margin-top: 10px")
                my.add_shadow(styles, "0px 0px 5px", shadow)

            elif size[0] > 100:
                x = int(float(size[0])/500*75)
                styles.append("width: %s%%"%x)
                styles.append("margin-left: 50px")
                styles.append("margin-bottom: 20px")
                styles.append("margin-top: 10px")
                my.add_shadow(styles, "0px 0px 5px", shadow)

            else:
                my.add_shadow(styles, "0px 0px 5px", shadow)

            styles.append("border: solid 1px rgba(0,0,0,0.3)")
            style = ";".join(styles)
            xml.set_attribute(node, "style", style)


            if src.startswith("/"):
                new_src = src
            elif dirname:
                new_src = "/doc/%s/%s" % (dirname, src)
            else:
                new_src = "/doc/%s" % (src)

            #print "src: ", src
            #print "new_src: ", new_src
            #print "---"
            xml.set_attribute(node, "src", new_src)



        # filter links
        elements = []
        link_nodes = xml.get_nodes("//a")
        for node in link_nodes:

            href = xml.get_attribute(node, "href")

            if not href:
                # Test link to GitHub docs
                """
                # add a link to github
                github_node = xml.create_text_element("div", "edit >>")
                xml.insert_after(github_node, node)
                xml.set_attribute(github_node, "style", "float: right; font-size: 0.8em; opacity: 0.3")
                xml.set_attribute(github_node, "class", "hand")
                url = '''https://github.com/Southpaw-TACTIC/Docs/tree/master/section/doc/tactic-end-user/end-user/creating-tasks'''
                xml.set_attribute(github_node, "onclick", "window.open('%s', 'TACTIC Docs')" % url)
                """

                continue



            if dirname:
                link_rel_path = "%s/%s" % (dirname, href)
            else:
                link_rel_path = "%s" % (href)
 
            target = xml.get_attribute(node, "target")
            if target:
                target = xml.set_attribute(node, "href", "/doc/%s" % link_rel_path)
                continue

            # get a unique id for the node
            unique_id = my.top.generate_unique_id(base='replace')
            xml.set_attribute(node, "id", unique_id)

            div = SpanWdg()
            elements.append(div)
            div.add_class("spt_replace_element")
            div.add_attr("spt_replace_id", unique_id)
            div.add_class("hand")
            div.add_class("spt_link")
            div.add_color("background", "background")

            text = xml.get_node_value(node)
            div.add(text)
            div.add_behavior( {
                'type': 'click_up',
                'rel_path': link_rel_path,
                'cbjs_action': '''
                spt.help.set_top();
                spt.help.load_rel_path( bvr.rel_path );
                '''
            } )


        # dummy div to get color
        div = DivWdg()

        # convert pre-elements to have &lt; and &gt;
        pre_nodes = xml.get_nodes("//pre")
        for node in pre_nodes:
            html = xml.to_string(node)
            html = html.replace('''<pre class="screen">''','')
            html = html.replace('''</pre>''','')
            if not html:
                continue
                
            styles = []
            styles.append("padding: 10px")
            styles.append("margin: 10px")
            styles.append("border: solid 1px %s" % div.get_color("border"))
            styles.append("background: %s" % div.get_color("background", -3))
            style = ";".join(styles)
            xml.set_attribute(node, "style", style)
            node.text = html


        # style the table nodes
        table_nodes = xml.get_nodes("//table")
        for node in table_nodes:
            styles = []
            #styles.append("border: solid 1px %s" % div.get_color("border"))
            styles.append("background: %s" % div.get_color("background", -1))
            style = ";".join(styles)
            xml.set_attribute(node, "style", style)
            xml.set_attribute(node, "cellpadding", "10")
            xml.set_attribute(node, "cellspacing", "0")
            xml.set_attribute(node, "border", "0")




        return elements



class HelpWdg(BaseRefreshWdg):

    def init(my):
        Container.put("HelpWdg::exists", True)
        my.show_add_new = my.kwargs.get('show_add_new') not in  ['false', False]

    def exists():
        return Container.get("HelpWdg::exists") == True
    exists = staticmethod(exists)


    def get_display(my):

        top = my.top

        #help_div = DivWdg()
        help_div = top
        #top.add(help_div)
        help_div.add_class("spt_help_top")
        help_div.set_id("spt_help_top")

        show_title = my.kwargs.get("show_title")
        if show_title in [True, 'true']:
            show_title = True
        else:
            show_title = False

        if show_title:
            title_wdg = DivWdg()
            help_div.add(title_wdg)
            title_wdg.add_style("font-size: 12px")
            title_wdg.add_style("font-weight: bold")
            title_wdg.add_color("background", "background", -10)
            title_wdg.add_style("padding: 3px")
            #title_wdg.add_style("margin-top: 8px")
            title_wdg.add_style("margin-bottom: 5px")
            title_wdg.add_style("height: 26px")
            title_wdg.add_style("padding: 6 0 0 6")
            title_wdg.set_round_corners(corners=['TL','TR'])

            icon = IconWdg("Close", IconWdg.KILL)
            title_wdg.add(icon)
            icon.add_style("float: right")
            title_wdg.add("Help")



        help_div.set_round_corners()
        help_div.add_color("color", "color2")
        help_div.add_color("background", "background")
        help_div.add_style("overflow: hidden")
        help_div.add_border()



        shelf_div = DivWdg()
        help_div.add(shelf_div)
        shelf_div.add_style("padding: 10px")
        shelf_div.add_color("background", "background", -10)
        shelf_div.add_style("height: 25px")


        #button = SingleButtonWdg(title="Documentation Main Page", icon=IconWdg.HOME)
        button = IconButtonWdg(title="Documentation Main Page", icon="BS_HOME")
        shelf_div.add(button)
        button.add_style("float: left")
        button.add_style("margin: 0px 10px")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.help.set_top();
        spt.help.load_alias("main")
        '''
        } )




        #button = SingleButtonWdg(title="Edit Help", icon=IconWdg.EDIT)
        if my.show_add_new:
            button = IconButtonWdg(title="Add New Help", icon="BS_EDIT")
            shelf_div.add(button)
            button.add_style("float: left")
            button.add_style("margin: 0px 10px")
            button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.app.HelpEditWdg';

            var element_name = spt.help.get_view();
            if (!element_name) {
              element_name = "default";
            }
            var kwargs = {
              view: element_name
            }

            spt.tab.add_new("help_edit", "Help Edit", class_name, kwargs);
                
            '''
            } )



        #button = SingleButtonWdg(title="Go Back One Page", icon=IconWdg.ARROW_LEFT)
        button = IconButtonWdg(title="Go Back One Page", icon="BS_CIRCLE_ARROW_LEFT")
        shelf_div.add(button)
        button.add_style("float: left")
        button.add_style("margin: 0px 10px")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.help.set_top();
        spt.help.load_prev();
        '''
        } )

        #button = SingleButtonWdg(title="Go Forward One Page", icon=IconWdg.ARROW_RIGHT)
        button = IconButtonWdg(title="Go Forward One Page", icon="BS_CIRCLE_ARROW_RIGHT")
        shelf_div.add(button)
        button.add_style("float: left")
        button.add_style("margin: 0px 10px")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.help.set_top();
        spt.help.load_next();
        '''
        } )



        #button = SingleButtonWdg(title="Documentation Downloads", icon=IconWdg.DOWNLOAD)
        button = IconButtonWdg(title="Documentation Downloads", icon="BS_DOWNLOAD")
        shelf_div.add(button)
        button.add_style("float: right")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.help.set_top();
        spt.help.load_alias("pdf")
        '''
        } )


        shelf_div.add("<br clear='all'/>")



        help_div.add_behavior( {
        'type': 'load',
        'cbjs_action': my.get_onload_js()
        })


        help_div.add_behavior( {
        'type': 'listen',
        'event_name': 'tab|select',
        'cbjs_action': '''

        var content = bvr.src_el.getElement(".spt_help_content");
        var options = bvr.firing_data;
        var element_name = options.element_name;
        var alias = options.alias;

        if (!alias) {
            alias = options.element_name;
        }

        spt.help.set_top();
        if (spt.help.is_visible()) {
            spt.help.load_alias(alias);
        }
        else {
            spt.help.set_view(alias);
        }
        '''

        } )


        help_div.add_behavior( {
        'type': 'listen',
        'event_name': 'show_help',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_help");
        var content = top.getElement(".spt_help_content");
        var firing_data = bvr.firing_data;
        var class_name = firing_data.class_name;
        if (!class_name) {
            class_name = 'tactic.ui.app.HelpContentWdg';
        }

        if (top.getStyle("display") != 'none') {
            spt.hide(top);
            return;
        }

        spt.help.set_top()

        // get the help view
        var help_view = spt.help.get_view();
        var html = firing_data.html;
        if (html) {
            spt.help.load_html(html);    
        }
        else {
            if (!help_view) {
                help_view = 'default'    
            }
            spt.help.load_alias(help_view);
        }

        var size = $(window).getSize();

        var dialog = bvr.src_el.getParent(".spt_dialog_content");

        dialog.setStyle("height", size.y - 100);
        dialog.setStyle("width", 650);

        var top = bvr.src_el.getParent(".spt_dialog_top");
        top.setStyle("left", size.x - 660);
        top.setStyle("top", 40);

        spt.show(top);
        '''
        } )






        content = DivWdg()
        help_div.add(content)
        content.add_class("spt_help_content");
        content.add_style("position: relative")
        content.add_style("overflow_x: auto")
        content.add_style("overflow_y: auto")
        content.add_style("margin-bottom: 10px")
        #content.add_style("border: solid 1px blue")
        content.add_style("height: 98%")


        #key = "schema_editor"
        #search = Search("config/doc")
        #search.add_filter("code", key)
        #doc = search.get_sobject()
        #doc_html = doc.get_value("doc")
        #help_div.add(doc_html)


        return top


    def get_onload_js(my):
        return '''


if (spt.help) {
    return;
}

spt.Environment.get().add_library("spt_help");


spt.help = {};
spt.help.top = null;
spt.help.content = null;

spt.help.history = [['alias', 'main']];
spt.help.history_index = -1;


spt.help.current_view = null;

spt.help.set_view = function(view) {
    spt.help.current_view = view;
}


spt.help.get_view = function() {
    return spt.help.current_view;
}


// DEPRECATED
spt.help.show_help = function() {
    spt.named_events.fire_event("show_help", {} );
}



spt.help.show = function() {
    var container = spt.help.top.getParent(".spt_help");
    spt.show(container);
}


spt.help.hide = function() {
    var container = spt.help.top.getParent(".spt_help");
    spt.hide(container);
}


spt.help.is_visible = function() {
    var container = spt.help.top.getParent(".spt_help");
    if (container.getStyle("display") == "none") {
        return false;
    }
    else {
        return true;
    }
}




spt.help.set_top = function(el) {
    if (typeof(el) == 'undefined') {
        el = $("spt_help_top");
        spt.help.top = el;
    }

    if (el.hasClass("spt_help_top")) {
        spt.help.top = el;
    }
    else {
        spt.help.top = el.getParent(".spt_help_top");
    }

    spt.help.content = el.getElement(".spt_help_content");
}




spt.help.load_prev = function() {

    if (spt.help.history_index == 0) {
        spt.alert("No more pages to load");
        return;
    }

    if (spt.help.history_index == -1) {
        spt.help.history_index = spt.help.history.length - 2;
    }
    else {
        spt.help.history_index -= 1;
    }

    var info = spt.help.history[spt.help.history_index];
    var type = info[0];
    var value = info[1];
    if (type == 'alias') {
        spt.help.load_alias(value, false);
    }
    else {
        spt.help.load_rel_path(value, false);
    }
}

spt.help.load_next = function() {

    if (spt.help.history_index == -1) {
        spt.alert("No more pages to load");
        return;
    }

    if (spt.help.history_index == spt.help.history.length - 1) {
        spt.alert("No more pages to load");
        return;
    }
    else {
        spt.help.history_index += 1;
    }

    var info = spt.help.history[spt.help.history_index];
    var type = info[0];
    var value = info[1];
    if (type == 'alias') {
        spt.help.load_alias(value, false);
    }
    else {
        spt.help.load_rel_path(value, false);
    }
}




// let the server figure out what do do
spt.help.load_html = function(html) {

    if (!spt.help.is_visible() ) {
        spt.help.show();
    }

    var class_name = 'tactic.ui.app.HelpContentWdg'; 
    var kwargs = {
        view: 'view',
        html: html
    }

    var server = TacticServerStub.get();
    var html = server.get_widget(class_name, { args: kwargs } );
    spt.behavior.replace_inner_html( spt.help.content, html );
}



// let the server figure out what do do
spt.help.load_alias = function(alias, history) {


    var class_name = 'tactic.ui.app.HelpContentWdg'; 
    var kwargs = {
        alias: alias
    }
    
    if (!spt.help) return;

    spt.help.set_view(alias);

    var server = TacticServerStub.get();
    var html = server.get_widget(class_name, { args: kwargs } );
    spt.behavior.replace_inner_html( spt.help.content, html );


    // resize
    var size = $(window).getSize();
    var dialog = bvr.src_el.getParent(".spt_dialog_content");
    if (dialog) {
        dialog.setStyle("height", size.y - 100);
        dialog.setStyle("width", 650);
    }

    if (!spt.help.is_visible() ) {
        spt.help.show();
    }


    if (typeof(history) == 'undefined') {
        history = true;
    }
    if (!history) {
        return;
    }

    if (spt.help.history_index != - 1) {
        spt.help.history = spt.help.history.slice(0, spt.help.history_index+1);
        spt.help.history_index = -1;
    }

    if (alias == spt.help.history[spt.help.history.length-1][1]) {
        return;
    }

    spt.help.history.push( ['alias', alias]);
}


spt.help.load_rel_path = function(rel_path, history) {

    if (!spt.help.is_visible() ) {
        spt.help.show();
    }

    var saved_path = rel_path;

    if (rel_path.indexOf("#") != -1) {
        var parts = rel_path.split("#");
        rel_path = parts[0];
        tag = parts[1];
    }
    else {
        tag = null;
    }

    var class_name = 'tactic.ui.app.HelpContentWdg'; 
    var kwargs = {
        rel_path: rel_path
    }

    var server = TacticServerStub.get();
    var html = server.get_widget(class_name, { args: kwargs } );
    spt.behavior.replace_inner_html( spt.help.content, html );

    // resize
    var size = $(window).getSize();
    var dialog = bvr.src_el.getParent(".spt_dialog_content");
    dialog.setStyle("height", size.y - 100);
    dialog.setStyle("width", 650);


    var help_top = bvr.src_el.getElement(".spt_help_content");
    if (help_top && tag) {
        help_top = help_top.getChildren()[0];
        var tag_els = help_top.getElements('a');
        var tag_el = null;
        for ( var i = 0; i < tag_els.length; i++) {
            var id = tag_els[i].getAttribute("id");
            if (id == tag) {
                tag_el = tag_els[i];
                break;
            }
        }
        var pos = tag_el.getPosition(help_top);
        setTimeout( function() {
            help_top.scrollTo(0, pos.y-30);
        }, 0 );
    }



    if (typeof(history) == 'undefined') {
        history = true;
    }
    if (!history) {
        return;
    }

    if (spt.help.history_index != - 1) {
        spt.help.history = spt.help.history.slice(0, spt.help.history_index+1);
        spt.help.history_index = -1;
    }

    if (rel_path == spt.help.history[spt.help.history.length-1][1]) {
        return;
    }

    spt.help.history.push( ['rel_path', saved_path]);
}



spt.help.load_custom = function(element_name) {
    var bvr = {};
    spt.help.set_view(element_name);
    bvr.options = {
      element_name: element_name,
    }
    spt.named_events.fire_event("show_help", bvr);
}




spt.help.set_top();
spt.help.set_view("main");



        '''


class HelpCreateWdg(BaseRefreshWdg):

    def get_display(my):
        alias = my.kwargs.get("alias")

        div = DivWdg()
        div.add_style("padding: 15px")
        div.add_style("margin: 10px")
        div.add_border()
        div.add_color("background", "background", -5)
        div.add_style("text-align: center")
        div.add_style("font-weight: bold")

        icon = IconWdg("WARNING", IconWdg.HELP_MISSING)
        div.add(icon)
        div.add("Add custom documentation page by clicking the Create button")

        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Create", tip="Create docs for this view")
        div.add(button)
        button.add_style("margin-right: auto")
        button.add_style("margin-left: auto")
        button.add_style("margin-top: 15px")
        button.add_style("margin-bottom: 15px")
        # FIXME: copied code from above
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.app.HelpEditWdg';

        var element_name = spt.help.get_view();
        if (!element_name) {
          element_name = "default";
        }
        var kwargs = {
          view: element_name
        }

        spt.tab.add_new("help_edit", "Help Edit", class_name, kwargs);
            
        '''
        } )
        return div



__all__.append("HelpContentWideWdg")
class HelpContentWideWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top
        top.add_color("background", "background", -5)

        help = HelpContentWdg(**my.kwargs)
        top.add(help)

        help_top = help.top
        help_top.add_style("margin: -1 auto 10 auto")
        help_top.add_border()

        return top



class HelpContentWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top
        top.add_style("height: 100%")
        top.add_style("overflow-x: hidden")
        top.set_unique_id()

        width = my.kwargs.get("width")
        if width:
            top.add_style("width: %s" % width)



        from tactic.ui.panel import CustomLayoutWdg
        html = my.kwargs.get("html")
        view = my.kwargs.get("view")

        alias = my.kwargs.get("alias")
        if alias:
            aliases = alias.split("|")
            alias = aliases[0]
            aliases = aliases[1:]
        else:
            aliases = []

        top.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_link',
            'cbjs_action': '''
            spt.mouse.table_layout_hover_over({}, {src_el: bvr.src_el, add_color_modifier: -5});
            '''
        } )

        top.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_link',
            'cbjs_action': '''
            spt.mouse.table_layout_hover_out({}, {src_el: bvr.src_el})
            '''
        } )

        top.add_smart_style("spt_link", "margin-left", "5px")
        if alias == 'main':
            top.add_smart_style("spt_link", "text-decoration", "none")
        else:
            top.add_smart_style("spt_link", "text-decoration", "underline")
        top.add_smart_style("spt_link", "padding", "1px")



        if aliases:
            related_wdg = my.get_related_wdg(aliases)
            top.add( related_wdg )


        rel_path = my.kwargs.get("rel_path")

        # attempt to get if from the widget config
        search = Search("config/widget_config")
        search.add_filter("category", "HelpWdg")
        search.add_filter("view", alias)
        config = search.get_sobject()


        if html:
            layout = CustomLayoutWdg(html=html, view=view)
            top.add(layout)

        # config can override alias
        elif config:
            layout = CustomLayoutWdg(config=config, view=alias)
            author = config.get_value("login")
            timestamp = config.get_value("timestamp")
            top.add(layout)

        elif alias:
            widget = HelpDocFilterWdg(alias=alias)
            top.add(widget)

        elif rel_path:
            widget = HelpDocFilterWdg(rel_path=rel_path)
            top.add(widget)


        elif not view:
            layout = DivWdg()
            top.add(layout)
            allow_create = my.kwargs.get("allow_create")
            if allow_create not in ['false', False]:
                layout.add(HelpCreateWdg())
            else:
                layout.add("No documentation found")
                layout.add_style("padding: 30px 20px")
                layout.add_style("margin-left: auto")
                layout.add_style("margin-right: auto")
                layout.add_style("margin-top: 50px")
                layout.add_style("text-align: center")
                layout.add_style("width: 250px;")
                layout.add_color("background", "background3")
                layout.add_color("color", "color3")
                layout.add_border()


        elif view == 'default':
            top.add(my.get_default_wdg())

        else:
            author = "TACTIC"
            timestamp = None

            search = Search("config/widget_config")
            search.add_filter("category", "HelpWdg")
            search.add_filter("view", view)
            config = search.get_sobject()
            if config:
                layout = CustomLayoutWdg(config=config, view=view)
                author = config.get_value("login")
                timestamp = config.get_value("timestamp")

            else:
                # get it from the file system
                layout = DivWdg()
                install_dir = Environment.get_install_dir()
                path = "%s/src/context/help/%s.html" % (install_dir,view)
                if os.path.exists(path):
                    f = open(path)
                    html = f.read()
                    f.close()
                    layout.add(html)

                else:
                    div = DivWdg()
                    layout.add(div)
                    div.add_style("padding: 15px")
                    div.add_style("margin: 10px")
                    div.add_border()
                    div.add_color("background", "background", -5)
                    div.add_style("text-align: center")
                    div.add_style("font-weight: bold")

                    icon = IconWdg("WARNING", IconWdg.WARNING)
                    div.add(icon)
                    div.add("There are no help pages available for this key [%s]<br/><br/>" % view)
                    div.add("<br/>")

                    div.add("Click to create a new custom doc:")
                    from tactic.ui.widget import ActionButtonWdg
                    button = ActionButtonWdg(title="Create", tip="Create docs for this view")
                    div.add(button)
                    button.add_style("margin-right: auto")
                    button.add_style("margin-left: auto")
                    button.add_style("margin-top: 15px")
                    button.add_style("margin-bottom: 15px")
                    # FIXME: copied code from above
                    button.add_behavior( {
                    'type': 'click_up',
                    'cbjs_action': '''
                    spt.tab.set_main_body_tab();
                    var class_name = 'tactic.ui.app.HelpEditWdg';

                    var element_name = spt.help.get_view();
                    if (!element_name) {
                      element_name = "default";
                    }
                    var kwargs = {
                      view: element_name
                    }

                    spt.tab.add_new("help_edit", "Help Edit", class_name, kwargs);
                        
                    '''
                    } )



                layout.add_style("margin-top: 10px")



            info_div = DivWdg()
            info_div.add("<i>Author: %s</i>" % author)
            info_div.add_style("opacity: 0.5")
            info_div.add_style("font-size: 10px")
            info_div.add_style("position: absolute")
            info_div.add_style("bottom: 20px")

            content_div = DivWdg()
            top.add(content_div)
            content_div.add_style("padding: 5px")
            content_div.add(layout)

            top.add(info_div)

        #top.add(HelpContentWdg.get_default_wdg(aliases))

        return top



    def get_related_wdg(my, aliases):
        div = DivWdg()
        div.add("<b>Related links</b>: &nbsp;&nbsp")
        div.add_style("margin-top: 5px")
        div.add_style("margin-bottom: 5px")
        div.add_style("margin-left: 10px")

        titles = [Common.get_display_title(x.replace("-"," ")) for x in aliases]
        for alias, title in zip(aliases, titles):

            link_div = SpanWdg()
            div.add(link_div)
            link_div.add_color("background", "background")
            link_div.add(title)
            link_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.help.set_top();
                spt.help.load_alias("%s");
                ''' % alias
            } )
            link_div.add_class("spt_link")
            link_div.add_class("hand")

        return div




    def get_default_wdg(cls, aliases=[]):
        div = DivWdg()
        div.set_unique_id()
        div.add_style("padding: 5px")
        if aliases:
            div.add("<b>Related links</b>:<br/><br/>")

            titles = [Common.get_display_title(x.replace("-"," ")) for x in aliases]
            for alias, title in zip(aliases, titles):

                link_div = DivWdg()
                div.add(link_div)
                link_div.add_color("background", "background")
                link_div.add(title)
                link_div.add_behavior( {
                    'type': 'click_up',
                    'cbjs_action': '''
                    spt.help.set_top();
                    spt.help.load_alias("%s");
                    ''' % alias
                } )
                link_div.add_class("spt_link")
                link_div.add_class("hand")

            div.add("<br/><br/>")


        div.add("<b>Additional useful links</b>:<br/><br/>")
        aliases = ['setup', 'end_user', 'developer', 'sys_admin']
        titles = ['Project Setup Documentation', 'End User Documentation', 'Developer Documentation', 'System Administrator Documentation']


        for alias, title in zip(aliases, titles):

            link_div = DivWdg()
            div.add(link_div)
            link_div.add_color("background", "background")
            link_div.add(title)
            link_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.help.set_top();
                spt.help.load_alias("%s");
                ''' % alias
            } )
            link_div.add_class("spt_link")
            link_div.add_class("hand")


        div.add("<br/>")

        link_div = DivWdg()
        div.add(link_div)
        link_div.add("TACTIC Documentation (PDF)")
        link_div.add_color("background", "background")
        link_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            window.open("/doc/", "TACTIC Docs");
            '''
        } )
        link_div.add_class("spt_link")
        link_div.add_class("hand")



        link_div = DivWdg()
        div.add(link_div)
        link_div.add_color("background", "background")
        link_div.add("TACTIC Community Site")
        link_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            window.open("http://community.southpawtech.com", "TACTIC Community Site");
            '''
        } )
        link_div.add_class("spt_link")
        link_div.add_class("hand")


        return div

    get_default_wdg = classmethod(get_default_wdg)


class HelpEditWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_class("spt_help_edit_top")
        top.add_color("background", "background")

        view = my.kwargs.get("view")

        from tactic.ui.container import ResizableTableWdg
        table = ResizableTableWdg()
        top.add(table)
        table.add_color("color", "color")
        table.add_style("width: 100%")
        table.add_style("height: 500px")


        table.add_row()
        left = table.add_cell()
        left.add_color("background", "background3")

        title_wdg = Table()
        
        title_wdg.add_row()
        left.add(title_wdg)
        title_wdg.add_gradient("background", "background", 0, -10)
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("margin-bottom: 5px")
        title_wdg.add_style("width: 100%")        

        title_div = DivWdg("<b>Help Pages</b>")
        title_cell = title_wdg.add_cell(title_div)
        title_cell.add_style("width: 100%")

        from tactic.ui.widget import ActionButtonWdg
        insert_button = ActionButtonWdg(title="+", size="small")
        insert_button.add_style("margin-top: -3px")
        insert_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''

        var class_name = "tactic.ui.panel.EditWdg"
        var view = "edit"
        var title = "Add new help doc"
        var cbjs_insert = "spt.tab.reload_selected();"
        var kwargs = {
          'view': view,
          'search_type': 'config/widget_config',
          'default': '{"category":"HelpWdg"}',
          'ignore': 'search_type|login|config',
          'mode': 'insert',
          //'cbjs_insert': cbjs_insert
        }

        spt.panel.load_popup(title, class_name, kwargs);

        '''
        })

        title_wdg.add_cell(insert_button)

        docs_wdg = my.get_doc_wdg()
        left.add(docs_wdg)
        left.add_style("width: 150px")
        left.add_style("min-width: 150px")
        left.add_style("min-height: 500px")
        left.add_style("vertical-align: top")
        left.add_border()


        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add_border()

        content = HelpEditContentWdg(view=view)
        right.add(content)


        return top


    def get_doc_wdg(my):
        div = DivWdg()

        search = Search("config/widget_config")
        search.add_filter("category", "HelpWdg")
        sobjects = search.get_sobjects()

        hover = div.get_color("background", -10)

        for sobject in sobjects:
            help_div = DivWdg()
            div.add(help_div)
            help_div.add_style("padding: 3px")

            view = sobject.get_value("view")
            help_div.add(view)

            help_div.add_class("hand");
            help_div.add_behavior( {
            'type': 'hover',
            'hover': hover,
            'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.hover);
            ''',
            'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
            '''
            } )


            help_div.add_behavior( {
            'type': 'click_up',
            'view': view,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_help_edit_top");
            var content = top.getElement(".spt_help_edit_content");

            var class_name = 'tactic.ui.app.HelpEditContentWdg';
            var kwargs = {
                view: bvr.view 
            };

            spt.panel.load(content, class_name, kwargs);

            '''
            } )

        return div



class HelpEditContentWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top

        view = my.kwargs.get("view")
        top.add_class("spt_help_edit_content")


        search = Search("config/widget_config")
        search.add_filter("category", "HelpWdg")
        search.add_filter("view", view)
        sobject = search.get_sobject()

        if not sobject:
            value = ""
            search_key = ""

        else:
            xml_value = sobject.get_xml_value("config")
            value = xml_value.get_value("config/%s/html/div" % (view) )
            search_key = sobject.get_search_key()


        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add("<b>View: %s</b>" % view)
        title_wdg.add_style("font-style: bold")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_gradient("background", "background", 0, -10)


        hidden = HiddenWdg("view")
        top.add(hidden)
        hidden.set_value(view)


        text = TextAreaWdg("content")
        text_id = text.set_unique_id()
        text.set_value(value)

        from tactic.ui.widget import ActionButtonWdg
        if sobject:
            delete_button = ActionButtonWdg(title="Delete")
            top.add(delete_button)
            delete_button.add_style("float: right")
            delete_button.add_style("margin-top: -3px")
            delete_button.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'cbjs_action': '''
            if (!confirm("Are you sure you wish to delete this help page?")) {
                return;
            }
            var server = TacticServerStub.get();
            server.delete_sobject(bvr.search_key);
            var top = bvr.src_el.getParent(".spt_help_edit_top");
            spt.panel.refresh(top);
            '''
            })



        test_button = ActionButtonWdg(title="Preview")
        top.add(test_button)
        test_button.add_style("float: right")
        test_button.add_style("margin-top: -3px")
        test_button.add_behavior( {
        'type': 'click_up',
        'text_id': text_id,
        'cbjs_action': '''

        var js_file = "ckeditor/ckeditor.js";

        var url = "/context/spt_js/" + js_file;
        var js_el = document.createElement("script");
        js_el.setAttribute("type", "text/javascript");
        js_el.setAttribute("src", url);

        var head = document.getElementsByTagName("head")[0];
        head.appendChild(js_el);



        var cmd = "CKEDITOR.instances." + bvr.text_id + ".getData()";
        var text_value = eval( cmd );

        bvr.options = {};
        bvr.options.html = text_value;
        spt.named_events.fire_event("show_help", bvr)
        '''
        })



        save_button = ActionButtonWdg(title="Save")
        top.add(save_button)
        save_button.add_style("float: right")
        save_button.add_style("margin-top: -3px")

        top.add("<br/>")


        save_button.add_behavior( {
        'type': 'click_up',
        'text_id': text_id,
        'cbjs_action': '''

        spt.app_busy.show("Saving Help", " ")

        var top = bvr.src_el.getParent(".spt_help_edit_content");
        var values = spt.api.Utility.get_input_values(top, null, false);

        var cmd = "CKEDITOR.instances." + bvr.text_id + ".getData()";
        var text_value = eval( cmd );
        values.content = text_value;

        var command = "tactic.ui.app.HelpEditCbk";
        var kwargs = values;
        var server = TacticServerStub.get();
        server.execute_cmd(command, kwargs);

        setTimeout("spt.app_busy.hide()", 200)
        '''
        } )

        #top.add("Style: ")
        #select = SelectWdg("style")
        #top.add(select)
        #select.set_option("values", "text|html")


        top.add("<br/>")

        top.add(text)
        text.set_value(value)
        text.add_style("width: 100%")
        text.add_style("height: 100%")
        text.add_style("min-height: 500px")
        text.add_style("display: none")
        text.add_behavior( {
        'type': 'load',
        'color': text.get_color("background", -10),
        'text_id': text_id,
        'cbjs_action': '''

        var js_file = "ckeditor/ckeditor.js";
        var url = "/context/spt_js/" + js_file;
        var js_el = document.createElement("script");
        js_el.setAttribute("type", "text/javascript");
        js_el.setAttribute("src", url);
        var head = document.getElementsByTagName("head")[0];
        head.appendChild(js_el);


        setTimeout( function() {


        CKEDITOR.on( 'instanceReady', function( ev )
        {
            ev.editor.dataProcessor.writer.indentationChars = ' ';
        });



        var config = {
          toolbar: 'Full',
          uiColor: bvr.color,
          height: '500px'
        };
config.toolbar_Full =
[
    ['Source'],
    ['Cut','Copy','Paste'],
    ['Undo','Redo','-','Find','Replace'],
    ['Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
    ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
    '/',
    ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote','CreateDiv'],
    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
    ['HorizontalRule','SpecialChar'],
    ['Styles','Format','Font','FontSize'],
    ['TextColor','BGColor'],
    ['Maximize', 'ShowBlocks']
];

        CKEDITOR.replace(bvr.text_id, config );
        bvr.src_el.setStyle("display", "");

        }, 500);
        '''
        } )

        return top


class HelpEditCbk(Command):
    def execute(my):

        view = my.kwargs.get("view")
        content = my.kwargs.get("content")

        search = Search("config/widget_config")
        search.add_filter("category", "HelpWdg")
        search.add_filter("view", view)
        config = search.get_sobject()
        if not config:
            config = SearchType.create("config/widget_config")
            config.set_value("category", "HelpWdg")
            config.set_value("view", view)

        config_xml = '''
<config>
  <%s>
<html><div><![CDATA[
%s
]]></div></html>
  </%s>
</config>
''' % (view, content, view)

        config.set_value("config", config_xml)

        config.commit()





