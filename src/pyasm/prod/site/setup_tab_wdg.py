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

__all__ = ["SetupTabWdg"]

from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *


class SetupTabWdg(Widget):

    def init(my):

        #tab = TabWdg(css=TabWdg.SMALL)
        tab = TabWdg()
        tab.set_tab_key("setup_tab")
        my.tab = tab
        my.handle_tab(tab)
        my.add(tab, "tab")


    def handle_tab(my, tab):

        my.tab_names = ["Overview", "Users", "Create Project", "Pipeline", "Asset Libraries", "Asset Creation", "Sequence Creation", "Shot Creation", "Finished"]
        
        tab.add(my.get_overview_wdg, _("Overview") )
        tab.add(my.get_user_wdg, _("Users") )
        tab.add(my.get_project_wdg, _("Create Project") )
        tab.add(my.get_pipeline_wdg, _("Pipeline") )
        tab.add(my.get_asset_library_wdg, _("Asset Libraries") )
        tab.add(my.get_asset_wdg, _("Asset Creation") )
        tab.add(my.get_sequence_wdg, _("Sequence Creation") )
        tab.add(my.get_shot_wdg, _("Shot Creation") )
        tab.add(my.get_finished_wdg, _("Finished") )




    def get_next_button_wdg(my, current_tab):

        index = my.tab_names.index(current_tab)
        redirect_tab = my.tab_names[index+1]


        button = IconSubmitWdg("Next", IconWdg.ARROW_RIGHT, long=True, icon_pos="right")
        redirect_tab_dict = {"setup_tab": redirect_tab}
        button.add_event("onclick", my.tab.get_redirect_script(redirect_tab_dict) )
        button.add_style("float: right")
        return button



    def get_overview_wdg(my):
        widget = Widget()
        widget.add( my.get_next_button_wdg("Overview") )

        widget.add("<h1>Welcome to TACTIC</h1>")
        widget.add("<h3>Now that you have successfully installed the software, you can take the next step to create and set up a project.</h3>")

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("padding: 0 20 0 20")

        div.add("<p><b>The following tabs describe the general steps required to set up a production</b></p>")
 
        div.add("<ol><li>Create Users</li>")
        div.add("<li>Create a Project</li>")
        div.add("<li>Create a Pipeline</li>")
        div.add("<li>Create an Asset Library</li>")
        div.add("<li>Create an Asset</li>")
        div.add("<li>Create a Sequence</li>")
        div.add("<li>Create a Shot</li>")
        div.add("<li>Plan Shots</li></ol>")

        widget.add(div)

        return widget


    def get_user_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("padding: 0 20 0 20")
        div.add('''<p>Create users here</p>''')
        
        widget.add( my.get_next_button_wdg("Users") )
        widget.add( HtmlElement.br(2))
        widget.add(div)

        search = Search("sthpw/login")
        table = TableWdg("sthpw/login")
        table.set_search(search)
        widget.add(table)
        return widget



    def get_project_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("padding: 0 20 0 20")
        widget.add( my.get_next_button_wdg("Create Project") )
        widget.add( HtmlElement.br(2))
        div.add('''<p>Create some users.</p>
        ''')
        widget.add(div)



        from pyasm.admin.creator import PipelineEditorWdg

        search = Search("sthpw/project")
        table = TableWdg("sthpw/project")
        table.set_search(search)
        widget.add(table)
        return widget


    def get_pipeline_wdg(my):
        widget = Widget()

        from pyasm.admin.creator import PipelineEditorWdg

        widget.add( my.get_next_button_wdg("Pipeline") )
        widget.add( HtmlElement.br(2))

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("height: 3em")
        div.add_style("padding: 10 20 10 20")
        div.add('You can create pipelines here. For more information on pipeline and this UI, please consult the ')
        icon = IconWdg(icon=IconWdg.HELP)
        data = 'Pipeline documentation %s.' %icon.get_buffer_display()
        link = HtmlElement.href(data=data, ref="/doc/general/pipeline.html", target='_blank')
        div.add(link)
        
        widget.add(div)
        widget.add(PipelineEditorWdg())
       
        return widget


    def get_asset_library_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("height: 3em")
        div.add_style("text-align: left")
        div.add_style("padding: 10 20 10 20")
        widget.add( my.get_next_button_wdg("Asset Libraries") )
        widget.add( HtmlElement.br(2))
        div.add('You can create asset libraries here.  These asset libraries categorize the assets.  Examples include characters, props, or locations.  For more information, please refer to the ')
        
        icon = IconWdg(icon=IconWdg.HELP)
        data = 'documentation %s.' %icon.get_buffer_display()
        link = HtmlElement.href(data=data, ref="/doc/production/asset_library.html", target='_blank')
        div.add(link)

        div.add('for creating asset libraries.  Asset Libraries are managed in the " Asset Pipeline -> Asset Libraries " tab.')

        widget.add(div)

        search = Search("prod/asset_library")
        table = TableWdg("prod/asset_library" )
        table.set_search(search)

        widget.add(table)

        return widget


    def get_asset_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("padding: 10 20 10 20")
        widget.add( my.get_next_button_wdg("Asset Creation") )
        widget.add( HtmlElement.br(2))

        icon = IconWdg(icon=IconWdg.HELP)
        data = 'documentation %s.' %icon.get_buffer_display()
        link = HtmlElement.href(data=data, ref="/doc/production/asset_list.html", target='_blank')
        
        div.add('Create a few assets.  For more information, please refer to the ')
        div.add(link) 
        div.add('for creating assets.  Assets are usually created in the " Asset Pipeline -> Asset List " tab')
        widget.add(div)

        search = Search("prod/asset")
        table = TableWdg("prod/asset", "manage")
        table.set_search(search)

        widget.add(table)

        return widget


    def get_sequence_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("height: 3em")
        div.add_style("padding: 10 20 10 20")
        widget.add( my.get_next_button_wdg("Sequence Creation") )
        widget.add( HtmlElement.br(2))
        div.add('You can create sequences here. For more information on creating sequence, please consult the ')
        icon = IconWdg(icon=IconWdg.HELP)
        data = 'Sequence documentation %s' %icon.get_buffer_display()
        link = HtmlElement.href(data=data, ref="/doc/production/sequence.html", target='_blank')
        div.add(link)
        
        widget.add(div)

        search = Search("prod/sequence")
        table = TableWdg("prod/sequence" )
        table.set_search(search)

        widget.add(table)

        return widget


    def get_shot_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("padding: 0 20 0 20")
        widget.add( my.get_next_button_wdg("Shot Creation") )
        widget.add( HtmlElement.br(2))
        div.add('''<p>Create a shot.</p>''') 
        

        widget.add(div)

        search = Search("prod/shot")
        table = TableWdg("prod/shot", "manage" )
        table.set_search(search)

        widget.add(table)

        return widget



    def get_finished_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        div.add_style("font-size: 1.4em")
        div.add_style("text-align: left")
        div.add_style("padding: 30")
        div.add("Congratulations...<br/><br/>")

        div.add("You have completed the initial set-up for a project.  You can now go to this project's site and explore.  Until you become familiar with the full interface, you can always come back here and make changes or additions.")

        widget.add(div)

        return widget


