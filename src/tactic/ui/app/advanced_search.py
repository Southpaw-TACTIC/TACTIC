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
__all__ = ["AdvancedSearchWdg", "AdvancedSearchKeywordWdg", "AdvancedSearchSaveWdg", "AdvancedSearchSavedSearchesWdg", "CustomSaveButtonsWdg",
"DeleteSavedSearchCmd", "SaveSearchCmd"]

from pyasm.common import Environment, Xml
from pyasm.command import Command
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, HtmlElement
from pyasm.widget import CheckboxWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.filter import BaseFilterWdg, FilterData
from tactic.ui.input import LookAheadTextInputWdg, TextInputWdg


class AdvancedSearchWdg(BaseRefreshWdg):

    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_advanced_search_top {
                position: relative;

                min-height: 300px;

                border-radius: 5px;
                overflow: hidden;
                box-shadow: 0px 2px 4px 0px #bbb;
                color: grey;
            }

            .spt_advanced_search_top .spt_template {
                display: none !important;
            }

            .spt_advanced_search_top .spt_search_top {
                display: flex;
                height: 300px;
            }

            .spt_advanced_search_top .overlay {
                position: absolute;
                top: 0;

                width: 100%;
                height: 100%;

                background-color: transparent;
                transition: 0.5s;
            }

            .spt_advanced_search_top .overlay.visible {
                background-color: rgba(0,0,0,0.4);
            }

            .spt_advanced_search_top .spt_save_top {
                position: absolute;
                top: 0px;
                right: -700px;

                width: 100%;
                height: 300px;

                background: #cecece;
                transition: 0.25s;
            }

            .spt_advanced_search_top .spt_save_top.visible {
                right: 0px;
            }

            .spt_advanced_search_top .spt_search_filters_top {
                position: relative;

                width: 500px;
                height: 100%;

                background: #cecece;
            }

            .spt_advanced_search_top .spt_saved_searches_top {
                width: 200px;
                height: 100%;

                background: #dbdbdb;
            }


            /* Seperator */
            .spt_advanced_search_top .seperator {
                height: 2px;
                margin: 0 15px;
                background: #f4f4f4;
            }

            ''')

        return styles


    def get_display(self):

        top = self.top
        top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
            })

        top.add_class("spt_advanced_search_top")

        # search and filters and saved searches
        search_top = DivWdg()
        top.add(search_top)
        search_top.add_class("spt_search_top")

        ## search and filters
        search_filter_top = DivWdg()
        search_top.add(search_filter_top)
        search_filter_top.add_class("spt_search_filters_top")

        ### look ahead
        look_ahead_top = AdvancedSearchKeywordWdg()
        search_filter_top.add(look_ahead_top)

        ### seperator
        seperator = DivWdg()
        search_filter_top.add(seperator)
        seperator.add_class("seperator")

        ### filters


        ### buttons
        buttons_container = CustomSaveButtonsWdg()
        search_filter_top.add(buttons_container)

        ## saved searches
        saved_top = AdvancedSearchSavedSearchesWdg()
        search_top.add(saved_top)

        #############################################

        # overlay
        overlay = DivWdg()
        top.add(overlay)
        overlay.add_class("overlay")
        overlay.add_style("display", "none")

        #############################################

        # save/save as
        save_top = AdvancedSearchSaveWdg()
        top.add(save_top)

        top.add(self.get_styles())

        return top


    def get_onload_js(self):

        return '''

