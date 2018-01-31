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

__all__ = ['SObjectCheckboxWdg','LayerCheckboxWdg','AssetCheckboxWdg', 
'ShotCheckboxWdg', 'LevelCheckboxWdg', 'NotesFilterSelectWdg',
'ProcessSelectWdg', 'ProcessFilterSelectWdg', 'UserSelectWdg',
'MultiUserSelectWdg', 'ProjectSelectWdg', 'MultiProjectSelectWdg',
'PipelineSelectWdg',
'WeekSelectWdg', 'YearSelectWdg', 'FrameInputWdg', 'FrameAction',
'CurrentCheckboxWdg', 'NotificationSelectWdg', 'SearchTypeSelectWdg']


from pyasm.widget import CheckboxColWdg, BaseTableElementWdg, CheckboxWdg, \
    SelectWdg, MultiSelectWdg, FilterSelectWdg, BaseInputWdg, FunctionalTableElement
from pyasm.web import SpanWdg, Table, DivWdg
from pyasm.prod.biz import *
from pyasm.biz import Pipeline, Project, CommandSObj, PrefSetting
from pyasm.search import Search, SearchType
from pyasm.security import Login
from pyasm.common import Date, Environment, Common

class SObjectCheckboxWdg(FunctionalTableElement):
    ''' a basic sobject checkbox wdg '''
    def get_title(self):
        return "Select"

    def get_display(self):

        sobject = self.get_current_sobject()

        checkbox = CheckboxWdg()
        checkbox.set_name(self.name)
        checkbox.set_option( "value", sobject.get_search_key() )

        return checkbox

    
class LayerCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_layer'
    def set_cb_name(self):
        self.name = self.CB_NAME

    
class AssetCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_asset'
    def set_cb_name(self):
        self.name = self.CB_NAME

class ShotCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_shot'
    def set_cb_name(self):
        self.name = self.CB_NAME

    def get_extra_attrs(self):
        return [('code', 'code')]

class LevelCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_level'
    def set_cb_name(self):
        self.name = self.CB_NAME

class ProcessSelectWdg(SelectWdg):
    '''Display a dropdown of processes for a given search type'''

    ARGS_KEYS = {}

    def __init__(self, name='process_select', label='', search_type=None, \
            has_empty=True, css='med', sobject=None):
        self.search_type = search_type
        self.is_filter = False
        self.has_empty = has_empty
        self._sobject = sobject
        super(ProcessSelectWdg,self).__init__(name, label=label, css=css)
        
        
    def _add_options(self):
        ''' add the options to the select '''
        search_type = self._get_search_type()
        if not search_type:
            return
        # get all processes if no search type is given
        proj_code = Project.extract_project_code(search_type)
        is_group_restricted = False

        if self.has_empty:
            self.add_first_option()
        else:
            from asset_filter_wdg import ProcessFilterWdg
            if ProcessFilterWdg.has_restriction():
                is_group_restricted = True

        process_names, process_values = Pipeline.get_process_select_data(\
            search_type, is_filter=self.is_filter, project_code=proj_code,\
            is_group_restricted=is_group_restricted, sobject = self._sobject)


        self.set_option("values", process_values)
        self.set_option("labels", process_names)
        if not self.is_filter:
            behavior = {
            'type': 'onchange',
            'cbjs_action': "if (bvr.src_el.value=='')\
                {alert('Please choose a valid process.');}" }
            #self.add_behavior(behavior)

    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_label(self, label):
        self.label = label

    def add_first_option(self):
        self.add_empty_option(label="-- Select a Process --")



    def _get_search_type(self):
        web = WebContainer.get_web()



        search_type = self.search_type
        if not search_type:
            # find the state
            search_type = self.get_state().get('search_type')
            if not search_type:
                search_type_option = web.get_form_value('parent_search_type')
                if search_type_option:
                    search_type = search_type_option
                else:
                    search_type_option = web.get_form_value('ref_search_type')
                    if search_type_option:
                        search_type = search_type_option
                    else:
                        search_type_option = web.get_form_value('search_type')
                        if search_type_option:
                            search_type = search_type_option
            current = self.get_current_sobject()
            # this is more direct and always overrides if available
            if current:
                if not current.is_insert():
                    search_type = current.get_value('search_type')
        return search_type

    def get_process_names(self):
        '''get a unique list of process names'''
        search_type = self._get_search_type()
        proj_code = Project.extract_project_code(search_type)

        dict = Pipeline.get_process_name_dict(search_type, project_code=proj_code)
        process_list = []
        for x in dict.values():
            process_list.extend(x)
        names = Common.get_unique_list(process_list)
        return names
    
    def get_display(self):
        self._add_options()
       
        return super(ProcessSelectWdg, self).get_display()
    
    

