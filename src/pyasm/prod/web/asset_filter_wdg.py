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

__all__ = ['BaseSelectFilterWdg', 'AssetFilterWdg', 'TextureFilterWdg', 'CodeFilterWdg',
'ShotFilterWdg', 'EpisodeShotFilterWdg', 'EpisodeFilterWdg',
'SequenceFilterWdg', 'SequenceShotFilterWdg', 'DateFilterWdg',
'SequenceInstanceFilterWdg', 'EpisodeInstanceFilterWdg', 'BinFilterWdg',
'BinTypeFilterWdg' ,'UserFilterWdg', 'ProjectFilterWdg', 'SnapshotFilterWdg',
'SearchFilterWdg', 'ContextFilterWdg', 'ProcessFilterWdg', 
'WeekFilterWdg', 'PipelineFilterWdg', 'SearchTypeFilterWdg']



from pyasm.common import *
from pyasm.search import Search, SearchType, Sql
from pyasm.web import *
from pyasm.widget import *
from shot_navigator_wdg import *
from prod_input_wdg import *
from pyasm.biz import Project, PrefSetting
from pyasm.prod.load import ProdLoaderContext
from pyasm.prod.biz import Shot



class AssetFilterWdg(Widget):

    def init(my):
        search_columns = my.get_search_columns()
        my.text = SearchFilterWdg("text_filter", columns=search_columns,\
                has_persistence=True)
        #my.text.set_persistence()

       
        
        name = "asset_library_selection"
        my.select = FilterSelectWdg(name)
        search = Search("prod/asset_library")
        my.select.set_search_for_options( search, "code", "title" )
        my.select.add_empty_option("-- Any --")
    
        asset_library = my.select.get_value()
        WebState.get().add_state("edit|asset_library", asset_library)


        title = "Library"
        span = SpanWdg(css="med")
        span.add( my.text )
        span.add( StringWdg("%s: " % title) )
        span.add( my.select )

        my.add(span)


        """
        name = "sequence_selection"
        my.seq_select = FilterSelectWdg(name)
        seq_search = Search("prod/sequence")
        my.seq_select.set_search_for_options( seq_search, "code", "code" )
        my.seq_select.add_empty_option("-- Any --")

        title = "Sequence"
        span = SpanWdg(css="med")
        span.add( StringWdg("%s: " % title) )
        span.add( my.seq_select )
        span.add_style("margin-top: 5px")

        my.add(span)
        """



    def get_search_columns(my):
        return ['code','name','description']



    def alter_search(my, search):

        value = my.select.get_value()
        if value != "":
            search.add_filter("asset_library", value)

        """
        seq_value = my.seq_select.get_value()
        if seq_value:
            search.add_where("code in (select asset_code from sequence_instance where sequence_code = '%s')" % seq_value)
        """

        my.text.alter_search(search)

    def get_display(my):

        span = SpanWdg(css="med")
        for widget in my.widgets:
            span.add(widget)

        return span
        


class TextureFilterWdg(AssetFilterWdg):

    def init(my):

        my.asset_code_select = FilterSelectWdg("asset_code_filter", \
            label='Asset Code: ', css='small')
        search = Search("prod/asset")
        my.asset_code_select.set_search_for_options(search, "code", "code")
        my.asset_code_select.add_empty_option('-- Any --')
        my.add( my.asset_code_select )
 
        my.text = FilterTextWdg("text_filter", label='Search: ', css='small')
        my.add( my.text )

        # don't ever name the filter after a column name in an sobjeet
        my.name = "category_filter"
        my.select = FilterSelectWdg(my.name, label='Category: ', css='snall')
        my.select.set_option("setting", "texture_category")
        my.select.add_empty_option('-- Any --')
        
        my.add( my.select )



    def get_search_columns(my):
        return ['code','description']


    def alter_search(my, search):

        asset_code = my.asset_code_select.get_value()
        if asset_code != "":
            search.add_filter("asset_code", asset_code)

        value = my.select.get_value()
        if value != "":
            search.add_filter("category", value)

        value = my.text.get_value()
        if not value or value == "":
            return

        value = value.lower()
        values = value.split(" ")

        columns = my.get_search_columns()
        for value in values:
            expr = [Search.get_regex_filter(x, value) for x in columns]
            expr_full = " or ".join(expr)
            search.add_where("(%s)" % expr_full)

