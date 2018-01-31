###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ADSearchWdg", "ADInputWdg", 'ADCacheUserCbk']

from pyasm.web import *

from pyasm.common import Config
from tactic.ui.common import BaseRefreshWdg

from pyasm.security import Login
from pyasm.web import DivWdg, Widget, Table
from pyasm.widget import ButtonWdg, CheckboxWdg, HiddenWdg, TextWdg, ProdIconButtonWdg, IconButtonWdg, IconWdg
from pyasm.search import Search, SearchType
from pyasm.common import Environment

from tactic.ui.widget import TextBtnSetWdg


INSTALL_DIR = Environment.get_install_dir()
BASE_DIR = "%s/src/tactic/active_directory" % INSTALL_DIR


class ADSearchWdg(BaseRefreshWdg):

    def init(self):
        pass


    def get_args_keys(self):
        return {
            'cbjs_action': 'callback when a user is clicked',
        }



    def get_display(self):
        web = WebContainer.get_web()
        key = web.get_form_value('name')

        top = DivWdg()
        top.add_class('ad_search_wdg_top')
        self.set_as_panel(top)

        text = TextWdg("name")
        text.set_value(key)

        close_wdg = SpanWdg()
        close_wdg.add( IconWdg("Close", IconWdg.POPUP_WIN_CLOSE) )
        close_wdg.add_style("float: right")
        close_wdg.add_class("hand")

        # NOTE: the div we are looking for to hide on 'close' is outside of the this widget and
        #       is part of the parent widget
        close_wdg.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
                var ad_input_content = bvr.src_el.getParent(".ad_input_content");
                spt.toggle_show_hide(ad_input_content);
            '''
        })

        top.add( close_wdg )
        top.add("Active Directory Search:<br clear='all'/> ")

        table = Table()
        table.add_row()
        table.add_cell(text)
        td = table.add_cell(self.get_search_wdg())
        td.add_style("display", "")
        top.add(table)



        results_div = DivWdg()
        top.add(results_div)
        results_div.add_style("border: solid 1px #444")
        results_div.add_style("margin: 10px")
        results_div.add_style("padding: 5px")
        #results_div.add_style("max-height: 400px")
        results_div.add_style("overflow: auto")

        if not key:
            results_div.add("Please enter search criteria")
            return top


        results_div.add("Results Found ...")
        users = self.find_users(key)

        max_num_users = 20
        if len(users) > max_num_users:
            display_users = users[:max_num_users]
        else:
            display_users = users

        for user in display_users:
            user_div = DivWdg()
            user_div.add_style("margin: 5px")
            user_div.add_class("hand")
            user_div.add_event("onmouseover", "$(this).setStyle('background','#444')")
            user_div.add_event("onmouseout", "$(this).setStyle('background','#222')")

            checkbox = CheckboxWdg()
            user_div.add(checkbox)

            display_name = user.get('display_name')
            if not display_name:
                display_name = "%s %s" % (user.get('first_name'), user.get('last_name'))
            email = user.get('email')
            login = user.get('login')
            phone_number = user.get('phone_number')

            user_div.add(display_name)
            if email:
                user_div.add(" (%s) " % email)


            self.cbjs_action = self.kwargs.get('cbjs_action')
            if self.cbjs_action:
                user_behavior = {
                    'type': 'click_up',
                    'cbjs_action': self.cbjs_action
                }
                user_div.add_behavior( user_behavior )
            else:
                user_behavior = {
                    'type': 'click_up',
                    'cbjs_action': 'alert("Not implemented")'
                }
                user_div.add_behavior( user_behavior )

            user_div.add_attr("spt_input_value", login)
            user_div.add_attr("spt_display_value", display_name)
            user_div.add_attr("spt_phone_number", phone_number)
            user_div.add_attr("spt_email", email)

            results_div.add(user_div)


        num_users = len(users)
        if num_users > max_num_users:

            results_div.add("... and %s more results matched" % (num_users-max_num_users))

            results_div.add("<br/>Please narrow your search")
            #nav_div = DivWdg()
            #num_categories = num_users / max_num_users + 1
            #if num_categories > 10:
            #    nav_div.add("<br/>Please narrow your search")
            #else:
            #    for i in range(0, num_categories):
            #        span = SpanWdg()
            #        span.add(i)
            #        span.add("&nbsp;&nbsp;")
            #        nav_div.add(span)
            #results_div.add(nav_div)


        if not users:
            user_div = DivWdg()
            user_div.add_style("margin: 5px")
            user_div.add("No Results")
            results_div.add(user_div)
        return top
        

    def find_users(self, key):
        # find users in the current database
        users = []

        try:
            import active_directory
            has_ad = True
        except ImportError:
            has_ad = False



        python = Config.get_value('services', 'python')
	if not python:
	    python = 'python'

        has_ad = True
        if has_ad:

            # look for defined domains
            domains_str = Config.get_value("active_directory", "domains")
            if not domains_str:
                domains = [None]
            else:
                domains = domains_str.split("|")
            print "domains: ", domains

           
            from subprocess import Popen, PIPE
            for domain in domains:
                # get the info from a separate process
                if domain:
                    cmd = [python, "%s/ad_get_user_list.py" % BASE_DIR, '-d', domain, "-k", key]
                else:
                    cmd = [python, "%s/ad_get_user_list.py" % BASE_DIR, "-k", key,]

                output = Popen( cmd, stdout=PIPE).communicate()[0]
                #import StringIO
                #output = StringIO.StringIO(output)

                attrs_map = {
                'sAMAccountName':   'login',
                'displayName':      'display_name',
                'telephoneNumber':  'phone_number',
                'l':                'location',
                'mail':             'email'
                }

                import simplejson
                print "outpu: ", output
                ad_users = simplejson.loads(output)
                for ad_user in ad_users:

                    user = {}
                    for ad_key, key in attrs_map.items():
                        user[key] = ad_user.get(ad_key)

                    users.append(user)



        # otherwise use sthpw login table
        else:
            if key:
                logins = Search.eval("@SOBJECT(sthpw/login['login','like','%%%s%%'])" % key)
            else:
                logins = Search.eval("@SOBJECT(sthpw/login)")
            if not logins:
                return []

            for i, login in enumerate(logins):
                user = {
                    'login': login.get_value('login'),
                    'display_name': login.get_value('display_name'),
                    'email': login.get_value('email'),
                    'phone_number': login.get_value('phone_number')
                }
                users.append(user)

        # sort the users
        def sort(a, b):
            return cmp( a.get('display_name'), b.get('display_name') )
        users.sort(cmp)

        return users


    def get_search_wdg(self):
        filter_div = DivWdg()
        filter_div.add_style("width: 100px")

        buttons_list = [
            {'label': 'Run Search', 'tip': 'Run search with this criteria' },
        ]

        txt_btn_set = TextBtnSetWdg( position='', buttons=buttons_list, spacing=6, size='large', side_padding=4 )
        run_search_bvr = {
            'type':         'click_up',
            'cbjs_action':  '''
                spt.app_busy.show('Search ...', 'Searching Active Directory for matching users.');
                setTimeout( function() {
                var top = bvr.src_el.getParent('.ad_search_wdg_top');
                var values = spt.api.Utility.get_input_values(top);
                spt.panel.refresh(top, values);
                spt.app_busy.hide();
                }, 100);
            '''
        }
        txt_btn_set.get_btn_by_label('Run Search').add_behavior( run_search_bvr )
        #filter_div.add( txt_btn_set )

        div = DivWdg()
        div.add_behavior(run_search_bvr)
        button = ProdIconButtonWdg("Run Search")
        button.add_behavior(run_search_bvr)

        div.add(button)
        filter_div.add(div)
        return filter_div




from pyasm.widget import BaseInputWdg
class ADInputWdg(BaseInputWdg):
    def get_display(self):
        top = DivWdg()
        top.add_class("ad_input_top")

        name = self.get_name()
        text = TextWdg(self.get_input_name())


        # get the login
        sobject = self.get_current_sobject()
        client = sobject.get_value("contact_name")
        print "client: ", client
        if client:
            login_sobj = Login.get_by_code(client)
        else:
            login_sobj = Environment.get_login()

        # build the display_name
        login = login_sobj.get_value("login")
        display_name = login_sobj.get_value("display_name")
        if not display_name:
            display_name = "%s %s" % (user.get('first_name'), user.get('last_name'))
        display_name = display_name.replace('"', "'")


        
        print "login: ", login
        hidden = HiddenWdg(self.get_input_name())
        hidden.set_options( self.options.copy() )
        hidden.add_class("spt_ad_input")
        if login:
            hidden.set_value(login)
        top.add(hidden)


        # copy over some options
        #text.set_options( self.options.copy() )
        if login:
            text.set_value(display_name)
        text.set_option("read_only", "true")
        text.add_class("spt_ad_display")
        top.add(text)



        top.add("&nbsp;&nbsp;")



        groups_str = self.get_option("groups_allowed_to_search")
        if groups_str:
            stmt = 'groups_list = %s' % groups_str
            exec stmt
        else:
            groups_list = None

        allow_search = True

        if groups_list:
            allow_search = False
            login_in_group_list = Search.eval("@SOBJECT(sthpw/login_in_group['login','=','%s'])" % login)
            for login_in_group in login_in_group_list:
                group = login_in_group.get_value("login_group")
                if group in groups_list:
                    allow_search = True
                    break

        if login == 'admin':
            allow_search = True


        if allow_search:
            button = IconButtonWdg('Search for User', IconWdg.USER)
            #button = ButtonWdg()
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent('.ad_input_top');
                var content = top.getElement('.ad_input_content');
                spt.toggle_show_hide(content);
                '''
            } )
            top.add(button)

        ad_top = DivWdg()
        ad_top.add_class("ad_input_content")
        ad_top.add_style("display: none")
        ad_top.add_style("position: absolute")
        ad_top.add_style("background: #222")
        ad_top.add_style("min-width: 300px")
        ad_top.add_style("border: solid 1px #000")
        ad_top.add_style("padding: 20px")

        cbjs_action = '''
        var value = bvr.src_el.getAttribute('spt_input_value');
        var display_value = bvr.src_el.getAttribute('spt_display_value');
        var phone_number = bvr.src_el.getAttribute('spt_phone_number');
        var email = bvr.src_el.getAttribute('spt_mail');

        var top = bvr.src_el.getParent('.ad_input_top');
        var content = top.getElement('.ad_input_content');
        var input = top.getElement('.spt_ad_input');
        var display = top.getElement('.spt_ad_display');
        input.value = value;
        display.value = display_value;

        server = TacticServerStub.get()
        server.execute_cmd("tactic.active_directory.ADCacheUserCbk", {login: value})

        spt.toggle_show_hide(content);

        '''
        ad_search_wdg = ADSearchWdg(cbjs_action=cbjs_action)
        ad_top.add(ad_search_wdg)

        top.add(ad_top)

        return top


from pyasm.command import Command
class ADCacheUserCbk(Command):
    def execute(self):
        # disabling for now
        print "caching user ..."

        web = WebContainer.get_web()
        login = self.kwargs.get("login")

        login_sobj = Search.eval("@SOBJECT(sthpw/login['login','%s'])" % login, show_retired=True)
        if login_sobj:
            print "login %s already exists" % login
            return

        # cache the user
        try:
            from ad_authenticate import ADAuthenticate

            authenticate = ADAuthenticate()

            login_sobj = SearchType.create("sthpw/login")
            login_sobj.set_value("login", login)
            authenticate.add_user_info(login_sobj, password=None)
            login_sobj.commit()
        except Exception, e:
            print "Error: ", str(e)

        return




