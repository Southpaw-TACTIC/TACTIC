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

import types, re, six

from pyasm.common import TacticException, Container, Date, jsonloads, jsondumps
from pyasm.search import Search, SearchKey, SObject
from pyasm.web import DivWdg, Widget, WebContainer, Table, HtmlElement, WikiUtil, SpanWdg
from pyasm.widget import IconWdg, TextWdg, TextAreaWdg, SelectWdg, ThumbWdg, PublishLinkWdg, IconButtonWdg, CheckboxWdg, SwapDisplayWdg, ProdIconButtonWdg
from pyasm.biz import Project, NamingUtil, ExpressionParser, Snapshot
from tactic.ui.common import BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.filter import FilterData
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg

class TypeTableElementWdg(SimpleTableElementWdg):
    '''The element widget that displays according to type'''


    def is_editable(self):
        return True

    def get_required_columns(self):
        return [self.name]

    def get_type(self):
        return self.type

    def handle_td(self, td):
        type = self.get_option("type")
        if not type:
            type = self.get_type()

        if type in ['float', 'int']:
            td.add_style("text-align: right")

        super(TypeTableElementWdg,self).handle_td(td)


    def get_text_value(self):
        type = self.get_option("type")
        if not type:
            type = self.get_type()
 
        if type in ['color', 'boolean','bigint', 'integer','float']:
            return self.get_value()
        else:
            return self.get_display()

    def get_display(self):
        value = self.get_value()
        name = self.get_name()

        type = self.get_option("type")
        if not type:
            type = self.get_type()

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
            if not isinstance(value, six.string_types):
                display = DivWdg()
                display.add_style("float: right")
                display.add_style("padding-right: 3px")
                display.add(str(value))
            else:
                display = value

        return display




class GeneralPublishElementWdg(BaseTableElementWdg):
    ''' A general publish table element with the option of having a thumbnail '''
    def get_arg_keys(self):
        return {'view': 'a custom view other than publish'}

    def preprocess(self):
        if self.get_option('preview') != 'false':
            self.thumb = ThumbWdg()
            self.thumb.set_sobjects(self.sobjects)
            self.thumb.set_icon_size(60)
            # passing options from this to ThumbWdg, shouldn't have conflicts
            options = self.options
            self.thumb.set_options(options)
        # for its own preprocess and data caching

    def get_display(self):
        self.view = self.kwargs.get('view')
        if not self.view:
            self.view = 'publish'
        widget = Widget()
        sobject = self.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        if self.get_option('preview') != 'false': 
            self.thumb.set_current_index(self.get_current_index())
            widget.add(self.thumb)

        publish_link = PublishLinkWdg(search_type,search_id, config_base=self.view) 
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

    def get_display(self):
        sobject = self.get_current_sobject()
        template = self.get_option("template")
        if not template:
            return super(SimpleTableElementWdg, self).__init__()

        display = NamingUtil.eval_template(template, sobject)
        self.value = display
        return display


__all__.append("ExpressionIsZeroElementWdg")
class ExpressionIsZeroElementWdg(BaseTableElementWdg):
    def get_display(self):
        sobject = self.get_current_sobject()
        expression = self.get_option("expression")

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
    def get_display(self):
        sobject = self.get_current_sobject()
        expression = self.get_option("expression")

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

    def _map_display_label(self):

        self.display_label = ''

        target_table = self.get_option("target_table")
        target_column = self.get_option("target_column")

        source_column = self.get_option("source_column")
        display_column = self.get_option("display_column")

        self.sobject = self.get_current_sobject()
        self.mapping_value = self.sobject.get_data().get( source_column )

        # do search here
        search = Search( target_table )
        search.add_filter( target_column, self.mapping_value)
        search.add_column( display_column )

        items = search.get_sobjects()
        if items:
            self.display_label = items[0].get_data().get( display_column )


    def get_display(self):

        self._map_display_label()
        div = DivWdg()
        div.add( '%s' % self.display_label )
        return div


    def handle_td(self, td):
        td.add_attr( "spt_input_value", self.value )


    def is_editable(self):
        return True

    def is_sortable(self):
        return True

    def is_groupable(self):
        return False


    def get_text_value(self):
        '''for csv export'''
        self._map_display_label()
        return self.display_label


    def set_td(self, td):
        self.td = td