class CodeFilterWdg(Widget):
    '''A text based code filter '''
    def init(my):

        my.text = FilterTextWdg("code_filter", label="Code: ", css='med')
        my.add(my.text)
        my.add(HintWdg('It accepts reg. expression e.g. 12-0[0-9]+ '))

    def alter_search(my, search):

        value = my.text.get_value()
        if value:
            search.add_regex_filter("code", value)


class ShotFilterWdg(AssetFilterWdg):

    def init(my):

        #my.text = FilterTextWdg("shot_search", label='Search: ', \
        #        css='med', has_persistence=True)
        search_columns = Shot.get_search_columns()
        my.text = SearchFilterWdg("shot_search", columns=search_columns,\
                 has_persistence=True)
        my.add(my.text)


        

    def get_search_columns(my):
        return ['code','description']



    def alter_search(my, search):

        my.text.alter_search(search)
        
        '''
        value = value.lower()
        values = value.split(" ")

        columns = my.get_search_columns()
        for value in values:
            expr = [Search.get_regex_filter(x, value) for x in columns]
            expr_full = " or ".join(expr)
            search.add_where("(%s)" % expr_full)

        '''

    def get_display(my):

        
        span = SpanWdg(css="med")
        for widget in my.widgets:
            span.add(widget)
        
        #span.add(HintWdg('You can enter shot code or description'))
        return span

class BaseSelectFilterWdg(Widget):
    ''' This is a base filter other select-based filter will derive off'''
    def __init__(my, name='', **kwargs):
        my.select_name = name
        my.kwargs = kwargs
        super(BaseSelectFilterWdg, my).__init__(name)
        my.default_mode = SelectWdg.ALL_MODE
        if my.kwargs.get('mode'):
            my.default_mode = my.kwargs.get('mode')
        my.hide_empty_option = False
        my.options = {}
        my.search_column = my.get_search_column()
        my.label = '' 
        
    def init(my):
        '''add the input to be drawn here. Note: For more complex navigators
        like more than one, override init and alter_search'''
        nav = my.get_input_cls()
        if not my.select_name:
            # use the default values
            my.navigator = Common.create_from_class_path(nav)
        else:
            my.navigator = Common.create_from_class_path(nav, [my.select_name], my.kwargs)
        my.add(my.navigator) 
        
        
    def get_input_cls(my):
        return "TextWdg"
    
    def alter_search(my, search):
        value = my.navigator.get_value()
        if not value:
            return
        search.add_filter(my.search_column, value)
    
    def get_search_column(my):
        return 'code'
        
    def set_search_column(my, column):
        ''' this provides a way to set the search_column name externally'''
        my.search_column = column

    def get_display(my):
        
        span = SpanWdg()
        for widget in my.widgets:
            if my.default_mode == SelectWdg.NONE_MODE:
                widget.add_none_option()
            if my.hide_empty_option:
                widget.remove_empty_option()
            for key, value in my.options.items():
                widget.set_option(key, value)
            span.add(widget)

        return span

    def get_value(my):
        return my.navigator.get_value()
   
    def get_values(my):
        return my.navigator.get_values()
   
    def add_none_option(my):
        ''' add the --NONE-- option '''
        my.default_mode = SelectWdg.NONE_MODE

    def remove_empty_option(my):
        my.hide_empty_option = True

    def set_option(my, name, value):
        my.options[name] = value

    def get_navigator(my):
        return my.navigator

    def get_label(my):
        return my.navigator.get_label()
        
class EpisodeShotFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(my):
        return "pyasm.prod.web.EpisodeShotNavigatorWdg"

    def get_search_column(my):
        return 'shot_code' 

class EpisodeFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(my):
        return "pyasm.prod.web.EpisodeNavigatorWdg"

    def get_search_column(my):
        return 'episode_code'

class SequenceFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(my):
        return "pyasm.prod.web.SequenceNavigatorWdg"

    
    def get_search_column(my):
        return 'sequence_code'

    def alter_search(my, search):
        
        epi_code, seq_code = my.navigator.get_value()
        if epi_code and not seq_code:
            search_str = "select code from sequence where episode_code='%s'" %epi_code
            search.add_where("%s in (%s)" %(my.search_column, search_str))
        elif seq_code:
            search.add_filter(my.search_column, seq_code)

        #if epi_code:
            #search.add_filter('episode_code', epi_code)
        #foreign_key = SearchType.get(Sequence.SEARCH_TYPE).get_foreign_key()

        # TODO: this requires database introspection
        #if not search.has_column(foreign_key):
        #    return

        #search.add_filter( foreign_key, sequence_code )


class SequenceInstanceFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(my):
        return "pyasm.prod.web.SequenceNavigatorWdg"

    
    def alter_search(my, search):
        epi_code, seq_code = my.get_value()
        if not seq_code:
            return

        search.add_where("code in (select asset_code from sequence_instance where sequence_code = '%s')" % seq_code)


 
class EpisodeInstanceFilterWdg(BaseSelectFilterWdg):
    OPTION_NAME = 'use_epi_planner'

    def get_input_cls(my):
        return "pyasm.prod.web.EpisodeNavigatorWdg"

    
    def alter_search(my, search):
        epi_code = my.get_value()
        if not epi_code:
            return
        use_epi = FilterCheckboxWdg(my.OPTION_NAME)
        if use_epi.is_checked(False):
            search.add_where("code in (select asset_code from episode_instance where episode_code = '%s')" % epi_code)
        else:
            search.add_filter("episode_code", epi_code)


      



class SequenceShotFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(my):
        return "pyasm.prod.web.SequenceShotNavigatorWdg"

    def get_search_column(my):
        return 'sequence_code', 'code' 

    def alter_search(my, search):
        epi_code, seq_code, shot_code = my.navigator.get_value()
     
        if seq_code:
            search.add_filter(my.search_column[0], seq_code)
        # this is if since they are not mutually exclusive
        if shot_code:
            search.add_filter(my.search_column[1], shot_code)
        
            

class DateFilterWdg(BaseSelectFilterWdg):
    ''' A filter for finding entries from a fixed number of days/hours ago ''' 
    
    def init(my):
        super(DateFilterWdg, my).init()
        my.navigator.set_persistence()
        my.navigator.add_behavior({'type' : 'change',
            'cbjs_action': "%s; %s" \
            % (my.navigator.get_save_script(), my.navigator.get_refresh_script())})

    def get_input_cls(my):
        return "pyasm.widget.DateSelectWdg"

    def get_search_column(my):
        pass

    def set_label(my, label):
        my.navigator.set_label(label)

    def set_value(my, value):
        my.navigator.set_value(value)

    def alter_search(my, search):
        value = my.navigator.get_value()
        if not value or value == SelectWdg.NONE_MODE:
            return
        search.add_where(my.navigator.get_where(value)) 
       
class BinFilterWdg(BaseSelectFilterWdg):
    ''' a filter for Bin used for dailies submissions only'''
    def init(my):
        super(BinFilterWdg, my).init()
        my.navigator.set_persistence()
        my.navigator.set_submit_onchange()
        my.navigator.add_empty_option(label='-- Select a bin --', \
            value=SelectWdg.NONE_MODE)
        my.navigator.set_label('Bin: ')

        value = my.get_value()
        WebState.get().add_state("edit|bin_select", value)
        
    def get_input_cls(my):
        return "pyasm.prod.web.BinFilterSelectWdg"

    def get_search_column(my):
        return "bin_id"

    def alter_search(my, search):
        ''' this is not really used now '''
        value = my.navigator.get_value()
        
        if not value:
            search.add_filter(my.search_column, 'NONE')
        else:
            search.add_filter(my.search_column, value)

