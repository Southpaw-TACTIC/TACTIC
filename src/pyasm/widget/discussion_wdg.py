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


__all__ = ['DiscussionWdg', 'CommentAttr', 'CommentCmd', 'NoteUtilWdg','NoteUtilCmd']

import time, types, re 

from pyasm.common import Xml, Date, Common, Environment, UserException
from pyasm.search import Search, SObject, SearchKey
from pyasm.biz import Snapshot, Note
from pyasm.command import CommandException, CommandExitException, Command
from pyasm.web import WebContainer, HtmlElement, SpanWdg, DivWdg, Html, Widget,\
        WikiUtil, FloatDivWdg, AjaxCmd, AjaxWdg, WidgetSettings
from pyasm.prod.biz import ProdSetting, Submission

from table_element_wdg import *
from input_wdg import TextAreaWdg, SelectWdg, PopupMenuWdg, HiddenWdg, FilterTextWdg, FilterSelectWdg, FilterCheckboxWdg
from icon_wdg import *
from web_wdg import *


from tactic.ui.common import BaseRefreshWdg

class DiscussionWdg(BaseTableElementWdg, AjaxWdg):

    # this default value should not be changed. You can modify it thru
    # display option 'process_filter'
    PROCESS_FILTER_NAME = "process_filter"
    DISPLAY_OPTION = "doption_DiscussionWdg"

    def __init__(self, **kwargs):

        self.kwargs = kwargs

        self.notes_dict = {}
        self.preprocess_notes = False
        self.contexts = []
        self.global_context = '' 
        self.append_context = ''
        self.append_setting = ''
        self.wdg_width = 400
        # this is needed for Ajax
        self.parent_wdg = None
        self.pref_text = None
        
        self.process_filter = self.PROCESS_FILTER_NAME
        self.include_submission = 'false'
     
        self.refresh_event_dict = {}
        from tactic.ui.container import PopupWdg, MenuWdg, MenuItem
        self.pop_menu = PopupWdg( id="NoteMenuWdg", allow_page_activity=True, width="", aux_position='right')
        self.pref_show_sub_notes = FilterCheckboxWdg('discussion_show_sub_notes', label='show submission notes')

        BaseTableElementWdg.__init__(self)
        AjaxWdg.__init__(self)

        self.sobject = None
        self.setting = None
      
        self.init_cgi()
        

    def is_ajax(self, xx=None):
        return self.kwargs.get("refresh") == "true"
        

    def init_cgi(self):

        # get the sobject
        if not self.is_ajax(True):
            return
        keys = self.web.get_form_keys()
        search_key = self.web.get_form_value("search_key")
        if not search_key:
            search_key = self.kwargs.get("search_key")
        
        self.sobject = Search.get_by_search_key(search_key)
        self.sobjects = [self.sobject]

        # set multiple display options
        hidden = HiddenWdg(self._get_display_option_name())
        disp_option = hidden.get_value()
        disp_options = disp_option.split('||')
        for option in disp_options:
            disp_option = option.split(':')
            if len(disp_option) == 2:
                self.set_option(disp_option[0], disp_option[1])
        
        self.init_setup()

    def is_searchable(self):
        return True

    def get_searchable_search_type(self):
        '''get the searchable search type for local search'''
        return 'sthpw/note'

    def set_context(self, context):
        '''takes a string that describes the context to be displayed'''
        self.context = context

        
    def init_setup(self):
        '''setup for a bunch of options and prefs used in this widget''' 
        self.global_context = self.get_option("context")

        self.append_context = self.get_option("append_context")
        if not self.append_context:
            self.append_context = self.kwargs.get("append_context")
        if self.get_option('process_filter'):
            self.process_filter = self.get_option('process_filter')
        self.setting = self.get_option('setting')
        if not self.setting:
            self.setting = self.kwargs.get('setting')
        self.append_setting = self.get_option('append_setting')
        if not self.append_setting:
            self.append_setting = self.kwargs.get("append_setting")
        self._get_sticky_status() 

        self.include_submission = self.get_option('include_submission')
        width = self.get_option("wdg_width")
        if width:
            self.wdg_width = width

        # put the display option in here
        hidden = HiddenWdg(self._get_display_option_name())
        self.add_ajax_input(hidden)
        self.add_ajax_input_name(self._get_pref_name("comments_max_height"))
        self.add_ajax_input_name(self._get_pref_name("discussion_wdg_width")) 
        self.add_ajax_input_name('discussion_show_sub_notes')
        
        self.set_ajax_option("config_base_temp", self._get_config_base())
        self.set_ajax_option("name", "discussion" )
        self._init_prefs()

    def _get_config_base(self):
        config_base = ''
        if self.get_config_base():
            config_base = self.get_config_base()
        else:
            #config_base = self.web.get_form_value('config_base_temp')
            config_base = self.kwargs.get('config_base_temp')
        return config_base

    def _get_search_type(self):
        search_type = ''
        if self.get_search_type():
            search_type = self.get_search_type()
        else:
            #search_type = self.web.get_form_value('search_type')
            search_type = self.kwargs.get('search_type')
        return search_type



    def _get_pref_name(self, pref_name):
        config_base = self._get_config_base()
        pref_name = '%s_%s' %(config_base, pref_name)
        return pref_name

    def _init_prefs(self):
        height_pref_name = self._get_pref_name('comments_max_height')
        self.pref_text = FilterTextWdg(height_pref_name,'Max height: ',\
            css='small', is_number=True)
        
        width_pref_name = self._get_pref_name('discussion_wdg_width')
        self.pref_width = FilterTextWdg(width_pref_name, 'Width: ',\
            css='small', is_number=True) 
        self.pref_show_sub_notes = FilterCheckboxWdg('discussion_show_sub_notes', label='show submission notes')
        # if a display option is defined, the widget setting will be true by default
        if self.get_option('include_submission') =='true':
            self.pref_show_sub_notes.set_checked()
            self.pref_show_sub_notes.set_attr('disabled', 'disabled')

    def get_prefs(self):
        widget = Widget()
        self.pref_text.set_attr('size','3')
        self.pref_text.set_unit('px')
        self.pref_text.set_option('default','200')
        if self.get_option("scroll") != "false":
            widget.add(self.pref_text)
        
        self.pref_width.set_attr('size','3')
        self.pref_width.set_unit('px')
        self.pref_width.set_option('default','400')
        widget.add(self.pref_width)
        
        widget.add(self.pref_show_sub_notes)
       
        return widget
    
    def handle_td(self, td):
        pass

    def get_note_menu(self):
        ''' add the Note Utililty popup menu'''

        # DEPRECATED: note that this whole widget is deprecated, but in this
        # the MenuWdg does not work ... presumable, the finger menu is
        # conflicting with what was there before
        return

        widget = self.pop_menu
        off_script = widget.get_cancel_script()
        note_util_wdg = NoteUtilWdg()
        hidden = HiddenWdg('base_name')
        widget.add(hidden)
        hidden = HiddenWdg('note_action')
        widget.add(hidden)
        hidden = HiddenWdg('skey_note')
        widget.add(hidden)
        hidden = HiddenWdg('skey_note_parent')
       

        refresh_event = 'refresh_note_menu_monitor'
        # values are outside the panel 
        script = "var values = spt.api.Utility.get_input_values('NoteMenuWdg_content', '.spt_input');\
                spt.panel.refresh($('%s').getElement('.spt_note_menu_panel'), values, true)" %widget.get_aux_id();
        behavior = {
            'type': 'listen',
            'event_name': refresh_event,
            'cbjs_action': script
        }
        hidden.add_behavior(behavior)

        widget.add(hidden)
        
        monitor_on_script = widget.get_show_aux_script()
        widget.add_aux(note_util_wdg)
        widget.add_title('Note Menu')


        menu = MenuWdg(mode='vertical', background='#999', top_class='old_note_menu')
        widget.add(menu)

        #span = DivWdg('Move', css='hand')
        span = MenuItem('action', label='move')
        script = [] 
        script.append(monitor_on_script)
        script.append("get_elements('note_action').set_value('MOVE')")
        script.append("spt.named_events.fire_event('%s', {})" % refresh_event)

        item_behavior = {
            'type': 'click_up',
            'cbjs_action': ';'.join(script)
        }
        span.add_behavior(item_behavior)
        menu.add(span)
        
        span = MenuItem('action', label='copy')
        script = [] 
        script.append(monitor_on_script)
        script.append("get_elements('note_action').set_value('COPY')")
        script.append("spt.named_events.fire_event('%s', {})" % refresh_event)

        item_behavior = {
            'type': 'click_up',
            'cbjs_action': ';'.join(script)
        }
        span.add_behavior(item_behavior)
        menu.add(span)

        span = MenuItem('action', label='edit')
        script = [] 
        script.append(monitor_on_script)
        script.append("get_elements('note_action').set_value('EDIT')")
        script.append("spt.named_events.fire_event('%s', {})" % refresh_event)

        item_behavior = {
            'type': 'click_up',
            'cbjs_action': ';'.join(script)
        }
        span.add_behavior(item_behavior)
        menu.add(span)

        span = MenuItem('action', label='delete')
        script = [] 
        script.append(monitor_on_script)
        script.append("get_elements('note_action').set_value('DEL')")
        script.append("spt.named_events.fire_event('%s', {})" % refresh_event)

        item_behavior = {
            'type': 'click_up',
            'cbjs_action': ';'.join(script)
        }
        span.add_behavior(item_behavior)
        menu.add(span)
       
        span = MenuItem('action', label='status')
        script = [] 
        script.append(monitor_on_script)
        script.append("get_elements('note_action').set_value('STATUS')")
        script.append("spt.named_events.fire_event('%s', {})" % refresh_event)

        item_behavior = {
            'type': 'click_up',
            'cbjs_action': ';'.join(script)
        }
        span.add_behavior(item_behavior)
        menu.add(span)


        hidden = HiddenWdg('note_util_offscript', off_script)
        widget.add(hidden)

        
        return widget

       

   

    def get_title(self):
        widget = Widget()
        # display options are formatted as 
        # <option1_name>:<option1_value>||<option2_name>:<option2_value>...
        dis_option = ['sticky:%s' % self.get_option('sticky')]
        dis_option.append('setting:%s' % self.get_option('setting'))
        dis_option.append('append_setting:%s' % self.get_option('append_setting'))
        dis_option.append('process_filter:%s' % self.get_option('process_filter'))
        dis_option.append('context:%s' % self.get_option('context'))
        dis_option.append('append_context:%s' % self.get_option('append_context'))
        dis_option.append('include_submission:%s' % self.get_option('include_submission'))
        dis_option.append('scroll:%s' % self.get_option('scroll'))


        self.dis_hidden = HiddenWdg(self._get_display_option_name(), '||'.join(dis_option))
        widget.add(self.dis_hidden) 
        
        widget.add(self.get_note_menu())
        widget.add(super(DiscussionWdg,self).get_title())

        return widget

    def _get_display_option_name(self):
        view = self._get_config_base() 
        search_type = self._get_search_type()
        dis_option_name = '%s_%s_%s' %(self.DISPLAY_OPTION, search_type, view)
        return dis_option_name

    def _get_discussion_context(self):
        ''' returns a list. look for a discussion_context. The order matters here
        context defined in config or as an option always takes precedence '''
       
        self.global_context = self.get_option("context")
        if not self.global_context:
            self.global_context = self.kwargs.get('context')
        if self.global_context:
            return [self.global_context]
        
        web = WebContainer.get_web()
        dis_context_name = self._get_pref_name("discussion_context")
        discussion_context = self.kwargs.get(dis_context_name)
        if discussion_context:
            return [discussion_context]
        
        # NO LONGER NEEDED for 2.5
        # sometimes user would pick "Any Contexts" in Dailies tab which is ''
        # FIXME: web has residual keys from the last tab right now, so this check doesn't work
        """
        if not discussion_context and web.has_form_key(self.process_filter):
            process_filter = FilterSelectWdg(name=self.process_filter)
            discussion_contexts = process_filter.get_values()
            discussion_context = [x for x in discussion_contexts if x]
        """
        if not discussion_context: 
            discussion_context = []
        return discussion_context

    def alter_note_search(self, search, prefix='children', prefix_namespace='' ):
        from tactic.ui.filter import FilterData, BaseFilterWdg, GeneralFilterWdg
        filter_data = FilterData.get()
        parent_search_type = self.sobjects[0].get_search_type()
        
        if not filter_data.get_data():
            # use widget settings
            key = "last_search:%s" % parent_search_type
            data = WidgetSettings.get_value_by_key(key)
            if data:
                filter_data = FilterData(data)
            filter_data.set_to_cgi()

        
        filter_mode_prefix = 'filter_mode'
        if prefix_namespace:
            filter_mode_prefix = '%s_%s' %(prefix_namespace, filter_mode_prefix)
        
        filter_mode = 'and'
        filter_mode_value = filter_data.get_values_by_index(filter_mode_prefix, 0)
        if filter_mode_value:
            filter_mode = filter_mode_value.get('filter_mode')
       
        if prefix_namespace:
            prefix = '%s_%s' %(prefix_namespace, prefix)
        values_list = BaseFilterWdg.get_search_data_list(prefix, \
                search_type=self.get_searchable_search_type())
        if values_list:
            
            if filter_mode != 'custom': 
                search.add_op('begin')
            GeneralFilterWdg.alter_sobject_search( search, values_list, prefix, mode='child')
                    
            if filter_mode != 'custom':
                search.add_op(filter_mode)
        
        
        return search
    

    def preprocess(self):
        '''get all of the notes for these sobjects'''
         
        self.init_setup()

        
        self.notes_dict = {}

        search = Note.get_search_by_sobjects(self.sobjects)
        if not search:
            return

       
        try:
            
            # go thru children of main search
            search = self.alter_note_search(search, prefix='children')
            #print "search ", search.get_statement()
            # go thru Local Search
            search = self.alter_note_search(search, prefix='main_body', prefix_namespace=self.__class__.__name__)

           
        except:
            from tactic.ui.app import SearchWdg
            parent_search_type = self.sobjects[0].get_search_type()
            SearchWdg.clear_search_data(parent_search_type)
            raise





        search.add_order_by("context")
        search.add_order_by("timestamp desc")

        discussion_contexts = self._get_discussion_context()
        
        discussion_context = ''
        context_list = []
        where_filters = []
        if len(discussion_contexts) > 1:
            context_list.extend(discussion_contexts)
            where_filters.append(search.get_filters('context', context_list))
            where_filters.append(search.get_filters('status', self.sticky))
        elif discussion_contexts:
            discussion_context = discussion_contexts[0]
        if discussion_context:
            if "," in discussion_context:
                context_list = discussion_context.split(',')
                where_filters.append(search.get_filters('context', context_list))
            else:
                where_filters.append(search.get_filter('context', discussion_context))

            # always get the notes with sticky statuses, only if context is selected
            where_filters.append(search.get_filters('status', self.sticky))
        if where_filters:
            search.add_where('( %s )' %' or '.join(where_filters))
        notes = search.get_sobjects()
        

        # Build up a dictionary.  Note: SObject.get_dict() does not work
        # here because we need a list for each sobject
        key_cols = ["search_type", "search_id"]
        for note in notes:

            key = '|'.join([ str(note.get_value(col)) for col in key_cols])
            notes_in_sobject = self.notes_dict.get(key)
            if not notes_in_sobject:
                notes_in_sobject = []
                self.notes_dict[key] = notes_in_sobject

            notes_in_sobject.append(note)


        # get all of the attachments for these notes
        #note_ids = [str(x.get_id()) for x in notes]
        #note_ids_str = ", ".join(note_ids)
        
        snapshots = Snapshot.get_by_sobjects(notes, is_latest=True)
        self.snapshots_count = {}
        self.snapshots = {}
        for snapshot in snapshots:
            search_id = snapshot.get_value("search_id")

            if not self.snapshots_count.get(search_id):
                self.snapshots_count[search_id] = 1
            else:
                self.snapshots_count[search_id] += 1


            list = self.snapshots.get(search_id)
            if not list:
                list = []
                self.snapshots[search_id] = list
            list.append(snapshot)

        self.preprocess_notes = True
    
    
      
    def _get_sticky_status(self):
        '''set what statuses are sticky for notes'''
        self.sticky = self.get_option('sticky')
        if isinstance(self.sticky, list):
            return
        if self.sticky:
            self.sticky = self.sticky.split('|')
        else:
            self.sticky = ['new']

    def get_text_value(self):
        self.sobject = self.get_current_sobject()

        comment_area = []

        # collect the notes
        self.sticky =  []
        if not self.preprocess_notes:
            self.preprocess()
        notes = self.notes_dict.get(self.sobject.get_search_key())
        if not notes:
            return ''

        last_context = None
        for i, note in enumerate(notes):
            context = note.get_value('context')
            # explicit compare to None
            if last_context == None or context != last_context:
                comment_area.append( "[ %s ] " % context )
            last_context = context
            
            child_notes = note.get_child_notes()
            # draw note item
            comment_area.append(note.get_value("login"))
            comment_area.append(note.get_value("note"))
            comment_area.append('\n')
            if child_notes:
                for child_note in child_notes:
                    child_note_value = child_note.get_value('note')
                    comment_area.append( "Reply: %s" %child_note_value)
                    comment_area.append( '\n' )
        return ' '.join(comment_area)


            
    def get_display(self):
        # replace the event container functions per get_display
        self.replace = True

        web = WebContainer.get_web()

        if not self.is_ajax():
            self.sobject = self.get_current_sobject()
        else:
            self.name = web.get_form_value("name")
        
        # in regular drawing mode, just call get_value()
        if self.pref_text:
            self.pref_height_value = self.pref_text.get_value()
            self.pref_width_value = self.pref_width.get_value()  
        else:
            self.pref_height_value = "100%"
            self.pref_width_value = "100%"

        self.show_sub_notes_value = self.pref_show_sub_notes.is_checked(False)
        try:
            if int(self.pref_width_value) > int(self.wdg_width):
                self.wdg_width = self.pref_width_value
        except ValueError:
            pass
        # get the context the config file or Note Context filter or Process filter
        
        self.contexts = self._get_discussion_context()
        search_type = self.sobject.get_search_type()
        id = self.sobject.get_id()

        # name is part of the base name
        name = self.get_name()
        if not name:
            name = self.kwargs.get("name")
        if not name:
            name = "notes"
        
        import random
        rand = random.randint(1, 100)
        self.base_name = "notes|%s|%s|%s" % (search_type, id, rand)
        
        self.status_id = '%s_sign' %self.base_name
        
        refresh_event = '%s_refresh' %self.base_name

        
        dis_context_name = self._get_pref_name("discussion_context")
        
      
        # ajax elements that must be defined here
        self.add_ajax_input_name(self.base_name)
        self.add_ajax_input_name("%s_context" % self.base_name)
        self.add_ajax_input_name("%s_parent" % self.base_name)
        

      
        if self.is_ajax():
            main_div = Widget()
        else:
            main_div = DivWdg()
            main_div.add_style('width: 100%')
            main_div.add_style('min-width: 200px')
            main_div.add_style('padding: 0px 0px 0px 3px')

            # new refresh using get_widget
            main_div.add_class("spt_discussion_panel")
            class_name = Common.get_full_class_name(self)
            main_div.add_attr("spt_class_name", class_name)

            # this base name will get outdated when it changes after each update by using a random number
            main_div.add_attr("spt_base_name", self.base_name)
            main_div.add_attr("spt_refresh", "true")
            main_div.add_attr("spt_config_base_temp", self._get_config_base())
            main_div.add_attr("spt_name", "discussion" )
            main_div.add_attr("spt_search_key", self.sobject.get_search_key() )
            main_div.add_attr("spt_search_type", self.sobject.get_base_search_type() )
            main_div.add_attr("spt_%s" % dis_context_name, ','.join(self.contexts))
            if self.global_context:
                main_div.add_attr("spt_context", self.global_context)

            if self.setting:
                main_div.add_attr("spt_setting", self.setting)
            if self.append_context:
                main_div.add_attr("spt_append_context", self.append_context)
            main_div.add_attr("spt_append_setting", self.append_setting)
           
        
        div = DivWdg()

        div.add_color('background','background', -10)
        div.add_style('width: 96%')
        div.add_style('padding: 5px')
        #div.add_style('width', '%spx' %self.wdg_width) 
        main_div.add(div)
        
        # these are for compatibility with CommentCmd
        hidden_base = HiddenWdg('base_name', self.base_name)
        div.add(hidden_base)

        hidden_base = HiddenWdg('search_key', self.sobject.get_search_key())
        div.add(hidden_base)

        #event = WebContainer.get_event_container()
        #caller = event.get_event_caller(SiteMenuWdg.EVENT_ID)
        #main_div.set_post_ajax_script(caller)

        # collect the notes
        if not self.preprocess_notes:
            self.preprocess()
        key = "%s|%s" % (self.sobject.get_search_type(), self.sobject.get_id())
        notes = self.notes_dict.get(key)
     
        if not notes:
            notes = []

        # add submission notes
        if self.include_submission == 'true' or self.show_sub_notes_value == True:
            filter_contexts = self._get_discussion_context()
            submission_notes = Submission.get_all_notes(self.sobject, filter_contexts)
            notes.extend(submission_notes)
            
            def compare_context(y, x):
                return cmp( y.get_value("context"), x.get_value("context") )
            def compare_time(x, y):
                return cmp( y.get_value("timestamp"), x.get_value("timestamp"))
            
            # this is not the fastest method but it's easier to read than lambda
            notes.sort(cmp = compare_time)
            notes.sort(cmp = compare_context)
            
        
        # declare comment_attr here
        comment_attr = None

        use_notes = True
        comment_toggle_event = '%s_toggle' % self.base_name
        new_note_swap = SwapDisplayWdg()
        num_comments = xrange(len(notes))
        if len(num_comments) == 0:
            div.add( self._get_add_comment_wdg(new_note_swap, comment_toggle_event) )
            return main_div
        
        # create an event
        event_name1 = '%s_main_expand' % self.base_name
        event_name2 = '%s_main_collapse' % self.base_name
        
        
        #comment_toggle_caller = event.get_event_caller(comment_toggle_event)
        comment_toggle_caller = "spt.named_events.fire_event('%s', {})" % comment_toggle_event
        # add expand/collapse button
        swap = SwapDisplayWdg()
    
        #swap.add_action_script(event.get_event_caller(event_name1), \
        #    event.get_event_caller(event_name2))
        swap.add_action_script(
            "spt.named_events.fire_event('%s', {})" % event_name1,
            "spt.named_events.fire_event('%s', {})" % event_name2
        )

        div.add(swap)

        # this needs to be the search_key since we may mix search type in the
        # same page like Artist tab.
        #base_id = "comment_%s" % self.sobject.get_search_key()
        base_id = "%s_comment" % self.base_name

        comment_area = DivWdg()

        if self.get_option("scroll") != "false":
            comment_area.add_style("max-height", "%spx" % self.pref_height_value)
            comment_area.add_style("overflow: auto")


        last_context = None 

        sticky_notes, parent_notes, note_dict = self._preprocess_notes(notes)
    
        sticky_base_id = '%s_stick' % base_id
        for i, note in enumerate(sticky_notes):
            child_notes = note_dict.get(note.get_id())
            self.draw_note(i, note, child_notes, comment_area, sticky_base_id, \
                 event_name1, event_name2, comment_toggle_caller, \
                 new_note_swap, 'discussion_sticky', use_notes)

        for i, note in enumerate(parent_notes):

            context = note.get_value('context')
            # explicit compare to None
            if last_context == None or context != last_context:
                comment_area.add( DivWdg(HtmlElement.b("[ %s ]" % context)) )
            last_context = context
           
            child_notes = note_dict.get(note.get_id())
            # draw note item
            self.draw_note(i, note, child_notes, comment_area, base_id, \
                 event_name1, event_name2, comment_toggle_caller, \
                 new_note_swap, 'discussion_parent', use_notes)

            

        #security = WebContainer.get_security()
        #if not security.check_access("sobject|column", \
        #        "%s|%s" % (search_type,self.name), "edit"):
        div.add(comment_area)

        div.add( self._get_add_comment_wdg(new_note_swap, comment_toggle_event) )
        
        # add a hidden input for storing parent_id
        hidden = HiddenWdg('%s_parent' %self.base_name, '')
        div.add(hidden)
        return main_div


    def _preprocess_notes(self, notes):
        '''sort out the parent and child relationsip here. and group the
        sticky notes '''
        sticky_notes = []
        sticky_dict = {}
        
        parent_notes = []
        note_dict = {}
        for note in notes:
            parent_id = note.get_parent_id()
            if parent_id:
                note_list = note_dict.get(parent_id)
                if note_list != None:
                    note_list.append(note)
                else:
                    note_dict[parent_id] = [note]
            else:
                parent_notes.append(note)
                if note.get_status() in self.sticky:
                    sticky_notes.append(note)
                    # used for chronological sorting
                    sticky_dict[note.get_value('timestamp')] = note

        # resort the sticky notes
        sticky_notes = Common.sort_dict(sticky_dict)
        sticky_notes.reverse()

        return sticky_notes, parent_notes, note_dict


    def draw_note(self, idx, note, child_notes, comment_area,  base_id, event_name1, event_name2, \
            comment_toggle_caller, new_note_swap, note_css, use_notes=True):
        event = WebContainer.get_event_container()

        status = ''
        if not use_notes:
            # skip if we have specified a context
            context = comment_attr.get_context(idx)
            if self.contexts != [""] and context not in self.contexts:
                return

            user, date, comment = comment_attr.get_comment_data(idx)
            date = date[4:16]
        else: # current implementation
            user = note.get_value("login")
            date = str(note.get_value("timestamp"))
            date = Date(db=date)
            date = date.get_display("%b %d - %H:%M")
            comment = note.get_value("note")
            context = note.get_value("context")
            status = note.get_value("status")
            note_id = note.get_id()
            parent_id = note.get_parent_id()

        # parent_id either comes from its parent or its own id if it is a parent
        if not parent_id:
            parent_id = note_id

        comment_div = DivWdg()
        if note_css == 'discussion_sticky':
            comment_div.add_color('background','background', +20)
        elif note_css == 'discussion_parent':
            comment_div.add_color('background','background', -20)
        elif note_css == 'discussion_child':
            comment_div.add_color('background','background', -10)

        from pyasm.widget import ClipboardAddWdg
        clipitem_add = ClipboardAddWdg(note)
        clipitem_add.set_thumbnail_mode(False)
        comment_div.add(clipitem_add)
        comment_div.set_id('note_id_%s' %note.get_id())
        comment_div.add_style("display", "block")

        date_span = SpanWdg(date, css='smaller')
        
        comment_div.add( date_span )
        
        # add status span
        if note_id == parent_id:
            status_span = self._get_status_span(status, note_id, event)
            comment_div.add(status_span)

        if not user:
            user_span = SpanWdg(css='small')
            user_span.add("<i>No user</i>")
            user_span.add('&gt;')
        else:
            user_span = UserExtraInfoWdg(user)
            user_span.add_class('small')
            user_span.add('&gt;')
        comment_div.add( user_span )

        comment = WikiUtil().convert(comment)
        max_comment_len = 40
        if self.wdg_width:
            try:
                max_comment_len = int(float(self.wdg_width) / 8)
            except ValueError:
                pass
        if len(comment) > max_comment_len:
            short = comment[:max_comment_len] + "..."
        else:
            short = comment

        comment = self._replace_references(comment)

        # TODO: index here is reused on refresh
        index = idx
        
        long_id = "%s_long_%s" % (base_id, index)
        
        short_id = "%s_short_%s" % (base_id, index)
        child_div_id = ''
        swap_function = ["swap_display('%s','%s')" % (long_id, short_id)]

        if child_notes:
            # add expand child notes function if applicable
            child_div_id = '%s_child' %long_id
            
            swap_function.append("Note.child_display('%s','%s','%s')" \
                    % (child_div_id, long_id, short_id))
        


        # have two div's, one short version and the other long version
        span_short = SpanWdg(short, css='hand')
        span_short.add_style("display", "inline")
        span_short.set_id(short_id)

        
        span_short.set_attr('parent_id', parent_id)

        # add self-swap event
        span_short.add_event('onclick', ';'.join(swap_function))

        span_long = SpanWdg( comment, css='hand')
        span_long.add_style("display", "none")
        span_long.set_id( long_id )
        span_long.add_event('onclick', ';'.join(swap_function))

        
        
        main_swap_function1 = "set_display_on('%s'); set_display_off('%s')" \
                % (long_id, short_id)
        main_swap_function2 = "set_display_on('%s'); set_display_off('%s')" \
                % (short_id, long_id)



        #event.add_listener(event_name1, main_swap_function1, self.replace )
        #event.add_listener(event_name2, main_swap_function2, self.replace )
        behavior = {
            'type': 'listen',
            'event_name': event_name1,
            'cbjs_action': main_swap_function1
        }
        comment_div.add_behavior(behavior)

        behavior = {
            'type': 'listen',
            'event_name': event_name2,
            'cbjs_action': main_swap_function2
        }
        comment_div.add_behavior(behavior)



        # stop resetting event container after the first note
        self.replace = False

        comment_div.add( span_short )
        comment_div.add( span_long )

       
        # add the reply link for parent note
        if note_id == parent_id:
            # add the total of child notes if any
            if child_notes:
                comment_div.add(' (%s)' %len(child_notes))
            script = []
            script.append(comment_toggle_caller)
            script.append("Note.focus_note('%s', -180, '%s', '%s')" \
                %(self.base_name, short_id, self.status_id))
            script.append(new_note_swap.get_swap_script(bias=SwapDisplayWdg.ON))
            
            # lock the context to match that of the parent note
            select_name = "%s_context" % self.base_name
            script.append("Note.lock_context('%s','%s')" %(select_name, context))

            reply = HtmlElement.href(data=" [ reply ] ", ref="#")
            reply.add_color('color','color2')
            reply.add_behavior({'type': 'click_up',
                'cbjs_action': ';'.join(script)})
            comment_div.add(reply)

            # add a function button
            
            icon_wdg = IconWdg("", IconWdg.INFO)
            icon_wdg.add_class('hand')
            

            menu_script = ["Note.setup_util('%s','%s','%s')" \
                %(note.get_search_key(), note.get_parent_search_key(), self.base_name)]
        
           
            menu_script.append(self.pop_menu.get_cancel_aux_script())
            menu_script.append("spt.popup.open('NoteMenuWdg');")
            menu_script.append('''
                    var pos = spt.mouse.get_abs_cusor_position(evt);
                    var offset_x = -300;
                    var popup = $('NoteMenuWdg');
                    popup.setStyle('left', pos.x + offset_x);
                    popup.setStyle('top', pos.y - 120);
            ''')


            icon_wdg.add_behavior({'type': 'click_up', \
                    'cbjs_action': ';'.join(menu_script)})

            action_wdg = SpanWdg(css='small')
            comment_div.add(action_wdg)
            action_wdg.add(icon_wdg)

            # if count is zero, the just add the publish link
            count = self.snapshots_count.get(note_id)
            if not count:
                # add a publish link
                from pyasm.widget import PublishLinkWdg, ThumbWdg
                publish_link = PublishLinkWdg("sthpw/note", note_id)
                publish_link.set_value_dict({'parent_search_key': \
                        note.get_parent_search_key()})
                action_wdg.add(publish_link)
            else:


                # add a publish link
                from pyasm.widget import PublishLinkWdg, ThumbWdg
                publish_link = PublishLinkWdg("sthpw/note", note_id)
                publish_link.set_value_dict({'parent_search_key': \
                        note.get_parent_search_key()})

                # build a popup link to show publish browsing
                browse_link = IconButtonWdg("Publish Browser", IconWdg.CONTENTS)
                browse_link.add_behavior({'type': 'click_up',
                    'cbfn_action': 'spt.popup.get_widget',
                    'options': {'popup_id' : 'publish_browser',
                                'class_name' : 'pyasm.prod.web.PublishBrowserWdg' ,
                                'title': 'Publish Browser'},
                    'args' : { 'search_type': 'sthpw/note',
                                'search_id' : note_id }
                    })


                # add the popup menu
                popup_menu = PopupMenuWdg("upload_pop_menu_%s" % note_id,  width='160px')
                popup_menu.set_submit(False)
                popup_menu.set_auto_hide(True)
                popup_menu.set_offset(-50,0)


                icon_span = SpanWdg(css='small')
                publish_link.add_style("float: left")
                icon_span.add(publish_link)
                icon_span.add(browse_link)
                popup_menu.add(icon_span)
                popup_menu.add('<br/>')
                popup_menu.add_title("Attachment")

                
                popup_link = IconButtonWdg("Attachment", IconWdg.SAVE)
                popup_link.add_event("onclick", popup_menu.get_on_script() )

                if count:
                    popup_menu.add("<hr/>")
                    snapshot_list = self.snapshots.get(note_id)
                    for snapshot in snapshot_list:
                        web_dir = snapshot.get_web_dir()
                        file_name = snapshot.get_file_name_by_type("main")
                        file_name_start = file_name[0:20]
                        file_name_end = file_name[-4:]
                        if len(file_name) > 20:
                            file_name2 = "%s...%s" % (file_name_start, file_name_end)
                        else:
                            file_name2 = file_name_start
                        file_path = "%s/%s" % (web_dir, file_name)
                        popup_menu.add("<a target='_blank' href='%s'>%s</a>" % (file_path, file_name2))
                        popup_menu.add("<br/>")



                # add the popup to the action_wdg
                action_wdg.add(popup_menu)
                action_wdg.add(popup_link)
                if count:
                    span = SpanWdg("(%s)" % count)
                    span.add_attr('title', 'Latest per context count')
                    action_wdg.add(span)






        comment_area.add( comment_div )

        

        # adding child notes
        if child_notes:
            # add expand child notes icon if applicable

            child_div = DivWdg(id = child_div_id)
            child_div.add_style('display: block')
            child_div.add_style('margin-left: 20px')
            
            #base_id = '%s_%s' %(base_id, child_div_id)
            base_id = child_div_id
            for idx, child_note in enumerate(child_notes):
                
                self.draw_note(idx, child_note, [], child_div, base_id, \
                     event_name1, event_name2, comment_toggle_caller, new_note_swap, \
                     note_css='discussion_child')

            comment_area.add(child_div)


    def _get_status_span(self, status, note_id, event):
        status_dict = ProdSetting.get_dict_by_key('note_status')
        status_value = status_dict.get(status)
        # add a default status (-) if not set yet
        if not status_value:
            status_value = '-'

        status_span = SpanWdg(HtmlElement.b(status_value), css='small_left selection_item') 
        status_span.add_behavior({'type': 'click', 'cbjs_action': "alert('Use the info button to change note status')"})
        
        return status_span

    def _get_add_comment_wdg(self, swap, toggle_event_name):

        div_id = "%s_add" % self.base_name

        div = DivWdg()

        #event = WebContainer.get_event_container()
        #event.add_listener(toggle_event_name, "set_display_on('%s')" % div_id)
        behavior = {
            'type': 'listen',
            'event_name': toggle_event_name,
            'cbjs_action': "spt.simple_display_show($(bvr.src_el).getParent('.spt_discussion_panel').getElement('.spt_discussion_new'))"
        }
        div.add_behavior(behavior)
        

        div.add_style("text-align: right")
        div.add_style("margin-bottom: 10px")
      
        
        
        add_comment = IconWdg("New Note", IconWdg.NOTE_ADD, True)
        hide_comment = IconWdg("Hide", IconWdg.NOTE_DELETE, True)

        swap.set_display_widgets(add_comment, hide_comment)
        #swap.add_action_script("toggle_display('%s')" % div_id)
        swap.add_action_script("spt.simple_display_toggle(bvr.src_el.getParent('.spt_discussion_panel').getElement('.spt_discussion_new'))")

        div.add(swap)
        div2 = DivWdg()
        div2.add_class("spt_discussion_new")
        
        div2.add_style("text-align: right")
        div2.set_id(div_id)
        div2.add_style("display: none")

        status_div = FloatDivWdg('New Note: ', id=self.status_id)
        status_div.add_class("left_content")
        div2.add(status_div)

        # add a new note link
        new_note_id = '%s_new' %self.base_name
        link = HtmlElement.js_href("Note.new_note('%s','%s','%s')" \
            % (new_note_id, self.status_id, self.base_name), data=" [ New note ]")
        new_note = FloatDivWdg(link, id = new_note_id )
        new_note.add_style('display: none')
        new_note.add_class("left_content")
        div2.add(new_note)

        textarea = TextAreaWdg(self.base_name)
        textarea.set_attr('rows','4')
        textarea.add_style("width: 90%")
        textarea.set_id(self.base_name)

        textarea.force_default_context_menu()

        cols = 35
        try:
            if self.wdg_width:
                cols = cols * int(self.wdg_width) / 350
        except ValueError:
            pass
        textarea.set_attr("cols", cols)
        div2.add(HtmlElement.br())
        div2.add(textarea)
        div2.add(HtmlElement.br())

        setting = self.setting
        select_name = "%s_context" % self.base_name
        
        # construct from setting if any
        context_span = None
        if setting:
            context_span = SpanWdg()
            context_span.add_style("float: left")
            context_select = SelectWdg(select_name)

            context_select.set_option("setting", setting)

            context_select.add_empty_option("<- Select ->")
            if self.contexts:
                # just take the first one
                context_select.set_value(self.contexts[0])
            
            context_span.add("Context: ")
            context_span.add(context_select)
            div2.add(context_span)
        elif self.global_context:
            context_select = SelectWdg(select_name)
            context_select.append_option(self.global_context, self.global_context)
            context_span = SpanWdg("Context: ")
            context_span.add_style("float: left")
            context_span.add(context_select)
            
            div2.add(context_span)


        else:
            # assume there is a ProcessFilterSelectWdg in the page
            from pyasm.prod.web import ProcessSelectWdg, ProcessFilterSelectWdg
            context_select = ProcessSelectWdg( has_empty=False,\
                search_type=self.sobject.get_base_search_type(), sobject=self.sobject)
            
            context_select._add_options()
            labels, values = context_select.get_select_values() 
            set_dom_again = False

            if self.append_setting:
                temp_select = SelectWdg(select_name)
                temp_select.set_option("setting", self.append_setting)
                append_values, append_labels = temp_select._get_setting()
                if append_values:
                    context_select.append_option('','')
                    context_select.append_option('&lt;&lt; %s &gt;&gt;' %self.append_setting, '')
                for value in append_values:
                    if value not in values:
                        context_select.append_option(value, value)
                        values.append(value)
                        set_dom_again = True
            for context in self.contexts:
                if context and context not in values and "," not in context:
                    context_select.append_option(context, context)
                    set_dom_again = True
            
            security = Environment.get_security()
            # append custom context
            append_context = self.append_context
            if append_context:
                append_context = append_context.split('|')
                for context in append_context:
                    if security.check_access('note_context', context, "view"):
                        context_select.append_option(context, context)
                set_dom_again = True
                
            if set_dom_again:
                context_select.set_dom_options()
            
            
            context_select.set_name(select_name)
            behavior = {
            'type': 'change',
            'cbjs_action': "if (bvr.src_el.value=='')\
                {alert('Please choose a valid context.');}" }
            
            context_select.add_behavior(behavior)

            
            process_filter =  ProcessFilterSelectWdg(\
                 search_type=self.sobject.get_base_search_type(),\
                 name=self.process_filter)
            
            current_filter_value = process_filter.get_value()

            # heading of processes contains commas
            if current_filter_value and ',' not in current_filter_value:
                context_select.set_value(current_filter_value)
            context_span = SpanWdg("Context: ")
            context_span.add_style("float: left")
            context_span.add(context_select)
            
            div2.add(context_span)

        context_span.add_style('padding-top','10px')
        # add add clipboard button
        #clipboard = SpanWdg()
        #clipboard.add("test clipboard")
        #div2.add( clipboard )

        # register the note entry ajax script 
        refresh_event = '%s_refresh' %self.base_name

        # TEST
        script = "spt.panel.refresh( $(bvr.src_el).getParent('.spt_discussion_panel'), null, true)";
       
        div2.add_named_listener(refresh_event, script)
 

        # FIXME: put the check for valid context back in somehow
        submit = IconButtonWdg("Submit Note", IconWdg.NOTE_GO, True)
        #add_script = ["if (get_elements('%s').get_value()=='')\
        #    {alert('Please choose a valid context.'); return false;}" %select_name]
        #add_script.append(event.get_event_caller(refresh_event))
        #submit.add_event("onclick", ";".join(add_script) )

        behavior = {
            'type': 'click_up',
            
            'cbjs_action': '''if (get_elements('%s').get_value()=='')
                {alert('Please choose a valid context.');} else { 
                try { 
                    TacticServerCmd.execute_cmd('pyasm.widget.CommentCmd',
                    $(bvr.src_el).getParent('.spt_discussion_panel'));}
                catch (e) {
                    alert(spt.exception.handler(e));}

                spt.named_events.fire_event('%s', bvr);}''' %(select_name, refresh_event)
        }
        submit.add_behavior(behavior)
        
        div2.add(HtmlElement.br(2))
        div2.add(submit)

        widget = Widget()
        widget.add(div)
        widget.add(div2)

        return widget


    def _replace_references(self, comment):
        ''' replace search_key with a thumbnail '''
        p = re.compile( r"\|\|(.*)\|\|", re.DOTALL )
        m = p.search(comment)
        if m:
            search_key = m.groups()[0]
            from file_wdg import ThumbWdg
            from pyasm.search import Search
            ref = Search.get_by_search_key(search_key)
            thumb = ThumbWdg()
            thumb.set_sobject(ref)
            thumb.set_icon_size(45)
            html = thumb.get_buffer_display()
            comment = comment.replace("||%s||" % search_key, html)

        return comment