class ProcessFilterSelectWdg(ProcessSelectWdg):
    '''Display a filter of processes for a given search type'''
    def __init__(self, label='', search_type=None, name='process_filter',\
            has_empty=True, css='med'):
        '''
        self.search_type = search_type
        self.label = label
        
        self.has_empty = has_empty
        self.css = css
        '''
        # TODO, fix it so that I can set add_empty_option() without setting
        # has_empty = False first
        ProcessSelectWdg.__init__(self, label=label, \
            search_type=search_type, name=name, has_empty=has_empty, css=css)
        
        self.set_persistence()
        self.set_form_submitted()
        self.add_behavior({'type' : 'change',
            'cbjs_action': self.get_refresh_script()
           })
        self.is_filter = True 
        """
        self.pref = PrefSetting.get_value_by_key("select_filter")

        if self.pref == "multi":
            self.set_attr("multiple", "1")
            self.set_attr("size", "6") 
        else:
            self.set_submit_onchange()
        """
    def add_first_option(self):
        self.add_empty_option(label="-- Any Processes --")
  
    def _is_selected(self, value, current_values):
        return value in current_values

    def alter_search(self, search):
        process_name = ''
        process_names = self.get_values()
       
        process_names = [x for x in process_names if x]
        if len(process_names) > 1:
            
            search.add_filters("process", process_names)
            search.add_enum_order_by("process", process_names)
        elif process_names:
            process_name = process_names[0]
        if process_name:
            if ',' in process_name:
                process_list = process_name.split(',')
                search.add_filters("process", process_list)
                search.add_enum_order_by("process", process_list)
            else:
                search.add_filter("process", process_name)

class UserSelectWdg(SelectWdg):
    ''' a select of users '''
    def __init__(self,  name='user_filter', **kwargs):
        
        super(UserSelectWdg, self).__init__(name, **kwargs)
        self.add_empty_option('-- Select a User --')
        

    def get_display(self):
        search = Search(Login)
        self.set_search_for_options(search, 'login','login')
        self.set_option("extra_values", "admin")
        if self.kwargs.get('default_user') =='true':
            self.set_option('default', Environment.get_user_name())
        return super(UserSelectWdg, self).get_display() 

class MultiUserSelectWdg(MultiSelectWdg):
    ''' a multi select of users '''
    def __init__(self,  name='user_filter', label='', css='med'):
        super(MultiUserSelectWdg, self).__init__(name=name, label=label, css=css)
        self.add_empty_option('-- Select a User --')
        

    def get_display(self):
        search = Search(Login)
        self.set_search_for_options(search, 'login','login')
        if self.kwargs.get('default_user') =='true':
            self.set_option('default', Environment.get_user_name())
        return super(MultiUserSelectWdg, self).get_display() 

class ProjectSelectWdg(SelectWdg):
    ''' a select of projects '''
    def __init__(self,  name='project_filter', label='', css='med'):
        super(ProjectSelectWdg, self).__init__(name, label=label, css=css)
        self.add_empty_option('-- Select a Project --')

    def get_display(self):
        search = Search(Project)
        search.add_where("\"code\" not in ('sthpw','admin')")
        self.set_search_for_options(search, 'code','code')
        self.set_option('default', Project.get_project_code())
        return super(ProjectSelectWdg, self).get_display() 

