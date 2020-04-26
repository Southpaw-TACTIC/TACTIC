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

__all__ = ['PreferenceWdg','PreferenceEditWdg','PreferenceDescriptionWdg','SetPreferenceCmd']


from pyasm.search import Search
from pyasm.command import Command
from pyasm.web import Widget, DivWdg, SpanWdg, WebContainer
from pyasm.widget import TableWdg, SelectWdg, PopupWdg, IconWdg, TextAreaWdg, TextWdg

from tactic.ui.common import BaseTableElementWdg
from pyasm.biz import PrefSetting


class PreferenceWdg(Widget):

    def get_display(self):

        widget = Widget()
         
        # added a change password widget to the preferences tab.  
        # This should be moved into the table eventually
        div = DivWdg()
        #div.add(ChangePasswordLinkWdg())
        div.set_style("font-size: 14px; padding-left: 10px; margin-top: 10px" )
        widget.add(div)



        search = Search("sthpw/pref_list")
        sobjects = search.get_sobjects()
        table = TableWdg("sthpw/pref_list", "user")
        table.set_sobjects(sobjects)
        widget.add(table)


        return widget


class PreferenceEditWdg(BaseTableElementWdg):
    
    def get_display(self):
        sobject = self.get_current_sobject()
        key = sobject.get_value("key")
        options = sobject.get_value("options")
        type = sobject.get_value("type")

        # get the value of the users preferences
        search = Search("sthpw/pref_setting")
        search.add_user_filter()
        search.add_filter("key", key)
        pref_setting = search.get_sobject()
        if pref_setting:
            value = pref_setting.get_value("value")
        else:
            value = ""

        div = DivWdg()

        element_name = "%s_%s" % (self.get_name(), sobject.get_id() )
      
        script = '''var server = TacticServerStub.get();
                var value = bvr.src_el.value;
                if (!value) return;

                spt.app_busy.show("Saving", "Saving Preference for [%s]");

                setTimeout( function() {
                    try{
                        server.execute_cmd('tactic.ui.table.SetPreferenceCmd', {key: '%s', value: value});
                    }catch(e){
                        spt.alert(spt.exception.handler(e));
                    }
                        
                    spt.app_busy.hide() 
                        
                    }, 200);'''%(key, key)

        if key in ['skin', 'palette', 'js_logging_level']:
            script = '''%s; spt.app_busy.show('Reloading Page ...'); setTimeout('spt.refresh_page()', 200);'''%script

        if type == "sequence":
            from pyasm.prod.web import SelectWdg
            select = SelectWdg(element_name)
            select.add_behavior({'type': "change", 
                'cbjs_action': script})

            select.set_option("values",options)
            if value:
                select.set_value(value)
            div.add(select)
        else:
            text = TextWdg(element_name)
            text.add_behavior({'type': "blur", 
                'cbjs_action': script})
            if value:
                text.set_value(value)
            div.add(text)
     
        return div

class PreferenceDescriptionWdg(BaseTableElementWdg):
    '''Preference description with help bubble if applicable'''
    def get_display(self):
        sobject = self.get_current_sobject()
        title = sobject.get_value("title")
        widget = Widget()
        widget.add(sobject.get_description())
        
        if title=='Debug':
            pop = PopupWdg("pref_help_%s" %title)
            hint = 'If set to [true], you can view the Debug Widget at the bottom left corner of your page.'
            icon_wdg = IconWdg(hint, IconWdg.HELP)
            widget.add(SpanWdg(icon_wdg, css='small'))
            
            widget.add(pop)

        elif title=='Filter':
            pop = PopupWdg("pref_help_%s" %title)
            hint = 'If set to [multi], It generally applies to filters in the filter box for Artist Tab.'
            icon_wdg = IconWdg(hint, IconWdg.HELP)
            widget.add(SpanWdg(icon_wdg, css='small'))
            
            widget.add(pop)

        elif title=='Quick Text':
            pop = PopupWdg("pref_help_%s" %title)
            hint = 'A list of | separated phrases a user can pick from to enter into the note area of Note Sheet.'
            icon_wdg = IconWdg(hint, IconWdg.HELP)
            widget.add(SpanWdg(icon_wdg, css='small'))
            
            widget.add(pop)

        return widget



class SetPreferenceCmd(Command):

    def get_title(self):
        return "Set Preference"

    def execute(self):
        web = WebContainer.get_web()
        #element_name = web.get_form_value("element_name")
        #key = web.get_form_value("key")
        key = self.kwargs.get('key')
        value = self.kwargs.get('value')

        PrefSetting.create(key,value)

        self.description = "Set Preference '%s' to '%s'" % (key,value)