spt.advanced_search = spt.advanced_search || {};


        '''



class AdvancedSearchKeywordWdg(BaseFilterWdg):


    def init(self):
        self.search_type = self.options.get("search_type")
        if not self.search_type:
            self.search_type = self.kwargs.get("search_type")

        stype_columns = SearchType.get_columns(self.search_type)

        self.columns = self.kwargs.get('columns')
        if self.columns:
            self.columns = self.columns.split('|')
        else: 
            self.columns = self.options.get("columns")
            if self.columns:
                self.columns = self.columns.split('|')

        if not self.columns:

            self.columns = []

            # need a way to specify the columns
            sobject = SearchType.create(self.search_type)
            if hasattr(sobject, 'get_search_columns'):
                self.columns = sobject.get_search_columns()

            self.columns.append('id')
            if 'code' in stype_columns:
                self.columns.append('code')

        
        self.prefix = self.kwargs.get("prefix")
        #self.text.set_persist_on_submit(prefix=self.prefix)
        #self.set_filter_value(self.text, filter_index)
        self.stype_columns = []
        self.text_value = ''


    def get_styles(self):

        styles = HtmlElement.style('''

            /* Look ahead and tags */
            .spt_look_ahead_top {
                padding: 20px 20px 10px 20px;
                color: grey;
            }

            .spt_look_ahead_top .spt_template {
                display: none !important;
            }

            .spt_look_ahead_top .spt_look_ahead_header {
                display: grid;
                grid-template-columns: auto 35px;
                grid-gap: 15px;
            }

            .spt_look_ahead_top .spt_look_ahead_header .info-icon {
                border-radius: 20px;
                margin: 5px;
                //border: 1px solid grey;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 15px;
            }

            .spt_look_ahead_top .spt_text_input_wdg {
                border-radius: 20px;
            }

            .spt_look_ahead_top .spt_search_tags {
                transition: 0.25s;
            }

            .spt_look_ahead_top .spt_search_tags.empty .spt_clear_tags {
                background: grey;
            }

            .spt_look_ahead_top .spt_clear_tags {
                background: black;
                color: #f4f4f4;
            }

            .spt_look_ahead_top .search-tag {
                border-radius: 20px;
                display: inline-block;
                font-size: 12px;
                padding: 4px 10px;
                margin: 5px 5px 0 0;
            }

            .spt_look_ahead_top .spt_search_tags:not(.empty) .search-tag:hover {
                box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.15);
            }

            .spt_look_ahead_top .spt_search_tag_item {
                position: relative;

                padding-right: 20px;
                background: #f4f4f4;
            }

            .spt_look_ahead_top .spt_search_tag_item .fa {
                position: absolute;
                right: 5;
                top: 5;

                cursor: pointer;
            }


            ''')

        return styles


    def get_display(self):

        look_ahead_top = self.top
        look_ahead_top.add_class("spt_look_ahead_top spt_search_filter")
        look_ahead_top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
            })
        self.add_relay_behaviors(look_ahead_top)

        look_ahead_header = DivWdg()
        look_ahead_top.add(look_ahead_header)
        look_ahead_header.add_class("spt_look_ahead_header")


        custom_cbk = {
            'enter': '''

            if (els && spt.text_input.index > -1)
                spt.advanced_search.keywords.add_keyword(bvr.src_el.value);

            '''
        }
        look_ahead_wdg = LookAheadTextInputWdg(name="", width="100%", background="#f4f4f4", custom_cbk=custom_cbk)
        look_ahead_header.add(look_ahead_wdg)

        info_wdg = DivWdg("<i class='fa fa-info'></i>")
        look_ahead_header.add(info_wdg)
        info_wdg.add_class("info-icon")
        info_wdg.add_class("hand")

        tag_cluster = DivWdg()
        look_ahead_top.add(tag_cluster)
        tag_cluster.add_class("spt_search_tags")
        # check if empty before adding this class
        tag_cluster.add_class("empty")

        clear_tags = DivWdg("Clear")
        tag_cluster.add(clear_tags)
        clear_tags.add_class("spt_clear_tags")
        clear_tags.add_class("search-tag hand")
        clear_tags.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let tagsContainer = bvr.src_el.getParent(".spt_search_tags");
            let items = tagsContainer.getElements(".spt_search_tag_item");

            items.forEach(function(item){
                if (item.hasClass("spt_template")) return;
                item.remove();
            })

            tagsContainer.addClass("empty");

            // extract and set keywords
            spt.advanced_search.keywords.set_keywords();

            '''
            })

        search_tag_item = DivWdg()
        tag_cluster.add(search_tag_item)
        search_tag_item.add_class("spt_search_tag_item")
        search_tag_item.add_class("spt_template search-tag")

        search_tag_label = DivWdg("#charHeroSimba")
        search_tag_item.add(search_tag_label)
        search_tag_label.add_class("spt_search_tag_label")

        search_tag_close = DivWdg("<i class='fa fa-times-circle'></i>")
        search_tag_item.add(search_tag_close)
        search_tag_close.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let tagsContainer = bvr.src_el.getParent(".spt_search_tags");
            let item = bvr.src_el.getParent(".spt_search_tag_item");
            item.remove();

            if (tagsContainer.childElementCount == 2)
                tagsContainer.addClass("empty");

            // extract and set keywords
            spt.advanced_search.keywords.set_keywords();

            '''
            })

        look_ahead_top.add('''<input type="hidden" name="prefix" value="%s" class="spt_input">''' % self.prefix)
        look_ahead_top.add('''<input type="hidden" name="%s_enabled" value="on" class="spt_input">''' % self.prefix)
        look_ahead_top.add('''<input type="hidden" name="%s_search_text" value="" class="spt_input spt_keywords">''' % self.prefix)
        look_ahead_top.add(self.get_styles())

        return look_ahead_top


    def get_onload_js(self):

        return '''

spt.advanced_search = spt.advanced_search || {};
spt.advanced_search.keywords = spt.advanced_search.keywords || {};

spt.advanced_search.keywords.add_keyword = function(display) {
    let tagsContainer = bvr.src_el.getElement(".spt_search_tags");
    let tagTemplate = tagsContainer.getElement(".spt_template");

    let clone = spt.behavior.clone(tagTemplate);
    clone.getElement(".spt_search_tag_label").innerText = "#"+display;
    clone.setAttribute("spt_value", display);
    clone.removeClass("spt_template");
    tagsContainer.appendChild(clone);

    tagsContainer.removeClass("empty");

    let textTop = bvr.src_el.getElement(".spt_input_text_top");
    let textInput = textTop.getElement(".spt_text_input");
    textInput.value = "";

    // extract and set keywords
    spt.advanced_search.keywords.set_keywords();
}

spt.advanced_search.keywords.extract_keywords = function() {
    let tagsContainer = bvr.src_el.getElement(".spt_search_tags");
    let items = tagsContainer.getElements(".spt_search_tag_item");
    let keywords = [];

    items.forEach(function(item){
        if (item.hasClass("spt_template")) return;
        keywords.push(item.getAttribute("spt_value"));
    })

    return keywords;
}

