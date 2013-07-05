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

__all__ = [
        'BaseFilterElementWdg',
        'SelectFilterElementWdg',
        'TextFilterElementWdg',
        'KeywordFilterElementWdg',
        'DateFilterElementWdg',
        'DateRangeFilterElementWdg',
        'LoginFilterElementWdg',
        'MultiSelectFilterElementWdg',
        'MultiFieldFilterElementWdg',
        'CompoundValueFilterElementWdg',
        'ExpressionFilterElementWdg',
        'ReplaceWithValueExpressionFilterElementWdg',
        'ButtonFilterElementWdg',
        'CheckboxFilterElementWdg'
]
import datetime
from dateutil.relativedelta import relativedelta

from pyasm.common import Common, TacticException
from pyasm.biz import Project
from pyasm.web import DivWdg, SpanWdg, Table, WebContainer
from pyasm.widget import CheckboxWdg, SelectWdg, TextWdg, HiddenWdg
from pyasm.search import Search, SearchException, SearchType

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg

from filter_data import FilterData


class BaseFilterElementWdg(BaseRefreshWdg):
    '''represents the base filter'''
    def __init__(my, **kwargs):
        my.values = {}
        my.show_title = False
        my.set_flag = False
        my.title = None
        super(BaseFilterElementWdg, my).__init__(**kwargs)

    def is_visible(my):
        return True

    def set_show_title(my, flag):
        my.show_title = flag


    def get_title_wdg(my):
        title_div = DivWdg()
        name = my.get_name()

        title = my.get_title()
        if not title:
            title = name
        title = Common.get_display_title(title)
        title_div.add("%s:" % title )
        title_div.add_style("font-weight: bold")

        return title_div


    def is_set(my):
        '''indicates whether this filter has values set that will
        oontribute to the search'''
        return my.set_flag

    def get_set_js_action(my):
        return r'''
        var top = bvr.src_el.getParent(".spt_filter_top");
        var set_icons = top.getElements(".spt_filter_set");

        for (var i = 0; i < set_icons.length; i++) {
            icon_name = set_icons[i].getAttribute("spt_element_name");
            if (icon_name == bvr.element_name) {
                var set_icon = set_icons[i];
                if (bvr.src_el.value == '') {
                    set_icon.setStyle("display", "none");
                }
                else {
                    set_icon.setStyle("display", "");
                }
                break;
            }
        }
        '''

    def set_value(my, name, value):
        my.values[name] = value

    def set_values(my, values):
        my.values = values

    def alter_search(my, search):
        pass

    def get_display(my):
        pass

    def set_title(my, title):
        my.title = title

    def get_title(my):
        return my.title