class BinTypeFilterWdg(BaseSelectFilterWdg):
    ''' a filter for Bin type used for dailies submissions only'''

    def get_search_column(my):
        return "type"

    def get_input_cls(my):
        return "pyasm.prod.web.BinTypeFilterSelectWdg"


        
class UserFilterWdg(BaseSelectFilterWdg):
    ''' a filter for sobject's using the login of users'''
 
    def __init__(my, select_name='user_filter', **kwargs):
        if not kwargs.get('label'):
            kwargs['label'] = 'User: '
        my.pref = kwargs.get('pref')
        super(UserFilterWdg, my).__init__(select_name, **kwargs)

        

    def init(my):
        if not my.pref:
            my.pref = PrefSetting.get_value_by_key("select_filter")
        super(UserFilterWdg, my).init()
        my.navigator.set_persistence()
        # has to set default here, not relying on the default_user option
        my.navigator.set_option("default", Environment.get_user_name())
        my.navigator.add_empty_option('-- Any Users --')
       
        """
        if my.pref == "multi":
            my.navigator.set_attr("multiple", "1")
            my.navigator.set_attr("size", "6") 
            icon = IconRefreshWdg(False)
            my.add(icon)
        """
    def alter_search(my, search):
        values = my.navigator.get_values()
        if not values or values == ['']:
            return
        if len(values) > 1:
            search.add_filters(my.search_column, values)
        else:
            search.add_filter(my.search_column, values[0])


    def get_input_cls(my):
        if my.pref == "multi":
            return "pyasm.prod.web.MultiUserSelectWdg"
        else:
            return "pyasm.prod.web.UserSelectWdg"

    def get_search_column(my):
        return "login"
   
class ProjectFilterWdg(BaseSelectFilterWdg):
    ''' a filter for sobject's using the project code'''
  
    def __init__(my, select_name='project_filter',  **kwargs):
        if not kwargs.get('label'):
            kwargs['label'] = 'Project: '
        super(ProjectFilterWdg, my).__init__(select_name, **kwargs)

    def init(my):
        my.pref = PrefSetting.get_value_by_key("select_filter")
        super(ProjectFilterWdg, my).init()
        my.navigator.set_persistence()
        my.navigator.add_empty_option(label='-- Any Projects --', value='')

        if my.pref == "multi":
            my.navigator.set_attr("multiple", "1")
            my.navigator.set_attr("size", "4") 
        else:
            my.navigator.set_submit_onchange()

    def get_input_cls(my):
        if my.pref == "multi":
            return "pyasm.prod.web.MultiProjectSelectWdg"
        else:
            return "pyasm.prod.web.ProjectSelectWdg"

    def get_search_column(my):
        return "project_code"
   

