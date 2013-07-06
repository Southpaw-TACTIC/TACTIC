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
__all__ = ["HeaderWdg", "DocMapping", "ProjectSwitchWdg"]

from pyasm.common import Environment, TacticException
from pyasm.web import *
from pyasm.widget import *
from pyasm.biz import *
from pyasm.search import Search, SObject
from clipboard_wdg import ClipboardWdg
from file_wdg import ThumbWdg
import math, random, types, cgi

class HeaderWdg(Widget):
    '''A widget that occupies the header area of a regular Tactic page'''
    def __init__(my, title='header'):
        super(HeaderWdg,my).__init__(title)
        my.title = title

    def extend(my):
        from tab_wdg import TabExtendWdg 
        extend_tab = TabExtendWdg()
        extend_tab.set_tab(my)
        extend_tab.get_display()


        
    def get_display(my):
        #my.extend()

        try:
            return my._get_display()
        except TacticException, e:
            from web_wdg import ExceptionWdg
            widget = ExceptionWdg(e)
            return widget

    def _get_display(my):
        login = WebContainer.get_login()
        login_name = login.get_login()

        web = WebContainer.get_web()
        context = web.get_site_context_url()
 
        div = HtmlElement.div()
        div.set_style("top: 0px; margin: 1.6em 0 2em 0; height: 4em")
        
        
        project = Project.get()
        if not my.title:
            my.title = project.get_value('title')

        title_data = HtmlElement.h4(my.title)
        
        link_width = '400'
        if web.get_app_name() != 'Browser':
            link_width = '240'
            title_data.add_class('app')



        control = DivWdg()
        control.set_style("position: absolute; float: right; top: 1px; right: 2px")

        help_menu = HelpMenuWdg()
        control.add(FloatDivWdg(help_menu, width=30))

        div.add(help_menu.get_panel())
        
        
        span = SpanWdg('[%s]' %project.get_code(), css='med hand')
        span.add_style("float: left")
        script = "Common.follow_click(event, '%s', 10, 0); set_display_on('%s');"\
                "Common.overlay_setup('mouseup',function(){%s})"\
            %(ProjectSwitchWdg.WDG_ID, ProjectSwitchWdg.WDG_ID, \
             ProjectSwitchWdg.get_off_script())
        span.add_event('onclick', script)
        control.add(span)
        div.add(ProjectSwitchWdg())
        
        root = web.get_site_root()
        
        #span = SpanWdg(HtmlElement.href(ref='/%s' % root, data='[home]'), css='med')
        #span.add_style("float: left")
        #control.add(span)

        span = SpanWdg(HtmlElement.href(ref='/doc/', data='[docs]', target='_blank'), css='med')
        span.add_style("float: left")
        control.add(span)


        from pyasm.prod.biz import ProdSetting
        project_docs = ProdSetting.get_value_by_key("project_docs_url")
        if project_docs:
            project_code = Project.get_project_code()
            span = SpanWdg(HtmlElement.href(ref=project_docs, data='[%s-docs]' % project_code, target='_blank'), css='med')
            span.add_style("float: left")
            control.add(span)

        app_name = web.get_app_name()
        if app_name != 'Browser':
            span = SpanWdg(HtmlElement.href(ref='%s/%s'\
                %(context.to_string(), app_name), data='[app]'), css='med')
            span.add_style("float: left")
        
            control.add(span)



        import urllib
        params = web.request.params
        edited_params = {}
        for name, value in params.items():
            if name in ['marshalled', 'password', 'login']:
                continue
            if type(value) == types.ListType:
                if len(value) == 1:
                    value = value[0]

            if isinstance(value, cgi.FieldStorage):
                continue

            if not value:
                continue
            edited_params[name] = value
                
        query_string = urllib.urlencode(edited_params, doseq=True)
        site_url = web.get_site_context_url().to_string()
        url = "%s?%s" % (site_url, query_string)

        span = SpanWdg()
        span.add_style("float: left")
        link = HtmlElement.href(ref=url, data='[link]')
        span.add(link)
        control.add(span)




        span = SpanWdg("user: ", css='med')
        span.add(login.get_full_name())
        control.add( span )
        control.add( SpanWdg(ChangePasswordLinkWdg(), css='med' ))
        control.add( SpanWdg(SignOutLinkWdg(), css='med') )

       
        # add the custom widgets
        #for widget in my.widgets:
        #    control.add(widget)
       
        div.add(control)

        clipboard_div = DivWdg()
        clipboard = ClipboardWdg()
        clipboard_div.add_style("float: right")
        clipboard_div.add(clipboard)
        div.add(clipboard_div)

        skin = WebContainer.get_web().get_skin()
        if skin == "classic":
            title_div = DivWdg()
            
            title_div.add_style('width', '800px')

            link = HtmlElement.href(data=title_data, ref='%s/' %context.to_string())
            link_div = FloatDivWdg(link, width=link_width, css='left_content')
            title_div.add(link_div)

            if not web.is_IE():
                trail_div = my.get_trail()
                title_div.add(trail_div)
            title_div.add(HtmlElement.br())
            div.add(title_div)


        else:
            my.add_logo(div, skin) 


        return div



    def add_logo(my, div, skin):
        '''add a logo that matches the skin'''
        logo_div = FloatDivWdg(css='')
        logo_div.add(HtmlElement.img(src='/context/skins/%s/images/tactic_logo.gif'% skin))
        div.add( logo_div )
        project = Project.get()
        if project.get_base_type():
            thumb = ThumbWdg()
            thumb.set_show_clipboard(False)
            thumb.set_icon_size(50)
            thumb.set_sobject(project)
            project_icon_div = FloatDivWdg(thumb)
            project_icon_div.add_style('margin-top: 3px')
            div.add(project_icon_div)

    def get_trail(my):
        ''' draws a trail'''
        trail_div = DivWdg()
        trail_div.add_style('margin','0px')
        color = '#e4e7eb'
        for j in xrange(1,6):
            box = None
            length = random.randint(20, 30)
            for i in xrange(1, length):
                width = 9 - random.randint(1, j)
                box = FloatDivWdg('&nbsp;', width=width)
                #box.add_style('height','0.5em')
                if random.random() > 0.5 * i/12:
                    box.add_class('trail_on')
                else:
                    box.add_class('trail_off')
              
                trail_div.add(box)
            # start a new line
            box.add_style('float','clear')
        return trail_div.get_buffer_display()