class SelectFilterElementWdg(BaseFilterElementWdg):
    
    def init(my):
        expression = my.kwargs.get("column")
        if not expression:
            return
        parts = expression.split(".")
        search_types = parts[:-1]

        my.multi_search_types = False
        if len(search_types) > 1:
            my.multi_search_types = True
        

    def is_set(my):
        value = my.values.get("value")
        if value:
            return True
        else:
            if not my.values and my.kwargs.get('default'):
                return True
            else:
                return False
        
        

    def alter_search(my, search):
        expression = my.kwargs.get("column")
        if not expression:
            return


        parts = expression.split(".")
        search_types = parts[:-1]
        column = parts[-1]
    


        value = my.values.get("value")
        #print "value: ", value
        if not value:
            default =  my.kwargs.get('default')
            if not my.values and default:
                value = default
            else:
                return

        # op should come from my.values
        op = my.values.get("op")
        if not op:
            op = '='

       

       
        # go through the hierarchy
        search2 = None
        sobjects = None
        if len(search_types) > 1:

            """
            #TODO: replace the for loop below with this @SEARCH code which should be more efficient
            search_types.reverse()
            top_search_type = search_types[0]
            search_type_str = '.'.join(search_types[1:])
            expr = '''@SEARCH(%s["%s","%s"].%s)'''%(top_search_type, column, value, search_type_str)
            search2 = Search.eval(expr)
            sobjects = search2.get_sobjects()
            if not sobjects:
                # if the trail ends, then set the null filter
                search2.set_null_filter()

            """
            search_types.reverse()
            for search_type in search_types:
                if sobjects == None:
                    search2 = Search(search_type)
                    search2.add_filter(column, value, "=")
                    sobjects = search2.get_sobjects()
                else:
                    if search_type == 'connect':
                        related_sobjects = []
                        from pyasm.biz import SObjectConnection
                        connections = SObjectConnection.get_connections(sobjects)
                        related_sobjects = SObjectConnection.get_sobjects(connections)
                        """    
                        for sobject in sobjects:
                            connections, sobjects = SObjectConnection.get_connected_sobjects(sobject)
                            related_sobjects.extend(sobjects)
                        """    
                        sobjects = related_sobjects[:]
                    else:
                        search2 = Search(search_type)
                        search2.add_relationship_filters(sobjects)
                        sobjects = search2.get_sobjects()

                if not sobjects:
                    # if the trail ends, then set the null filter and exit
                    search.set_null_filter()
                    return
                

        elif not search_types:
            if op == '!=':
                search.add_op('begin')
                search.add_filter(column, value, op)
                search.add_filter(column, None)
                search.add_op('or')
            elif op in ['~']:
                filters = [[column,'~',value]]
                search.add_op_filters(filters)
            else:
                search.add_filter(column, value, op)
            return
        else:
            search_type = search_types[0]

            # get all the sobjects at the appropriate hierarchy
            try:
                search2 = Search(search_type)
                if value:
                    if op == 'exists':
                        search.add_relationship_search_filter(search2, op=value)
                        return

                    else:
                        #search2.add_filter(column, value, op)
                        if op == '!=':
                            search2.add_op('begin')
                            search2.add_filter(column, value, op)
                            search2.add_filter(column, None)
                            search2.add_op('or')
                        elif op in ['~']:
                            filters = [[column,'~',value]]
                            search2.add_op_filters(filters)
                        else:
                            search2.add_filter(column, value, op)
                search.add_relationship_search_filter(search2, op="in")
            except SearchException, e:
                raise SearchException('[%s] in simple search definition may have syntax error. %s ' %(expression, e.__str__()))
            return

        if sobjects:
            if op == '=':
                op = 'in'
            else:
                op = 'not in'
            search.add_relationship_filters(sobjects, op=op)
        else:
            search.set_null_filter()



    def get_display(my):

        div = DivWdg()
        #div.add_style("width: 350px")

        select = SelectWdg("value")
        select.add_style("width: 150px")

        # TODO: this is needed for multiple selection, but it is ugly
        #select.set_attr("multiple", "1")
        #select.add_attr("spt_is_multiple", "true")
        # if there is a link search already, don't use default
        if my.values and my.kwargs.get('default'):
            my.kwargs.pop('default')

        select.set_options(my.kwargs)
        select.add_empty_option("-- Select --")
        name = my.get_name()

        select.add_behavior( {
            'type': 'change',
            'element_name': name,
            'cbjs_action': my.get_set_js_action()
        } )

        # this is needed so they don't cross contaminate
        # FIXME: this is probably a bug in SelectWdg
        select.set_value('')
        value = my.values.get("value")
        if value:
            select.set_value(value)

        if my.show_title:
            title_div = DivWdg()
            div.add(title_div)
            title_div.add_style("float: left")

            name = my.get_name()

            title = my.get_title()
            if not title:
                title = name
                title = Common.get_display_title(title)
            title_div.add("%s:" % title )
            title_div.add_style("width: 80px")
            title_div.add_style("font-weight: bold")
            title_div.add_style("margin-left: 15px")
            title_div.add_style("padding-top: 2px")

        op = my.kwargs.get("op")
        if op == 'exists':
            div.add("&nbsp;&nbsp;&nbsp;is&nbsp;&nbsp;&nbsp;")
        elif op == '~':
            div.add("&nbsp;&nbsp;&nbsp;contains&nbsp;&nbsp;&nbsp;")
        else:
            op_select = SelectWdg("op")
            # only support in or not in for multi stypes column
            if my.multi_search_types:
                op_select.set_option("labels", "is|is not")
                op_select.set_option("values", "=|!=")
            else:
                op_select.set_option("labels", "is|is not|contains")
                op_select.set_option("values", "=|!=|~")

            value = my.values.get("op")
            if value:
                op_select.set_value(value)

            div.add(op_select)
            op_select.add_style("float: left")
            op_select.add_style("margin-right: 3px")

        div.add(select)

        # TEST Dynamic loading of select widget
        # Disabling: delay is too long.
        """
        parent_div = DivWdg()
        div.add(parent_div)

        select = SelectWdg("value")
        parent_div.add(select)
        select.add_style("width: 150")
        select.add_color("background", "background")

        value = my.values.get("value")
        if value:
            select.set_option("values", [value])
            select.set_value(value)

        select.add_empty_option("-- Select --")

        select.add_behavior( {
            'type': 'mouseover',
            'kwargs': my.kwargs,
            'cbjs_action': '''
            var top = bvr.src_el.getParent();
            var class_name = 'tactic.ui.filter.ReplaceSelectWdg';
            spt.panel.load( top, class_name, bvr.kwargs);
            '''
        } )
        """

        return div

class TextFilterElementWdg(SelectFilterElementWdg):
    ''' derives from SelectFilterElementWdg but with a text box'''
    def get_display(my):
        div = DivWdg()

        text = TextWdg("value")
        if not my.kwargs.get('column'):
            text.set_attr('readonly','readonly')
            text.set_value('Warning: column option not defined')
            text.add_class('disabled')

        
        text.add_style("width: 170px")

        # if there is a link search already, don't use default
        if my.values and my.kwargs.get('default'):
            my.kwargs.pop('default')

        text.set_options(my.kwargs)
        name = my.get_name()

        text.add_behavior( {
            'type': 'blur',
            'element_name': name,
            'cbjs_action': my.get_set_js_action()
        } )

        text.add_behavior( {
        'type': 'keyup',
        'cbjs_action': '''
        var key = evt.key;
        if (key == 'enter') {
            spt.dg_table.search_cbk( {}, {src_el: bvr.src_el} );
        }
        ''' } )

        value = my.values.get("value")
        if value:
            select.set_value(value)

        if my.show_title:
            title_div = DivWdg()
            div.add(title_div)
            title_div.add_style("float: left")

            name = my.get_name()

            title = my.get_title()
            if not title:
                title = name
                # only do this filtering to the name
                title = Common.get_display_title(title)
            title_div.add("%s:" % title )
            title_div.add_style("width: 80px")
            title_div.add_style("font-weight: bold")
            title_div.add_style("margin-left: 15px")
            title_div.add_style("padding-top: 2px")

        op = my.kwargs.get("op")
        if op == 'exists':
            div.add("&nbsp;&nbsp;&nbsp;is&nbsp;&nbsp;&nbsp;")
        elif op == '~':
            div.add("&nbsp;&nbsp;&nbsp;contains&nbsp;&nbsp;&nbsp;")
        else:
            op_select = SelectWdg("op")
            op_select.set_option("labels", "is|is not|contains")
            op_select.set_option("values", "=|!=|~")

            value = my.values.get("op")
            if value:
                op_select.set_value(value)

            op_select.add_style("margin-right: 3px")
            op_select.add_style("float: left")
            div.add(op_select)

        

        
        div.add(text)
        return div


