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

    def init(self):
        search_columns = self.get_search_columns()
        self.text = SearchFilterWdg("text_filter", columns=search_columns,\
                has_persistence=True)
        #self.text.set_persistence()

       
        
        name = "asset_library_selection"
        self.select = FilterSelectWdg(name)
        search = Search("prod/asset_library")
        self.select.set_search_for_options( search, "code", "title" )
        self.select.add_empty_option("-- Any --")
    
        asset_library = self.select.get_value()
        WebState.get().add_state("edit|asset_library", asset_library)


        title = "Library"
        span = SpanWdg(css="med")
        span.add( self.text )
        span.add( StringWdg("%s: " % title) )
        span.add( self.select )

        self.add(span)


        """
        name = "sequence_selection"
        self.seq_select = FilterSelectWdg(name)
        seq_search = Search("prod/sequence")
        self.seq_select.set_search_for_options( seq_search, "code", "code" )
        self.seq_select.add_empty_option("-- Any --")

        title = "Sequence"
        span = SpanWdg(css="med")
        span.add( StringWdg("%s: " % title) )
        span.add( self.seq_select )
        span.add_style("margin-top: 5px")

        self.add(span)
        """



    def get_search_columns(self):
        return ['code','name','description']



    def alter_search(self, search):

        value = self.select.get_value()
        if value != "":
            search.add_filter("asset_library", value)

        """
        seq_value = self.seq_select.get_value()
        if seq_value:
            search.add_where("code in (select asset_code from sequence_instance where sequence_code = '%s')" % seq_value)
        """

        self.text.alter_search(search)

    def get_display(self):

        span = SpanWdg(css="med")
        for widget in self.widgets:
            span.add(widget)

        return span
        


class TextureFilterWdg(AssetFilterWdg):

    def init(self):

        self.asset_code_select = FilterSelectWdg("asset_code_filter", \
            label='Asset Code: ', css='small')
        search = Search("prod/asset")
        self.asset_code_select.set_search_for_options(search, "code", "code")
        self.asset_code_select.add_empty_option('-- Any --')
        self.add( self.asset_code_select )
 
        self.text = FilterTextWdg("text_filter", label='Search: ', css='small')
        self.add( self.text )

        # don't ever name the filter after a column name in an sobjeet
        self.name = "category_filter"
        self.select = FilterSelectWdg(self.name, label='Category: ', css='snall')
        self.select.set_option("setting", "texture_category")
        self.select.add_empty_option('-- Any --')
        
        self.add( self.select )



    def get_search_columns(self):
        return ['code','description']


    def alter_search(self, search):

        asset_code = self.asset_code_select.get_value()
        if asset_code != "":
            search.add_filter("asset_code", asset_code)

        value = self.select.get_value()
        if value != "":
            search.add_filter("category", value)

        value = self.text.get_value()
        if not value or value == "":
            return

        value = value.lower()
        values = value.split(" ")

        columns = self.get_search_columns()
        for value in values:
            expr = [Search.get_regex_filter(x, value) for x in columns]
            expr_full = " or ".join(expr)
            search.add_where("(%s)" % expr_full)

class CodeFilterWdg(Widget):
    '''A text based code filter '''
    def init(self):

        self.text = FilterTextWdg("code_filter", label="Code: ", css='med')
        self.add(self.text)
        self.add(HintWdg('It accepts reg. expression e.g. 12-0[0-9]+ '))

    def alter_search(self, search):

        value = self.text.get_value()
        if value:
            search.add_regex_filter("code", value)


class ShotFilterWdg(AssetFilterWdg):

    def init(self):

        #self.text = FilterTextWdg("shot_search", label='Search: ', \
        #        css='med', has_persistence=True)
        search_columns = Shot.get_search_columns()
        self.text = SearchFilterWdg("shot_search", columns=search_columns,\
                 has_persistence=True)
        self.add(self.text)


        

    def get_search_columns(self):
        return ['code','description']



    def alter_search(self, search):

        self.text.alter_search(search)
        
        '''
        value = value.lower()
        values = value.split(" ")

        columns = self.get_search_columns()
        for value in values:
            expr = [Search.get_regex_filter(x, value) for x in columns]
            expr_full = " or ".join(expr)
            search.add_where("(%s)" % expr_full)

        '''

    def get_display(self):

        
        span = SpanWdg(css="med")
        for widget in self.widgets:
            span.add(widget)
        
        #span.add(HintWdg('You can enter shot code or description'))
        return span

