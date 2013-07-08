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

__all__ = ["MayaTabWdg"]

from pyasm.biz import PrefSetting
from pyasm.web import Widget, HtmlElement, WebContainer
from pyasm.widget import UndoButtonWdg, RedoButtonWdg, IconRefreshWdg, HiddenWdg, GeneralAppletWdg, BaseTabWdg
from tactic.ui.app import UndoLogWdg
from pyasm.prod.web import *
from pyasm.common import Container


class MayaTabWdgImpl(TabWdg):
    def add_event_to_header(my, tab_name, link):
        # disable this for performance reasons
        check_in_tabs = ["Checkin", "Custom", "Anim Checkin", "Layer Checkin", "Shot"]
        if tab_name in check_in_tabs:
            link.add_event("onclick", "introspect()", 0)


class MayaTabWdg(BaseTabWdg):

    def init(my):

        help = HelpItemWdg('Loader', 'The Loader lets you load 3D assets into your 3D applications. Among many options, you can choose to either reference, import, or open the asset through http or the internal file system.')
        my.add(help)

        pref = PrefSetting.get_value_by_key("use_java_maya")
        app = WebContainer.get_web().get_app_name_by_uri()
        
        if app == "Maya":
            if not Container.get('GeneralAppletWdg'):
                my.add( GeneralAppletWdg() )
                Container.put('GeneralAppletWdg', True)
        site_menu = SiteMenuWdg()
        site_menu.add_style("float", "right")
        site_menu.add_style("margin-top", "-2px")
        my.add(site_menu)
        
        WebContainer.add_js('MayaWebTools.js')
        WebContainer.add_js('PyMaya.js')
        
        tab = MayaTabWdgImpl()
        tab_value = tab.set_tab_key("maya_tab")
        #my.handle_tab(tab)
        #my.add(tab,"tab")
        my.setup_tab("maya_tab", tab=tab)
        my.add( ProgressWdg() )

    def handle_tab(my, tab):
        tab.add(MayaLoadWdg, _("Loader") )
        #tab.add(MayaNamespaceWdg, "Namespace")
        tab.add(MayaAssetCheckinWdg, _("Checkin") )
        #tab.add(CustomCheckinWdg, _("Custom") )
        tab.add(MayaSetWdg, _("Sets") )
        tab.add(MayaAnimLoadWdg, _("Instance Loader") )
        tab.add(MayaAnimCheckinWdg, _("Instance Checkin") )
        #tab.add(MayaLayerLoadWdg, "Layer Loader")
        #tab.add(SObjectCheckinWdg, "Layer Checkin")
        tab.add(MayaShotCheckinWdg, _("Shot") )
        tab.add(SessionWdg, _("Session") )
        tab.add(PublishLogWdg, _("Log") )
        tab.add(my.get_undo_wdg, _("Undo") )
        #tab.add(AppSetupWizardWdg, _("Setup") )


    def get_undo_wdg(my):
        widget = UndoLogWdg()
        return widget



from pyasm.prod.web import ProdIconButtonWdg

class AppSetupWizardWdg(Widget):

    def get_display(my):
        widget = Widget()

        app = "Maya"

        widget.add("<h3>Application Setup Wizard</h3>")
        block = HtmlElement.blockquote()


        block.add("<p>Step 1: Launch %s (or start with a new session)</p>" % app)

        # sphere test
        block.add("<p>Step 2: Sphere test</p>")

        sphere_button = ProdIconButtonWdg("Sphere")
        sphere_button.add_event("onclick", "app.mel('sphere')")
        block.add( sphere_button)
        block.add( "If a sphere appears when clicking on this button, then the Maya connector is functiioning")

        block.add("<p>Step 3: Introspection</p>")

        introspect_button = ProdIconButtonWdg("Introspect")
        introspect_button.add_event("onclick", "introspect()")
        block.add( introspect_button)
 
        block.add("<p>Step 4: Create C:/temp/sthpw</p>")

        block.add("<p>Step 5: Check in Sphere</p>")

        block.add("<p>Step 6: Load Sphere</p>")

        widget.add(block)

        return widget