__all__.append("ReplaceSelectWdg")
class ReplaceSelectWdg(BaseRefreshWdg):
    def get_display(my):

        select = SelectWdg("value")
        select.add_style("width: 150px")

        # TODO: this is needed for multiple selection, but it is ugly
        #select.set_attr("multiple", "1")
        #select.add_attr("spt_is_multiple", "true")
        # if there is a link search already, don't use default
        #if my.values and my.kwargs.get('default'):
        #    my.kwargs.pop('default')

        select.set_options(my.kwargs)
        select.add_empty_option("-- Select --")

        """
        select.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.focus();
            '''
        } )
        """


        select.add_behavior( {
            'type': 'change',
            'cbjs_action': my.get_set_js_action()
        } )

        # this is needed so they don't cross contaminate
        # FIXME: this is probably a bug in SelectWdg
        select.set_value('')
        #value = my.values.get("value")
        #if value:
        #    select.set_value(value)

        return select




class KeywordFilterElementWdg(BaseFilterElementWdg):


    def init(my):

        my.search_type = ''
        my.columns = []
        my.mode = my.get_option("mode")
        my.relevant = my.get_option("relevant")
        my.cross_db = my.get_option("cross_db") =='true'
        column = my.get_option("column")
        if column:
            my.columns = column.split('|')
        

        if not my.mode:
            my.mode = "global"

        # TODO: this is dependent on the default database and not
        # on the database that may actually be searched on
        from pyasm.search import Sql
        database_type = Sql.get_default_database_type()

        has_index = False
        if database_type == 'PostgreSQL':

            database_version = Sql.get_default_database_version()
            major = database_version[0]
            minor = database_version[1]

            if major >= 9:
                has_index = True
            elif major < 8:
                has_index = False
            else:
                if minor >= 4:
                    has_index = True
                else:
                    has_index = False

        my.has_index = has_index
      


    def alter_search(my, search):

        overall_search = search
        search = Search(overall_search.get_search_type())

        value = my.values.get("value")
        if not value:
            return

        name = my.get_name()
        if not my.columns:
            my.columns = [name]
        search_type = search.get_search_type()

        partial = my.values.get("partial") == 'on'

        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            is_ascii = False
        else:
            is_ascii = True

        # keywords in a list is treated with AND in full-text search
        # which is usually preferred in global search
        keywords = value.split(" ")
      

        if search_type == 'sthpw/sobject_list':
            column = "keywords"
            project_code = Project.get_project_code()
            overall_search.add_filter("project_code", project_code)
            if my.has_index and is_ascii:
                if partial:
                    overall_search.add_op("begin")
                    overall_search.add_text_search_filter(column, keywords)
                    overall_search.add_keyword_filter(column, keywords)
                    overall_search.add_op("or")
                else:
                    overall_search.add_text_search_filter(column, keywords)

            else:
                overall_search.add_keyword_filter(column, keywords)
               

        # this is the default when the xml is just <element name='keywords'/>
        elif my.mode == 'global':
            column = "keywords"

            search2 = Search("sthpw/sobject_list")

            project_code = Project.get_project_code()
            search2.add_filter("project_code", project_code)
            search2.add_filter("search_type", search_type)
            if my.has_index and is_ascii:
                if partial:
                    search2.add_op("begin")
                    search2.add_text_search_filter(column, keywords)
                    search2.add_keyword_filter(column, keywords)
                    search2.add_op("or")
                else:
                    search2.add_text_search_filter(column, keywords)

            else:
                search2.add_keyword_filter(column, keywords)

            refs = search2.get_sobjects()
            overall_search.add_filters("id", [x.get_value("search_id") for x in refs])


        elif my.mode == 'keyword':
            if my.cross_db:
                sub_search_list = []

            else:
                overall_search.add_op('begin')
                #search.add_op('begin')


            for column in my.columns:
                if my.cross_db:
                    search2 = None
                    sub_search = None
                if my.has_index and is_ascii:
                    
                    value = value.replace(",", " ")
                    keywords = value.split(" ")

                    search_type_obj = SearchType.get(search_type)
                    table = search_type_obj.get_table()

                    #print "column: ", column
                    search = Search(overall_search.get_search_type())
                    if column.find(".") != -1:
                        parts = column.split(".")
                        search_types = parts[:-1]
                        column = parts[-1]

                        if my.cross_db:
                            search_types.reverse()
                            top_search_type = search_types[0]
                            search_type_str = '.'.join(search_types[1:])
                            if search_type_str:
                                expr = '''@SEARCH(%s)'''%(search_type_str)
                                sub_search = Search.eval(expr)
                            search2 = Search(top_search_type)
                            table = SearchType.get(top_search_type).get_table()
                        else:
                            prev_stype = search_type
                            for next_stype in search_types:
                                path = None
                                # support for path
                                if ':' in next_stype:
                                    path, next_stype = next_stype.split(':')
                                search.add_join(next_stype, prev_stype, path=path)
                                prev_stype = next_stype
                            table = SearchType.get(next_stype).get_table()

                    
                    if partial:
                        if my.cross_db:
                            search2.add_op("begin")
                            search2.add_text_search_filter(column, keywords, table=table)
                            search2.add_keyword_filter(column, keywords, table=table)
                            search2.add_op("or")

                            if sub_search:
                                sub_search.add_relationship_search_filter(search2, op="in")
                            else:
                                sub_search = search2

                        else:
                            search.add_op("begin")
                            search.add_text_search_filter(column, keywords, table=table)
                            search.add_keyword_filter(column, keywords, table=table)
                            search.add_op("or")
                            overall_search.add_relationship_search_filter(search, op="in")
                    else:
                        if my.cross_db:
                            if not search2:
                                raise TacticException('If cross_db is set to true, all the columns should be formatted in expression-like format with one or more sTypes: sthpw/task.description')
                            search2.add_text_search_filter(column, keywords, table=table)
                            if sub_search:
                                sub_search.add_relationship_search_filter(search2, op="in")
                            else:
                                sub_search = search2
                        else:
                            search.add_text_search_filter(column, keywords, table=table)
                            overall_search.add_relationship_search_filter(search, op="in")
                else:
                    value = value.replace(",", " ")
                    keywords = value.split(" ")
                    search_type_obj = overall_search.get_search_type_obj() 
                    table = search_type_obj.get_table()
                    column_type = None
                    search = Search(overall_search.get_search_type())
                    if column.find(".") != -1:
                        parts = column.split(".")
                        search_types = parts[:-1]
                        column = parts[-1]

                        if my.cross_db:
                            search_types.reverse()
                            top_search_type = search_types[0]
                            search_type_str = '.'.join(search_types[1:])
                            if search_type_str:
                                expr = '''@SEARCH(%s)'''%(search_type_str)
                                sub_search = Search.eval(expr)
                            search2 = Search(top_search_type)
                            table = SearchType.get(top_search_type).get_table()
                            column_types = SearchType.get_column_types(top_search_type)
                            column_type = column_types.get(column) 
                        else:

                            prev_stype = search_type
                            for next_stype in search_types:
                                path = None
                                # support for path
                                if ':' in next_stype:
                                    path, next_stype = next_stype.split(':')
                                search.add_join(next_stype, prev_stype, path=path)
                                prev_stype = next_stype
                            table = SearchType.get(next_stype).get_table()
                            column_types = SearchType.get_column_types(next_stype)
                            column_type = column_types.get(column)
                    if my.cross_db:
                        search2.add_keyword_filter(column, keywords, table=table, column_type=column_type)
                        # sub_search is not present if it only traverses thru 1 sType
                        if sub_search:
                            sub_search.add_relationship_search_filter(search2, op="in")
                        else:
                            sub_search = search2
                    else:
                        search.add_keyword_filter(column, keywords, table=table, column_type=column_type)
                        overall_search.add_relationship_search_filter(search, op="in")
                if my.cross_db:
                    sub_search_list.append(sub_search)

            #if not my.cross_db:
            #    search.add_op('or')
            my.search_type = search.get_search_type()


            if my.cross_db:
                rtn_history = False
                overall_search.add_op('begin')
                for sub_search in sub_search_list:
                    rtn = overall_search.add_relationship_search_filter(sub_search, op="in", delay_null=True)
                    if rtn_history == False:
                        rtn_history = rtn
                # if all the sub_search return false, set null filter
                if not rtn_history:
                    overall_search.set_null_filter()
                overall_search.add_op('or')

            else:
                overall_search.add_op('or')

        else:
            raise TacticException('Mode [%s] in keyword search not support' % my.mode)

        #print "overall: ", overall_search.get_statement()


    def get_display(my):
        # can predefine a filter_search_type for the look ahead search
        my.filter_search_type = my.get_option("filter_search_type")

        div = DivWdg()
        #div.add_style("width: 360px")
        #div.add_style("height: 35px")
        #div.add_style("padding-top: 15px")
        #div.add_style("padding-left: 25px")

        if my.show_title:
            name = my.get_name()

            title = my.get_title()
            if title == None:
                title = name
            title = Common.get_display_title(title)

            #title_div = DivWdg()
            #div.add(title_div)
            #title_div.add("%s: " % title )
            #title_div.add_style("float: left")
            if title:
                div.add("<b>%s: &nbsp;</b>" % title )


        #text = TextWdg("value")
        #text = TextInputWdg(name="value")

        custom_cbk = {
            'enter': '''
            spt.dg_table.search_cbk( {}, {src_el: bvr.src_el} );
            '''
        }



        if my.show_title:
            title_div = DivWdg()

            div.add(title_div)
            title_div.add_style("float: left")

            name = my.get_name()

            title = my.get_title()
            if not title:
                title = name
            title = Common.get_display_title(title)
            title_div.add("%s:" % title )
            title_div.add_style("width: 80px")
            title_div.add_style("font-weight: bold")
            title_div.add_style("margin-left: 15px")
            title_div.add_style("padding-top: 2px")


       
        column = None
        hint_text = 'any keywords'
        search_type = 'sthpw/sobject_list'


       

        if not my.columns:
            my.columns = [my.get_name()]

     


        elif my.mode == 'keyword':
            search_type = my.filter_search_type

            # clean up the hint text and find the last search_type
            hints = []
            for column in my.columns:
                if column.find(".") != -1:
                    parts = column.split(".")
                    hint = parts[-1]
                    #NOTE: no need to determine sType
                    #tmp_search_type = parts[-2]
                   
                else:
                    hint = column
                hints.append(hint)

            hint_text = ', '.join(hints)



            if len(hint_text) > 30:
                hint_text = '%s...'%hint_text[0:29]


        if my.kwargs.get("hint_text"):
            hint_text = my.kwargs.get("hint_text")

        # search_type is a list matching the column for potential join
        text = LookAheadTextInputWdg(
                name="value",
                custom_cbk=custom_cbk,
                filter_search_type=my.filter_search_type,
                relevant = my.relevant,
                search_type=search_type,
                column=my.columns,
                width ='230',
                hint_text=hint_text
        )

        value = my.values.get("value")
        if value:
            text.set_value(value)
        div.add(text)


        text.add_behavior( {
        'type': 'keyup',
        'cbjs_action': '''
        var key = evt.key;
        if (key == 'enter') {
            spt.dg_table.search_cbk( {}, {src_el: bvr.src_el} );
        }
        ''' } )

        #text.add_behavior( {
        #    'type': 'change',
        #    'cbjs_action': my.get_set_js_action()
        #} )


        if my.mode == 'keyword' and my.has_index:
            checkbox = CheckboxWdg("partial")
            checkbox.add_attr("title", "Use partial word match (slower)")
            div.add(checkbox)
        elif my.mode =='global' and my.has_index:
            checkbox = CheckboxWdg("partial")
            checkbox.add_attr("title", "Use partial word match (slower)")
            checkbox.set_default_checked()
            div.add(checkbox)
            
        else:
            # partial is implied otherwise
            hidden = HiddenWdg("partial")
            div.add(hidden)
            hidden.set_value("on")



        return div