class BaseSelectFilterWdg(Widget):
    ''' This is a base filter other select-based filter will derive off'''
    def __init__(self, name='', **kwargs):
        self.select_name = name
        self.kwargs = kwargs
        super(BaseSelectFilterWdg, self).__init__(name)
        self.default_mode = SelectWdg.ALL_MODE
        if self.kwargs.get('mode'):
            self.default_mode = self.kwargs.get('mode')
        self.hide_empty_option = False
        self.options = {}
        self.search_column = self.get_search_column()
        self.label = '' 
        
    def init(self):
        '''add the input to be drawn here. Note: For more complex navigators
        like more than one, override init and alter_search'''
        nav = self.get_input_cls()
        if not self.select_name:
            # use the default values
            self.navigator = Common.create_from_class_path(nav)
        else:
            self.navigator = Common.create_from_class_path(nav, [self.select_name], self.kwargs)
        self.add(self.navigator) 
        
        
    def get_input_cls(self):
        return "TextWdg"
    
    def alter_search(self, search):
        value = self.navigator.get_value()
        if not value:
            return
        search.add_filter(self.search_column, value)
    
    def get_search_column(self):
        return 'code'
        
    def set_search_column(self, column):
        ''' this provides a way to set the search_column name externally'''
        self.search_column = column

    def get_display(self):
        
        span = SpanWdg()
        for widget in self.widgets:
            if self.default_mode == SelectWdg.NONE_MODE:
                widget.add_none_option()
            if self.hide_empty_option:
                widget.remove_empty_option()
            for key, value in self.options.items():
                widget.set_option(key, value)
            span.add(widget)

        return span

    def get_value(self):
        return self.navigator.get_value()
   
    def get_values(self):
        return self.navigator.get_values()
   
    def add_none_option(self):
        ''' add the --NONE-- option '''
        self.default_mode = SelectWdg.NONE_MODE

    def remove_empty_option(self):
        self.hide_empty_option = True

    def set_option(self, name, value):
        self.options[name] = value

    def get_navigator(self):
        return self.navigator

    def get_label(self):
        return self.navigator.get_label()
        
class EpisodeShotFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(self):
        return "pyasm.prod.web.EpisodeShotNavigatorWdg"

    def get_search_column(self):
        return 'shot_code' 

class EpisodeFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(self):
        return "pyasm.prod.web.EpisodeNavigatorWdg"

    def get_search_column(self):
        return 'episode_code'

class SequenceFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(self):
        return "pyasm.prod.web.SequenceNavigatorWdg"

    
    def get_search_column(self):
        return 'sequence_code'

    def alter_search(self, search):
        
        epi_code, seq_code = self.navigator.get_value()
        if epi_code and not seq_code:
            search_str = "select code from sequence where episode_code='%s'" %epi_code
            search.add_where("%s in (%s)" %(self.search_column, search_str))
        elif seq_code:
            search.add_filter(self.search_column, seq_code)

        #if epi_code:
            #search.add_filter('episode_code', epi_code)
        #foreign_key = SearchType.get(Sequence.SEARCH_TYPE).get_foreign_key()

        # TODO: this requires database introspection
        #if not search.has_column(foreign_key):
        #    return

        #search.add_filter( foreign_key, sequence_code )


class SequenceInstanceFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(self):
        return "pyasm.prod.web.SequenceNavigatorWdg"

    
    def alter_search(self, search):
        epi_code, seq_code = self.get_value()
        if not seq_code:
            return

        search.add_where("code in (select asset_code from sequence_instance where sequence_code = '%s')" % seq_code)


 
class EpisodeInstanceFilterWdg(BaseSelectFilterWdg):
    OPTION_NAME = 'use_epi_planner'

    def get_input_cls(self):
        return "pyasm.prod.web.EpisodeNavigatorWdg"

    
    def alter_search(self, search):
        epi_code = self.get_value()
        if not epi_code:
            return
        use_epi = FilterCheckboxWdg(self.OPTION_NAME)
        if use_epi.is_checked(False):
            search.add_where("code in (select asset_code from episode_instance where episode_code = '%s')" % epi_code)
        else:
            search.add_filter("episode_code", epi_code)


      



