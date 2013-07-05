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

__all__ = ['SubmissionWdg', 'RenderSubmissionWdg', 'BinSelectWdg', 
            'BinFilterSelectWdg', 'BinSelectionWdg', 'BinLabelFilterSelectWdg',
            'BinTypeFilterSelectWdg', 'SubmissionOptionsWdg',
            'SubmissionDescriptionWdg',
            'SubmissionInfo', 'SubmissionDataTableElement', 
            'DailiesLink', 'SubmissionTableWdg', 'SubmissionItemFilterWdg']
            


from pyasm.widget import *
from pyasm.web import *
from pyasm.search import Search, SObject, SearchType, Select, SearchKey
from pyasm.prod.biz import Bin
from pyasm.common import Container
from pyasm.biz import Snapshot

from tactic.ui.panel import EditWdg
from tactic.ui.widget import TextBtnSetWdg
from tactic.ui.common import BaseRefreshWdg

class SubmissionWdg(EditWdg):

    #def __init__(my, search_type,base_config="submit", input_prefix='edit'):
    #    super(SubmissionWdg,my).__init__(search_type,base_config, input_prefix)

    def get_args_keys(my):
        return {
        "search_type": "search_type to be operated on",
        "parent_search_type": "parent search_type for this submission",
        "parent_search_id": "parent search_id for this submission",
        "view": "the view to get the widgets from",
        "input_prefix": "a prefix to give all of the input widget ids",

        # depreacted
        "base_config": "the view to get the widgets from"
        }
    
    def init(my):
        super(SubmissionWdg, my).init()
        my.mode = 'Submit'


    def add_header(my, table, title):
        table.add_style('width', '50em')
        
        parent_st = my.kwargs.get('parent_search_type')
        parent_sid =  my.kwargs.get('parent_search_id')
        parent_context = ''
        parent_version = ''

        sobj = Search.get_by_id(parent_st, parent_sid)
        sobj_code = 'New'
        sobj_title = ''
        if sobj:
            sobj_code = sobj.get_code()
            sobj_title = sobj.get_search_type_obj().get_title()
            if isinstance(sobj, Snapshot):
                parent_context = sobj.get_context()
                parent_version = sobj.get_version()
        th = table.add_header( "Add Submission for %s [%s]" % (sobj_title, sobj_code))
        th.set_attr("colspan", "2")
        hidden = HiddenWdg('parent_search_type', parent_st )
        th.add(hidden)
        hidden = HiddenWdg('parent_search_id', parent_sid )
        th.add(hidden)
        
        hidden = HiddenWdg('parent_context', parent_context )
        th.add(hidden)

        hidden = HiddenWdg('parent_version', parent_version )
        th.add(hidden)
        
        if sobj:
            hidden = HiddenWdg('parent_search_key', SearchKey.get_by_sobject(sobj) )
            th.add(hidden)
        
    def get_action_html(my):
        search_key = SearchKey.get_by_sobject(my.sobjects[0], use_id=True)
        behavior_submit = {
            'type': 'click_up',
            'cb_fire_named_event': 'submit_pressed',
            'element_names': my.element_names,
            'search_key': search_key,
            'input_prefix': my.input_prefix

        }
        behavior_cancel = {
            'type': 'click_up',
            'cb_fire_named_event': 'preclose_edit_popup',
            'cbjs_postaction': "spt.popup.destroy( spt.popup.get_popup( $('edit_popup') ) );"
        }
        button_list = [{'label':  "%s/Close" % my.mode.capitalize(),
            'bvr': behavior_submit},
            {'label':  "Cancel", 'bvr': behavior_cancel}]        
        edit_close = TextBtnSetWdg( buttons=button_list, spacing =6, size='large', \
                align='center',side_padding=10)
        
       
        #key = 'edit|submit'
        
        div = DivWdg()
        div.add_styles('height: 35px; margin-top: 10px;')
       
        div.center()
        div.add(edit_close)

        return div
    


