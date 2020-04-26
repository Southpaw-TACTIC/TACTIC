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

    def __init__(self, name='search_limit', label="Showing", limit=10, refresh=True):
        self.search_limit_name = name
        self.label = label
        self.search_limit = limit
        self.fixed_offset = False
        self.style = self.DETAIL
        self.refresh = refresh
        self.refresh_script = ''
        if self.refresh:
            self.prev_hidden_name = 'Prev'
            self.next_hidden_name='Next'
        else:
            self.prev_hidden_name = '%s_Prev' %self.label
            self.next_hidden_name = '%s_Next' %self.label

        super(SearchLimitWdg, self).__init__()
        
    def init(self):
        
        self.current_offset = 0
        self.count = None
        self.text = FilterTextWdg(self.search_limit_name, is_number=True, has_persistence=False)

    def set_refresh_script(self, script):
        self.refresh_script = script

    def set_label(self, label):
        self.label = label

    def get_limit(self):
        return self.search_limit

    def set_limit(self, limit):
        if limit <= 10:
            limit = 10
        self.search_limit = limit

    def set_offset(self, offset):
        self.fixed_offset = True
        self.current_offset = offset

    def set_style(self, style):
        self.style = style

    def alter_search(self, search):

        self.set_search(search)
        self.count = search.get_count()
        web = WebContainer.get_web()
        
        
        search_limit = self.text.get_value()
        if search_limit != "":
            try:
                self.search_limit = int(search_limit)
            except ValueError:
                self.search_limit = 20
            if self.search_limit <= 0:
                self.search_limit = 1
        
        # find out what the last offset was
        last_search_offset = web.get_form_value("%s_last_search_offset"%self.label)

        if last_search_offset != "":
            last_search_offset = int(last_search_offset)
        else:
            last_search_offset = 0

        # based on the action, set the new offset
        if web.get_form_value(self.next_hidden_name) == "Next":
            current_offset = last_search_offset + self.search_limit
            if current_offset >= self.count:
                current_offset = 0

        elif web.get_form_value(self.prev_hidden_name) == "Prev":
            current_offset = last_search_offset - self.search_limit
            if current_offset < 0:
                current_offset = int(self.count/self.search_limit) * self.search_limit
       
        # this happens when the user jumps from Page 3 of a tab to a tab that
        # doesn't really need this widget
        elif last_search_offset > self.count:
            current_offset = 0
        elif web.get_form_value(self.label) != "":
            value = web.get_form_value(self.label)
            current_offset, tmp = value.split(" - ")
            current_offset = int(current_offset) - 1
        else:
            current_offset = 0 

       
        if self.fixed_offset == False:
            self.current_offset = current_offset
       
        self.search.set_limit(self.search_limit)
        self.search.set_offset(self.current_offset)

    def get_display(self):

        web = WebContainer.get_web()

        widget = Widget()

        div = SpanWdg(css='med')
        div.set_attr("nowrap", "1")

        limit_wdg = self.text
        limit_wdg.add_event('onchange', 'if (this.value < 20 || !Common.validate_int(this.value)) this.value=20 ') 
        limit_wdg.add_style("margin-top: -3px")
        limit_wdg.set_attr("size", "1")
        #limit_wdg.set_value(self.search_limit)

        offset_wdg = HiddenWdg("%s_last_search_offset" %self.label)
        offset_wdg.set_value(self.current_offset)
        #div.add(limit_wdg)
        div.add(offset_wdg)
    

        if self.search or self.sobjects:
            # self.count should have been set in alter_search()
            # which can be called explicitly thru this instance, self.
            if not self.count:
                self.count = self.search.get_count()
            
            # if self.sobjects exist thru inheriting from parent widgets
            # or explicitly set, (this is not mandatory though)
            if self.sobjects and len(self.sobjects) < self.search_limit:
                limit = len(self.sobjects)
            elif self.search and self.count < self.search_limit:
                # this is only true if the total result of the search is 
                # less than the limit and so this wdg will not display
                limit = self.count
            else:
                limit = self.search_limit
 
        
            if self.current_offset == 0 and limit < self.search_limit:
                return None
              
            if self.refresh:
                prev = IconSubmitWdg("Prev", IconWdg.LEFT, False )
                next = IconSubmitWdg("Next", IconWdg.RIGHT, False, icon_pos="right" )
            else:
                prev = IconButtonWdg("Prev", IconWdg.LEFT, False )
                hidden_name = self.prev_hidden_name
                hidden = HiddenWdg(hidden_name,"")
                prev.add(hidden)
                prev.add_event('onclick',"get_elements('%s').set_value('Prev');%s"\
                        %(hidden_name, self.refresh_script))
                next = IconButtonWdg("Next", IconWdg.RIGHT, False, icon_pos="right" )
                hidden_name = self.next_hidden_name
                hidden = HiddenWdg(hidden_name,"")
                next.add(hidden)
                next.add_event('onclick',"get_elements('%s').set_value('Next');%s" \
                        %(hidden_name, self.refresh_script))

            label_span = SpanWdg("Showing:")
            label_span.add_style('color','#c2895d')
            div.add(label_span)
            div.add( prev )
           

            # this min calculation is used so that if self.sobjects is not set
            # above for the calculation of the limit, which will make the last 
            # set of range numbers too big
            
            left_bound = self.current_offset+1
            right_bound = min(self.current_offset+limit, self.count)
            if left_bound > right_bound:
                left_bound = 1
            current_value = "%d - %d" % (left_bound, right_bound)

            if self.style == self.SIMPLE:
                div.add( current_value )
            else:
                # add a range selector using ItemsNavigatorWdg
                from input_wdg import ItemsNavigatorWdg
                selector = ItemsNavigatorWdg(self.label, self.count, self.search_limit, refresh=self.refresh)
                selector.set_style(self.style)

                selector.set_value(current_value)
                selector.set_display_label(False)
                if self.refresh_script:
                    selector.set_refresh_script(self.refresh_script)
                div.add( selector) 
                div.add( " - ")
                div.add( limit_wdg)

            div.add( next )

            widget.add(div)

            


        return widget



class RetiredFilterWdg(SwapDisplayWdg):
    ''' a button that triggers the display of retired items''' 
    def __init__(self, prefix='', refresh=True):
        name = 'show_retired'
        if prefix:
            name = '%s_show_retired' %prefix
        self.hidden = HiddenWdg(name,'')
        if refresh:
            self.hidden.set_persistence() 
        self.refresh = refresh
        super(RetiredFilterWdg, self).__init__()
       
    def _get_script(self, value):
        script = "var x=get_elements('%s'); x.set_value('%s')"\
                 %(self.hidden.get_name(), value) 
        if self.refresh:
            script = "%s;document.form.submit()" %script
        return script

    def get_display(self):
        
        on_icon = IconWdg('click to show retired', icon="/context/icons/common/hide_retire.png")
        off_icon = IconWdg('click to hide retired', icon=IconWdg.RETIRE)
        off_icon.add(self.hidden)
        
        on_script = self._get_script('true')
        off_script = self._get_script('false')
        
        # swap the icons if it is clicked on 
        if self.get_value()=='true':
            self.set_display_widgets(off_icon, on_icon)
            self.add_action_script(off_script, on_script)
        else:
            self.set_display_widgets(on_icon, off_icon)
            self.add_action_script(on_script, off_script)

        return super(RetiredFilterWdg, self).get_display()
    
    def get_value(self):
        return self.hidden.get_value()
    

    def alter_search(self, search):
        if self.get_value() == 'true':
            search.set_show_retired(True)


