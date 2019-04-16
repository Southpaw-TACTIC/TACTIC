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
__all__ = ["AdvancedSearchWdg", "AdvancedSearchKeywordWdg", "AdvancedSearchSaveWdg", "AdvancedSearchSavedSearchesWdg", "CustomSaveButtonsWdg"]

from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, HtmlElement
from pyasm.widget import CheckboxWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.filter import BaseFilterWdg, FilterData
from tactic.ui.input import LookAheadTextInputWdg


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
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .spt_save_top .save-row {
                display: flex;
                justify-content: center;
                padding: 5px 0;
            }

            .spt_save_top .spt_search_name_input {
                width: 380px;
                height: 35px;
                border-radius: 20px;
                border: 1px solid #ccc;
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


            ''')

        return styles


    def get_display(self):

        save_top = self.top
        save_top.add_class("spt_save_top")

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

        save_second_row = DivWdg()
        save_content.add(save_second_row)
        save_second_row.add_class("save-row")

        look_ahead_wdg = HtmlElement.text()
        save_second_row.add(look_ahead_wdg)
        look_ahead_wdg.add_class("spt_search_name_input")

        search_button = DivWdg("Save")
        save_second_row.add(search_button)
        search_button.add_class("search-button")
        search_button.add_class("hand")
        search_button.add_behavior( {
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_save_top");
            var input = top.getElement(".spt_search_name_input");
            var value = input.value;
            if (!value) {
                spt.alert("No view name specified");
                return;
            }
            spt.table.save_search(value, {personal: true});
            spt.notify.show_message("Search saved");
            '''
        } )

        save_third_row = DivWdg()
        save_content.add(save_third_row)
        save_third_row.add_class("save-row")
        save_third_row.add_style("margin-left: -110px;")

        my_searches_checkbox = CheckboxWdg("my_searches")
        save_third_row.add(my_searches_checkbox)

        save_third_row.add("<div style='margin: 0 20px 0 8px; display: flex; align-items: center;'>Save to <b style='margin-left: 5px'>My Searches</b></div>")

        shared_searches_checkbox = CheckboxWdg("shared_searches")
        save_third_row.add(shared_searches_checkbox)

        save_third_row.add("<div style='margin: 0 20px 0 8px; display: flex; align-items: center;'>Save to <b style='margin-left: 5px'>Shared Searches</b></div>")

        save_top.add(self.get_styles())

        return save_top




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

            .spt_saved_searches_top .spt_my_searches {
                display: flex;
                align-items: center;

                opacity: 1;
                transition: 0.25s;
            }

            .spt_saved_searches_top .spt_my_searches.gone {
                opacity: 0;
            }

            .spt_saved_searches_top .spt_my_searches_title {
                font-size: 14px;
                font-weight: 500;
            }

            .spt_saved_searches_top .spt_my_searches .fa {
                margin: 0 10px;
            }

            .spt_saved_searches_top .spt_my_searches_input {
                position: absolute;

                border: none;
                background: transparent;
                border-bottom: 2px solid #f4f4f4;
                opacity: 0;
                transition: 0.25s;
            }

            .spt_saved_searches_top .spt_my_searches_input.visible {
                opacity: 1;
            }

            .spt_saved_searches_top .spt_saved_searches_container {
                padding: 5px 20px 20px 20px;
                font-size: 11px;
            }

            .spt_saved_searches_top .spt_saved_search_item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;

                color: #bbb;
                padding: 5px 0;
            }

            .spt_saved_searches_top .spt_saved_search_label {
                width: 80%;

                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
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

        values = [x.get("view") for x in configs]
        labels = [x.get("title") or x.get("view") for x in configs]

        #################################################################

        saved_top = self.top
        saved_top.add_class("spt_saved_searches_top")

        ### saved searches header
        saved_header = DivWdg()
        saved_top.add(saved_header)
        saved_header.add_class("spt_saved_searches_header")

        #### my searches (dropdown)
        my_searches_wdg = DivWdg()
        saved_header.add(my_searches_wdg)
        my_searches_wdg.add_class("spt_my_searches")
        my_searches_wdg.add_class("hand")

        my_searches_title = DivWdg("My Searches")
        my_searches_wdg.add(my_searches_title)
        my_searches_title.add_class("spt_my_searches_title")

        my_searches_wdg.add("<i class='fa fa-angle-down'></i>")

        #### my searches (input)
        my_searches_search = DivWdg("<i class='fa fa-search'></i>")
        saved_header.add(my_searches_search)
        my_searches_search.add_class("spt_my_searches_search hand")

        my_searches_search.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let searches_top = bvr.src_el.getParent(".spt_saved_searches_top");
            let my_searches = searches_top.getElement(".spt_my_searches");
            let searches_input = searches_top.getElement(".spt_my_searches_input");

            searches_input.setStyle("display", "");
            searches_input.addClass("visible");
            my_searches.addClass("gone");

            spt.body.add_focus_element(searches_input);
            searches_input.focus();

            '''
            })

        my_searches_input = HtmlElement.text()
        saved_header.add(my_searches_input)
        my_searches_input.add_class("spt_my_searches_input")
        my_searches_input.add_style("display", "none")

        my_searches_input.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            let searches_top = bvr.src_el.getParent(".spt_saved_searches_top");
            let my_searches = searches_top.getElement(".spt_my_searches");

            bvr.src_el.on_complete = function(el) {
                el.removeClass("visible");
                my_searches.removeClass("gone");

                setTimeout(function(){
                    el.setStyle("display", "none");
                }, 250);
            }

            '''
            })

        my_searches_input.add_behavior({
            'type': 'keyup',
            'cbjs_action': '''

            let value = bvr.src_el.value;

            let searches_top = bvr.src_el.getParent(".spt_saved_searches_top");
            let search_items = searches_top.getElements(".spt_saved_search_item");

            search_items.forEach(function(search_item){
                if (search_item.hasClass("spt_template")) return;

                let label = search_item.getElement(".spt_saved_search_label");
                if (label.innerText.includes(value)) search_item.setStyle("display", "");
                else search_item.setStyle("display", "none");
            });

            '''
            })

        ### saved searches template item
        saved_searches_container = DivWdg()
        saved_top.add(saved_searches_container)
        saved_searches_container.add_class("spt_saved_searches_container")

        saved_search_item = DivWdg()
        saved_searches_container.add(saved_search_item)
        saved_search_item.add_class("spt_saved_search_item")
        saved_search_item.add_class("spt_template hand")

        saved_search_label = DivWdg("")
        saved_search_item.add(saved_search_label)
        saved_search_label.add_class("spt_saved_search_label")

        saved_search_delete = DivWdg("<i class='fa fa-trash'></i>")
        saved_search_item.add(saved_search_delete)
        saved_search_delete.add_class("spt_saved_search_delete")

        saved_top.add_behavior({
            'type': 'load',
            'values': values,
            'labels': labels,
            'cbjs_action': '''

            let container = bvr.src_el.getElement(".spt_saved_searches_container");
            let template = bvr.src_el.getElement(".spt_template");

            for (let i=0; i<bvr.values.length; i++) {
                let clone = spt.behavior.clone(template);
                let label = clone.getElement(".spt_saved_search_label");
                label.innerText = bvr.labels[i];
                clone.setAttribute("spt_value", bvr.values[i]);

                clone.removeClass("spt_template");

                container.appendChild(clone);
            }

            '''
            })

        saved_search_item.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            let value = bvr.src_el.getAttribute("spt_value");
            spt.table.load_search(value);

            '''
            })

        saved_top.add(self.get_styles())

        return saved_top


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

        buttons_container = self.top
        buttons_container.add_class("spt_advanced_search_buttons")
        self.add_relay_behaviors(buttons_container)

        # Save buttons
        save_buttons = DivWdg()
        buttons_container.add(save_buttons)
        save_buttons.add_class("save-buttons")

        save_button = DivWdg("Save")
        save_buttons.add(save_button)
        save_button.add_class("spt_save_button save-button enabled hand")
        save_button.add_style("margin-right: 5px;")

        save_as_button = DivWdg("Save As")
        save_buttons.add(save_as_button)
        save_as_button.add_class("spt_save_button save-button enabled hand ")

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
            'cbjs_action': '''

            let top = bvr.src_el.getParent(".spt_search_top");
            let overlay = top.getElement(".overlay");
            let saveTop = top.getElement(".spt_save_top");

            overlay.setStyle("display", "");
            overlay.addClass("visible");
            saveTop.addClass("visible");
            saveTop.getElement(".spt_save_title").innerText = bvr.src_el.innerText;

            '''
            })