class NoteUtilWdg(BaseRefreshWdg):


    def get_args_keys(self):
        '''external settings which populate the widget'''
        return { 'base_name': 'Base name for the DiscussionWdg',
                 'skey_note': 'Search key for the note',
                 'skey_note_parent': 'Search key for the parent',
                 'note_action': 'Note Action like EDIT or MOVE or STATUS',
                 'note_util_offscript': 'Off script'}

    def init(self):
        self.parent = None
        self.new_parent = None
        self.main_div = DivWdg(id='parent_sobj')
        self.main_div.add_style('margin: 4px')
        class_name = Common.get_full_class_name(self)
        self.main_div.add_attr("spt_class_name", class_name)
        
        self.main_div.add_class("spt_note_menu_panel")

        # get the sobject
        web = WebContainer.get_web() 
        search_key = self.kwargs.get('skey_note_parent')
        note_search_key = self.kwargs.get('skey_note')
        if note_search_key:
            self.note = Search.get_by_search_key(note_search_key)
        self.off_script = self.kwargs.get('note_util_offscript')
        self.note_action = self.kwargs.get('note_action')
        self.base_name = self.kwargs.get('base_name')
        new_parent_search_key = self.kwargs.get('skey_new_parent')
        if search_key:
            self.parent = Search.get_by_search_key(search_key)
        if new_parent_search_key:
            self.new_parent = Search.get_by_search_key(new_parent_search_key)

       
  
    def add(self, widget):
        self.main_div.add(widget)


    def get_display(self):
        #TODO: on refresh, don't draw container div 
        
        widget = self.main_div
       
        # no parent in first draw
        if not self.parent:
            return widget

        
        is_action = True
        note = self.note.get_value('note')[:30]
        span = DivWdg('%s...' %note)
        span.add_style('line-height: 1.0em')
        widget.add(span)
        widget.add(HtmlElement.br())
        msg = ''
        msg_css = ''
        if self.note_action == "MOVE":
            msg = 'Move to:'
        elif self.note_action == "COPY":
            msg = 'Copy to:'
        elif self.note_action == "EDIT":
            msg = 'Edit:'
        elif self.note_action == "DEL":
            msg_css = 'warning'
            security = Environment.get_security()
            if self.note.get_login() == Environment.get_user_name() or \
                    security.check_access("project", "admin", "view"):
                msg = "Delete this note?"
            elif self.note.get_login() != Environment.get_user_name():
                msg = "You can only delete your own notes."
                is_action = False

        elif self.note_action == "STATUS":
            msg = 'Edit Status:'
        span = SpanWdg('%s '%msg, css='small %s' %msg_css)
        widget.add(span)
        search_type = self.parent.get_value('search_type', no_exception=True)
        web = WebContainer.get_web()
       
        parent_search_key = ''

        # trying to look for grandparent
        if search_type:
            parent_search_key = self.parent.get_parent_search_key()
        else: # settle for just the parent
            search_type = self.parent.get_search_type()
       
   
        # values are outside the panel intentionally
        server_cmd = "values =spt.api.Utility.get_input_values(bvr.src_el.getParent('.spt_popup_content'), '.spt_input'); "
        server_cmd += "TacticServerCmd.execute_cmd('pyasm.widget.NoteUtilCmd', null, {}, values);"


        widget.add(self._get_monitor(self.note_action, search_type))
        
        # add OK button
        button = ProdIconButtonWdg('OK')
        div = DivWdg(button)

        div.add_style('float','right')
        div.add_style('right','14px')
        div.add_style('margin-bottom', '10px')
        widget.add(HtmlElement.br(2))
        widget.add(div)
        script = []
        script.append( server_cmd )
        script.append( self.off_script )
        
        execute_event = 'NoteUtilCmd_exe'
       
        #pat = re.compile(r'(.*\|)(.*\|.*)(\|.*)')
        #new_base_name = pat.sub( r'\1%s\3'%self.parent.get_search_key(), self.base_name)
       
        #TODO: this does not account for the Destination search key for edit and copy operation
        behavior = {
            'type': 'click_up',
            'cbjs_action': ';'.join(script),
            'cbjs_postaction': "spt.named_events.fire_event('%s_refresh', {})" %(self.base_name)} 


            
        button.add_behavior(behavior)
        return widget

    def _get_status_wdg(self):
        div = DivWdg()
        div.add(HtmlElement.br())

        values_map = ProdSetting.get_map_by_key('note_status')
        if not values_map:
            # put in a default
            ProdSetting.create('note_status', 'new:N|read:R|old:O|:-', 'map',\
                description='Note Statuses', search_type='sthpw/note')

        # display the shortform (value), store the full value (key) in db
        labels, values = [], []
        for key, value in values_map:
            desc = key
            if desc == '':
                desc = '&lt; empty &gt;'
            labels.append('%s: %s'%(value, desc))
            values.append(key)
        
        status_sel = SelectWdg('note_status')
        status_sel.set_option('labels', labels)
        status_sel.set_option('values', values)
        status_sel.add_empty_option('-- Select a Status --')
        cur_status = self.note.get_value('status')
        
        #if cur_status:
        status_sel.set_value(cur_status)
        div.add(status_sel)

        return div

    def _get_monitor(self, action, search_type):
        '''get the widget on the right side (the monitor)'''
        widget = Widget()
        if action in ['COPY', 'MOVE']:
            select = SelectWdg('skey_new_parent')
            parent_search_key = ''

            # trying to look for grandparent
            search_type = self.parent.get_value('search_type', no_exception=True)
            if search_type:
                parent_search_key = self.parent.get_parent_search_key()
            else: # settle for just the parent
                search_type = self.parent.get_search_type()
            # start a search
            search = Search(search_type)
            self.categorize(widget, search_type, search)
            search.add_order_by("code")
           
            sobjects = search.get_sobjects()
            
            values = [x.get_search_key() for x in sobjects]

            labels = []
            code_col = 'code'
            for x in sobjects:
                name = x.get_name()
                code = x.get_code()
                if code_col and x.has_value(code_col):
                    code = x.get_value(code_col) 
                if name == code:
                    labels.append(code)
                else:
                    labels.append("%s - %s" % (code, name) )

            select.set_option("values", values)
            select.set_option("labels", labels)
            select.add_empty_option()
            # TO BE REMOVED: transfer the options
            for key, value in self.options.items():
                select.set_option(key, value)
         
            if parent_search_key: 
                select.set_value(parent_search_key) 
            widget.add(select)

        elif action == 'EDIT':
            text = TextAreaWdg('edited_note')
            text.set_attr('rows','4')
            text.set_attr('cols','30')
            text.set_value(self.note.get_value('note'))
            widget.add(text)

        elif action == 'STATUS':
            widget.add(self._get_status_wdg())
        return widget

    def categorize(self, widget, search_type, search):
        '''categorize parents based on search_type'''
        # FIXME: this should not be here.  This is a general class for all
        # search types, not just prod/asset
        if "prod/asset" in search_type:
            lib_select = SelectWdg('parent_lib')
            lib_select.persistence = False
            search2 = Search("prod/asset_library")
            lib_select.set_search_for_options( search2, "code", "title" )
            lib_select.add_empty_option("-- Any --")
            widget.add(lib_select) 
            # get all of the options for this search type
            parent_lib = lib_select.get_value()
            if parent_lib:
                search.add_filter('asset_library', parent_lib)
        elif "prod/shot" in search_type:
            lib_select = SelectWdg('parent_lib')
            lib_select.persistence = False
            search2 = Search("prod/sequence")
            lib_select.set_search_for_options( search2, "code", "code" )
            lib_select.add_empty_option("-- Any --")
            
            widget.add(lib_select)

            # get all of the options for this search type
            parent_lib = lib_select.get_value()
            if parent_lib:
                search.add_filter('sequence_code', parent_lib)
        elif 'prod/texture' in search_type:
            lib_select = SelectWdg('parent_lib')
            lib_select.persistence = False
            search2 = Search("prod/texture")
            search2.add_column('category')
            search2.add_group_by("category")
            lib_select.set_search_for_options( search2, "category", "category" )
            lib_select.add_empty_option("-- Any --")
            widget.add(lib_select)

            # get all of the options for this search type
            parent_lib = lib_select.get_value()
            if parent_lib:
                search.add_filter('category', parent_lib)
    
    def get_off_script(self):
        return "set_display_off(\\'%s\\')" %self.main_div.get_id()

