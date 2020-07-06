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


__all__ = ['CsvExportWdg', 'CsvDownloadWdg', 'CsvImportWdg']

import csv, os
import string
import datetime
import shutil

from pyasm.biz import CsvParser, File, Project
from pyasm.search import Search, SObjectFactory, SearchType, SearchKey
from pyasm.command import Command, FileUpload, CsvImportCmd
from pyasm.web import HtmlElement, SpanWdg, DivWdg, Table, WebContainer, Widget, FloatDivWdg 
from pyasm.widget import CheckboxWdg, IconSubmitWdg, HiddenRowToggleWdg, HiddenWdg, WidgetConfigView, ProdIconButtonWdg, TextWdg, TextAreaWdg, IconWdg, ProgressWdg, HintWdg, SelectWdg
from pyasm.common import Common, Environment, TacticException

from tactic.ui.common import BaseRefreshWdg

from .misc_input_wdg import SearchTypeSelectWdg
from .upload_wdg import SimpleUploadWdg
from .button_new_wdg import ActionButtonWdg
from .swap_display_wdg import SwapDisplayWdg

class CsvExportWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {'search_type': 'Search Type',
                'view': 'View of the search type',
                'related_view': 'Related View of search type',
                'mode': 'export mode',
                'selected_search_keys': 'Selected Search Keys',
                'document': 'document to be exported',
                'search_class': 'Custom search class used',
                }


    def init(self):
        self.search_type = self.kwargs.get('search_type')
        # reconstruct the full search_type if it's base SType
        if self.search_type.find("?") == -1:
            project_code = Project.get_project_code()
            self.search_type = SearchType.build_search_type(self.search_type, project_code)
        
        self.view = self.kwargs.get('view')
        self.element_names = self.kwargs.get('element_names')
        self.related_view = self.kwargs.get('related_view')
        self.search_class = self.kwargs.get('search_class')
        self.search_view = self.kwargs.get('search_view')
        self.simple_search_view = self.kwargs.get('simple_search_view')
        self.mode = self.kwargs.get('mode')
        self.close_cbfn = self.kwargs.get('close_cbfn')
        self.input_search_keys = self.kwargs.get('selected_search_keys')
        self.selected_search_keys = []
        self.error_msg = ''
        self.search_type_list = []
        self.is_test = self.kwargs.get('test') == True
        self.table = None
        self.document = self.kwargs.get("document")

    def check(self):
        if self.mode == 'export_matched':
            from tactic.ui.panel import TableLayoutWdg
            self.table = TableLayoutWdg(search_type=self.search_type, view=self.view,\
                show_search_limit='false', search_limit=-1, search_view=self.search_view,\
                search_class=self.search_class, simple_search_view=self.simple_search_view, init_load_num=-1)
            self.table.handle_search()
            search_objs = self.table.sobjects
            self.selected_search_keys = SearchKey.get_by_sobjects(search_objs, use_id=True)
            return True

        for sk in self.input_search_keys:
            st = SearchKey.extract_search_type(sk)
            if st not in self.search_type_list:
                self.search_type_list.append(st)

            id = SearchKey.extract_id(sk)
            if id == '-1':
                continue
            
            self.selected_search_keys.append(sk)
        
        if len(self.search_type_list) > 1:
            self.check_passed = False
            self.error_msg = 'More than 1 search type is selected. Please keep the selection to one type only.'
            return False

        if not self.search_type_list and self.mode == 'export_selected':
            self.check_passed = False
            self.error_msg = 'Search type cannot be identified. Please select a valid item.'
            return False
        return True

    def get_display(self): 
      
        top = self.top
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("padding: 10px")
        top.add_style("min-width: 400px")
     
        from tactic.ui.app import HelpButtonWdg
        help_wdg = HelpButtonWdg(alias="exporting-csv-data")
        top.add(help_wdg)
        help_wdg.add_style("float: right")
        help_wdg.add_style("margin-top: -3px")
        
        if not self.check(): 
            top.add(DivWdg('Error: %s' %self.error_msg))
            top.add(HtmlElement.br(2))
            return super(CsvExportWdg, self).get_display()

        if self.search_type_list and self.search_type_list[0] != self.search_type:
            st = SearchType.get(self.search_type_list[0])
            title_div =DivWdg('Exporting related items [%s]' % st.get_title())
            top.add(title_div)
            top.add(HtmlElement.br())
            self.search_type = self.search_type_list[0]
            self.view = self.related_view

        if self.mode != 'export_all':
            num = len(self.selected_search_keys)
        else:
            search = Search(self.search_type)
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
        div.add_color("background", "background", -5)
        div.add_style("padding: 10px")
        div.add_style("margin: 5px")
        
        div.add_styles('max-height: 350px; overflow: auto')
        table = Table()
        table.add_color("color", "color")
        div.add(table)
        table.set_id('csv_export_table')
        table.center()
        table.add_style("width: 70%")
        
        
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
        td.add_style("padding: 10px 0px")
        label = HtmlElement.i('toggle all')
        label.add_style('color: #888')
        td = table.add_cell(label)
        td.add_style("padding: 3px")


        col1 = table.add_col()
        col1.add_style('width: 35px')
        col2 = table.add_col()
        
        if not self.search_type or not self.view:
            return table

        # use overriding element names and derived titles if available
        config = WidgetConfigView.get_by_search_type(self.search_type, self.view)
        if self.element_names and config:
            filtered_columns = self.element_names
            titles = []
            for name in self.element_names:
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
            td = table.add_cell(cb)
            td.add_style("padding: 5px 0px")
            
            
            title = titles[idx]
            #td = table.add_cell('<b>%s</b> (%s) '%(title, column))
            td = table.add_cell('<b>%s</b>'%(title))
            td.add_style("padding: 3px")



        widget = DivWdg()

        show_include_id = self.kwargs.get("show_include_id")
        if show_include_id in ['false', False]:
            widget.set_style("display: none")

        table.add_row_cell(widget)
        widget.add_style("margin: 20px 0 10px 0px")
        cb = CheckboxWdg('include_id', label=" Include ID")
        cb.set_default_checked()
        widget.add(cb)
        hint = HintWdg('To update entries with specific ID later, please check this option. For new inserts in this or other table later on, uncheck this option.') 
        widget.add(" ")
        widget.add(hint)





        label = string.capwords(self.mode.replace('_', ' '))
        button = ActionButtonWdg(title=label, size='l')
        is_export_all  = self.mode == 'export_all'

        button.add_behavior({
        'type': "click_up",
        'element': 'csv_export',
        'column_names': 'csv_column_name',
        'search_type': self.search_type,
        'view': self.view,
        'search_keys' : self.selected_search_keys,
        'document': self.document,
        'is_export_all' : is_export_all,
        'cbfn_action': '''
        //spt.dg_table_action.csv_export

        var my_search_type = bvr.search_type;
        var my_is_export_all = bvr.is_export_all;
        var filename = my_search_type.replace(/[\/\?\=]/g,"_") + "_" + bvr.view + ".csv";
        //var class_name = "pyasm.widget.CsvDownloadWdg";
        var class_name = "tactic.ui.widget.CsvDownloadWdg";
        var column_name_vals = spt.api.Utility.get_input_values('csv_export_table', 'input[name=' + bvr.column_names+']');
        var selected_search_keys = '';
        if (my_is_export_all != 'true')
            selected_search_keys = bvr.search_keys;

        var column_names = column_name_vals[bvr.column_names];
        var no_column_name = true;

        for (var k=0;  k<column_names.length; k++){
            if(column_names[k] != '') {
                no_column_name = false;
                break;
            }
        }
        var my_include_id = spt.api.Utility.get_input('csv_export_action',
            'include_id').checked;

        if ( no_column_name && !my_include_id) {
            alert('Please select at least 1 column or just the "Include ID" checkbox')
            return;
        }

        var options = {
            search_type: my_search_type,
            view: bvr.view,
            filename: filename,
            column_names: column_names,
            search_keys: selected_search_keys,
            document: bvr.document,
            include_id: my_include_id
        };
        var popup = bvr.src_el.getParent('.spt_popup');
        // this is assgined in spt.dg_table.gear_smenu_export_cbk
        var values = popup.values_dict;

        var server = TacticServerStub.get();


        var kwargs = {'args': options, 'values': values};
        var rtn_file_path = '';
        try {
            rtn_file_path = server.get_widget(class_name, kwargs);
        } catch(e) {
            spt.error(spt.exception.handler(e));
            return;
        }
        if (rtn_file_path.length > 200 ) {
            spt.alert("Error exporting one of the widgets:\\n" + rtn_file_path, {type: 'html'} );
            return;
        }


        document.location = rtn_file_path;

        ''',
            
        })

        self.close_action = "var popup = bvr.src_el.getParent('.spt_popup');spt.popup.close(popup)"
        if self.close_action:
            close_button = ActionButtonWdg(title='Close')
            close_button.add_behavior({
                'type': "click",
                'cbjs_action': self.close_action
            })




        top.add(div)
        top.add(HtmlElement.br())

        action_div = DivWdg()
        top.add(action_div)


        table = Table()
        action_div.add(table)
        table.center()
        table.add_row()
        td = table.add_cell(button)
        td.add_style("width: 130px")
        table.add_cell(close_button)

        action_div.add("<br clear='all'/>")

        if self.is_test:
            rtn_data = {'columns': self.element_names, 'count': len(self.selected_search_keys)}
            if self.mode == 'export_matched':
                rtn_data['sql'] =  self.table.search_wdg.search.get_statement()
            from pyasm.common import jsondumps
            rtn_data = jsondumps(rtn_data)
            return rtn_data

        return top