class RenderSubmissionWdg(EditWdg):

    #def __init__(my,search_type,base_config="submit", input_prefix='edit'):
    #    super(RenderSubmissionWdg,my).__init__(search_type,base_config, input_prefix)
    def get_args_keys(my):
        return {
        "search_type": "search_type to be operated on",
        "view": "the view to get the widgets from",
        "input_prefix": "a prefix to give all of the input widget ids",

        # depreacted
        "base_config": "the view to get the widgets from"
        }




    def add_header(my, table, title):
        table.add_style('width', '50em')
        th = table.add_header( "Add Render Submission" )
        th.set_attr("colspan", "2")
        
    def get_action_html(my):
        from pyasm.prod.site import EditorialTabWdg, MainTabWdg, ClientTabWdg

        #edit = SubmitWdg("do_edit", "Submit/Next" )
        edit_continue = SubmitWdg("do_edit", "Submit/Close" )
        edit_continue.add_event("onclick", "document.form.%s.value='true'"%my.CLOSE_WDG) 
        
        # call an edit event
        #event = WebContainer.get_event("sthpw:submit")
        #edit.add_event( "onclick", event.get_caller() )
        

        # create a cancel button to close the window
        cancel = ButtonWdg("Cancel")
        iframe = Container.get("iframe")
        cancel.add_event("onclick", "window.parent.%s" % iframe.get_off_script() )

        div = DivWdg(css='centered')
        
        div.center()
        #div.add(SpanWdg(edit, css='med'))
        div.add(SpanWdg(edit_continue, css='med'))
        div.add(SpanWdg(cancel, css='med'))

        return div

class BinSelectWdg(SelectWdg):
    ''' a select of bins'''
    DEFAULT_LIMIT = 10
    SELECT_NAME = 'dailies_bin_select'
    def __init__(my,  name=SELECT_NAME, label='', type='dailies'):
        my.display_limit = my.DEFAULT_LIMIT
        my.add_category = False
        my.sub_type = type
        super(BinSelectWdg, my).__init__(name, label=label)
        
    
    def _get_bins(my):
        
        search = Search(Bin)

        # get all the types in the Bin table
        type_search = Search(Bin)
        type_search.add_column('type')
        type_search.add_group_by('type')
        types = SObject.get_values(type_search.get_sobjects(), 'type')

        select = SelectWdg('display_limit')
        select.set_option('persist', 'true')
        display_limit = select.get_value()
        if display_limit:
            my.display_limit = display_limit

        # by default, get 10 for each type
        joined_statements = []
        for type in types:
            # TODO: fix this sql to run through search
            select = Search('prod/bin')
            select.add_filter("type", type)
            select.set_show_retired(False)
            select.add_order_by("code")
            select.add_limit(my.display_limit)
            statement = select.get_statement()
            joined_statements.append(statement)

            #joined_statements.append("select * from \"bin\" where \"type\" ='%s' and (\"s_status\" != 'retired' or \"s_status\" is NULL)" \
            #    " order by \"code\" desc limit %s" % (type, my.display_limit))

        if len(joined_statements) > 1:
            joined_statements = ["(%s)"%x for x in joined_statements]
            statement = ' union all '.join(joined_statements)
        elif len(joined_statements) == 1:
            statement = joined_statements[0]
        else:
            # no bins created yet
            return []
        #print "statement: ", statement
    
        return Bin.get_by_statement(statement)
    
    def _add_options(my):
        bins = my._get_bins()
        type = None
        for bin in bins:
            if my.add_category and type != bin.get_type():
                my.append_option('<< %s >>' %bin.get_type(), '')
                type = bin.get_type()
            my.append_option(bin.get_label(), bin.get_id())
            
        #my.add_empty_option(label='-- Select a bin --')
        my.add_behavior({'type': 'change', \
            "cbjs_action:" : "if (this.value =='') alert('Please choose a valid bin.')"})

    def set_label(my, label):
        my.label = label
        
    def set_category_display(my, display):
        my.add_category = display

    #def init(my):
        
    def get_display(my):
        my._add_options()     
       
        return super(BinSelectWdg, my).get_display()

