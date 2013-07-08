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


__all__ = ["CsvImportWdg"]

import csv, os

from pyasm.web import Widget, DivWdg, Table, SpanWdg
from pyasm.search import Search, SearchType, SObjectFactory
from pyasm.biz import CsvParser
from pyasm.web import Widget, HtmlElement, WebContainer, AjaxCmd
from pyasm.widget import SelectWdg, SimpleUploadWdg, IconSubmitWdg, IconButtonWdg, IconWdg, HiddenWdg, TextWdg, HintWdg, CheckboxWdg, SiteMenuWdg, ProgressWdg, FilterCheckboxWdg, TextAreaWdg

from pyasm.command import FileUpload
from pyasm.prod.web import SearchTypeSelectWdg
from tactic.ui.common import BaseRefreshWdg

class CsvImportWdg(BaseRefreshWdg):

    def get_display(my):
        widget = Widget()
        widget.add( my.get_first_row_wdg() )
        widget.add(ProgressWdg())
        return widget




    def get_upload_wdg(my):
        widget = Widget()

        # get the search type
        widget.add( "1. Select type of asset: ")

        # handle new search_types
        new_search_type = CheckboxWdg("new_search_type_checkbox")
        new_search_type.add_event("onclick", "toggle_display('new_search_type_div')")
        #span = SpanWdg(css="med")
        #span.add(new_search_type)
        #span.add("Create new type")
        #span.add(" ... or ... ")
        #widget.add(span)

        new_search_type_div = DivWdg()
        new_search_type_div.set_id("new_search_type_div")

        name_input = TextWdg("asset_name")
        title = TextWdg("asset_title")
        description = TextAreaWdg("asset_description")

        table = Table()
        table.add_style("margin: 10px 20px")
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


        # or use a pre-existing one
        search_type_select = SearchTypeSelectWdg("filter|search_type")
        search_type_select.add_empty_option("-- Select --")
        search_type_select.set_persist_on_submit()
        search_type_select.set_submit_onchange()
        widget.add(search_type_select)
        

        my.search_type = search_type_select.get_value()
        if my.search_type:
            sobj = SObjectFactory.create(my.search_type)
            required_columns = sobj.get_required_columns()
            
            widget.add(SpanWdg("Required Columns: ", css='med'))
            if not required_columns:
                required_columns = ['n/a']
            widget.add(SpanWdg(', '.join(required_columns), css='med'))

        widget.add( HtmlElement.br(2) )
        widget.add( "2. Upload a csv file: ")
        upload_wdg = HtmlElement.upload("uploaded_file")
        widget.add(upload_wdg)
        submit = IconSubmitWdg("Upload", IconWdg.UPLOAD, True)
        widget.add(submit)

        web = WebContainer.get_web()
        field_storage = web.get_form_value("uploaded_file")
        if field_storage != "":
            upload = FileUpload()
            upload.set_field_storage(field_storage)
            upload.set_create_icon(False)
            upload.execute()

            files = upload.get_files()
            if files:
                my.file_path = files[0]
            else:
                my.file_path = web.get_form_value("file_path")


        if my.file_path:
            hidden = HiddenWdg("file_path", my.file_path)
            widget.add(hidden)

        return widget



    def get_first_row_wdg(my):

        # read the csv file
        my.file_path = ""

        div = DivWdg()

        div.add( my.get_upload_wdg() )

        if not my.search_type:
            return div

        if not my.file_path:
            return div


        if not my.file_path.endswith(".csv"):
            div.add( "Uploaded file [%s] is not a csv file"% my.file_path)
            return div

        if not os.path.exists(my.file_path):
            raise Exception("Path '%s' does not exists" % my.file_path)

        div.add(HtmlElement.br(2))

        div.add( HtmlElement.b("The following is taken from first line in the uploaded csv file.  Select the appropriate column to match.") )
        div.add(HtmlElement.br())
        div.add(  HtmlElement.b("Make sure you have all the required columns** in the csv."))
        option_div = DivWdg()
        
        option_div.add_style("float: left")
        option_div.add_style("margin-right: 30px")

        option_div.add("<p>3. Parsing Options:</p>")

        my.search_type_obj = SearchType.get(my.search_type)


        # first row and second row
        option_div.add( HtmlElement.br(2) )
        option_div.add("Use Title Row: ")
        title_row_checkbox = FilterCheckboxWdg("has_title")
        title_row_checkbox.set_default_checked()
        option_div.add(title_row_checkbox)
        option_div.add( HintWdg("Set this to use the first row as a title row to match up columns in the database") )
        
        option_div.add( HtmlElement.br(2) )
        option_div.add("Sample Data Row: ")
        data_row_text = TextWdg("data_row")
        data_row_text.set_attr("size", "3")
        option_div.add(data_row_text)
        option_div.add( HintWdg("Set this as a sample data row to match the columns to the database") )

        option_div.add( HtmlElement.br(2) )
        
       
        div.add(option_div)
        my.has_title = title_row_checkbox.is_checked()
        
        
        # parse the first fow
        csv_parser = CsvParser(my.file_path)
        if my.has_title:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)
        csv_parser.parse()
        csv_titles = csv_parser.get_titles()
        csv_data = csv_parser.get_data()



        data_row = data_row_text.get_value()
        if not data_row:
            data_row = 0
        else:
            try:
                data_row = int(data_row)
            except ValueError:
                data_row = 0

            if data_row >= len(csv_data):
                data_row = len(csv_data)-1
        data_row_text.set_value(data_row)




        table = Table()
        table.set_attr("cellpadding", "10")

        table.add_row()
        table.add_header("CSV Column Value")
        table.add_header("TACTIC Column")
        table.add_header("Create New Column")
        
        columns = my.search_type_obj.get_columns()
        search_type = my.search_type_obj.get_base_search_type()
        sobj = SObjectFactory.create(search_type)
        required_columns = sobj.get_required_columns()
        
        row = csv_data[data_row]
        labels = []
        for column in columns:
            if column in required_columns:
                label = '%s**'%column
            else:
                label = column
            labels.append(label)

        for j, cell in enumerate(row):
            table.add_row()
            table.add_cell(cell)

            column_select = SelectWdg("column_%s" % j)
            column_select.add_event("onchange", "if (this.value!='') {set_display_off('new_column_div_%s')} else {set_display_on('new_column_div_%s')}" % (j,j))

            column_select.add_empty_option("-- Select --")
            column_select.set_option("values", columns)
            column_select.set_option("labels", labels)

            # only set the value if it is actually in there
            if csv_titles[j] in columns:
                column_select.set_option("default", csv_titles[j])
            column_select.set_persist_on_submit()
            column_select_value = column_select.get_value()


            display = column_select.get_buffer_display()
            td = table.add_cell( display )

            if csv_titles[j] not in columns:
                td.add(" <b style='color: red'>*</b>")

                # new property
                new_column_div = DivWdg()

                if column_select_value:
                    new_column_div.add_style("display", "none")
                else:
                    new_column_div.add_style("display", "block")

                new_column_div.set_id("new_column_div_%s" % j)

                td = table.add_cell( new_column_div )
                text = TextWdg("new_column_%s" % j)
                text.set_persist_on_submit()

                if my.has_title:
                    text.set_value(csv_titles[j])


                new_column_div.add( " ... or ..." )
                new_column_div.add( text )


        my.num_columns = len(row)
        hidden = HiddenWdg("num_columns", my.num_columns)


        # need to somehow specify defaults for columns


        div.add(table)

        div.add("<br/><br/>")


        div.add(my.get_preview_wdg())


        return div          
                    

    def get_preview_wdg(my):

        widget = Widget()

        web = WebContainer.get_web()

        csv_parser = CsvParser(my.file_path)
        csv_parser.parse()
        csv_titles = csv_parser.get_titles()
        csv_data = csv_parser.get_data()



        ajax = AjaxCmd()
        ajax.set_option("search_type", my.search_type)
        ajax.set_option("file_path", my.file_path)
        ajax.add_element_name("has_title")

        event = WebContainer.get_event_container()
        caller = event.get_event_caller(SiteMenuWdg.EVENT_ID)
        div = ajax.generate_div()
        div.set_post_ajax_script(caller)
        widget.add(div)

        columns = []
        num_columns = len(csv_titles)
        ajax.set_option("num_columns", num_columns)
        for i in range(0, num_columns):
            column = web.get_form_value("column_%s" % i)
            if column:
                column = csv_titles[i]
            else:
                column = web.get_form_value("column_new_%s" % i)

            columns.append(column)

            ajax.add_element_name("column_%s" % i)
            ajax.add_element_name("new_column_%s" % i)


        ajax.register_cmd("pyasm.command.csv_import_cmd.CsvImportCmd")
        import_button = IconButtonWdg("Import", IconWdg.REFRESH, True)
        import_button.add_event("onclick", ajax.get_on_script(show_progress=False))
        import_button.add_style("float: right")
        widget.add( import_button )


        preview_submit = IconSubmitWdg("Preview", IconWdg.REFRESH, True)
        preview_submit.add_style("float: right")
        widget.add(preview_submit)

        sobject_title = my.search_type_obj.get_title()
        widget.add("<p>4. Import</p>")
        widget.add(HtmlElement.br())
        widget.add("<p>The following table will be imported into %s (Showing Max: 100)</p>" % sobject_title)


        table = Table(css="table")
        table.add_style("width: 100%")

        table.add_row()
        for i, title in enumerate(columns):
            if not title:
                title = "<b style='color:red'>*</b>"
            table.add_header(title)

        for i, row in enumerate(csv_data):
            if i > 100:
                break
            table.add_row()
            for j, cell in enumerate(row):
                table.add_cell(cell)

        widget.add(table)

        return widget

 