class CsvDownloadWdg(BaseRefreshWdg):
    '''Dynamically generates a csv file to download'''

    def get_args_keys(self):
        return {'table_id': 'Table Id', 'search_type': 'Search Type',
                'close_cbfn': 'Cbk function',
                'view': 'View of search type',
                'column_names': 'Column Names to export',
                'filename': 'filename to export',
                'search_keys': 'True if it is in title mode',
                'search_type': 'Selected Search Keys',
                'document': 'Document to be exported',
                'include_id': 'Include an id in export'}

    def init(self):
        self.filename = self.kwargs.get("filename")
        self.column_names = self.kwargs.get('column_names')
        self.view = self.kwargs.get('view')
        self.search_type = self.kwargs.get('search_type')
        self.close_cbfn = self.kwargs.get('close_cbfn')
        self.include_id = self.kwargs.get('include_id')
        self.search_keys = self.kwargs.get('search_keys')
        self.document = self.kwargs.get('document')
        #if self.search_keys:
        #    self.search_keys = self.search_keys.split(',')


    def get_display(self):
        web = WebContainer.get_web()

        column_names = self.column_names
        column_names = [ x for x in column_names if x ]
        # create the file path
        tmp_dir = web.get_upload_dir()

        env = Environment.get()
        asset_dir = env.get_asset_dir()
        web_dir = env.get_web_dir()
        tmp_dir = env.get_tmp_dir()

        ticket = Environment.get_ticket()
        link = "%s/temp/%s/%s" % (web_dir, ticket, self.filename)

        file_path = "%s/%s" % (tmp_dir, self.filename)

        from pyasm.command import CsvExportCmd

        cmd = CsvExportCmd(self.search_type, self.view, column_names, file_path, document=self.document)
        if self.search_keys:
            cmd.set_search_keys(self.search_keys)

        cmd.set_include_id(self.include_id)
        try:
            cmd.execute()
        except Exception as e:
            raise

        asset_download_dir = "%s/temp/%s" % (asset_dir, ticket)
        if not os.path.exists(asset_download_dir):
            os.makedirs(asset_download_dir)
        download_path = "%s/%s" % (asset_download_dir, self.filename)
        if os.path.exists(download_path):
            os.remove(download_path)
        shutil.move(file_path, asset_download_dir)

        return link





class CsvImportWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
                'search_type': 'Search Type to import'}


    def init(self):
        web = WebContainer.get_web()
        
        self.is_refresh = self.kwargs.get('is_refresh')
        if not self.is_refresh:
            self.is_refresh = web.get_form_value('is_refresh')

        self.search_type = self.kwargs.get('search_type')
        if not self.search_type:
            self.search_type = web.get_form_value('search_type_filter')
        self.close_cbfn = self.kwargs.get('close_cbfn')

        self.data = web.get_form_value("data")
        self.web_url = web.get_form_value("web_url")
        self.file_path = None
        if self.web_url:
            import urllib2
            response = urllib2.urlopen(self.web_url)
            csv = response.read()
            self.file_path = "/tmp/test.csv"
            f = open(self.file_path, 'w')
            f.write(csv)
            f.close()

        if not self.file_path:
            self.file_path =  web.get_form_value('file_path')

        if not self.file_path:
            ticket = web.get_form_value('html5_ticket')
            if not ticket:
                ticket =  web.get_form_value('csv_import|ticket')

            file_name =  web.get_form_value('file_name')
            if self.data:
                if not file_name:
                    file_name = "%s.csv" % ticket

                self.file_path = '%s/%s' %(web.get_upload_dir(ticket=ticket), file_name)
                import codecs
                f = codecs.open(self.file_path, 'wb', 'utf-8')
                #f = open(self.file_path, "wb")
                f.write(self.data)
                f.close()
            elif file_name:
                self.file_path = '%s/%s' %(web.get_upload_dir(ticket=ticket), file_name)
                

        self.columns = self.kwargs.get("columns")
        if not self.columns:
            self.columns = web.get_form_value("columns")
        if self.columns and isinstance(self.columns, basestring):
            self.columns = self.columns.split("|")

        self.labels = self.kwargs.get("labels")
        if not self.labels:
            self.labels = web.get_form_value("labels")
        if self.labels and isinstance(self.labels, basestring):
            self.labels = self.labels.split("|")




    def get_display(self):
        
        widget = DivWdg()

        show_title = self.kwargs.get("show_title") not in [False, 'false']

        if show_title and not self.is_refresh:
            title_div = DivWdg()
            widget.add(title_div)
            title_div.add_style("margin: 10px 20px")

            title_wdg = DivWdg()
            title_div.add(title_wdg)
            title_wdg.add_style("font-size: 25px")
            title_wdg.add("Import Data")

            title_wdg = DivWdg()
            title_div.add(title_wdg)
            title_wdg.add("Bulk upload data using a CSV file or copy data directly from a spreadsheet")
            title_wdg.add("<hr/>")


        widget.add_style('padding: 10px')
        widget.add_style('font-size: 12px')
        #widget.add_border()
        widget.add_color('color','color') 
        widget.add_color('background','background') 
        widget.add_class("spt_import_top")
       

        inner = DivWdg()
        widget.add(inner)
        inner.add( self.get_first_row_wdg() )
        inner.add(ProgressWdg())

        if self.is_refresh:
            return inner
        else:
            return widget

    def get_upload_wdg(self):
        '''get search type select and upload wdg'''

        key = 'csv_import'


        widget = DivWdg(css='spt_import_csv')
        widget.add_color('color','color')
        widget.add_color('background','background')
        widget.add_style('width: 600px')

        # get the search type
        stype_div = DivWdg()
        widget.add(stype_div)



        show_stype_select = self.kwargs.get("show_stype_select")
        if show_stype_select in ['true',True] or not self.search_type:

            title = DivWdg("<b>Select sType to import data into:</b>&nbsp;&nbsp;")
            stype_div.add( title )
            title.add_style("float: left")

            search_type_select = SearchTypeSelectWdg("search_type_filter", mode=SearchTypeSelectWdg.ALL)
            search_type_select.add_empty_option("-- Select --")
            if not search_type_select.get_value():
                search_type_select.set_value(self.search_type)
            search_type_select.set_persist_on_submit()

            stype_div.add(search_type_select)



            search_type_select.add_behavior( {'type': 'change', \
                  'cbjs_action': "spt.panel.load('csv_import_main','%s', {}, {\
                  'search_type_filter': bvr.src_el.value});" %(Common.get_full_class_name(self)) } )

        else:
            hidden = HiddenWdg("search_type_filter")
            stype_div.add(hidden)
            hidden.set_value(self.search_type)


        if self.search_type:
            sobj = None
            try:
                sobj = SObjectFactory.create(self.search_type)
            except ImportError:
                widget.add(HtmlElement.br())
                widget.add(SpanWdg('WARNING: Import Error encountered. Please choose another search type.', css='warning')) 
                return widget

            extra_data = self.kwargs.get("extra_data")

            required_columns = sobj.get_required_columns()
            if required_columns:
                widget.add(HtmlElement.br())
                req_span = DivWdg("Required Columns: ", css='med')
                req_span.add_color('color','color')
                widget.add(req_span)
                #required_columns = ['n/a']
                req_span.add(', '.join(required_columns))

            widget.add( HtmlElement.br() )



            if self.file_path:
                hidden = HiddenWdg("file_path", self.file_path)
                widget.add(hidden)

                button = ActionButtonWdg(title='Start Again')
                button.add_style('float','right')
                button.add_behavior( {
                    'type': 'click_up', 
                    'columns': "|".join(self.columns),
                    'labels': "|".join(self.labels),
                    'cbjs_action': '''
                    spt.panel.load('csv_import_main','%s', {}, {
                        search_type_filter: '%s',
                        columns: bvr.columns,
                        labels: bvr.labels,
                        is_refresh: true
                    });''' %(Common.get_full_class_name(self), self.search_type)
                } )
                widget.add(button)


                
                if self.web_url:
                    file_div = FloatDivWdg('URL: <i>%s</i>&nbsp;&nbsp;&nbsp;' %self.web_url, css='med')

                else:
                    if not self.data:
                        file_div = FloatDivWdg('File uploaded: <i>%s</i>&nbsp;&nbsp;&nbsp;' %os.path.basename(self.file_path), css='med')
                    else:
                        lines = len(self.data.split("\n"))
                        file_div = DivWdg("Found <b>%s</b> entries." % lines)

                file_div.add_color('color','color')
                file_div.add_style('margin: 8px 0 0 10px')
                file_div.add_style('font-size: 14px')
                widget.add(file_div)

                widget.add("<br clear='all'/>")
                widget.add(HtmlElement.br())
                return widget

            widget.add_style("overflow-y: auto")

            msg = DivWdg()
            widget.add(msg)
            msg.add_border()
            msg.add_style("width: 500px")
            msg.add_color("background", "background", -3)
            msg.add_style("padding: 30px")
            msg.add_style("margin: 10 auto")

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
            browse_div = DivWdg()
            msg.add(browse_div)
            browse = UploadButtonWdg(name='new_csv_upload', title="Upload a CSV file", tip="Click to choose a csv file", on_complete=on_complete, ticket=ticket, width=250)

            browse_div.add(browse)
            browse_div.add_style("width: 250")
            browse_div.add_style("margin: 0px auto")


            
            # this is now only used in the copy and paste Upload button for backward-compatibility
            upload_div = DivWdg()
            msg.add(upload_div)
            upload_div.add_style("display: none")
            upload_wdg = SimpleUploadWdg(key=key, show_upload=False)
            upload_div.add(upload_wdg)


            msg.add("<br/>")
          

            msg.add("<div style='margin: 30px; text-align: center'>-- OR --</div>")

            msg.add("<b>Copy and Paste from a Spreadsheet: </b><br/>") 
            text = TextAreaWdg("data")
            text.add_style('width: 100%')
            text.add_style('height: 100px')
            text.add_class("spt_import_cut_paste")
            msg.add(text)
            msg.add("<br/>"*3)


            button = ActionButtonWdg(title="Parse List", color="default", width=250)
            button.add_style("margin: 5px auto")
            msg.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'columns': "|".join(self.columns),
                'labels': "|".join(self.labels),
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



    def get_first_row_wdg(self):

        # read the csv file
        #self.file_path = ""

        div = DivWdg(id='csv_import_main')
        div.add_class('spt_panel')
        
        div.add( self.get_upload_wdg() )
        if not self.search_type:
            return div

        if not self.file_path:
            return div


        if not self.file_path.endswith(".csv"):
            div.add('<br/>')
            div.add( "Uploaded file [%s] is not a csv file. Refreshing in 3 seconds. . ."% os.path.basename(self.file_path))
            div.add_behavior( {'type': 'load', \
                                  'cbjs_action': "setTimeout(function() {spt.panel.load('csv_import_main','%s', {}, {\
                                    'search_type_filter': '%s'});}, 3000);" %(Common.get_full_class_name(self), self.search_type) } )
            return div

        if not os.path.exists(self.file_path):
            raise TacticException("Path '%s' does not exist" % self.file_path)

        


        div.add(HtmlElement.br(3))
        option_div_top = DivWdg()
        option_div_top.add_color('color','color')
        option_div_top.add_color('background','background', -5)
        option_div_top.add_style("padding: 10px")
        option_div_top.add_border()
        option_div_top.add_style("width: auto")

        swap = SwapDisplayWdg(title="Parsing Options")
        option_div_top.add(swap)

        option_div_top.add_style("margin-right: 30px")

        self.search_type_obj = SearchType.get(self.search_type)

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
        
        # Has title is default true
        title_row_checkbox.set_default_checked()
        title_row_checkbox.set_checked()
        self.has_title = True

        title_row_checkbox.add_behavior({
            'type' : 'click_up',
            'propagate_evt': 'true',
            'cbjs_action': """
                spt.panel.refresh('preview_data', spt.api.Utility.get_input_values('csv_import_main'));
            """
        })
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
        #columns = self.search_type_obj.get_columns()
        columns = SearchType.get_columns(self.search_type)
        
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

        
        
        # need to somehow specify defaults for columns
        div.add(self.get_preview_wdg())


        return div          


    
    def get_preview_wdg(self):
        columns = self.columns
        labels = self.labels
        preview = PreviewDataWdg(file_path=self.file_path, search_type=self.search_type, columns=columns, labels=labels)
        return preview

