from pyasm.command import Command
from pyasm.common import Environment, Common
from pyasm.biz import Project
from pyasm.security import Sudo, Site
from pyasm.search import Search

import datetime
import os
import subprocess

__all__ = ['SiteUpgradeCmd']


class SiteUpgradeCmd(Command):
    
    def execute(self):
        '''Update the Plugins and Database of this project'''
        sudo = Sudo()
        from tactic.command import PluginUninstaller, PluginInstaller
        
        project_code = self.kwargs.get("project_code") or None
        site = self.kwargs.get("site") or None
        db_update = self.kwargs.get("db_update") or None
        plugin_update = self.kwargs.get("plugin_update") or {}
        tmp_dir = "%s/upgrade" % Environment.get_tmp_dir()
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        if site:
            update_status_path = "%s/upgrade_%s_%s.txt" % (tmp_dir, site, project_code)
        else:
            update_status_path = "%s/upgrade_default_%s.txt" % (tmp_dir, project_code)
        Site.set_site(site)
        Project.set_project(project_code)

        if db_update:
            install_dir = Environment.get_install_dir()
            upgrade_db_path = "%s/src/bin/upgrade_db.py" % install_dir

            python = Common.get_python()

            if not site:
                site = "default"

            for x in db_update:          
                args = [python, upgrade_db_path, "-y", "-p", x, "-s", site]
                subprocess.run(args)
                
        for code, data in plugin_update.items():
            update_status_f = open(update_status_path, 'w')
            update_status_f.write("start")
            update_status_f.close()

            plugin_dir = data[0]
            latest_version = data[1]
            log_path = "%s/upgrade_log.txt" % plugin_dir

            print("Uninstalling plugin: ", plugin_dir)
            uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
            uninstaller.execute()
            
            print("Installing plugin: ", plugin_dir)
            installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True, version=latest_version)
            installer.execute()

            log_f = open(log_path, 'a')
            log_f.write("Plugin Updated to version %s: %s\n" % (latest_version, datetime.datetime.now()))
            log_f.close()

            update_status_f = open(update_status_path, 'w')
            update_status_f.write("end")
            update_status_f.close()
        
        
        sudo.exit()
        return
