###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['TypeTableElementWdg', 'TemplateElementWdg', 'GeneralPublishElementWdg','NotificationTriggerElementWdg','CheckinButtonElementWdg','CheckoutButtonElementWdg','RecipientElementWdg']

import types, re

from pyasm.common import TacticException, Container, Date, jsonloads, jsondumps
from pyasm.search import Search, SearchKey, SObject
from pyasm.web import DivWdg, Widget, WebContainer, Table, HtmlElement, WikiUtil, SpanWdg
from pyasm.widget import IconWdg, TextWdg, TextAreaWdg, SelectWdg, ThumbWdg, PublishLinkWdg, IconButtonWdg, CheckboxWdg, SwapDisplayWdg, ProdIconButtonWdg
from pyasm.biz import Project, NamingUtil, ExpressionParser, Snapshot
from tactic.ui.common import BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.filter import FilterData
from tactic.ui.widget import ActionButtonWdg

class TypeTableElementWdg(SimpleTableElementWdg):
    '''The element widget that displays according to type'''


    def is_editable(my):
        return True

    def get_required_columns(my):
        return [my.name]

    def get_type(my):
        return my.type

    def handle_td(my, td):
        type = my.get_option("type")
        if not type:
            type = my.get_type()

        if type in ['float', 'int']:
            td.add_style("text-align: right")

        super(TypeTableElementWdg,my).handle_td(td)


    def get_text_value(my):
        type = my.get_option("type")
        if not type:
            type = my.get_type()
 
        if type in ['color', 'boolean','bigint', 'integer','float']:
            return my.get_value()
        else:
            return my.get_display()

    def get_display(my):
        value = my.get_value()
        name = my.get_name()

        type = my.get_option("type")
        if not type:
            type = my.get_type()

        # FIXME: this needs to be handled outside of this class to centralize
        # the type of an element!!!
        if type in ["timestamp"]:
            # make a guess here
            if name.endswith('time'):
                type = 'time'
            elif name.endswith('date'):
                type = 'date'

        if type == "text":
            wiki = WikiUtil()
            display = wiki.convert(value)

        elif type in ["time"]:
            if value:
                display = Date(value).get_display_time()
            else:
                display = ''

        elif type in ["datetime"]:
            if value:
                display = Date(value).get_display_datetime()
            else:
                display = ''

        elif type in ["timestamp", 'date']:
            if value == '{now}':
                display = Date()
            elif value:
                display = Date(value).get_display_date()
            else:
                display = ''
        elif type == "timecode":
            display = "00:00:00:00"
        elif type == "currency":
            display = "$%s" % value


        elif type == "color":
            display = DivWdg()

            color = DivWdg("&nbsp")
            color.add_style("height: 15px")
            color.add_style("width: 15px")
            color.add_style("float: left")
            color.add_style("margin: 0 5px 0 5px")
            color.add_style("background: %s" % value)
            display.add(color)

            display.add(value)

            display.add_style("width: 100%")
            display.add_style("height: 100%")

        elif type == "boolean":
            display = DivWdg()
            display.add_style("text-align: center")
            display.add_style("width: 100%")
            display.add_style("height: 100%")
            if value == True:
                from pyasm.widget import IconWdg
                icon = IconWdg("True", IconWdg.CHECK)
                display.add(icon)
            elif value == False:
                from pyasm.widget import IconWdg
                icon = IconWdg("False", IconWdg.INVALID)
                display.add(icon)
            else:
                display.add("&nbsp;")
        else:
            if not isinstance(value, basestring):
                display = DivWdg()
                display.add_style("float: right")
                display.add_style("padding-right: 3px")
                display.add(str(value))
            else:
                display = value

        return display