class NoteUtilCmd(Command):

    MOVE = "MOVE"
    COPY = "COPY"
    EDIT = "EDIT"
    DEL = "DEL"
    STATUS = "STATUS"

    def get_title(self):
        return "NoteUtilCmd"

    def init(self):
        web = WebContainer.get_web()
        self.search_type = web.get_form_value("search_type")
        self.note_search_key = web.get_form_value('skey_note')
        self.note = Search.get_by_search_key(self.note_search_key)
        self.note_parent_search_key = web.get_form_value('skey_note_parent')
        self.note_parent = Search.get_by_search_key(self.note_parent_search_key)
        self.new_parent_search_key = web.get_form_value('skey_new_parent')
        self.note_new_parent = None
        self.action = web.get_form_value('note_action')
        self.edited_note = web.get_form_value('edited_note')
        self.status = web.get_form_value('note_status')

    def check(self):
        self.init()
        web = WebContainer.get_web()

        if self.edited_note and self.note:
            return True

        if self.new_parent_search_key:
            self.note_new_parent = Search.get_by_search_key(self.new_parent_search_key)
        
        elif self.action not in [self.DEL, self.STATUS]:
            raise UserException("Please select a new parent from the dropdown.")
        
        if not self.action:
            raise UserException("Unknown Action.")
            return False
        
        if not self.note or not self.note_parent:
            return False

        if not self.note_new_parent and self.action not in [self.DEL, self.STATUS] :
            raise UserException("The new parent does not exist [%s]" %self.new_parent_search_key)
            return False
        

        if self.note_parent_search_key == self.new_parent_search_key:
            raise UserException("The new parent is the same as current parent. Skipped.")
            return False
        return True

    def execute(self):
        if self.action == self.MOVE:
            self.note.set_sobject_value(self.note_new_parent)
            self.note.commit()
            self.sobjects = [self.note]
            # move the child notes as well
            child_notes = self.note.get_child_notes()
            for child_note in child_notes:
                child_note.set_sobject_value(self.note_new_parent)
                child_note.commit()
            self.add_description('Moved note [%s...] and replied notes from [%s] to [%s]' \
                    %(self.note.get_value('note')[:10], self.note_parent.get_code(), self.note_new_parent.get_code()))
        elif self.action == self.COPY:
            new_note = self.note.copy_note(self.note_new_parent)
            self.sobjects = [new_note] 
            # move the child notes as well
            child_notes = self.note.get_child_notes()
            for child_note in child_notes:
                child_note.copy_note(self.note_new_parent, new_note)

            self.add_description('Copied note [%s...] and replied notes from [%s] to [%s]' \
                %(self.note.get_value('note')[:10], self.note_parent.get_code(), self.note_new_parent.get_code()))
        elif self.action == self.EDIT:
            parent_code = self.note_parent.get_code()
            self.sobjects = [self.note]
            self.note.set_value('note', self.edited_note)
            self.note.commit()
            self.add_description('Edited note for [%s]' %(parent_code))

        elif self.action == self.DEL:
            value = self.note.get_value('note')
            parent_code = self.note_parent.get_code()
            self.sobjects = [self.note]
            self.note.delete()
            self.add_description('Deleted note [%s] from [%s]' %(value, parent_code))
            

        elif self.action == self.STATUS:
            self.note.set_value('status', self.status)
            self.note.commit()
            self.add_description('Changed status of a note')

    


