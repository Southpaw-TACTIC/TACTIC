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
from pyasm.web import SpanWdg
from pyasm.prod.biz import *
from pyasm.biz import Pipeline, Project, CommandSObj, PrefSetting
from pyasm.search import Search, SearchType
from pyasm.security import Login
from pyasm.common import Date, Environment, Common

class SObjectCheckboxWdg(FunctionalTableElement):
    ''' a basic sobject checkbox wdg '''
    def get_title(my):
        return "Select"

    def get_display(my):

        sobject = my.get_current_sobject()

        checkbox = CheckboxWdg()
        checkbox.set_name(my.name)
        checkbox.set_option( "value", sobject.get_search_key() )

        return checkbox

    
class LayerCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_layer'
    def set_cb_name(my):
        my.name = my.CB_NAME

    
class AssetCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_asset'
    def set_cb_name(my):
        my.name = my.CB_NAME

class ShotCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_shot'
    def set_cb_name(my):
        my.name = my.CB_NAME

    def get_extra_attrs(my):
        return [('code', 'code')]

class LevelCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'prod_level'
    def set_cb_name(my):
        my.name = my.CB_NAME

class ProcessSelectWdg(SelectWdg):
    '''Display a dropdown of processes for a given search type'''

    ARGS_KEYS = {}

    def __init__(my, name='process_select', label='', search_type=None, \
            has_empty=True, css='med', sobject=None):
        my.search_type = search_type
        my.is_filter = False
        my.has_empty = has_empty
        my._sobject = sobject
        super(ProcessSelectWdg,my).__init__(name, label=label, css=css)
        
        
    def _add_options(my):
        ''' add the options to the select '''
        search_type = my._get_search_type()
        if not search_type:
            return
        # get all processes if no search type is given
        proj_code = Project.extract_project_code(search_type)
        is_group_restricted = False

        if my.has_empty:
            my.add_first_option()
        else:
            from asset_filter_wdg import ProcessFilterWdg
            if ProcessFilterWdg.has_restriction():
                is_group_restricted = True

        process_names, process_values = Pipeline.get_process_select_data(\
            search_type, is_filter=my.is_filter, project_code=proj_code,\
            is_group_restricted=is_group_restricted, sobject = my._sobject)


        my.set_option("values", process_values)
        my.set_option("labels", process_names)
        if not my.is_filter:
            behavior = {
            'type': 'onchange',
            'cbjs_action': "if (bvr.src_el.value=='')\
                {alert('Please choose a valid process.');}" }
            #my.add_behavior(behavior)

    def set_search_type(my, search_type):
        my.search_type = search_type

    def set_label(my, label):
        my.label = label

    def add_first_option(my):
        my.add_empty_option(label="-- Select a Process --")



    def _get_search_type(my):
        web = WebContainer.get_web()



        search_type = my.search_type
        if not search_type:
            # find the state
            search_type = my.get_state().get('search_type')
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
            current = my.get_current_sobject()
            # this is more direct and always overrides if available
            if current:
                if not current.is_insert():
                    search_type = current.get_value('search_type')
        return search_type

    def get_process_names(my):
        '''get a unique list of process names'''
        search_type = my._get_search_type()
        proj_code = Project.extract_project_code(search_type)

        dict = Pipeline.get_process_name_dict(search_type, project_code=proj_code)
        process_list = []
        for x in dict.values():
            process_list.extend(x)
        names = Common.get_unique_list(process_list)
        return names
    
    def get_display(my):
        my._add_options()
       
        return super(ProcessSelectWdg, my).get_display()
    
    