class SnapshotFilterWdg(Widget):

    def init(my):
        # add search_type select
        my.search_type_sel = FilterSelectWdg('publish_search_type')
        search = Search(SearchType.SEARCH_TYPE)
        #search.add_where("\"search_type\" ~ '(^prod|^game).*'")
        search.add_regex_filter("search_type", '^prod|^game')
        search.add_order_by('search_type')
        my.search_type_sel.set_search_for_options(search, "search_type",\
            "title")
        my.search_type_sel.set_option('default','prod/asset')

        span = SpanWdg("Type: ", css='small smaller')
        span.add(my.search_type_sel)
        my.add(span)

        # add context field
        my.context_txt = TextWdg("snapshot_context")
        my.context_txt.add_style('margin-bottom','0.4em')
        my.context_txt.set_option("size","6")
        my.context_txt.set_submit_onchange()
        my.context_txt.set_persistence()
        span = SpanWdg("Context: ", css='small smaller')
        span.add(my.context_txt)

        my.add(span)

        # add date select

        label_list = ['Today','Last 2 days', 'Last 5 days', 'Last 30 days']
        value_list = ['today','1 Day', '4 Day','29 Day']
        my.date_sel = DateFilterWdg(['publish_date', None])
        my.date_sel.set_label(label_list)
        my.date_sel.set_value(value_list)
        
        span = SpanWdg('Date: ', css='smaller')
        span.add(my.date_sel)

        my.user_filter = UserFilterWdg(pref='single')
        my.user_filter.get_navigator().set_submit_onchange()
        span.add(my.user_filter)
        my.add(span)

    def alter_search(my, search):

        value = my.search_type_sel.get_value()
        project_name = Project.get_project_name()
        if value:
            # the full name may have been stored in WidgetSettings
            if '?' in value:
                search_str = value
            else:
                search_str = '%s?project=%s' %(value,project_name)
            search.add_filter('search_type', search_str)

        value = my.context_txt.get_value().strip()
        if value:
            search.add_filter('context', value)

        my.date_sel.alter_search(search)

        my.user_filter.alter_search(search)



class SearchFilterWdg(FilterTextWdg):

    def __init__(my, name=None, label="Search: ", css=None, has_persistence=True, columns=[]):
        my.columns = columns
        if not name:
            name = "search_filter"
        super(SearchFilterWdg,my).__init__(name=name, label=label, css=css ,has_persistence=has_persistence)
  
    def alter_search(my, search):
        ''' customize the search here '''
        value = my.get_value()
        if value and my.columns:
            filter_string = Search.get_compound_filter(value, my.columns)
            search.add_where(filter_string)

    def set_columns(my, columns):
        my.columns = columns

    def get_display(my):
        widget = Widget()
        main = FilterTextWdg.get_class_display(my)
        if not my.columns:
            raise SetupException('A list of column names expected for SearchFilterWdg')
        hint = HintWdg( "Words in '%s' can be used for search." %"', '".join(my.columns))
        widget.add(main)
        widget.add(hint)

        return widget

class ContextFilterWdg(Widget):
    ''' A context filter used in App Loading tabs '''
    def __init__(my, context_data, load_type):
        my.context_data = context_data
        my.load_type = load_type
        super(ContextFilterWdg, my).__init__()
        
    def init(my):
        context_span = SpanWdg()
        context_span.set_style("white-space: nowrap")       
        context_span.add(SpanWdg("Context:", css='small'))
        context_select = FilterSelectWdg("load_%s_context" %my.load_type)
        context_select.append_option(ProdLoaderContext.LATEST, \
            ProdLoaderContext.LATEST )

        labels, values = my.context_data
        context_select.set_option("values", values)
        context_select.set_option("labels", labels)

        context_span.add(context_select)
        # to be retrieved by other elements in the tab
        Container.put('context_filter', context_select)
        my.add(context_span)




class ProcessFilterWdg(Widget):
    ''' A process filter used in App Loading tabs '''
    def __init__(my, context_data, load_type):
        my.context_data = context_data
        my.load_type = load_type
        super(ProcessFilterWdg, my).__init__()
        
    def init(my):
        context_span = SpanWdg()
        context_span.set_style("white-space: nowrap")       
        context_span.add(SpanWdg("Process: ", css='small'))

        # click the Run Search for refresh
        refresh_script = '''spt.named_events.fire_event('search_%s', bvr)'''%my.load_type
        my.context_select = SelectWdg("load_%s_process" %my.load_type)
        my.context_select.set_persistence()
        my.context_select.add_behavior({'type' : 'change',
            'cbjs_action': "%s; %s" \
            % (my.context_select.get_save_script(), refresh_script)})
       
        if my.context_data:
            labels, values = my.context_data
            my.context_select.set_option("values", values)
            my.context_select.set_option("labels", labels)

        context_span.add(my.context_select)
        # to be retrieved by other elements in the tab
        Container.put('process_filter', my.context_select)
        my.add(context_span)

    def alter_search(my, search):
        '''this alter search is needed to call the get_value() once before
        get_display()'''
        process = my.context_select.get_value()

    def get_value(my):
        return my.context_select.get_value()

