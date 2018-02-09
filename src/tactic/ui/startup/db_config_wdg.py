###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['DbConfigPanelWdg', 'DbConfigWdg', 'DbConfigCbk', 'DbConfigSaveCbk']

from pyasm.common import Config, Environment, Common, TacticException
from pyasm.search import DatabaseImpl, Search, SearchType
from pyasm.web import DivWdg, Table
from pyasm.widget import CheckboxWdg, TextWdg, SelectWdg
from pyasm.command import Command
from pyasm.web import WebContainer

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import WizardWdg
from tactic.ui.widget import ActionButtonWdg
from tactic.ui.input import TextInputWdg, PasswordInputWdg

import os
import shutil
import threading


DEFAULTS = {}
DEFAULTS['PostgreSQL'] = {
    'server': 'localhost',
    'port': None,
    'user': 'postgres',
    'password': ''
}
DEFAULTS['Oracle'] = {
    'server': 'localhost',
    'port': 1521,
    'user': '__EMPTY__',   # This should be hidden from the user?
    'password': ''
}
DEFAULTS['MySQL'] = {
    'server': 'localhost',
    'port': None,
    'user': 'root',   # This should be hidden from the user?
    'password': '',
    'encoding': '',
    'charset': ''
}
DEFAULTS['SQLServer'] = {
    'server': 'localhost',
    'port': None,
    'user': 'root',
    'password': ''
}


class DbConfigPanelWdg(BaseRefreshWdg):
    '''Container with a nice border and centered'''

    def get_display(self):
        top = self.top

        top.set_round_corners()
        top.add_style("margin: 20px")

        top.add_border()
        top.add_color("background", "background2", +10)
        top.add_color("color", "color2")

        top.add_style("width: 430px")
        top.add_style("min-height: 500")
        top.add_style("margin-left: auto")
        top.add_style("margin-right: auto")
        top.add_style("padding: 20px")

        config_wdg = DbConfigContentWdg()
        top.add(config_wdg)

        return top



class DbConfigWdg(BaseRefreshWdg):
    '''Container with a nice border and centered'''

    
    def get_display(self):
        top = self.top

        top.add_border()
        top.add_color("background", "background")
        top.add_color("color", "color2")

        top.add_style("width: 100%")
        top.add_style("min-height: 500")
        top.add_style("padding: 10px 0px 20px 0px")

        config_wdg = DbConfigContentWdg()
        top.add(config_wdg)

        return top



class DbConfigContentWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_class("spt_db_config_top")
        top.add_style("width: 430px")
        top.add_style("min-height: 500")
        top.add_style("padding: 15px")
        top.add_style("margin-left: auto")
        top.add_style("margin-right: auto")
        top.add_color("background", "background", -10)
        top.add_border()

        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add("System Configuration Setup")
        title_wdg.add_style("font-size: 20px")


        top.add("<hr/>")

        top.add("<i style='opacity: 0.5'>%s</i><br/>" % Config.get_config_path())
        top.add("<br/>")


        checkin_keys=Config.get_section_values('checkin')
        checkin_keys=checkin_keys.keys()
        save_button = self.get_save_button(checkin_keys)
        top.add(save_button)
        vendor = Config.get_value("database", "vendor")

        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add("<b>Database Setup</b>")
        title_wdg.add_style("margin-bottom: 10px")


        db_select = SelectWdg("database/vendor")
        db_select.set_option("labels", "SQLite|PostgreSQL|MySQL|Oracle|SQLServer")
        db_select.set_option("values", "Sqlite|PostgreSQL|MySQL|Oracle|SQLServer")

        db_select.set_value(vendor)

        db_select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''

        var key;
        if (bvr.src_el.value == 'Sqlite') {
            key = 'Sqlite';
        }
        else if (bvr.src_el.value == 'MySQL') {
            key = 'MySQL';
        }
        else {
            key = 'Other';
        }
        var top = bvr.src_el.getParent(".spt_db_config_top");
        var options_els = top.getElements(".spt_db_options");
        for (var i = 0; i < options_els.length; i++) {
            var vendor = options_els[i].getAttribute("spt_vendor");
            if (vendor == key) {
                spt.show(options_els[i]);
            }
            else {
                spt.hide(options_els[i]);
            }

        }
        '''
        } )
 
        option_div = DivWdg()
        top.add(option_div)
        option_div.add("Vendor: ")
        option_div.add(db_select)
        option_div.add_style("margin: 20px")

        sqlite_wdg = self.get_sqlite_wdg()
        option_div.add(sqlite_wdg)
        mysql_wdg = self.get_mysql_wdg()
        option_div.add(mysql_wdg)        
        otherdb_wdg = self.get_otherdb_wdg()
        option_div.add(otherdb_wdg)

        if vendor == 'Sqlite':
            sqlite_wdg.add_style("display", "")
            otherdb_wdg.add_style("display: none")
            mysql_wdg.add_style("display: none")

        if vendor == 'MySQL':
            mysql_wdg.add_style("display", "")
            otherdb_wdg.add_style("display: none")
            sqlite_wdg.add_style("display: none")
            
        else:
            otherdb_wdg.add_style("display", "")
            mysql_wdg.add_style("display: none")
            sqlite_wdg.add_style("display: none")

        test_button = ActionButtonWdg(title=" Test ", tip="Test connecting to database")
        option_div.add(test_button)
        test_button.add_style("margin-left: auto")
        test_button.add_style("margin-right: auto")
        test_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_db_config_top");
        var values = spt.api.Utility.get_input_values(top, null, false);
        var class_name = 'tactic.ui.startup.DbConfigCbk';
        var server = TacticServerStub.get();
        var kwargs = {};
        var ret_val = server.execute_cmd(class_name, kwargs, values);
        var info = ret_val.info;
        if (info.error) {
            spt.error(info.error);
        }
        else {
            spt.info("Connection to database successful");
        }
        '''
        } )


        #
        # Install
        #
        top.add("<hr/>")

        top.add("<br/>")

        title = "Installation"

        category = "install"

        options = ['default_project']

        if 'tmp_dir' not in options:
            options.append('tmp_dir')



        top.add( self.configure_category(title, category, options) )

        top.add("<hr/>")

        top.add("<br/>")
        top.add("<br/>")

        title = "Asset Management Setup"
        category = "checkin"


        options=checkin_keys[:]

        self._remove_item_from_list(options,'win32_server_handoff_dir')
        self._remove_item_from_list(options,'linux_server_handoff_dir')

        if os.name == "nt":
            options.append('win32_server_handoff_dir')
        else:
            options.append('linux_server_handoff_dir')


        top.add( self.configure_category(title, category, options) )

        top.add("<hr/>")
        top.add("<br/>")

        title = "Mail Server"
        category = "services"
        options = ['mailserver', 'mail_user', 'mail_password', 'mail_port', 
            'mail_tls_enabled', 'mail_sender_disabled']
        top.add( self.configure_category(title, category, options) )

        top.add("<hr/>")

        title = "Services"
        category = "services"
        options = ['process_count', 'process_time_alive', 'thread_count', 
            'python_path','rsync']
        top.add( self.configure_category(title, category, options) )

        top.add("<hr/>")

        title = "Look and Feel"
        category = "look"
        options = ['palette']
        top.add( self.configure_category(title, category, options) )

        top.add("<hr/>")

        title = "Security"
        category = "security"
        options = ['ticket_expiry','authenticate_mode','authenticate_class',
            'authenticate_version','auto_create_user','api_require_password',
            'api_password','max_login_attempt','account_logout_duration',
            'allow_guest','guest_mode']
        options_type = {'ticket_expiry':'string',
            'authenticate_mode':'string','authenticate_class':'string',
            'authenticate_version':'number','auto_create_user':'bool',
            'api_require_password':'bool','api_password':'string',
            'max_login_attempt':'number','account_logout_duration':'number',
            'allow_guest':'bool','guest_mode':'string'}
        top.add( self.configure_category(title, category, options,options_type) )


        #wizard_wdg = WizardWdg()
        #top.add(wizard_wdg)
        #wizard_wdg.add(DivWdg("cow"), "cow")
        #wizard_wdg.add(DivWdg("pig"), "pig")
        #wizard_wdg.add(DivWdg("dog"), "dog")
        return top

    def configure_category(self, title, category, options, options_type = {}):
        div = DivWdg()

        title_wdg = DivWdg()
        div.add(title_wdg)

        #from tactic.ui.widget.swap_display_wdg import SwapDisplayWdg
        #swap = SwapDisplayWdg()
        #div.add(swap)

        title_wdg.add("<b>%s</b>" % title)


        table = Table()
        div.add(table)
        #table.add_color("color", "color")
        table.add_style("color: #000")
        table.add_style("margin: 20px")

        for option in options:
            table.add_row()
            display_title = Common.get_display_title(option)
            td = table.add_cell("%s: " % display_title)
            td.add_style("width: 150px")

            option_type = options_type.get(option)
            validation_scheme = ""

            #add selectWdg for those options whose type is bool
            if option_type == 'bool':
                text = SelectWdg(name="%s/%s" % (category, option))
                text.set_option('values','true|false')
                text.set_option('empty','true')
                text.add_style("margin-left: 0px")

                        
            elif option.endswith('password'):
                text = PasswordInputWdg(name="%s/%s" % (category, option))

            # dealing with options whose type is number   
            else:
                if option_type == 'number':
                    validation_scheme = 'INTEGER'
                    
                else:
                    validation_scheme = ""

                text = TextInputWdg(name="%s/%s" % (category, option), validation_scheme=validation_scheme, read_only="false")
                

            value = Config.get_value(category, option)
            if value:
                text.set_value(value)

            table.add_cell(text)

        return div




    def get_sqlite_wdg(self):
        div = DivWdg()
        div.add_class("spt_db_options")
        div.add_attr("spt_vendor", "Sqlite")
        div.add_style("padding: 20px")

        div.add("Database Folder: ")
        text = TextInputWdg(name="database/sqlite_db_dir")
        div.add(text)


        db_dir = Config.get_value("database", "sqlite_db_dir")
        if not db_dir:
            data_dir = Environment.get_data_dir()
            db_dir = "%s/db" % data_dir

        text.set_value(db_dir)

        return div

    def get_mysql_wdg(self):
        div = self.common_wdg(vendor='MySQL')
        return div

    def get_otherdb_wdg(self):
        div = self.common_wdg(vendor='')
        return div

    def common_wdg(self,vendor):
        div = DivWdg()
        div.add_class("spt_db_options")
        div.add_style("margin: 20px")
        if vendor !='MySQL':
            div.add_attr("spt_vendor", "Other")
        table = Table()
        div.add(table)
        table.add_color("color", "color")


        table.add_row()
        table.add_cell("Server: ")
        text = TextInputWdg(name="server")
        text.set_value("localhost")
        table.add_cell(text)
        server = Config.get_value("database", "server")
        if server:
            text.set_value(server)

        table.add_row()
        table.add_cell("Port: ")
        text = TextInputWdg(name="port")
        table.add_cell(text)
        port = Config.get_value("database", "port")
        if port:
            text.set_value(port)

        table.add_row()
        table.add_cell("Login: ")
        text = TextInputWdg(name="user")
        table.add_cell(text)
        user = Config.get_value("database", "user")
        if user:
            text.set_value(user)

        table.add_row()
        text = PasswordInputWdg(name="password")
        table.add_cell("Password: ")
        table.add_cell(text)
        password = Config.get_value("database", "password")
        if password:
            text.set_value(password)

        if vendor == 'MySQL':
            div.add_attr("spt_vendor", "MySQL")
            table.add_row()
            text = TextInputWdg(name="encoding")
            table.add_cell("Encoding: ")
            table.add_cell(text)
            encoding = Config.get_value("database", "encoding")
            if encoding:
                text.set_value(encoding)

            table.add_row()
            text = TextInputWdg(name="charset")
            table.add_cell("Charset: ")
            table.add_cell(text)
            charset = Config.get_value("database", "charset")
            if charset:
                text.set_value(charset)
        #from pyasm.search import Sql
        #sql.connect()

        return div

    def get_asset_dir_wdg(self):
        div = DivWdg()
        return div

    def _remove_item_from_list(self,the_list,val):
        if val in the_list:
            the_list.remove(val)

    def get_save_button(self,checkin_keys):
        save_button = ActionButtonWdg(title="Save >>", tip="Save configuration and start using TACTIC")
   
        save_button.add_style("float: right")
        save_button.add_behavior( {
            'type': 'click_up',
            'os' : os.name, 
            'checkin_options':checkin_keys,
            'cbjs_action': '''
            
            var top = bvr.src_el.getParent(".spt_db_config_top");
            var failed_els = top.getElements('.spt_input_validation_failed')
            if (failed_els.length > 0){
                spt.alert('One of the fields fail validation. Please correct it before saving')
                return;
            }
            spt.app_busy.show("Saving configuration. Please wait...")
            var values = spt.api.Utility.get_input_values(top, null, false);
            var class_name = 'tactic.ui.startup.DbConfigSaveCbk';
            var server = TacticServerStub.get();
            var kwargs = {checkin_options:bvr.checkin_options};
            try {
                var ret_val = server.execute_cmd(class_name, kwargs, values);
                var info = ret_val.info;
            }
            catch(e) {
                log.critical(spt.exception.handler(e));
                //FIXME: recognize it's a 502 which is normal and pass , otherwise throw the error
                //spt.error(spt.exception.handler(e));
                //spt.app_busy.hide();
                //return;
            }

           
            
            // This means TACTIC was restarted
            
            if (typeof(info) == 'undefined' || bvr.os == 'nt' ) {
                spt.app_busy.show("Restarting TACTIC ...");
                var id = setInterval( function() {
                    var ping_rtn =  server.ping();
                    if (ping_rtn) {
                        window.location = '/tactic';
                        clearInterval(id);
                    }
                  
                }, 5000 );

            }
            else if (info.error) {
                spt.alert(info.error);
                spt.app_busy.hide();
            }
            else {
                window.location = '/tactic';
            }

            '''
            } )
        return save_button




