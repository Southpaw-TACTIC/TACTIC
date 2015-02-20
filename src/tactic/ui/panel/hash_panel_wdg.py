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
from pyasm.search import Search, SearchType
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



    def _get_flags(cls, xml, sobject=None, force_no_index=False, kwargs={}):
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
                else:
                    use_index = False

            use_admin = sobject.get_value("admin", no_exception=True)
            if not use_admin:
                use_admin = xml.get_value("/element/@admin");
                if use_admin in ['true', True]:
                    use_admin = True
                else:
                    use_admin = False

                use_sidebar = xml.get_value("/element/@sidebar");
                if use_sidebar in ['false', False]:
                    use_sidebar = False
                else:
                    use_sidebar = True

        return use_index, use_admin, use_sidebar

    _get_flags = classmethod(_get_flags)




    def _get_predefined_url(cls, key, hash):

        # make some predefined fake urls
        if key in ["link", "tab", "admin"]:
            # this is called by PageNav
            if key == "admin":
                expression = "/admin/link/{link}"
            else:
                expression = "/%s/{link}" % key
            options = Common.extract_dict(hash, expression)
            link = options.get("link")

            if not link:
                return None


            from tactic.ui.panel import SideBarBookmarkMenuWdg
            personal = False
            if '.' in link:

                # put in a check to ensure this is a user
                parts = link.split(".")

                # you can only see your personal links
                user = Environment.get_user_name()
                if user == parts[0]:
                    personal = True

            # test link security
            project_code = Project.get_project_code()
            security = Environment.get_security()
            keys = [
                    { "element": link },
                    { "element": "*" },
                    { "element": link, "project": project_code },
                    { "element": "*", "project": project_code }
            ]
            if not personal and not security.check_access("link", keys, "allow", default="deny"):
                print "Not allowed"
                return None



            config = SideBarBookmarkMenuWdg.get_config("SideBarWdg", link, personal=personal)
            options = config.get_display_options(link)
            if not options:

                from pyasm.biz import Schema
                config_xml = []
                config_xml.append( '''
                <config>
                ''')
         
                config_schema = Schema.get_predefined_schema('config')
                SideBarBookmarkMenuWdg.get_schema_snippet("_config_schema", config_schema, config_xml)
                schema = Schema.get_admin_schema()
                SideBarBookmarkMenuWdg.get_schema_snippet("_admin_schema", schema, config_xml)

                config_xml.append( '''
                </config>
                ''')

                xml = "".join(config_xml)

                from pyasm.widget import WidgetConfig
                schema_config = WidgetConfig.get(view="_admin_schema", xml=xml)
                options = schema_config.get_display_options(link)
                if not options:
                    schema_config.set_view("_config_schema")
                    options = schema_config.get_display_options(link)

                if not options:
                    return None




            class_name = options.get("class_name")
            widget_key = options.get("widget_key")
            if widget_key:
                class_name = WidgetClassHandler().get_display_handler(widget_key)
            elif not class_name:
                class_name = 'tactic.ui.panel.ViewPanelWdg'


            if key in ["admin", "tab"]:
                use_index = "false"
            else:
                use_index = "true"

            if key in ['admin']:
                use_admin = "true"
            else:
                use_admin = "false"


            xml = []
            xml.append('''<element admin="%s" index="%s">''' % (use_admin, use_index))
            xml.append('''  <display class="%s">''' % class_name)
            for name, value in options.items():
                xml.append("<%s>%s</%s>" % (name, value, name) )
            xml.append('''  </display>''')
            xml.append('''</element>''')

            xml = "\n".join(xml)

            sobject = SearchType.create("config/url")
            sobject.set_value("url", "/%s/{value}" % key)
            sobject.set_value("widget", xml )

            return sobject
 
        else:
            return None

    _get_predefined_url = classmethod(_get_predefined_url)




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
            if return_none:
                return None
            print "Cannot parse hash[%s]" % hash
            return DivWdg("Cannot parse hash [%s]" % hash)
        key = m.groups()[0]

        if key != 'login':
            security = Environment.get_security()
            login = security.get_user_name()
            # guest user should never be able to see admin site
            if login == "guest" and key == 'admin':
                #from pyasm.widget import Error403Wdg
                #return Error403Wdg().get_buffer_display()
                from pyasm.widget import WebLoginWdg
                # HACK: if the guest access is full, the the outer form
                # is not defined ... force it in here.  This is because the
                # top used it TopWdg and not TitleTopWdg
                div = DivWdg()
                div.add("<form id='form' name='form' method='post' enctype='multipart/form-data'>\n")
                web_login_wdg = WebLoginWdg().get_buffer_display()
                div.add(web_login_wdg)
                div.add("</form>\n")
                return div





        sobject = cls._get_predefined_url(key, hash)

        # look up the url
        if not sobject:
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
        config = config.replace('&','&amp;')

        url = sobject.get_value("url")
        url = url.strip()

        # update the config value with expressions
        options = Common.extract_dict(hash, url)
        for name, value in options.items():
            config = config.replace("{%s}" % name, value)


        xml = Xml()
        xml.read_string(config)


        use_index, use_admin, use_sidebar = cls._get_flags(xml, sobject, force_no_index, kwargs)


        if use_admin:
            # use admin
            from tactic.ui.app import PageNavContainerWdg
            top = PageNavContainerWdg( hash=hash, use_sidebar=use_sidebar )
            return top.get_buffer_display()

        elif use_index:

            # check if there is an index
            search = Search("config/url")
            search.add_filter("url", "/index")
            index = search.get_sobject()
            # just use admin if no index page is found
            if not index:
                from tactic.ui.app import PageNavContainerWdg
                top = PageNavContainerWdg( hash=hash, use_sidebar=use_sidebar )
                return top.get_buffer_display()
                
            config = index.get_value("widget")
            xml = Xml()
            xml.read_string(config)
            node = xml.get_node("element/display")

            options.update(xml.get_node_values_of_children(node))

            class_name = xml.get_value("element/display/@class")
            if class_name:
                options['class_name'] = class_name

            # this passes the hash value to the index widget
            # which must handle it accordingly
            options['hash'] = hash
            top = cls.build_widget(options)

            return top.get_buffer_display()




        # process the options and then build the widget from the xml


        options = Common.extract_dict(hash, url)
        for name, value in kwargs.items():
            options[name] = value

        node = xml.get_node("element/display")
        options.update(xml.get_node_values_of_children(node))

        class_name = xml.get_value("element/display/@class")
        if class_name:
            options['class_name'] = class_name

        widget = cls.build_widget(options)

        name = hash.lstrip("/")
        name_array = name.split("/")
        try:
            name_end = name_array[-1]
            name_end = name_end.replace("_", " ")
            widget.set_name(name_end)
        except IndexError:
            widget.set_name(name)

        return widget

    get_widget_from_hash = classmethod(get_widget_from_hash)



