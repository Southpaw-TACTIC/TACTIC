###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['DiscussionElementWdg', 'DiscussionWdg', 'DiscussionAddNoteWdg', 'DiscussionAddNoteCmd', 'NoteStatusEditWdg', 'NoteCollectionWdg']

from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg

from pyasm.common import Environment, TacticException, jsondumps, jsonloads, SPTDate, Common
from pyasm.biz import Pipeline, Project, File, IconCreator, Schema
from pyasm.command import Command, EmailTrigger2
from pyasm.web import DivWdg, Table, WikiUtil, HtmlElement, SpanWdg, Widget
from pyasm.search import Search, SearchType, SObject, SearchKey
from pyasm.widget import SwapDisplayWdg, CheckboxWdg, IconButtonWdg, IconWdg, TextWdg, TextAreaWdg, SelectWdg, ProdIconButtonWdg, HiddenWdg
from pyasm.biz import ProjectSetting
#from tactic.ui.panel import TableLayoutWdg
from tactic.ui.container import DialogWdg, MenuWdg, MenuItem, SmartMenu, Menu
from pyasm.security import Login
from pyasm.widget import ThumbWdg

import dateutil, os

from tactic.ui.widget.button_new_wdg import ActionButtonWdg, IconButtonWdg

class DiscussionElementWdg(BaseTableElementWdg):

    ARGS_KEYS = {

    'process': {
         'description': 'Explicitly set the process for notes that can be added.',
         'category': 'Options',
         'order': 0
     },
    
    'context': {
        'description': 'Explicitly set the context(s) for notes that can be added.  This can be a list separated by commas',
        'category': 'Options',
        'order': 1
    },
    'use_parent': {
        'description': 'Determine whether or not to enter notes for parent sObject',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 2
    }
    ,
    'show_fullscreen_button': {
        'description': 'Determine whether or not to show the expand notes icon button',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 3
    },
    'note_format': {
        'description': 'Determine if the notes are shown in compact or full mode. Full- shows thumbnail, login-info, email and notes. Compact- shows just the notes.',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'compact|full',
        'order': 4
    },

    'show_note_status': {
        'description': 'Determine whether or not to show the note status in abbreviated form.',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 5
    },
    # FIXME: need a better name for this
    'show_context_notes': {
        'description': '(DEPRECATED) Determine if the notes in the context are hidden',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 6
    },
    
    'note_expandable': {
        'description': 'Determine whether or not a note is expandable. True- shows a short version of the note that can be expanded. False- shows the full note',
        'category' : 'Options',
        'type' : 'SelectWdg',
        'values' : 'true|false',
        'order' : 7        
    },

    'append_process': {
        'description': 'Append a list of comma separated processes in addition of the ones defined in the pipeline',
        'category' : 'Options',
        'type' : 'TextWdg',
        'order' : 8        
    },

    'allow_email': {
        'description': 'Allow email to be sent out directly in this widget',
        'category' : 'Options',
        'type' : 'SelectWdg',
        'values' : 'true|false',
        'order': 9
    },

    'show_task_process': {
        'description': 'Determine if Add Note widget only shows the processes of existing tasks',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 10
    }

    }

  
   
    def is_editable(cls):
        return False
    is_editable = classmethod(is_editable)

    def handle_th(my, th, wdg_idx=None):

        #edit_wdg = DiscussionEditWdg()
        #my.menu = edit_wdg.get_menu()
        #th.add(edit_wdg)
        pass


    def get_width(my):
        mode = my.kwargs.get("mode")
        if mode == "icon":
            return 75
        else:
            return 150
       
   

    def handle_layout_behaviors(my, layout):
        # in case the note widget appears more than once in a table
        if my.parent_wdg:
            if my.parent_wdg.drawn_widgets.get(my.__class__.__name__) == True:
                return

            version = my.parent_wdg.get_layout_version()
            if version == "2":
                pass
            else:
                layout.add_smart_styles("spt_discussion_element_top", {
                    'margin': '-3px -4px -3px -6px',
                    'min-width': '300px'
                } )

        # extra js_action on mouseover to assign the search key of the note to hidden input
        js_action ='''
           var sk_input = menu_top.getElement('.spt_note_action_sk');
           var note_top = bvr.src_el
           sk_input.value = note_top.getAttribute('note_search_key');
            '''

        # disable the default activator
        # my.menu.set_activator_over(layout, 'spt_note_header', js_action=js_action)

        # add action triggle for context itself
        #my.menu.set_activator_over(layout, 'spt_note', js_action=js_action)
        #my.menu.set_activator_out(layout, 'spt_discussion_top')


        DiscussionWdg.add_layout_behaviors(layout, my.hidden, my.allow_email, my.show_task_process)
        


    def init(my):
        my.hidden = False
        my.allow_email = my.kwargs.get('allow_email') != 'false'
        my.show_task_process = my.kwargs.get('show_task_process') == 'true'
        my.discussion = DiscussionWdg(show_border='false', contexts_checked='false', add_behaviors=False,**my.kwargs)
        

    def get_required_columns(my):
        '''method to get the require columns for this'''
        return []

    def preprocess(my):
        parent =  my.get_parent_wdg()
        if parent and parent.kwargs.get('__hidden__') in [True, 'True']:
            my.discussion.kwargs['hidden'] = True
            my.hidden = True
           
        my.discussion.set_sobjects(my.sobjects)

    def set_sobjects(my, sobjects, search=None):
        my.discussion.set_sobjects(sobjects)
        my.discussion.notes_dict = None
        super(DiscussionElementWdg, my).set_sobjects(sobjects)

      
    def get_display(my):
        # setting the index so that the proper key is used for note retrieval
        idx = my.get_current_index()
        my.discussion.set_current_index(idx)
        top = DivWdg()
        top.add_class("spt_discussion_element_top")

        sobject = my.get_current_sobject()

        # this is usually not necessary since we call set_sobjects() in preprocess already
        # but on Edit of a note thru FingerMenu, it is needed
        my.discussion.kwargs['search_key'] = sobject.get_search_key()

        top.force_default_context_menu()
        top.add(my.discussion)


        return top



    def get_header_option_wdg(my):
        #div = DivWdg()
        #button = ActionButtonWdg(title="Expand")
        #div.add(button)
        #return div
        return None


    def get_text_value(my):
        '''for csv export'''

        from dateutil import parser
        comment_area = []
        
        idx = my.get_current_index()
        my.discussion.set_current_index(idx)

        my.discussion.preprocess_notes()

        notes = my.discussion.get_notes()
        
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
            date = note.get_value('timestamp')
            value = parser.parse(date)
            setting = "%Y-%m-%d %H:%M"
            date_value = value.strftime(setting)
            comment_area.append(note.get_value("login"))
            comment_area.append(date_value)
            comment_area.append(note.get_value("note"))
            comment_area.append('\n')
            if child_notes:
                for child_note in child_notes:
                    child_note_value = child_note.get_value('note')
                    comment_area.append( "Reply: %s" %child_note_value)
                    comment_area.append( '\n' )
        return ' '.join(comment_area)