class GeneralPublishElementWdg(BaseTableElementWdg):
    ''' A general publish table element with the option of having a thumbnail '''
    def get_arg_keys(my):
        return {'view': 'a custom view other than publish'}

    def preprocess(my):
        if my.get_option('preview') != 'false':
            my.thumb = ThumbWdg()
            my.thumb.set_sobjects(my.sobjects)
            my.thumb.set_icon_size(60)
            # passing options from this to ThumbWdg, shouldn't have conflicts
            options = my.options
            my.thumb.set_options(options)
        # for its own preprocess and data caching

    def get_display(my):
        my.view = my.kwargs.get('view')
        if not my.view:
            my.view = 'publish'
        widget = Widget()
        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        if my.get_option('preview') != 'false': 
            my.thumb.set_current_index(my.get_current_index())
            widget.add(my.thumb)

        publish_link = PublishLinkWdg(search_type,search_id, config_base=my.view) 
        div = DivWdg(publish_link)
        div.set_style('clear: left; padding-top: 6px')
        widget.add(div)

        # build a popup link to show publish browsing
        browse_link = IconButtonWdg("Publish Browser", IconWdg.CONTENTS)
        browse_link.add_behavior({'type': 'click_up',
            'cbjs_action': 'spt.popup.get_widget(evt, bvr)',
            'options': {'popup_id' : 'publish_browser',
                        'class_name' : 'pyasm.prod.web.PublishBrowserWdg' ,
                        'title': 'Publish Browser'},
            'args' : { 'search_type': search_type,
                        'search_id' : search_id }
            })
        div.add(browse_link)
        div.set_style('padding-top: 6px')


        return widget



 

# DEPRECATED: use ExpressionElementWdg above
class TemplateElementWdg(SimpleTableElementWdg):
    '''The element widget that displays according to type'''

    def get_display(my):
        sobject = my.get_current_sobject()
        template = my.get_option("template")
        if not template:
            return super(SimpleTableElementWdg, my).__init__()

        display = NamingUtil.eval_template(template, sobject)
        my.value = display
        return display


__all__.append("ExpressionIsZeroElementWdg")
class ExpressionIsZeroElementWdg(BaseTableElementWdg):
    def get_display(my):
        sobject = my.get_current_sobject()
        expression = my.get_option("expression")

        parser = ExpressionParser()
        value = parser.eval(expression, sobject)

        div = DivWdg()
        div.add_style("text-align: center")
        if value == False:
            div.add( IconWdg("XXX", IconWdg.DOT_GREEN) )
        else:
            div.add( IconWdg("YYY", IconWdg.DOT_RED) )

        return div



__all__.append("ExpressionIsCountZeroElementWdg")
class ExpressionIsCountZeroElementWdg(BaseTableElementWdg):
    def get_display(my):
        sobject = my.get_current_sobject()
        expression = my.get_option("expression")

        parser = ExpressionParser()
        value = parser.eval(expression, sobject)

        div = DivWdg()
        div.add_style("text-align: center")
        if int(value) > 0:
            div.add( IconWdg("XXX", IconWdg.DOT_GREEN) )
        else:
            div.add( IconWdg("YYY", IconWdg.DOT_RED) )

        div.add(value)

        return div





__all__.append("IndirectMappedDisplayLabelWdg")
class IndirectMappedDisplayLabelWdg(BaseTableElementWdg):

    def _map_display_label(my):

        my.display_label = ''

        target_table = my.get_option("target_table")
        target_column = my.get_option("target_column")

        source_column = my.get_option("source_column")
        display_column = my.get_option("display_column")

        my.sobject = my.get_current_sobject()
        my.mapping_value = my.sobject.get_data().get( source_column )

        # do search here
        search = Search( target_table )
        search.add_filter( target_column, my.mapping_value)
        search.add_column( display_column )

        items = search.get_sobjects()
        if items:
            my.display_label = items[0].get_data().get( display_column )


    def get_display(my):

        my._map_display_label()
        div = DivWdg()
        div.add( '%s' % my.display_label )
        return div


    def handle_td(my, td):
        td.add_attr( "spt_input_value", my.value )


    def is_editable(my):
        return True

    def is_sortable(my):
        return True

    def is_groupable(my):
        return False


    def get_text_value(my):
        '''for csv export'''
        my._map_display_label()
        return my.display_label


    def set_td(my, td):
        my.td = td