class CommentAttr(object):

    def __init__(self, sobject, name):
        self.sobject = sobject
        self.name = name

        self.xml = self.sobject.get_xml_value(self.name, "discussion")

        self._extract_data()


    def _extract_data(self):
        self.nodes = self.xml.get_nodes("discussion/comment")


    def get_num_comments(self):
        return len(self.nodes)


    def get_comment_data(self, index):
        #return (self.users[index], self.dates[index], self.comments[index])
        user = Xml.get_attribute(self.nodes[index], "user")
        date = Xml.get_attribute(self.nodes[index], "date")

        # FIXME: Don't like this dependency on "childNodes"!
        comment = self.nodes[index].childNodes[0].nodeValue
        return user, date, comment


    def get_context(self, index):
        context = Xml.get_attribute(self.nodes[index], "context")
        return context



    def add_comment(self, comment, context=""):

        user = WebContainer.get_login().get_login()

        # compare this comment to the last one: avoiding the whole reload
        # problem
        num = self.get_num_comments()
        if num != 0:
            last_user, last_date, last_comment = self.get_comment_data(num-1)
            if user == last_user and comment == last_comment:
                return

        # get the latest snapshot for this asset
        snapshot = Snapshot.get_latest( \
                self.sobject.get_search_type(), self.sobject.get_id() )

        # get root
        doc = self.xml.get_doc()
        root = doc.documentElement

        # create a new comment element and add it to the root
        comment_element = self.xml.create_element("comment")
        Xml.set_attribute(comment_element, "user", user)
        Xml.set_attribute(comment_element, "date", time.asctime() )
        Xml.set_attribute(comment_element, "context", context)

        # relate this note to the latest snapshot
        if snapshot != None:
            Xml.set_attribute(comment_element, "snapshot_code", snapshot.get_code() )

        data_element = doc.createTextNode(comment)
        comment_element.appendChild(data_element)

        root.appendChild(comment_element)

        # commit it to the sobject
        self.sobject.set_value(self.name, self.xml.get_xml() )
        self.sobject.commit()

        self._extract_data()





    def remove_comment(self, index):
        """remove the comment located at a particular index"""
        doc = self.xml.get_doc()
        root = doc.documentElement
        nodes = self.xml.get_nodes("discussion/comment" )
        node = nodes[index]

        root.removeChild(node)

        # commit it to the sobject
        self.sobject.set_value(self.name, self.xml.get_xml() )
        self.sobject.commit()

        self._extract_data()



