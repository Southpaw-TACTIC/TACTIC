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

from pyasm.common import Environment, jsonloads, jsondumps, TacticException, Common
from pyasm.web import DivWdg, Table
from pyasm.widget import IconWdg, TextWdg, SelectWdg, CheckboxWdg, RadioWdg, TextAreaWdg, HiddenWdg
from pyasm.command import Command
from pyasm.search import SearchType, Search
from pyasm.biz import File, Project, FileGroup, FileRange, Snapshot, ProjectSetting
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import DialogWdg
from tactic.ui.widget import IconButtonWdg

from tactic.ui.input import UploadButtonWdg, TextInputWdg
from tactic.ui.widget import ActionButtonWdg

from tactic_client_lib import TacticServerStub

import os
import os.path
import re
import shutil

import six
basestring = six.string_types


__all__ = ['IngestUploadWdg', 'IngestCheckCmd', 'IngestUploadCmd']


class IngestUploadWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'base_dir': 'Base directory to check into',
        'search_type': 'Search Type to ingest into',
        'parent_key': 'Parent search key to relate create sobject to',
        'process': 'The default process to ingest into',
        'context': 'Fixed context to ingest into',
        'ingest_data_view': 'Specify a ingest data view, defaults to edit',
        'extra_data': 'Extra data (JSON) to be added to created sobjects',
        'oncomplete_script_path': 'Script to be run on a finished ingest',
        'update_mode': 'Takes values "true" or "false".  When true, uploaded files will update existing file iff exactly one file exists already with the same name.',
        'context_mode': 'Set or remove context case sensitivity.',
        'hidden_options': 'Comma separated list of hidden settings i.e. "process,context_mode"',
        'title': 'The title to display at the top',
        'library_mode': 'Mode to determine if Ingest should handle huge amounts of files',
        'dated_dirs': 'Determines update functionality, marked true if relative_dir is timestamped',
        'update_process': 'Determines the update process for snapshots when the update_mode is set to true and one sobject is found',
        'ignore_path_keywords': 'Comma separated string of path keywords to be hidden',
        'project_code': 'Publish to another project',
        'keyword_mode': 'Takes values "simplified" and "none". When "simplified", keywords will not be extracted from file name. When "none", keywords will notbe ingested into sobject.',
        'create_icon': 'determines if an icon is created or not'
    }


    def get_display(self):

        self.sobjects = self.kwargs.get("sobjects")

        # if search_keys are passed in, then these are used to copy
        search_keys = self.kwargs.get("search_keys")
        # add a project to copy to.  Check that it is permitted
        self.project_code = self.kwargs.get("project_code")

        if search_keys:
            self.sobjects = Search.get_by_search_keys(search_keys)

            projects = Project.get_user_projects()
            project_codes = [x.get_code() for x in projects]
            if self.project_code not in project_codes:
                self.project_code = None



        asset_dir = Environment.get_asset_dir()

        base_dir = self.kwargs.get("base_dir")
        if base_dir:
            if not base_dir.startswith(asset_dir):
                raise Exception("Path needs to be in asset root")
            else:
                relative_dir = base_dir.replace(asset_dir, "")
                relative_dir = relative_dir.strip("/")
        else:
            relative_dir = self.kwargs.get("relative_dir")

        self.relative_dir = relative_dir


        # This is used to check into a search key (not create a new sobject)
        self.orig_sobject = None
        self.search_key = self.kwargs.get("search_key") or ""
        if self.search_key:
            self.sobject = Search.get_by_search_key(self.search_key)

            if self.kwargs.get("use_parent") in [True, 'true']:
                self.orig_sobject = self.sobject
                self.sobject = self.sobject.get_parent()
                self.search_key = self.sobject.get_search_key()

            self.search_type = self.sobject.get_search_type()

            self.show_settings = self.kwargs.get("show_settings")
            if self.show_settings in [False, 'false']:
                self.show_settings = False
            elif self.show_settings in [True, 'true']:
                self.show_settings = True


        else:
            self.search_type = self.kwargs.get("search_type")
            self.sobject = None
            self.search_key = None

            self.show_settings = self.kwargs.get("show_settings")
            if self.show_settings == None or self.show_settings in [True, 'true']:
                self.show_settings = True
            elif self.show_settings in [False, 'false']:
                self.show_settings = False


        top = self.top
        top.add_class("spt_ingest_top")



        hidden = HiddenWdg(name="parent_key")
        #hidden = TextWdg(name="parent_key")
        top.add(hidden)
        hidden.add_class("spt_parent_key")

        if self.search_key:
            hidden.set_value(self.search_key)




        table = Table()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add( self.get_content_wdg() )

        if not self.search_key or self.show_settings:
            right = table.add_cell()
            right.add_class("spt_right_content")
            right.add_style("vertical-align: top")
            right.add( self.get_settings_wdg() )
            if self.show_settings in [False, 'false', 'hidden']:
                right.add_style("display: none")


            process = self.kwargs.get("process")
            if process:
                hidden = HiddenWdg(name="process")
                right.add(hidden)
                hidden.add_class("spt_process")
                hidden.set_value(process)





        else:
            if self.orig_sobject and self.orig_sobject.column_exists("process"):
                hidden = HiddenWdg(name="process")
                top.add(hidden)
                hidden.add_class("spt_process")
                process = self.orig_sobject.get_value("process")
                hidden.set_value(process)

            elif self.kwargs.get("process"):
                process = self.kwargs.get("process")
                hidden = HiddenWdg(name="process")
                top.add(hidden)
                hidden.add_class("spt_process")
                hidden.set_value(process)



        return top


    def get_file_wdg(self, sobject=None):

        # template for each file item
        file_template = DivWdg()
        if not sobject:
            file_template.add_class("spt_upload_file_template")
            file_template.add_style("display: none")
            file_template.add_class("SPT_TEMPLATE")
        else:
            file_template.add_class("spt_upload_file")

        file_template.add_style("overflow: hidden")
        file_template.add_style("margin-bottom: 3px")
        file_template.add_style("padding: 3px")
        file_template.add_style("height: 40px")

        thumb_div = DivWdg()
        file_template.add(thumb_div)
        thumb_div.add_style("float: left")
        thumb_div.add_style("width: 60")
        thumb_div.add_style("height: 40")
        thumb_div.add_style("overflow: hidden")
        thumb_div.add_style("margin: 3 10 3 0")
        thumb_div.add_class("spt_thumb")



        info_div = DivWdg()
        file_template.add(info_div)
        info_div.add_style("float: left")

        name_div = DivWdg()
        name_div.add_class("spt_name")
        info_div.add(name_div)
        name_div.add_style("width: 225px")
        name_div.add_style("overflow-x: hidden")
        name_div.add_style("text-overflow: ellipsis")



        date_div = DivWdg()
        date_div.add_class("spt_date_label")
        info_div.add(date_div)
        date_div.add("")
        date_div.add_style("opacity: 0.5")
        date_div.add_style("font-size: 0.8em")
        date_div.add_style("font-style: italic")
        date_div.add_style("margin-top: 3px")

        hidden_date_div = HiddenWdg("date")
        hidden_date_div.add_class("spt_date")
        info_div.add(date_div)



        size_div = DivWdg()
        size_div.add_class("spt_size")
        file_template.add(size_div)
        size_div.add_style("float: left")
        size_div.add_style("width: 150px")
        size_div.add_style("text-align: right")

        remove_div = DivWdg()
        remove_div.add_class("spt_remove")
        file_template.add(remove_div)
        icon = IconButtonWdg(title="Remove", icon="FA_TIMES")
        icon.add_style("float: right")
        remove_div.add(icon)
        #remove_div.add_style("text-align: right")



        if sobject:
            from pyasm.common import FormatValue
            from tactic.ui.panel import ThumbWdg2


            if sobject.get_base_search_type() != "sthpw/snapshot":
                search_code = sobject.get_code()
                search = Search("sthpw/snapshot")
                search.add_filter("search_code", search_code)
                search.add_filter("is_latest", True)
                snapshot = search.get_sobject()
            else:
                snapshot = sobject

            thumb = ThumbWdg2()
            thumb_div.add(thumb)
            thumb.set_sobject(snapshot)
            lib_path = thumb.get_lib_path()

            name = os.path.basename(lib_path)
            name = re.sub(r"_v\d+", "", name)


            if sobject.get_base_search_type() == "sthpw/snapshot":
                if sobject.get("snapshot_type") == "sequence":
                    paths = sobject.get_expanded_lib_paths()
                    file_range = sobject.get_file_range()
                    size = 0
                    for path in paths:
                        size += os.path.getsize(path)
                    name = "%s (%s)" % (name, file_range.get_display())
                else:
                    size = os.path.getsize(lib_path)

            else:
                size = os.path.getsize(lib_path)


            name_div.add( name )

            size = FormatValue().get_format_value(size, "KB")
            size_div.add(size)

            file_template.add_attr("spt_search_key", sobject.get_search_key())

        else:
            # example data
            size_div.add("433Mb")
            name_div.add("image001.jpg")

        return file_template



    def get_settings_wdg(self):

        div = DivWdg()
        div.add_style("width: 400px")
        div.add_style("padding: 20px")
        # div.add_style("max-height: 510px")
        div.add_style("overflow: auto")
        div.add_style("margin-bottom: 20px")

        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Ingest Settings")
        title_wdg.add_style("font-size: 25px")

        # Build list of process names
        process_names = set()
        from pyasm.biz import Pipeline
        from pyasm.widget import SelectWdg
        search_type_obj = SearchType.get(self.search_type)
        base_type = search_type_obj.get_base_key()


        pipeline_search = Search("sthpw/pipeline")
        if self.sobject and self.sobject.column_exists("pipeline_code"):
            pipeline_code = self.sobject.get_value("pipeline_code")
            if pipeline_code:
                pipeline_search.add_filter("code", pipeline_code)
            else:
                pipeline_search.set_null_filter()
        else:
            pipeline_search.add_project_filter()
            pipeline_search.add_filter("search_type", base_type)

        pipelines = pipeline_search.get_sobjects()
        for pipeline in pipelines:
            process_names.update(pipeline.get_process_names())

        selected_process = self.kwargs.get("process")
        if selected_process:
            process_names.add(selected_process)

        if process_names:
            process_names = list(process_names)
            process_names.sort()
        else:
            process_names = []

        """
        if process_names:
            process_names.append("---")
        process_names.append("publish")
        process_names.append("icon")
        """


        hidden_options = self.kwargs.get("hidden_options").split(',')

        process_wdg = DivWdg()
        div.add(process_wdg)

        title_wdg = DivWdg()
        process_wdg.add(title_wdg)
        title_wdg.add("Process")
        title_wdg.add_style("margin-top: 20px")
        title_wdg.add_style("font-size: 16px")

        process_wdg.add("<br/>")

        select = SelectWdg("process")
        process_wdg.add(select)
        select.set_option("values", process_names)
        select.add_empty_option("- Select Process to ingest to-")
        if selected_process:
            select.set_option("default", selected_process)

        process_wdg.add("<br/>")

        if not process_names or "process" in hidden_options:
            process_wdg.set_style("display: none")


        # Metadata
        #hidden_options.append("metadata")
        if "metadata" not in hidden_options:
            process_wdg.add("<hr/>")

            title_wdg = DivWdg()
            div.add(title_wdg)
            title_wdg.add("Metadata")
            title_wdg.add_style("margin-top: 20px")
            title_wdg.add_style("font-size: 16px")
            title_wdg.add_style("margin-bottom: 5px")

            desc_wdg = DivWdg("The following metadata will be added to the ingested files.")
            desc_wdg.add_style("margin-bottom: 10px")
            div.add(desc_wdg)

            from tactic.ui.panel import EditWdg

            ingest_data_view = self.kwargs.get('metadata_view')
            if not ingest_data_view:
                ingest_data_view = self.kwargs.get('ingest_data_view')

            if self.search_key:
                sobject = SearchType.create("sthpw/snapshot")
            else:
                sobject = SearchType.create(self.search_type)

            metadata_element_names = self.kwargs.get("metadata_element_names")

            if self.show_settings:
                edit = EditWdg(
                        search_key=sobject.get_search_key(),
                        mode='view',
                        view=ingest_data_view,
                        element_names=metadata_element_names,
                        show_header=False,
                        width="100%",
                        display_mode="single_cell",
                        extra_data=self.kwargs.get("extra_data"),
                        default=self.kwargs.get("default"),
                )

                div.add(edit)


            div.add("<br/>")


        # options


        # update mode
        map_div = DivWdg()
        div.add(map_div)
        map_div.add("<hr/>")

        title_wdg = DivWdg()

        map_div.add(title_wdg)
        title_wdg.add("Mapping Files to Items")
        title_wdg.add_style("margin-top: 20px")
        title_wdg.add_style("font-size: 16px")

        if "map_option" in hidden_options:
            map_div.add_style("display: none")


        if "update_option" not in hidden_options:
            label_div = DivWdg()
            label_div.add("Determine how the file maps to a particular item")
            map_div.add(label_div)
            label_div.add_style("margin-top: 10px")
            label_div.add_style("margin-bottom: 8px")

            update_mode_option = self.kwargs.get("update_mode")
            if not update_mode_option:
                update_mode_option = "false"
            update_mode = SelectWdg(name="update mode")
            update_mode.add_class("spt_update_mode_select")
            update_mode.set_option("values", ["false", "true", "sequence"])
            update_mode.set_option("labels", ["Always insert a new item", "Update duplicate items", "Update groups as sequences"])
            update_mode.set_option("default", update_mode_option)
            update_mode.add_style("margin-top: -3px")
            update_mode.add_style("margin-right: 5px")
            map_div.add(update_mode)

            update_mode.add_behavior( {
                "type": "listen",
                "event_name": "set_ingest_update_mode",
                "cbjs_action": '''
                var value = bvr.firing_data.value;
                bvr.src_el.value = value;
                '''
            } )



        if not self.search_key and "ext_option" not in hidden_options:
            label_div = DivWdg()
            label_div.add("Ignore File Extension")
            map_div.add(label_div)
            label_div.add_style("margin-top: 10px")
            label_div.add_style("margin-bottom: 8px")

            ignore_ext_option = self.kwargs.get("ignore_ext")
            if not ignore_ext_option:
                ignore_ext_option = "false"
            ignore_ext = SelectWdg(name="update mode")
            ignore_ext.add_class("spt_ignore_ext_select")
            ignore_ext.set_option("values", ["true", "false"])
            ignore_ext.set_option("labels", ["Yes", "No"])
            ignore_ext.set_option("default", ignore_ext_option)
            ignore_ext.add_style("margin-top: -3px")
            ignore_ext.add_style("margin-right: 5px")
            map_div.add(ignore_ext)


        if not self.search_key and "column_option" not in hidden_options:
            label_div = DivWdg()
            label_div.add("Map file name to column")
            map_div.add(label_div)
            label_div.add_style("margin-top: 10px")
            label_div.add_style("margin-bottom: 8px")

            column_option = self.kwargs.get("column")
            if not column_option:
                column_option = "name"
            column_select = SelectWdg(name="update mode")
            column_select.add_class("spt_column_select")
            column_select.set_option("values", ["name", "code"])
            column_select.set_option("labels", ["Name", "Code"])
            column_select.set_option("default", column_option)
            column_select.add_style("margin-top: -3px")
            column_select.add_style("margin-right: 5px")
            map_div.add(column_select)



        if "zip_mode" not in hidden_options:
            label_div = DivWdg()
            label_div.add("When checking in zipped files:")
            map_div.add(label_div)
            label_div.add_style("margin-top: 10px")
            label_div.add_style("margin-bottom: 8px")

            column_option = self.kwargs.get("column")
            if not column_option:
                column_option = "name"
            column_select = SelectWdg(name="zip mode")
            column_select.add_class("spt_zip_mode_select")
            column_select.set_option("values", ["single", "unzip"])
            column_select.set_option("labels", ["Check-in as a single zipped file", "Unzip and check-in each file"])
            column_select.set_option("default", "single")
            column_select.add_style("margin-top: -3px")
            column_select.add_style("margin-right: 5px")
            map_div.add(column_select)




        if not self.search_key and "context_mode" not in hidden_options:
            map_div.add("<br/>")
            map_div.add("<hr/>")

            title_wdg = DivWdg()
            map_div.add(title_wdg)
            title_wdg.add("Context Mode")
            title_wdg.add_style("font-size: 16px")

            map_div.add("<br/>")

            context_mode_option = self.kwargs.get("context_mode")
            if not context_mode_option:
                context_mode_option = "case_sensitive"
            context_mode = SelectWdg(name="context_mode")
            context_mode.add_class("spt_context_mode_select")
            context_mode.set_option("values", "case_insensitive|case_sensitive")
            context_mode.set_option("labels", "Case Insensitive|Case Sensitive")
            context_mode.set_option("default", context_mode_option)
            context_mode.add_style("margin-top: -3px")
            context_mode.add_style("margin-right: 5px")
            map_div.add(context_mode)




        extra_data = self.kwargs.get("extra_data")
        if not isinstance(extra_data, basestring):
            extra_data = jsondumps(extra_data)

        if extra_data and extra_data != "null":
            # it needs a TextArea instead of Hidden because of JSON data
            text = TextAreaWdg(name="extra_data")
            text.add_style('display: none')
            text.set_value(extra_data)
            div.add(text)



        return div





    def get_content_wdg(self):

        """
        asset_dir = Environment.get_asset_dir()

        base_dir = self.kwargs.get("base_dir")
        if base_dir:
            if not base_dir.startswith(asset_dir):
                raise Exception("Path needs to be in asset root")
            else:
                relative_dir = base_dir.replace(asset_dir, "")
                relative_dir = relative_dir.strip("/")
        else:
            relative_dir = self.kwargs.get("relative_dir")

        self.relative_dir = relative_dir
        """

        div = DivWdg()
        div.add_style("width: auto")
        div.add_style("min-width: 600px")
        div.add_style("padding: 20px")
        div.add_color("background", "background")

        header_div = DivWdg()
        div.add(header_div)


        if self.show_settings:
            button_div = DivWdg()
            header_div.add(button_div)
            button = IconButtonWdg(title="Expand Options", icon="FA_ELLIPSIS_V")
            button_div.add(button)
            button_div.add_style("float: right")
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_ingest_top");
                var right = top.getElement(".spt_right_content");
                spt.toggle_show_hide(right);

                '''
            } )


        title = self.kwargs.get("title")
        if not title:
            if self.project_code:
                project_title = Project.get_by_code(self.project_code).get_value("title")
                title = "Copy files to '%s'" % project_title
                title_description = "These will be copied to the asset library"
            else:
                title = "Ingest Files"
                title_description = "Either drag files into the queue box or click 'Add Files to Queue'"
        else:
            title_description = "Either drag files into the queue box or click 'Add Files to Queue'"

        description = self.kwargs.get("description")
        if description in ["none", ""]:
            title_description = ""

        title_wdg = DivWdg()
        header_div.add(title_wdg)
        title_wdg.add("<span style='font-size: 25px'>%s</span>" % title)
        title_wdg.add("<br/>")
        title_wdg.add(title_description)
        title_wdg.add_style("display", "inline-block")

        # create the help button
        is_admin_site = Project.get().is_admin()
        show_help = self.kwargs.get("show_help") or True
        if self.kwargs.get("show_help") not in ['false', False] and is_admin_site:
            help_button_wdg = DivWdg()
            header_div.add(help_button_wdg)
            help_button_wdg.add_styles("float: right; margin-top: 11px;")
            help_button = ActionButtonWdg(title="?", tip="Ingestion Widget Help", size='s')
            help_button_wdg.add(help_button)

            help_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''spt.help.load_alias("ingestion_widget")'''
            } )

        div.add("<hr style='margin-right: 4px'/>")

        shelf_div = DivWdg()
        div.add(shelf_div)
        shelf_div.add_style("margin-bottom: 10px")

        if self.search_key:
            div.add("<input class='spt_input' type='hidden' name='search_key' value='%s'/>" % self.search_key)
        else:
            div.add("<input class='spt_input' type='hidden' name='search_key' value=''/>")


        if not self.search_type:
            div.add("No search type specfied")
            return div

        if self.relative_dir:
            folder_div = DivWdg()
            shelf_div.add(folder_div)
            folder_div.add("Folder: %s" % self.relative_dir)
            folder_div.add_style("opacity: 0.5")
            folder_div.add_style("font-style: italic")
            folder_div.add_style("margin-bottom: 10px")

        # update_process
        self.update_process = self.kwargs.get("update_process") or ""

        # ignore_path_keywords
        self.ignore_path_keywords = self.kwargs.get("ignore_path_keywords") or ""

        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        shelf_div.add(upload)



        button = ActionButtonWdg(title="Add Files to Queue", width=150, color="secondary")
        #button.add_style("float: right")
        button.add_style("display: inline-block")
        button.add_style("margin-top: -3px")
        shelf_div.add(button)

        button.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )

        button.add_behavior( {
            'type': 'click',
            'normal_ext': File.NORMAL_EXT,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');

            //clear upload progress
            var upload_bar = top.getElement('.spt_upload_progress');
            if (upload_bar) {
                upload_bar.setStyle('width','0%');
                upload_bar.innerHTML = '';
            }


            var upload_button = top.getElement(".spt_upload_files_top");

            var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                spt.ingest.select_files(top, files, bvr.normal_ext);
            }

            spt.html5upload.clear();
            spt.html5upload.set_form( top );
            spt.html5upload.select_file( onchange );

         '''
         } )




        button = ActionButtonWdg(title="Clear", color="secondary")
        #button.add_style("float: right")
        button.add_style("display: inline-block")
        button.add_style("margin-top: -3px")
        button.add_style("margin-left: 5px")
        shelf_div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingest_top");
            var file_els = top.getElements(".spt_upload_file");
            for ( var i = 0; i < file_els.length; i++) {
                spt.behavior.destroy( file_els[i] );
            };

            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "");

            var button = top.getElement(".spt_upload_files_top");
            button.setStyle("display", "none");


            //clear upload progress
            var upload_bar = top.getElement('.spt_upload_progress');
            if (upload_bar) {
                upload_bar.setStyle('width','0%');
                upload_bar.innerHTML = '';
                upload_bar.setStyle("visibility", "hidden");

                var info_el = top.getElement(".spt_upload_info");
                info_el.innerHTML = "";

            }

         '''
         } )

        ingest = self.get_ingest_button()
        shelf_div.add(ingest)
        ingest.add_style("float: right")

        shelf_div.add("<br clear='all'/>")


        progress_wdg = self.get_progress_div()
        shelf_div.add(progress_wdg)

        border_color_light = div.get_color("background2", 8)
        border_color_dark = div.get_color("background2", -15)
        background_mouseout = div.get_color("background", 10)
        background_mouseenter = div.get_color("background", 8)


        files_div = DivWdg()
        files_div.add_style("position: relative")
        files_div.add_class("spt_to_ingest_files")
        div.add(files_div)
        files_div.add_style("max-height: 400px")
        files_div.add_style("height: 400px")
        files_div.add_style("overflow-y: auto")
        files_div.add_style("padding: 3px")
        files_div.add_color("background", background_mouseout)
        files_div.add_style("border: 3px dashed %s" % border_color_light)
        #files_div.add_style("border-radius: 20px 20px 20px 20px")
        files_div.add_style("z-index: 1")
        files_div.add_style("margin: 5px 0px")
        #files_div.add_style("width", "586px")
        #files_div.add_style("display: none")

        bgcolor = div.get_color("background")
        bgcolor2 = div.get_color("background", -3)

        #style_text = "text-align: center; margin-top: 100px; color: #A0A0A0; font-size: 3.0em; z-index: 10;"

        background = DivWdg()
        background.add_class("spt_files_background")
        files_div.add(background)
        if self.sobjects:
            background.add_style("display: none")

        background.add_style("text-align: center")
        background.add_style("margin-top: 75px")
        background.add_style("font-size: 3.0em")
        background.add_style("z-index: 10")
        background.add_color("color", "color", 70)


        icon = "<i class='fa fa-cloud-upload-alt' style='font-size: 150px'> </i>"
        background.add(icon)

        background_text = DivWdg("<p>Drag Files Here</p>")

        background.add(background_text)

        files_div.add_behavior( {
            'type': 'mouseover',
            'cbjs_action': '''
            bvr.src_el.setStyle("border","3px dashed %s")
            bvr.src_el.setStyle("background","%s")
            ''' % (border_color_dark, background_mouseenter)
        } )

        files_div.add_behavior( {
            'type': 'mouseout',
            'cbjs_action': '''
            bvr.src_el.setStyle("border", "3px dashed %s")
            bvr.src_el.setStyle("background","%s")
            ''' % (border_color_light, background_mouseout)
        } )


        #background.add( self.get_select_files_button() )






        # Test drag and drop files
        files_div.add_attr("ondragenter", "return false")
        files_div.add_attr("ondragover", "return false")
        files_div.add_attr("ondrop", "spt.drag.noop(event, this)")
        files_div.add_behavior( {
        'type': 'load',
        'normal_ext': File.NORMAL_EXT,
        'cbjs_action': '''
        spt.drag = {}
        var background;

        spt.drag.show_file = function(file, top, delay, icon) {

            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "none");


            var template = top.getElement(".spt_upload_file_template");
            var clone = spt.behavior.clone(template);

            clone.removeClass("spt_upload_file_template");
            clone.addClass("spt_upload_file");
            clone.setStyle("display", "");

            if (typeof(delay) == 'undefined') {
                delay = 0;
            }

            // remember the file handle
            clone.file = file;

            var name = file.name;
            var size = parseInt(file.size / 1024 * 10) / 10;

            var thumb_el = clone.getElement(".spt_thumb");
            var date_label_el = clone.getElement(".spt_date_label");
            var date_el = clone.getElement(".spt_date");

            //var loadingImage = loadImage(
            setTimeout( function() {
                var draw_empty_icon = function() {
                        var img = document.id(document.createElement("div"));
                        img.setStyle("width", "58");
                        img.setStyle("height", "34");
                        //img.innerHTML = "MP4";
                        img.setStyle("border", "1px dotted #222")
                        thumb_el.appendChild(img);
                    };
                if (icon) {
                        var loadingImage = loadImage(
                            file,
                            function (img) {
                            if (img.width)
                                thumb_el.appendChild(img);
                            else
                                draw_empty_icon();

                            },
                            {maxWidth: 80, maxHeight: 60, canvas: true, contain: true}
                        );

                }
                else {
                    draw_empty_icon();
                }


                loadImage.parseMetaData(
                    file,
                    function(data) {
                        if (data.exif) {
                            var date = data.exif.get('DateTimeOriginal');
                            if (date) {
                                date_label_el.innerHTML = date;
                                if (date_el) {
                                    date_el.value = date;
                                }
                            }
                        }

                    }
                );

            }, delay );

            /*
            var reader = new FileReader();
            reader.thumb_el = thumb_el;
            reader.onload = function(e) {
                this.thumb_el.innerHTML = [
                    '<img class="thumb" src="',
                    e.target.result,
                    '" title="', escape(name),
                    '" width="60px"',
                    '" padding="5px"',
                    '"/>'
                ].join('');
            }
            reader.readAsDataURL(file);
            */

            clone.getElement(".spt_name").innerHTML = file.name;
            clone.getElement(".spt_size").innerHTML = size + " KB";
            clone.inject(top);
        }

        spt.drag.noop = function(evt, el) {
            var top = document.id(el).getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            evt.stopPropagation();
            evt.preventDefault();
            evt.dataTransfer.dropEffect = 'copy';
            var files = evt.dataTransfer.files;

            var delay = 0;
            var skip = false;
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');
            for (var i = 0; i < files.length; i++) {
                var size = files[i].size;
                var file_name = files[i].name;
                var is_normal = regex.test(file_name);
                if (size >= 10*1024*1024 || is_normal) {
                    spt.drag.show_file(files[i], files_el, 0, false);
                }
                else {
                    spt.drag.show_file(files[i], files_el, delay, true);

                    if (size < 100*1024)       delay += 50;
                    else if (size < 1024*1024) delay += 500;
                    else if (size < 10*1024*1024) delay += 1000;
                }

            }

            // get all of the current filenames
            var filenames = []
            var items = top.getElements(".spt_upload_file");
            for (var i = 0; i < items.length; i++) {
                var file = items[i].file;
                filenames.push(file.name);
            }


            // check if this is a sequence or zip
            var server = TacticServerStub.get();
            var cmd = 'tactic.ui.tools.IngestCheckCmd';
            var kwargs = {
                file_names: filenames
            };
            var ret_val = server.execute_cmd(cmd, kwargs);
            var info = ret_val.info;

            var ok = function() {
                var upload_button = top.getElement(".spt_upload_files_top");
                upload_button.setStyle("display", "");
            }

            ok();



        }
        '''
        } )

        # create a template that will be filled in for each file
        files_div.add_relay_behavior( {
            'type': 'mouseenter',
            'color': files_div.get_color("background3", -5),
            'bvr_match_class': 'spt_upload_file',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.color);
            '''
        } )
        files_div.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_upload_file',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )
        files_div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_remove',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingest_top");

            var el = bvr.src_el.getParent(".spt_upload_file");
            spt.behavior.destroy_element(el);

            var els = top.getElements(".spt_upload_file");

            if (els.length == 0) {
                var background = top.getElement(".spt_files_background");
                background.setStyle("display", "");


                var upload_button = top.getElement(".spt_upload_files_top");
                upload_button.setStyle("display", "none");
            }

            '''
        } )


        """
        metadata_view = "test/wizard/metadata"
        files_div.add_relay_behavior( {
            'type': 'mouseup',
            'view': metadata_view,
            'bvr_match_class': 'spt_upload_file',
            'cbjs_action': '''
            var class_name = 'tactic.ui.panel.CustomLayoutWdg';
            var kwargs = {
                view: bvr.view
            }
            spt.app_busy.show("Loading Metadata");
            spt.panel.load_popup("Metadata", class_name, kwargs);
            spt.app_busy.hide();
            '''
        } )
        """


        # add the passed in sobject files
        for sobject in self.sobjects:
            files_div.add( self.get_file_wdg(sobject) )


        # add the template
        files_div.add( self.get_file_wdg() )


        div.add("<br/>")


        #upload_wdg = self.get_ingest_button()
        #div.add(upload_wdg)

        return div



    def get_ingest_button(self):

        div = DivWdg()
       


        library_mode = self.kwargs.get("library_mode") or False
        dated_dirs = self.kwargs.get("dated_dirs") or False





        # NOTE: files variable is passed in automatically

        upload_init = '''
        var info_el = top.getElement(".spt_upload_info");
        info_el.innerHTML = "Uploading ...";


        // start the upload
        var progress_el = top.getElement(".spt_upload_progress");
        var progress_top = top.getElement(".spt_upload_progress_top");

        setTimeout( function() {
            progress_el.setStyle("visibility", "visible");
            progress_top.setStyle("margin-top", "0px");
        }, 0);


        server.start( {description: "Upload and check-in of ["+files.length+"] files"} );
        '''

        upload_progress = '''
        var top = bvr.src_el.getParent(".spt_ingest_top");
        progress_el = top.getElement(".spt_upload_progress");
        var percent = Math.round(evt.loaded * 100 / evt.total);
        progress_el.setStyle("width", percent + "%");
        progress_el.innerHTML = String(percent) + "%";
        progress_el.setStyle("background", "#f0ad4e");

        // to prevent another upload via multiple clicks.
        // we will detect this in button click behaviour.
        bvr.src_el.in_progress = true;
        '''



        oncomplete_script = '''
        spt.notify.show_message("Ingest Completed");
        server.finish();

        spt.message.stop_interval(message_key);

        if (typeof(top) != "undefined") {

            var file_els = top.getElements(".spt_upload_file");
            for ( var i = 0; i < file_els.length; i++) {
                spt.behavior.destroy( file_els[i] );
            };
            var background = top.getElement(".spt_files_background");
            background.setStyle("display", "");


            var info_el = top.getElement(".spt_upload_info");
            info_el.innerHTML = '';

            var progress_el = top.getElement(".spt_upload_progress");
            var progress_top = top.getElement(".spt_upload_progress_top");

            setTimeout( function() {
                progress_el.setStyle("visibility", "hidden");
                progress_top.setStyle("margin-top", "-30px");
            }, 0);

        
            ingest_btn_top = top.getElement(".spt_ingest_btn");
            ingest_btn_top.in_progress = false;
        }
            
         
        '''



        script_found = True
        oncomplete_script_path = self.kwargs.get("oncomplete_script_path")
        if oncomplete_script_path:
            script_folder, script_title = oncomplete_script_path.split("/")
            oncomplete_script_expr = "@GET(config/custom_script['folder','%s']['title','%s'].script)" %(script_folder,script_title)
            server = TacticServerStub.get()
            oncomplete_script_ret = server.eval(oncomplete_script_expr, single=True)

            if oncomplete_script_ret:
                oncomplete_script = oncomplete_script + oncomplete_script_ret
            else:
                script_found = False
                oncomplete_script = "alert('Error: oncomplete script not found');"


        if self.kwargs.get("oncomplete_script"):
            oncomplete_script += self.kwargs.get("oncomplete_script")
        if self.kwargs.get("on_complete"):
            oncomplete_script += self.kwargs.get("on_complete")



        on_complete = '''
        var top = bvr.src_el.getParent(".spt_ingest_top");
        var update_data_top = top.getElement(".spt_edit_top");

        var progress_el = top.getElement(".spt_upload_progress");
        progress_el.innerHTML = "100%";
        progress_el.setStyle("width", "100%");
        progress_el.setStyle("background", "#337ab7");


        var info_el = top.getElement(".spt_upload_info");

        var search_type = bvr.kwargs.search_type;
        var relative_dir = bvr.kwargs.relative_dir;
        var context = bvr.kwargs.context;
        var update_process = bvr.kwargs.update_process;
        var ignore_path_keywords = bvr.kwargs.ignore_path_keywords;

        var library_mode = bvr.kwargs.library_mode;
        var keyword_mode = bvr.kwargs.keyword_mode;
        var dated_dirs = bvr.kwargs.dated_dirs;
        var project_code = bvr.kwargs.project_code;
        if (!project_code) {
            project_code = null;
        }

        create_icon = bvr.kwargs.create_icon;

        // Data comes from Ingest Settings
        var context_mode_select = top.getElement(".spt_context_mode_select");
        var context_mode = context_mode_select ? context_mode_select.value : bvr.kwargs.context_mode;

        // settings
        var update_mode = null;
        var ignore_ext = null;
        var column = null;
        var zip_mode = null;

        var update_mode_select = top.getElement(".spt_update_mode_select");
        if (update_mode_select)
            update_mode = update_mode_select.value;

        var ignore_ext_select = top.getElement(".spt_ignore_ext_select");
        if (ignore_ext_select)
            ignore_ext = ignore_ext_select.value;

        var column_select = top.getElement(".spt_column_select");
        if (column_select)
            column = column_select ? column_select.value : bvr.kwargs.column;

        var zip_mode_select = top.getElement(".spt_zip_mode_select");
        if (zip_mode_select)
            zip_mode = zip_mode_select.value;




        var filenames = [];
        for (var i = 0; i != files.length;i++) {
            var name = files[i].name;
            if (name) {
                filenames.push(name);
            }
            else {
                filenames.push(files[i]);
            }
        }


        var values = spt.api.get_input_values(top);
        //var category = values.category[0];

        var keywords = values["edit|user_keywords"];

        if (keywords) {
            keywords = keywords[0];
        }
        else {
            keywords = "";
        }

        var extra_data = values.extra_data ? values.extra_data[0]: {};
        var parent_key = values.parent_key[0];
        var search_key = values.search_key[0];

        var convert_el = top.getElement(".spt_image_convert")
        if (convert_el) {
            convert = spt.api.get_input_values(convert_el);
        }
        else {
            convert = null;
        }

        var processes = values.process;
        if (processes) {
            process = processes[0];
            if (!process) {
                process = null;
            }
        }
        else {
            process = null;
        }

        var return_array = false;
        // non-existent when self.show_settings is False
        var update_data = update_data_top ? spt.api.get_input_values(update_data_top, null, return_array): {};


        var message_key = spt.message.generate_key();
        message_key = "IngestUploadCmd|" + search_key + "|" + message_key;



        var kwargs = {
            search_key: search_key,
            search_type: search_type,
            relative_dir: relative_dir,
            filenames: filenames,
            message_key: message_key,
            parent_key: parent_key,
            //category: category,
            keywords: keywords,
            update_process: update_process,
            ignore_path_keywords: ignore_path_keywords,
            extra_data: extra_data,
            update_data: update_data,
            process: process,
            context: context,
            convert: convert,
            update_mode: update_mode,
            ignore_ext: ignore_ext,
            column: column,
            library_mode: library_mode,
            keyword_mode: keyword_mode,
            dated_dirs: dated_dirs,
            context_mode: context_mode,
            zip_mode: zip_mode,
            project_code: project_code,
            create_icon: create_icon,
        }

        on_complete = function(rtn_data) {

        ''' + oncomplete_script + '''

        };

        on_error = function(error) {
            spt.alert(error);
            progress_el.setStyle("background", "#F00");
            spt.message.stop_interval(message_key);

            // set in_progress variable back to false.
            // so we can upload again.
            bvr.src_el.in_progress = false;
        }


        var class_name = bvr.action_handler;
        // TODO: make the async_callback return throw an e so we can run
        // server.abort
        server.execute_cmd(class_name, kwargs, {}, {on_complete:on_complete, on_error: on_error});

        on_progress = function(message) {

            msg = JSON.parse(message.message);
            var percent = msg.progress;
            var description = msg.description;
            var error = msg.error;
            info_el.innerHTML = description;
            progress_el.setStyle("width", percent+"%");
            progress_el.innerHTML = percent + "%";

            if (error) {
                progress_el.setStyle("background", "#F00");
                spt.message.stop_interval(message_key);
            }

        }
        spt.message.set_interval(message_key, on_progress, 2000, bvr.src_el);

        '''



        upload_div = DivWdg()


        search_keys = self.kwargs.get("search_keys")
        if not search_keys:
            upload_div.add_style("display: none")


        upload_div.add_class("spt_upload_files_top")
        div.add(upload_div)
        if self.sobjects:
            button = ActionButtonWdg(title="Copy Files", width=200, color="primary")
        else:
            button = ActionButtonWdg(title="Upload Files", width=200, color="primary")
        upload_div.add(button)
        #button.add_style("float: right")
        #upload_div.add_style("margin-bottom: 20px")


        button.add_class("spt_ingest_btn")
        upload_div.add("<br clear='all'/>")


        action_handler = self.kwargs.get("action_handler")
        if not action_handler:
            action_handler = 'tactic.ui.tools.IngestUploadCmd'

        context = self.kwargs.get("context")
        context_mode = self.kwargs.get("context_mode")
        keyword_mode = self.kwargs.get("keyword_mode")

        create_icon = self.kwargs.get("create_icon")
        if create_icon in ['false', False]:
            create_icon = False
        else:
            create_icon = True


        button.add_behavior( {
            'type': 'click_up',
            'action_handler': action_handler,
            'kwargs': {
                'search_type': self.search_type,
                'relative_dir': self.relative_dir,
                'script_found': script_found,
                'context': context,
                'library_mode': library_mode,
                'dated_dirs' : dated_dirs,
                'context_mode': context_mode,
                'update_process': self.update_process,
                'ignore_path_keywords': self.ignore_path_keywords,
                'project_code': self.project_code,
                'keyword_mode': keyword_mode,
                'create_icon': create_icon
            },
            'cbjs_action': '''

            if (bvr.kwargs.script_found != true)
            {
                spt.alert("Error: provided on_complete script not found");
                return;
            }

            var top = bvr.src_el.getParent(".spt_ingest_top");

            // upload in progress, prevent another upload through
            // multiple clicks.
            if (bvr.src_el.in_progress == true) {
                return;
            }

            var file_els = top.getElements(".spt_upload_file");
            var num_files = file_els.length;
            var files_top = top.getElement(".spt_to_ingest_files");

            spt.notify.show_message("Ingesting "+num_files+" Files");

            // get the server that will be used in the callbacks
            var server = TacticServerStub.get();

            // retrieved the stored file handles
            var files = [];
            for (var i = 0; i < file_els.length; i++) {
                if (file_els[i].file) {
                    files.push( file_els[i].file );
                }
                else {
                    var search_key = file_els[i].getAttribute("spt_search_key");
                    files.push("search_key:"+search_key);
                }

            }
            if (files.length == 0) {
                spt.alert("Either click 'Add' or drag some files over to ingest.");
                return;
            }


            // defined the callbacks
            var upload_start = function(evt) {
            }

            var upload_progress = function(evt) {
            %s;
            }

            var upload_complete = function(evt) {
            %s;
            }


            var upload_file_kwargs =  {
                files: files,
                upload_start: upload_start,
                upload_complete: upload_complete,
                upload_progress: upload_progress
            };
            if (bvr.ticket)
               upload_file_kwargs['ticket'] = bvr.ticket;

            %s;

            spt.html5upload.set_form( top );
            spt.html5upload.upload_file(upload_file_kwargs);

            ''' % (upload_progress, on_complete, upload_init)
        } )


        return div



    def get_progress_div(self):

        div = DivWdg()
        div.add_style("overflow-y: hidden")

        inner = DivWdg()
        div.add(inner)
        inner.add_class("spt_upload_progress_top")
        inner.add_style("margin-top: -30px")

        info = DivWdg()
        inner.add(info)
        info.add_class("spt_upload_info")


        progress_div = DivWdg()
        progress_div.add_class("spt_upload_progress_top")
        inner.add(progress_div)
        progress_div.add_style("width: 595px")
        progress_div.add_style("height: 15px")
        progress_div.add_style("margin-bottom: 10px")
        progress_div.add_border()
        #progress_div.add_style("display: none")

        progress = DivWdg()
        progress_div.add(progress)
        progress.add_class("spt_upload_progress")
        progress.add_style("width: 0px")
        progress.add_style("visibility: hidden")
        progress.add_style("height: 100%")
        progress.add_gradient("background", "background3", -10)
        progress.add_style("text-align: right")
        progress.add_style("overflow: hidden")
        progress.add_style("padding-right: 3px")

        from tactic.ui.app import MessageWdg
        progress.add_behavior( {
            'type': 'load',
            'cbjs_action': MessageWdg.get_onload_js()
        } )

        return div





    def get_select_files_button(self):


        button = ActionButtonWdg(title="Add Files to Queue", width=150, color="warning")

        from tactic.ui.input import Html5UploadWdg
        upload = Html5UploadWdg(multiple=True)
        button.add(upload)


        button.add_style("margin: 30px auto")

        button.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )


        button.add_behavior( {
            'type': 'click_up',
            'normal_ext': File.NORMAL_EXT,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files = spt.html5upload.get_files();

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');

            // clear upload progress
            var upload_bar = top.getElement('.spt_upload_progress');
            if (upload_bar) {
                upload_bar.setStyle('width','0%');
                upload_bar.innerHTML = '';
            }

            var upload_button = top.getElement(".spt_upload_files_top");

            var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                spt.ingest.select_files(top, files, bvr.normal_ext);
            }

            spt.html5upload.clear();
            spt.html5upload.set_form( top );
            spt.html5upload.select_file( onchange );

            '''
        } )

        button.add_behavior( {
            'type': 'click_upX',
            'normal_ext': File.NORMAL_EXT,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingest_top");
            var files_el = top.getElement(".spt_to_ingest_files");
            var regex = new RegExp('(' + bvr.normal_ext.join('|') + ')$', 'i');

            // clear upload progress
            var upload_bar = top.getElement('.spt_upload_progress');
            if (upload_bar) {
                upload_bar.setStyle('width','0%');
                upload_bar.innerHTML = '';
            }

            var upload_button = top.getElement(".spt_upload_files_top");

            var onchange = function (evt) {
                var files = spt.html5upload.get_files();
                var delay = 0;
                for (var i = 0; i < files.length; i++) {
                    var size = files[i].size;
                    var file_name = files[i].name;
                    var is_normal = regex.test(file_name);
                    if (size >= 10*1024*1024 || is_normal) {
                        spt.drag.show_file(files[i], files_el, 0, false);
                    }
                    else {
                        spt.drag.show_file(files[i], files_el, delay, true);

                        if (size < 100*1024)       delay += 50;
                        else if (size < 1024*1024) delay += 500;
                        else if (size < 10*1024*1024) delay += 1000;
                    }
                }

                upload_button.setStyle("display", "");
            }

            spt.html5upload.clear();
            spt.html5upload.set_form( top );
            spt.html5upload.select_file( onchange );

         '''
        } )

        return button



    def get_onload_js(self):

        return r'''

spt.ingest = {};

spt.ingest.select_files = function(top, files, normal_ext) {

    var files_el = top.getElement(".spt_to_ingest_files");

    var regex = new RegExp('(' + normal_ext.join('|') + ')$', 'i');

    var delay = 0;
    var skip = false;
    for (var i = 0; i < files.length; i++) {
        var size = files[i].size;
        var file_name = files[i].name;
        var is_normal = regex.test(file_name);
        if (size >= 10*1024*1024 || is_normal) {
            spt.drag.show_file(files[i], files_el, 0, false);
        }
        else {
            spt.drag.show_file(files[i], files_el, delay, true);

            if (size < 100*1024)       delay += 50;
            else if (size < 1024*1024) delay += 500;
            else if (size < 10*1024*1024) delay += 1000;
        }

    }

    // get all of the current filenames
    var filenames = []
    var items = top.getElements(".spt_upload_file");
    for (var i = 0; i < items.length; i++) {
        var file = items[i].file;
        filenames.push(file.name);
    }


    // check if this is a sequence or zip
    var server = TacticServerStub.get();
    var cmd = 'tactic.ui.tools.IngestCheckCmd';
    var kwargs = {
        file_names: filenames
    };
    var ret_val = server.execute_cmd(cmd, kwargs);
    var info = ret_val.info;

    var ok = function() {
        var upload_button = top.getElement(".spt_upload_files_top");
        upload_button.setStyle("display", "");
    }

    ok();
}

    '''