class SequenceShotFilterWdg(BaseSelectFilterWdg):

    def get_input_cls(self):
        return "pyasm.prod.web.SequenceShotNavigatorWdg"

    def get_search_column(self):
        return 'sequence_code', 'code' 

    def alter_search(self, search):
        epi_code, seq_code, shot_code = self.navigator.get_value()
     
        if seq_code:
            search.add_filter(self.search_column[0], seq_code)
        # this is if since they are not mutually exclusive
        if shot_code:
            search.add_filter(self.search_column[1], shot_code)
        
            

class DateFilterWdg(BaseSelectFilterWdg):
    ''' A filter for finding entries from a fixed number of days/hours ago ''' 
    
    def init(self):
        super(DateFilterWdg, self).init()
        self.navigator.set_persistence()
        self.navigator.add_behavior({'type' : 'change',
            'cbjs_action': "%s; %s" \
            % (self.navigator.get_save_script(), self.navigator.get_refresh_script())})

    def get_input_cls(self):
        return "pyasm.widget.DateSelectWdg"

    def get_search_column(self):
        pass

    def set_label(self, label):
        self.navigator.set_label(label)

    def set_value(self, value):
        self.navigator.set_value(value)

    def alter_search(self, search):
        value = self.navigator.get_value()
        if not value or value == SelectWdg.NONE_MODE:
            return
        search.add_where(self.navigator.get_where(value)) 
       
class BinFilterWdg(BaseSelectFilterWdg):
    ''' a filter for Bin used for dailies submissions only'''
    def init(self):
        super(BinFilterWdg, self).init()
        self.navigator.set_persistence()
        self.navigator.set_submit_onchange()
        self.navigator.add_empty_option(label='-- Select a bin --', \
            value=SelectWdg.NONE_MODE)
        self.navigator.set_label('Bin: ')

        value = self.get_value()
        WebState.get().add_state("edit|bin_select", value)
        
    def get_input_cls(self):
        return "pyasm.prod.web.BinFilterSelectWdg"

    def get_search_column(self):
        return "bin_id"

    def alter_search(self, search):
        ''' this is not really used now '''
        value = self.navigator.get_value()
        
        if not value:
            search.add_filter(self.search_column, 'NONE')
        else:
            search.add_filter(self.search_column, value)

class BinTypeFilterWdg(BaseSelectFilterWdg):
    ''' a filter for Bin type used for dailies submissions only'''

    def get_search_column(self):
        return "type"

    def get_input_cls(self):
        return "pyasm.prod.web.BinTypeFilterSelectWdg"


        
class UserFilterWdg(BaseSelectFilterWdg):
    ''' a filter for sobject's using the login of users'''
 
    def __init__(self, select_name='user_filter', **kwargs):
        if not kwargs.get('label'):
            kwargs['label'] = 'User: '
        self.pref = kwargs.get('pref')
        super(UserFilterWdg, self).__init__(select_name, **kwargs)

        

    def init(self):
        if not self.pref:
            self.pref = PrefSetting.get_value_by_key("select_filter")
        super(UserFilterWdg, self).init()
        self.navigator.set_persistence()
        # has to set default here, not relying on the default_user option
        self.navigator.set_option("default", Environment.get_user_name())
        self.navigator.add_empty_option('-- Any Users --')
       
        """
        if self.pref == "multi":
            self.navigator.set_attr("multiple", "1")
            self.navigator.set_attr("size", "6") 
            icon = IconRefreshWdg(False)
            self.add(icon)
        """
    def alter_search(self, search):
        values = self.navigator.get_values()
        if not values or values == ['']:
            return
        if len(values) > 1:
            search.add_filters(self.search_column, values)
        else:
            search.add_filter(self.search_column, values[0])


    def get_input_cls(self):
        if self.pref == "multi":
            return "pyasm.prod.web.MultiUserSelectWdg"
        else:
            return "pyasm.prod.web.UserSelectWdg"

    def get_search_column(self):
        return "login"
   