class NotificationTriggerElementWdg(BaseTableElementWdg):

    def get_display(self):
         
        search_key = ''
        sobj = self.get_current_sobject()

        top = DivWdg() 
        top.add_style("padding-top: 5px")

        span = ActionButtonWdg(title="Email Test")
        #span = ProdIconButtonWdg('Email Test')
        top.add(span)
        span.add_behavior(self.get_behavior(sobj))


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

                   msg= msg.replace(/\\n/g, '<br/>');

                   var options = { 'html': '<div><div style="background:%s; padding: 5px">' + msg + '</div></div>'};
                   var kwargs = {'width':'600px'};
                   spt.panel.load_popup(popup_id, class_name, options, kwargs);
                   
                  ''' %(sobj_json, bg_color)}
        return bvr

from .button_wdg import ButtonElementWdg
class CheckinButtonElementWdg(ButtonElementWdg):

    ARGS_KEYS = {
    'transfer_mode': {
        'category': '1. Modes',
        'description': 'Mode by which files are transferred to the server',
        'type': 'SelectWdg',
        'order': 1,
        'values': 'upload|copy|move|local'
        },
     'use_applet': { 'type': 'SelectWdg',
            'category': '1. Modes',
            'values': 'true|false',
            'order': 2,
            'description': 'Determines which sobject to check into'},

      'mode': { 'type': 'SelectWdg',
            'category': '1. Modes',
            'order': 3,
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
     'checkin_options_view':  {'type': 'TextWdg',
            'category': '2. Display',
            'order': 9,
            'description': 'custom layout view which defines a custom check-in options UI to appear on the left side of the UI'}

     #'show_sub_context' : {'type': 'SelectWdg',
     #       'category': '2. Display',
     #       'values': 'true|false',
     #       'order': 9,
     #       'description': 'Determines whether to show the sub_context selector'},




    }

    #def init(self):
    #    return super(CheckinButtonElementWdg, self).init()


    def preprocess(self):

        mode = self.get_option('mode')

        width = self.get_option('width')
        size = self.get_option('icon_size')
        if mode == 'add':
            self.set_option('icon', "PUBLISH_MULTI")
        else:
            if size == 'large':
                self.set_option('icon', "PUBLISH_LG")
            else:
                self.set_option('icon', "PUBLISH")


        self.set_option("icon", "FA_UPLOAD")


        transfer_mode = self.get_option('transfer_mode')
        checkin_ui_options = self.get_option('checkin_ui_options')
        if not checkin_ui_options:
            checkin_ui_options = ''

        # do not preset it, let the auto-detection take care of it
        #if not transfer_mode:
        #    transfer_mode = 'upload'
        if not mode:
            mode = ''

        checkin_script = self.get_option("checkin_script")
        checkin_script_path = self.get_option("checkin_script_path")
        checkin_panel_script_path = self.get_option("checkin_panel_script_path")
        validate_script_path = self.get_option("validate_script_path")
        if not checkin_script:
            checkin_script = ''
        if not checkin_script_path:
            checkin_script_path = ''
        if not checkin_panel_script_path:
            checkin_panel_script_path = ''
        if not validate_script_path:
            validate_script_path = '' 

        lock_process = self.get_option("lock_process")
        if not lock_process:
            lock_process = ''
        sandbox_dir = self.get_option("sandbox_dir")
        if not sandbox_dir:
            sandbox_dir = ''

        checkin_relative_dir = self.get_option("checkin_relative_dir")

        if not checkin_relative_dir:
            checkin_relative_dir = ''


        show_context = self.get_option("show_context")
        show_sub_context = self.get_option("show_sub_context")

        use_applet = self.get_option("use_applet")
        if use_applet in ['true', True]:
            use_applet = True
        else:
            use_applet = False
        
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
        kwargs['use_applet'] = use_applet

        self.behavior['kwargs'] = kwargs
        self.behavior['cbjs_action'] = '''
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
                var table_layout = spt.table.get_layout();
                var popup = spt.popup.get_widget({}, bvr2);
                popup.layout = table_layout;
                spt.app_busy.hide();
            }
        }
        '''



    def get_display(self):

        self.context = ''
        sobject = self.get_current_sobject()

        if sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
            self.process = sobject.get_value('process')
            if not self.process:
                self.process = ''

            self.context = sobject.get_value('context')
            if re.search(r'/(\d+)$', self.context):
                self.context = ""



            sobject_mode = self.kwargs.get("sobject_mode")
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
            self.process = self.get_option('process')
            if not self.process:
                self.process = "publish"
            search_key = SearchKey.get_by_sobject(sobject)


        # set the atrs
        div = super(CheckinButtonElementWdg, self).get_display()
        div.add_attr("spt_process", self.process)
        div.add_attr("spt_context", self.context)
        div.add_attr("spt_search_key", search_key)

        return div





class CheckoutButtonElementWdg(ButtonElementWdg):

    def preprocess(self):
        mode = self.get_option('mode')
        size = self.get_option('icon_size')
        if mode == 'add':
            self.set_option('icon', "CHECK_OUT")
        else:
            if size == 'large':
                self.set_option('icon', "CHECK_OUT_LG")
            else:
                #self.set_option('icon', "CHECK_OUT_SM")
                self.set_option('icon', "FA_DOWNLOAD")


        #icon = IconButtonWdg( name="Checkout", icon=self.get_option('icon') )
        #top.add(icon)


        self.process = self.get_option('process')
        self.context = ''
        transfer_mode = self.get_option('transfer_mode')
        
        sobject = self.get_current_sobject()
        if sobject and sobject.get_id() == -1:
            sobject = None 

        if not sobject:
            return


        snapshot_code = self.get_option("snapshot_code")
        sandbox_dir = self.get_option("sandbox_dir")
        if not sandbox_dir and sobject and isinstance(sobject, Snapshot):
            sandbox_dir = sobject.get_sandbox_dir(file_type='main')
            snapshot_code = sobject.get_code()
	 
        lock_process = self.get_option("lock_process")
        sobject = self.get_current_sobject()
        search_key = SearchKey.get_by_sobject(sobject)
        

        if sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
            self.process = sobject.get_value('process')
            self.context = sobject.get_value('context')
            if not self.process:
                self.process = ''

            parent = sobject.get_parent()
            if not parent:
                return DivWdg()
            search_key = SearchKey.get_by_sobject(parent)
        else:
            self.process = self.get_option('process')
            search_key = SearchKey.get_by_sobject(sobject)


        checkout_script_path = self.get_option("checkout_script_path")
        checkout_panel_script_path = self.get_option("checkout_panel_script_path")
        lock_process = self.get_option("lock_process")
        if not checkout_script_path:
            checkout_script_path = ''
        if not checkout_panel_script_path:
            checkout_panel_script_path = ''


        # FIXME: this does not get passed through 'cuz get_display is overridden here
        # so passed in directly in the script below
        self.behavior['checkout_panel_script_path'] = checkout_panel_script_path
        self.behavior['checkout_script_path'] = checkout_script_path
        self.behavior['process'] = self.process
        self.behavior['context'] = self.context

        self.behavior['lock_process'] = lock_process
        self.behavior['search_key'] = search_key
        self.behavior['snapshot_code'] = snapshot_code
        self.behavior['sandbox_dir'] = sandbox_dir

        self.behavior['transfer_mode'] = transfer_mode

        #layout_wdg = self.get_layout_wdg()
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
            setTimeout( function() {
            try {
                spt.CustomProject.exec_custom_script(evt, bvr);
            }
            catch(e) {
                throw(e);
                spt.alert('No script found. <checkout_panel_script_path> display option should refer to a valid script path.');
            }

            }, 50);
        }
        else {
            if (bvr.snapshot_code) {
                if (!bvr.checkout_script_path){
                    spt.notify.show_message("Checking out files", 'To: '+ bvr.sandbox_dir);
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
                                spt.notify.show_message("Reading file system ...")
                                spt.panel.refresh(checkin_top);
                            }

                        }
                        catch(e) {
                            spt.alert(spt.exception.handler(e));
                        }
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
        ''' % (self.behavior)

        self.behavior['type'] = 'click_up'
        self.behavior['cbjs_action'] = cbjs_action

        self.add_behavior(self.behavior)


class RecipientElementWdg(BaseTableElementWdg):

    def get_logins(self):
        sobject = self.get_current_sobject()
        id = sobject.get_id()

        search = Search("sthpw/notification_login")
        search.add_filter('notification_log_id', id)
        notification_logins = search.get_sobjects()
        return notification_logins
    
    def get_display(self):
        notification_logins = self.get_logins()

        table = Table()
        table.add_color("color", "color")

        for notification_login in notification_logins:
            type = notification_login.get_value("type")
            user = notification_login.get_value("login")
            table.add_row()
            table.add_cell(type)
            table.add_cell(user)

        return table

    def get_text_value(self):
        name_list = []
        notification_logins = self.get_logins()
        for notification_login in notification_logins:
            type = notification_login.get_value("type")
            user = notification_login.get_value("login")
            name_list.append('%s: %s' %(type, user))

        return '\n'.join(name_list)
