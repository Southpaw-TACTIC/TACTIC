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

__all__ = ['SearchLimitWdg', 'SearchLimitSimpleWdg']

from pyasm.common import Environment
from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, SpanWdg, Table
from pyasm.widget import HiddenWdg, SubmitWdg, SelectWdg, TextWdg, IconSubmitWdg, IconWdg, SwapDisplayWdg
from tactic.ui.filter import FilterData
from tactic.ui.common import BaseRefreshWdg

from tactic.ui.widget import IconButtonWdg
       
class SearchLimitWdg(Widget):
    DETAIL = "detail_style"
    LESS_DETAIL = "less_detail_style"
    SIMPLE = "simple_style"

    def __init__(my, name='search_limit', label="Showing", limit=None, refresh=True):

        my.search_limit_name = name
        my.label = label
        my.search_limit = limit
        my.fixed_offset = False
        my.style = my.DETAIL
        my.prefix = "search_limit"
        my.refresh = refresh
        my.refresh_script = 'spt.dg_table.search_cbk(evt, bvr)'
        if my.refresh:
            my.prev_hidden_name = 'Prev'
            my.next_hidden_name='Next'
        else:
            my.prev_hidden_name = '%s_Prev' %my.label
            my.next_hidden_name = '%s_Next' %my.label


        my.chunk_size = 0
        my.chunk_num = 0

        super(SearchLimitWdg, my).__init__()
        
    def init(my):
        my.current_offset = 0
        my.count = None
        #my.text = TextWdg(my.search_limit_name)
        my.text = HiddenWdg(my.search_limit_name)
        my.text.add_style("width: 23px")
        my.text.add_style("margin-bottom: -1px")
        my.text.add_class("spt_search_limit_text")
        my.text.set_persist_on_submit(prefix=my.prefix)

        behavior = {
                'type': 'keydown',
                'cbjs_action': '''
                 if (evt.key=='enter') {
                    // register this as changed item
                    var value = bvr.src_el.value;
                    
                        if (isNaN(value) || value.test(/[\.-]/)) {
                            spt.error('You have to use an integer.');
                        }
                }
        '''}

        my.text.add_behavior(behavior)

        # get the search limit that is passed in
        filter_data = FilterData.get()
        values = filter_data.get_values_by_prefix(my.prefix)
        if not values:
            # check web for embedded table
            web = WebContainer.get_web()
            values = {}
            limit_value = web.get_form_value("search_limit")
            label_value = web.get_form_value(my.label)
            if limit_value:
                values['search_limit'] = limit_value
            if label_value:
                values[my.label] = label_value
        else:
            values = values[0]


        my.values2 = filter_data.get_values_by_prefix("search_limit_simple")
        if not len(my.values2):
            my.values2 = {}
        else:
            my.values2 = my.values2[0]


        my.stated_search_limit = values.get("search_limit")
        """
        if not my.stated_search_limit:
            my.stated_search_limit = values.get("limit_select")
        if not my.stated_search_limit:
            my.stated_search_limit = values.get("custom_limit")
        """
        if my.stated_search_limit:
            my.stated_search_limit = int(my.stated_search_limit)
        else:
            my.stated_search_limit = 0
      
        # reused for alter_search() later
        my.values = values
       
    def set_refresh_script(my, script):
        my.refresh_script = script

    def set_label(my, label):
        my.label = label

    def get_limit(my):
        return my.search_limit

    def get_stated_limit(my):
        return my.stated_search_limit


    def get_count(my):
        return my.count


    def set_limit(my, limit):
        my.search_limit = limit
        # this is user defined, should be set in init() instead
        #my.stated_search_limit = limit
 

    def set_offset(my, offset):
        my.fixed_offset = True
        my.current_offset = offset


    def set_style(my, style):
        my.style = style


    def set_chunk(my, chunk_size, chunk_num, limit=None):
        my.chunk_size = chunk_size
        my.chunk_num = chunk_num
        if limit:
            my.search_limit = limit
        else:
            # avoid undefined chunk_size
            if chunk_size:
                my.search_limit = chunk_size

        # to avoid 0 limit on undefined search limit in fast table
        if my.search_limit == 0:
            my.search_limit = 50
        

    def alter_search(my, search):
        if not search:
            return
        my.set_search(search)
        security = Environment.get_security()
        # allow security to alter the search
        security.alter_search(search)
        search.set_security_filter()

        my.count = search.get_count()

        web = WebContainer.get_web()

        values = my.values
        vaelus2 = my.values2

        # look at the stated search limit only if there is no chunk_size
        if not my.chunk_size:
            search_limit = my.stated_search_limit
            if search_limit:
                try:
                    my.search_limit = int(search_limit)
                except ValueError:
                    my.search_limit = 20
                if my.search_limit <= 0:
                    my.search_limit = 1
            elif my.search_limit:
                # this usually happens with search_limit set in side bar or kwarg for TableLayoutWdg
                pass
            else:
                # for backward compatibility with the default chunk size of 100
                my.search_limit = 100

        
        # find out what the last offset was
        #last_search_offset = web.get_form_value("last_search_offset")
        last_search_offset = values.get("%s_last_search_offset"%my.label)
        if last_search_offset:
            last_search_offset = int(last_search_offset)
        else:
            last_search_offset = 0
        # based on the action, set the new offset
        #if web.get_form_value("Next"):
        # FIXME: Next Prev not working for embedded tables yet


        # look at various values to change the search criteria
        page = my.values2.get("page")
        if page:
            current_offset = my.search_limit * (int(page)-1)

        elif values.get("Next"):
            current_offset = last_search_offset + my.search_limit
            if current_offset >= my.count:
                current_offset = 0

        #elif web.get_form_value("Prev"):
        elif values.get("Prev"):
            current_offset = last_search_offset - my.search_limit
            if current_offset < 0:
                current_offset = int(my.count/my.search_limit) * my.search_limit




      
        # this happens when the user jumps from Page 3 of a tab to a tab that
        # doesn't really need this widget
        elif last_search_offset > my.count:
            current_offset = 0
        elif values.get(my.label):
            value = values.get(my.label)
            if not value.startswith("+"):
                current_offset, tmp = value.split(" - ")
                current_offset = int(current_offset) - 1
            else:
                current_offset = 0
        else:
            current_offset = 0 

        if my.fixed_offset == False:
            my.current_offset = current_offset


        # add ability to break search limit search into chunks
        my.current_offset = my.current_offset

        if my.chunk_num:
            my.current_offset = last_search_offset + (my.chunk_num*my.chunk_size)
      
       
        if my.search_limit >= 0:
            my.search.set_limit(my.search_limit)
        my.search.set_offset(my.current_offset)


    def get_info(my):

        return {
            "count": my.count,
            "current_offset": my.current_offset,
            "search_limit": my.search_limit,
        }



    def get_display(my):

        web = WebContainer.get_web()

        widget = DivWdg()
        widget.add_class("spt_search_limit_top")
        #widget.add_style("border", "solid 1px blue")
        widget.add_color("background", "background")
        widget.add_color("color", "color")
        widget.add_style("padding: 10px")

        hidden = HiddenWdg("prefix", my.prefix)
        widget.add(hidden)

   
        if not my.search and not my.sobjects:
            widget.add("No search or sobjects found")
            return widget

        # my.count should have been set in alter_search()
        # which can be called explicitly thru this instance, my.
        if not my.count:
            my.count = my.search.get_count(no_exception=True)
        
        # if my.sobjects exist thru inheriting from parent widgets
        # or explicitly set, (this is not mandatory though)
        if my.sobjects and len(my.sobjects) < my.search_limit:
            limit = len(my.sobjects)
        elif my.search and my.count < my.search_limit:
            # this is only true if the total result of the search is 
            # less than the limit and so this wdg will not display
            limit = my.count
        else:
            limit = my.search_limit

        if not limit:
            limit = 50
            my.search_limit = limit

    
        if my.refresh: 
            prev = SpanWdg( IconButtonWdg(title="Prev", icon="BS_CHEVRON_LEFT") )
            prev.add_style("margin-left: 8px")
            prev.add_style("margin-right: 6px")
            prev.add_style("margin-top: 5px")

            next = SpanWdg( IconButtonWdg(title="Next", icon="BS_CHEVRON_RIGHT" ))
            next.add_style("margin-left: 6px")
            next.add_style("margin-top: 5px")

            prev.add_behavior( {
                'type': 'click_up',
                'cbjs_action': my.refresh_script
            } )
            next.add_behavior( {
                'type': 'click_up',
                'cbjs_action': my.refresh_script
            } )

            prev.add_style("float: left")
            next.add_style("float: left")

        else: # the old code pre 2.5
            prev = IconButtonWdg(title="Prev", icon="BS_CHEVRON_LEFT" )
            hidden_name = my.prev_hidden_name
            hidden = HiddenWdg(hidden_name,"")
            prev.add(hidden)
            prev.add_event('onclick'," spt.api.Utility.get_input(document,'%s').value ='Prev';%s"\
                    %(hidden_name, my.refresh_script))
            next = IconButtonWdg(title="Next", icon="BS_CHEVRON_RIGHT" )
            hidden_name = my.next_hidden_name
            hidden = HiddenWdg(hidden_name,"")
            next.add(hidden)
            next.add_event('onclick',"spt.api.Utility.get_input(document,'%s').value ='Next';%s" \
                    %(hidden_name, my.refresh_script))


        showing_wdg = DivWdg()
        widget.add(showing_wdg)
        showing_wdg.add_style("padding: 20px")
        showing_wdg.add_style("margin: 10px")
        showing_wdg.add_color("background", "background", -5)
        #showing_wdg.add_color("text-align", "center")
        showing_wdg.add_border()

        label_span = SpanWdg("Showing: ")
        showing_wdg.add(label_span)
        showing_wdg.add("<br clear='all'/>")
        showing_wdg.add("<br/>")
        showing_wdg.add( prev )
       

        # this min calculation is used so that if my.sobjects is not set
        # above for the calculation of the limit, which will make the last 
        # set of range numbers too big
        
        left_bound = my.current_offset+1
        if not limit:
            # prevent error in ItemsNavigatorWdg if a search encounters query error
            limit = 50
            my.search_limit = limit

        right_bound = min(my.current_offset+limit, my.count)
        if left_bound > right_bound:
            left_bound = 1
        current_value = "%d - %d" % (left_bound, right_bound)

        if my.style == my.SIMPLE:
            showing_wdg.add( current_value )
        else:
            # add a range selector using ItemsNavigatorWdg
            from pyasm.widget import ItemsNavigatorWdg
            selector = ItemsNavigatorWdg(my.label, my.count, my.search_limit)
            selector.select.add_behavior( {
                'type': 'change',
                'cbjs_action': my.refresh_script
            } )

            selector.set_style(my.style)
            selector.select.add_style("width: 100px")
            #selector.add_style("display: inline")
            selector.add_style("float: left")

            selector.set_value(current_value)
            selector.set_display_label(False)

            showing_wdg.add( selector) 

        showing_wdg.add( next )


        showing_wdg.add("<br clear='all'/>")
        showing_wdg.add("<br clear='all'/>")


        #showing_wdg.add( " x ")
        showing_wdg.add(my.text)
        my.text.add_style("margin-top: -3px")
        my.text.set_attr("size", "1")
        my.text.add_attr("title", "Set number of items per page")


        # set the limit
        set_limit_wdg = my.get_set_limit_wdg()
        widget.add(set_limit_wdg)


        from tactic.ui.widget.button_new_wdg import ActionButtonWdg
        button = ActionButtonWdg(title='Search')
        widget.add(button)
        button.add_style("float: right")
        button.add_style("margin-top: 8px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_search_limit_top");
            var select = top.getElement(".spt_search_limit_select");
            var value = select.value;
            if (value == 'Custom') {
                custom = top.getElement(".spt_search_limit_custom_text");
                value = custom.value;
            }
            if (value == '') {
                value = 20;
            }
            var text = top.getElement(".spt_search_limit_text");
            text.value = value;

            spt.dg_table.search_cbk({}, bvr) 
            '''
        } )


        offset_wdg = HiddenWdg("%s_last_search_offset" %my.label)
        offset_wdg.set_value(my.current_offset)
        widget.add(offset_wdg)

        widget.add("<br clear='all'/>")
 
        return widget


    def get_set_limit_wdg(my):
        limit_content = DivWdg()
        limit_content.add_style("font-size: 10px")
        limit_content.add_style("padding", "15px")
        #limit_content.add_border()

        limit_content.add("Show ")

        limit_select = SelectWdg("limit_select")
        limit_select.add_class("spt_search_limit_select")
        limit_select.set_option("values", "10|20|50|100|200|Custom")
        limit_select.add_style("font-size: 10px")
        limit_content.add(limit_select)
        limit_content.add(" items per page<br/>")

        if my.search_limit in [10,20,50,100,200]:
            limit_select.set_value(my.search_limit)
            is_custom = False
        else:
            limit_select.set_value("Custom")
            is_custom = True

        limit_select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_search_limit_top");
            var value = bvr.src_el.value;
            var custom = top.getElement(".spt_search_limit_custom");
            if (value == 'Custom') {
                custom.setStyle("display", "");
            }
            else {
                custom.setStyle("display", "none");
            }

            '''
        } )


        custom_limit = DivWdg()
        limit_content.add(custom_limit)
        custom_limit.add_class("spt_search_limit_custom")
        custom_limit.add("<br/>Custom: ")
        text = TextWdg("custom_limit")
        text.add_class("spt_search_limit_custom_text")
        text.add_style("width: 50px")
        if not is_custom:
            custom_limit.add_style("display: none")
        else:
            text.set_value(my.search_limit)
        custom_limit.add(text)
        text.add(" items")
        behavior = {
                'type': 'keydown',
                'cbjs_action': '''
                 if (evt.key=='enter') {
                    // register this as changed item
                    var value = bvr.src_el.value;
                    if (isNaN(value) || value.test(/[\.-]/)) {
                        spt.error('You have to use an integer.');
                    }
                }
        '''}

        
        text.add_behavior(behavior)

        return limit_content