class PreviewDataWdg(BaseRefreshWdg):

    
    def init(self):

        self.is_refresh = self.kwargs.get('is_refresh') 
        self.file_path = self.kwargs.get('file_path') 
        self.search_type = self.kwargs.get('search_type')
        self.search_type_obj = SearchType.get(self.search_type)
        web = WebContainer.get_web()
        self.encoder = web.get_form_value('encoder')

        if self.is_refresh in [True, "true"]:
            has_title = web.get_form_value("has_title")
        else:
            has_title = True
        self.has_title = has_title


        lowercase_title_checkbox = CheckboxWdg("lowercase_title")

        self.lowercase_title = lowercase_title_checkbox.is_checked()


        self.columns = web.get_form_value("columns")
        if not self.columns: 
            self.columns = self.kwargs.get("columns")
        if self.columns and isinstance(self.columns, basestring):
            self.columns = self.columns.split("|")

        self.labels = web.get_form_value("labels")
        if not self.labels: 
            self.labels = self.kwargs.get("labels")
        if self.labels and isinstance(self.labels, basestring):
            self.labels = self.labels.split("|")
 
        self.csv_column_data = {}



    def get_column_preview(self, div):
        # parse the first fow
        csv_parser = CsvParser(self.file_path)
        if self.has_title in [True, "true", "on"]:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)

        if self.lowercase_title:
            csv_parser.set_lowercase_title(True)
        if self.encoder:
            csv_parser.set_encoder(self.encoder)
        try:    
            csv_parser.parse()
        # that can be all kinds of encoding/decoding exception
        except Exception as e:
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
        if self.columns:
            columns_wdg.set_value("|".join(self.columns))

        labels_wdg = HiddenWdg("labels")
        div.add(labels_wdg)
        if self.labels:
            labels_wdg.set_value("|".join(self.labels))



        div.add( "The following is taken from the first line in the uploaded csv file.  Select the appropriate column to match." )

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
        th = table.add_header("Column Value")
        th.add_style("padding: 5px")
        th.add_class('smaller')
 
        # Matching TACTIC column or new column selection
        th = table.add_header("TACTIC Column")
        th.add_style("padding: 5px")
        th.add_class('smaller')
    
        # Settings activator 
        th = table.add_header("&nbsp;")
        th.add_style("padding: 5px")
        th.add_style('min-width: 10px')
        th.add_class('smaller')

        # set the columns and labels
        columns = self.columns
        labels = self.labels
        
        # Get columns or labels if missing
        if not columns:
            columns = SearchType.get_columns(self.search_type)
            sobj = SObjectFactory.create(self.search_type)
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

        row = csv_data[data_row]
        self.num_columns = len(row)
        hidden = HiddenWdg("num_columns", self.num_columns)
        div.add(hidden)
 
        skipped_columns = []

        column_option_message = DivWdg()
        div.add(column_option_message)
        column_option_message.add_class("spt_column_option_message")
        column_option_message.add_style("padding: 10px")
        column_option_message.add("Select <div class='fa fa-cog'></div> to edit column definition.")
         
        csv_column_data = self.csv_column_data
        
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
            
            
            tr = table.add_row()
            tr.add_class("tactic_hover")

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
                if sel_val != '' or not self.is_refresh:
                    cb.set_default_checked()

            td = table.add_cell(cb) 
            td.add_style("padding-left: 5px")


            td = table.add_cell(cell)
            td.add_style("padding: 3px")
            
            # this is an optimal max width
            td.add_style('max-width: 600px')

            # On change, refresh the panel.
            column_select.add_behavior( {
                'type': "change",
                'id': str(j),
                'cbjs_action': '''
                var values = spt.api.Utility.get_input_values('csv_import_main');
                
                //If user selected "**Widget" option, then default to Note.
                column_select_key = "column_" + bvr.id; 
                if (values[column_select_key] == "widget") {
                    values[column_select_key] = "(note)";
                } 

                spt.panel.refresh('preview_data', values );
            '''
            } )

            # Get new column or note process options
            column_data = csv_column_data.get(j)
            
            processed_title = ""
            processed_type = ""
            process_value = ""
            if column_data and self.has_title:
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
                        processed_type = self._guess_column_type(csv_data, j)
            
            
            column_select.add_empty_option("%s (New)" % processed_title)
            column_select.set_persist_on_submit()
            
            # Set options and labels
            column_options = list(columns)
            column_options.append("widget")
            column_options.append("(note)")
            label_options = list(labels)
            label_options.append("**Widget")
            label_options.append("Note")

            column_select.set_option("values", column_options)
            column_select.set_option("labels", label_options)
 
            display = column_select.get_buffer_display()
            td = table.add_cell( display )
            td.add_style("padding: 3px")

            # Secondary column options - column type or note process
            column_option_div = IconWdg(icon="FA_COG")
            td = table.add_cell( column_option_div )
            td.add_style("padding: 3px 3px 3px 10px")
            if sel_val == '(note)' or sel_val == '':
                options_form = DivWdg(id="column_options_form")
                options_form.add_style("width", "250px")
                options_form.add_style("margin-top", "10px")
                options_form.add_class("spt_form")
                
                # Inputs in form depend on note or new column
                options_form_inputs = DivWdg()
                options_form.add(options_form_inputs)
                options_form_inputs.add_style("display", "inline-block")
                
                save = ActionButtonWdg(title="OK")
                save.add_style("display", "block")
                save.add_style("width", "150px")
                save.add_style("margin", "5px auto")
                options_form.add(save)
                save.add_behavior( {
                    'type': 'click_up',
                    'id': str(j),
                    'cbjs_action': '''
                        // Transfer over inputted values for column options
                        var values = spt.api.Utility.get_input_values('csv_import_main');

                        new_name_key = 'new_column_name_' + bvr.id;
                        name_key = 'new_column_' + bvr.id;
                        if (values[new_name_key]) {
                            values[name_key] = values[new_name_key]; 
                        }
                        
                        new_type_key  = 'column_type_' + bvr.id;
                        type_key = 'column_type_' + bvr.id;  
                        if (values[new_type_key]) {
                            values[type_key] = values[new_type_key]; 
                        }

                        new_note_process_key = 'new_note_process_' + bvr.id;
                        note_process_key = 'note_process_' + bvr.id;
                        note_process = values[new_note_process_key]
                        if (values[new_note_process_key] == 'custom') {
                            custom_key = 'new_note_process_custom_' + bvr.id;
                            note_process = values[custom_key];
                        } else {
                            note_process = values[new_note_process_key];
                        }
                        
                        if (note_process) {
                            values[note_process_key] = note_process;
                        }
   
                        spt.panel.refresh('preview_data', values );
                    '''
                } )
                
                options_form.add("<br clear='all'/>")
                options_form.add("<br clear='all'/>")

                offset = {'x':10, 'y': 0}
                from tactic.ui.container import DialogWdg
                dialog = DialogWdg(offset=offset)
                dialog.add(options_form, name="content")
                dialog.set_as_activator(column_option_div)
                div.add(dialog)  
            else:
                column_option_div.add_style("display", "none")
 
            if sel_val == '(note)':
                # Context options for note column
                process = HiddenWdg("note_process_%s" % j)
                column_option_div.add( process )
                process.add_style("display", "none")
                if not process_value:
                    process_value = "publish"
                process.set_value(process_value)

                # Option form for new note column
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
                process_pipeline_input = SelectWdg("new_note_process_%s" % j)
                note_process_input_group.add(process_pipeline_input)
                
                # Get processes from pipelines, and add 'publish' and 'custom' options
                from pyasm.biz import Pipeline
                search_type_obj = SearchType.get(self.search_type)
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

                process_text_input = TextWdg("new_note_process_custom_%s" % j)
                note_process_input_group.add(process_text_input)
                process_text_input.add_class("form-control")
                process_text_input.add_class("spt_custom_process_input")
                styles = "margin: 10px; display: none; border-color: #8DA832; width: 150px"
                process_text_input.add_styles(styles)
            elif sel_val == '':
                # Name and type options for new column
                column_name = HiddenWdg("new_column_%s" % j)
                column_option_div.add( column_name )
                column_name.set_value(processed_title)
 
                column_type = HiddenWdg("column_type_%s" % j)
                column_option_div.add( column_type )
                column_type.set_value(processed_type)
                
                # Option form for new column
                column_name_group = DivWdg()
                options_form_inputs.add(column_name_group)
                column_name_group.add_class("form-group")
                column_name_group.add_style("display", "inline-block")
                column_name_group.add_style("padding", "5px")

                column_name_group.add("<label>Column name</label>") 
                column_name_input = TextWdg("new_column_name_%s" % j)
                column_name_group.add(column_name_input)
                column_name_input.add_class("form-control")
                #column_name_input.add_style("width", "150px")
                column_name_input.set_value(processed_title)

                column_type_group = DivWdg()
                options_form_inputs.add(column_type_group)
                column_type_group.add_class("form-group")
                column_type_group.add_style("display", "inline-block")
                column_type_group.add_style("padding", "5px")
                
                column_type_group.add("<label>Column type</label>")
                column_type_input = SelectWdg("column_type_%s" % j)
                column_type_group.add( column_type_input )
                column_type_input.set_option("labels", "Varchar(256)|Text|Integer|Float|Date|Boolean")
                column_type_input.set_option("values", "varchar(256)|text|integer|float|timestamp|boolean")
                column_type_input.add_class("form-control")
                #column_type_input.add_style("width", "150px")
                column_type_input.set_option("default", processed_type)

        if skipped_columns:
            div.add(SpanWdg('WARNING: Some titles are empty or there are too many data cells. Column index [%s] '\
                'are skipped.' %','.join(skipped_columns), css='warning'))
            div.add(HtmlElement.br(2))


        div.add(table)




     
    

    def get_display(self):


        web = WebContainer.get_web()

        csv_parser = CsvParser(self.file_path)
        if self.encoder:
            csv_parser.set_encoder(self.encoder)

        try:    
            csv_parser.parse()
        # that can be all kinds of encoding/decoding exception
        except Exception as e:
            widget = DivWdg()
            widget.add_style("margin: 20px")
            widget.add("<div>Error: %s</div><br/>" % str(e))
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
                note_process = web.get_form_value("note_process_%s" % i)
                if not note_process:
                    note_process = "publish"
                csv_column_data[i] = {'name': '(note)', 'process': note_process}
                columns.append('Note: %s' % note_process)
            elif column == "":
                new_column_name = web.get_form_value("new_column_%s" % i)
                if not new_column_name and self.has_title:
                    new_column_name = csv_titles[i]
                column_type = web.get_form_value("column_type_%s" % i)
                csv_column_data[i] = {'name': new_column_name, 'type': column_type}
                columns.append(new_column_name)
            else:
                csv_column_data[i] = {'name': column}
                columns.append(column)
        self.csv_column_data = csv_column_data

        # Preview data and column selection 
        widget = DivWdg(id='preview_data')
        widget.add_style('padding: 6px')
        self.set_as_panel(widget)
        widget.add(SpanWdg(), 'warning')
        widget.add(HtmlElement.br(2))
        self.get_column_preview(widget)

        response_div = DivWdg(css='spt_cmd_response')
        #response_div.add_style('color','#F0C956') 
        response_div.add_color('background','background3')
        response_div.add_color('color','color3') 
        response_div.add_style('padding: 30px')
        response_div.add_style('display: none')
        widget.add(HtmlElement.br())
        widget.add(response_div)
        widget.add(HtmlElement.br(2))

        sobject_title = self.search_type_obj.get_title()
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
        div.add("<br/>")
        
        refresh_button = ActionButtonWdg(title="Refresh")

        refresh_button.add_behavior({
            'type' : 'click_up',
            'cbjs_action': '''
            spt.panel.refresh('preview_data', spt.api.Utility.get_input_values('csv_import_main'))
            '''
        })

        refresh_button.add_style("float: left")
        div.add(refresh_button)


        entry_error_msg = CsvImportCmd.ENTRY_ERROR_MSG

        import_button = ActionButtonWdg(title="Import")
        # import_button.set_id('CsvImportButton')
        import_button.add_behavior({
            'type':'click_up', 
            'entry_error_msg': entry_error_msg,
            'top_id':'csv_import_main',
            'cbjs_action': r'''
            var src_el = bvr.src_el;

            var project = spt.Environment.get().get_project();
            var my_search_type = bvr.search_type;
            var top_id = bvr.top_id;

            values = spt.api.Utility.get_input_values(top_id);

            var server = TacticServerStub.get();
            var class_name = 'pyasm.command.CsvImportCmd';

            var response_div = src_el.getParent('.spt_panel').getElement('.spt_cmd_response');
            var csv_control = src_el.getParent('.spt_panel').getElement('.spt_csv_sample')
            
            var run_cmd;

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
                var err_message = spt.exception.handler(e);

                spt.app_busy.hide();
                
                // This function is executed when Command fails or user
                // chooses to abort after single entry fails.
                var abort = function() {
                    var response_div = document.getElement('.spt_cmd_response');
                    err_message = err_message.replace(/\\n/g,'<br/>');
                    response_div.innerHTML = 'Error: ' + err_message;
                    response_div.setStyle("display", "");
                    spt.show(csv_control);
                }

                if (err_message.startsWith(bvr.entry_error_msg)) {
                    var message_parts = err_message.match("^"+bvr.entry_error_msg+" \\[(.*)\\]:.*")
                    new_start_index = parseInt(message_parts[1]) + 1;
                    ok_fn = run_cmd;
                    cancel_fn = abort;
                    options = {ok_args: [new_start_index], okText: "Skip this entry", cancelText: "Cancel entire import"}; 
                    spt.confirm(err_message, ok_fn, cancel_fn, options);
                    return;
                } 
                
                spt.error(err_message);
                abort();
            }
            
            var run_cmd = function (start_index) {
                if (start_index) {
                    values['start_index'] = start_index; 
                }
                spt.app_busy.show("Importing Data");
                server.execute_cmd(class_name, {}, values,  {on_complete: on_complete, on_error: on_error});
                spt.hide(csv_control);
            }

            run_cmd();

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
                column_type = web.get_form_value("column_type_%s" % j)
                td = table.add_cell(cell)

                # If data does not match selected column type, then let user know.
                if column_type == 'timestamp' and not self._check_timestamp(cell):
                    td.add_style("color: red")
                elif column_type == 'boolean' and not self._check_boolean(cell):
                    td.add_style("color: red")
                elif column_type == 'integer' and not self._check_integer(cell):
                    td.add_style("color: red")
                elif column_type == 'float' and not self._check_float(cell):
                    td.add_style("color: red")
                elif column_type == 'varchar(256)' and not self._check_varchar(cell):
                    td.add_style("color: red")
                
        return widget 

    def _guess_column_type(self, csv_data, idx):
        ''' given csv data and a column idx, determine appropriate data type '''
        column_types = {}
        data_cell_list = []
        column_type = ''       
        for k, row in enumerate(csv_data):
            if k >= len(row):
                data = ''
            else:
                data = row[idx] 
            if data.strip() == '':
                continue
            
            # Use democracy to determine type
            column_type = self._check_timestamp(data)
            if not column_type:
                column_type = self._check_boolean(data)
                if not column_type:
                    column_type = self._check_integer(data)
                    if not column_type:
                        column_type = self._check_float(data)
                        if not column_type:
                            column_type = self._check_varchar(data)

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
    def _parse_date(self, dt_str):    
        from dateutil import parser
        dt = parser.parse(dt_str, default=datetime.datetime(1900, 1, 1)).date()
        dt2 = parser.parse(dt_str, default=datetime.datetime(1901, 2, 2)).date()
        if dt == dt2:
            return dt
        else:
            return None


    def _check_varchar(self, data):
        column_type = None
        if len(data) <= 256:
            column_type = 'varchar(256)'
        else:
            column_type = 'text'
       
        return column_type

    def _check_boolean(self, data):
        column_type = None
        if data in ['true', 'True', 'False', 'false', '0','1']:
            column_type = 'boolean'

        return column_type

    def _check_integer(self, data):
        column_type = None
        try:
            int(data)
            column_type = 'integer'
        except ValueError as e:
            pass
       
        return column_type

    def _check_float(self, data):
        column_type = None
        try:
            float(data)
            column_type = 'float'
        except ValueError as e:
            pass
        
        return column_type

    def _check_timestamp(self, data):
        column_type = None
        try: 
            timestamp = self._parse_date(data)
            if timestamp:
                column_type = 'timestamp'
            else:
                # if it is just some number instead of a real date or timestamp
                column_type = self._check_integer(data)
        except Exception as e:
            pass
           
        return column_type 