class DateFilterElementWdg(BaseFilterElementWdg):
    '''This filter uses a subselect so that it can look for dates that
    are on another table than the main serach'''
    def alter_search(my, search):

        expression = my.kwargs.get("column")
        if not expression:
            return
        
        search_types = []

        if expression.find(".") != -1:
            #search_type, date_col = expression.split(".")
            parts = expression.split(".")
            search_types = parts[:-1]
            if search_types:
                search_type = '.'.join(search_types)
            date_col = parts[-1]
        else:
            search_type = search.get_search_type()
            date_col = expression

        start_date = my.values.get("start_date")
        end_date = my.values.get("end_date")
        if not start_date and not end_date:
            return



        
        from pyasm.search import Search

        # use the expression only if 1 or more search_types defined in column
        if search_types:
            expr = "@SEARCH(%s)"%search_type
            search2 = Search.eval(expr)
        else:
            search2 = Search(search_type)

        search2.add_date_range_filter(date_col, start_date, end_date)

        
        search.add_relationship_search_filter(search2)




    def get_display(my):

        div = DivWdg()

        table = Table()
        div.add(table)
        table.add_row()

        if my.show_title:
            title_div = DivWdg()

            table.add_cell(title_div)

            name = my.get_name()

            title = my.get_title()
            if not title:
                title = name
            title = Common.get_display_title(title)
            title_div.add("%s:" % title )
            title_div.add_style("width: 80px")
            title_div.add_style("font-weight: bold")
            title_div.add_style("margin-left: 15px")
            title_div.add_style("padding-top: 2px")

        td = table.add_cell()
        op = DivWdg("is")
        td.add(op)
        td = table.add_cell()
        op = DivWdg("between&nbsp;&nbsp;&nbsp;")
        td.add(op)

        from tactic.ui.widget import CalendarInputWdg
        td = table.add_cell()
        cal1 = CalendarInputWdg("start_date")
        td.add(cal1)

        td = table.add_cell()
        spacing = DivWdg("&nbsp;and&nbsp;")
        td.add(spacing)

        td = table.add_cell()
        cal2 = CalendarInputWdg("end_date")
        td.add(cal2)

        return div




class DateRangeFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        start_col = my.kwargs.get("start_date_col")
        end_col = my.kwargs.get("end_date_col")



        name = my.get_name()
        if not start_col:
            start_col = "%s_start_date" % name
        if not end_col:
            end_col = "%s_end_date" % name

        # find a relative search type if needed
        parts = start_col.split(".")
        search_types = parts[:-1]
        start_col = parts[-1]

        # find a relative search type if needed
        parts = end_col.split(".")
        search_types2 = parts[:-1]
        end_col = parts[-1]

        if search_types != search_types2:
            raise SearchException('Search types for start and end column must match')


        # just take the first one
        if search_types:
            #search_type = search_types[0]
            search_type = '.'.join(search_types)
        else:
            search_type = search.get_search_type()


        start_date = my.values.get("start_date")
        end_date = my.values.get("end_date")

        if not start_date and not end_date:
            return


        operator = my.get_option("op")
        if operator != 'not in':
            operator = 'in'

        from pyasm.search import Search
    
        # use the expression only if 1 or more search_types defined in column
        if search_types:
            expr = "@SEARCH(%s)"%search_type
            search2 = Search.eval(expr)
        else:
            search2 = Search(search_type)


        search2.add_dates_overlap_filter(start_col, end_col, start_date, end_date, op="in")
        search.add_relationship_search_filter(search2, op=operator)

        return

        # Add in the ability to do something like ...
        #select * from sequence where code not in (select distinct sequence_code from shot);
        relationship = None
        if relationship == 'search_type':
            where = '''id not in (select distinct search_id from task where search_type like 'prod/asset?project=%')'''
        else:
            where = '''id not in (select distinct sequence_code from shot)'''

        #search.add_empty_related_filter("sthpw/task", op='not in')





    def get_display(my):

        div = DivWdg()

        name = my.get_name()

        title = Common.get_display_title(name)

        operator = my.get_option("op")
        if operator != 'not in':
            operator = 'in'

        table = Table()
        div.add(table)
        table.add_row()
        table.add_color("color", "color")

        name_div = DivWdg()
        #name_div.add("%s " % title)
        table.add_cell(name_div)

        #div.add_style("border: solid blue 1px")
        if operator == 'in':
            op = DivWdg("overlap ")
        else:
            op = DivWdg("does not overlap ")
        table.add_cell(op)

        from tactic.ui.widget import CalendarInputWdg
        cal1 = CalendarInputWdg("start_date")
        table.add_cell(cal1)

        start_date = my.values.get("start_date")
        if start_date:
            cal1.set_value(start_date)
 
        table.add_cell(" and ")

        cal2 = CalendarInputWdg("end_date")
        table.add_cell(cal2)

        end_date = my.values.get("end_date")
        if end_date:
            cal2.set_value(end_date)

        return div



class ExpressionFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        prefix = my.values.get("prefix")
        #column = my.values.get("%s_column" % prefix)




        option = my.values.get("option")
        if option == 'my_items':
            expr = my.get_option("expression")
            column = my.get_option("column")


            from pyasm.biz import ExpressionParser
            parser = ExpressionParser()
            value = my.values.get("value")
            if results:
                search.add_filters(column, results)
            else:
                search.add_filter(column, 'NULL')

        elif option == 'all_items':
            pass
       

    def get_display(my):

        title = my.get_option("title")
        if not title:
            title = my.get_option("expression")

        div = SpanWdg()
        div.add("%s: " % title)
        checkbox = CheckboxWdg("option")
        checkbox.set_attr("value", "my_items")
        checkbox.set_checked()
        div.add(checkbox)
        div.add("&nbsp;&nbsp;")
        div.add("All")
        checkbox = CheckboxWdg("option")
        checkbox.set_attr("value", "all_items")
        div.add(checkbox)

        return div



# --------------------------------------------------------------------------------------------------------------------
# ReplaceWithValueExpressionFilterElementWdg ...
#
#     This is really just the ExpressionFilterElementWdg but with the ability to have a text field entry
#     for a value to replace within your expression. Where-ever you place $REPLACE in your expression string
#     will be replaced with the value you enter in the text field entry. Below is some example configuration
#     XML for this widget ...
#
#     <element name='has_subtask_with_lead'> 
#       <display class='tactic.ui.filter.ReplaceWithValueExpressionFilterElementWdg'>
#         <expression>@GET(MMS/subtask['lead_name','$REPLACE'].job_id)</expression>
#         <column>id</column>
#         <field_size>22</field_size>
#         <field_label>matching:</field_label>
#       </display>
#     </element>
#
class ReplaceWithValueExpressionFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        expr = my.get_option("expression")
        column = my.get_option("column")

        field_value = my.values.get("field")

        from pyasm.biz import ExpressionParser
        parser = ExpressionParser()
        if field_value:
            results = parser.eval(expr, vars={
                "REPLACE": field_value,
                "VALUE": field_value
            })

            if results:
                search.add_filters(column, results)
            else:
                search.set_null_filter()


    def get_display(my):
        # mode "text" uses a textbox to search, while "select" uses a select dropdown.
        mode = my.get_option("mode")
        if not mode:
            mode = "text"
        if mode not in ["select", "text"]:
            class_name = my.__class__.__name__
            raise TacticException("%s mode option can only be 'select' or 'text'." %class_name)

        field_size = my.get_option("field_size")
        #if not field_size:
        #    field_size = "32"
        #else:
        #    field_size = "%s" % field_size
        
        div = SpanWdg()

        if mode == "text":
            kwargs = {
                "name": "field",
                "search_type": my.get_option("search_type"),
                "column": my.get_option("display_column"),
                "value_column": my.get_option("value_column"),
            }
            if my.get_option("search_type"):
                text = LookAheadTextInputWdg(**kwargs)
                text.set_name("field")
            else:
                text = TextInputWdg(name="field")
    
            if field_size:
                text.add_attr("size", field_size)
            div.add(text)

            text.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            var key = evt.key;
            if (key == 'enter') {
                spt.dg_table.search_cbk( {}, {src_el: bvr.src_el} );
            }
            ''' } )

        elif mode == "select":
            values = my.get_option("select_values")
            labels = my.get_option("select_labels")
            select = SelectWdg("field")
            select.add_style("width: 120px")

            select.add_empty_option("-- Select --")
            select.set_option("values", values)
            select.set_option("labels", labels)
            div.add(select)
    
        mod_value = my.get_option('last_modified_days')
        if mod_value:
            select = SelectWdg("last_modified", label='modified in: ')
            #select.add_style("width: 10px")
            if mod_value =='true':
                mod_value = '10|20|30|60|90'
            mod_values = mod_value.split('|')
            mod_values = [x.strip() for x in mod_values]
            mod_labels = ["last %s Days"%x for x in mod_values] 
            select.add_empty_option("-- Select --")
            select.set_option("values", mod_values)
            select.set_option("labels", mod_labels)
            div.add(select)
            
            
        return div


__all__.append("TaskConnectFilterElementWdg")
class TaskConnectFilterElementWdg(ReplaceWithValueExpressionFilterElementWdg):
    def alter_search(my, search):
        field_value = my.values.get("field")
        last_mod_value = None

        last_mod_option = my.get_option("last_modified_days")
        if last_mod_option:
            last_mod_value = my.values.get('last_modified')

        search_type = my.get_option("search_type")
        if search_type:
            search_type = Project.get_full_search_type(search_type)

        # This controls what to filter at the end other than id
        filter_column = my.get_option("filter_column")

        do_search = my.get_option("do_search")
        if not field_value:
            if do_search =='true':
                pass
            else:
                return
        column = my.get_option("column")
        assert column

        search2 = Search("sthpw/connection")

        select = search2.get_select()
        from_table = "connection"
        to_table = "task"
        from_col = "src_search_id"
        to_col = "id"
        select.add_join(from_table, to_table, from_col, to_col, join="INNER")
    
        prefix = "src_"
        prefix2 = "dst_"
        search2.add_filter("%ssearch_type" % prefix, "sthpw/task")
        # one can supply a search type for searching in the connection table
        if not search_type:
            search_type = search.get_search_type()
        search2.add_filter("%ssearch_type" % prefix2, search_type)

        search2.add_column("%ssearch_id" % prefix2)


        # use field value
        if field_value:
            search2.add_filter(column, field_value, table="task")

        filters = my.get_option("filters")
        if filters:
            search2.add_op_filters(filters)
        

        if last_mod_value:
            last_mod_value = int(last_mod_value)
            today = datetime.datetime.today()
            date =  today + relativedelta(days=-last_mod_value)
            setting = "%Y-%m-%d"
            date_value = date.strftime(setting)
            search2.add_where( "task.id in (SELECT search_id from status_log where timestamp  > '%s')"%date_value )

        statement = search2.get_statement()
        sql = search2.get_sql()
        values = sql.do_query(statement)
        values = [x[0] for x in values]

        if not filter_column:
            filter_column = 'id'
        search.add_filters(filter_column, values)






class LoginFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        prefix = my.values.get("prefix")
        column = my.values.get("%s_column" % prefix)

        option = my.values.get("option")
        if option == 'my_items':
            search.add_user_filter()
        elif option == 'all_items':
            pass
       

    def get_display(my):

        # FIXME
        title = "Jobs"

        div = SpanWdg()
        div.add("My %s: " % title)
        checkbox = CheckboxWdg("option")
        checkbox.set_attr("value", "my_items")
        checkbox.set_checked()
        div.add(checkbox)
        div.add("&nbsp;&nbsp;")
        div.add("All User %s: " % title)
        checkbox = CheckboxWdg("option")
        checkbox.set_attr("value", "all_items")
        div.add(checkbox)
        return div



#
# FIXME: hardcoded for MMS
#
class MultiSelectFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        filters = ['MMS/job.job_number_prefix', 'MMS/job.job_number_year', 'MMS/job.job_number']
        for filter in filters:
            value = my.values.get(filter)
            if value:
                #search.add_relationship_filter(filter)
                search_type, column = filter.split('.')
                search.add_filter(column, value)



    def get_display(my):

        top = SpanWdg()
        top.add("&nbsp; matches &nbsp;")

        filters = ['MMS/job.job_number_prefix', 'MMS/job.job_number_year', 'MMS/job.job_number']

        for filter in filters:
            text = TextWdg(filter)
            text.add_attr("size", "5")
            top.add(text)
            top.add("&nbsp;-&nbsp;")

        return top



# This is a generalized version of the MultiSelectFilterElementWdg
#
class MultiFieldFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        field_list_option = my.get_option("field_list")
        if not field_list_option:
            return

        stmt = 'field_info_list = %s' % field_list_option.replace("\n"," ")
        try:
            exec stmt
        except:
            return

        for field_info in field_info_list:

            field = field_info.get('field')
            op = field_info.get('op')
            if not op:
                op = '='

            if field:
                value = my.values.get(field)
                to = field_info.get('to')
                if to:
                    if to.endswith('()'):
                        stmt = 'value = value.%s' % to
                    else:
                        # assume casting to other value besides string ...
                        stmt = 'value = %s(value)' % to
                    try:
                        exec stmt
                    except:
                        # TODO ... proper error message here?
                        continue
                if value:
                    # print "field is [%s] ... op is [%s] ... to is [%s] ... value is [%s]" % (field, op, to, value)
                    search.add_filter(field, value, op)


    def set_configuration_error(my, top_el, error_message):

        top_el.add("Error in Configuration -- %s" % error_message)
        top_el.add_styles("color: orange; font-style: italic; font-weight: bold;")


    def get_display(my):

        top = SpanWdg()

        field_list_option = my.get_option("field_list")
        if not field_list_option:
            my.set_configuration_error( top, "No 'field_list' option provided" )
            return top

        top.add("&nbsp; matches &nbsp;")
        stmt = 'field_info_list = %s' % field_list_option.replace("\n"," ")
        try:
            exec stmt
        except:
            my.set_configuration_error( top, "badly formed 'field_list' option" )
            return top

        # field_list option should look like this:
        #     [ {'field': 'job_number_prefix', 'size': '1', 'maxlength': '1', 'label': 'Prefix', 'to': 'upper()' },
        #       {'field': 'job_number_year', 'size': '2', 'maxlength': '2', 'label': 'Year (2 digits)', 'to': 'int' },
        #       {'field': 'job_number', 'size': '5', 'maxlength': '5', 'label': 'Number', 'to': 'int' },
        #     ]
        #
        # ... you can also specify a specific op in each of the above ... defaults to 'op': '='

        default_size = 10

        done_first = False
        for field_info in field_info_list:
            field = field_info.get('field')
            if field:
                text = TextWdg(field)
                size = field_info.get('size')
                if not size:
                    size = default_size

                text.add_attr("size", "%s" % size)
                maxlength = field_info.get('maxlength')
                if maxlength:
                    text.add_attr("maxlength", "%s" % maxlength)

                label = field_info.get('label')
                if label:
                    if done_first:
                        top.add("&nbsp;&nbsp;&nbsp;%s: " % label)
                    else:
                        top.add("%s: " % label)
                top.add(text)

                done_first = True

        return top


# --------------------------------------------------------------------------------------------------------------------
# CompoundValueFilterElemenetWdg ...
#
#     This is used to set up multiple text field entries to build a single value up to compare to a specific
#     column ... example is for MMS job number. Below is some example configuration XML for this widget ...
#
# <display class='tactic.ui.filter.CompoundValueFilterElementWdg'>
#     <field_list> [
#         { 'field': 'job_number_prefix', 'label': 'Prefix', 'size': '1', 'maxlength': '1', 'to': 'upper()' },
#         { 'field': 'job_number_year', 'label': 'Year (2 digit)', 'size': '2', 'maxlength': '2', 'to': 'zfill(2)' },
#         { 'field': 'job_number', 'label': 'Number', 'size': '5', 'maxlength': '5', 'to': 'zfill(5)' }
#     ] </field_list>
#     <column>job_number_full</column>
#     <compound_value_expr>{job_number_prefix}{job_number_year}-{job_number}</compound_value_expr>
#     <op>=</op>
# </display> 
#
class CompoundValueFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        field_list_option = my.get_option("field_list")
        if not field_list_option:
            return

        stmt = 'field_info_list = %s' % field_list_option.replace("\n"," ")
        try:
            exec stmt
        except:
            return

        column = my.get_option("column")
        if not column:
            print
            print
            print "*** ERROR: no column specified for CompoundValueFilterElementWdg"
            print
            print
            return

        field_map = {}

        for field_info in field_info_list:

            field = field_info.get('field')
            if field:
                value = my.values.get(field)
                to = field_info.get('to')
                if to:
                    if to.endswith(')'):
                        stmt = 'value = value.%s' % to
                    else:
                        # assume casting to other value besides string ...
                        stmt = 'value = %s(value)' % to
                    try:
                        exec stmt
                    except:
                        # TODO ... proper error message here?
                        continue
                if value:
                    field_map[field] = value

        compound_value = my.get_option("compound_value_expr")
        if not compound_value:
            return

        for f,v in field_map.iteritems():
            compound_value = compound_value.replace( "{%s}" % f, v )

        op = my.get_option("op")
        if not op:
            op = "="

        search.add_filter( column, compound_value, op)


    def set_configuration_error(my, top_el, error_message):

        top_el.add("Error in Configuration -- %s" % error_message)
        top_el.add_styles("color: orange; font-style: italic; font-weight: bold;")


    def get_display(my):

        top = SpanWdg()

        field_list_option = my.get_option("field_list")
        if not field_list_option:
            my.set_configuration_error( top, "No 'field_list' option provided" )
            return top

        top.add("&nbsp; matches")
        stmt = 'field_info_list = %s' % field_list_option.replace("\n"," ")
        try:
            exec stmt
        except:
            my.set_configuration_error( top, "badly formed 'field_list' option" )
            return top

        # field_list option should look like this:
        #     [ {'field': 'job_number_prefix', 'size': '1', 'maxlength': '1', 'label': 'Prefix', 'to': 'upper()' },
        #       {'field': 'job_number_year', 'size': '2', 'maxlength': '2', 'label': 'Year (2 digits)', 'to': 'int' },
        #       {'field': 'job_number', 'size': '5', 'maxlength': '5', 'label': 'Number', 'to': 'int' },
        #     ]

        default_size = 10

        for field_info in field_info_list:
            field = field_info.get('field')
            if field:
                text = TextWdg(field)
                size = field_info.get('size')
                if not size:
                    size = default_size

                text.add_attr("size", "%s" % size)
                maxlength = field_info.get('maxlength')
                if maxlength:
                    text.add_attr("maxlength", "%s" % maxlength)

                label = field_info.get('label')
                if label:
                    top.add("&nbsp;&nbsp;&nbsp;%s: " % label)

                top.add(text)

        return top



class CheckboxFilterElementWdg(BaseFilterElementWdg):

    def alter_search(my, search):

        keys = []
        for key, value in my.values.items():
            if not key.startswith("button"):
                continue
            if value != "on":
                continue

            keys.append(key)

        #if not keys:
        #    search.set_null_filter()


        search.add_op("begin")
        for key in keys:
            button = my.values.get("button_%s" % key)

            option = key.replace("button_", "")

            expression = my.get_option(option)
            if expression:
                sobjects = Search.eval(expression)
                ids = [x.get_id() for x in sobjects]

                search.add_filters("id", ids)

        search.add_op("or")


    def get_display(my):

        from tactic.ui.widget import ActionButtonWdg

        top = my.top

        mode = 'checkbox'

        
        titles = my.get_option("options")
        actual_titles = []

        if titles:
            titles = titles.split("|")
            
            actual_titles = my.get_option("titles")
            if actual_titles:
                actual_titles = actual_titles.split("|")
                if len(actual_titles) != len(titles):
                    raise TacticException('titles count have to match the options count in the Checkbox Filter Element in Simple Search.')
            else:
                actual_titles = titles[:]
        else:
            titles = []

        table = Table()
        table.add_color("color", "color")
        top.add(table)
        table.add_row()

        if mode == 'button':
            text = HiddenWdg("button")
            top.add(text)
            text.add_class("spt_text")


            for title in titles:
                button = ActionButtonWdg(title=title)
                table.add_cell(button)


                button.add_behavior( {
                'type': 'click_up',
                'title': title,
                'cbjs_action': my.get_set_js_action()
                } )

        else:

            for i, title in enumerate(titles):
                td = table.add_cell()

                if i != 0:
                    div = DivWdg()
                    div.add_style("float: left")
                    td.add(div)
                    div.add_style("height: 30px")
                    #div.add("&nbsp;")
                    div.add_style("border-style: solid")
                    div.add_style("border-width: 0 1 0 0")
                    div.add_style("margin-right: 15px")
                    div.add_style("border-color: %s" % div.get_color("border"))



                button_title = "button_%s" % title
                checkbox = CheckboxWdg(button_title)
                td.add(checkbox)
                actual_title = actual_titles[i]
                td.add(actual_title)

                if my.values.get(button_title):
                    checkbox.set_checked()
            

        return top



class ButtonFilterElementWdg(CheckboxFilterElementWdg):
    pass



