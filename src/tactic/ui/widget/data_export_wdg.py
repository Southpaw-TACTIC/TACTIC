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


__all__ = ['CsvExportWdg', 'CsvImportWdg']

import csv, os
import string
import datetime

from pyasm.biz import CsvParser, File, Project
from pyasm.search import Search, SObjectFactory, SearchType, SearchKey, SObject
from pyasm.command import Command, FileUpload
from pyasm.web import HtmlElement, SpanWdg, DivWdg, Table, WebContainer, Widget, FloatDivWdg 
from pyasm.widget import CheckboxWdg, IconSubmitWdg, HiddenRowToggleWdg, HiddenWdg, WidgetConfigView, ProdIconButtonWdg, TextWdg, TextAreaWdg, IconWdg, ProgressWdg, HintWdg, SelectWdg
from pyasm.common import Common, Environment, TacticException

from tactic.ui.common import BaseRefreshWdg

from misc_input_wdg import SearchTypeSelectWdg
from upload_wdg import SimpleUploadWdg
from button_new_wdg import ActionButtonWdg
from swap_display_wdg import SwapDisplayWdg

class CsvExportWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {'search_type': 'Search Type', \
                'view': 'View of the search type', \
                'related_view': 'Related View of search type',
                'mode': 'export mode',\
                'selected_search_keys': 'Selected Search Keys',
                'search_class': 'Custom search class used',
                }


    def init(my):
        my.search_type = my.kwargs.get('search_type')
        # reconstruct the full search_type if it's base SType
        if my.search_type.find("?") == -1:
            project_code = Project.get_project_code()
            my.search_type = SearchType.build_search_type(my.search_type, project_code)
        
        my.view = my.kwargs.get('view')
        my.element_names = my.kwargs.get('element_names')
        my.related_view = my.kwargs.get('related_view')
        my.search_class = my.kwargs.get('search_class')
        my.search_view = my.kwargs.get('search_view')
        my.simple_search_view = my.kwargs.get('simple_search_view')
        my.mode = my.kwargs.get('mode')
        my.close_cbfn = my.kwargs.get('close_cbfn')
        my.input_search_keys = my.kwargs.get('selected_search_keys')
        my.selected_search_keys = []
        my.error_msg = ''
        my.search_type_list = []
        my.is_test = my.kwargs.get('test') == True
        my.table = None

    def check(my):
        if my.mode == 'export_matched':
            from tactic.ui.panel import TableLayoutWdg
            my.table = TableLayoutWdg(search_type=my.search_type, view=my.view,\
                show_search_limit='false', search_limit=-1, search_view=my.search_view,\
                search_class=my.search_class, simple_search_view=my.simple_search_view, init_load_num=-1)
            my.table.handle_search()
            search_objs = my.table.sobjects
            my.selected_search_keys = SearchKey.get_by_sobjects(search_objs, use_id=True)
            return True

        for sk in my.input_search_keys:
            st = SearchKey.extract_search_type(sk)
            if st not in my.search_type_list:
                my.search_type_list.append(st)

            id = SearchKey.extract_id(sk)
            if id == '-1':
                continue
            
            my.selected_search_keys.append(sk)
        
        if len(my.search_type_list) > 1:
            my.check_passed = False
            my.error_msg = 'More than 1 search type is selected. Please keep the selection to one type only.'
            return False

        if not my.search_type_list and my.mode == 'export_selected':
            my.check_passed = False
            my.error_msg = 'Search type cannot be identified. Please select a valid item.'
            return False
        return True

    def get_display(my): 

        top = my.top
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("padding: 10px")
        top.add_style("min-width: 400px")

        from tactic.ui.app import HelpButtonWdg
        help_wdg = HelpButtonWdg(alias="exporting-csv-data")
        top.add(help_wdg)
        help_wdg.add_style("float: right")
        help_wdg.add_style("margin-top: -3px")
        
        if not my.check(): 
            top.add(DivWdg('Error: %s' %my.error_msg))
            top.add(HtmlElement.br(2))
            return super(CsvExportWdg, my).get_display()

        if my.search_type_list and my.search_type_list[0] != my.search_type:
            st = SearchType.get(my.search_type_list[0])
            title_div =DivWdg('Exporting related items [%s]' % st.get_title())
            top.add(title_div)
            top.add(HtmlElement.br())
            my.search_type = my.search_type_list[0]
            my.view = my.related_view

        if my.mode != 'export_all':
            num = len(my.selected_search_keys)
        else:
            search = Search(my.search_type)
            num = search.get_count()
        msg_div = DivWdg('Total: %s items to export'% num)
        msg_div.add_style("font-size: 12px")
        msg_div.add_style("font-weight: bold")
        msg_div.add_style('margin-left: 4px')
        top.add(msg_div)
        if num > 300:
            msg_div.add_behavior({'type':'load',
            'cbjs_action': "spt.alert('%s items are about to be exported. It may take a while.')" %num})
                
        top.add(HtmlElement.br())

        div  = DivWdg(css='spt_csv_export', id='csv_export_action')
        div.add_color("background", "background", -10)
        div.add_style("padding: 10px")
        div.add_style("margin: 5px")
        
        div.add_styles('max-height: 350px; overflow: auto')
        table = Table( css='minimal')
        table.add_color("color", "color")
        div.add(table)
        table.set_id('csv_export_table')
        table.center()
        
        
        cb_name = 'csv_column_name'
        master_cb = CheckboxWdg('master_control')
        master_cb.set_checked()
        master_cb.add_behavior({'type': 'click_up',
            'propagate_evt': True,
            'cbjs_action': '''
                var inputs = spt.api.Utility.get_inputs(bvr.src_el.getParent('.spt_csv_export'),'%s');
                for (var i = 0; i < inputs.length; i++)
                    inputs[i].checked = !inputs[i].checked;
                    ''' %cb_name})


        span = SpanWdg('Select Columns To Export')
        span.add_style('font-weight','600')
        table.add_row_cell(span)
        table.add_row_cell(HtmlElement.br())

        tr = table.add_row()
        tr.add_style('border-bottom: 1px groove #777')
        td = table.add_cell(master_cb)
        label = HtmlElement.i('toggle all')
        label.add_style('color: #888')
        table.add_cell(label)


        col1 = table.add_col()
        col1.add_style('width: 35px')
        col2 = table.add_col()
        
        if not my.search_type or not my.view:
            return table

        # use overriding element names and derived titles if available
        config = WidgetConfigView.get_by_search_type(my.search_type, my.view)
        if my.element_names and config:
            filtered_columns = my.element_names
            titles = []
            for name in my.element_names:
                title = config.get_element_title(name)
                titles.append(title)

        else:
            
            # excluding FunctionalTableElement
            filtered_columns = []
            titles = []
            if not config:
                columns = search.get_columns()
                filtered_columns = columns
                titles = ['n/a'] * len(filtered_columns)
            else:
                columns = config.get_element_names()
                
                filtered_columns = columns
                titles = config.get_element_titles()

        
            """
            # commented out until it is decided 2.5 widgets will 
            # use this class to differentiate between reg and functional element
            from pyasm.widget import FunctionalTableElement
            for column in columns:
                widget = config.get_display_widget(column)

                if isinstance(widget, FunctionalTableElement):
                    continue
                filtered_columns.append(column)
            """

        for idx, column in enumerate(filtered_columns):
            table.add_row()
            cb = CheckboxWdg(cb_name)
            cb.set_option('value', column)
            cb.set_checked()
            table.add_cell(cb)
            
            
            title = titles[idx]
            table.add_cell('<b>%s</b> (%s) '%(title, column))

        action_div = DivWdg()
        widget = DivWdg()
        table.add_row_cell(widget)
        widget.add_style("margin: 20px 0 10px 0px")
        cb = CheckboxWdg('include_id', label=" Include ID")
        cb.set_default_checked()
        widget.add(cb)
        hint = HintWdg('To update entries with specific ID later, please check this option. For new inserts in this or other table later on, uncheck this option.') 
        widget.add(hint)

        label = string.capwords(my.mode.replace('_', ' '))
        button = ActionButtonWdg(title=label, size='l')
        is_export_all  = my.mode == 'export_all'
        button.add_behavior({
            'type': "click_up",
            'cbfn_action': 'spt.dg_table_action.csv_export',
            'element': 'csv_export',
            'column_names': 'csv_column_name',
            'search_type': my.search_type,
            'view': my.view,
            'search_keys' : my.selected_search_keys,
            'is_export_all' : is_export_all
            
        })

        my.close_action = "var popup = bvr.src_el.getParent('.spt_popup');spt.popup.close(popup)"
        if my.close_action:
            close_button = ActionButtonWdg(title='Close')
            close_button.add_behavior({
                'type': "click",
                'cbjs_action': my.close_action
            })


        table = Table()
        action_div.add(table)
        table.center()
        table.add_row()
        td = table.add_cell(button)
        td.add_style("width: 130px")
        table.add_cell(close_button)

        action_div.add("<br clear='all'/>")

        top.add(div)
        top.add(HtmlElement.br())
        top.add(action_div)

        if my.is_test:
            rtn_data = {'columns': my.element_names, 'count': len(my.selected_search_keys)}
            if my.mode == 'export_matched':
                rtn_data['sql'] =  my.table.search_wdg.search.get_statement()
            from pyasm.common import jsondumps
            rtn_data = jsondumps(rtn_data)
            return rtn_data

        return top


class CsvImportWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
                'search_type': 'Search Type to import'}


    def init(my):
        web = WebContainer.get_web()
        
        my.is_refresh = my.kwargs.get('is_refresh')
        if not my.is_refresh:
            my.is_refresh = web.get_form_value('is_refresh')

        my.search_type = my.kwargs.get('search_type')
        if not my.search_type:
            my.search_type = web.get_form_value('search_type_filter')
        my.close_cbfn = my.kwargs.get('close_cbfn')

        my.data = web.get_form_value("data")
        my.web_url = web.get_form_value("web_url")
        my.file_path = None
        if my.web_url:
            import urllib2
            response = urllib2.urlopen(my.web_url)
            csv = response.read()
            my.file_path = "/tmp/test.csv"
            f = open(my.file_path, 'w')
            f.write(csv)
            f.close()

        if not my.file_path:
            my.file_path =  web.get_form_value('file_path')

        if not my.file_path:
            ticket = web.get_form_value('html5_ticket')
            if not ticket:
                ticket =  web.get_form_value('csv_import|ticket')

            file_name =  web.get_form_value('file_name')
            if my.data:
                if not file_name:
                    file_name = "%s.csv" % ticket

                my.file_path = '%s/%s' %(web.get_upload_dir(ticket=ticket), file_name)
                f = open(my.file_path, "wb")
                f.write(my.data)
                f.close()
            elif file_name:
                my.file_path = '%s/%s' %(web.get_upload_dir(ticket=ticket), file_name)
                

        my.columns = my.kwargs.get("columns")
        if not my.columns:
            my.columns = web.get_form_value("columns")
        if my.columns and isinstance(my.columns, basestring):
            my.columns = my.columns.split("|")

        my.labels = my.kwargs.get("labels")
        if not my.labels:
            my.labels = web.get_form_value("labels")
        if my.labels and isinstance(my.labels, basestring):
            my.labels = my.labels.split("|")




    def get_display(my):
        
        widget = DivWdg()
        if not my.is_refresh:
            from tactic.ui.widget import TitleWdg
            title = TitleWdg(name_of_title='Import CSV', help_alias='importing-csv-data')
            widget.add(title)

        widget.add_style('padding: 10px')
        widget.add_style('font-size: 12px')
        #widget.add_border()
        widget.add_color('color','color') 
        widget.add_color('background','background') 
        widget.add_class("spt_import_top")
       

        inner = DivWdg()
        widget.add(inner)
        inner.add( my.get_first_row_wdg() )
        inner.add(ProgressWdg())

        if my.is_refresh:
            return inner
        else:
            return widget

    def get_upload_wdg(my):
        '''get search type select and upload wdg'''

        key = 'csv_import'


        widget = DivWdg(css='spt_import_csv')
        widget.add_color('color','color')
        widget.add_color('background','background')
        widget.add_style('width: 600px')

        # get the search type
        stype_div = DivWdg()
        widget.add(stype_div)


        # DEPRECATED
        # handle new search_types
        """
        new_search_type = CheckboxWdg("new_search_type_checkbox")
        new_search_type.add_event("onclick", "toggle_display('new_search_type_div')")
        new_search_type_div = DivWdg()
        new_search_type_div.set_id("new_search_type_div")

        name_input = TextWdg("asset_name")
        title = TextWdg("asset_title")
        description = TextAreaWdg("asset_description")

        table = Table()
        table.set_id('csv_main_body')
        table.add_style("margin: 10px 10px")
        table.add_col().set_attr('width','140')
        table.add_col().set_attr('width','400')
        
        table.add_row()
        table.add_header("Search Type: ").set_attr('align','left')
        table.add_cell(name_input)
        table.add_row()
        table.add_header("Title: ").set_attr('align','left')
        table.add_cell(title)
        table.add_row()
        table.add_header("Description: ").set_attr('align','left')
        table.add_cell(description)
        new_search_type_div.add(table)
        new_search_type_div.add_style("display: none")
        #widget.add(new_search_type_div)
        """


        show_stype_select = my.kwargs.get("show_stype_select")
        if show_stype_select in ['true',True] or not my.search_type:

            title = DivWdg("<b>Select sType to import data into:</b>&nbsp;&nbsp;")
            stype_div.add( title )
            title.add_style("float: left")

            search_type_select = SearchTypeSelectWdg("search_type_filter", mode=SearchTypeSelectWdg.ALL)
            search_type_select.add_empty_option("-- Select --")
            if not search_type_select.get_value():
                search_type_select.set_value(my.search_type)
            search_type_select.set_persist_on_submit()

            stype_div.add(search_type_select)



            search_type_select.add_behavior( {'type': 'change', \
                  'cbjs_action': "spt.panel.load('csv_import_main','%s', {}, {\
                  'search_type_filter': bvr.src_el.value});" %(Common.get_full_class_name(my)) } )

        else:
            hidden = HiddenWdg("search_type_filter")
            stype_div.add(hidden)
            hidden.set_value(my.search_type)


        if my.search_type:
            sobj = None
            try:
                sobj = SObjectFactory.create(my.search_type)
            except ImportError:
                widget.add(HtmlElement.br())
                widget.add(SpanWdg('WARNING: Import Error encountered. Please choose another search type.', css='warning')) 
                return widget

            required_columns = sobj.get_required_columns()
           
            if required_columns:
                widget.add(HtmlElement.br())
                req_span = SpanWdg("Required Columns: ", css='med')
                req_span.add_color('color','color')
                widget.add(req_span)
                #required_columns = ['n/a']
                req_span.add(', '.join(required_columns))

            widget.add( HtmlElement.br() )



            if my.file_path:
                hidden = HiddenWdg("file_path", my.file_path)
                widget.add(hidden)
                
                if my.web_url:
                    file_span = FloatDivWdg('URL: <i>%s</i>&nbsp;&nbsp;&nbsp;' %my.web_url, css='med')

                else:
                    if not my.data:
                        file_span = FloatDivWdg('File uploaded: <i>%s</i>&nbsp;&nbsp;&nbsp;' %os.path.basename(my.file_path), css='med')
                    else:
                        lines = len(my.data.split("\n"))
                        file_span = FloatDivWdg("Uploaded [%s] lines of entries: &nbsp; " % lines)
                file_span.add_color('color','color')
                file_span.add_style('margin: 8px 0 0 10px')
                file_span.add_style('font-size: 14px')
                widget.add(file_span)

                button = ActionButtonWdg(title='Change')
                button.add_style('float','left')
                button.add_behavior( {
                    'type': 'click_up', 
                    'columns': "|".join(my.columns),
                    'labels': "|".join(my.labels),
                    'cbjs_action': '''
                    spt.panel.load('csv_import_main','%s', {}, {
                        search_type_filter: '%s',
                        columns: bvr.columns,
                        labels: bvr.labels,
                        is_refresh: true
                    });''' %(Common.get_full_class_name(my), my.search_type)
                } )
                widget.add(button)
                widget.add("<br clear='all'/>")
                widget.add(HtmlElement.br())
                return widget

            widget.add_style("overflow-y: auto")

            msg = DivWdg()
            widget.add(msg)
            msg.add_border()
            msg.add_style("width: 500px")
            msg.add_color("background", "background3")
            msg.add_style("padding: 30px")
            msg.add_style("margin: 10 auto")
            #msg.add_style("text-align: center")

            msg.add( "<div style='float: left; padding-top: 6px; margin-right: 105px'><b>Upload a csv file: </b></div>")

            ticket = Environment.get_security().get_ticket_key()

            
            on_complete = '''var server = TacticServerStub.get();
            var file = spt.html5upload.get_file();
            if (file) {
                var file_name = file.name;
                // clean up the file name the way it is done in the server
                //file_name = spt.path.get_filesystem_name(file_name);    
                var server = TacticServerStub.get();

                var class_name = 'tactic.ui.widget.CsvImportWdg';
                var values = spt.api.Utility.get_input_values('csv_import_main');
                values['is_refresh'] = true;
                values['file_name'] = file_name;
                values['html5_ticket'] = '%s';
                try {
                    var info = spt.panel.load('csv_import_main', class_name, {}, values);
                    spt.app_busy.hide();
                }
                catch(e) {
                    spt.alert(spt.exception.handler(e));
                }
            }
            else  {
              alert('Error: file object cannot be found.')
            }
            spt.app_busy.hide();'''%ticket
            from tactic.ui.input import UploadButtonWdg
            browse = UploadButtonWdg(name='new_csv_upload', title="Browse", tip="Click to choose a csv file",\
                    on_complete=on_complete, ticket=ticket)
            browse.add_style('float: left')
            msg.add(browse)


            
            # this is now only used in the copy and paste Upload button for backward-compatibility
            upload_wdg = SimpleUploadWdg(key=key, show_upload=False)
            upload_wdg.add_style('display: none')
            msg.add(upload_wdg)


            msg.add("<br/>")
          
            """
            msg.add("<div style='margin: 30px; text-align: center'>-- OR --</div>")

            msg.add("<b>Published URL: </b><br/>") 
            from tactic.ui.input import TextInputWdg
            text = TextInputWdg(name="web_url")
            text.add_style("width: 100%")
            msg.add(text)
            """
 


            msg.add("<div style='margin: 30px; text-align: center'>-- OR --</div>")

            msg.add("<b>Copy and Paste from a Spreadsheet: </b><br/>") 
            text = TextAreaWdg("data")
            text.add_style('width: 100%')
            text.add_style('height: 100px')
            text.add_class("spt_import_cut_paste")
            msg.add(text)
            msg.add("<br/>"*3)


            button = ActionButtonWdg(title="Parse")
            button.add_style("margin: 5px auto")
            msg.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'columns': "|".join(my.columns),
                'labels': "|".join(my.labels),
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_import_top");
                var el = top.getElement(".spt_import_cut_paste");

                var value = el.value;
                var csv = [];
                // convert to a csv file!
                lines = value.split("\\n");
                for (var i = 0; i < lines.length; i++) {
                    if (lines[i] == '') {
                        continue;
                    }
                    var parts = lines[i].split("\\t");
                    var new_line = [];
                    for (var j = 0; j < parts.length; j++) {
                        if (parts[j] == '') {
                            new_line.push('');
                        }
                        else {
                            new_line.push('"'+parts[j]+'"');
                        }
                    }
                    new_line = new_line.join(",");
                    csv.push(new_line);
                }

                csv = csv.join("\\n")

                /*
                // FIXME: need to get a local temp directory
                var applet = spt.Applet.get();
                var path = spt.browser.os_is_Windows() ? "C:/sthpw/copy_n_paste.csv" : "/tmp/sthpw/copy_n_paste.csv";
                applet.create_file(path, csv);

                // upload the file
                applet.upload_file(path)
                applet.rmtree(path);

                var top = bvr.src_el.getParent(".spt_import_csv");
                var hidden = top.getElement(".spt_upload_hidden");
                hidden.value = path;

                var file_name = spt.path.get_basename(hidden.value);
                file_name = spt.path.get_filesystem_name(file_name); 
                */

                var class_name = 'tactic.ui.widget.CsvImportWdg';
                var values = spt.api.Utility.get_input_values('csv_import_main');
                values['is_refresh'] = true;
                //values['file_name'] = file_name;
                values['data'] = csv;

                var kwargs = {
                    columns: bvr.columns,
                    labels: bvr.labels
                };
                values['labels'] = bvr.labels;
                var info = spt.panel.load('csv_import_main', class_name, kwargs, values);
                '''
            } )

        
        return widget



    def get_first_row_wdg(my):

        # read the csv file
        #my.file_path = ""

        div = DivWdg(id='csv_import_main')
        div.add_class('spt_panel')
        
        div.add( my.get_upload_wdg() )
        if not my.search_type:
            return div

        if not my.file_path:
            return div


        if not my.file_path.endswith(".csv"):
            div.add('<br/>')
            div.add( "Uploaded file [%s] is not a csv file. Refreshing in 3 seconds. . ."% os.path.basename(my.file_path))
            div.add_behavior( {'type': 'load', \
                                  'cbjs_action': "setTimeout(function() {spt.panel.load('csv_import_main','%s', {}, {\
                                    'search_type_filter': '%s'});}, 3000);" %(Common.get_full_class_name(my), my.search_type) } )
            return div

        if not os.path.exists(my.file_path):
            raise TacticException("Path '%s' does not exist" % my.file_path)

        
        div.add(HtmlElement.br(2))



        # NOT NEEDED:  clear the widget settings before drawing
        #expr = "@SOBJECT(sthpw/wdg_settings['key','EQ','pyasm.widget.input_wdg.CheckboxWdg|column_enabled_']['login','$LOGIN']['project_code','$PROJECT'])"
        #sobjs = Search.eval(expr)
        #for sobj in sobjs:
        #    sobj.delete(log=False)


        div.add( HtmlElement.b("The following is taken from the first line in the uploaded csv file.  Select the appropriate column to match.") )
        div.add(HtmlElement.br())
        """
        text =  HtmlElement.b("Make sure you have all the required columns** in the csv.")
        text.add_style('text-align: left')
        div.add(text)
        """
        div.add(HtmlElement.br(2))
        option_div_top = DivWdg()
        option_div_top.add_color('color','color')
        option_div_top.add_color('background','background', -5)
        option_div_top.add_style("padding: 10px")
        option_div_top.add_border()
        option_div_top.add_style("width: auto")

        swap = SwapDisplayWdg(title="Parsing Options")
        option_div_top.add(swap)

        option_div_top.add_style("margin-right: 30px")

        my.search_type_obj = SearchType.get(my.search_type)

        option_div = DivWdg()
        swap.set_content_id(option_div.set_unique_id() )
        option_div.add_style("display: none")
        option_div.add_style('margin-left: 14px')
        option_div.add_style('margin-top: 10px')
        option_div.add_style("font-weight: bold")
        option_div_top.add(option_div)

        # first row and second row
        #option_div.add( HtmlElement.br() )
        option_div.add(SpanWdg("Use Title Row: ", css='med'))
        title_row_checkbox = CheckboxWdg("has_title")
        title_row_checkbox.set_default_checked()

        title_row_checkbox.add_behavior({'type' : 'click_up',
                    'propagate_evt': 'true',
                    'cbjs_action': "spt.panel.refresh('preview_data',\
                    spt.api.Utility.get_input_values('csv_import_main'))"})
        option_div.add(title_row_checkbox)
        option_div.add( HintWdg("Set this to use the first row as a title row to match up columns in the database") )
        

        option_div.add( HtmlElement.br(2) )
        option_div.add(SpanWdg("Use Lowercase Title: ", css='med'))
        lower_title_checkbox = CheckboxWdg("lowercase_title")

        lower_title_checkbox.add_behavior({'type' : 'click_up',
                    'propagate_evt': 'true',
                    'cbjs_action': "spt.panel.refresh('preview_data',\
                    spt.api.Utility.get_input_values('csv_import_main'))"})
        option_div.add(lower_title_checkbox)
        option_div.add( HtmlElement.br(2) )

        span = SpanWdg("Sample Data Row: ", css='med')
        option_div.add(span)
        option_div.add(HtmlElement.br())
        data_row_text = SelectWdg("data_row")
        data_row_text.add_style('float','left')
        data_row_text.add_style('width','80%')
        data_row_text.set_option('values', '1|2|3|4|5')
        data_row_text.set_value('1')
        data_row_text.add_behavior({'type' : 'change',
                    'cbjs_action': "spt.panel.refresh('preview_data',\
                    spt.api.Utility.get_input_values('csv_import_main'))"})
        option_div.add(data_row_text)
        hint = HintWdg("Set this as a sample data row for display here") 
        hint.add_styles('padding-top: 8px; display: block')
        option_div.add( hint )

        option_div.add( HtmlElement.br(2) )
      
        # encoder
        span = SpanWdg("Encoder: ", css='med')
        option_div.add(span)
        option_div.add(HtmlElement.br())
        select_wdg = SelectWdg('encoder')
        select_wdg.set_option('values', ['','utf-8', 'iso_8859-1']) 
        select_wdg.set_option('labels', ['ASCII (default)','UTF-8','Excel ISO 8859-1']) 
        select_wdg.add_style('width','80%')
        select_wdg.add_behavior({'type' : 'change',
                    'cbjs_action': "spt.panel.refresh('preview_data',\
                    spt.api.Utility.get_input_values('csv_import_main'))"})
        option_div.add(select_wdg)
        option_div.add( HtmlElement.br(2) )


        span = SpanWdg("Identifying Column: ", css='med')
        option_div.add(span)
        option_div.add(HtmlElement.br())
        select_wdg = SelectWdg('id_col')
        select_wdg.set_option('empty','true')
        select_wdg.add_style('float','left')
        select_wdg.add_style('width','80%')
        #columns = my.search_type_obj.get_columns()
        columns = SearchType.get_columns(my.search_type)
        
        # make sure it starts off with id, code where applicable
        if 'code' in columns:
            columns.remove('code')
            columns.insert(0, 'code')
        if 'id' in columns:
            columns.remove('id')
            columns.insert(0, 'id')

        select_wdg.set_option('values', columns) 
        option_div.add(select_wdg)
        hint = HintWdg("Set which column to use for identifying an item to update during CSV Import") 
        hint.add_styles('padding-top: 8px; display: block')
        option_div.add( hint )
        option_div.add( HtmlElement.br(2) )

        
        # triggers mode
        span = SpanWdg("Triggers: ", css='med')
        option_div.add(span)
        option_div.add(HtmlElement.br())
        select_wdg = SelectWdg('triggers_mode')
        select_wdg.set_option('values', ['','False', 'True', 'none']) 
        select_wdg.set_option('labels', ['- Select -','Internal Triggers Only','All Triggers','No Triggers']) 
        select_wdg.add_style('float','left')
        select_wdg.add_style('width','80%')
        select_wdg.add_behavior({'type' : 'change',
                    'cbjs_action': "spt.panel.refresh('preview_data',\
                    spt.api.Utility.get_input_values('csv_import_main'))"})
        option_div.add(select_wdg)
        option_div.add( HtmlElement.br(2) )

        div.add(option_div_top)

        my.has_title = title_row_checkbox.is_checked()
        
        
        # need to somehow specify defaults for columns
        div.add(my.get_preview_wdg())


        return div          


    
    def get_preview_wdg(my):
        columns = my.columns
        labels = my.labels
        preview = PreviewDataWdg(file_path=my.file_path, search_type=my.search_type, columns=columns, labels=labels)
        return preview

class PreviewDataWdg(BaseRefreshWdg):

    
    def init(my):

        my.is_refresh = my.kwargs.get('is_refresh') 
        my.file_path = my.kwargs.get('file_path') 
        my.search_type = my.kwargs.get('search_type')
        my.search_type_obj = SearchType.get(my.search_type)
        web = WebContainer.get_web()
        my.encoder = web.get_form_value('encoder')
        title_row_checkbox = CheckboxWdg("has_title")

        my.has_title = title_row_checkbox.is_checked()

        lowercase_title_checkbox = CheckboxWdg("lowercase_title")

        my.lowercase_title = lowercase_title_checkbox.is_checked()


        my.columns = web.get_form_value("columns")
        if not my.columns: 
            my.columns = my.kwargs.get("columns")
        if my.columns and isinstance(my.columns, basestring):
            my.columns = my.columns.split("|")

        my.labels = web.get_form_value("labels")
        if not my.labels: 
            my.labels = my.kwargs.get("labels")
        if my.labels and isinstance(my.labels, basestring):
            my.labels = my.labels.split("|")
 
        my.csv_column_data = {}
        my.selected_column_option_id = None



    def get_column_preview(my, div):
        # parse the first fow
        csv_parser = CsvParser(my.file_path)
        if my.has_title:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)

        if my.lowercase_title:
            csv_parser.set_lowercase_title(True)
        if my.encoder:
            csv_parser.set_encoder(my.encoder)
        try:    
            csv_parser.parse()
        # that can be all kinds of encoding/decoding exception
        except Exception, e:
            # possibly incompatible encoder selected, use the default instead.
            # Let the user pick it.
            span = SpanWdg('WARNING: The selected encoder is not compatible with your csv file. Please choose the proper one (e.g. UTF-8). Refer to the documentation/tutorial on how to save your csv file with UTF-8 encoding if you have special characters in it.', css='warning')
            div.add(SpanWdg(e.__str__()))
            div.add(HtmlElement.br())
            div.add(span, 'warning')
            return div
        
        # For 2nd guess of similar column titles
        csv_titles = csv_parser.get_titles()
        processed_csv_titles = [x.replace(' ', '_').lower() for x in csv_titles]
        csv_data = csv_parser.get_data()

        web = WebContainer.get_web()
        data_row = web.get_form_value('data_row')
        if not csv_data:
            div.add(SpanWdg('Your csv file seems to be empty', css='warning'))
            return div
        if not data_row:
            data_row = 0
        else:
            try:
                data_row = int(data_row)
                data_row -= 1
            except ValueError:
                data_row = 0

            if data_row >= len(csv_data):
                data_row = len(csv_data)-1
        #data_row_text.set_value(data_row)


        columns_wdg = HiddenWdg("columns")
        div.add(columns_wdg)
        if my.columns:
            columns_wdg.set_value("|".join(my.columns))

        labels_wdg = HiddenWdg("labels")
        div.add(labels_wdg)
        if my.labels:
            labels_wdg.set_value("|".join(my.labels))


        div.add( IconWdg("Important", IconWdg.CREATE) )
        div.add("Use the sample row to match which columns the data will be imported into TACTIC<br/><br/>")
        
        table = Table()
        table.add_class("spt_csv_table")
        table.add_color('background','background')
        table.add_color('color','color')
        table.add_style("width: 100%")

        table.set_attr("cellpadding", "7")
        table.add_border()


        tr = table.add_row()
        tr.add_color("background", "background", -5)
        tr.add_border()
        
        # Checkbox
        cb = CheckboxWdg('csv_row')
        cb.set_default_checked()
        cb.add_behavior( {
            'type': 'click_up',
            'propagate_evt': True,
            'cbjs_action': '''
             // Toggle all cbs off or on
             var top_cb = bvr.src_el;
             var toggle =  top_cb.checked;

             var cbs = top_cb.getParent('.spt_csv_table').getElements('.spt_csv_row');
             for (i=0; i < cbs.length; i++) {
                cbs[i].checked = toggle;
             }
        '''
        } ) 

        th = table.add_header(cb)
        th.add_style("padding: 5px")
        
        # Preview column value
        th = table.add_header("CSV Column Value")
        th.add_style("padding: 5px")
        th.add_class('smaller')
 
        # Matching TACTIC column or new column selection
        th = table.add_header("TACTIC Column")
        th.add_style("padding: 5px")
        th.add_class('smaller')
    
        # Settings activator 
        th = table.add_header("<div class='glyphicon glyphicon-cog'/>")
        th.add_style("padding: 5px")
        th.add_style('min-width: 10px')
        th.add_class('smaller')

        # set the columns and labels
        columns = my.columns
        labels = my.labels
        
        # Get columns or labels if missing
        if not columns:
            columns = SearchType.get_columns(my.search_type)
            sobj = SObjectFactory.create(my.search_type)
            required_columns = sobj.get_required_columns()

            columns.sort()

            labels = []
           
            for column in columns:
                if column in required_columns:
                    label = '%s**'%column
                else:
                    label = column

                label = Common.get_display_title(label)
                labels.append(label)

        elif not labels:
            labels = []
            for column in columns:
                label = Common.get_display_title(column)
                labels.append(label)

       
        # Add an implicit note column
        columns.append("(note)")
        labels.append("Note")


        row = csv_data[data_row]
        my.num_columns = len(row)
        hidden = HiddenWdg("num_columns", my.num_columns)
        div.add(hidden)
 
        skipped_columns = []

        # Column option section - form based on note or new column selection
        column_option_section = DivWdg()
        column_option_section.add_class("spt_column_option_section")
        column_option_section.add_style("padding: 10px")
        column_option_section.add("Column options - select <div class='glyphicon glyphicon-cog'></div> to edit column definition.")
         
        csv_column_data = my.csv_column_data
        print csv_column_data
        # Build the column selection table
        for j, cell in enumerate(row):
            # skip extra empty title
            if j >= len(csv_titles):
                skipped_columns.append(str(j))
                continue

            column_select = SelectWdg("column_%s" % j)

            use_processed = False
            # only set the value if it is actually in there
            if csv_titles[j] in columns:
                column_select.set_option("default", csv_titles[j])
            elif processed_csv_titles[j] in columns:
                column_select.set_option("default", processed_csv_titles[j])
                use_processed = True
            sel_val = column_select.get_value()
            
            
            table.add_row()
            cb = CheckboxWdg('column_enabled_%s' %j) 
            cb.add_style("margin-left: 5px")
            cb.set_default_checked()
            #cb.set_persistence()
            cb.set_persist_on_submit()
            cb.add_class('spt_csv_row')
            # disable the id column by default
            if csv_titles[j] in columns and csv_titles[j] == 'id':
                cb.set_option('special','true')
                cb.add_behavior({
                    'type':'click_up',
                    #'propagate_evt': True,
                    'cbjs_action': '''
            spt.alert('The id column is not meant to be imported. It can only be chosen as an Identifying Column for update purpose.'); bvr.src_el.checked = false;
                    '''
                } )
            else:
                # if it is not a new column, and column selected is empty, we don't select the checkbox by default
                if sel_val != '' or not my.is_refresh:
                    cb.set_default_checked()

            table.add_cell(cb) 
            td = table.add_cell(cell)
            td.add_style("padding: 3px")
            
            # this is an optimal max width
            td.add_style('max-width: 600px')

            column_select.add_behavior({'type': "change",
                'cbjs_action': '''if (bvr.src_el.value !='') {
                    set_display_off('new_column_div_%s');
                } else {
                    set_display_on('new_column_div_%s')
                };

                var values = spt.api.Utility.get_input_values('csv_import_main');
                spt.panel.refresh('preview_data', values );

            '''% (j,j)})

            # Get new column or note process options
            column_data = csv_column_data.get(j)
            
            processed_title = ""
            processed_type = ""
            process_value = ""
            if column_data and my.has_title:
                processed_title = column_data.get("name")
                if processed_title == "(note)":
                    process_value = column_data.get("process")
                    if not process_value:
                        process_value = "publish"
                else:
                    if not processed_title and use_processed:
                        processed_title = processed_csv_titles[j]
                    if not processed_title:
                        processed_title = csv_titles[j]
                    
                    processed_type = column_data.get("type")
                    if not processed_type:
                        processed_type = my._guess_column_type(csv_data, j)
            
            
            column_select.add_empty_option("%s (New)" % processed_title)
            column_select.set_persist_on_submit()
            column_select.set_option("values", columns)
            column_select.set_option("labels", labels)

            display = column_select.get_buffer_display()
            td = table.add_cell( display )
            td.add_style("padding: 3px")

            # Secondary column options - column type or note process
            column_option_div = IconWdg(icon="BS_COG")
            td = table.add_cell( column_option_div )
            if sel_val == '(note)' or sel_val == '':
                column_option_div.add_style("opacity", "0.0")
                column_option_div.add_behavior( {
                    'type': 'mouseenter',
                    'cbjs_action': '''
                        bvr.src_el.setStyle("opacity", "1.0");
                    '''
                } )
                column_option_div.add_behavior( {
                    'type': 'mouseleave',
                    'cbjs_action': '''
                        bvr.src_el.setStyle("opacity", "0.0");
                    '''
                } )
                column_option_div.add_behavior( {
                    'type': "click",
                    'id': str(j),
                    'cbjs_action': '''
                    var values = spt.api.Utility.get_input_values('csv_import_main');
                    values['selected_column_option_id'] = bvr.id; 
                    spt.panel.refresh('preview_data', values );
                    '''
                } )
                
                if my.selected_column_option_id == j: 
                    options_form = DivWdg(id="column_options_form")
                    column_option_section.add(options_form) 
                    options_form.add_style("margin-top", "10px")
                    options_form.add_class("spt_form")
                    
                    # Inputs in form depend on note or new column
                    options_form_inputs = DivWdg()
                    options_form.add(options_form_inputs)
                    options_form_inputs.add_style("display", "inline-block")
                    # Save script should update HiddenWdg form values and refresh
                    save = ActionButtonWdg(title="Save")
                    save.add_style("display", "inline-block")
                    save.add_style("padding", "5px")
                    save.add_style("float", "right")
                    options_form.add(save)
                    save.add_behavior( {
                        'type': 'click_up',
                        'id': str(j),
                        'cbjs_action': '''
                            var values = spt.api.Utility.get_input_values('csv_import_main');
                            var settings = spt.api.Utility.get_input_values('column_options_form');
                            
                            name_key = 'new_column_' + bvr.id;
                            if (settings['column_option_name']) {
                                values[name_key] = settings['column_option_name']; 
                            }

                            type_key  = 'new_column_type_' + bvr.id;
                            if (settings['column_option_type']) {
                                values[type_key] = settings['column_option_type']; 
                            }

                            note_process_key = 'new_note_process_' + bvr.id;
                            note_process = settings['new_note_process'];
                            if (note_process == 'custom') {
                                note_process = settings['new_note_process_custom'];
                            }
                            
                            if (note_process) {
                                values[note_process_key] = note_process; 
                            }

                            values['selected_column_option_id'] = bvr.id; 
                            spt.panel.refresh('preview_data', values );
                        '''
                    } )
            else:
                column_option_div.add_style("display", "none")
 
            if sel_val == '(note)':
                # Context options for note column
                process = HiddenWdg("new_note_process_%s" % j)
                column_option_div.add( process )
                process.add_style("display", "none")
                if not process_value:
                    process_value = "publish"
                process.set_value(process_value)
                
                # Option form for new note column
                if my.selected_column_option_id == j:
                    note_process_group = DivWdg()
                    options_form_inputs.add(note_process_group)
                    note_process_group.add_class("form-group")
                    note_process_group.add_style("display", "inline-block")
                    note_process_group.add_style("padding", "5px")
                    
                    note_process_group.add("<label>Note process</label>")
                    
                    note_process_input_group = DivWdg()
                    note_process_group.add(note_process_input_group)
                   
                    # Choose process from pipeline (SelectWdg) or custom process (TextWdg)
                    # Custom process is hidden by default
                    process_pipeline_input = SelectWdg("new_note_process")
                    note_process_input_group.add(process_pipeline_input)
                    
                    # Get processes from pipelines, and add 'publish' and 'custom' options
                    from pyasm.biz import Pipeline
                    search_type_obj = SearchType.get(my.search_type)
                    base_type = search_type_obj.get_base_key()
                    pipelines = Pipeline.get_by_search_type(base_type)
                    all_processes = []
                    for pipeline in pipelines:
                        process_names = pipeline.get_process_names()
                        all_processes.extend(process_names) 
                    process_names = list(set(all_processes))
                    
                    process_names.append("publish")
                    if process_value not in process_names:
                        process_names.append(process_value)
                    process_pipeline_input.set_option("values", process_names)
                    process_pipeline_input.set_option("default", process_value)
                    process_pipeline_input.append_option("Custom process", "custom")
                    
                    process_pipeline_input.add_style("display", "inline-block")
                    process_pipeline_input.add_class("form-control")
                    process_pipeline_input.add_style('border-color: #8DA832')
                    process_pipeline_input.add_style("width", "150px")
                    process_pipeline_input.add_behavior( {
                        'type': 'change',
                        'cbjs_action': '''
                            // Toggle display of custom input
                            var pipeline_input = bvr.src_el;
                            var input_top = pipeline_input.getParent(".form-group");
                            var custom_input = input_top.getElement(".spt_custom_process_input");
                            var select_value = pipeline_input.value;
                            if (select_value == 'custom') {
                                custom_input.setStyle("display", "inline-block");
                            } else {
                                custom_input.setStyle("display", "none");
                            }
                        '''
                    } )

                    process_text_input = TextWdg("new_note_process_custom")
                    note_process_input_group.add(process_text_input)
                    process_text_input.add_class("spt_custom_process_input")
                    process_text_input.add_class("form-control")
                    process_text_input.add_style("margin-left", "5px")
                    process_text_input.add_style("display", "none")
                    process_text_input.add_class("form-control")
                    process_text_input.add_style('border-color: #8DA832')
                    process_text_input.add_style("width", "150px")

            elif sel_val == '':
                # Name and type options for new column
                column_name = HiddenWdg("new_column_%s" % j)
                column_option_div.add( column_name )
                column_name.set_value(processed_title)
 
                column_type = HiddenWdg("new_column_type_%s" % j)
                column_option_div.add( column_type )
                column_type.set_value(processed_type)
      
                # Option form for new column
                if my.selected_column_option_id == j:
                    column_name_group = DivWdg()
                    options_form_inputs.add(column_name_group)
                    column_name_group.add_class("form-group")
                    column_name_group.add_style("display", "inline-block")
                    column_name_group.add_style("padding", "5px")

                    column_name_group.add("<label>Column name</label>") 
                    column_name_input = TextWdg("column_option_name")
                    column_name_group.add(column_name_input)
                    column_name_input.add_class("form-control")
                    column_name_input.add_style('border-color: #8DA832')
                    column_name_input.add_style("width", "150px")
                    column_name_input.set_value(processed_title)

                    column_type_group = DivWdg()
                    options_form_inputs.add(column_type_group)
                    column_type_group.add_class("form-group")
                    column_type_group.add_style("display", "inline-block")
                    column_type_group.add_style("padding", "5px")
                    
                    column_type_group.add("<label>Column type</label>")
                    column_type_input = SelectWdg("column_option_type")
                    column_type_group.add( column_type_input )
                    column_type_input.set_option("values", "varchar(256)|text|integer|float|timestamp")
                    column_type_input.add_class("form-control")
                    column_type_input.add_style('border-color: #8DA832')
                    column_type_input.add_style("width", "150px")
                    column_type_input.set_option("default", processed_type)

        if skipped_columns:
            div.add(SpanWdg('WARNING: Some titles are empty or there are too many data cells. Column index [%s] '\
                'are skipped.' %','.join(skipped_columns), css='warning'))
            div.add(HtmlElement.br(2))


        div.add(table)

        # Add the options form
        div.add(column_option_section)



     
    

    def get_display(my):


        web = WebContainer.get_web()

        csv_parser = CsvParser(my.file_path)
        if my.encoder:
            csv_parser.set_encoder(my.encoder)

        try:    
            csv_parser.parse()
        # that can be all kinds of encoding/decoding exception
        except Exception, e:
            # possibly incompatible encoder selected, use the default instead.
            # Let the user pick it.
            span = SpanWdg('WARNING: The selected encoder is not compatible with your csv file. Please choose the proper one. Refer to the documentation/tutorial on how to save your csv file with UTF-8 encoding if you have special characters in it.', css='warning')
            widget.add(span, 'warning')
            return widget
            #csv_parser.set_encoder(None)
            #csv_parser.parse()

        csv_titles = csv_parser.get_titles()
        csv_column_data = {}
        csv_data = csv_parser.get_data()

        columns = []
        num_columns = len(csv_titles)
        for i in range(0, num_columns):
            column = web.get_form_value("column_%s" % i)
            if column == "(note)":
                # If new column is a note, get note process:
                new_note_process = web.get_form_value("new_note_process_%s" % i)
                csv_column_data[i] = {'name': '(note)', 'process': new_note_process}
                columns.append('note')
            elif column == "":
                new_column_name = web.get_form_value("new_column_%s" % i)
                new_column_type = web.get_form_value("new_column_type_%s" % i)
                csv_column_data[i] = {'name': new_column_name, 'type': new_column_type}
                columns.append(new_column_name)
            else:
                csv_column_data[i] = {'name': column}
                columns.append(column)
        my.csv_column_data = csv_column_data

        # Get the selected column option id
        selected_column_option_id = web.get_form_value("selected_column_option_id")
        try:
            my.selected_column_option_id = int(selected_column_option_id)
        except ValueError:
            my.selected_column_option_id = None

        # Preview data and column selection 
        widget = DivWdg(id='preview_data')
        widget.add_style('padding: 6px')
        my.set_as_panel(widget)
        widget.add(SpanWdg(), 'warning')
        widget.add(HtmlElement.br(2))
        my.get_column_preview(widget)

        response_div = DivWdg(css='spt_cmd_response')
        #response_div.add_style('color','#F0C956') 
        response_div.add_color('background','background3')
        response_div.add_color('color','color3') 
        response_div.add_style('padding: 30px')
        response_div.add_style('display: none')
        widget.add(HtmlElement.br())
        widget.add(response_div)
        widget.add(HtmlElement.br(2))

        sobject_title = my.search_type_obj.get_title()
        div = DivWdg(css='spt_csv_sample')
        widget.add(div)
        h3 = DivWdg("Preview Data") 
        #h3.add_border()
        h3.add_color('color','color')
        #h3.add_gradient('background','background', -5)
        h3.add("<hr style='dashed'/>")
        h3.add_style("padding: 5px")
        h3.add_style("font-weight: bold")
        h3.add_style("margin-left: -20px")
        h3.add_style("margin-right: -20px")
        div.add(h3)
        div.add("</br>")
        
        refresh_button = ActionButtonWdg(title="Refresh")

        refresh_button.add_behavior({'type' : 'click_up',
                    'cbjs_action': "spt.panel.refresh('preview_data',\
                    spt.api.Utility.get_input_values('csv_import_main'))"})

        refresh_button.add_style("float: left")
        div.add(refresh_button)



        import_button = ActionButtonWdg(title="Import")
        import_button.set_id('CsvImportButton')
        import_button.add_behavior({
            'type':'click_up', 
            'top_id':'csv_import_main',
            'cbjs_action':'''
            var src_el = bvr.src_el;

            var project = spt.Environment.get().get_project();
            var my_search_type = bvr.search_type;
            var top_id = bvr.top_id;

            values = spt.api.Utility.get_input_values(top_id);

            var server = TacticServerStub.get();
            var class_name = 'pyasm.command.CsvImportCmd';

            var response_div = src_el.getParent('.spt_panel').getElement('.spt_cmd_response');
            var csv_control = src_el.getParent('.spt_panel').getElement('.spt_csv_sample')
            
            var run_cmd = function (start_index) {
                spt.app_busy.show("Importing Data");
         
                server.execute_cmd(class_name, {}, values,  {on_complete: on_complete, on_error: on_error});

                // TODO... why is there a set timeout here?
                setTimeout(function() {spt.hide(csv_control)}, 500);
            }
 
            var on_complete = function(response_div) {
                spt.app_busy.hide();
                
                response_div.innerHTML = 'CSV Import Completed';
                 
                setTimeout( function() { 
                    var popup = bvr.src_el.getParent(".spt_popup");
                    if (popup) {
                        spt.popup.hide_background();
                        popup.destroy();
                    }
                    spt.table.run_search() } , 2000
                );
            }
           
            /* On error includes handling of failure for single commit.
             * If a single commit fails, user is prompted to skip that 
             * entry or abort entire import. */
            var on_error = function(e) {
                spt.app_busy.hide();
                
                // This function is executed when Command fails or user
                // chooses to abort after single entry fails.
                var abort = function() {
                    var response_div = document.getElement('.spt_cmd_response');
                    err_message = err_message.replace(/\\n/g,'<br/>');
                    response_div.innerHTML = 'Error: ' + err_message;
                    response_div.setStyle("display", "");
                    setTimeout(function() {spt.show(csv_control)}, 500);
                }

                var err_message = spt.exception.handler(e);
                //TODO err_message should be dictionary...
                
                if err_message.startsWith("Error creating new entry for row") {
                    message = "Upload failed with the following message: " + spt.exception.handler(err) + ". Try again?";
                    fail_index = 1;
                    ok_fn = run_cmd;
                    ok_fn_args = {}
                    cancel_fn = abort();
                    options = {ok_args: [fail_index], okText: "Skip"}; 
                    spt.confirm(message, ok_fn, cancel_fn, options);
                    return;
                } else {
                    spt.error(err_message);
                    abort();
                }
            }

            '''
        })
        import_button.add_style("float: left")
        div.add( import_button )
        div.add(HtmlElement.br(clear='all'))
        div.add(HtmlElement.br(clear='all'))

        message_div = DivWdg("The following table will be imported into <b>%s</b> (Showing Max: 100)" % sobject_title)
        message_div.add_color('color','color')
        message_div.add_style('margin-left: 14px')
        div.add(message_div)
        
        widget.add(HtmlElement.br())


        table_div = DivWdg()
        widget.add(table_div)
        table_div.add_style("max-width: 800px")
        table_div.add_style("overflow-x: auto")


        # draw the actual table of data
        table = Table()
        table_div.add(table)
        table.add_color('background','background')
        table.add_color('color','color')
        table.add_border()
        table.set_attr("cellpadding", "3")
        #table.add_attr('border','1')

        table.add_style("width: 100%")


        table.add_row()
        for i, title in enumerate(columns):
            if not title:
                title = "<b style='color:red'>*</b>"
            th = table.add_header(title)
            th.add_style("min-width: 100px")
            th.add_color("background", "background", -5)
            th.add_style("padding: 3px")
            th.add_style("text-align: left")

        for i, row in enumerate(csv_data):
            if i > 100:
                break
            tr = table.add_row()
            if i % 2:
                tr.add_color("background", "background")
            else:
                tr.add_color("background", "background3")

            for j, cell in enumerate(row):
                column_type = web.get_form_value("new_column_type_%s" % j)
                td = table.add_cell(cell)

                if column_type == 'timestamp' and not my._check_timestamp(cell):
                    td.add_style("color: red")
                if column_type == 'integer' and not my._check_integer(cell):
                    td.add_style("color: red")
                if column_type == 'float' and not my._check_float(cell):
                    td.add_style("color: red")


        return widget 

    def _guess_column_type(my, csv_data, idx):
        ''' given csv data and a column idx, determine appropriate data type '''
        column_types = {}
        data_cell_list = []
        my.CHECK = 5
        column_type = ''       
        for k, row in enumerate(csv_data):
            if k >= len(row):
                data = ''
            else:
                data = row[idx] 
            if data.strip() == '':
                continue
            if my.CHECK == 5:
                column_type = my._check_timestamp(data)
            if my.CHECK == 4:
                column_type = my._check_integer(data)
            if my.CHECK == 3:
                column_type = my._check_float(data)
            if my.CHECK == 2:
                column_type = my._check_varchar(data)

            # TEST: use democracy to determine type
            column_type = my._check_timestamp(data)
            if not column_type:
                column_type = my._check_integer(data)
                if not column_type:
                    column_type = my._check_float(data)
                    if not column_type:
                        column_type = my._check_varchar(data)

            if column_types.get(column_type) == None:
                column_types[column_type] = 1
            else:
                column_types[column_type] = column_types[column_type] + 1


            # max 30 per analysis    
            if k > 30:
                break

        largest = 0
        for key, num in column_types.items():
            if num > largest:
                column_type = key
                largest = num
            return column_type
    
    # ensure this is not a partial date, which should be treated as a regular integer
    def _parse_date(my, dt_str):    
        from dateutil import parser
        dt = parser.parse(dt_str, default=datetime.datetime(1900, 1, 1)).date()
        dt2 = parser.parse(dt_str, default=datetime.datetime(1901, 2, 2)).date()
        if dt == dt2:
            return dt
        else:
            return None


    def _check_varchar(my, data):
        column_type = None
        if len(data) <= 256:
            column_type = 'varchar(256)'
        else:
            my.CHECK = 1
            column_type = 'text'
       
        return column_type

    def _check_integer(my, data):
        column_type = None
        try:
            int(data)
            column_type = 'integer'
        except ValueError, e:
            my.CHECK = 3
       
        return column_type

    def _check_float(my, data):
        column_type = None
        try:
            float(data)
            column_type = 'float'
        except ValueError, e:
            my.CHECK = 2
        return column_type

    def _check_timestamp(my, data):
        column_type = None
        try: 
            timestamp = my._parse_date(data)
            if timestamp:
                column_type = 'timestamp'
            else:
                # if it is just some number instead of a real date or timestamp
                column_type = my._check_integer(data)
                if column_type:
                    my.CHECK = 4
                else:
                    my.CHECK = 3
        except Exception, e:
            my.CHECK = 4
           
        return column_type 