class MultiProjectSelectWdg(MultiSelectWdg):

    def __init__(self,  name='project_filter', label='', css='med'):
        super(MultiProjectSelectWdg, self).__init__(name, label=label, css=css)
        self.add_empty_option('-- Select a Project --')


    def get_display(self):
        search = Search(Project)
        search.add_where("\"code\" not in ('sthpw','admin')")
        self.set_search_for_options(search, 'code','code')
        self.set_option('default', Project.get_project_code())
        return super(MultiProjectSelectWdg, self).get_display() 
   

class PipelineSelectWdg(SelectWdg):
    ''' a select of pipelines '''
    def __init__(self, name='pipeline_filter', **kwargs):
        
        super(PipelineSelectWdg, self).__init__(name, **kwargs)
        self.search_type = self.kwargs.get('search_type')

    def set_search_type(self, search_type):
        self.search_type = search_type

    def get_display(self):
        pipeline_search = Search( Pipeline )
        if not self.search_type:
            search_type_option = self.get_option('search_type')
            if search_type_option:
                self.search_type = search_type_option
        if self.search_type:
            pipeline_search.add_filter( 'search_type', self.search_type )
        pipeline_search.add_order_by( 'code' )
        project_code = Project.get_project_code()
        pipeline_search.add_project_filter(project_code)

        self.set_search_for_options( pipeline_search, 'code', 'code' )

        return super(PipelineSelectWdg, self).get_display()
                

class WeekSelectWdg(SelectWdg):
    ''' a select of weeks '''
    def __init__(self,  name='week_select', **kwargs):
        
        super(WeekSelectWdg, self).__init__(name, **kwargs)


    def get_display(self):
        last_week = 52
        if self.kwargs.get('show_future') == 'false':
            today = Date()
            last_week = int(today.get_week())

        weeks = [i for i in xrange(1, last_week + 1)]
        weeks.reverse()
        self.set_option('values', weeks)
        return super(WeekSelectWdg, self).get_display()

class YearSelectWdg(SelectWdg):
    ''' a select of years '''
    def __init__(self,  name='year_select', **kwargs):
        super(YearSelectWdg, self).__init__(name, **kwargs)
       
    def get_display(self):
        today = Date()
        cur_year = int(today.get_year())
       
        limit = self.get_option('limit')
        if limit:
            limit = int(limit)
        else:
            limit = 10
        years = [i for i in xrange(cur_year-limit + 1, cur_year + 1)]
        years.reverse()
        self.set_option('values', years)

        return super(YearSelectWdg, self).get_display()
        
    

class NotesFilterSelectWdg(FilterSelectWdg):
    ''' a select of notes contexts '''
    def __init__(self,  name='discussion_context', label='Notes Context: ', css='med', setting=None):
        self.setting = setting
        super(NotesFilterSelectWdg, self).__init__(name, label=label)
        
        # we must have a list to choose from
        assert self.setting != None

        self.set_option("setting", self.setting)
    


from pyasm.widget import TextWdg, TextAreaWdg
from pyasm.web import DivWdg, WebContainer
from pyasm.command import DatabaseAction