class DiscussionWdg(BaseRefreshWdg):
    '''Special widget to add work hours'''

    HELP = "discussion-wdg"

    def init(my):
        my.process = my.kwargs.get("process") or ""
        my.contexts = []
        my.use_parent = my.kwargs.get('use_parent') 
        my._load_js = False

        my.notes_dict = None
        
        # we need to collect all the parents of the notes for preprocess search
        my.parent_dict = {}
        my.parents = []
        my.parent_processes = []
        my.append_processes = my.kwargs.get('append_process')
        my.custom_processes = my.kwargs.get('custom_processes')
        my.show_task_process = my.kwargs.get('show_task_process')
        
        my.allow_email = my.kwargs.get('allow_email')
        





    def get_onload_js(my):
        return '''
        spt.discussion = {};
        spt.discussion.refresh = function(src_el) {
            var discussion_top = spt.has_class(src_el, 'spt_discussion_top') ? src_el: src_el.getParent(".spt_discussion_top");

            // find out which contexts are open
            var contexts = discussion_top.getElements(".my_context");
            var default_contexts_open = [];
            for (var i = 0; i < contexts.length; i++) {
                if (contexts[i].getAttribute("spt_state") == 'open') {
                    var context = contexts[i].getAttribute("my_context");
                    if (context.strip())
                        default_contexts_open.push(context);
                }
            }

            var top = discussion_top;
           
            var dialog_content = top.getElement(".spt_discussion_content");
            var group_top = dialog_content ? dialog_content.getParent(".spt_discussion_context_top") : null;

            // refresh the dialog and the note count for this context
            if (group_top && group_top.getAttribute("spt_is_loaded") == "true") {
                var parent_key = dialog_content.getAttribute('spt_parent_key');
                var class_name = 'tactic.ui.widget.NoteCollectionWdg';
                var kwargs = {
                    parent_key: parent_key,
                    context: dialog_content.getAttribute('spt_context'),
                    default_num_notes: dialog_content.getAttribute('spt_default_num_notes'),
                    note_expandable: dialog_content.getAttribute('spt_note_expandable'),
                    note_format: dialog_content.getAttribute('spt_note_format')
                }

                // clear textarea and toggle add widget
                var text = top.getElement('textarea[@name=note]');
                if (text)
                    text.value = '';
                var add_note = top.getElement(".spt_discussion_add_note");
                if (add_note)
                    spt.toggle_show_hide(add_note);

                // update dialog
                
                spt.panel.load(dialog_content, class_name, kwargs, {}, {is_refresh: 'true'});
               
                // update note count
                var note_count_div = group_top.getElement('.spt_note_count');
                if (note_count_div) {

                    var s = TacticServerStub.get();
                    var note_count = s.eval('@COUNT(sthpw/note)', {search_keys: [parent_key]});
                    note_count_div.innerHTML = '(' + note_count + ')';
                }

            }
            else {
                spt.panel.refresh(top, {default_contexts_open: default_contexts_open, is_refresh: 'true'});
            }

        }'''



    def add_layout_behaviors(cls, layout, hidden=False, allow_email=True, show_task_process=False):
        '''hidden means it's a hidden row table'''
        
        layout.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_note_attachment',
            'cbjs_action': '''
            var code_str = bvr.src_el.getAttribute("spt_note_attachment_codes");
            var server = TacticServerStub.get();
            var codes = code_str.split("|");
            for (var i = 0; i < codes.length; i++) {
                // get the files for this snapshot
                var path = server.get_path_from_snapshot(codes[i], {mode:'web'});
                window.open(path);
            }
            '''
        } )



        match_class = cls.get_note_class(hidden, 'spt_discussion_add')
        layout.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': match_class,
            'hidden': hidden,
            'allow_email': allow_email,
            'show_task_process': show_task_process,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_dialog_top");
            if (top == null) {
                top = bvr.src_el.getParent(".spt_discussion_top");
            }

            var container = top.getElement(".spt_add_note_container");
            var add_note = container.getElement(".spt_discussion_add_note");

            if (! add_note) {
                var kwargs = container.getAttribute("spt_kwargs");
                kwargs = kwargs.replace(/'/g, '"');
                kwargs = JSON.parse(kwargs);

                if (spt.table) {
                    var layout = spt.table.get_layout();
                    var upload_id = layout.getAttribute('upload_id')
                    kwargs.upload_id = upload_id; 
                }
                kwargs.hidden = bvr.hidden;
                kwargs.allow_email = bvr.allow_email;
                kwargs.show_task_process = bvr.show_task_process;
                var class_name = 'tactic.ui.widget.DiscussionAddNoteWdg';
                spt.panel.load(container, class_name, kwargs, {},  {fade: false, async: false});
                add_note = top.getElement(".spt_discussion_add_note");
            }
            
            if (bvr.src_el.getAttribute('force_show') == 'true')
                spt.show(add_note);
            else
                spt.toggle_show_hide(add_note);

            //new Fx.Tween(add_note,{duration:"short"}).start('margin-top', 0);

            // select the appropriate context or process
            var select = add_note.getElement(".spt_add_note_process");
            if (select) {
                var process = bvr.src_el.getAttribute("spt_process");
                var context = bvr.src_el.getAttribute("spt_context");

                var match = process ? process : context;
                for(var i = 0; i < select.options.length; i++) {
                  
                    if (select.options[i].value == match) {
                        select.selectedIndex = i;
                        break;
                    }
                }
            }

            '''
            } )


        # DEPRECATED?
        # for expand note widget
        layout.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_discussion_expand',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_discussion_top");
            var float = top.getElement(".spt_float");
            var clone = spt.behavior.clone(top);

            expand = clone.getElement(".spt_discussion_expand");
            spt.hide(expand);

            var code = bvr.src_el.getAttribute('code')
            var title = "Notes: " + code;
            var element_name = bvr.src_el.getAttribute('search_key')

            spt.tab.set_main_body_tab();
            spt.tab.add_new(element_name, title);
            spt.tab.load_node(element_name, clone);
            spt.tab.select(element_name);


            var notes = clone.getElements(".spt_note_content");
            for ( var i = 0; i < notes.length; i++ ) {
                spt.show( notes[i] );
            }

            '''
            } )

        submit_class = cls.get_note_class(hidden, 'spt_discussion_submit') 
        # for the Submit button
        layout.add_relay_behavior( {
        'type': 'mouseup',
        'bvr_match_class': submit_class,
        'cbjs_action': '''

        var note_top = bvr.src_el.getParent(".spt_add_note_top");
        var values = spt.api.get_input_values(note_top, null, false);
        if (values.note == '') {
            spt.alert("Please enter a note before saving");
        }
        else {
            spt.app_busy.show("Adding note ...");

            var top = bvr.src_el.getParent(".spt_discussion_add_note");
            var attach_top = top.getElement(".spt_attachment_top");
            var ticket_key = attach_top.getAttribute('ticket_key');
            var files = attach_top.files;
            var server = TacticServerStub.get();
            if (!ticket_key)
                server.start({title: 'New Note', transaction_ticket: ticket_key});

            if (typeof(files) != 'undefined') {
                /*
                for (var i = 0; i < files.length; i++) {
                    spt.app_busy.show("Uploading ...", files[i]);
                    server.upload_file(files[i], ticket_key);
                }
                */
                spt.app_busy.hide()

                values['files'] = files;
                values['ticket'] = ticket_key;
            }
            else {
                values['files'] = [];
            }
            // rename add_process and add_context for the Cmd
            var process = values.add_process;
            values['process'] = process;
            var context = values.add_context;
            values['context'] = context;
            delete values.add_process;
            delete values.add_context;

            var cmd = 'tactic.ui.widget.DiscussionAddNoteCmd';
            
            try{
                server.execute_cmd(cmd, values);
                server.finish();
            }
            catch (e) {
                spt.alert(spt.exception.handler(e));
                server.abort();
            }

            spt.discussion.refresh(top);

            spt.app_busy.hide();
        }
        '''
        })



        layout.add_relay_behavior( {
            'type': 'click',
            'width': "",
            'align': "",
            'bvr_match_class': 'spt_open_thumbnail',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_discussion_top");
            var tile_tops = top.getElements(".spt_open_thumbnail");


            var search_keys = [];
            for (var i = 0; i < tile_tops.length; i++) {
                var tile_top = tile_tops[i];
                var tile_top = tile_top.getFirst();
                var search_key = tile_top.getAttribute("spt_search_key_v2");
                var search_key = tile_top.getAttribute("id");
                search_key = search_key.replace("thumb_", "");
                search_keys.push(search_key);
            }

            var tile_top = bvr.src_el;
            var tile_top = tile_top.getFirst();
            var search_key = tile_top.getAttribute("spt_search_key_v2");
            var search_key = tile_top.getAttribute("id");
            search_key = search_key.replace("thumb_", "");

            var class_name = 'tactic.ui.widget.gallery_wdg.GalleryWdg';
            var kwargs = {
                search_keys: search_keys,
                search_key: search_key,
                align: bvr.align
            };
            if (bvr.width) 
                kwargs['width'] = bvr.width;
            var gallery_el = top.getElement(".spt_note_gallery");
            spt.panel.load(gallery_el, class_name, kwargs);

            '''
        } )



    add_layout_behaviors = classmethod(add_layout_behaviors)




    def _get_parent(my, sobject):
        '''caching is automatically done in SObject level''' 
        parent = sobject.get_parent()
        return parent

    def get_note_class(cls, hidden, cls_name):
        ''' An attempt to separate the main table relay and hidden table relay. Otherwise it will toggle twice making it look like the button doesn't work'''
        if hidden == True:
            return '%s_hidden'%cls_name
        else:
            return cls_name

    get_note_class = classmethod(get_note_class)

    def preprocess_notes(my):
        '''this call get_all_notes once by design to build the dict''' 
        # this check stops this method from being called more than once per table
        insert_mode = False
        if len(my.sobjects) == 1 and my.sobjects[0].is_insert():
            insert_mode = True
            my.notes_dict = {}

        if my.notes_dict != None or insert_mode:
            return my.notes_dict 
        # collect my.parents 
        # use_parent and sobject option are mutually exclusive for now 
        # I think this is only used for a single object view with notes
        my.parent = my.kwargs.get("sobject")
        if not my.parent:
            if my.sobjects:
                has_process = my.sobjects[0].has_value('process')
                if my.use_parent == 'true':

                    for sobject in my.sobjects:
                        process = ''
                        if has_process:
                            process = sobject.get_value('process')
                        # this is used in the key for note_dict
                        my.parent_processes.append(process)
                        parent = my._get_parent(sobject)
                        # must append even if it is None
                        my.parents.append(parent)
                else:
                    my.parents = my.sobjects
            else: # indiviual update     
                search_key = my.kwargs.get("search_key")
                assert search_key
                my.parent = Search.get_by_search_key(search_key)
                # this is required for refresh
                has_process = my.parent.has_value('process')
                my.sobjects = [my.parent]
                if my.use_parent == 'true':
                    process = ''
                    if has_process:
                        process = my.parent.get_value('process')
                    # this is used in the key for note_dict
                    my.parent_processes.append(process)
                    
                    parent = my.parent.get_parent()
                    # must append even if it is None
                    my.parents.append(parent)
                else:
                    my.parents = [my.parent]
        else:
            my.parents = [my.parent]


        # append processes can't be used in conjuntion with use_parent when it has_process
        # in this case since this is meant for task or snapshot notes
        if has_process and my.use_parent =='true':
           my.append_processes = ''
           my.custom_processes = ''

       

        if my.use_parent == 'true':
            pass
          
        else:
            my.process = my.kwargs.get("process")

            # TODO: this needs to be eval to be a list if it's a comma separated string
            my.contexts = my.kwargs.get("context")
            if my.contexts and isinstance(my.contexts, basestring):
                my.contexts = my.contexts.split(',')
                my.contexts =[x.strip() for x in my.contexts if x.strip()]

        
        my.get_all_notes()


    def get_all_notes(my):
        ''' this is called by get_notes() in the very first get_display() since we dont have preprocess for BaseRefreshWdg'''
       

        my.notes_dict = {}

        # maintain index but we want to filter out deleted parents (None)
        my.filtered_parents = [p for p in my.parents if p]
        search = Search("sthpw/note") 
        search.add_relationship_filters(my.filtered_parents, type='hierarchy')
        search.add_order_by("process")
        search.add_order_by("timestamp desc")

        if my.process:
            search.add_op("begin")
            search.add_filter("process", my.process)
            search.add_filter("process", "%s/%%" % my.process, op="like")
            search.add_op("or")

        if my.contexts:
            search.add_filters("context", my.contexts)

        notes = search.get_sobjects()
        has_process = my.sobjects[0].has_value('process')
        schema = Schema.get()

        for note in notes:

            """
            search_type = note.get_value("search_type")
            #search_id = note.get_value("search_id")
            search_code = note.get_value("search_code")
            if my.use_parent == 'true' and has_process:
                process = note.get_value("process")
                key = "%s|%s|%s" % (search_type, search_code, process)
            else:
                key = "%s|%s" % (search_type, search_code)
            """

            if my.use_parent in ['true', True] and has_process:
                process = note.get_value("process")
            else:
                process = "publish"

            # NOTE: this could be an issue if the process contains a "/" init
            if process.endswith("/review") or process.endswith("/error"):
                process = process.split("/")[0]

            search_type = note.get_value("search_type")

            attrs = schema.get_relationship_attrs("sthpw/note", search_type)
            attrs = schema.resolve_relationship_attrs(attrs, "sthpw/note", search_type)
            from_col = attrs.get("from_col")
            to_col = attrs.get("to_col")

            search_code = note.get_value(from_col)
            if search_code:
                key = "%s|%s|%s" % (search_type, search_code, process)
            else:
                continue


            notes_list = my.notes_dict.get(key)
            if notes_list == None:
                notes_list = []
                my.notes_dict[key] = notes_list
            notes_list.append(note)


        my.attachments = {}


        return my.notes_dict
  
    
           
   
    def get_notes(my):
        my.preprocess_notes()
        # this is -1 for a single sobject refresh like after an edit, which works like 0
        idx = my.get_current_index()

        # getting sobj here instead of using my.parent since my.parent could change with the use_parent option
        my.sobject = my.sobjects[idx]
        my.parent = None
        if my.sobject.is_insert():
            return []


        my.parent = my.parents[idx]
        has_process = my.sobject.has_value('process')

        if not my.parent:
            key = ""
        else:
            search_type = my.parent.get_search_type()

            from pyasm.biz import Schema
            schema = Schema.get()
            attrs = schema.get_relationship_attrs("sthpw/note", search_type)
            attrs = schema.resolve_relationship_attrs(attrs, "sthpw/note", search_type)
            from_col = attrs.get("from_col")
            to_col = attrs.get("to_col")
            search_code = my.parent.get_value(to_col)

            #database_type = my.parent.get_database_type()
            #if database_type == "MongoDb":
            #    search_code = my.parent.get_id()
            #else:
            #    search_code = my.parent.get_code()

            if my.use_parent == 'true':
                parent_process = my.parent_processes[idx]
                if has_process:
                    key = "%s|%s|%s" % (search_type, search_code, parent_process)
                else:
                    key = "%s|%s|publish" % (search_type, search_code)
            else:
                key = "%s|%s|publish" % (search_type, search_code)


        notes = my.notes_dict.get(key)
        if not notes:
            notes = []





        # not very efficient, but filter notes afterwards
        security = Environment.get_security()
        project_code = Project.get_project_code()
        allowed = []
        for note in notes:
            process = note.get_value("process")
            keys = [
                    {"process": process},
                    {"process": "*"},
                    {"process": process, "project": project_code},
                    {"process": "*", "project": project_code}
            ]
            if security.check_access("process", keys, "allow", default="deny"):
                allowed.append(note)

        return allowed


    
    def load_js(my, ele):
        '''add load bvr to the widget at startup or refresh'''
        ele.add_behavior({'type': 'load',
            'cbjs_action': my.get_onload_js()})
        my._load_js = True





    def get_display(my):
        
        my.is_refresh = my.kwargs.get("is_refresh")

        my.hidden = my.kwargs.get('hidden') == True 
        
        mode = my.kwargs.get("mode")

        my.show_border = my.kwargs.get("show_border")
        if my.show_border in ['false', False]:
            my.show_border = False
        else:
            my.show_border = True


        my.contexts_checked = my.kwargs.get("contexts_checked")
        if my.contexts_checked in ['false', False]:
            my.contexts_checked = False
        else:
            my.contexts_checked = True


        # explicitly set the contexts
        my.contexts = my.kwargs.get("context")

        # this should be maintained as a list
        if not my.contexts:
            my.contexts = []
        if my.contexts:
            my.contexts = my.contexts.split(",")
            # remove any spaces
            my.contexts = [x.strip() for x in my.contexts]
       


        # show context header
        my.show_context_header = my.kwargs.get("show_context_header")
        if my.show_context_header in ['true', True]:
            my.show_context_header = True
        else:
            my.show_context_header = False

            

        # show the number of notes that will start open.  default is 0
        my.default_num_notes = my.kwargs.get("default_num_notes")
        if my.default_num_notes:
            my.default_num_notes = int(my.default_num_notes)
        else:
            my.default_num_notes = 0

        show_fullscreen_button = my.kwargs.get("show_fullscreen_button")
        if show_fullscreen_button in ['true', True]:
            show_fullscreen_button = True
        else:
            show_fullscreen_button = False

        my.note_expandable = my.kwargs.get("note_expandable")
        
        my.note_format = my.kwargs.get("note_format")

        if my.note_format in ['', None]:
            #my.note_format = 'compact'
            my.note_format = 'full'

        my.show_note_status = my.kwargs.get("show_note_status")
        if my.show_note_status in ['true', True]:
            my.show_note_status = True
            my.note_status_dict = ProjectSetting.get_dict_by_key('note_status')
        else:
            my.show_note_status = False

        #my.default_contexts_open = my.kwargs.get("default_contexts_open")
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        my.default_contexts_open = web.get_form_values("default_contexts_open")
        if not my.default_contexts_open:
            my.default_contexts_open = my.kwargs.get("default_contexts_open")
        if not my.default_contexts_open:
            my.default_contexts_open = []



        notes = my.get_notes()

        # group notes under contexts
        contexts = []
        context_notes = {}
        process_notes = {}
        last_context = None
        last_process = None
        for i, note in enumerate(notes):
            context = note.get_value("context")
            process = note.get_value("process")

            if last_context == None or context != last_context:
                contexts.append(context)
            
            note_list = context_notes.get(context)
            if note_list == None:
                note_list = []
                context_notes[context] = note_list
            note_list.append(note)

            note_list = process_notes.get(process)
            if note_list == None:
                note_list = []
                process_notes[process] = note_list
            note_list.append(note)


            last_context = context
            last_process = process


        if my.is_refresh =='true':
            top = DivWdg()
        else:
            top = DivWdg()
            if not my._load_js:
                my.load_js(top)
            
                if my.kwargs.get("add_behaviors") != False:
                    my.add_layout_behaviors(top, allow_email=my.allow_email, show_task_process=my.show_task_process)


            # add a refresh listener
            top.add_class("spt_discussion_top")
            my.set_as_panel(top)
            if mode != "icon":
                top.add_style("min-width: 300px")


            max_height = my.kwargs.get("max_height")
            if max_height:
                top.add_style("overflow: auto")
                top.add_style("max-height: %spx" % max_height)


            gallery_div = DivWdg()
            gallery_div.add_class("spt_note_gallery")
            top.add( gallery_div )


        context_str = ",".join(contexts)
        update_div = DivWdg()
        top.add(update_div)

        search_key = my.kwargs.get("search_key")
        # check for changes in the context_str
        update_div.add_update( {
            'search_key': search_key,
            'compare': "@JOIN(@UNIQUE(@GET(sthpw/note.context)), ',') == '%s'" % context_str,
            'cbjs_postaction': '''
            var top = bvr.src_el.getParent(".spt_discussion_top");
            spt.panel.refresh(top);
            '''
        } )

        
        stype = 'sthpw/note'
        expr_key = None
        if my.use_parent == 'true':
            idx = my.get_current_index()
            # when the sobject is in insert mode, it doesn't have parent
            if my.parent:
                expr_key = my.parent.get_search_key()
        else:
            expr_key = search_key

        if expr_key:
            update_div.add_update( {
                   "search_type": stype,
                   'compare': "@COUNT(sthpw/note) == %s" %len(notes),
                   'expr_key': expr_key,
                   'interval': 2,
                   "cbjs_action": '''
                var top = bvr.src_el.getParent(".spt_discussion_top");
                var dialog_content = top.getElement(".spt_discussion_content");

                var group_top = dialog_content ? dialog_content.getParent(".spt_discussion_context_top") : null;
                
                // update dialog and the count if dialog is visible 
                if (group_top && group_top.getAttribute("spt_is_loaded") == "true") {
                    var parent_key = dialog_content.getAttribute('spt_parent_key');
                    var class_name = 'tactic.ui.widget.NoteCollectionWdg';
                    var kwargs = {
                        parent_key: parent_key,
                        context: dialog_content.getAttribute('spt_context'),
                        default_num_notes: dialog_content.getAttribute('spt_default_num_notes'),
                        note_expandable: dialog_content.getAttribute('spt_note_expandable'),
                        note_format: dialog_content.getAttribute('spt_note_format')
                    }
                    spt.panel.load(dialog_content, class_name, kwargs, {}, {is_refresh: true});
                    var note_count_div = group_top.getElement('.spt_note_count');
                    
                    var s = TacticServerStub.get();
                    var note_count = s.eval('@COUNT(sthpw/note)', {search_keys: [parent_key]});
                    note_count_div.innerHTML = '(' + note_count + ')';

                }
                else {
                    spt.panel.refresh(top);
                }


                '''
            })


        if my.use_parent == 'true' and not notes and not my.parent:
            sobj = my.parent
            if my.sobject.is_insert():
                return top
            if sobj:
                st_obj = sobj.get_search_type_obj()
                msg = 'Warning: The parent of this [%s] cannot be found. If this happens for every item, try not to set the display option [use_parent] to true.' % st_obj.get_title()
            else:
                msg = 'Warning: The parent cannot be found for this sObject. If this happens for every item, try not to set the display option [use_parent] to true.'
            top.add(msg)
            top.add_style("padding: 5px")
            return top

        if my.sobject.is_insert():
            return top

        code = my.parent.get_code()
       
        sobj = my.sobject
        has_process = my.sobject.has_value('process')
        has_context = my.sobject.has_value('context')

        if notes:
            expand_div = DivWdg()

            # FIXME: this is current broken because of the dialogs on notes
            show_fullscreen_button = False
            if show_fullscreen_button:
                top.add(expand_div)
                expand_div.add_class("spt_discussion_expand")
                #expand_div.add_style("float: right")
                expand_div.add_style("margin: -2px 3px 2px 3px")
                expand_div.add_style("margin-right: 3px")

                expand_wdg = IconButtonWdg(title="Expand in new tab", icon=IconWdg.ZOOM)
                expand_div.add(expand_wdg)

                expand_div.add_attr('code', code)
                expand_div.add_attr('search_key', my.parent.get_search_key())




        # This only shows up if there are no notes
        else:
            no_notes_div = DivWdg()

            top.add(no_notes_div)
            if my.show_border:
                no_notes_div.add_color("background", "background")
                no_notes_div.add_color("color", "color")
            no_notes_div.add_style("padding", "0px 5px")

  
            add_class = my.get_note_class(my.hidden, 'spt_discussion_add') 

            no_notes_msg = DivWdg()
            no_notes_msg.add_style("opacity: 0.5")
            no_notes_msg.add_style("min-height: 18px")
            no_notes_div.add(no_notes_msg)


            if mode == "icon":
                add_wdg = IconWdg("Add Note", "BS_PENCIL")
                no_notes_msg.add(add_wdg)
                if len(notes):
                    no_notes_msg.add("<i> (%s) </i>" % len(notes))

            else:
                add_wdg = IconWdg("Add Note", "BS_PLUS", size=12)
                no_notes_msg.add(add_wdg)
                add_wdg.add_style("display: inline-block")
                msg = "No notes."
                no_notes_msg.add("<div style='display: inline-block'><i> %s </i></div>" % _(msg))
                no_notes_div.add_style("font-size: 0.9em")
            no_notes_div.add_class("hand")



            no_notes_msg.add_class(add_class)
            # force the add textarea to show in js
            no_notes_msg.add_attr("force_show", "true")
          
            # only pass in the context choices if has_process is true e.g. for Task and Snapshot notes
            if my.contexts:
                context_choices = my.contexts
            elif has_process and has_context:
                context_choices = [sobj.get_value('context')]
            else:
                context_choices = []

            process_choice = ''
            if my.process:
                process_choice = my.process
            elif has_process:
                process_choice = sobj.get_value('process')

            
            sk = my.parent.get_search_key(use_id=True)
            if isinstance(sk, unicode):
                sk = sk.encode('utf-8')
            
            kwargs = {
                    'search_key': sk,
                    'context': context_choices,
                    'process': process_choice,
                    'use_parent': my.use_parent,
                    'append_process': my.append_processes,
                    'custom_processes': my.custom_processes
            }


            note_dialog = DialogWdg(display=False)
            note_dialog.add_style("font-size: 12px")
            note_dialog.add_title("Add Note")
            note_dialog.add_style("overflow-y: auto")
            no_notes_div.add(note_dialog)
            #note_dialog.set_as_activator(no_notes_msg, offset={'x':-5,'y':0})
            note_dialog.set_as_activator(no_notes_msg, position="right")

            add_note_wdg = DivWdg()
            add_note_wdg.add_class("spt_add_note_container")
            add_note_wdg.add_attr("spt_kwargs", jsondumps(kwargs).replace('"',"'"))

            
            #no_notes_div.add(add_note_wdg)
            note_dialog.add(add_note_wdg)


            return top

        # calculate the number for each context
        my.context_counts = {}
        my.process_counts = {}
        for note in notes:
            process = note.get_value("process")
            context = note.get_value("context")
            count = my.context_counts.get(context)
            if count == None:
                count = 1
            else:
                count += 1 
            my.context_counts[context] = count

            count = my.process_counts.get(process)
            if count == None:
                count = 1
            else:
                count += 1 
            my.process_counts[process] = count





        if my.show_context_header:
            contexts = set()
            for note in notes:
                context = note.get_value("context")
                contexts.add(context)
            contexts_div = DivWdg()
            contexts_div.add_color("color", "color")
            if my.show_border:
                contexts_div.add_border()
            top.add(contexts_div)
            for context in contexts:
                checkbox = CheckboxWdg("context")
                #if my.contexts_checked:
                checkbox.set_checked()
                checkbox.add_behavior( {
                'type': 'change',
                'context': context,
                'cbjs_action': '''

                var value = bvr.src_el.checked;
                var top = bvr.src_el.getParent(".spt_discussion_top");
                var contexts = top.getElements(".my_context");
                for (var i = 0; i < contexts.length; i++) {
                    if (contexts[i].getAttribute("my_context") == bvr.context) {
                        if (value == true) {
                            spt.show(contexts[i]);
                        }
                        else {
                            spt.hide(contexts[i]);
                        }
                    }
                }

                var notes = top.getElements(".spt_note");
                for (var i = 0; i < notes.length; i++) {
                    if (notes[i].getAttribute("my_context") == bvr.context) {
                        if (value == true) {
                            spt.show(notes[i]);
                        }
                        else {
                            spt.hide(notes[i]);
                        }

                    }
                }
 

                '''
                } )
                contexts_div.add(checkbox)
                contexts_div.add(context)
                contexts_div.add("&nbsp;"*3)
            
        #if mode == "icon":
        #    contexts = contexts[:1]

        # go through every process and display notes.
        #for context in contexts:
        for process in process_notes:
            #notes_list = context_notes.get(context)

            # This widget used to be context centric ... it is now process centric
            # ... for now, make the context variable equal to process
            context = process
            notes_list = process_notes.get(context)

            note_keys = []
            for note in notes_list:
                note_key = note.get_search_key()
                note_keys.append(note_key)

            count = len(notes_list)


            # get the last context
            if count:
                last_context = notes_list[0].get("context")
            else:
                last_context = process



            context_top = DivWdg()
            context_top.add_class("spt_discussion_context_top")
            context_top.add_class("my_context")
            context_top.add_class("hand")
            #context_top.add_class("hand")
            context_top.add_attr("my_context", context.encode('utf-8'))
            top.add(context_top)

            if context not in my.default_contexts_open:
                context_top.add_attr("spt_state", 'closed')

            if mode == "icon":
                if last_context.endswith("/review") or last_context.endswith("/error"):
                    context_wdg = IconWdg("View '%s' notes" % context, "BS_FLAG")
                    context_wdg.add_style("color: rgb(232, 74, 77)")
                    context_wdg.add_style("margin-top: 2px")
                    context_top.add("<div style='height: 3px'></div>")
                else:
                    context_wdg = IconWdg("View '%s' notes" % context, "BS_PENCIL")

                context_top.add(context_wdg)
                if count:
                    context_top.add("<i> (%s) </i>" % count)

                context_wdg.add_style("margin-left: 5px")


            else:
                context_wdg = IconWdg("View '%s' notes" % context, "BS_PENCIL", size="12")
                context_top.add(context_wdg)
                context_wdg.add_style("float: left")

                # process arg is meaningless
                context_wdg = my.get_context_wdg(process, context, count)

                context_top.add(context_wdg)
                context_top.add_style("min-width: 300px")
                if last_context.endswith("/review") or last_context.endswith("/error"):
                    context_wdg.add_style("color: #F00")


            if my.contexts:
                context_choices = my.contexts
            elif has_process and has_context:
                context_choices = [sobj.get_value('context')]
            else:
                context_choices = []

            process_choice = ''
            if my.process:
                process_choice = my.process
            elif has_process:
                process_choice = sobj.get_value('process')
                       

            context_count = 0

            note_dialog_div = DivWdg()
            context_top.add(note_dialog_div)
            note_dialog_div.add_style("font-size: 12px")
           
            note_dialog = DialogWdg(display=False)
            note_dialog_div.add(note_dialog)
            note_dialog.add_title("Notes for: %s" % context)
            note_dialog.add_style("overflow-y: auto")
            #note_dialog.set_as_activator(context_wdg, offset={'x':0,'y':0})
            note_dialog.set_as_activator(context_wdg, position="right")


            show_add = my.kwargs.get("show_add")
            if show_add not in ['false', False]:

                shelf_wdg = DivWdg()
                note_dialog.add(shelf_wdg)
                shelf_wdg.add_style("height: 36px")
                #shelf_wdg.add_color("background", "background3")

                add_wdg = ActionButtonWdg(title="+", title2="-", tip='Add a new note', size='small', opacity=0.7)
                shelf_wdg.add(add_wdg)
                add_wdg.add_style("float: right")
                shelf_wdg.add_style("padding-top: 3px")

                add_wdg.add_attr("spt_process", process)
                add_wdg.add_attr("spt_context", context)
                add_class = my.get_note_class(my.hidden, 'spt_discussion_add') 
                add_wdg.add_class(add_class)

                sk = my.parent.get_search_key(use_id=True)
                if isinstance(sk, unicode):
                    sk = sk.encode('utf-8')


                kwargs = {
                        'search_key': sk,
                        'context': context_choices,
                        'process': process_choice,
                        'use_parent': my.use_parent,
                        'append_process': my.append_processes,
                        'custom_processes': my.custom_processes
                }

                add_note_wdg = DivWdg()
                add_note_wdg.add_class("spt_add_note_container")
                add_note_wdg.add_attr("spt_kwargs", jsondumps(kwargs).replace('"',"'"))
                note_dialog.add(add_note_wdg)

                from tactic.ui.panel import ThumbWdg2
                thumb_wdg = ThumbWdg2()
                thumb_wdg.set_sobject(my.sobject)
                thumb_wdg.add_style("width: 60px")
                thumb_wdg.add_style("margin: 0px 5px")
                shelf_wdg.add(thumb_wdg)



            content = DivWdg()
            note_dialog.add(content)
            content.add_style("min-width: 300px")
            content.add_style("min-height: 150px")
            content.add_class("spt_discussion_content")
            content.add_color("background", "background")
            
            # context and parent_key are for dynamic update
            context_wdg.add_behavior( {
                'type': 'click',
                'note_keys': note_keys,
                'default_num_notes': my.default_num_notes,
                'note_expandable': my.note_expandable,
                'note_format': my.note_format,
                'context': context,
                'parent_key': my.parent.get_search_key(),
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_discussion_context_top");
                if (top.getAttribute("spt_is_loaded") == "true") {
                    return;
                }

                var class_name = 'tactic.ui.widget.NoteCollectionWdg';
                var kwargs = {
                    note_keys: bvr.note_keys,
                    default_num_notes: bvr.default_num_notes,
                    note_expandable: bvr.note_expandable,
                    note_format: bvr.note_format,
                    context: bvr.context,
                    parent_key: bvr.parent_key
                }

                var el = top.getElement(".spt_discussion_content");
                spt.panel.load(el, class_name, kwargs);

                top.setAttribute("spt_is_loaded", "true");

                '''
            } )

        return top



    def get_context_wdg(my, process, context, count):
        ''' this is drawn per process/context group of notes'''
        div = DivWdg()
        div.add_class("hand")


        icon_div = SpanWdg()
        # NOTE: removing this from now ....
        #div.add(icon_div)
        icon_div.add_border()
        icon_div.add_style("width: 16px")
        icon_div.add_style("height: 16px")
        icon_div.add_style("overflow: hidden")
        icon_div.add_style("margin-right: 5px")
        icon_div.add_style("float: left")

        icon = IconWdg( "View", IconWdg.ARROWHEAD_DARK_DOWN)
        icon_div.add(icon)



        div.add_color("color", "color")
        div.add_style("padding", "0px 0px 5px 5px")
        #div.add_color("background", "background", -5, -5)
        div.add_style("height", "15px")
        div.add_style("font-weight", "bold")
        #div.add_style("margin-bottom", "-1px")
        div.add_style("border-width: 0px 0px 0px 0px")
        div.add_style("border-style: solid")
        div.add_color("border-color", "table_border")
        if not context:
            display_context = '<i>(no context)</i>'
        elif context == "publish":
            display_context = "Notes"
        else:
            display_context = context
        div.add(display_context)

        count_div = SpanWdg(css="spt_note_count")
        div.add(count_div)
        count_div.add("(%s)" % count)
        count_div.add_style("font-weight: normal")
        count_div.add_style("font-size: 1.0em")
        count_div.add_style("font-style: italic")
        count_div.add_style("margin-left: 3px")

        #count_div.add_update( {
        #    'search_key': my.kwargs.get("search_key"),
        #    'expression': "({@COUNT(sthpw/note['context','%s'])})" % context,
        #} )

        return div




class NoteCollectionWdg(BaseRefreshWdg):

    def get_display(my):
        notes = my.kwargs.get("notes")
        note_keys = my.kwargs.get("note_keys")
        parent_key = my.kwargs.get("parent_key")
        context = my.kwargs.get("context")
        process = my.kwargs.get("process")

        if note_keys:
            notes = Search.get_by_search_keys(note_keys)
            parent = Search.get_by_search_key(parent_key)
        elif parent_key:
            # during dynamic update, parent_key and context are used
            parent = Search.get_by_search_key(parent_key)
            if context:
                notes = Search.eval("@SOBJECT(sthpw/note['context','%s'])"%context, sobjects=[parent])
            elif process:
                notes = Search.eval("@SOBJECT(sthpw/note['process','%s'])"%process, sobjects=[parent])
            else:
                notes = Search.eval("@SOBJECT(sthpw/note['context','%s'])"%context, sobjects=[parent])

            
        if not notes:
            return my.top

        my.default_num_notes = my.kwargs.get("default_num_notes")
        my.note_expandable = my.kwargs.get("note_expandable")
        my.show_note_status = my.kwargs.get("show_note_status")

        my.attachments = my.kwargs.get("attachments")


        if my.attachments == None:

            from pyasm.biz import Snapshot

            my.attachments = {}

            snapshots = Snapshot.get_by_sobjects(notes)
            for snapshot in snapshots:
                note_key = snapshot.get_parent_search_key()
                xx = my.attachments.get(note_key)
                if not xx:
                    xx = []
                    my.attachments[note_key] = xx
                xx.append(snapshot)



            if True and parent:

                """
                search = Search("sthpw/snapshot")
                search.add_parent_filter(parent)
                #search.add_filter("process", process)
                search.add_filter("context", context)
                parent_snapshots = search.get_sobjects()
                #parent_snapshots = Snapshot.get_by_sobject(parent, process=process)
                """

                #context = "attachment"
                #parent_snapshots = Search.eval("@SOBJECT(sthpw/note.connect['context','%s'].sthpw/snapshot)" % context, notes)

                for note in notes:

                    parent_snapshots = note.get_connections(context="attachment")

                    note_key = note.get_search_key()
                    xx = my.attachments.get(note_key)

                    if not xx:
                        xx = []
                        my.attachments[note_key] = xx

                    for snapshot in parent_snapshots:
                        if snapshot:
                            xx.append(snapshot)



        elif not my.attachments or my.attachments == "{}":
            my.attachments = {}




        if my.show_note_status:
            my.note_status_dict = ProjectSetting.get_dict_by_key('note_status')
        else:
            my.note_status_dict = {}

        my.note_format = my.kwargs.get("note_format")


        div = my.top
        
        context_count = 0



       

        for i, note in enumerate(notes):

            note_content = DivWdg()
            div.add(note_content)
            note_content.add_style("max-height: 500px")
            note_content.add_style("overflow-y: auto")
            note_content.add_style("overflow-x: hidden")

            if my.default_num_notes == -1:
                note_hidden = True
            elif context_count >= my.default_num_notes:
                note_hidden = True
            else:
                note_hidden = False

            note_wdg = my.get_note_wdg(note, note_hidden=note_hidden)


            """
            if i % 2 == 0:
                note_wdg.add_color("background", "background", -3)
            else:
                note_wdg.add_color("background", "background", -6)
            note_wdg.add_style("border-style: solid")
            note_wdg.add_style("border-width: 0 0 1px 0")
            note_wdg.add_style("border-color: %s" % div.get_color("table_border"))
            """

            note_content.add(note_wdg)
            note_wdg.add_style("width: 395px")

            context_count += 1


        return div



    def get_note_wdg(my, note, note_hidden=False):
        div = DivWdg()
        widget = NoteWdg(
            note=note,
            note_hidden=note_hidden,
            note_expandable=my.note_expandable,
            show_note_status=my.show_note_status,
            note_format=my.note_format,
            attachments=my.attachments,

        )

        div.add(widget)
        return div

     


class NoteWdg(BaseRefreshWdg):
    """Display of a single note.  Used by NoteCollectionWdg."""

    def get_display(my):
        note = my.kwargs.get("note")
        note_key = my.kwargs.get("note_key")
        if note_key:
            note = Search.get_by_search_key(note_key)
        my.kwargs['note_key'] = note.get_search_key()


        note_hidden = my.kwargs.get("note_hidden")

        my.note_expandable = my.kwargs.get("note_expandable")
        my.show_note_status = my.kwargs.get("show_note_status")

        my.attachments = my.kwargs.get("attachments")
        if not my.attachments or my.attachments == "{}":
            my.attachments = {}


        if my.show_note_status:
            my.note_status_dict = ProjectSetting.get_dict_by_key('note_status')
        else:
            my.note_status_dict = {}

        my.note_format = my.kwargs.get("note_format")

        return my.get_note_wdg(note, note_hidden)



    def get_note_menu(my):
 
        menu = Menu(width=120)
        menu_item = MenuItem(type='title', label='Actions...')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Edit Note')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_note_top");
            var search_key = top.getAttribute("note_search_key");
 
            var server = TacticServerStub.get();
            var note = null;
            
            try {
                note = server.get_by_search_key(search_key);
            }
            catch(e) {
                    spt.alert(spt.exception.handler(e));
            }
            
            var ok = function(value) {
                try{
                    var title = 'Saving Note';
                    server.update(search_key, {note: value});
                    var menu = spt.table.get_edit_menu(bvr.src_el);
                    spt.discussion.refresh(activator);

                }
                catch(e) {
                    spt.alert(spt.exception.handler(e));
                }
            }
            spt.prompt('Edit note [ ' + note.context + ' ]:', ok, 
            {title: 'Edit',
            text_input_default: note.note, 
            okText: 'Save'});
            '''
        } )



        #menu_item = MenuItem(type='action', label='Change Status')
        #menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Delete Note')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_note_top");
            var search_key = top.getAttribute("note_search_key");
            spt.confirm( "Are you sure you wish to delete this note?", function() {

                var server = TacticServerStub.get();
                server.delete_sobject(search_key);

                spt.discussion.refresh(activator);
            } )
            
            '''
        } )

        menu_item = MenuItem(type='action', label='Edit Status')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_note_top");
            var search_key = top.getAttribute("note_search_key");
            
           
            var server = TacticServerStub.get();
            var wdg = '';
            try {
                var class_name = 'tactic.ui.widget.NoteStatusEditWdg';
                var kwargs = {args: {search_key: search_key}};
                var wdg = server.get_widget(class_name, kwargs);
            }
            catch(e) {
                spt.alert(spt.exception.handler(e));
            }
            
            var ok = function(button) {
            
                var server = TacticServerStub.get();
                var status_sel  = button.getParent('.content').getElement("[name='note_status']");
                if (status_sel) {
                    var status = status_sel.value;
                    try{
                        var title = 'Saving Note Status';
                        server.update(search_key, {status: status});
                        spt.discussion.refresh(top);
                    }
                    catch(e) {
                        spt.alert(spt.exception.handler(e));
                    }
                }
                    
            };
            
            spt.prompt('Edit note status:', ok, 
                {title: 'Edit Note Status',
                 okText: 'Save',
                custom_html: wdg
                });

            
            
            '''
        } )

        return menu



    def get_note_wdg(my, note, note_hidden=False):
        context = note.get_value("context")

        mode = "dialog"

        div = DivWdg()
        # this is not meant to be refreshed
        #my.set_as_panel(div)
        div.add_class("spt_note")
        div.add_attr('note_search_key', note.get_search_key())
        div.add_class("spt_note_top")


        note_value = note.get_value("note") 
        login = note.get_value("login")
        date = note.get_value("timestamp")
        context = note.get_value("context")

        div.add_attr("my_context", context.encode("UTF-8"))

        from pyasm.security import Login
        user = Login.get_by_code(login)
        if not user:
            display_name = login
        else:
            display_name = user.get_value("display_name")

        if not display_name:
            display_name = login



        #content = Table(css='minimal')
        content = Table()
        content.add_style("width: 100%")
        content.add_color("color", "color")
        content.add_style("margin: 4px")

        div.add(content)


        tr = content.add_row()

        if context.endswith("/review") or context.endswith("/error"):
            context_wdg = IconWdg("View '%s' notes" % context, "BS_FLAG")
            tr.add_style("background: rgba(232, 74, 77, 0.8)")

        else:
            tr.add_color("background", "background", -10)

        td = content.add_cell()


        icon = IconWdg("Note", "BS_PENCIL")
        #td.add(icon)
        icon.add_style("float: left")
        icon.add_style("margin: 0px 5px")


        title = DivWdg()
        title.add_class("spt_note_header")
        title.add_style("margin: 5px 12px")
        #title.add_style("font-weight: bold")





        current_login = Environment.get_user_name()
        security = Environment.get_security()
        if security.is_admin() or current_login == login:

            icon = IconButtonWdg(title="Options", icon="BS_PENCIL")
            title.add(icon)
            icon.add_style("float: right")
            icon.add_style("margin-top: -5px")
            icon.add_style("margin-left: 3px")


            menus = [my.get_note_menu()]
            SmartMenu.add_smart_menu_set( icon, { 'NOTE_EDIT_CTX': menus } )
            SmartMenu.assign_as_local_activator( icon, "NOTE_EDIT_CTX", True )








        tbody = content.add_tbody()

        if my.note_expandable in ['true', True]:
            title.add_class("hand")
            swap = SwapDisplayWdg.get_triangle_wdg()
            if note_hidden in ['true', True]:
                swap.set_off()
            SwapDisplayWdg.create_swap_title(title, swap, tbody)
            title.add(swap)
            


        date_obj = dateutil.parser.parse(date)
        display_date = SPTDate.get_time_ago(date_obj)

        date_obj = SPTDate.convert_to_local(date_obj)
        display_date_full = date_obj.strftime("%b %d, %Y %H:%M")
        #display_date = date_obj.strftime("%b %d - %H:%M")



        if my.note_expandable in ['true', True]:
            if len(note_value) > 30:
                short_note = "%s ..." % note_value[:28]
            else:    
                short_note = note_value
                
        else: 
            # show the entire note
            #short_note = WikiUtil().convert(note_value)
            short_note = ''
            
           
        if short_note:
            title.add("<div style='float: left'> %s - %s</div>" % (display_name, short_note) )
        else:
            title.add("<b style='float: left; font-size: 1.1em'>%s</b>" % (display_name) )

        note_status = note.get('status')
        if note_status:
            status_div = DivWdg(note_status[0].upper())
            status_div.add_attr('title', note_status)
            status_div.add_styles('float: left; font-weight: 800; width: 12px; padding: 0 6 0 6; margin-bottom: 2px')
            title.add(status_div)

        
        title.add("<div style='float: right; padding-right: 2px'>%s</div>" % display_date)
        title.add_attr("title", display_date_full)

        if my.show_note_status:
            status = note.get_value('status')
            status_label = my.note_status_dict.get(status)
            if status_label:
                title.add (' - %s ' %status_label)


        td.add(title)

        # Paper clip button code
        key = note.get_search_key()
        attachments = my.attachments.get(key)
        if attachments:
            bubble = 'View Attachments'
            if len(attachments) > 1:
                bubble = '%s (%s)'%(bubble, len(attachments))
            btn = IconButtonWdg(title=bubble, icon="BS_PAPERCLIP")
            title.add("&nbsp;");
            btn.add_style("float: right");
            btn.add_style("margin-top: -3px");
            title.add(btn)
            btn.add_class("spt_note_attachment")

            # get the codes to the attachments
            attachment_codes = []
            for attachment in attachments:
                attachment_codes.append( attachment.get_code() )
            btn.add_attr("spt_note_attachment_codes", "|".join(attachment_codes) )









        tbody.add_class("spt_note_content")

        if mode == "dialog":
            tbody.add_style("display", "")

        elif note_hidden in ['true', True] and my.note_expandable in ['true', True]:
            tbody.add_style("display: none")
        else:
            tbody.add_style("display", "")
        
        # don't draw the detailed attachment and user info
        '''
        if my.note_format == 'compact':
            content.close_tbody()
            return div
        '''
        content.add_row()
        if my.note_format == 'full':
            left = content.add_cell()
            left.add_style("padding: 10px")
            left.add_style("width: 55px")
            left.add_style("min-height: 100px")
            left.add_style("vertical-align: top")
            #left.add_style("border-right: solid 1px %s" % left.get_color("table_border"))

            if not login:
                login = "-- No User --"
                left.add(login)
            else:
                login_sobj = Login.get_by_code(login)

                thumb = ThumbWdg()
                thumb.set_icon_size("45")
                thumb.add_style("border: solid 1px #DDD")
                thumb.add_style("border-radius: 45px")
                thumb.add_style("overflow: hidden")
                if login_sobj:
                    thumb.set_sobject(login_sobj)
                    left.add(thumb)
                    left.add_style("font-size: 1.0em")

                    #name = "%s %s" % (login_sobj.get_value("first_name"), login_sobj.get_value("last_name") )
                    #left.add("%s<br/>" % name)
                    #left.add("%s<br/>" % login_sobj.get_value("email"))





        right = content.add_cell()
        right.add_style("vertical-align: top")
        right.add_style("padding: 10px 30px 10px 15px")

        context = note.get_value("context")

        right.add( WikiUtil().convert(note_value) )
        right.add_style("word-wrap: break-word")
        right.add_style("max-width: 300px")


        attached_div = DivWdg()
        attached_div.add_style("margin-top: 10px")
        snapshots = attachments

        # Snapshot thumbnail code
        if snapshots:
            #attached_div.add("<hr/>Attachments: %s<br/>" % len(snapshots) )
           
            """
            attached_div.add_relay_behavior( {         
            'type': 'click',
            'mouse_btn': 'LMB',
            'bvr_match_class': 'spt_open_thumbnail',
            'cbjs_action': '''

            var src_el = bvr.src_el;
            var thumb_href = src_el.getElement('.spt_thumb_href');
            var thumb_path = thumb_href.getAttribute('href');
            window.open(thumb_path);
            '''
            } )
            """

            right.add("<hr/>")
            right.add('''
            <div style="margin-bottom: -10px; font-size: 0.8em;">Attachments:</div>
            ''')

            for snapshot in snapshots:
                thumb = ThumbWdg()
                thumb.set_option('detail','none')
                thumb.set_option('image_link_order' , 'main|web|icon')
                thumb.set_icon_size(60)
                thumb.set_sobject(snapshot)

                thumb_div = DivWdg()
                thumb_div.add_style("float: left")
                thumb_div.add(thumb)
                thumb_div.add_class("spt_open_thumbnail")
                            
                attached_div.add(thumb_div)


        right.add(attached_div)

        content.close_tbody()

        return div