class CommentCmd(Command):


    def get_title(self):
        return "Add Note"


    def check(self):
        web = WebContainer.get_web()

        # get all of the relevant keys
        self.search_keys = []
        self.values = {}
        self.contexts = {}
        self.parent_ids = {}
        
        
        key = web.get_form_value('base_name')

        search_key = web.get_form_value('search_key')

        self.search_keys.append(search_key)
        # key is based on self.base_name defined in DiscussionWdg
        
        note_value = web.get_form_value(key)
        if not note_value:
            return False
        self.values[search_key] = note_value
        
        self.contexts[search_key] = web.get_form_value("%s_context" % key)
        self.parent_ids[search_key] = web.get_form_value("%s_parent" % key)
        if self.search_keys:
            return True
        else:
            return False




    def execute(self):
        if not self.search_keys:
            return

        # get all of the affected sobjects
        web = WebContainer.get_web()

        added = False
        for search_key in self.search_keys:
            value = self.values[search_key]
            # needed for filtering out other search key in the page
            if value == "":
                continue
            #value = r"%s" %value
            #value = re.sub(r"\\", "/", value)

            #value = value.replace("\\", "\\\\")


            context = self.contexts.get(search_key)
            if not context:
                # this should be illegal, raise a warning
                #context = web.get_form_value("discussion_context")
                Environment.add_warning('note context missing', \
                    'This note will not be entered.')
                continue
            # get parent_id 
            parent_id = self.parent_ids.get(search_key)
            sobject = Search.get_by_search_key(search_key)

            # for now, assume process = context
            process = None


            # this is for the new sobject implementation of notes
            note = Note.create(sobject, value, context, process=process, parent_id=parent_id)
            self.sobjects.append(note)

            self.info['context'] = context
            self.info['process'] = process
            self.info['search_key'] = search_key

            if not context:
                context = "main"
            self.description = "Note added: '%s' in the '%s' context" % (value, context)

            added = True

        #if not added:
        #    raise CommandExitException()

        