class ProcessFilterSelectWdg(ProcessSelectWdg):
    '''Display a filter of processes for a given search type'''
    def __init__(my, label='', search_type=None, name='process_filter',\
            has_empty=True, css='med'):
        '''
        my.search_type = search_type
        my.label = label
        
        my.has_empty = has_empty
        my.css = css
        '''
        # TODO, fix it so that I can set add_empty_option() without setting
        # has_empty = False first
        ProcessSelectWdg.__init__(my, label=label, \
            search_type=search_type, name=name, has_empty=has_empty, css=css)
        
        my.set_persistence()
        my.set_form_submitted()
        my.add_behavior({'type' : 'change',
            'cbjs_action': my.get_refresh_script()
           })
        my.is_filter = True 
        """
        my.pref = PrefSetting.get_value_by_key("select_filter")

        if my.pref == "multi":
            my.set_attr("multiple", "1")
            my.set_attr("size", "6") 
        else:
            my.set_submit_onchange()
        """
    def add_first_option(my):
        my.add_empty_option(label="-- Any Processes --")
  
    def _is_selected(my, value, current_values):
        return value in current_values

    def alter_search(my, search):
        process_name = ''
        process_names = my.get_values()
       
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
    def __init__(my,  name='user_filter', **kwargs):
        
        super(UserSelectWdg, my).__init__(name, **kwargs)
        my.add_empty_option('-- Select a User --')
        

    def get_display(my):
        search = Search(Login)
        my.set_search_for_options(search, 'login','login')
        my.set_option("extra_values", "admin")
        if my.kwargs.get('default_user') =='true':
            my.set_option('default', Environment.get_user_name())
        return super(UserSelectWdg, my).get_display() 

class MultiUserSelectWdg(MultiSelectWdg):
    ''' a multi select of users '''
    def __init__(my,  name='user_filter', label='', css='med'):
        super(MultiUserSelectWdg, my).__init__(name=name, label=label, css=css)
        my.add_empty_option('-- Select a User --')
        

    def get_display(my):
        search = Search(Login)
        my.set_search_for_options(search, 'login','login')
        if my.kwargs.get('default_user') =='true':
            my.set_option('default', Environment.get_user_name())
        return super(MultiUserSelectWdg, my).get_display() 

class ProjectSelectWdg(SelectWdg):
    ''' a select of projects '''
    def __init__(my,  name='project_filter', label='', css='med'):
        super(ProjectSelectWdg, my).__init__(name, label=label, css=css)
        my.add_empty_option('-- Select a Project --')

    def get_display(my):
        search = Search(Project)
        search.add_where("\"code\" not in ('sthpw','admin')")
        my.set_search_for_options(search, 'code','code')
        my.set_option('default', Project.get_project_code())
        return super(ProjectSelectWdg, my).get_display() 

class MultiProjectSelectWdg(MultiSelectWdg):

    def __init__(my,  name='project_filter', label='', css='med'):
        super(MultiProjectSelectWdg, my).__init__(name, label=label, css=css)
        my.add_empty_option('-- Select a Project --')


    def get_display(my):
        search = Search(Project)
        search.add_where("\"code\" not in ('sthpw','admin')")
        my.set_search_for_options(search, 'code','code')
        my.set_option('default', Project.get_project_code())
        return super(MultiProjectSelectWdg, my).get_display() 
   

class PipelineSelectWdg(SelectWdg):
    ''' a select of pipelines '''
    def __init__(my, name='pipeline_filter', **kwargs):
        
        super(PipelineSelectWdg, my).__init__(name, **kwargs)
        my.search_type = my.kwargs.get('search_type')

    def set_search_type(my, search_type):
        my.search_type = search_type

    def get_display(my):
        pipeline_search = Search( Pipeline )
        if not my.search_type:
            search_type_option = my.get_option('search_type')
            if search_type_option:
                my.search_type = search_type_option
        if my.search_type:
            pipeline_search.add_filter( 'search_type', my.search_type )
        pipeline_search.add_order_by( 'code' )
        project_code = Project.get_project_code()
        pipeline_search.add_project_filter(project_code)

        my.set_search_for_options( pipeline_search, 'code', 'code' )

        return super(PipelineSelectWdg, my).get_display()
                

class WeekSelectWdg(SelectWdg):
    ''' a select of weeks '''
    def __init__(my,  name='week_select', **kwargs):
        
        super(WeekSelectWdg, my).__init__(name, **kwargs)


    def get_display(my):
        last_week = 52
        if my.kwargs.get('show_future') == 'false':
            today = Date()
            last_week = int(today.get_week())

        weeks = [i for i in xrange(1, last_week + 1)]
        weeks.reverse()
        my.set_option('values', weeks)
        return super(WeekSelectWdg, my).get_display()