class DiscussionAddNoteWdg(BaseRefreshWdg):
    '''This widget draws the UI that user clicks to add note'''
        
    def add_style(my, name, value=None):
        my.top.add_style(name, value)


    def init(my):
        my.hidden = my.kwargs.get("hidden")
        my.append_processes = my.kwargs.get("append_process")
        if my.append_processes:
            my.append_processes = my.append_processes.split(",")
            # remove any spaces
            my.append_processes = [x.strip() for x in my.append_processes if x]


        my.custom_processes = my.kwargs.get("custom_processes")
        if my.custom_processes:
            my.custom_processes = my.custom_processes.split(",")
            # remove any spaces
            my.custom_processes = [x.strip() for x in my.custom_processes if x]


        my.upload_id = my.kwargs.get("upload_id")
        
        my.allow_email = my.kwargs.get("allow_email") not in ['false', False]
        my.show_task_process = my.kwargs.get('show_task_process') in ['true', True]



    def get_display(my):

        parent = my.kwargs.get("parent")
        if not parent:
            search_key = my.kwargs.get("search_key")
            parent = Search.get_by_search_key(search_key)
        elif isinstance(parent, basestring):
            search_key = parent
            parent = Search.get_by_search_key(parent)




        # explicitly set the contexts
        my.contexts = my.kwargs.get("context")
        # need the process to predict the notification to and cc
        my.process = my.kwargs.get('process')

      
        content_div = my.top
        content_div.add_style("min-width: 300px")

        my.set_as_panel(content_div)
        content_div.add_class("spt_discussion_add_note")

        display = my.kwargs.get("display")
        if not display:
            display = "none"
        content_div.add_style("display: %s" % display)

        content_div.add_color("background", "background")
        content_div.add_color("color", "color")
        content_div.add_style("padding: 10px")
        #content_div.add_border(style="solid")
        content_div.add_class("spt_add_note_top")

        search_key_hidden = HiddenWdg("search_key")
        search_key_hidden.set_value(parent.get_search_key())
        content_div.add(search_key_hidden)

        content_div.add('''<div style="margin-top: 10px; font-size: 16px">Add New Note</div>''')
        content_div.add('''<hr/>''')



        # get the pipeline if one is defined
        pipeline_code = parent.get_value("pipeline_code", no_exception=True)
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
        else:
            pipeline = None


        # figure out which processes to show
        if my.process:
            process_names = []
            if pipeline:
                process_obj = pipeline.get_process(my.process)
                if process_obj:
                    process_type = process_obj.get_type()
                else:
                    process_type = ""
                if process_type == "approval":
                    input_processes = pipeline.get_input_processes(my.process)
                    process_names.extend( [x.get_name() for x in input_processes] )
                    process_obj = pipeline.get_process(my.process)

            process_names.append(my.process)
        
        elif my.show_task_process:
            task_expr = "@GET(sthpw/task.process)"
            task_processes = Search.eval(task_expr, sobjects=[parent])
            
            process_names = task_processes
        else:
            if pipeline:
                process_names = pipeline.get_process_names()
                if not process_names:
                    process_names = ["publish"]
            else:
                process_names = ["publish"] 


        if my.append_processes:
            process_names.extend(my.append_processes)

        if my.custom_processes:
            process_names = my.custom_processes
        
        security = Environment.get_security()
        project_code = Project.get_project_code()
        allowed = []

        for process in process_names:
            keys = [
                    {"process": process},
                    {"process": "*"},
                    {"process": process, "project": project_code},
                    {"process": "*", "project": project_code}
            ]
            if security.check_access("process", keys, "allow", default="deny"):
                allowed.append(process)
        process_names = allowed

        if not process_names:
            content_div.add("<i>You do not have permission to add notes here.</i>")
            return content_div

        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias="notes-widget")
        content_div.add(help_button)
        help_button.add_style("float: right")
        help_button.add_style("margin-top: -5px")

        # prevent ppl from defining contexts directly when there is nothing defined for process, aka, publish
        
        if process_names == ["publish"]:
            hidden = HiddenWdg("add_process", 'publish')
            #hidden.set_value("publish")
            content_div.add(hidden)
            if my.contexts:
                content_div.add("Warning: You should define %s in process display option. 'publish' will override." % my.contexts)
        
            # context is optional, only drawn if it's different from process
        elif len(process_names) == 1:
            wdg_label = "Send To Process:"
            span = SpanWdg(wdg_label)
            span.add_style('padding-right: 4px')
            content_div.add(span)

            hidden = HiddenWdg("add_process")
            hidden.set_value(process_names[0])
            content_div.add(hidden)
            content_div.add("<b>%s</b>" % process_names[0])
        else:
            wdg_label = "Send To Process:"
            span = SpanWdg(wdg_label)
            span.add_style('padding-right: 4px')
            content_div.add(span)

            process_select = SelectWdg("add_process")
            process_select.add_class("spt_add_note_process")
            process_select.set_option("values", process_names)
            process_select.add_style("width: 200px")
            content_div.add(process_select)


        # add the context label if it is different from process in use_parent mode
        # this is a special case where we explicitly use processs/context for note
        if my.contexts:
            hidden = HiddenWdg("add_context")
            hidden.set_value(my.contexts[0])
            content_div.add(hidden)
            if my.contexts[0] != my.process:
                context_span = SpanWdg(my.contexts[0], css='small')
                content_div.add(context_span)

        content_div.add("<br/>")


        text = TextAreaWdg("note")
        text.add_class("form-control")
        text.add_style("width: 100%")
        text.add_style("height: 100px")
        content_div.add(text)

        #content_div.add_style("padding: 20px 10px")
        #content_div.add_color("background", "background", -3)

        content_div.add("<br/>"*2)


        #add_button = ProdIconButtonWdg("Submit Note")
        add_button = ActionButtonWdg(title="Add Note", color="primary", tip='Submit information to create a new note')
        content_div.add(add_button)
        add_button.add_style("float: right")

        submit_class = DiscussionWdg.get_note_class(my.hidden, 'spt_discussion_submit') 
        add_button.add_class(submit_class)


        # attachments
        attachment_div = DivWdg()
        content_div.add(attachment_div)
        attachment_div.add_class("spt_attachment_top")

       
        from tactic.ui.input import UploadButtonWdg 
        on_complete = '''
       
        var files = spt.html5upload.get_files(); 

        var top = bvr.src_el.getParent(".spt_attachment_top")
        var list = top.getElement(".spt_attachment_list");

        if (!top.files) {
            top.files = [];
        }
      
        var file_names = [];
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            file_names.push(file.name);

            var loadingImage = loadImage(
                file,
                function (img) {
                    var div = $(document.createElement("div"));
                    list.appendChild(div);
                    div.setStyle("padding", "0px 5px");
                    div.setStyle("display", "inline-block");
                    div.setStyle("vertical-align", "middle");
                    div.setStyle("width", "80px");
                    img = $(img);
                    div.appendChild(img)
                    img.setStyle("width", "100%");
                    img.setStyle("height", "auto");
                },
                {maxWidth: 80, canvas: true, contains: true}
            );

            top.files.push(file.name);
        }
      
       
        spt.app_busy.hide();
        '''
        table_upload_id = my.upload_id
      

        upload_init = ''' 
        var server = TacticServerStub.get();
        var ticket_key = server.start({title: 'New Note'});
        var top = bvr.src_el.getParent(".spt_attachment_top");
        top.setAttribute('ticket_key', ticket_key);
        upload_file_kwargs['ticket'] = ticket_key;
      
       
        '''

      

        browse_button = UploadButtonWdg(title="Attach File", tip='Browse for files to attach to this note', on_complete=on_complete,\
                upload_init=upload_init, multiple='true', upload_id=table_upload_id) 
        attachment_div.add(browse_button)
        #browse_button.add_style("float: left")


        attach_list = DivWdg()
        attach_list.add_style('margin-top: 8px')
        attachment_div.add(HtmlElement.br(2))
        attachment_div.add(attach_list)
        attach_list.add_class("spt_attachment_list")


        if not my.allow_email:
            return content_div

        content_div.add( HtmlElement.br() )

        swap = SwapDisplayWdg()
        content_div.add(swap)
        swap.add_style("float: left")
        title = DivWdg("Mail Options")
        title.add_style("margin: 2px 0px 0px -2px")
        content_div.add(title)

        mail_div = DivWdg()
        SwapDisplayWdg.create_swap_title(title, swap, mail_div)

        content_div.add("<br/>")
        content_div.add(mail_div)

        mail_div.add_class("spt_discussion_mail")
        #mail_div.add_style("display: none")
        mail_div.add("Mail will be sent to:<br/>")
        mail_div.add_style("margin-left: 20px")

        from pyasm.command import EmailHandler

        # there could be multiple.. so this is not always accurate
        search = Search("sthpw/notification")
        search.add_filter("process", process_names[0])
        search.add_filter("event", "insert|sthpw/note")
        notification = search.get_sobject()
        if notification:
            handler = EmailHandler(notification, None, None, None, None)
            to = handler.get_mail_users("mail_to")
            cc = handler.get_mail_users("mail_cc")
            to_emails = []
            cc_emails = []
            for x in to:
                if isinstance(x, SObject):
                    to_emails.append(x.get_value('email'))
                else:
                    to_emails.append(x)
            for x in cc:
                if isinstance(x, SObject):
                    cc_emails.append(x.get_value('email'))
                else:
                    cc_emails.append(x)

           
            mail_div.add("To: %s<br/>" % ",".join(to_emails))
            mail_div.add("Cc: %s<br/>" % ",".join(cc_emails))


        mail_div.add(HtmlElement.br())
        # mail cc and bcc
        mail_div.add("Extra list of email addresses - comma separated:")



        table = Table()
        table.add_color("color", "color")
        mail_div.add(table)

        from tactic.ui.input import TextInputWdg

        # CC
        table.add_row()
        table.add_cell("Cc: ")
        text = TextInputWdg(name="mail_cc")
        text.add_style("width: 250px")
        table.add_cell(text)

        tr, td = table.add_row_cell()
        td.add("<br/>")

        # BCC 
        table.add_row()
        table.add_cell("Bcc: ")
        text = TextInputWdg(name="mail_bcc")
        text.add_style("width: 250px")
        table.add_cell(text)

        tr, td = table.add_row_cell()
        td.add("<br/>")

        return content_div