class ProjectSwitchWdg(Widget):
    ''' this is a popup widget for switching between project'''
    WDG_ID = "project_switch_wdg_id"
    
    def get_display(my):
        widget = Widget()
        span = SpanWdg('[ projects ]', css='hand')
        span.add_style('color','white')
        span.add_event('onclick',"spt.show_block('%s')" %my.WDG_ID)
        widget.add(span)
        
        # add the popup
        div = DivWdg(id=my.WDG_ID, css='popup_wdg')
        widget.add(div)
        div.add_style('width', '80px')
        div.add_style('display', 'none')
        title_div = DivWdg()
        div.add(title_div)
        title = FloatDivWdg('&nbsp;', width='60px')
        title.add_style('margin-right','2px')
        title_div.add_style('padding-bottom', '4px')
        title_div.add(title)
        title_div.add(CloseWdg(my.get_off_script(), is_absolute=False))


        div.add(HtmlElement.br())
        
        search = Search(Project)
        search.add_where("\"code\" not in ('sthpw','admin')")
        search.add_column('code')
        projects = search.get_sobjects()
        values = SObject.get_values(projects, 'code')

        web = WebContainer.get_web()
        root = web.get_site_root()
        
        
        security = Environment.get_security()
        for value in values:
            if not security.check_access("project", value, "view"):
                continue
            script = "location.href='/%s/%s'"%(root, value)
            sub_div = DivWdg(HtmlElement.b(value), css='selection_item') 
            sub_div.add_event('onclick', script)
            div.add(sub_div)
        
        div.add(HtmlElement.hr())
        if security.check_access("project", 'default', "view"):
            script = "location.href='/%s'" % root
            sub_div = DivWdg('home', css='selection_item') 
            sub_div.add_event('onclick', script)
            div.add(sub_div)

        if security.check_access("project", "admin", "view"):
            script = "location.href='/%s/admin/'" %root
            sub_div = DivWdg('admin', css='selection_item') 
            sub_div.add_event('onclick', script)
            div.add(sub_div)

       

        return widget

    def get_off_script():
        return "spt.hide('%s'); document.removeEvents('mouseup') " % ProjectSwitchWdg.WDG_ID
    get_off_script = staticmethod(get_off_script)

class DocMapping(object):
    '''class which maps the Tactic documentation to a specific tab'''

    def get_mapping(my,title):

        project = Project.get()

        type = project.get_base_type()

        base = "doc"

        parts = []
        parts.append("/doc")

        if type == "prod":
            parts.append("production")
        elif type == "flash":
            parts.append("flash")

        # HACK: remove plural
        if title.endswith("s"):
            title = title[:-1]

        name = title.lower()
        name = name.replace(" ", "_")
        name += ".html"


        parts.append( name )

        url = "/".join( parts )
        return url




