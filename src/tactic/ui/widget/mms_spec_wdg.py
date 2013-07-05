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
__all__ = ["MMSSpecWdg","MMSDuplicateJobCmd","MMSCompanyObjectiveSearchWdg"]

import datetime

from pyasm.common import TacticException, Date, Container, Environment
from pyasm.command import Command
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer, Table
from pyasm.search import SearchType, Search, SearchKey
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg, TextWdg, SelectWdg, CheckboxWdg, HiddenWdg

from tactic.ui.common import BaseRefreshWdg


class MMSSpecWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'parent_key': 'the parent of the specification'
        }


    def get_display(my): 

        top = DivWdg()

        parent_key = my.kwargs.get("parent_key")
        if not parent_key:
            top.add("No parent key found")
            return top


        if my.kwargs.get("is_refresh") == 'true':
            cmd = MMSSpecCmd(parent_key=parent_key)
            Command.execute_cmd(cmd)

        top.add_class("spt_spec_top")
        my.set_as_panel(top)

        web = WebContainer.get_web()


        parent = SearchKey.get_by_search_key(parent_key)
        discipline = Search.eval("@SOBJECT(MMS/subtask_product.MMS/product_type.MMS/discipline)", parent, single=False)

        if not discipline:
            top.add("No discipline defined for this subtask")
            return top
            



        # get all of the keys
        spec_keys = Search.eval("@SOBJECT(MMS/specification_key)", discipline, list=True, single=False)

        if not spec_keys:
            top.add("No Specification Keys found for this discipline")
            return top

 
        # add cthe commit buttons
        commit_button = my.get_commit_button()
        top.add( commit_button )




        # display it in a select
        spec_select = SelectWdg("spec_key")
        spec_select.set_sobjects_for_options(spec_keys, "id", "specification_key")
        spec_select.set_persistence()
        spec_select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
                var top = bvr.src_el.getParent('.spt_spec_top');
                spt.panel.refresh(top)'''
        } )
        top.add(spec_select)

        try:
            spec_key_id = int(spec_select.get_value())
        except:
            spec_key_id = None

        if spec_key_id not in [x.get_id() for x in spec_keys]:
            spec_key = spec_keys[0]
        elif spec_key_id:
            spec_key = Search.get_by_id("MMS/specification_key", spec_key_id)
        elif spec_keys:
            spec_key = spec_keys[0]
        else:
            return top



        # get all of the groupings in the key
        spec_groups = spec_key.get_related_sobjects("MMS/specification_grouping")
        # get all of the subtask_specs and break up according to detail
        subtask_spec_info = {}
        subtask_specs = parent.get_related_sobjects("MMS/subtask_specification")
        for subtask_spec in subtask_specs:
            id = subtask_spec.get_value("specification_detail_id")
            subtask_spec_info[id] = subtask_spec


        # list out all of the sobjects
        for spec_group in spec_groups:
            spec_group_div = DivWdg()
            spec_group_div.add_class("maq_search_bar")

            spec_group_name = spec_group.get_value("group_name")
            spec_group_div.add(spec_group_name)

            # get all of the spec details
            spec_details = spec_group.get_related_sobjects("MMS/specification_detail")

            table = Table()
            table.add_style("width: 100%")
            for i, spec_detail in enumerate(spec_details):
                if i == 0 or i % 2 == 0:
                    table.add_row()

                # get the previous value
                id = spec_detail.get_id()
                subtask_spec = subtask_spec_info.get(id)
                if subtask_spec:
                    value = subtask_spec.get_value("value")
                else:
                    value = None


                td = table.add_cell( my.get_spec_detail_wdg(spec_detail, value) )
                td.add_style("padding-right: 10px")

                td.add_style("width: 50%")
                td.add_style("padding: 3px")

            top.add(spec_group_div)
            top.add(table)

        if not spec_groups:
            spec_group_div = DivWdg()
            spec_group_div.add_style("margin: 20px")
            spec_group_div.add_style("text-align: center")
            spec_group_div.add("No specifications defined for this selection")

            top.add(spec_group_div)


        return top


    def get_commit_button(my):

        from tactic.ui.widget import TextBtnSetWdg
        commit_label = 'Commit'
        buttons_list = []
        buttons_list.append( {'label': commit_label, 'tip': 'Commit Changes' })
                          

        commit_add_btns = TextBtnSetWdg( float="right", buttons=buttons_list,
                                         spacing=6, size='small', side_padding=4 )
        commit_btn_top_el = commit_add_btns.get_btn_top_el_by_label(commit_label)
        commit_btn_top_el.add_class("spt_table_commit_btn")
        #commit_btn_top_el.add_styles("display: none;")

        #commit_btn_top_el.add_behavior( {'type': 'show',
        #         'cbjs_action': 'spt.widget.btn_wdg.set_btn_width( bvr.src_el );'} );

        commit_btn_top_el.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
                var top = bvr.src_el.getParent('.spt_spec_top');
                var server = TacticServerStub.get();
                spt.panel.refresh(top);'''
        } )

        return commit_add_btns


    

    def get_spec_detail_wdg(my, spec_detail, value):
        spec_detail_div = DivWdg()
        name = spec_detail.get_value('name')
        id = spec_detail.get_id()


        data_type = spec_detail.get_value("data_type")
        if data_type == 'string':
            input_wdg = TextWdg(id)
        elif data_type == 'int':
            input_wdg = TextWdg(id)
        elif data_type == 'boolean':
            input_wdg = CheckboxWdg(id)
        else:
            input_wdg = TextWdg(id)

        if value:
            input_wdg.set_value(value)

        input_wdg.add_style("float: right")
        spec_detail_div.add(input_wdg)

        spec_detail_div.add("%s: " % name)

        #print name, data_type

        return spec_detail_div


        