class SearchLimitSimpleWdg(BaseRefreshWdg):

    def alter_search(my, search):
        pass



    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.set_unique_id()
        top.add_class("spt_search_limit_top")



        # this info comes from the SearchLimit above (function get_info() )
        count = my.kwargs.get("count")
        if count == 0:
            return top

        search_limit = my.kwargs.get("search_limit")
        # account for cases where this shouldn't even be called in a non search scenario
        if not search_limit:
            search_limit = 100
        current_offset = my.kwargs.get("current_offset")

        num_pages = int( float(count-1) / float(search_limit) ) + 1
        current_page = int (float(current_offset) / count * num_pages) + 1

        # show even if there is only a single page
        #if num_pages == 1:
        #    return top

        #print "current: ", current_offset
        #print "search_limit: ", search_limit
        #print "current_page: ", current_page

        table = Table()
        table.add_style("float: right")
        top.add(table)

        top.add_color("background", "background", -5)
        top.add_color("color", "color3")
        top.add_style("margin: -1px 0px 10px 0px")
        top.add_border(color="table_border")
        top.add_style("padding-right: 30px")
        top.add_style("padding-left: 8px")
        top.add_style("padding-top: 5px")
        top.add_style("padding-bottom: 5px")

        showing_div = DivWdg()
        showing_div.add_style("padding: 5px")
        top.add(showing_div)
        start_count = current_offset + 1
        end_count = current_offset + search_limit
        total_count = count
        if num_pages > 1:
            showing_div.add("Showing %s - %s &nbsp; of &nbsp; %s" % (start_count, end_count, total_count))
        else:
            showing_div.add("Showing %s - %s &nbsp; of &nbsp; %s" % (start_count, count, count))
            return top


        table.add_row()


        top.add_smart_style("spt_link", "padding", "5px 10px 5px 10px")
        top.add_smart_style("spt_link", "margin", "0px 5px 0px 5x")
        top.add_smart_style("spt_link", "cursor", "pointer")
        #top.add_smart_style("spt_link", "border", "solid 1px blue")

        top.add_smart_style("spt_no_link", "padding", "5px 10px 5px 10px")
        top.add_smart_style("spt_no_link", "margin", "0px 5px 0px 5x")
        top.add_smart_style("spt_no_link", "opacity", "0.5")
        top.add_smart_style("spt_no_link", "font-style", "italic")


        top.add_relay_behavior( {
            'type': 'mouseup',
            'search_limit': search_limit,
            'limit': search_limit,
            'current_page': current_page,
            'num_pages': num_pages,
            'bvr_match_class': 'spt_link',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_search_limit_top");
            var page_el = top.getElement(".spt_page");

            var value = bvr.src_el.getAttribute("spt_page");
            if (value == 'next') {
                value = bvr.current_page + 1;
                if ( value < 1 ) value = 1;
            }
            else if (value == 'prev') {
                value = bvr.current_page - 1;
                if ( value > bvr.num_pages ) value = bvr.num_pages;
            }
            page_el.value = value;

            bvr.src_el = bvr.src_el.getParent('.spt_table_top');
            //bvr.panel = bvr.src_el.getParent('.spt_view_panel');
            spt.dg_table.search_cbk(evt, bvr);
            '''
        } )


        bgcolor = top.get_color("background3")
        bgcolor2 = top.get_color("background3", 10)
        top.add_relay_behavior( {
            'type': 'mouseover',
            'bgcolor': bgcolor2,
            'bvr_match_class': 'spt_link',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )
        top.add_relay_behavior( {
            'type': 'mouseout',
            'bgcolor': bgcolor,
            'bvr_match_class': 'spt_link',
            'cbjs_action': '''
            if (!bvr.src_el.hasClass('spt_current_page'))
                bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )



        top.add_class("spt_table_search")
        hidden = HiddenWdg("prefix", "search_limit_simple")
        top.add(hidden)

        hidden = HiddenWdg("page", "")
        hidden.add_class("spt_page")
        top.add(hidden)


        td = table.add_cell()
        left = "< Prev"
        td.add(left)
        if current_page > 1:
            td.add_class("spt_link")
        else:
            td.add_class("spt_no_link")

        td.add_attr("spt_page", "prev")

        # find the range ... always show 10 pages max
        start_page = current_page - 5
        if start_page < 1:
            start_page = 1


        if start_page + 9 <= num_pages:
            end_page = start_page + 10 - 1
        elif start_page > 5:
            end_page = current_page + 5
        else:
            end_page = num_pages
            start_page = 1

        # if end_pages for whatever reason, exceeds num_pages, limit it
        if end_page > num_pages:
            end_page = num_pages

        # if for whatever reason, end_page - 10 > 1, then limit it
        if end_page == num_pages and end_page - 10 > 1:
            start_page = end_page - 10




        for i in range(start_page, end_page + 1):
            td = table.add_cell()
            td.add(i)
            td.add_class("spt_link")
            td.add_attr("spt_page", i)
            if i == current_page:
                td.add_color("color", "color")
                td.add_class("spt_current_page")
                td.add_color("background", "background3", 10)
                td.add_color("border-color", "border")
                td.add_style("border-width", "0px 1px 0px 1px")
                td.add_style("border-style", "solid")


        td = table.add_cell()
        right = "Next >"
        td.add(right)
        if current_page < num_pages:
            td.add_class("spt_link")
        else:
            td.add_class("spt_no_link")
        td.add_attr("spt_page", "next")




        return top