spt.advanced_search.keywords.set_keywords = function() {
    let keywords = spt.advanced_search.keywords.extract_keywords();
    let keywordsStorage = bvr.src_el.getElement(".spt_keywords");
    keywordsStorage.value = keywords.join(",");
}

        '''


    def add_relay_behaviors(self, top):

        top.add_behavior({
            'type': 'load',
            'values': self.get_value(),
            'cbjs_action': '''

            if (bvr.values) {
                let values = bvr.values.split(",");
                values.forEach(function(value) {
                    spt.advanced_search.keywords.add_keyword(value);
                });
            }

            '''
            })

        top.add_relay_behavior({
            'type': 'mouseup',
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''

            var display = bvr.src_el.getAttribute("spt_display");
            display = JSON.parse(display);
            var value = bvr.src_el.getAttribute("spt_value");
            if (!display) {
                display = value;
            }

            spt.advanced_search.keywords.add_keyword(display);

            '''
            })


    def get_value(self):

        filter_data = FilterData.get()
        values = filter_data.get_values_by_index(self.prefix, 0)
        return values.get("%s_search_text"%self.prefix)


    def alter_search(self, search):
        ''' customize the search here '''
        
        self.stype_columns = search.get_columns()
        
        values = FilterData.get().get_values_by_index(self.prefix, 0)
        # check if this filter is enabled
        enabled = values.get("%s_enabled" % self.prefix)
        value = self.get_value()

        if enabled == None:
            # by default, the filter is enabled
            is_enabled = True
        else:
            is_enabled = (str(enabled) in ['on', 'true'])

        if not is_enabled:
            return

        if is_enabled and value:
            self.num_filters_enabled += 1



        if not value:
            return
        self.text_value = value
        search.add_op("begin")

        for column in self.columns:
            if not column in self.stype_columns:
                continue

            # id and code should be exact matches
            if column == 'id':
                try:
                    search.add_filter(column, int(value))
                except ValueError:
                    pass
            elif column != 'keywords':
                search.add_filter(column, value)


        #filter_string = Search.get_compound_filter(value, self.columns)
        #if filter_string:
        #    search.add_where(filter_string)


        # add keywords
        column = 'keywords'
        if value and column in self.stype_columns:
            search.add_text_search_filter(column, value)

        search.add_op("or")