class NotificationTriggerElementWdg(BaseTableElementWdg):

    def get_display(my):
         
        search_key = ''
        sobj = my.get_current_sobject()

        top = DivWdg() 
        top.add_style("padding-top: 5px")

        span = ActionButtonWdg(title="Email Test")
        #span = ProdIconButtonWdg('Email Test')
        top.add(span)
        span.add_behavior(my.get_behavior(sobj))


        return top

    def get_behavior(cls, sobject):
        '''it takes sobject as an argument and turn it into a dictionary to pass to 
            NotificationTestCmd'''
        pal = WebContainer.get_web().get_palette()
        bg_color = pal.color('background')
        sobj_dict = SObject.get_sobject_dict(sobject)
        sobj_json = jsondumps(sobj_dict)
        bvr = {'type': 'click_up',
                 'cbjs_action': '''
                   var server = TacticServerStub.get();
                   var rtn = {};
                   var msg = '';

                   try
                   { 
                      spt.app_busy.show( 'Email Test', 'Waiting for email server response...' );
                      rtn = server.execute_cmd('tactic.command.NotificationTestCmd', args={'sobject_dict': %s});
                      msg = rtn.description;
                      msg += '\\nYou can also review the notification in the Notification Log.'
                   }
                   catch(e) {
                       msg = 'Error found in this notification:\\n\\n' + spt.exception.handler(e);
                   }
                   //console.log(msg)
                   spt.app_busy.hide();
                   var popup_id = 'Notification test result';

                   var class_name = 'tactic.ui.panel.CustomLayoutWdg';

                   msg= msg.replace(/\\n/g, '<br>');

                   var options = { 'html': '<div><div style="background:%s; padding: 5px">' + msg + '</div></div>'};
                   var kwargs = {'width':'600px'};
                   spt.panel.load_popup(popup_id, class_name, options, kwargs);
                   
                  ''' %(sobj_json, bg_color)}
        return bvr