class MMSSpecCmd(Command):
    def execute(my):
        print "MMSSpecCmd"

        parent_key = my.kwargs.get("parent_key")
        assert parent_key
        subtask = SearchKey.get_by_search_key(parent_key)
        subtask_id = subtask.get_id()

        # find all of the specifications that current exist
        expr = '''@SOBJECT(MMS/subtask_specification['subtask_id','%s'])''' % subtask_id
        specs = Search.eval(expr)

        web = WebContainer.get_web()
        keys = web.get_form_keys()

        # get all of the spec details.
        search = Search("MMS/specification_detail")

        # HACK: remove
        keys.remove("spec_key")

        search.add_filters("id", keys)
        spec_details = search.get_sobjects()

        for key in keys:
            value = web.get_form_value(key)
            key = int(key)

            # first see if the specification already exists
            spec = None
            for existing_spec in specs:
                if existing_spec.get_value("specification_detail_id") == key:
                    spec = existing_spec
                    break
                    
            if not spec:
                spec = SearchType.create("MMS/subtask_specification")
                spec.set_value("specification_detail_id", key)
                spec.set_value("subtask_id", subtask_id)

            spec.set_value("value", value)
            spec.commit()




class MMSDuplicateJobCmd(Command):

    def is_api_executable(my):
        return True


    def get_title(my):
        return "Duplicate Job"


    def execute(my):

        search_key = my.kwargs.get("search_key")
        job = SearchKey.get_by_search_key(search_key)
        if not job:
            raise TacticException("Job [%s] does not exist" % search_key)

        # print "Cloning Job with search key [%s] ..." % search_key

        # don't duplicate related_type of 'MMS/subtask', as we'll clone the subtasks individually in order
        # to clone each subtask's related types easily (subtask has more related types) ...
        related_types = ['MMS/job_labor']
        job_clone = job.clone(related_types=related_types)

        job_id = job.get_id()

        # renumber job number
        job_number_prefix = job.get_value('job_number_prefix')

        # get all of the highest job with this prefix
        search = Search("MMS/job")
        search.add_filter("job_number_prefix", job_number_prefix)
        search.add_order_by("job_number desc")
        last_job = search.get_sobject()
        if not last_job:
            new_job_number = 1
        else:
            new_job_number = last_job.get_value("job_number") + 1

        # need current job year for 'job_number_year' field ...
        import datetime
        today = datetime.datetime.now()
        new_job_year_str = str(today.year)[2:]

        print "new: ", new_job_number
        job_clone.set_value("job_number", new_job_number)

        # FIXME: Do we override the job year with current year?
        job_clone.set_value("job_number_year", int(new_job_year_str))

        # be sure to set cached 'job_number_full' value ...
        job_clone.set_value("job_number_full", "%s%s-%s" %
                            (job_number_prefix, new_job_year_str, str(new_job_number).zfill(5)))

        job_clone.set_value("current_job_status", "In Work")
        job_clone.set_value("logic_bar_code_number", "")  # this should be null ... check to see if this makes it null

        # TODO: need to set logged in user as job's supervisor

        job_clone.commit()

        new_job_id = job_clone.get_id()

        # -- now run through and process subtasks ...

        # get all subtasks of source job and clone them for the new job ...
        search = Search("MMS/subtask")
        search.add_filter("job_id", job_id)
        search.add_order_by("subtask_letter asc")
        subtasks = search.get_sobjects()

        for stask in subtasks:
            stask_related_types = [ 'MMS/subtask_product', 'MMS/subtask_specification', 'MMS/subtask_material',
                                    'MMS/subtask_material_aggrgt', 'MMS/subtask_pieces', 'MMS/subtask_pieces_aggrgt',
                                    'MMS/subtask_vendor', 'MMS/subtask_vndrcost_aggrgt' ]

            stask_clone = stask.clone(related_types=stask_related_types)
            stask_clone.set_value("current_subtask_status", "In Work")
            stask_clone.set_value("job_id", new_job_id)

            stask_clone.commit()


        # TODO: Duplication of a Job does NOT trigger a create job event, so generation of LOGIC XML
        #       output for duplicated job must occur here ... for now just repeat the code in the
        #       create job trigger (see 701MMS, 'job_created_trigger', custom script)

        from mms import MMSJobActivity
        job_activity = MMSJobActivity( job_id=new_job_id )

        audit_comment = 'Job CREATED on DUPLICATION of Job number %s' % job.get_value("job_number_full")
        job_activity.create_job_audit_log_entry( audit_comment )
        job_activity.generate_new_job_xml()

        my.description = "Duplicated Job with search key [%s]" % search_key