class WeekFilterWdg(Widget):
    ''' a week filter with a forward and backward button '''
    #TODO: add a this week link
    def __init__(my, date=None, calendar_name=''):
        my.date = date
        my.calendar_name = calendar_name
        week_name = "week_filter"
        my.week_filter = SelectWdg(week_name)
        my.week_filter.add_class('spt_week_filter')
        
        super(WeekFilterWdg, my).__init__()

    def get_display(my):
        main_div = SpanWdg()
        weeks = [str(i) for i in xrange(1, 53)]

        current_week = ''
        if my.date:
            date = Date(db_date=my.date)
            current_week = date.get_week()
        
        my.week_filter.set_attr('disabled','true')
        my.week_filter.add_class('med')
        my.week_filter.set_option('values', weeks)
        if current_week:
            my.week_filter.set_value(str(current_week))
        #refresh_script = 'document.form.submit()'

        script = ["Timecard.summary_cal_update('%s', 'backward')" %my.calendar_name]
        #script.append(refresh_script)

        forward_script ='''var week =bvr.src_el.getParent('.spt_panel').getElement('.spt_week_filter');
            var new_val = parseInt(week.value, 10) + 1; if (new_val>52) new_val=1;
            week.value=new_val;'''
            
        backward_script ='''var week =bvr.src_el.getParent('.spt_panel').getElement('.spt_week_filter');
            var new_val = parseInt(week.value, 10) - 1; if (new_val <1) new_val=52; 
            week.value=new_val;'''

        script.append(backward_script)
        img = IconWdg("previous_week", icon=IconWdg.ARROW_LEFT)
        img.add_behavior( {'type': 'click_up',
            'cbjs_action': ';'.join(script)})
        div = SpanWdg()
        div.add(img)
        main_div.add(div)
        div.add("Week&nbsp;")
        
        div.add(my.week_filter)
        div = SpanWdg()
        
        main_div.add(div)
        script = ["Timecard.summary_cal_update('%s', 'forward')" %my.calendar_name]
        script.append(forward_script)

        img = IconWdg("next_week", icon=IconWdg.ARROW_RIGHT)
      
        img.add_behavior( {'type': 'click_up',
            'cbjs_action': ';'.join(script)})

        div.add(img)

        return main_div

    def get_value(my):
        return my.week_filter.get_value()


class PipelineFilterWdg(BaseSelectFilterWdg):
    ''' a filter for sobject's using the project code'''
    
    def __init__(my, select_name=['pipeline_filter', None, 'Pipeline: ']):
        super(PipelineFilterWdg, my).__init__(select_name)

    def init(my):
        super(PipelineFilterWdg, my).init()
        my.navigator.set_persistence()
        my.navigator.set_submit_onchange()
        my.navigator.add_empty_option(label='-- Any Pipeline --', value='')
    

    def set_search_type(my, search_type):
        my.navigator.set_search_type(search_type)

    def get_input_cls(my):
        return "pyasm.prod.web.PipelineSelectWdg"

    def get_search_column(my):
        return "pipeline_code"

class SearchTypeFilterWdg(BaseSelectFilterWdg):

    def __init__(my, select_name=['search_type_filter','Search Type: ','']):
        super(SearchTypeFilterWdg, my).__init__(select_name)

    def init(my):
        super(SearchTypeFilterWdg, my).init()
        my.navigator.set_persistence()
        my.navigator.set_submit_onchange()
        my.navigator.add_empty_option(label='-- Any Search Type --', value='')

    def alter_search(my, search):
        value = my.navigator.get_value()
        if not value:
            return
        search.add_regex_filter(my.search_column, "^%s.*" %value, "EQ")

    def get_input_cls(my):
        return "pyasm.prod.web.SearchTypeSelectWdg"
    
    def get_search_column(my):
        return 'search_type'