class ProjectFilterWdg(BaseSelectFilterWdg):
    ''' a filter for sobject's using the project code'''
  
    def __init__(self, select_name='project_filter',  **kwargs):
        if not kwargs.get('label'):
            kwargs['label'] = 'Project: '
        super(ProjectFilterWdg, self).__init__(select_name, **kwargs)

    def init(self):
        self.pref = PrefSetting.get_value_by_key("select_filter")
        super(ProjectFilterWdg, self).init()
        self.navigator.set_persistence()
        self.navigator.add_empty_option(label='-- Any Projects --', value='')

        if self.pref == "multi":
            self.navigator.set_attr("multiple", "1")
            self.navigator.set_attr("size", "4") 
        else:
            self.navigator.set_submit_onchange()

    def get_input_cls(self):
        if self.pref == "multi":
            return "pyasm.prod.web.MultiProjectSelectWdg"
        else:
            return "pyasm.prod.web.ProjectSelectWdg"

    def get_search_column(self):
        return "project_code"
   

class SnapshotFilterWdg(Widget):

    def init(self):
        # add search_type select
        self.search_type_sel = FilterSelectWdg('publish_search_type')
        search = Search(SearchType.SEARCH_TYPE)
        #search.add_where("\"search_type\" ~ '(^prod|^game).*'")
        search.add_regex_filter("search_type", '^prod|^game')
        search.add_order_by('search_type')
        self.search_type_sel.set_search_for_options(search, "search_type",\
            "title")
        self.search_type_sel.set_option('default','prod/asset')

        span = SpanWdg("Type: ", css='small smaller')
        span.add(self.search_type_sel)
        self.add(span)

        # add context field
        self.context_txt = TextWdg("snapshot_context")
        self.context_txt.add_style('margin-bottom','0.4em')
        self.context_txt.set_option("size","6")
        self.context_txt.set_submit_onchange()
        self.context_txt.set_persistence()
        span = SpanWdg("Context: ", css='small smaller')
        span.add(self.context_txt)

        self.add(span)

        # add date select

        label_list = ['Today','Last 2 days', 'Last 5 days', 'Last 30 days']
        value_list = ['today','1 Day', '4 Day','29 Day']
        self.date_sel = DateFilterWdg(['publish_date', None])
        self.date_sel.set_label(label_list)
        self.date_sel.set_value(value_list)
        
        span = SpanWdg('Date: ', css='smaller')
        span.add(self.date_sel)

        self.user_filter = UserFilterWdg(pref='single')
        self.user_filter.get_navigator().set_submit_onchange()
        span.add(self.user_filter)
        self.add(span)

    def alter_search(self, search):

        value = self.search_type_sel.get_value()
        project_name = Project.get_project_name()
        if value:
            # the full name may have been stored in WidgetSettings
            if '?' in value:
                search_str = value
            else:
                search_str = '%s?project=%s' %(value,project_name)
            search.add_filter('search_type', search_str)

        value = self.context_txt.get_value().strip()
        if value:
            search.add_filter('context', value)

        self.date_sel.alter_search(search)

        self.user_filter.alter_search(search)



class SearchFilterWdg(FilterTextWdg):

    def __init__(self, name=None, label="Search: ", css=None, has_persistence=True, columns=[]):
        self.columns = columns
        if not name:
            name = "search_filter"
        super(SearchFilterWdg,self).__init__(name=name, label=label, css=css ,has_persistence=has_persistence)
  
    def alter_search(self, search):
        ''' customize the search here '''
        value = self.get_value()
        if value and self.columns:
            filter_string = Search.get_compound_filter(value, self.columns)
            search.add_where(filter_string)

    def set_columns(self, columns):
        self.columns = columns

    def get_display(self):
        widget = Widget()
        main = FilterTextWdg.get_class_display(self)
        if not self.columns:
            raise SetupException('A list of column names expected for SearchFilterWdg')
        hint = HintWdg( "Words in '%s' can be used for search." %"', '".join(self.columns))
        widget.add(main)
        widget.add(hint)

        return widget

class ContextFilterWdg(Widget):
    ''' A context filter used in App Loading tabs '''
    def __init__(self, context_data, load_type):
        self.context_data = context_data
        self.load_type = load_type
        super(ContextFilterWdg, self).__init__()
        
    def init(self):
        context_span = SpanWdg()
        context_span.set_style("white-space: nowrap")       
        context_span.add(SpanWdg("Context:", css='small'))
        context_select = FilterSelectWdg("load_%s_context" %self.load_type)
        context_select.append_option(ProdLoaderContext.LATEST, \
            ProdLoaderContext.LATEST )

        labels, values = self.context_data
        context_select.set_option("values", values)
        context_select.set_option("labels", labels)

        context_span.add(context_select)
        # to be retrieved by other elements in the tab
        Container.put('context_filter', context_select)
        self.add(context_span)