from tactic.ui.common import BaseRefreshWdg
from tactic.ui.filter import FilterData
from tactic.ui.widget import CalendarInputWdg, TextBtnSetWdg

from datetime import datetime
from dateutil import parser


class MMSCompanyObjectiveSearchWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget'
        }


    def init(my):
        #my.handle_search()
        pass

    def handle_search(my):
        search_type = my.kwargs.get("search_type")
        my.search = Search(search_type)
        my.alter_search(my.search)
        return my.search

    def get_search(my):
        return my.search


    def alter_search(my, search):

        filter_data = FilterData.get()
        values = filter_data.get_values_by_index("week", 0)

        date_string = values.get("start_calendar")
        if date_string:
            start_date = parser.parse(date_string)
        else:
            start_date = None

        date_string = values.get("end_calendar")
        if date_string:
            end_date = parser.parse(date_string)
        else:
            end_date = None

        objective = values.get('objective')

        if objective:
            search.add_filter('company_objective_id', objective)


        column = 'actual_completion_date'
        search.add_date_range_filter(column, start_date, end_date)


        
    def get_display(my):

        date = Date()
        date_string = date.get_db_date()

        my.prefix = 'week'
        top = DivWdg()
        top.add_class("spt_table_search")

        from tactic.ui.container import RoundedCornerDivWdg
        inner = RoundedCornerDivWdg(corner_size=10, hex_color_code='949494')
        inner.set_dimensions(width_str="100%", content_height_str='100%', height_str="100%")
        inner.add_style("margin: 20px")
        top.add(inner)


        hidden = HiddenWdg("prefix", my.prefix)
        top.add(hidden)


        table = Table()
        table.add_style("color: black")
        table.add_style("width: 800px")
        table.add_row()
        inner.add(table)

        td = table.add_cell("Company Objective: <br/>")
        select = SelectWdg('objective')
        select.set_option('query', 'MMS/company_objective|id|objective')
        select.set_option('empty', '-- Select --')
        table.add_cell( select )

 
        table.add_cell("After Date: <br/>")
        calendar = CalendarInputWdg('start_calendar')
        table.add_cell( calendar )

        table.add_cell("Before Date: <br/>")
        calendar = CalendarInputWdg('end_calendar')
        table.add_cell( calendar )

        #table.add_cell( my.get_search_wdg() )
        inner.add( HtmlElement.br(1) )
        inner.add( my.get_search_wdg() )

        return top



    def get_search_wdg(my):
        filter_div = DivWdg()

        buttons_list = [
                {'label': 'Run Search', 'tip': 'Run search with this criteria' },
                {'label': 'Clear', 'tip': 'Clear all search criteria',
                    'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        ]

        txt_btn_set = TextBtnSetWdg( position='', buttons=buttons_list, spacing=6, size='small', side_padding=4 )
        run_search_bvr = {
            'type':         'click_up',
            'cbfn_action':  'spt.dg_table.search_cbk',
            'panel_id':     my.prefix
        }
        txt_btn_set.get_btn_by_label('Run Search').add_behavior( run_search_bvr )

        filter_div.add( txt_btn_set )
        return filter_div



__all__.append("MMSMetricsReportSearchWdg")
class MMSMetricsReportSearchWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget'
        }


    def init(my):
        #my.handle_search()
        pass

    def handle_search(my):
        search_type = my.kwargs.get("search_type")
        my.search = Search(search_type)
        my.alter_search(my.search)
        return my.search

    def get_search(my):
        return my.search


    def alter_search(my, search):

        filter_data = FilterData.get()
        values = filter_data.get_values_by_index("metrics", 0)

        start_date = values.get("start_calendar")
        end_date = values.get("end_calendar")
        search.add_date_range_filter("actual_completion_date", start_date, end_date)

        jobs = values.get('jobs')


        supervisor = values.get('supervisor')
        if supervisor:
            select = search.get_select()
            select.add_join("job_labor")
            select.add_filter("title", "Supervisor")
            select.add_filter("assigned_company_srvcs_user_id", supervisor)
            print select.get_statement()


        # only show closed jobs
        my.search_type = my.kwargs.get("search_type")
        if my.search_type == "MMS/job":
            search.add_filters("current_job_status",['Closed'])
        else:
            search.add_filters("current_subtask_status",['Closed'])



        
    def get_display(my):

        date = Date()
        date_string = date.get_db_date()

        my.prefix = 'metrics'
        top = DivWdg()
        top.add_class("spt_table_search")

        from tactic.ui.container import RoundedCornerDivWdg
        inner = RoundedCornerDivWdg(corner_size=10, hex_color_code='949494')
        inner.set_dimensions(width_str="95%", content_height_str='95%', height_str="100%")
        inner.add_style("margin: 20px")
        top.add(inner)


        hidden = HiddenWdg("prefix", my.prefix)
        top.add(hidden)


        table = Table()
        table.add_style("color: black")
        table.add_style("width: 800px")
        table.add_row()
        inner.add(table)


        td = table.add_cell("Jobs: <br/>")

        # NOTE: hard code this default
        security = Environment.get_security()
        if (security.is_in_group("supervisor") or 
                security.is_in_group("senior_manager") ):
            select = SelectWdg('jobs')
            select.set_option('values', "My Jobs|All Jobs")
            select.set_value("All Jobs")
        #elif security.is_in_group("media_products_services"):
        else:
            select = TextWdg('jobs')
            select.set_option("read_only", "true")
            select.set_value("My Jobs")

        table.add_cell( select )

 

        td = table.add_cell("Supervisor: <br/>")
        select = SelectWdg('supervisor')
        select.set_option('values_expr', "@GET(sthpw/login_group['login_group','supervisor'].sthpw/login_in_group.sthpw/login.login)")
        select.set_option('empty', '-- Select --')
        table.add_cell( select )

 
        table.add_cell("After Date: <br/>")
        calendar = CalendarInputWdg('start_calendar')
        table.add_cell( calendar )

        table.add_cell("Before Date: <br/>")
        calendar = CalendarInputWdg('end_calendar')
        table.add_cell( calendar )

        #table.add_cell( my.get_search_wdg() )
        inner.add( HtmlElement.br(1) )
        inner.add( my.get_search_wdg() )

        return top



    def get_search_wdg(my):
        filter_div = DivWdg()

        buttons_list = [
                {'label': 'Run Search', 'tip': 'Run search with this criteria' },
                {'label': 'Clear', 'tip': 'Clear all search criteria',
                    'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        ]

        txt_btn_set = TextBtnSetWdg( position='', buttons=buttons_list, spacing=6, size='small', side_padding=4 )
        run_search_bvr = {
            'type':         'click_up',
            'cbfn_action':  'spt.dg_table.search_cbk',
            'panel_id':     my.prefix
        }
        txt_btn_set.get_btn_by_label('Run Search').add_behavior( run_search_bvr )

        filter_div.add( txt_btn_set )
        return filter_div



__all__.extend(["MMSDCISearchWdg", "MMSDCIReportTaskElementWdg", "MMSDCIReportMonthElementWdg"])
from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg

class MMSDCISearchWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget'
        }


    def init(my):
        #my.handle_search()
        pass

    def handle_search(my):
        search_type = my.kwargs.get("search_type")
        my.search = Search(search_type)
        my.alter_search(my.search)
        return my.search

    def get_search(my):
        return my.search


    def alter_search(my, search):

        filter_data = FilterData.get()
        values = filter_data.get_values_by_index("DCI", 0)

        year_string = values.get("year")
        Container.put("DCI:year", year_string)

        supervisor = values.get('supervisor')
        employee = values.get('employee')

        security = Environment.get_security()
        if security.is_in_group("media_products_services"):
            login = Environment.get_security().get_user_name()
            search.add_filter("login", login)
        elif employee != 'My Report':
            if supervisor:
                # find the supervisor's employees
                employees = Search.eval("@GET(MMS/group_supervisor['supervisor_login_id','%s'].sthpw/login.login)" % supervisor)

                if employees:
                    search.add_filters("login", employees)
                else:
                    search.set_null_filter()
            #else:
            #    search.set_null_filter()
        else:
            employee = values.get("employee")
            login = Environment.get_security().get_user_name()
            search.add_filter("login", login)
        
    def get_display(my):

        date = Date()
        date_string = date.get_db_date()

        my.prefix = 'DCI'
        top = DivWdg()
        top.add_class("spt_table_search")

        from tactic.ui.container import RoundedCornerDivWdg
        inner = RoundedCornerDivWdg(corner_size=10, hex_color_code='949494')
        inner.set_dimensions(width_str="95%", content_height_str='95%', height_str="100%")
        inner.add_style("margin: 20px")
        top.add(inner)


        hidden = HiddenWdg("prefix", my.prefix)
        top.add(hidden)


        table = Table()
        table.add_style("color: black")
        table.add_style("width: 600px")
        table.add_row()
        inner.add(table)

        td = table.add_cell("Year: <br/>")
        year_wdg = TextWdg('year')
        year_wdg.set_attr("size", "5")
        today = datetime.today()
        year = today.year
        year_wdg.set_value(year)
        table.add_cell( year_wdg )


        security = Environment.get_security()
        if security.is_in_group("media_products_services"):
            td = table.add_cell("Employee: My Report<br/>")
        else:
            td = table.add_cell("Supervisor: <br/>")
            supervisor_wdg = SelectWdg('supervisor')
            supervisor_wdg.add_empty_option("-- Select --")
            supervisor_wdg.set_option("values_expr", "@GET(sthpw/login_in_group['login_group','supervisor'].sthpw/login.login)")
            table.add_cell( supervisor_wdg )

            td = table.add_cell("Employee: <br/>")
            employee_wdg = SelectWdg('employee')
            employee_wdg.set_option("values", "My Report|All Employees")
            employee_wdg.set_option("default", "All Employees")
            table.add_cell( employee_wdg )


 
 

 
        #table.add_cell( my.get_search_wdg() )
        inner.add( HtmlElement.br(1) )
        inner.add( my.get_search_wdg() )

        return top



    def get_search_wdg(my):
        filter_div = DivWdg()

        buttons_list = [
                {'label': 'Run Search', 'tip': 'Run search with this criteria' },
                {'label': 'Clear', 'tip': 'Clear all search criteria',
                    'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        ]

        txt_btn_set = TextBtnSetWdg( position='', buttons=buttons_list, spacing=6, size='small', side_padding=4 )
        run_search_bvr = {
            'type':         'click_up',
            'cbfn_action':  'spt.dg_table.search_cbk',
            'panel_id':     my.prefix
        }
        txt_btn_set.get_btn_by_label('Run Search').add_behavior( run_search_bvr )

        filter_div.add( txt_btn_set )
        return filter_div






class MMSDCIReportTaskElementWdg(BaseTableElementWdg):

    def init(my):
        my.labor_types = Search.eval("@GET(MMS/discipline['dci','yes'].MMS/labor_type.labor_type)")


    def get_display(my):
        top = DivWdg()

        #labor_types = ['ADM','HW/SW','MTG','TRNG','DIRECT','NO WK']
        labor_types = my.labor_types
        for i, labor_type in enumerate(labor_types):
            labor_div = DivWdg()
            labor_div.add("%d: %s" % (i+1,labor_type))
            labor_div.add_style("padding: 2px 4px")
            top.add(labor_div)

        top.add("<hr style='size: 0'/>")
        top.add("Summary")

        return top


from dateutil import parser
from datetime import datetime

class MMSDCIReportMonthElementWdg(BaseTableElementWdg):

    def init(my):
        my.labor_types = Search.eval("@SOBJECT(MMS/discipline['dci','yes'].MMS/labor_type)")


    def preprocess(my):

        my.aggrgt_dict = Container.get("MMSDCIReport::aggrgt")
        my.aggrgt_year_dict = Container.get("MMSDCIReport::aggrgt_year")

        if my.aggrgt_dict == None:
            my.aggrgt_year_dict = {}

            # find all the dci aggregates for this user
            search = Search("MMS/dci_aggrgt")
            aggrgts = search.get_sobjects()

            my.aggrgt_dict = {}
            for aggrgt in aggrgts:
                a_login = aggrgt.get_value("login")
                a_labor_type_id = aggrgt.get_value("labor_type_id")
                a_month_date = aggrgt.get_value("month_date")

                key = "%s|%s|%s" % (a_login, a_labor_type_id, a_month_date)
                my.aggrgt_dict[key] = aggrgt

                # calculate the total
                a_month_datetime = parser.parse(a_month_date)
                year = a_month_datetime.year
                key = "%s|%s|%s" % (a_login, a_labor_type_id, year)

                total = my.aggrgt_year_dict.get(key)
                if not total:
                    total = 0
                total += aggrgt.get_value("total_hours")

                my.aggrgt_year_dict[key] = total


            Container.put("MMSDCIReport::aggrgt", my.aggrgt_dict)
            Container.put("MMSDCIReport::aggrgt_year", my.aggrgt_year_dict)



    def get_display(my):
        top = DivWdg()

        #labor_types = ['ADM','HW/SW','MTG','TRNG','DIRECT','NO WK']
        labor_types = my.labor_types

        sobject = my.get_current_sobject()
        login = sobject.get_value("login")

        year = Container.get("DCI:year")
        if not year:
            today = datetime.today()
            year = today.year

        month = my.get_name()
        if month != "total":
            month_date_str = "%s 1, %s" % (month, year)
            month_date = parser.parse(month_date_str)
            month_date_str = month_date.strftime("%Y-%m-%d")
            month_date_str = "%s 00:00:00" % month_date_str


        import random
        total = 0
        for i, labor_type in enumerate(labor_types):

            labor_type_id = labor_type.get_id()

            labor_div = DivWdg()
            if month != 'total':
                key = "%s|%s|%s" % (login, labor_type_id, month_date_str)
                aggrgt = my.aggrgt_dict.get(key)
                if not aggrgt:
                    hours = 0.0
                    labor_div.add("&nbsp;")
                else:
                    hours = aggrgt.get_value("total_hours")
                    labor_div.add("%0.1f" % hours)
            else:
                key = "%s|%s|%s" % (login, labor_type_id, year)
                hours = my.aggrgt_year_dict.get(key)
                if hours:
                    labor_div.add("%0.1f" % hours)
                else:
                    hours = 0.0
                    labor_div.add("&nbsp;")

            labor_div.add_style("text-align: right")
            labor_div.add_style("padding: 2px 4px")
            top.add(labor_div)
            total += hours

        top.add("<hr style='size: 0'/>")
        total_div = DivWdg()
        total_div.add_style("text-align: right")
        total_div.add("%0.1f" % total)
        total_div.add_style("padding: 2px 4px")
        top.add(total_div)

        return top