class IngestCheckCmd(Command):

    def execute(self):

        from pyasm.biz import FileRange

        file_names = self.kwargs.get("file_names")


        info = FileRange.get_sequences(file_names)

        #info = FileRange.check(file_names)
        self.info = info






class IngestUploadCmd(Command):

    # FOLDER_LIMIT can be adjusted as desired.
    FOLDER_LIMIT = 500

    def get_server(self):

        if not self.server:
            project_code = self.kwargs.get("project_code")
            if not project_code:
                self.server = TacticServerStub.get()

            else:
                self.server = TacticServerStub(protocol="local")
                self.server.set_project(project_code)

        return self.server

    def execute(self):

        import time
        start = time.time()

        self.server = None

        self.message_key = self.kwargs.get("message_key")
        try:
            ret_val = self._execute()
        except Exception as e:
            if self.message_key:
                msg = {
                    'progress': 100,
                    'error': '%s' % e,
                    'description': 'Error: %s' % e
                }

                server = self.get_server()
                server.log_message(self.message_key, msg, status="in progress")

                raise


        end = time.time()
        return ret_val


    def _execute(self):

        library_mode = self.kwargs.get("library_mode")
        current_folder = 0

        dated_dirs = self.kwargs.get("dated_dirs")

        filenames = self.kwargs.get("filenames")
        relative_dir = self.kwargs.get("relative_dir")

        base_dir = self.kwargs.get("base_dir")
        if not base_dir:
            upload_dir = Environment.get_upload_dir()
            base_dir = upload_dir

        context_mode = self.kwargs.get("context_mode")
        if not context_mode:
            context_mode = "case_sensitive"
        update_mode = self.kwargs.get("update_mode")
        ignore_ext = self.kwargs.get("ignore_ext")
        column = self.kwargs.get("column")
        if not column:
            column = "name"


        search_key = self.kwargs.get("search_key")
        if search_key:
            self.sobject = Search.get_by_search_key(search_key)
            search_type = self.sobject.get_base_search_type()
        else:
            search_type = self.kwargs.get("search_type")
            self.sobject = None


        if not relative_dir:
            project_code = Project.get_project_code()
            search_type_obj = SearchType.get(search_type)
            table = search_type_obj.get_table()
            relative_dir = "%s/%s" % (project_code, table)

        server = self.get_server()

        parent_key = self.kwargs.get("parent_key")
        category = self.kwargs.get("category")
        keywords = self.kwargs.get("keywords")
        update_process = self.kwargs.get("update_process")
        ignore_path_keywords = self.kwargs.get("ignore_path_keywords")
        if ignore_path_keywords:
            ignore_path_keywords = ignore_path_keywords.split(",")
            ignore_path_keywords = [x.strip() for x in ignore_path_keywords]

        update_data = self.kwargs.get("update_data")
        extra_data = self.kwargs.get("extra_data")
        if extra_data:
            extra_data = jsonloads(extra_data)
        else:
            extra_data = {}

        update_sobject_found = False
        # TODO: use this to generate a category
        category_script_path = self.kwargs.get("category_script_path")
        """
        ie:
            from pyasm.checkin import ExifMetadataParser
            parser = ExifMetadataParser(path=file_path)
            tags = parser.get_metadata()

            date = tags.get("EXIF DateTimeOriginal")
            return date.split(" ")[0]
        """


        # remap the filenames for sequences
        if update_mode == "sequence":
            sequences = FileRange.get_sequences(filenames)
            filenames = []
            for sequence in sequences:

                if sequence.get('is_sequence'):
                    filename = sequence.get("template")
                else:
                    filename = sequence.get("filenames")[0]
                filenames.append(filename)



        input_prefix = update_data.get('input_prefix')
        non_seq_filenames = []


        if library_mode:
            relative_dir = "%s/001" % relative_dir


        snapshots = []

        for count, filename in enumerate(filenames):
        # Check if files should be updated.
        # If so, attempt to find one to update.
        # If more than one is found, do not update.



            if filename.endswith("/"):
                # this is a folder:
                    continue

            new_keywords = keywords

            if filename.startswith("search_key:"):
                mode = "search_key"
                tmp, search_key = filename.split("search_key:")
                snapshot = Search.get_by_search_key(search_key)

                source_keywords = snapshot.get_value("keywords", no_exception=True)
                if source_keywords:
                    new_keywords = "%s %s" % (new_keywords, source_keywords)

                if snapshot.get_base_search_type() == "sthpw/snapshot":
                    lib_path = snapshot.get_lib_path_by_type()
                    filename = os.path.basename(lib_path)
                    new_filename = re.sub(r"_v\d+", "", filename)
                else:
                    snapshot = Snapshot.get_latest_by_sobject(snapshot, process="publish")
                    lib_path = snapshot.get_lib_path_by_type()
                    filename = os.path.basename(lib_path)
                    new_filename = re.sub(r"_v\d+", "", filename)

                if not snapshot:
                    raise Exception("Must pass in snapshot search_key")



            else:
                mode = "multi"
                new_filename = filename

            if library_mode:

                # get count of number of files in the current asset ingest dir
                import glob
                abs_path = Environment.get_asset_dir() + "/" + relative_dir + "/*"

                if len(glob.glob(abs_path)) > self.FOLDER_LIMIT:
                    current_folder = current_folder + 1
                    relative_dir = "%s/%03d" % (relative_dir[:-4], current_folder)


            unzip = self.kwargs.get("unzip")
            zip_mode = self.kwargs.get("zip_mode")
            if zip_mode in ['unzip'] or unzip in ["true", True] and filename.endswith(".zip"):
                from pyasm.common import ZipUtil
                unzip_dir = Environment.get_upload_dir()

                if not os.path.exists(unzip_dir):
                    os.makedirs(unzip_dir)

                zip_path = "%s/%s" % (base_dir, filename)
                ZipUtil.extract(zip_path, base_dir=unzip_dir)

                paths = ZipUtil.get_file_paths(zip_path)

                new_kwargs = self.kwargs.copy()
                new_kwargs['filenames'] = paths
                new_kwargs['base_dir'] = unzip_dir
                new_kwargs['zip_mode'] = "single"
                ingest = IngestUploadCmd(**new_kwargs)
                ingest.execute()

                continue


            if self.sobject:
                sobject = self.sobject

            elif update_mode in ["true", True, "update"]:
                # first see if this sobjects still exists
                search = Search(search_type)
                # ingested files into search type applies filename without i.e. _v001 suffix
                search.add_filter(column, new_filename)

                if relative_dir and search.column_exists("relative_dir"):
                    if not dated_dirs:
                        search.add_filter("relative_dir", relative_dir)

                sobjects = search.get_sobjects()

                if len(sobjects) > 1:
                    sobject = None
                elif len(sobjects) == 1:
                    sobject = sobjects[0]
                    update_sobject_found = True
                else:
                    sobject = None

            elif update_mode == "sequence":
                # This check is not needed anymore as the sequence analyzer
                # can handle a mix of sequence and non sequences
                #if not FileGroup.is_sequence(filename):
                #    raise TacticException('Please modify sequence naming to have at least three digits [%s].' % filename)
                search = Search(search_type)
                search.add_filter(column, filename)

                if relative_dir and search.column_exists("relative_dir"):
                    if not dated_dirs:
                        search.add_filter("relative_dir", relative_dir)
                sobjects = search.get_sobjects()
                if sobjects:
                    sobject = sobjects[0]
                else:
                    sobject = None

            else:
                sobject = None


            # Create a new entry
            if not sobject:
                if update_mode not in ['true', True, "update"]:
                    sobjects = []

                #self.check_existing_file(search_type, new_filename, relative_dir, update_mode, sobjects)

                sobject = SearchType.create(search_type)

                if ignore_ext in ['true', True]:
                    name, ext = os.path.splitext(new_filename)
                else:
                    name = new_filename

                # if the name contains a path, the only take basename
                name = os.path.basename(name)

                sobject.set_value(column, name)
                if relative_dir and sobject.column_exists("relative_dir"):
                    sobject.set_value("relative_dir", relative_dir)

            if mode == "search_key":
                path = lib_path

            elif relative_dir:
                path = "%s/%s" % (relative_dir, filename)
            else:
                path = filename

            # Handle update data
            # for some unknown reason, this input prefix is ignored
            new_data = {}
            for name, value in update_data.items():
                if name == "input_prefix":
                    continue

                name = name.replace("%s|"%input_prefix, "")
                new_data[name] = value

            if new_data:
                from tactic.ui.panel import EditCmd

                cmd = EditCmd(
                        view="edit",
                        sobject=sobject,
                        data=new_data,
                        commit="false",
                )
                cmd.execute()


            # Don't want the keywords being extracted from lib_path, extract the relative dir path instead
            # Using new_filename because it is the filename without version numbers
            if relative_dir:
                path_for_keywords = "%s/%s" % (relative_dir, new_filename)
            else:
                path_for_keywords = new_filename

            cmd_keyword_mode = self.kwargs.get("keyword_mode")

            if cmd_keyword_mode == "simplified":
                file_keywords = []
            else:
                file_keywords = Common.extract_keywords_from_path(path_for_keywords)

            # Extract keywords from the path to be added to keywords_data,
            # if ignore_path_keywords is found, remove the specified keywords
            # from the path keywords

            if ignore_path_keywords:
                for ignore_path_keyword in ignore_path_keywords:
                    if ignore_path_keyword in file_keywords:
                        file_keywords.remove(ignore_path_keyword)

            file_keywords.append(filename.lower())
            file_keywords = " ".join(file_keywords)


            new_file_keywords = ""

            # handle setting keywords to parent
            if SearchType.column_exists(search_type, "keywords"):

                old_keywords = sobject.get_value("keywords")

                if new_keywords:
                    new_file_keywords = "%s %s" % (new_keywords, file_keywords)
                else:
                    new_file_keywords = file_keywords

                if new_file_keywords:
                    new_file_keywords = "%s %s" % (old_keywords, new_file_keywords)

                # remove duplicated
                new_file_keywords = set( new_file_keywords.split(" ") )
                new_file_keywords = " ".join(new_file_keywords)

                if not cmd_keyword_mode == "none":
                    sobject.set_value("keywords", new_file_keywords)


            if SearchType.column_exists(search_type, "user_keywords"):
                if new_keywords:
                    if not cmd_keyword_mode == "none":
                        sobject.set_value("user_keywords", new_keywords)


            if SearchType.column_exists(search_type, "keywords_data"):
                data = sobject.get_json_value("keywords_data", {})
                data['user'] = new_keywords
                data['path'] = file_keywords
                sobject.set_json_value("keywords_data", data)



            # extract metadata
            #file_path = "%s/%s" % (base_dir, File.get_filesystem_name(filename))
            if update_mode == "sequence":
                sequence = sequences[count]
                file_path = "%s/%s" % (base_dir, sequence.get("filenames")[0])

            elif mode == "search_key":
                file_path = path
            else:
                file_path = "%s/%s" % (base_dir, filename)

            """
            # TEST: convert on upload
            try:
                convert = self.kwargs.get("convert")
                if convert:
                    message_key = "IngestConvert001"
                    cmd = ConvertCbk(**convert)
                    cmd.execute()
            except Exception as e:
                print("WARNING: ", e)
            """


            # check if the file exists
            if mode != "search_key" and not os.path.exists(file_path):
                raise Exception("Path [%s] does not exist" % file_path)

            # get the metadata from this image
            if SearchType.column_exists(search_type, "relative_dir"):
                if category and category not in ['none', None]:
                    from pyasm.checkin import ExifMetadataParser
                    parser = ExifMetadataParser(path=file_path)
                    tags = parser.get_metadata()

                    date = tags.get("EXIF DateTimeOriginal")
                    if not date:
                        date_str = "No-Date"
                    else:
                        date_str = str(date)
                        # this can't be parsed correctly by dateutils
                        parts = date_str.split(" ")
                        date_str = parts[0].replace(":", "-")
                        date_str = "%s %s" % (date_str, parts[1])

                        from dateutil import parser
                        orig_date = parser.parse(date_str)

                        if category == "by_day":
                            date_str = orig_date.strftime("%Y/%Y-%m-%d")
                        elif category == "by_month":
                            date_str = orig_date.strftime("%Y-%m")
                        elif category == "by_week":
                            date_str = orig_date.strftime("%Y/Week-%U")

                    full_relative_dir = "%s/%s" % (relative_dir, date_str)
                    sobject.set_value("relative_dir", full_relative_dir)

            # Add parent sObject
            if parent_key and parent_key != search_key:
                parent = Search.get_by_search_key(parent_key)
                if parent:
                    try:
                        sobject.set_sobject_value(parent)
                    except:
                        pass


            # Handle extra_data
            for key, value in extra_data.items():
                if SearchType.column_exists(search_type, key):
                    sobject.set_value(key, value)


            """
            if category:

                if SearchType.column_exists(search_type, "category"):
                    sobject.set_value("category", category)


                if SearchType.column_exists(search_type, "relative_dir"):
                    full_relative_dir = "%s/%s" % (relative_dir, category)
                    sobject.set_value("relative_dir", category)
            """


            # commit sobject
            sobject.commit()
            search_key = sobject.get_search_key()


            # add to a collection if specified
            collection_key = self.kwargs.get("collection_key")
            if collection_key:
                collection = Search.get_by_search_key(collection)
                sobject.add_to_collection(collection)



            status = sobject.get_value("status", no_exception=True)
            is_verified = status in ['Verified']


            create_icon = self.kwargs.get("create_icon")
            if create_icon in ['false', False]:
                create_icon = False
            else:
                create_icon = True


            # use API to check in file

            process = self.kwargs.get("process")
            if not process:
                process = "publish"


            context = self.kwargs.get("context")
            if not context:
                context = process

            if process == "icon":
                context = "icon"
            else:
                format_context = ProjectSetting.get_value_by_key("checkin/format_context", search_type=search_type)
                if format_context not in ['false', "False", False]:
                    context = "%s/%s" % (context, filename)

            if context_mode == "case_insensitive":
                context = context.lower()


            version = None
            if not is_verified and update_process and update_sobject_found:
                process = update_process

                # find what the version number should be
                search = Search("sthpw/snapshot")
                search.add_parent_filter(sobject)
                search.add_filter("context", context)
                search.add_order_by("version desc")
                max_snapshot = search.get_sobject()
                version = max_snapshot.get_value("version")
                if not version:
                    version = 1
                else:
                    version += 1


            if update_mode == "sequence":

                file_range = sequence.get("range")
                if file_range == "":
                    raise Exception("Error: %s" % sequence.get("error"))

                if sequence.get("is_sequence"):
                    file_path = "%s/%s" % (base_dir, sequence.get("template"))
                    snapshot = server.group_checkin(search_key, context, file_path, file_range, mode='move', version=version)
                else:
                    file_path = "%s/%s" % (base_dir, sequence.get("filenames")[0])
                    snapshot = server.simple_checkin(search_key, context, file_path, mode='uploaded', version=version, create_icon=create_icon)

            elif mode == "search_key":

                if lib_path.find("##") != -1:
                    file_range = snapshot.get_file_range().get_display
                    file_path = lib_path
                    snapshot = server.group_checkin(search_key, context, file_path, file_range, mode='copy')
                else:
                    # copy the file to a temporary location
                    tmp_dir = Environment.get_tmp_dir()
                    tmp_path = "%s/%s" % (tmp_dir, new_filename)
                    shutil.copy(file_path, tmp_path)
                    # auto create icon
                    snapshot = server.simple_checkin(search_key, context, tmp_path, process=process, mode='move', create_icon=create_icon)

            elif self.kwargs.get("base_dir"):
                # auto create icon
                snapshot = server.simple_checkin(search_key, context, file_path, process=process, mode='move', version=version, create_icon=create_icon)

            else:
                snapshot = server.simple_checkin(search_key, context, filename, process=process, mode='uploaded', version=version, create_icon=create_icon)


            snapshots.append(snapshot)

            #server.update(snapshot, {"user_keywords": "abc 123"} )

            percent = int((float(count)+1) / len(filenames)*100)


            if self.message_key:
                msg = {
                    'progress': percent,
                    'description': 'Checking in file [%s]' % filename,
                }

                server.log_message(self.message_key, msg, status="in progress")


            if self.info.get("snapshots"):
                self.info["snapshots"].append(snapshot)
            else:
                self.info["snapshots"] = [snapshot]



        if self.message_key:
            msg = {
                'progress': '100',
                'description': 'Check-ins complete'
            }
            server.log_message(self.message_key, msg, status="complete")


        return


    def check_existing_file(self, search_type, new_filename, relative_dir, update_mode, sobjects):
        project_code = Project.get_project_code()
        file_search_type = SearchType.build_search_type(search_type, project_code)

        search_name, search_ext = os.path.splitext(new_filename)
        search_name = "%s.%%" % search_name

        search_file = Search("sthpw/file")
        search_file.add_filter("search_type", file_search_type)
        search_file.add_filter("relative_dir", relative_dir)
        search_file.add_filter("file_name", search_name, op='like')

        print(search_file.get_statement())

        file_sobjects = search_file.get_sobjects()

        if file_sobjects and update_mode in ['true', True] and len(sobjects) > 1:
            raise TacticException('Multiple files with the same name as "%s" already exist. Uncertain as to which file to update. Please individually update each file.' % new_filename)
        elif file_sobjects:
            raise TacticException('A file with the same name as "%s" already exists in the file table with path "%s". Please rename the file and ingest again.' % (new_filename, relative_dir))

    def natural_sort(self,l):
        '''
        natural sort will makesure a list of names passed in is
        sorted in an order of 1000 to be after 999 instead of right after 101
        '''
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(l, key = alphanum_key)


    """
    def find_sequences(self, filenames):
        '''
        Parse a list of filenames into a dictionary of sequences.  Filenames not
        part of a sequence are returned in the None key

        :param      filenames | [<str>, ..]

        :return     {<str> sequence: [<str> filename, ..], ..}
        '''
        local_filenames   = filenames[:]
        sequence_patterns = {}
        sequences         = {None: []}

        # sort the files (by natural order) so we always generate a pattern
        # based on the first potential file in a sequence

        local_filenames = self.natural_sort(local_filenames)

        for filename in local_filenames:
            count = re.findall('\d+', filename)

            if not count:
                raise TacticException("Please ingest sequences only.")

            base, file_ext = os.path.splitext(filename)

            if file_ext:
                file_ext = file_ext[1:]

            # if last set of digits is not a file extension, and is less than 3 digits
            # because common.get_dir_info only works with 3 of more digits
            if len(count[-1]) <= 1 and file_ext.isalpha():
                raise TacticException('Please modify sequence naming to have at least three digits.')


            # if file extension found, and contains a number in the extension (but also not completely numbers)
            # grab the second last set of digits
            # ie. .mp3, .mp4, .23p

            if file_ext and not file_ext.isalpha() and not file_ext.isdigit():
                seq_digit_length = len(count[-2])
            else:
                seq_digit_length = len(count[-1])



            # if file_ext is empty, or if file_ext[1] is all numbers, use expression below
            # abc0001, abc.0001 ...etc
            if not file_ext or file_ext.isdigit():
                try:
                    pattern_expr = re.compile('^(.*)(\d{%d})([^\d]*)$'%seq_digit_length)
                except:
                    sequences[None].append(filename)
                    continue

            # then for regular filenames, try grabbing filenames by looking at the digits before the last dot
            # for files with extensions:
            # abc.0001.png, abc.0001.mp3, abc0001.mp3,
            else:
                try:
                    pattern_expr = re.compile('^(.*)(\d{%d})(\..*)$'%seq_digit_length)
                except:
                    sequences[None].append(filename)
                    continue


            pound_length = seq_digit_length
            pounds = "#" * pound_length

            # first, check to see if this filename matches a sequence
            found = False

            for key, pattern in sequence_patterns.items():
                match = pattern.match(filename)
                if not match:
                    continue

                sequences[key].append(filename)
                found = True
                break

            # if we've already been matched, then continue on
            if found:
                continue

            # next, see if this filename should start a new sequence
            basename = os.path.basename(filename)

            pattern_match = pattern_expr.match(basename)

            if pattern_match:
                opts = (pattern_match.group(1), pattern_match.group(3))
                key  = '%s%s%s' % (opts[0], pounds, opts[1])

                # create a new pattern based on the filename
                sequence_pattern = re.compile('^%s\d+%s$' % opts)

                sequence_patterns[key] = sequence_pattern
                sequences[key] = [filename]
                continue

            # otherwise, add it to the list of non-sequences
            sequences[None].append(filename)

        # now that we have grouped everything, we'll merge back filenames
        # that were potential sequences, but only contain a single file to the
        # non-sequential list
        for key, filenames in sequences.items():
            if ( key is None or len(filenames) > 1 ):
                continue

            sequences.pop(key)
            sequences[None] += filenames

        return sequences, seq_digit_length
    """
