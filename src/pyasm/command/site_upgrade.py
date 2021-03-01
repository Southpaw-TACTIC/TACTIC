from pyasm.command import Command
from pyasm.common import Environment, Common
from pyasm.biz import Project
from pyasm.security import Sudo, Site
from pyasm.search import Search, SearchType
            

import datetime
import os
import subprocess

__all__ = ['SiteUpgradeCmd']


class SiteUpgradeCmd(Command):
    
    def execute(self):
        '''Update the Plugins and Database of this project'''
        from tactic.command import PluginUninstaller, PluginInstaller

        project_code = self.kwargs.get("project_code") or None
        site = self.kwargs.get("site") or "default"
        db_update = self.kwargs.get("db_update") or None
        plugin_update = self.kwargs.get("plugin_update") or {}
        plugin_order = self.kwargs.get("plugin_order") or {}
        sorted_order = sorted(plugin_order.keys())
        upgrade_status_path = self.kwargs.get("upgrade_status_path")
            

        # Determine tmp dir for plugin upgrade path 
        if not site or site == "default":
            site_tmp_dir = Environment.get_tmp_dir()
        else:
            site_obj = Site.get()
            site_tmp_dir = site_obj.get_site_dir(site)
        
        try:
            sudo = Sudo()
            Site.set_site(site)
            Project.set_project(project_code)
            if db_update:
                install_dir = Environment.get_install_dir()
                upgrade_db_path = "%s/src/bin/upgrade_db.py" % install_dir

                python = Common.get_python()
                for x in db_update:          
                    args = [python, upgrade_db_path, "-f", "-y", "-p", x, "-s", site]
                    subprocess.call(args)
               

            # Uninstall in reverse order 
            reverse_order = list(sorted_order)
            reverse_order.reverse()
            for order in reverse_order:
                codes = plugin_order[order]
                for code in codes:
                    data = plugin_update[code]
                    plugin_dir = data[0]

                    print("Uninstalling plugin: ", plugin_dir)
                    uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
                    uninstaller.execute()
                    
            # Install in order
            for order in sorted_order:
                codes = plugin_order[order]
                for code in codes:
                    data = plugin_update[code]
                    plugin_dir = data[0]
                    latest_version = data[1]

                    print("Installing plugin: ", plugin_dir)
                    installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True, version=latest_version)
                    installer.execute()

                    plugin_name = code.replace("/", "_")
                    log_path = "%s/%s_upgrade.txt" % (site_tmp_dir, plugin_name)
                    log_f = open(log_path, 'a')
                    log_f.write("Plugin Updated to version %s: %s\n" % (latest_version, datetime.datetime.now()))
                    log_f.close()
               
        except Exception as e:
            self.set_upgrade_status(project_code, site, "fail")

            from pyasm.search import ExceptionLog
            ExceptionLog.log(e)
            raise
        finally:
            sudo.exit()
        
        self.set_upgrade_status(project_code, site, "end")

    def get_upgrade_status(self, project, site):
        try:
            sudo = Sudo()
            Site.set_site(site)
            message = Search.get_by_code("sthpw/message", "SPT_SITE_UPGRADE")
            if message:
                upgrade_status = message.get_value("message")
            else:
                message = SearchType.create("sthpw/message")
                message.set_value("code", "SPT_SITE_UPGRADE")
                
                upgrade_status = "end"
                message.set_value("message", upgrade_status)
                
                message.commit()
           
        
        finally:
            sudo.exit()
            Site.pop_site()
            
        return upgrade_status


    def set_upgrade_status(self, project, site, upgrade_status):
        try:
            sudo = Sudo()
            Site.set_site(site)
            message = Search.get_by_code("sthpw/message","SPT_SITE_UPGRADE")
            if not message:
                message = SearchType.create("sthpw/message")
                message.set_value("code", "SPT_SITE_UPGRADE")

            message.set_value("message", upgrade_status) 
            message.commit()
        finally:
            sudo.exit()
            Site.pop_site()