class AdvancedSearchSaveWdg(BaseRefreshWdg):

    def get_styles(self):

        styles = HtmlElement.style('''

            /* Save */
            .spt_save_top {
                display: grid;
                grid-template-rows: 40px auto;

                background: white;
                color: grey;
            }

            .spt_save_top .spt_save_header {
                display: flex;
                justify-content: space-between;
                align-items: center;

                background: black;
                padding: 15px;
                color: white;
            }

            .spt_save_top .spt_save_close {

            }

            .spt_save_top .spt_save_content {
                margin: auto;
            }

            .spt_save_top .save-row {
                display: flex;
                padding: 5px 0;
            }

            .spt_save_top .spt_search_name_input {
                width: 380px;
                height: 35px;
                border-radius: 20px;
                border: 1px solid #ccc;
                padding: 0 12px;
                background: #f4f4f4;
            }

            .spt_save_top .search-button {
                background: #eee;
                border-radius: 20px;
                margin-left: 15px;

                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0 20px;
            }

            .spt_save_top input[type='checkbox'] {
                margin: 0px !important;
            }

            .spt_save_top .spt_error_message {
                color: red;
                height: 14px;
            }


            ''')

        return styles


    def get_display(self):

        search_type = self.kwargs.get("search_type")

        save_top = self.top
        save_top.add_class("spt_save_top")
        save_top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
            })

        ## header
        save_header = DivWdg()
        save_top.add(save_header)
        save_header.add_class("spt_save_header")

        save_title = DivWdg("Save")
        save_header.add(save_title)
        save_title.add_class("spt_save_title")

        save_close = DivWdg("<i class='fa fa-times'></i>")
        save_header.add(save_close)
        save_close.add_class("spt_save_close")
        save_close.add_class("hand")

        save_close.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let top = bvr.src_el.getParent(".spt_search_top");
            let overlay = top.getElement(".overlay");
            let saveTop = top.getElement(".spt_save_top");

            overlay.removeClass("visible");
            saveTop.removeClass("visible");
            setTimeout(function(){
                overlay.setStyle("display", "none");
            }, 250);

            '''
            })

        ## content
        save_content = DivWdg()
        save_top.add(save_content)
        save_content.add_class("spt_save_content")

        save_first_row = DivWdg()
        save_content.add(save_first_row)
        save_first_row.add_class("spt_error_message")
        save_first_row.add_class("save-row")

        save_second_row = DivWdg()
        save_content.add(save_second_row)
        save_second_row.add_class("save-row")

        look_ahead_wdg = TextInputWdg(name="search_name", width="380px", background="#f4f4f4")
        save_second_row.add(look_ahead_wdg)
        look_ahead_wdg.add_class("spt_input spt_search_name_input")
        look_ahead_wdg.add_behavior({
            'type': 'keyup',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_save_top");
            var errorDiv = top.getElement(".spt_error_message");
            errorDiv.innerText = "";

            '''
            })

        search_button = DivWdg("Save")
        save_second_row.add(search_button)
        search_button.add_class("search-button")
        search_button.add_class("hand")
        search_button.add_behavior( {
            'search_type': search_type,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_save_top");
            var inputs = spt.api.get_input_values(top);
            var errorDiv = top.getElement(".spt_error_message");

            var value = inputs.search_name[0];
            if (!value) {
                spt.alert("No view name specified");
                return;
            }
            var save_personal = inputs.my_searches[0] == "on";
            var save_shared = inputs.shared_searches[0] == "on";

            //spt.table.save_search(value);

            var new_values = spt.advanced_search.generate_json();
            var search_values_dict = JSON.stringify(new_values);

            var options = {
                'search_type': bvr.search_type,
                'display': 'block',
                'view': value,
                'save_personal': save_personal,
                'save_shared': save_shared
            };

            // replace the search widget
            var server = TacticServerStub.get();

            let on_complete = function(ret_val) {
                spt.notify.show_message("Search saved");

                // DEPENDENCY?
                if (save_personal) {
                    let key = "my_searches";
                    spt.advanced_search.saved.create_item(key, value, value);
                    spt.advanced_search.saved.add_item(key, value, value);
                }
                if (save_shared) {
                    let key = "shared_searches";
                    spt.advanced_search.saved.create_item(key, value, value);
                    spt.advanced_search.saved.add_item(key, value, value);
                }
            }

            let on_error = function(err) {
                errorDiv.innerText = err;
            }

            var class_name = "tactic.ui.app.SaveSearchCmd";
            server.execute_cmd(class_name, options, search_values_dict, {on_complete: on_complete, on_error: on_error});

            '''
        } )

        save_third_row = DivWdg()
        save_content.add(save_third_row)
        save_third_row.add_class("save-row")

        my_searches_checkbox = CheckboxWdg(name="my_searches")
        save_third_row.add(my_searches_checkbox)

        save_third_row.add("<div style='margin: 0 20px 0 8px; display: flex; align-items: center;'>Save to <b style='margin-left: 5px'>My Searches</b></div>")

        shared_searches_checkbox = CheckboxWdg(name="shared_searches")
        save_third_row.add(shared_searches_checkbox)

        save_third_row.add("<div style='margin: 0 20px 0 8px; display: flex; align-items: center;'>Save to <b style='margin-left: 5px'>Shared Searches</b></div>")

        save_top.add(self.get_styles())

        return save_top


    def get_onload_js(self):

        return '''

spt.advanced_search = spt.advanced_search || {};

spt.advanced_search.generate_json = function() {
    var search_top = bvr.src_el.getParent(".spt_search_top");
    var new_values = [];
    if (search_top) {
        var search_containers = search_top.getElements('.spt_search_filter')
        for (var i = 0; i < search_containers.length; i++) {
            var values = spt.api.Utility.get_input_values(search_containers[i],null, false);
            new_values.push(values);
        }
        var ops = search_top.getElements(".spt_op");       // special code for ops
        var results = [];
        var levels = [];
        var modes = [];
        var op_values = [];
        for (var i = 0; i < ops.length; i++) {
            var op = ops[i];
            var level = op.getAttribute("spt_level");
            level = parseInt(level);
            var op_value = op.getAttribute("spt_op");
            results.push( [level, op_value] );
            var op_mode = op.getAttribute("spt_mode");
            levels.push(level);
            op_values.push(op_value);
            modes.push(op_mode);        }
        var values = {
            prefix: 'search_ops',
            levels: levels,
            ops: op_values,
            modes: modes
        };
        new_values.push(values);    
    }    // convert to json
    
    return new_values;

}

        '''



class SaveSearchCmd(Command):
    
    def init(self):
        # handle the default
        config = self.kwargs.get('config')
        self.search_type = self.kwargs.get("search_type")
        self.view = self.kwargs.get("view")
        assert(self.search_type)


    def execute(self):
        self.init()

        # create the filters
        self.filters = []

        config = "<config>\n"
        config += "<filter>\n"

        # get all of the serialized versions of the filters
        filter_data = FilterData.get()
        json = filter_data.serialize()
        value_type = "json"
        config += "<values type='%s'>%s</values>\n" % (value_type, json)
        config += "</filter>\n"
        config += "</config>\n"
        

        # format the xml
        xml = Xml()
        xml.read_string(config)


        if not self.view:
            saved_view = "saved_search:%s" % self.search_type
        else:
            saved_view = self.view
        #    if self.view.startswith("saved_search:"):
        #        saved_view = self.view
        #    else:
        #        saved_view = "saved_search:%s" % self.view

        save_personal = self.kwargs.get("save_personal")
        save_shared = self.kwargs.get("save_shared")
        save_overwrite = self.kwargs.get("save_overwrite");

        # use widget config instead
        search = Search('config/widget_config')
        search.add_filter("view", saved_view)
        search.add_filter("search_type", self.search_type)
        shared_config = search.get_sobject()
        
        search.add_user_filter()
        personal_config = search.get_sobject()


        if save_overwrite:
            config = shared_config if save_shared else personal_config
            config.set_value("config", xml.to_string())
            config.commit()
            return


        if save_shared:
            if shared_config:
                raise Exception("Shared search with name '%s' already exists." % saved_view)

            config = SearchType.create('config/widget_config')
            config.set_value("view", saved_view)
            config.set_value("search_type", self.search_type)

            config.set_value("category", "search_filter")
            config.set_value("config", xml.to_string())
            config.commit()

        if save_personal:
            if personal_config:
                raise Exception("My search with name '%s' already exists." % saved_view)

            config = SearchType.create('config/widget_config')
            config.set_value("view", saved_view)
            config.set_value("search_type", self.search_type)
            config.set_user()

            config.set_value("category", "search_filter")
            config.set_value("config", xml.to_string())
            config.commit()




class AdvancedSearchSavedSearchesWdg(BaseRefreshWdg):

    def get_styles(self):

        styles = HtmlElement.style('''

            /* Saved searches */
            .spt_saved_searches_top {

            }

            .spt_saved_searches_top .spt_template {
                display: none !important;
            }

            .spt_saved_searches_top .spt_saved_searches_header {
                position: relative;
                
                display: flex;
                justify-content: space-between;
                align-items: center;

                margin: 22px 20px 20px 20px;
            }

            .spt_saved_searches_top .spt_saved_searches {
                display: flex;
                align-items: center;

                opacity: 1;
                transition: 0.25s;
            }

            .spt_saved_searches_top .spt_saved_searches.gone {
                opacity: 0;
            }

            .spt_saved_searches_top .spt_saved_searches_title {
                font-size: 14px;
                font-weight: 500;
            }

            .spt_saved_searches_top .spt_saved_searches .fa {
                margin: 0 10px;
            }

            .spt_saved_searches_top .spt_saved_searches_input {
                position: absolute;

                border: none;
                background: transparent;
                border-bottom: 2px solid #f4f4f4;
                opacity: 0;
                transition: 0.25s;
            }

            .spt_saved_searches_top .spt_saved_searches_input.visible {
                opacity: 1;
            }

            .spt_saved_searches_top .spt_saved_searches_container {
                padding: 5px 0px 20px 0px;
                font-size: 11px;
            }

            .spt_saved_searches_top .spt_saved_searches_item {
                padding: 5px 0px 20px 0px;
                display: none;
            }

            .spt_saved_searches_top .spt_saved_searches_item.selected {
                display: block;
            }

            .spt_saved_searches_top .spt_saved_search_category {
                font-weight: 500;
                padding: 5px 20;
            }

            .spt_saved_searches_top .spt_saved_searches_container:not(.search) .spt_saved_search_category {
                display: none;
            }

            .spt_saved_searches_top .spt_saved_search_item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;

                color: #bbb;
                padding: 5px 20;
                box-sizing: border-box;
            }

            .spt_saved_searches_top .spt_saved_search_item:hover,
            .spt_saved_searches_top .spt_saved_search_item.selected {
                background: #eee
            }

            .spt_saved_searches_top .spt_saved_search_label {
                width: 80%;

                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .spt_saved_searches_top .spt_saved_search_item:hover .spt_saved_search_delete {
                display: block;
            }

            .spt_saved_searches_top .spt_saved_search_delete {
                display: none;
            }

            .spt_saved_searches_top .spt_saved_search_delete:hover {
                color: red;
            }

            .spt_saved_searches_top .spt_search_categories_dropdown {
                position: absolute;
                top: 30px;
                right: 40px;
                box-shadow: 0px 2px 4px 0px #bbb;
                border-radius: 3px;
                background: white;
            }

            .spt_saved_searches_top .spt_search_category {
                padding: 8px 20px;
                width: 130px;
            }

            .spt_saved_searches_top .spt_search_category:hover {
                background: #ccc;
            }


            ''')

        return styles


    def get_display(self):

        search_type = self.kwargs.get("search_type")

        search = Search("config/widget_config")
        search.add_op("begin")
        search.add_filter("view", 'saved_search:%', op="like")
        search.add_filter("category", 'search_filter')
        search.add_op("or")
        search.add_op("begin")
        search.add_user_filter()
        search.add_filter("login", "NULL", op="is", quoted=False)
        search.add_op("or")
        search.add_filter("search_type", search_type)
        configs = search.get_sobjects()

        categories = {
            "my_searches": "My Searches", 
            "shared_searches": "Shared Searches"
        }

        values = {
            "my_searches": [],
            "shared_searches": []
        }

        labels = {
            "my_searches": [],
            "shared_searches": []
        }

        user = Environment.get_user_name()
        for config in configs:

            login = config.get_value("login")
            if login == user:
                labels["my_searches"].append(config.get("view"))
                values["my_searches"].append(config.get("view"))
            else:
                labels["shared_searches"].append(config.get("view"))
                values["shared_searches"].append(config.get("view"))

        # values = [x.get("view") for x in configs]
        # labels = [x.get("title") or x.get("view") for x in configs]

        #################################################################

        saved_top = self.top
        saved_top.add_class("spt_saved_searches_top")
        saved_top.add_behavior({
            'type': 'load',
            'values': values,
            'labels': labels,
            'categories': categories,
            'cbjs_action': self.get_onload_js()
            })

        ### saved searches header
        saved_header = self.get_header()
        saved_top.add(saved_header)

        ### new container
        saved_searches_container = DivWdg()
        saved_top.add(saved_searches_container)
        saved_searches_container.add_class("spt_saved_searches_container")

        saved_searches_category_container = DivWdg()
        saved_searches_container.add(saved_searches_category_container)
        saved_searches_category_container.add_class("spt_saved_searches_item")
        saved_searches_category_container.add_class("spt_template")

        saved_searches_category = DivWdg()
        saved_searches_category_container.add(saved_searches_category)
        saved_searches_category.add_class("spt_saved_search_category")

        saved_search_item_container = DivWdg()
        saved_searches_category_container.add(saved_search_item_container)
        saved_search_item_container.add_class("spt_saved_search_item_container")

        saved_search_item = DivWdg()
        saved_search_item_container.add(saved_search_item)
        saved_search_item.add_class("spt_saved_search_item")
        saved_search_item.add_class("spt_template hand")

        saved_search_label = DivWdg("")
        saved_search_item.add(saved_search_label)
        saved_search_label.add_class("spt_saved_search_label")

        saved_search_delete = DivWdg("<i class='fa fa-trash'></i>")
        saved_search_item.add(saved_search_delete)
        saved_search_delete.add_class("spt_saved_search_delete")

        saved_item_action = self.kwargs.get("saved_item_action") or '''

            bvr.src_el.addClass("selected");

            let value = bvr.src_el.getAttribute("spt_value");
            spt.table.load_search(value);

            '''
        saved_search_item.add_behavior({
            'type': 'click',
            'cbjs_action': saved_item_action
            })

        saved_search_delete.add_behavior({
            'type': 'click',
            'search_type': search_type,
            'cbjs_action': '''

            let item = bvr.src_el.getParent(".spt_saved_search_item");

            let label = item.innerText;
            let value = item.getAttribute("spt_value");
            let key = item.getAttribute("spt_category");

            let server = TacticServerStub.get();
            let kwargs = {
                view: value,
                search_type: bvr.search_type,
                personal: key == "my_searches"
            }
            let classname = "tactic.ui.app.DeleteSavedSearchCmd";
            server.p_execute_cmd(classname, kwargs)
            .then(function(ret_val) {
                item.remove();
                spt.notify.show_message("Deleted");
                spt.advanced_search.saved.delete_item(key, label);
            });

            '''
            })

        saved_searches_container.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            let template = bvr.src_el.getElement(".spt_saved_searches_item");
            let itemTemplate = template.getElement(".spt_saved_search_item");
            let allValues = spt.advanced_search.saved.values;
            let allLabels = spt.advanced_search.saved.labels;
            let categories = spt.advanced_search.saved.categories;

            for (var key in categories) {
                let values = allValues[key];
                let labels = allLabels[key];

                let clone = spt.behavior.clone(template);
                let category = categories[key];
                let categoryDiv = clone.getElement(".spt_saved_search_category");
                categoryDiv.innerText = category;
                clone.setAttribute("spt_category", key);

                let container = clone.getElement(".spt_saved_search_item_container");

                for (let i=0; i<values.length; i++) {
                    let value = values[i];
                    let label = labels[i];

                    let itemClone = spt.behavior.clone(itemTemplate);
                    let labelDiv = itemClone.getElement(".spt_saved_search_label");
                    labelDiv.innerText = label;
                    itemClone.setAttribute("spt_value", value);
                    itemClone.setAttribute("spt_category", key);

                    itemClone.removeClass("spt_template");
                    container.appendChild(itemClone);
                }

                clone.removeClass("spt_template");
                bvr.src_el.appendChild(clone);
            }

            '''
            })

        saved_searches_container.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            spt.advanced_search.saved.load_items("my_searches");

            '''
            })

        saved_top.add(self.get_styles())

        return saved_top


    def get_onload_js(self):

        return '''