class BinFilterSelectWdg(BinSelectWdg):
    ''' A SelectWdg used in Dailies Tab thru BinFilterWdg''' 
    def _get_bins(my):
        search = Search(Bin)
        search.add_filter('type', my.sub_type)
        search.add_order_by('code desc')
        return search.get_sobjects()

class BinSelectionWdg(BaseRefreshWdg, BaseInputWdg):
    ''' a select of bins and a choice of creating a new one'''
  

    def init(my):
        my.input_name = my.kwargs.get('input_name')

    def get_display(my):
        if not my.input_name:
            my.input_name = my.get_input_name()
        
        # the limit has to be calculated first to determine how many bins are to be displayed
        # by the BinSelectWdg
        div = DivWdg()
        div.add_class('spt_panel')
        div.set_attr('spt_class_name', 'pyasm.prod.web.BinSelectionWdg')
        div.set_attr('spt_input_name', my.input_name)
        limit_sel = FilterSelectWdg('display_limit', label = 'limit / type: ')
        limit_sel.set_option('values', '5|10|20|100')
        limit_sel.set_option('default', '%s' %BinSelectWdg.DEFAULT_LIMIT)
        
        limit_span = SpanWdg(limit_sel, css='small')
        limit_span = limit_span.get_buffer_display()

        

        #TODO: not hardcoding this client_bin_select Select Name
        #set_bin_script = ["Submission.set_bin('client_bin_select', this.value, true)"] 
                    
        #set_bin_script.append("Submission.set_bin('%s', this.value, true)" \
        #        %BinSelectWdg.SELECT_NAME)
        #my.add_event('onchange', ';'.join(set_bin_script))
            
        select = BinSelectWdg(my.input_name)
        select.set_category_display(True)
        select.add_empty_option(label='-- Select a bin --')
        div.add(select)
        div.add(limit_span)
       
        """
        iframe_link = IframeInsertLinkWdg(search.get_search_type())
        iframe_link.set_iframe_width(74)
        iframe_link.set_refresh_mode('page')
        span.add(iframe_link)
        """
        return div
       
        
class BinLabelFilterSelectWdg(FilterSelectWdg):
    ''' a select of different labels for bin '''
    def __init__(my,  name='bin_label_select', label='Label: ', css='med'):
        super(BinLabelFilterSelectWdg, my).__init__(name, label)
        
    def init(my):
        search = Search(Bin)
        
        search.add_column('label')
        search.add_group_by('label')
        my.set_search_for_options(search, 'label','label')
        my.add_empty_option('-- Any --')

class BinTypeFilterSelectWdg(FilterSelectWdg):
    ''' a select of different types for bin '''
    def __init__(my,  name='bin_type_select', label='Type: ', css='med'):
        super(BinTypeFilterSelectWdg, my).__init__(name, label)
        
    def init(my):
        search = Search(Bin)
        
        search.add_column('type')
        search.add_group_by('type')
        my.set_search_for_options(search, 'type','type')
        my.add_empty_option('-- Any --')


class SubmissionOptionsWdg(BaseInputWdg):
    ''' add the submission options here '''
    TO_DAILY = "go_to_daily"
    TO_CLIENT = "go_to_client"
    def get_display(my):

        cb = CheckboxWdg(my.TO_DAILY)
        span = SpanWdg(cb)
        span.add('Go to Dailies tab')
        my.add(span)

        if my.get_option("show_client") == 'true':
            cb = CheckboxWdg(my.TO_CLIENT)
            span = SpanWdg(cb, css='large')
            span.add('Go to Client Review tab')
            my.add(span)

       

        super(SubmissionOptionsWdg, my).get_display()

class SubmissionDescriptionWdg(TextAreaWdg):
    '''Pulls in a description from the parent sobject'''
    def get_display(my):
        web = WebContainer.get_web()
        parent_search_type = web.get_form_value("parent_search_type")
        parent_search_id = web.get_form_value("parent_search_id")
        parent = Search.get_by_id(parent_search_type, parent_search_id)

        value = ''
        if parent:
            if parent.has_value("description"):
                value = parent.get_value("description")
            else:
                value = parent.get_name()

        my.set_value(value)

        return super(SubmissionDescriptionWdg,my).get_display()