from button_wdg import ButtonElementWdg
class CheckinButtonElementWdg(ButtonElementWdg):

    ARGS_KEYS = {
    'transfer_mode': {
        'category': '1. Required',
        'description': 'Mode by which files are transferred to the server',
        'type': 'SelectWdg',
        'order': 1,
        'values': 'upload|copy|move'
        },
      'mode': { 'type': 'SelectWdg',
            'category': '2. Display',
            'order': 2,
            'values': 'sequence|file|dir|multi_file|add',
            'description': 'determines whether this widget can only check-in sequences, file, or directory'},
     #'checkin_panel_script_path': {'type': 'TextWdg',
     #       'category': '2.Display',
     #       'description': 'path to the check-in panel script'},
     'checkin_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 3,
            'description': 'path to the check-in script'},
     'validate_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 4,
            'description': 'path to the validation script'},
     'process' : {'type': 'TextWdg',
            'category': '2. Display',
            'order': 5,
            'description': 'process under which the check-in occurs'},
     'lock_process':  {'type': 'CheckboxWdg',
            'category': '2. Display',
            'order': 6,
            'description': 'If turned on, the process specified cannot be changed by the user'},
     'width' : {'type': 'TextWdg',
            'category': '2. Display',
            'order': 7,
            'description': 'width of the widget'},
     'show_context' : {'type': 'SelectWdg',
            'category': '2. Display',
            'values': 'true|false',
            'order': 8,
            'description': 'Determines whether to show the context selector'},
     'sobject_mode': { 'type': 'SelectWdg',
             'category': '2. Display',
            'values': 'parent|connect|sobject',
            'order': 8,
            'description': 'Determines which sobject to check into'},
            
            
     #'show_sub_context' : {'type': 'SelectWdg',
     #       'category': '2. Display',
     #       'values': 'true|false',
     #       'order': 9,
     #       'description': 'Determines whether to show the sub_context selector'},




    }

    #def init(my):
    #    return super(CheckinButtonElementWdg, my).init()


    def preprocess(my):

        mode = my.get_option('mode')

        width = my.get_option('width')
        size = my.get_option('icon_size')
        if mode == 'add':
            my.set_option('icon', "PUBLISH_MULTI")
        else:
            if size == 'large':
                my.set_option('icon', "PUBLISH_LG")
            else:
                my.set_option('icon', "PUBLISH")

        transfer_mode = my.get_option('transfer_mode')
        checkin_ui_options = my.get_option('checkin_ui_options')
        if not checkin_ui_options:
            checkin_ui_options = ''

        # do not preset it, let the auto-detection take care of it
        #if not transfer_mode:
        #    transfer_mode = 'upload'
        if not mode:
            mode = ''

        checkin_script = my.get_option("checkin_script")
        checkin_script_path = my.get_option("checkin_script_path")
        checkin_panel_script_path = my.get_option("checkin_panel_script_path")
        validate_script_path = my.get_option("validate_script_path")
        if not checkin_script:
            checkin_script = ''
        if not checkin_script_path:
            checkin_script_path = ''
        if not checkin_panel_script_path:
            checkin_panel_script_path = ''
        if not validate_script_path:
            validate_script_path = '' 

        lock_process = my.get_option("lock_process")
        if not lock_process:
            lock_process = ''
        sandbox_dir = my.get_option("sandbox_dir")
        if not sandbox_dir:
            sandbox_dir = ''

        checkin_relative_dir = my.get_option("checkin_relative_dir")

        if not checkin_relative_dir:
            checkin_relative_dir = ''


        show_context = my.get_option("show_context")
        show_sub_context = my.get_option("show_sub_context")

        
        kwargs = {}
        kwargs['checkin_script'] = checkin_script
        kwargs['checkin_script_path'] = checkin_script_path
        kwargs['checkin_panel_script_path'] = checkin_panel_script_path
        kwargs['validate_script_path'] = validate_script_path

        kwargs['lock_process'] = lock_process
        kwargs['transfer_mode'] = transfer_mode
        kwargs['checkin_ui_options'] = checkin_ui_options
        kwargs['mode'] = mode
        kwargs['width'] = width
        kwargs['sandbox_dir'] = sandbox_dir
        kwargs['checkin_relative_dir'] = checkin_relative_dir
        kwargs['show_context'] = show_context
        kwargs['show_sub_context'] = show_sub_context

        my.behavior['kwargs'] = kwargs
        my.behavior['cbjs_action'] = '''
        var kwargs = bvr.kwargs;

        spt.app_busy.show("Opening Check-In Widget...");

        // sobject specific data
        var top = bvr.src_el.getParent(".spt_button_top");
        var search_key = top.getAttribute("spt_search_key");
        var process = top.getAttribute("spt_process");
        var context = top.getAttribute("spt_context");
        kwargs['search_key'] = search_key;
        kwargs['process'] = process;
        kwargs['context'] = context;


        var values = {};
        var top = bvr.src_el.getParent(".spt_checkin_top");
        if (top) {
            var transfer_mode = top.getElement(".spt_checkin_transfer_mode").value;
            values['transfer_mode'] = transfer_mode;
        }
        script = spt.CustomProject.get_script_by_path(bvr.checkin_panel_script_path);
        if (script)
        {
            bvr['script'] = script;
            bvr.values = kwargs;
            spt.app_busy.show("Running Custom Check-in Script", kwargs.checkin_panel_script_path);
            setTimeout( function() {
            try {
                    spt.CustomProject.exec_custom_script(evt, bvr);
                }
            
            catch(e) {
                throw(e);
                spt.alert('No script found[' + bvr.checkin_panel_script_path + ']. <checkin_panel_script_path> display option should refer to a valid script path.');
            }

            spt.app_busy.hide();
            }, 50);
        }
        else {
            var layout = bvr.src_el.getParent(".spt_tool_top");
            if (layout != null) {
                var class_name = 'tactic.ui.widget.CheckinWdg';
                spt.app_busy.show("Loading ...");
                var layout = bvr.src_el.getParent(".spt_tool_top");
                var element = layout.getElement(".spt_tool_content");
                spt.panel.load(element, class_name, kwargs);
                spt.app_busy.hide();
            }
            else {
                var options=  {
                    title: "Check-in Widget",
                    class_name: 'tactic.ui.widget.CheckinWdg',
                    popup_id: 'checkin_widget'
                };
                var bvr2 = {};
                bvr2.options = options;
                bvr2.values = values;
                bvr2.args = kwargs;
                spt.popup.get_widget({}, bvr2)
                spt.app_busy.hide();
            }
        }
        '''



    def get_display(my):

        my.context = ''
        sobject = my.get_current_sobject()

        if sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
            my.process = sobject.get_value('process')
            my.context = sobject.get_value('context')
            if not my.process:
                my.process = ''


            sobject_mode = my.kwargs.get("sobject_mode")
            if not sobject_mode:
                sobject_mode = "parent"
            #sobject_mode = "connect"
            if sobject_mode == "parent":
                parent = sobject.get_parent()
            elif sobject_mode == "connect":
                parent = Search.eval("@SOBJECT(connect)", sobject, single=True)
            elif sobject_mode == "expression":
                expression = "???"
                parent = Search.eval("@SOBJECT(connect)", sobject, single=True)
            else:
                parent = sobject

            if not parent:
                return DivWdg()

            search_key = SearchKey.get_by_sobject(parent)
        else:
            my.process = my.get_option('process')
            search_key = SearchKey.get_by_sobject(sobject)


        #my.behavior['process'] = my.process
        #my.behavior['context'] = my.context
        #my.behavior['search_key'] = search_key

        # set the atrs
        div = super(CheckinButtonElementWdg, my).get_display()
        div.add_attr("spt_process", my.process)
        div.add_attr("spt_context", my.context)
        div.add_attr("spt_search_key", search_key)

        return div