spt.advanced_search = spt.advanced_search || {};
spt.advanced_search.saved = spt.advanced_search.saved || {};

spt.advanced_search.saved.categories = bvr.categories;
spt.advanced_search.saved.values = bvr.values;
spt.advanced_search.saved.labels = bvr.labels;

spt.advanced_search.saved.add_item = function(key, label, value) {
    let container = bvr.src_el.getElement(".spt_saved_searches_container");
    let categoryContainer = container.querySelector("div.spt_saved_searches_item[spt_category='"+key+"']");
    let template = categoryContainer.getElement(".spt_saved_search_item.spt_template");

    let clone = spt.behavior.clone(template);
    let labelDiv = clone.getElement(".spt_saved_search_label");
    labelDiv.innerText = label;

    clone.setAttribute("spt_category", key);
    clone.setAttribute("spt_value", value);
    clone.removeClass("spt_template");
    categoryContainer.appendChild(clone);
}

spt.advanced_search.saved.create_item = function(key, label, value) {
    spt.advanced_search.saved.labels[key].push(label);
    spt.advanced_search.saved.values[key].push(value);
}

spt.advanced_search.saved.delete_item = function(key, label) {
    let index = spt.advanced_search.saved.labels[key].indexOf(label);
    spt.advanced_search.saved.labels[key].splice(index, 1);
    spt.advanced_search.saved.values[key].splice(index, 1);
}