class DbConfigCbk(Command):

    def execute(self):

        # make sure tmp config is unset.
        Config.unset_tmp_config()
        Config.reload_config()

        web = WebContainer.get_web()

        vendor = web.get_form_value("database/vendor")


        if vendor == 'Sqlite':
            db_dir = web.get_form_value("database/sqlite_db_dir")
            database = "sthpw"
            db_path = "%s/%s.db" % (db_dir, database)
            if os.path.exists(db_path):
                return

        elif vendor == 'PostgreSQL':
            self.test_postgres(vendor)
            return

        elif vendor in ['MySQL','SQLServer','Oracle']:
            self.test_postgres(vendor)
            return

        self.info['error'] = "Cannot connect to database"


    def check_database_schema(self):
        pass


    def test_postgres(self, vendor):
        web = WebContainer.get_web()

        defaults = DEFAULTS[vendor]

        default_server = defaults['server']
        default_port = defaults['port']
        default_user = defaults['user']
        default_password = defaults['password']

        server = web.get_form_value("server")
        if not server:
            server = default_server
        port = web.get_form_value("port")
        if not port:
            port = default_port
        else:
            port = int(port)
        user = web.get_form_value("user")
        if not user:
            user = default_user
        password = web.get_form_value("password")
        if not password:
            password = default_password

        # Need to access remote database
        create = False
        impl = DatabaseImpl.get(vendor)
        exists = impl.database_exists("sthpw", host=server, port=port)

        if not create:
            if not exists:
                self.info['error'] = "Database [sthpw] does not exist.  This is required for TACTIC to function."

                return

        else:
            print "Running bootstrap"

            install_dir = Environment.get_install_dir()
            python = Config.get_value("services", "python")
            if not python:
                python = "python"

            # create the database and inject the bootstrap data
            impl.create_database("sthpw", host=server, port=port)

            cmd = "%s %s/src/pyasm/search/upgrade/%s/bootstrap_load.py" % (python, install_dir, vendor.lower())
            os.system(cmd)




        from pyasm.search import Sql
        sql = Sql("sthpw", server, user, password=password, vendor=vendor, port=port)
        try:
            # attempt
            sql.connect()
            sql.do_query("select id from transaction_log limit 1")
        except Exception as e:
            self.info['error'] = "Could not connect to database with (vendor=%s, server=%s, user=%s, port=%s)" % (vendor, server, user, port)
            self.info['message'] = str(e)
            print e