class SubmissionInfo(object):
    ''' info of the sobject that a submission is made for '''
    def __init__(my, sobjects):
        my.sobjs = sobjects
        
    def get_info(my):
        # check if the sobj type is the same
        search_types = SObject.get_values(my.sobjs, 'search_type', unique=True)
        search_ids = SObject.get_values(my.sobjs, 'search_id', unique=False)
      
        infos = []
        # this doesn't really work if the same asset is submitted multiple times
        if len(search_types) == 1 and len(search_ids) == len(my.sobjs):
            assets = []
            if search_types[0]:
                assets = Search.get_by_id(search_types[0], search_ids)
            
            asset_dict = SObject.get_dict(assets)
            for id in search_ids:
                asset = asset_dict.get(id)
                aux_dict = {}
                aux_dict['info'] = SubmissionInfo._get_target_sobject_data(asset)
                aux_dict['search_key'] = '%s:%s' %(search_types[0], id)
                infos.append(aux_dict)
            
        else:
            # TODO: this is a bit database intensive, mixed search_types not
            # recommended
            search_types = SObject.get_values(my.sobjs, 'search_type',\
                unique=False)
            for idx in xrange(0, len(search_types)):
                search_type = search_types[idx]
                    
                aux_dict = {}
                aux_dict['info'] = ''
                aux_dict['search_key'] = ''
                if search_type:
                    asset = Search.get_by_id(search_type, search_ids[idx])
                    aux_dict['info'] = SubmissionInfo._get_target_sobject_data(asset)
                    aux_dict['search_key'] = '%s:%s' %(search_types[idx], search_ids[idx])
                infos.append(aux_dict)
        return infos
    
    def _get_target_sobject_data(asset):
        '''get the info data for the Info column of the submission'''
        data = 'Unknown'
        if not asset:
            return data
        title = SearchType.get(asset.get_search_type()).get_title()
        data = ''
        if asset.has_value('code'):
            if asset.has_value('name'):
                data = '%s: %s_%s' % \
                        (title, asset.get_code(), asset.get_value('name'))
            else:
                data = '%s: %s' % (title, asset.get_code())
        return data
    _get_target_sobject_data = staticmethod(_get_target_sobject_data)

class SubmissionDataTableElement(AuxDataWdg):

    def handle_tr(my, tr):
        aux_data = my.get_current_aux_data()
        if aux_data:
            search_key = aux_data.get('search_key')
            tr.set_attr('search_key', search_key)
            # this is used in EditorialTabWdg
            tr.set_attr('name', 'sub_row')

    def get_display(my):
        table = Table()
        sobject = my.get_current_sobject()
        aux_data = my.get_current_aux_data()
        if aux_data:
            info = aux_data.get('info')
            if info:
                table.add_row()
                table.add_row_cell(info)
        
        table.add_row()
        table.add_cell( "Context:" )
        context = sobject.get_value("context") 
        if context:
            table.add_cell(context)
        else:
            table.add_blank_cell()

        table.add_row()
        table.add_cell( "Version:" )
        version = sobject.get_value("version") 
        if version:
            table.add_cell(version)
        else:
            table.add_blank_cell()
        return table

    def get_simple_display(my):
        sobject = my.get_current_sobject()
        aux_data = my.get_current_aux_data()
        if aux_data:
            info = aux_data.get('info')
        else:
            info = "???"
        #parent = sobject.get_parent()
        #info = parent.get_code()

        context = sobject.get_value("context")
        version = str( sobject.get_value("version") )

        return "[%s, %s, %s]" %(info, context, version)