spt.advanced_search.saved.load_items = function(key) {
    /*let values = spt.advanced_search.saved.get_values(key);
    let labels = spt.advanced_search.saved.get_labels(key);

    for (let i=0; i<values.length; i++) {
        let label = labels[i];
        let value = values[i];
        
        spt.advanced_search.saved.add_item(key, label, value);
    }*/

    let container = bvr.src_el.getElement(".spt_saved_searches_container");
    let selected = container.getElement(".spt_saved_searches_item.selected");
    let categoryContainer = container.querySelector("div.spt_saved_searches_item[spt_category='"+key+"']");
    if (selected) selected.removeClass("selected");
    categoryContainer.addClass("selected");
}

spt.advanced_search.saved.clear_items = function() {
    let container = bvr.src_el.getElement(".spt_saved_searches_container");
    let items = container.getElements(".spt_saved_search_item");

    items.forEach(function(item){
        if (item.hasClass("spt_template")) return;
        item.remove();
    });
}


spt.advanced_search.saved.toggle_dropdown = function(display) {
    let dropdown = bvr.src_el.getElement(".spt_search_categories_dropdown");

    if (display) 
        dropdown.setStyle("display", display);
    else
        spt.toggle_show_hide(dropdown);
}

spt.advanced_search.saved.get_values = function(key) {
    return spt.advanced_search.saved.values[key];
}

