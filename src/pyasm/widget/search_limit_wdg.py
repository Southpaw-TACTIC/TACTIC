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

__all__ = ['SearchLimitWdg','RetiredFilterWdg']

from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, SpanWdg
from input_wdg import HiddenWdg, SubmitWdg, FilterSelectWdg, TextWdg, FilterTextWdg, FilterCheckboxWdg
from icon_wdg import IconSubmitWdg, IconWdg, IconButtonWdg
from web_wdg import SwapDisplayWdg


# DEPRECATED

class SearchLimitWdg(Widget):
    DETAIL = "detail_style"
    LESS_DETAIL = "less_detail_style"
    SIMPLE = "simple_style"

    def __init__(my, name='search_limit', label="Showing", limit=10, refresh=True):
        my.search_limit_name = name
        my.label = label
        my.search_limit = limit
        my.fixed_offset = False
        my.style = my.DETAIL
        my.refresh = refresh
        my.refresh_script = ''
        if my.refresh:
            my.prev_hidden_name = 'Prev'
            my.next_hidden_name='Next'
        else:
            my.prev_hidden_name = '%s_Prev' %my.label
            my.next_hidden_name = '%s_Next' %my.label

        super(SearchLimitWdg, my).__init__()
        
    def init(my):
        
        my.current_offset = 0
        my.count = None
        my.text = FilterTextWdg(my.search_limit_name, is_number=True, has_persistence=False)

    def set_refresh_script(my, script):
        my.refresh_script = script

    def set_label(my, label):
        my.label = label

    def get_limit(my):
        return my.search_limit

    def set_limit(my, limit):
        if limit <= 10:
            limit = 10
        my.search_limit = limit

    def set_offset(my, offset):
        my.fixed_offset = True
        my.current_offset = offset

    def set_style(my, style):
        my.style = style

    def alter_search(my, search):

        my.set_search(search)
        my.count = search.get_count()
        web = WebContainer.get_web()
        
        
        search_limit = my.text.get_value()
        if search_limit != "":
            try:
                my.search_limit = int(search_limit)
            except ValueError:
                my.search_limit = 20
            if my.search_limit <= 0:
                my.search_limit = 1
        
        # find out what the last offset was
        last_search_offset = web.get_form_value("%s_last_search_offset"%my.label)

        if last_search_offset != "":
            last_search_offset = int(last_search_offset)
        else:
            last_search_offset = 0

        # based on the action, set the new offset
        if web.get_form_value(my.next_hidden_name) == "Next":
            current_offset = last_search_offset + my.search_limit
            if current_offset >= my.count:
                current_offset = 0

        elif web.get_form_value(my.prev_hidden_name) == "Prev":
            current_offset = last_search_offset - my.search_limit
            if current_offset < 0:
                current_offset = int(my.count/my.search_limit) * my.search_limit
       
        # this happens when the user jumps from Page 3 of a tab to a tab that
        # doesn't really need this widget
        elif last_search_offset > my.count:
            current_offset = 0
        elif web.get_form_value(my.label) != "":
            value = web.get_form_value(my.label)
            current_offset, tmp = value.split(" - ")
            current_offset = int(current_offset) - 1
        else:
            current_offset = 0 

       
        if my.fixed_offset == False:
            my.current_offset = current_offset
       
        my.search.set_limit(my.search_limit)
        my.search.set_offset(my.current_offset)

    def get_display(my):

        web = WebContainer.get_web()

        widget = Widget()

        div = SpanWdg(css='med')
        div.set_attr("nowrap", "1")

        limit_wdg = my.text
        limit_wdg.add_event('onchange', 'if (this.value < 20 || !Common.validate_int(this.value)) this.value=20 ') 
        limit_wdg.add_style("margin-top: -3px")
        limit_wdg.set_attr("size", "1")
        #limit_wdg.set_value(my.search_limit)

        offset_wdg = HiddenWdg("%s_last_search_offset" %my.label)
        offset_wdg.set_value(my.current_offset)
        #div.add(limit_wdg)
        div.add(offset_wdg)
    

        if my.search or my.sobjects:
            # my.count should have been set in alter_search()
            # which can be called explicitly thru this instance, my.
            if not my.count:
                my.count = my.search.get_count()
            
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
 
        
            if my.current_offset == 0 and limit < my.search_limit:
                return None
              
            if my.refresh:
                prev = IconSubmitWdg("Prev", IconWdg.LEFT, False )
                next = IconSubmitWdg("Next", IconWdg.RIGHT, False, icon_pos="right" )
            else:
                prev = IconButtonWdg("Prev", IconWdg.LEFT, False )
                hidden_name = my.prev_hidden_name
                hidden = HiddenWdg(hidden_name,"")
                prev.add(hidden)
                prev.add_event('onclick',"get_elements('%s').set_value('Prev');%s"\
                        %(hidden_name, my.refresh_script))
                next = IconButtonWdg("Next", IconWdg.RIGHT, False, icon_pos="right" )
                hidden_name = my.next_hidden_name
                hidden = HiddenWdg(hidden_name,"")
                next.add(hidden)
                next.add_event('onclick',"get_elements('%s').set_value('Next');%s" \
                        %(hidden_name, my.refresh_script))

            label_span = SpanWdg("Showing:")
            label_span.add_style('color','#c2895d')
            div.add(label_span)
            div.add( prev )
           

            # this min calculation is used so that if my.sobjects is not set
            # above for the calculation of the limit, which will make the last 
            # set of range numbers too big
            
            left_bound = my.current_offset+1
            right_bound = min(my.current_offset+limit, my.count)
            if left_bound > right_bound:
                left_bound = 1
            current_value = "%d - %d" % (left_bound, right_bound)

            if my.style == my.SIMPLE:
                div.add( current_value )
            else:
                # add a range selector using ItemsNavigatorWdg
                from input_wdg import ItemsNavigatorWdg
                selector = ItemsNavigatorWdg(my.label, my.count, my.search_limit, refresh=my.refresh)
                selector.set_style(my.style)

                selector.set_value(current_value)
                selector.set_display_label(False)
                if my.refresh_script:
                    selector.set_refresh_script(my.refresh_script)
                div.add( selector) 
                div.add( " - ")
                div.add( limit_wdg)

            div.add( next )

            widget.add(div)

            


        return widget