class DailiesLink(BaseTableElementWdg):

    def preprocess(my):
        my.redirect_tab = my.get_option('dailies_tab')

    def get_hidden(my):
        widget = Widget()
        hidden = HiddenWdg(BinSelectWdg.SELECT_NAME)
        widget.add(hidden)
        hidden = HiddenWdg('client_bin_select')
        widget.add(hidden)
        return widget

    def get_display(my):
        sobject = my.get_current_sobject()
        
        widget = Widget()

        if sobject.get_value('type') == my.redirect_tab:
            #from pyasm.prod.site import EditorialTabWdg
            #location = {EditorialTabWdg.TAB_KEY: EditorialTabWdg.DAILIES_TAB}
            #redirect = [TabWdg.get_redirect_script(location, is_child=False)]
            #set_bin_script = "Submission.set_bin('%s','%s', false)" \
            #    %(BinSelectWdg.SELECT_NAME, sobject.get_id())
            ##redirect.append(set_bin_script)
            #redirect.append('document.form.submit()')

            class_name = "tactic.ui.panel.ViewPanelWdg"
            search_type = "prod/submission"
            view = "table"

            behavior = {
                "type": "click_up",
                "cbfn_action": "spt.popup.get_widget",
                "options": {
                    "title": "Submission",
                    "class_name": class_name,
                    "popup_id": 'submission_popup'
                },
                "args": {
                    "search_type": search_type,
                    "view": view,
                }
            }

            icon = IconWdg(icon=IconWdg.JUMP)
            icon.add_tip('Jump to Dailies of this bin')

            icon_widget = DivWdg()
            icon_widget.add(icon)
            icon_widget.add_behavior(behavior)
            widget.add(icon_widget)

        else:
            widget.add("&nbsp;")
        return widget