class ProcessFilterWdg(Widget):
    ''' A process filter used in App Loading tabs '''
    def __init__(self, context_data, load_type):
        self.context_data = context_data
        self.load_type = load_type
        super(ProcessFilterWdg, self).__init__()
        
    def init(self):
        context_span = SpanWdg()
        context_span.set_style("white-space: nowrap")       
        context_span.add(SpanWdg("Process: ", css='small'))

        # click the Run Search for refresh
        refresh_script = '''spt.named_events.fire_event('search_%s', bvr)'''%self.load_type
        self.context_select = SelectWdg("load_%s_process" %self.load_type)
        self.context_select.set_persistence()
        self.context_select.add_behavior({'type' : 'change',
            'cbjs_action': "%s; %s" \
            % (self.context_select.get_save_script(), refresh_script)})
       
        if self.context_data:
            labels, values = self.context_data
            self.context_select.set_option("values", values)
            self.context_select.set_option("labels", labels)

        context_span.add(self.context_select)
        # to be retrieved by other elements in the tab
        Container.put('process_filter', self.context_select)
        self.add(context_span)

    def alter_search(self, search):
        '''this alter search is needed to call the get_value() once before
        get_display()'''
        process = self.context_select.get_value()

    def get_value(self):
        return self.context_select.get_value()

class WeekFilterWdg(Widget):
    ''' a week filter with a forward and backward button '''
    #TODO: add a this week link
    def __init__(self, date=None, calendar_name=''):
        self.date = date
        self.calendar_name = calendar_name
        week_name = "week_filter"
        self.week_filter = SelectWdg(week_name)
        self.week_filter.add_class('spt_week_filter')
        
        super(WeekFilterWdg, self).__init__()

    def get_display(self):
        main_div = SpanWdg()
        weeks = [str(i) for i in xrange(1, 53)]

        current_week = ''
        if self.date:
            date = Date(db_date=self.date)
            current_week = date.get_week()
        
        self.week_filter.set_attr('disabled','true')
        self.week_filter.add_class('med')
        self.week_filter.set_option('values', weeks)
        if current_week:
            self.week_filter.set_value(str(current_week))
        #refresh_script = 'document.form.submit()'

        script = ["Timecard.summary_cal_update('%s', 'backward')" %self.calendar_name]
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
        
        div.add(self.week_filter)
        div = SpanWdg()
        
        main_div.add(div)
        script = ["Timecard.summary_cal_update('%s', 'forward')" %self.calendar_name]
        script.append(forward_script)

        img = IconWdg("next_week", icon=IconWdg.ARROW_RIGHT)
      
        img.add_behavior( {'type': 'click_up',
            'cbjs_action': ';'.join(script)})

        div.add(img)

        return main_div

    def get_value(self):
        return self.week_filter.get_value()


class PipelineFilterWdg(BaseSelectFilterWdg):
    ''' a filter for sobject's using the project code'''
    
    def __init__(self, select_name=['pipeline_filter', None, 'Pipeline: ']):
        super(PipelineFilterWdg, self).__init__(select_name)

    def init(self):
        super(PipelineFilterWdg, self).init()
        self.navigator.set_persistence()
        self.navigator.set_submit_onchange()
        self.navigator.add_empty_option(label='-- Any Pipeline --', value='')
    

    def set_search_type(self, search_type):
        self.navigator.set_search_type(search_type)

    def get_input_cls(self):
        return "pyasm.prod.web.PipelineSelectWdg"

    def get_search_column(self):
        return "pipeline_code"

class SearchTypeFilterWdg(BaseSelectFilterWdg):

    def __init__(self, select_name=['search_type_filter','Search Type: ','']):
        super(SearchTypeFilterWdg, self).__init__(select_name)

    def init(self):
        super(SearchTypeFilterWdg, self).init()
        self.navigator.set_persistence()
        self.navigator.set_submit_onchange()
        self.navigator.add_empty_option(label='-- Any Search Type --', value='')

    def alter_search(self, search):
        value = self.navigator.get_value()
        if not value:
            return
        search.add_regex_filter(self.search_column, "^%s.*" %value, "EQ")

    def get_input_cls(self):
        return "pyasm.prod.web.SearchTypeSelectWdg"
    
    def get_search_column(self):
        return 'search_type'