class RetiredFilterWdg(SwapDisplayWdg):
    ''' a button that triggers the display of retired items''' 
    def __init__(my, prefix='', refresh=True):
        name = 'show_retired'
        if prefix:
            name = '%s_show_retired' %prefix
        my.hidden = HiddenWdg(name,'')
        if refresh:
            my.hidden.set_persistence() 
        my.refresh = refresh
        super(RetiredFilterWdg, my).__init__()
       
    def _get_script(my, value):
        script = "var x=get_elements('%s'); x.set_value('%s')"\
                 %(my.hidden.get_name(), value) 
        if my.refresh:
            script = "%s;document.form.submit()" %script
        return script

    def get_display(my):
        
        on_icon = IconWdg('click to show retired', icon="/context/icons/common/hide_retire.png")
        off_icon = IconWdg('click to hide retired', icon=IconWdg.RETIRE)
        off_icon.add(my.hidden)
        
        on_script = my._get_script('true')
        off_script = my._get_script('false')
        
        # swap the icons if it is clicked on 
        if my.get_value()=='true':
            my.set_display_widgets(off_icon, on_icon)
            my.add_action_script(off_script, on_script)
        else:
            my.set_display_widgets(on_icon, off_icon)
            my.add_action_script(on_script, off_script)

        return super(RetiredFilterWdg, my).get_display()
    
    def get_value(my):
        return my.hidden.get_value()
    

    def alter_search(my, search):
        if my.get_value() == 'true':
            search.set_show_retired(True)