class DbConfigSaveCbk(Command):

    def execute(self):
        self.section = None

        # make sure tmp config is unset.
        Config.unset_tmp_config()
        Config.reload_config()

        web = WebContainer.get_web()

        # read the current config file.


        # copy config to the path
        config_path = Config.get_config_path()
        if not os.path.exists(config_path):
            print "Installing default config file"

            dirname = os.path.dirname(config_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            if os.name == 'nt':
                osname = 'win32'
            else:
                osname = 'linux'

            install_dir = Environment.get_install_dir()
            install_config_path = "%s/src/install/start/config/tactic_%s-conf.xml" % ( install_dir, osname)

            shutil.copy(install_config_path, dirname)

        try:
            self.configure_db()
            self.configure_install()
            self.configure_mail_services()
            self.configure_gen_services()
            self.configure_asset_dir()
            self.configure_palette()
            self.configure_security()
        except Exception as e:
            raise TacticException('Error in [%s]: %s'%(self.section, e.__str__()))
        # FIXME: if this all fails, then revert back
        
        self.save_config()

        # after saving the config, test the database
        self.load_bootstrap()

        # remove the first run file
        data_dir = Environment.get_data_dir()
        path = "%s/first_run" % data_dir
        if os.path.exists(path):
            os.unlink(path)


        self.restart_program()


    

    def restart_program(self):
        '''Restarts the current program.'''
        import sys
        python = sys.executable
        # for windows
        python = python.replace('\\','/')
        if os.name =='nt':
            import subprocess
            subprocess.Popen([python, sys.argv])
            pid = os.getpid()
            kill = KillProcessThread(pid)
            kill.start()
        else:
            os.execl(python, python, * sys.argv)



    def load_bootstrap(self):
        impl = DatabaseImpl.get()
        exists = impl.database_exists("sthpw")
        print "exists: ", exists

        vendor = impl.get_database_type()

        if not exists:
            print "Running bootstrap"

            install_dir = Environment.get_install_dir()
            python = Config.get_value("services", "python")
            if not python:
                python = "python"

            # create the database and inject the bootstrap data
            impl.create_database("sthpw")

            cmd = "%s %s/src/pyasm/search/upgrade/%s/bootstrap_load.py" % (python, install_dir, vendor.lower())
            os.system(cmd)





    def configure_install(self):
        self.section = 'Installation'
        web = WebContainer.get_web()

        default_project = web.get_form_value("install/default_project")
        tmp_dir = web.get_form_value("install/tmp_dir")

        if default_project:
            Config.set_value("install", "default_project", default_project)
        else:
            Config.remove("install", "default_project")

        if tmp_dir:
            Config.set_value("install", "tmp_dir", tmp_dir)
        else:
            Config.set_value("install", "tmp_dir", '')


    def configure_db(self):

        self.section = 'Database Setup'
        web = WebContainer.get_web()

        vendor = web.get_form_value("database/vendor")
        if not vendor:
            raise TacticException("A vendor needs to be passed in.")

        if vendor == 'Sqlite':
            # take the current files and copy them to the database folder
            db_dir = web.get_form_value("database/sqlite_db_dir")
            if not db_dir:
                raise TacticException("No Folder configured for Sqlite Database")

            if not os.path.exists(db_dir):
                os.makedirs(db_dir)

            # check to see if the sthpw database is in this folder
            sthpw_path = "%s/sthpw.db" % (db_dir)
            if not os.path.exists(sthpw_path):
                # copy the default database over
                install_dir = Environment.get_install_dir()
                template_db = "%s/src/install/start/db/sthpw.db" % install_dir
                shutil.copy(template_db, db_dir)

            Config.set_value("database", "sqlite_db_dir", db_dir)

            Config.remove("database", "server")
            Config.remove("database", "port")
            Config.remove("database", "user")
            Config.remove("database", "password")


        else:

            defaults = DEFAULTS[vendor]

            default_server = defaults['server']
            default_port = defaults['port']
            default_user = defaults['user']
            default_password = defaults['password']

            Config.remove("database", "sqlite_db_dir")

            if vendor == 'MySQL':
                default_encoding = defaults['encoding']
                default_charset= defaults['charset']

                encoding = web.get_form_value("encoding")
                if not encoding:
                    encoding = default_encoding
                if encoding:
                    Config.set_value("database", "encoding", encoding)
                else:
                    Config.set_value("database", "encoding", "")

                charset = web.get_form_value("charset")
                if not charset:
                    charset = default_charset
                if charset:
                    Config.set_value("database", "charset", charset)
                else:
                    Config.set_value("database", "charset", "")                    

            # get the info
            server = web.get_form_value("server")
            if not server:
                server = default_server
            port = web.get_form_value("port")
            if not port:
                port = default_port
            else:
                port = int(port)
            user = web.get_form_value("user")
            if not user:
                user = default_user
            password = web.get_form_value("password")
            if not password:
                password = default_password


            if server:
                Config.set_value("database", "server", server)
            else:
                #Config.remove("database", "server")
                Config.set_value("database", "server", "")

            if port:
                Config.set_value("database", "port", port)
            else:
                #Config.remove("database", "port")
                Config.set_value("database", "port", "")

            if user:
                Config.set_value("database", "user", user)
            else:
                #Config.remove("database", "user")
                Config.set_value("database", "user", "")

            if password:
                Config.set_value("database", "password", password)
            else:
                Config.set_value("database", "password", "")
                #Config.remove("database", "password")

        # save the database
        Config.set_value("database", "vendor", vendor)



    def configure_asset_dir(self):
        self.section = 'Asset Management Setup'

        web = WebContainer.get_web()
        keys = web.get_form_keys()
        option_list = []
        for key in keys:
            if key.startswith('checkin/'):
                key = key.replace('checkin/','')
                option_list.append(key)
  
        asset_dir = web.get_form_value("checkin/asset_base_dir")
        if asset_dir != None:
            if asset_dir and not os.path.exists(asset_dir):
                os.makedirs(asset_dir)
            Config.set_value("checkin", "asset_base_dir", asset_dir)

        if 'asset_base_dir' in option_list:
            option_list.remove('asset_base_dir')

        for item_dir in option_list:
            item_in_list=web.get_form_value('checkin/%s'%item_dir)
            if item_in_list:
                Config.set_value("checkin", '%s'%item_dir, item_in_list)
            else:
                Config.set_value("checkin", '%s'%item_dir, "")

    def configure_palette(self):
        self.section = 'Look and Feel'
        web = WebContainer.get_web()
        palette = web.get_form_value("look/palette")

        if palette:
            Config.set_value("look", "palette", palette)
        else:
            Config.set_value("look", "palette", "")
            #Config.remove("look", "palette")


    def configure_mail_services(self):
        self.section = 'Mail Server'
        web = WebContainer.get_web()

        options = ['server', '_user', '_password', '_port', '_tls_enabled','_sender_disabled']
        for option in options:
            server = web.get_form_value("services/mail%s" %option)

            if server:
                Config.set_value("services", "mail%s" %option, server)
            else:
                #Config.remove("services", "mail%s"%option)
                Config.set_value("services", "mail%s"%option,  "")

    def configure_gen_services(self):
        self.section = 'Services'
        web = WebContainer.get_web()

        options = ['process_count', 'process_time_alive', 'thread_count', 'python_path','rsync']
        for option in options:
            value = web.get_form_value("services/%s" %option)

            if value:
                Config.set_value("services", option, value)
            else:
                
                Config.set_value("services", option,  "")



    def configure_security(self):
        self.section = 'Security'
        web = WebContainer.get_web()

        options = ['allow_guest','ticket_expiry','authenticate_mode',
            'authenticate_class','authenticate_version','auto_create_user',
            'api_require_password','api_password','max_login_attempt','account_logout_duration']
        for option in options:
            security_value = web.get_form_value("security/%s" %option)

            if security_value:
                Config.set_value("security", option, security_value)
            else:
                Config.set_value("security", option,  "")



    def save_config(self):
        Config.save_config()
        Config.reload_config()

class KillProcessThread(threading.Thread):
    '''Kill a Windows process'''
    def __init__(self, pid):
        super(KillProcessThread, self).__init__()
        self.pid = pid

    def run(self):
        """kill function for Win32 prior to Python2.7"""
        import time
        # pause for the DbConfigSaveCbk to finish first
        time.sleep(2)
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, self.pid)
        return (0 != kernel32.TerminateProcess(handle, 0))