class SubmissionTableWdg(Widget):

    def init(my):
        web = WebContainer.get_web()
        args = web.get_form_args()
        # get the args in the URL
        my.search_type = args.get('search_type')
        my.search_id = args.get('search_id')
        if not my.search_type:
            my.search_type = web.get_form_value("search_type")
            my.search_id = web.get_form_value("search_id")

    def get_display(my):
        div_id = "SubmissionTableWdg_top"
        ajax = AjaxLoader(div_id)
        if ajax.is_refresh():
            widget = Widget()
        else:
            widget = DivWdg(id=div_id)
            widget.add_style("display: block")
            #widget.add_style("width: 95%")
            widget.add_style("margin-left: 20px") 
        

        search = Search("prod/submission")
        widget.add(my.get_filter_wdg(search, my.search_type, my.search_id, div_id))

        
        search.add_filter("search_type", my.search_type)
        search.add_filter("search_id", my.search_id)
        # hide client submissions
        # TODO: this is EXTREMELY inefficient.  Is there any reason why we need 
        # a many to many relationship for submissions to bins?
        #search.add_where("id not in (select submission_id from submission_in_bin where bin_id in (select id from bin where type = 'client') )" )

        search.add_order_by("timestamp desc")
        sobjects = search.get_sobjects()
        #from pyasm.prod.web import SubmissionInfo
        info = SubmissionInfo(sobjects)
        aux_data = info.get_info()
        dailies_div = DivWdg(id=div_id)
        dailies_div.add_style('display','block')
        dailies_table = TableWdg("prod/submission", "table",\
            css='table')
        dailies_table.set_show_property(False)
        dailies_table.set_id('sthpw/dailies_%s' % my.search_id)
        dailies_table.set_sobjects(sobjects)
        dailies_table.set_aux_data(aux_data)
        dailies_div.add(dailies_table)
        dailies_div.add(HtmlElement.br(2))
        widget.add(dailies_div)

        return widget

    def get_filter_wdg(my, search, search_type, search_id, div_id):
        
        ajax = AjaxLoader()
        ajax.set_option("search_type", search_type)
        ajax.set_option("search_id", search_id)
        bin_name = "bin_%s_%s" % (search_type, search_id)
        artist_name = "artist_%s_%s" % (search_type, search_id)
        status_name = "status_%s_%s" % (search_type, search_id)
        retired_name = "%s_%s_show_retired" % (search_type, search_id)
        ajax.add_element_name(bin_name )
        ajax.add_element_name(artist_name )
        ajax.add_element_name(status_name )
        ajax.add_element_name(retired_name )
        # add a shot id
        #ajax.add_element_name("shot_id")
        ajax.set_display_id(div_id)

        cls = my.__class__
        class_path = '%s.%s' %(cls.__module__, cls.__name__)
        ajax.set_load_class( class_path )
        refresh_script = ajax.get_refresh_script(show_progress=False)


       
       # select.set_persist_on_submit()

     
        filter_wdg = DivWdg()
        filter_wdg.add_style("margin-bottom: 5px")
        filter_wdg.add_style("text-align: right")
        from asset_filter_wdg import UserFilterWdg
        bin_filter = BinFilterSelectWdg(bin_name, label='Bin: ')
        bin_filter.add_empty_option('-- Any Bin --')
        #bin_filter.get_navigator().set_submit_onchange(False)
        bin_filter.set_event('onchange', refresh_script)
        bin_filter.set_persist_on_submit()
        bin_id = bin_filter.get_value()
        if not bin_id or bin_id == SelectWdg.NONE_MODE:
           #search.add_filter('id','-1')
           search.add_where("\"id\" in (select \"submission_id\" from "\
            " submission_in_bin"\
            " where \"bin_id\" in (select \"id\" from bin where \"type\" = 'dailies') )" )
        elif bin_id:
           search.add_where("\"id\" in (select \"submission_id\" from "\
            " submission_in_bin"\
            " where \"bin_id\" = %s)" %bin_id)
        
        filter_wdg.add(bin_filter)
        hint = HintWdg("To see any bins, you need to create them (Type 'dailies') in the Bins tab.")
        filter_wdg.add(hint)

        
        user_filter = UserFilterWdg(artist_name, label='Artist: ')
        user_filter.get_navigator().set_submit_onchange(False)
        user_filter.get_navigator().set_persist_on_submit()
        user_filter.get_navigator().add_event('onchange', refresh_script)

        user_filter.set_search_column('artist')
        filter_wdg.add(user_filter)

        config_base = 'table' 
       

        user_filter.alter_search(search)

        status_filter = SelectWdg(status_name, label='Status: ')
        status_filter.add_empty_option("-- Any Status--")
        status_filter.set_option('setting', 'dailies_submission_status')
        status_filter.add_event('onchange', refresh_script)
        status_filter.set_persist_on_submit()
        
        filter_wdg.add(status_filter)

        status_value = status_filter.get_value()
        if status_value:
            search.add_filter('status', status_value)

        prefix = "%s_%s" % (search_type, search_id)
        retired_filter = RetiredFilterWdg(prefix=prefix, refresh=False)
        retired_filter.add_event('onclick', refresh_script)
        filter_wdg.add(retired_filter)


        retired_value = WebContainer.get_web().get_form_value(retired_name)
        if retired_value == 'true':
            search.set_show_retired(True)
        button = IconButtonWdg("Refresh", IconWdg.REFRESH, long=False)
        button.add_event("onclick", refresh_script)
        filter_wdg.add(button)


        
        return filter_wdg


class SubmissionItemFilterWdg(SelectWdg):

    def __init__(my, sobjs, name='item_filter', label='Item Filter: ', css='med'):
        info = SubmissionInfo(sobjs)
        aux_data = info.get_info()
        my.aux_data = aux_data
        my.sobjs = sobjs
        super(SubmissionItemFilterWdg, my).__init__(name=name, label=label, css=css)

    def get_display(my):
        # add an asset select filter
        filter_labels = []
        for x in my.aux_data:
            info = x.get('info') 
            if info not in filter_labels:
                filter_labels.append(info)

        filter_values = []
        for x in my.sobjs:
            search_type = x.get_value('search_type')
            value = ''
            if search_type:
                value = '%s:%s' %(search_type, \
                    x.get_value('search_id'))
            if value not in filter_values:
                filter_values.append(value)
       
        my.add_empty_option('-- Show all submission items --')
        my.set_option('values', '|'.join(filter_values))
        my.set_option('labels', '|'.join(filter_labels))
        
        return super(SubmissionItemFilterWdg, my).get_display()

    

    def alter_search(my, search, item_value):
        if item_value:
            search_type, search_id = item_value.split(':', 1)
            search.add_filter('search_type', search_type)
            search.add_filter('search_id', search_id)
