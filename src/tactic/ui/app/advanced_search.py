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
__all__ = ["AdvancedSearchWdg"]

from pyasm.web import DivWdg, HtmlElement

from tactic.ui.common import BaseRefreshWdg
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


            /* Look ahead and tags */
            .spt_advanced_search_top .spt_look_ahead_top {
                padding: 20px 20px 10px 20px;
            }

            .spt_advanced_search_top .spt_look_ahead_header {
                display: grid;
                grid-template-columns: auto 35px;
                grid-gap: 15px;
            }

            .spt_advanced_search_top .spt_look_ahead_header .info-icon {
                border-radius: 20px;
                margin: 5px;
                //border: 1px solid grey;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 15px;
            }

            .spt_advanced_search_top .spt_text_input_wdg {
                border-radius: 20px;
            }

            .spt_advanced_search_top .spt_search_tags {
                transition: 0.25s;
            }

            .spt_advanced_search_top .spt_search_tags.empty .spt_clear_tags {
                background: #grey;
            }

            .spt_advanced_search_top .spt_clear_tags {
                background: black;
                color: #f4f4f4;
            }

            .spt_advanced_search_top .search-tag {
                border-radius: 20px;
                display: inline-block;
                font-size: 12px;
                padding: 4px 10px;
                margin: 5px 5px 0 0;
            }

            .spt_advanced_search_top .search-tag:hover {
                box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.15);
            }

            .spt_advanced_search_top .spt_search_tag_item {
                position: relative;

                padding-right: 20px;
                background: #f4f4f4;
            }

            .spt_advanced_search_top .spt_search_tag_item .fa {
                position: absolute;
                right: 5;
                top: 5;

                cursor: pointer;
            }


            /* Seperator */
            .spt_advanced_search_top .seperator {
                height: 2px;
                margin: 0 15px;
                background: #f4f4f4;
            }


            /* Buttons */
            .spt_advanced_search_top .buttons {
                position: absolute;
                bottom: 0;

                display: flex;
                justify-content: space-between;
                align-items: center;

                padding: 10px 15px;
            }

            .spt_advanced_search_top .save-buttons {
                display: flex;
            }

            .spt_advanced_search_top .save-button {
                padding: 5px;
            }

            .spt_advanced_search_top .save-button.enabled:hover {
                //background: #f4f4f4;
            }


            /* Saved searches */
            .spt_advanced_search_top .spt_saved_searches_header {
                position: relative;
                
                display: flex;
                justify-content: space-between;
                align-items: center;

                margin: 22px 20px 20px 20px;
            }

            .spt_advanced_search_top .spt_my_searches {
                display: flex;
                align-items: center;

                opacity: 1;
                transition: 0.25s;
            }

            .spt_advanced_search_top .spt_my_searches.gone {
                opacity: 0;
            }

            .spt_advanced_search_top .spt_my_searches_title {
                font-size: 14px;
                font-weight: 500;
            }

            .spt_advanced_search_top .spt_my_searches .fa {
                margin: 0 10px;
            }

            .spt_advanced_search_top .spt_my_searches_input {
                position: absolute;

                border: none;
                background: transparent;
                border-bottom: 2px solid #f4f4f4;
                opacity: 0;
                transition: 0.25s;
            }

            .spt_advanced_search_top .spt_my_searches_input.visible {
                opacity: 1;
            }

            .spt_advanced_search_top .spt_saved_searches_container {
                padding: 5px 20px 20px 20px;
                font-size: 11px;
            }

            .spt_advanced_search_top .spt_saved_search_item {
                width: 100%;

                overflow: hidden;
                color: #bbb;
                text-overflow: ellipsis;
                white-space: nowrap;
                margin: 5px 0;
            }


            /* Save */
            .spt_advanced_search_top .spt_save_header {
                display: flex;
                justify-content: space-between;
                align-items: center;

                padding: 15px;
            }

            .spt_advanced_search_top .spt_save_close {

            }


            ''')

        return styles


    def get_display(self):

        top = self.top
        top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
            })
        self.set_relay_behaviors(top)

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
        look_ahead_top = self.get_search_display()
        search_filter_top.add(look_ahead_top)

        ### seperator
        seperator = DivWdg()
        search_filter_top.add(seperator)
        seperator.add_class("seperator")

        ### filters


        ### buttons
        buttons_container = DivWdg()
        search_filter_top.add(buttons_container)
        buttons_container.add_class("buttons")

        save_buttons = DivWdg()
        buttons_container.add(save_buttons)
        save_buttons.add_class("save-buttons")

        save_button = DivWdg("Save")
        buttons_container.add(save_button)
        save_button.add_class("spt_save_button save-button enabled hand")
        save_button.add_style("margin-right: 5px;")

        save_as_button = DivWdg("Save As")
        buttons_container.add(save_as_button)
        save_as_button.add_class("spt_save_button save-button enabled hand ")

        ## saved searches
        saved_top = self.get_saved_searches_display()
        search_top.add(saved_top)

        #############################################

        # overlay
        overlay = DivWdg()
        top.add(overlay)
        overlay.add_class("overlay")
        overlay.add_style("display", "none")

        #############################################

        # save/save as
        save_top = self.get_save_display()
        top.add(save_top)

        top.add(self.get_styles())

        return top


    def get_search_display(self):

        look_ahead_top = DivWdg()
        look_ahead_top.add_class("spt_look_ahead_top")

        look_ahead_header = DivWdg()
        look_ahead_top.add(look_ahead_header)
        look_ahead_header.add_class("spt_look_ahead_header")

        look_ahead_wdg = LookAheadTextInputWdg(name="keyword_search", width="100%", background="#f4f4f4")
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

            '''
            })

        return look_ahead_top


    def get_saved_searches_display(self):

        saved_top = DivWdg()
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

        ### saved searches template item
        saved_searches_container = DivWdg()
        saved_top.add(saved_searches_container)
        saved_searches_container.add_class("spt_saved_searches_container")

        saved_search_item = DivWdg("FILTER IEE")
        saved_searches_container.add(saved_search_item)
        saved_search_item.add_class("spt_saved_search_item")
        saved_search_item.add_class("spt_template hand")


        return saved_top


    def get_save_display(self):

        save_top = DivWdg()
        save_top.add_class("spt_save_top")

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

            let top = bvr.src_el.getParent(".spt_advanced_search_top");
            let overlay = top.getElement(".overlay");
            let saveTop = top.getElement(".spt_save_top");

            overlay.removeClass("visible");
            saveTop.removeClass("visible");
            setTimeout(function(){
                overlay.setStyle("display", "none");
            }, 250);

            '''
            })

        return save_top


    def set_relay_behaviors(self, top):

        top.add_relay_behavior({
            'type': 'click',
            'bvr_match_class': 'spt_save_button',
            'cbjs_action': '''

            let top = bvr.src_el.getParent(".spt_advanced_search_top");
            let overlay = top.getElement(".overlay");
            let saveTop = top.getElement(".spt_save_top");

            overlay.setStyle("display", "");
            overlay.addClass("visible");
            saveTop.addClass("visible");
            saveTop.getElement(".spt_save_title").innerText = bvr.src_el.innerText;

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

            let top = bvr.src_el.getParent(".spt_advanced_search_top");
            let tagsContainer = top.getElement(".spt_search_tags");
            let tagTemplate = tagsContainer.getElement(".spt_template");

            let clone = spt.behavior.clone(tagTemplate);
            clone.getElement(".spt_search_tag_label").innerText = "#"+display;
            clone.removeClass("spt_template");
            tagsContainer.appendChild(clone);

            tagsContainer.removeClass("empty");

            '''
            })


    def get_onload_js(self):

        return '''

spt.advanced_search = spt.advanced_search || {};


        '''