class FrameInputWdg(BaseInputWdg):
    '''Display a number of interface elements depending on the available
    columns in the shot table'''

    def get_display(self):
        sobject = self.get_current_sobject()

        # handle the start and end
        frame_start = sobject.get_value("tc_frame_start")
        frame_end = sobject.get_value("tc_frame_end")

        frame_start_text = TextWdg("tc_frame_start")
        frame_start_text.set_value(frame_start)
        frame_start_text.set_option("size", "2")

        frame_end_text = TextWdg("tc_frame_end")
        frame_end_text.set_value(frame_end)
        frame_end_text.set_option("size", "2")

        # handle the notes
        frame_notes = sobject.get_value("frame_note")
        frame_notes_text = TextAreaWdg("frame_note")
        frame_notes_text.set_value(frame_notes)
        frame_notes_text.set_option("rows", "2")


        # handle the in and out handles
        frame_in = sobject.get_value("frame_in")
        frame_out = sobject.get_value("frame_out")

        frame_in_text = TextWdg("frame_in")
        frame_in_text.set_value(frame_in)
        frame_in_text.set_option("size", "2")

        frame_out_text = TextWdg("frame_out")
        frame_out_text.set_value(frame_out)
        frame_out_text.set_option("size", "2")


        div = DivWdg()


        table = Table()
        div.add(table)
        table.add_row()
        td = table.add_cell("Range:")
        td.add_style("width: 100px")
        td = table.add_cell()
        td.add_style("text-align: right")
        td.add_style("padding: 5px")
        td.add("start: ")
        td.add(frame_start_text)
        td = table.add_cell()
        td.add_style("text-align: right")
        td.add_style("padding: 5px")
        td.add("end: ")
        td.add(frame_end_text)

        table.add_row()
        table.add_cell("Handles:")
        td = table.add_cell()
        td.add_style("text-align: right")
        td.add_style("padding: 5px")
        td.add("in: ")
        td.add(frame_in_text)
        td = table.add_cell()
        td.add_style("text-align: right")
        td.add_style("padding: 5px")
        td.add("out: ")
        td.add(frame_out_text)
        td.add("<br/>")

        table.add_row()
        table.add_cell("Notes:")
        td = table.add_cell(frame_notes_text)
        td.add_style("padding: 5px")
        td.add_attr("colspan", "2")

        return div



class FrameAction(DatabaseAction):

    def execute(self):
        sobject = self.sobject

        web = WebContainer.get_web()

        attrs = ["tc_frame_start", "tc_frame_end", "frame_in", "frame_out", "frame_note"]
        for attr in attrs:
            value = web.get_form_value(attr)
            sobject.set_value(attr,value)

class CurrentCheckboxWdg(CheckboxWdg):
    ''' used for displaying whether a snapshot is current or not'''
    def get_display(self):
        if self.get_value() == True:
            self.set_checked()
        super(CurrentCheckboxWdg, self).get_display()


class NotificationSelectWdg(SelectWdg):
    ''' a select of notification codes '''
    def __init__(self,  name='notification_select', css=''):
        super(NotificationSelectWdg, self).__init__(name)
        
    def init(self):
        search = Search(CommandSObj)
        search.add_column('notification_code')
        search.add_group_by('notification_code')
        self.set_search_for_options(search, 'notification_code','notification_code')
      

# TODO: this class should not be in prod!!! It should be in pyasm.widget
class SearchTypeSelectWdg(SelectWdg):
    ''' a select of production search types, so no sthpw search types'''
    (ALL, CURRENT_PROJECT, ALL_BUT_STHPW) = range(3)

    def __init__(self,  name='search_type_select', label='', css='', mode=None):
        self.mode = mode
        super(SearchTypeSelectWdg, self).__init__(name,  label=label, css=css)

    def init(self):
        
        #defining init is better than get_display() for this kind of SelectWdg
        search = Search( SearchType.SEARCH_TYPE )
        
        if self.mode == None or self.mode == self.ALL_BUT_STHPW:
            # always add the login / login group search types
            filter = search.get_regex_filter("search_type", "login|task|note|timecard|milestone", "EQ")
            no_sthpw_filter = search.get_regex_filter("search_type", "^(sthpw).*", "NEQ")   
            search.add_where('%s or %s' %(filter, no_sthpw_filter))
        elif self.mode == self.CURRENT_PROJECT:
            project = Project.get()
            project_code = project.get_code()
            #project_type = project.get_project_type().get_type()
            project_type = project.get_value("type")
            search.add_where("\"namespace\" in ('%s','%s') " % (project_type, project_code))

        
        search.add_order_by("search_type")
        self.set_search_for_options(search, "search_type", "get_label()")
        self.add_empty_option(label='-- Select Search Type --')