spt.advanced_search.saved.get_labels = function(key) {
    return spt.advanced_search.saved.labels[key];
}

spt.advanced_search.saved.get_selected = function() {
    return bvr.src_el.getElement(".spt_saved_search_item.selected");
}

        '''

    # TODO: make categories!!
    def get_header(self):

        saved_header = DivWdg()
        saved_header.add_class("spt_saved_searches_header")

        #### my searches (dropdown)
        saved_searches_wdg = DivWdg()
        saved_header.add(saved_searches_wdg)
        saved_searches_wdg.add_class("spt_saved_searches")
        saved_searches_wdg.add_class("hand")
        saved_searches_wdg.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            //spt.advanced_search.saved.toggle_dropdown();

            let header = bvr.src_el.getParent(".spt_saved_searches_header");
            let dropdown = header.getElement(".spt_search_categories_dropdown");
            spt.body.add_focus_element(dropdown);
            dropdown.setStyle("display", "");

            '''
            })

        searches_dropdown = DivWdg()
        saved_header.add(searches_dropdown)
        searches_dropdown.add_class("spt_search_categories_dropdown")
        searches_dropdown.add_style("display: none")

        searches_dropdown.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            bvr.src_el.on_complete = function(el) {
                bvr.src_el.setStyle("display", "none");
            };

            let header = bvr.src_el.getParent(".spt_saved_searches_header");
            let dropdown = header.getElement(".spt_search_categories_dropdown");
            let template = header.getElement(".spt_template");

            let categories = spt.advanced_search.saved.categories;

            for (var key in categories) {
                let label = categories[key];
                let value = key;

                let clone = spt.behavior.clone(template);
                clone.innerText = label;
                clone.setAttribute("spt_value", value);
                clone.removeClass("spt_template");

                dropdown.appendChild(clone);
            }

            '''
            })

        searches_dropdown_item = DivWdg()
        searches_dropdown.add(searches_dropdown_item)
        searches_dropdown_item.add_class("spt_search_category")
        searches_dropdown_item.add_class("spt_template hand")
        searches_dropdown_item.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let header = bvr.src_el.getParent(".spt_saved_searches_header");
            let dropdown = header.getElement(".spt_search_categories_dropdown");
            let title = header.getElement(".spt_saved_searches_title");
            let value = bvr.src_el.getAttribute("spt_value");
            let label = bvr.src_el.innerText;

            title.innerText = label;

            //spt.advanced_search.saved.clear_items();
            spt.advanced_search.saved.load_items(value);

            spt.body.remove_focus_element(dropdown);
            dropdown.on_complete();

            '''
            })

        saved_searches_title = DivWdg("My Searches")
        saved_searches_wdg.add(saved_searches_title)
        saved_searches_title.add_class("spt_saved_searches_title")

        saved_searches_wdg.add("<i class='fa fa-angle-down'></i>")

        #### my searches (input)
        saved_searches_search = DivWdg("<i class='fa fa-search'></i>")
        saved_header.add(saved_searches_search)
        saved_searches_search.add_class("spt_saved_searches_search hand")

        saved_searches_search.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let searches_top = bvr.src_el.getParent(".spt_saved_searches_top");
            let saved_searches = searches_top.getElement(".spt_saved_searches");
            let searches_input = searches_top.getElement(".spt_saved_searches_input");

            searches_input.setStyle("display", "");
            searches_input.addClass("visible");
            saved_searches.addClass("gone");

            spt.body.add_focus_element(searches_input);
            searches_input.focus();

            '''
            })

        saved_searches_input = HtmlElement.text()
        saved_header.add(saved_searches_input)
        saved_searches_input.add_class("spt_saved_searches_input")
        saved_searches_input.add_style("display", "none")

        saved_searches_input.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            let searches_top = bvr.src_el.getParent(".spt_saved_searches_top");
            let saved_searches = searches_top.getElement(".spt_saved_searches");

            bvr.src_el.on_complete = function(el) {
                let top = bvr.src_el.getParent(".spt_saved_searches_top");
                let container = top.getElement(".spt_saved_searches_container");
                container.removeClass("search");

                let searchesItems = top.getElements(".spt_saved_searches_item");
                searchesItems.forEach(function(searchesItem) {
                    searchesItem.setStyle("display", "");

                    let searchItems = searchesItem.getElements(".spt_saved_search_item");
                    searchItems.forEach(function(searchItem){
                        searchItem.setStyle("display", "");
                    });
                });

                el.removeClass("visible");
                saved_searches.removeClass("gone");

                setTimeout(function(){
                    el.setStyle("display", "none");
                }, 250);
            }

            '''
            })

        saved_searches_input.add_behavior({
            'type': 'keyup',
            'cbjs_action': '''

            let value = bvr.src_el.value;

            let top = bvr.src_el.getParent(".spt_saved_searches_top");
            let container = top.getElement(".spt_saved_searches_container");
            container.addClass("search");

            let searchesItems = top.getElements(".spt_saved_searches_item");
            searchesItems.forEach(function(searchesItem) {
                let searchItems = searchesItem.getElements(".spt_saved_search_item");
                let display = "none";
                searchItems.forEach(function(searchItem){
                    if (searchItem.hasClass("spt_template")) return;

                    let label = searchItem.getElement(".spt_saved_search_label");
                    if (label.innerText.includes(value)) {
                        searchItem.setStyle("display", "");
                        display = "block";
                    } else searchItem.setStyle("display", "none");
                });
                searchesItem.setStyle("display", display);
            });

            '''
            })

        return saved_header






