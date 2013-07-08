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
__all__ = ["HashPanelWdg"]

import os, types, re
from pyasm.common import Xml, XmlException, Common, TacticException, Environment, jsondumps
from pyasm.biz import Project
from pyasm.security import Security
from pyasm.search import Search
from pyasm.web import WebEnvironment, DivWdg

from tactic.ui.common import BaseRefreshWdg, WidgetClassHandler


class HashPanelWdg(BaseRefreshWdg):

    def get_args_keys(cls):
        return {
        'hash': 'hash used to build a widget'
        }
    get_args_keys = classmethod(get_args_keys)



    def get_display(my):

        hash = my.kwargs.get("hash")

        top = my.top
        widget = my.get_widget_from_hash(hash, kwargs=my.kwargs)
        top.add(widget)
        return top




    def build_widget(cls, options):
        class_name = options.get('class_name')
        if not class_name:
            class_name = 'tactic.ui.panel.ViewPanelWdg'
        else:
            del(options['class_name'])

        widget = Common.create_from_class_path(class_name, kwargs=options)
        return widget
    build_widget = classmethod(build_widget)



    def get_url_from_hash(cls, hash):

        import re
        p = re.compile("^/(\w+)")
        m = p.search(hash)
        if not m:
            print "Cannot parse hash[%s]" % hash
            return None
        key = m.groups()[0]

        # skip links because it is reserved
        if key == 'link':
            return None

        # look up the expression
        search = Search("config/url")
        search.add_filter("url", "/%s/%%"%key, "like")
        search.add_filter("url", "/%s"%key)
        search.add_where("or")
        sobject = search.get_sobject()

        return sobject

    get_url_from_hash = classmethod(get_url_from_hash)




    def get_widget_from_hash(cls, hash, return_none=False, force_no_index=False, kwargs={}):

        from pyasm.web import DivWdg
        if hash.startswith("//"):
            use_top = False
            hash = hash[1:]
        else:
            use_top = True

        import re
        p = re.compile("^/(\w+)")
        m = p.search(hash)
        if not m:
            print "Cannot parse hash[%s]" % hash
            return DivWdg("Cannot parse hash [%s]" % hash)
        key = m.groups()[0]

        # add some predefined ones
        if key == "link":
            expression = "/link/{link}"
            options = Common.extract_dict(hash, expression)

           

            # This is the standard way of communicating through main interface
            # It uses the link keyword to draw the main widget
            if use_top:
                top_class_name = WebEnvironment.get_top_class_name()
                kwargs = {
                    "link": options.get("link")
                }
            else:
                top_class_name = 'tactic.ui.panel.HashPanelWdg'
                kwargs = {
                    "hash": hash.replace("/link", "/tab")
                }

                
            widget = Common.create_from_class_path(top_class_name, [], kwargs) 
            return widget

            #expression = "/link/{link}"
            #options = Common.extract_dict(hash, expression)
            #return cls.build_widget(options)


        elif key == 'tab':
            # this is called by PageNav
            expression = "/tab/{link}"
            options = Common.extract_dict(hash, expression)
            link = options.get("link")

            # test link security
            project_code = Project.get_project_code()
            security = Environment.get_security()
            link = options.get("link")
            keys = [
                    { "element": link },
                    { "element": "*" },
                    { "element": link, "project": project_code },
                    { "element": "*", "project": project_code }
                    ]
            if not security.check_access("link", keys, "allow", default="deny"):
                widget = DivWdg()
                widget.add_color("color", "color")
                widget.add_color("background", "background3")
                widget.add_style("width: 600px")
                widget.add_style("height: 200px")
                widget.add_style("margin: 50px auto")
                widget.add_style("text-align: center")
                widget.add_border()


                widget.add("<br/>"*5)
                widget.add("This link [%s] either does not exist or you are not permitted to see it" % link)
                return widget
 


            from tactic.ui.panel import SideBarBookmarkMenuWdg
            personal = False
            if '.' in link:
                personal = True

            config = SideBarBookmarkMenuWdg.get_config("SideBarWdg", link, personal=personal)
            options = config.get_display_options(link)

            class_name = options.get("class_name")
            widget_key = options.get("widget_key")
            if widget_key:
                class_name = WidgetClassHandler().get_display_handler(widget_key)
            elif not class_name:
                class_name = 'tactic.ui.panel.ViewPanelWdg'
            widget = Common.create_from_class_path(class_name, [], options) 

            return widget

        # these show only the widget without a top
        elif key == "encoded":
            expression = "/encoded/{encoded}"
            options = Common.extract_dict(hash, expression)
            encoded = options['encoded']
            import json, binascii
            data = json.loads( binascii.unhexlify(encoded) )
            class_name = data[0]
            args = data[1]
            kwargs = data[2]

            widget = Common.create_from_class_path(class_name, args, kwargs) 
            return cls.build_widget(options)
            
        elif key == "calendar":
            from tactic.ui.widget import CalendarWdg
            return CalendarWdg()

        elif key == "list":
            expression = "/list/{search_type}/{view}"
            options = Common.extract_dict(hash, expression)
            class_name = 'tactic.ui.panel.ViewPanelWdg'
            widget = Common.create_from_class_path(class_name, [], options) 
            return widget

        elif key == "widget":
            expression = "/widget/{class_name}"
            options = Common.extract_dict(hash, expression)
            class_name = options.get("class_name")
            kwargs = {
            }

            widget = Common.create_from_class_path(class_name, [], kwargs) 
            return widget
 
        else:
            # look up the expression
            search = Search("config/url")
            search.add_filter("url", "/%s/%%"%key, "like")
            search.add_filter("url", "/%s"%key)
            search.add_where("or")
            sobject = search.get_sobject()

            if not sobject:
                if return_none:
                    return None
                return DivWdg("No Widget found for hash [%s]" % hash)
 

            config = sobject.get_value("widget")
            xml = Xml()
            xml.read_string(config)


            use_index = kwargs.get("use_index")
            if use_index in [True, 'true']:
                use_index = True
            elif use_index in [False, 'false']:
                use_index = False

            use_admin = kwargs.get("use_admin")
            if use_admin in [True, 'true']:
                use_admin = True
            elif use_admin in [False, 'false']:
                use_admin = False


            use_sidebar = kwargs.get("use_sidebar")
            if use_sidebar in [False, 'false']:
                use_sidebar = False
            elif use_admin in [True, 'true']:
                use_sidebar = True


            if use_index is not None or use_admin is not None:
                pass

            elif force_no_index in [True, 'true']:
                use_index = False
            else:
                use_index = sobject.get_value("index", no_exception=True)
                if not use_index:
                    use_index = xml.get_value("/element/@index");
                    if use_index in ['true', True]:
                        use_index = True

                use_admin = sobject.get_value("admin", no_exception=True)
                if not use_admin:
                    use_admin = xml.get_value("/element/@admin");
                    if use_admin in ['true', True]:
                        use_admin = True

                    use_sidebar = xml.get_value("/element/@sidebar");
                    if use_sidebar in ['false', False]:
                        use_sidebar = False


            if use_index or use_admin:
                # check if there is an index
                search = Search("config/url")
                search.add_filter("url", "/index")
                index = search.get_sobject()

                if not index or use_admin:
                    # use admin
                    from tactic.ui.app import PageNavContainerWdg
                    top = PageNavContainerWdg( hash=hash, use_sidebar=use_sidebar )

                else:
                    config = index.get_value("widget")
                    xml = Xml()
                    xml.read_string(config)
                    node = xml.get_node("element/display")

                    options = {}
                    options.update(xml.get_node_values_of_children(node))

                    class_name = xml.get_value("element/display/@class")
                    if class_name:
                        options['class_name'] = class_name

                    options['hash'] = hash
                    top = cls.build_widget(options)



                return top.get_buffer_display()
 

            # build the widget
            url = sobject.get_value("url")
            url = url.strip()
            options = Common.extract_dict(hash, url)


            node = xml.get_node("element/display")
            options.update(xml.get_node_values_of_children(node))

            class_name = xml.get_value("element/display/@class")
            if class_name:
                options['class_name'] = class_name

            widget = cls.build_widget(options)

            name = hash.lstrip("/")
            name = name.replace("/", " ")
            widget.set_name(name)

            if not widget and return_none:
                return None

            # NOTE: This has been moved to TopWdg ... the reason being that
            # there are a lot of global entities like app_busy and popups that
            # are defined there and are not taken into account if the
            # palette is set here.  Leaving this in hear in case it ever
            # becomes possible for a lower widget to affect the global palette
            """
            palette_key = xml.get_value("element/@palette")
            if url == "/index" and palette_key:

                from pyasm.web import Palette

                # look up palette the expression for index
                palette = Palette.get()

                palette.set_palette(palette_key)
                colors = palette.get_colors()
                colors = jsondumps(colors)

                widget.add_behavior( {
                    'type': 'load',
                    'palette_key': palette_key,
                    'colors': colors,
                    'cbjs_action': '''
                    var env = spt.Environment.get();
                    env.set_colors(%s);
                    env.set_palette(bvr.palette_key);
                    ''' % colors
                } )
            """

            return widget



    get_widget_from_hash = classmethod(get_widget_from_hash)