class YearSelectWdg(SelectWdg):
    ''' a select of years '''
    def __init__(my,  name='year_select', **kwargs):
        super(YearSelectWdg, my).__init__(name, **kwargs)
       
    def get_display(my):
        today = Date()
        cur_year = int(today.get_year())
       
        limit = my.get_option('limit')
        if limit:
            limit = int(limit)
        else:
            limit = 10
        years = [i for i in xrange(cur_year-limit + 1, cur_year + 1)]
        years.reverse()
        my.set_option('values', years)

        return super(YearSelectWdg, my).get_display()
        
    

class NotesFilterSelectWdg(FilterSelectWdg):
    ''' a select of notes contexts '''
    def __init__(my,  name='discussion_context', label='Notes Context: ', css='med', setting=None):
        my.setting = setting
        super(NotesFilterSelectWdg, my).__init__(name, label=label)
        
        # we must have a list to choose from
        assert my.setting != None

        my.set_option("setting", my.setting)
    


from pyasm.widget import TextWdg, TextAreaWdg
from pyasm.web import DivWdg, WebContainer
from pyasm.command import DatabaseAction


class FrameInputWdg(BaseInputWdg):
    '''Display a number of interface elements depending on the available
    columns in the shot table'''

    def get_display(my):
        sobject = my.get_current_sobject()

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
        frame_notes_text.set_option("rows", "1")


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
        div.add("Range - start: ")
        div.add(frame_start_text)
        div.add(" - end: ")
        div.add(frame_end_text)
        div.add("<br/>")
        div.add("Handles - in: ")
        div.add(frame_in_text)
        div.add(" - out: ")
        div.add(frame_out_text)
        div.add("<br/>")
        div.add("Notes:")
        div.add(frame_notes_text)

        return div



class FrameAction(DatabaseAction):

    def execute(my):
        sobject = my.sobject

        web = WebContainer.get_web()

        attrs = ["tc_frame_start", "tc_frame_end", "frame_in", "frame_out", "frame_note"]
        for attr in attrs:
            value = web.get_form_value(attr)
            sobject.set_value(attr,value)

class CurrentCheckboxWdg(CheckboxWdg):
    ''' used for displaying whether a snapshot is current or not'''
    def get_display(my):
        if my.get_value() == True:
            my.set_checked()
        super(CurrentCheckboxWdg, my).get_display()


class NotificationSelectWdg(SelectWdg):
    ''' a select of notification codes '''
    def __init__(my,  name='notification_select', css=''):
        super(NotificationSelectWdg, my).__init__(name)
        
    def init(my):
        search = Search(CommandSObj)
        search.add_column('notification_code')
        search.add_group_by('notification_code')
        my.set_search_for_options(search, 'notification_code','notification_code')
      

# TODO: this class should not be in prod!!! It should be in pyasm.widget
class SearchTypeSelectWdg(SelectWdg):
    ''' a select of production search types, so no sthpw search types'''
    (ALL, CURRENT_PROJECT, ALL_BUT_STHPW) = range(3)

    def __init__(my,  name='search_type_select', label='', css='', mode=None):
        my.mode = mode
        super(SearchTypeSelectWdg, my).__init__(name,  label=label, css=css)

    def init(my):
        
        #defining init is better than get_display() for this kind of SelectWdg
        search = Search( SearchType.SEARCH_TYPE )
        
        if my.mode == None or my.mode == my.ALL_BUT_STHPW:
            # always add the login / login group search types
            filter = search.get_regex_filter("search_type", "login|task|note|timecard|milestone", "EQ")
            no_sthpw_filter = search.get_regex_filter("search_type", "^(sthpw).*", "NEQ")   
            search.add_where('%s or %s' %(filter, no_sthpw_filter))
        elif my.mode == my.CURRENT_PROJECT:
            project = Project.get()
            project_code = project.get_code()
            #project_type = project.get_project_type().get_type()
            project_type = project.get_value("type")
            search.add_where("\"namespace\" in ('%s','%s') " % (project_type, project_code))

        
        search.add_order_by("search_type")
        my.set_search_for_options(search, "search_type", "get_label()")
        my.add_empty_option(label='-- Select Search Type --')