class DeleteSavedSearchCmd(Command):

    def execute(self):

        view = self.kwargs.get("view")
        search_type = self.kwargs.get("search_type")
        personal = self.kwargs.get("personal")

        search = Search("config/widget_config")
        # search.add_op("begin")
        search.add_filter("view", view)
        search.add_filter("category", 'search_filter')
        # search.add_op("or")
        # search.add_op("begin")
        if personal:
            search.add_user_filter()
        else:
            search.add_filter("login", "NULL", op="is", quoted=False)
        # search.add_op("or")
        search.add_filter("search_type", search_type)
        config = search.get_sobject()

        self.info['deleted'] = False
        if config:
            config.delete()
            self.info['deleted'] = True



class CustomSaveButtonsWdg(BaseRefreshWdg):

    def get_styles(self):

        styles = HtmlElement.style('''

            /* Buttons */
            .spt_advanced_search_buttons {
                display: flex;
                justify-content: space-between;
                align-items: center;

                padding: 10px 15px;
                width: 100%;
                box-sizing: border-box;
            }

            .spt_advanced_search_buttons .save-buttons {
                display: flex;
            }

            .spt_advanced_search_buttons .save-button {
                padding: 5px;
            }

            .spt_advanced_search_buttons .save-button.enabled:hover {
                //background: #f4f4f4;
            }

            .spt_advanced_search_buttons .spt_search_button {
                background: #999;
                color: #f4f4f4;
                border-radius: 3px;
                padding: 6px 14px;
            }


            ''')

        return styles

    def get_display(self):

        prefix = self.kwargs.get("prefix")
        mode = self.kwargs.get("mode")

        buttons_container = self.top
        buttons_container.add_class("spt_advanced_search_buttons")
        self.add_relay_behaviors(buttons_container)

        # Save buttons
        save_buttons = DivWdg()
        buttons_container.add(save_buttons)
        save_buttons.add_class("save-buttons")

        save_button = DivWdg("Save")
        save_buttons.add(save_button)
        save_button.add_class("spt_save_button spt_save save-button enabled hand")
        save_button.add_style("margin-right: 5px;")

        save_as_button = DivWdg("Save As")
        save_buttons.add(save_as_button)
        save_as_button.add_class("spt_save_button spt_save_as save-button enabled hand ")
        save_as_button.add_attr("spt_action", "save_as")

        if mode == "save":
            save_button.add_attr("spt_action", "save_as")
            save_as_button.add_style("display: none")
        else:
            save_button.add_attr("spt_action", "save")

        # Search button
        search_button = DivWdg("Search")
        buttons_container.add(search_button)
        search_button.add_class("spt_search_button")
        search_button.add_class("hand")

        search_action = self.kwargs.get("search_action") or 'spt.dg_table.search_cbk(evt, bvr)'
        search_button.add_behavior({
                'type':         'click_up',
                'new_search':   True,
                'cbjs_action':  search_action,
                'panel_id':     prefix,
                
            })

        buttons_container.add(self.get_styles())

        return buttons_container

    def add_relay_behaviors(self, top):

        top.add_relay_behavior({
            'type': 'click',
            'bvr_match_class': 'spt_save_button',
            'search_type': self.kwargs.get("search_type"),
            'cbjs_action': '''

            let action = bvr.src_el.getAttribute("spt_action");

            if (action == "save_as") {
                let top = bvr.src_el.getParent(".spt_search_top");
                let overlay = top.getElement(".overlay");
                let saveTop = top.getElement(".spt_save_top");

                overlay.setStyle("display", "");
                overlay.addClass("visible");
                saveTop.addClass("visible");
                saveTop.getElement(".spt_save_title").innerText = bvr.src_el.innerText;
            } else if (action == "save") {
                var selected = spt.advanced_search.saved.get_selected();
                if (!selected) {
                    spt.alert("No search item selected");
                    return;
                }

                var save_personal = selected.getAttribute("spt_category") == "my_searches";
                var save_shared = !save_personal;
                var value = selected.getAttribute("spt_value");

                var new_values = spt.advanced_search.generate_json();
                var search_values_dict = JSON.stringify(new_values);

                var options = {
                    'search_type': bvr.search_type,
                    'display': 'block',
                    'view': value,
                    'save_personal': save_personal,
                    'save_shared': save_shared,
                    'save_overwrite': true
                };

                // replace the search widget
                var server = TacticServerStub.get();

                let on_complete = function(ret_val) {
                    spt.notify.show_message("Search saved");
                }

                var class_name = "tactic.ui.app.SaveSearchCmd";
                server.execute_cmd(class_name, options, search_values_dict, {on_complete: on_complete});
            }

            '''
            })