class DiscussionAddNoteCmd(Command):
    ''' this is the UI to add note when someone clicks on the + button. It does not contain the + button'''
    def get_title(my):
        return "Added a note"

    def execute(my):
        search_key = my.kwargs.get("search_key")
        sobject = Search.get_by_search_key(search_key)

        ticket = my.kwargs.get('ticket')
        note = my.kwargs.get("note")
        mail_cc = my.kwargs.get("mail_cc")
        mail_bcc = my.kwargs.get("mail_bcc")
        if mail_cc:
            mail_cc = mail_cc.split(',')
        else:
            mail_cc = []
        if mail_bcc:
            mail_bcc = mail_bcc.split(',')
        else:
            mail_bcc = []
        process = my.kwargs.get("process")
        context = my.kwargs.get("context")
        if not context:
            context = process
        elif context.find("/"):
            parts = context.split("/")
            if parts:
                try:
                    # if the subcontext is a number, then ignore this
                    subcontext = int(parts[1])
                    context = parts[0]
                except:
                    pass


        from pyasm.biz import Note
        note_sobj = Note.create(sobject, note, context=context, process=process)
        subject = 'Added Note'
        message = 'The following note has been added for [%s]:\n%s '%(sobject.get_code(), note_sobj.get_value('note'))
        project_code = Project.get_project_code()
        users = []
        users.extend(mail_cc)
        users.extend(mail_bcc)
        if len(users) > 0:
            EmailTrigger2.add_notification(users, subject, message, project_code)
            EmailTrigger2.send([],[],[], subject, message, cc_emails=mail_cc,bcc_emails=mail_bcc)


        

        from pyasm.checkin import FileCheckin
        files = my.kwargs.get("files")

        upload_dir = Environment.get_upload_dir(ticket)
        for i, path in enumerate(files):

            path = path.replace("\\", "/")
            basename = os.path.basename(path)
            basename = Common.get_filesystem_name(basename) 
            new_path = "%s/%s" % (upload_dir, basename)
            context = "publish"

            file_paths = [new_path]
            source_paths = [new_path]
            file_types = ['main']
            # if this is a file, then try to create an icon
            if os.path.isfile(new_path):
                icon_creator = IconCreator(new_path)
                icon_creator.execute()

                web_path = icon_creator.get_web_path()
                icon_path = icon_creator.get_icon_path()
                if web_path:
                    file_paths = [new_path, web_path, icon_path]
                    file_types = ['main', 'web', 'icon']
                    source_paths.append(web_path)
                    source_paths.append(icon_path)

            # specify strict checkin_type to prevent latest versionless generated

            checkin_mode = "parent"
            if checkin_mode == "parent":
                attachment_process = "%s/attachment" % process

                # NOTE: we may want to use a random key rather than the
                # basename to ensure that there is never a duplicate
                # context
                attachment_context = "attachment/%s/%s" % (process, basename)
                checkin = FileCheckin(sobject, file_paths=file_paths, file_types = file_types, \
                    source_paths=source_paths,  process=attachment_process, \
                    context=attachment_context, checkin_type='strict')

                checkin.execute()

                snapshot = checkin.get_snapshot()
                snapshot.connect(note_sobj, context="attachment")

            else:
                checkin = FileCheckin(note_sobj, file_paths= file_paths, file_types = file_types, \
                    source_paths=source_paths,  context=context, checkin_type='strict')

                checkin.execute()


        my.call_triggers(note_sobj)

        my.info = {
                "note": note_sobj.get_sobject_dict()
        }


    def call_triggers(my, note_sobj):

        prefix = "note"
        sobject = note_sobj.get_parent()
        context = note_sobj.get("context")
        process = note_sobj.get("process")

        my.sobjects = [sobject]

        # call the done trigger for checkin
        from pyasm.command import Trigger
        output = {}
        output['search_key'] = SearchKey.build_by_sobject(note_sobj)
        output['update_data'] = note_sobj.data.copy()
        output['note'] = note_sobj.get_sobject_dict()
        #output['files'] = [x.get_sobject_dict() for x in my.file_objects]


        # Add the checkin triggers
        base_search_type = sobject.get_base_search_type()
        Trigger.call(my, prefix, output)
        Trigger.call(my, "%s|%s" % (prefix, base_search_type), output)
        Trigger.call(my, "%s|%s|%s" % (prefix, base_search_type, context), output)
        
        # get the process (assumption here) and call both on process and process code
        pipeline = None
        if process:
            Trigger.call(my, "%s|%s" % (prefix, base_search_type), output, process=process)
        
            pipeline_code = sobject.get_value("pipeline_code", no_exception=True)
            if pipeline_code:
                pipeline = Pipeline.get_by_code(pipeline_code)

            if pipeline and process:
                search = Search("config/process")
                search.add_filter("pipeline_code", pipeline_code)
                search.add_filter("process", process)
                process_sobj = search.get_sobject()
                if process_sobj:
                    process_code = process_sobj.get_code()
                    Trigger.call(my, "%s|%s" % (prefix, base_search_type), output, process=process_code)