class CheckoutButtonElementWdg(ButtonElementWdg):

    def get_display(my):

        mode = my.get_option('mode')
        size = my.get_option('icon_size')
        if mode == 'add':
            my.set_option('icon', "CHECK_OUT")
        else:
            if size == 'large':
	        my.set_option('icon', "CHECK_OUT_LG")
	    else:
	        my.set_option('icon', "CHECK_OUT_SM")


        top = DivWdg()
        icon = IconButtonWdg( "Checkout", eval( "IconWdg.%s" % my.get_option('icon') ) )
        top.add(icon)


        my.process = my.get_option('process')
        my.context = ''
        transfer_mode = my.get_option('transfer_mode')
        
        sobject = my.get_current_sobject()
        if sobject.get_id() == -1:
            sobject = None 


        snapshot_code = my.get_option("snapshot_code")
        sandbox_dir = my.get_option("sandbox_dir")
        if not sandbox_dir and sobject and isinstance(sobject, Snapshot):
            sandbox_dir = sobject.get_sandbox_dir(file_type='main')
   	    snapshot_code = sobject.get_code()
	 
        lock_process = my.get_option("lock_process")
        sobject = my.get_current_sobject()
        search_key = SearchKey.get_by_sobject(sobject)
        

        if sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
            my.process = sobject.get_value('process')
            my.context = sobject.get_value('context')
            if not my.process:
                my.process = ''

            parent = sobject.get_parent()
            if not parent:
                return DivWdg()
            search_key = SearchKey.get_by_sobject(parent)
        else:
            my.process = my.get_option('process')
            search_key = SearchKey.get_by_sobject(sobject)


        checkout_script_path = my.get_option("checkout_script_path")
        checkout_panel_script_path = my.get_option("checkout_panel_script_path")
        lock_process = my.get_option("lock_process")
        if not checkout_script_path:
            checkout_script_path = ''
        if not checkout_panel_script_path:
            checkout_panel_script_path = ''


        # FIXME: this does not get passed through 'cuz get_display is overridden here
        # so passed in directly in the script below
        my.behavior['checkout_panel_script_path'] = checkout_panel_script_path
        my.behavior['checkout_script_path'] = checkout_script_path
        my.behavior['process'] = my.process
        my.behavior['context'] = my.context

        my.behavior['lock_process'] = lock_process
        my.behavior['search_key'] = search_key
        my.behavior['snapshot_code'] = snapshot_code
        my.behavior['sandbox_dir'] = sandbox_dir

        my.behavior['transfer_mode'] = transfer_mode

        #layout_wdg = my.get_layout_wdg()
        #state = layout_wdg.get_state()

        cbjs_action = '''
        var kwargs = {
            search_key: '%(search_key)s',
            sandbox_dir: '%(sandbox_dir)s',
            process: '%(process)s',
            context: '%(context)s',
            lock_process: '%(lock_process)s',
            checkout_script_path: '%(checkout_script_path)s'
        };


        var transfer_mode = bvr.transfer_mode;
        if (!transfer_mode) {
            transfer_mode = spt.Environment.get().get_transfer_mode();
        }
        if (transfer_mode == null) {
            transfer_mode = 'web';
        }

        // NOTE: reusing checkin transfer mode
        if (transfer_mode == 'copy') {
            transfer_mode = 'client_repo';
        }

        var values = {};
        var top = bvr.src_el.getParent(".spt_checkin_top");
        script = spt.CustomProject.get_script_by_path(bvr.checkout_panel_script_path);
        if (script)
        {
            bvr['script'] = script;
            bvr.values = kwargs;
            spt.app_busy.show("Running Checkout Panel Script", kwargs.checkout_panel_script_path);
            setTimeout( function() {
            try {
                spt.CustomProject.exec_custom_script(evt, bvr);
            }
            catch(e) {
                throw(e);
                spt.alert('No script found. <checkout_panel_script_path> display option should refer to a valid script path.');
            }

            spt.app_busy.hide();
            }, 50);
        }
        else {
            if (bvr.snapshot_code) {
                if (!bvr.checkout_script_path){
                    

                    spt.app_busy.show("Checking out files", 'To: '+ bvr.sandbox_dir);
                
                    setTimeout( function() {
                        try {
                            var server = TacticServerStub.get();
                            file_types = ['main'];
                            filename_mode = 'source';
                            // we want this undefined so the checkout
                            // snapshot can deal with it correctly.  Explicitly
                            // putting in a dir will force it to go there,
                            // regardless of naming conventions
                            sandbox_dir = null;

                            server.checkout_snapshot(bvr.snapshot_code, sandbox_dir, {mode: transfer_mode, filename_mode: filename_mode, file_types: file_types} );
                            var checkin_top = bvr.src_el.getParent(".spt_checkin_top");
                            if (checkin_top) {
                                spt.app_busy.show("Reading file system ...")
                                spt.panel.refresh(checkin_top);
                                spt.app_busy.hide();
                            }

                        }
                        catch(e) {
                            spt.alert(spt.exception.handler(e));
                        }
                        spt.app_busy.hide();
                    }, 50);
                }
                else {
                    setTimeout( function() {
                    try {
                        bvr['script'] = bvr.checkout_script_path;
                        bvr.values = kwargs;
                        spt.CustomProject.exec_custom_script(evt, bvr);
                    }
                    catch(e) {
                        spt.alert(spt.exception.handler(e));
                    }
                    spt.app_busy.hide();
                    }, 50);
                }

            }
            else {
                var class_name = 'tactic.ui.widget.CheckoutWdg';
	   
	        var values = kwargs;
                bvr.values = values;
	        var search_key = values.search_key;
	        var sandbox_dir = values.sandbox_dir;
	        var process = values.process;
	        var context = values.context;

	        var options = { 'show_publish': 'false',
	       	  'process': process,
	       	  'context': context,
	       	    'search_key': search_key,
	       	    'checkout_script_path': bvr.checkout_script_path,
	       	    'sandbox_dir': sandbox_dir
	        };
	        var popup_id ='Check-out Widget';
	        spt.panel.load_popup(popup_id, class_name, options);
            }

        }
        ''' % (my.behavior)

        my.behavior['type'] = 'click_up'
        my.behavior['cbjs_action'] = cbjs_action

        icon.add_behavior(my.behavior)

        return top

class RecipientElementWdg(BaseTableElementWdg):

    def get_logins(my):
        sobject = my.get_current_sobject()
        id = sobject.get_id()

        search = Search("sthpw/notification_login")
        search.add_filter('notification_log_id', id)
        notification_logins = search.get_sobjects()
        return notification_logins
    
    def get_display(my):
        notification_logins = my.get_logins()

        table = Table()
        table.add_color("color", "color")

        for notification_login in notification_logins:
            type = notification_login.get_value("type")
            user = notification_login.get_value("login")
            table.add_row()
            table.add_cell(type)
            table.add_cell(user)

        return table

    def get_text_value(my):
        name_list = []
        notification_logins = my.get_logins()
        for notification_login in notification_logins:
            type = notification_login.get_value("type")
            user = notification_login.get_value("login")
            name_list.append('%s: %s' %(type, user))

        return '\n'.join(name_list)