class NoteStatusEditWdg(BaseRefreshWdg):
    ''' Custom widget used in the prompt for changing note status'''

    def get_display(my):
        values_map = ProjectSetting.get_map_by_key('note_status')
        if not values_map:
            # put in a default
            ProjectSetting.create('note_status', 'new:N|read:R|old:O|:', 'map',\
                description='Note Statuses', search_type='sthpw/note')
            values_map = ProjectSetting.get_map_by_key('note_status')

        labels = []
        values = []
        for key, value in values_map:
            desc = key
            if desc == '':
                desc = '&lt; empty &gt;'
            labels.append('%s'%(desc))
            values.append(key)

        div = DivWdg(css='note_edit_top')
        select = SelectWdg('note_status')
        select.set_option('empty','true')
        select.set_option('values', values)
        select.set_option('labels', labels)
        div.add(select)

        sk = my.kwargs.get('search_key')
        note = SearchKey.get_by_search_key(sk)
        if note:
            current_status = note.get_value('status')
            select.set_value(current_status)

        return div


'''
#Testing of using the gear menu code 
class NoteEditMenuWdg(BaseRefreshWdg):

    def get_display(my):
        from tactic.ui.container import SmartMenu, SmartMenuButtonDropdownWdg
        menus = [ my.get_main_menu(), my.get_status_menu() ]

    
        #from tactic.ui.widget import SingleButtonWdg
        #btn_dd = SingleButtonWdg(title='Global Options', icon=IconWdg.INFO, show_arrow=True)
        btn = IconWdg(icon=IconWdg.INFO)


        #btn_dd.add_behavior( { 'type': 'hover',
        #            'mod_styles': 'background-image: url(/context/icons/common/gear_menu_btn_bkg_hilite.png); ' \
        #                            'background-repeat: no-repeat;' } )
        smenu_set = SmartMenu.add_smart_menu_set( btn, { 'NOTE_EDIT_MENU': menus } )
        btn.add_class( "SPT_SMENU_CONTAINER" )
        #SmartMenu.assign_as_local_activator( btn, "NOTE_EDIT_MENU", True )
        btn_set = SmartMenuButtonDropdownWdg(menus=menus)
        return btn_set


    def get_main_menu(my):
        return { 'menu_tag_suffix': 'MAIN', 'width': 100, 'opt_spec_list': [
            { "type": "action", "label": "Edit",  "bvr_cb": {'cbjs_action': "alert('Edt')"} },
            { "type": "action", "label": "Delete" },
            { "type": "submenu", "label": "Status", "submenu_tag_suffix": "STATUS" },
        ] }


    def get_status_menu(my):
        return {
            'menu_tag_suffix': 'STATUS', 'width': 80, 'opt_spec_list': [

                # { "type": "title", "label": "Edit" },

                { "type": "action", "label": "New",
                    "bvr_cb": {'cbjs_action': "alert(123)"}
                },

                { "type": "action", "label": "Read",
                    "bvr_cb": {'cbjs_action': "alert(123)"}
                },

                { "type": "action", "label": "Old",
                     "bvr_cb": {'cbjs_action':"alert(123)"}
                }

        ] }
'''
