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

__all__ = ['SObjectDetailWdg', 'AssetDetailWdg', 'ShotDetailWdg', 'LayerDetailWdg', 'TaskDetailWdg',
            'SimpleDetailWdg']

from pyasm.prod.biz import Shot
from pyasm.search import Search, SearchType, SearchKey
from pyasm.web import Widget, Table, WebContainer, DivWdg, SpanWdg, HtmlElement, AjaxLoader
from pyasm.widget import ThumbWdg, TableWdg, FilterSelectWdg, SimpleStatusWdg, SwapDisplayWdg, IconWdg

from layout_summary_wdg import AssignedShotWdg, AssetsInShotWdg
from pyasm.common import Common
from tactic.ui.common import BaseRefreshWdg

class SObjectDetailWrapperWdg(Widget):
    '''wrapper widget that determines which detail widget to use'''
    def init(self):
        # get the args in the URL
        if not self.sobjects:
            args = WebContainer.get_web().get_form_args()
            search_type = args['search_type']
            search_id = args['search_id']

            sobject = Search.get_by_id(search_type, search_id)
        else:
            sobject = self.sobjects[0]
            search_type = sobject.get_search_type()
            search_id = sobject.get_id()

        if search_type.startswith("prod/asset?"):
            detail = AssetDetailWdg()
        elif search_type.startswith("prod/shot?"):
            detail = ShotDetailWdg()

        self.add(detail)



class SObjectDetailWdg(BaseRefreshWdg):

    def init(self):
        sobject = None
        if not self.sobjects:
            """
            args = WebContainer.get_web().get_form_args()
            search_type = args['search_type']
            search_id = args['search_id']
            """
            search_key = self.kwargs.get('search_key')
            if search_key:
                sobject = SearchKey.get_by_search_key(search_key)
        else:
            sobject = self.sobjects[0]
            search_type = sobject.get_search_type()
            search_id = sobject.get_id()
        self.parent = sobject

    def get_display(self):
        # get the args in the URL
        sobject = self.parent
        main_div = DivWdg()
        main_div.add_style("width: 99%")
        main_div.add_style("float: right")
        #self.add(main_div)


        # add notes
        notes_head, notes_div = self.get_sobject_wdg(sobject, "sthpw/note", view="summary", show_count=False)
        main_div.add(notes_head)
        main_div.add(notes_div)



        # add references
        ref_head, ref_div = self.get_sobject_wdg(sobject, "sthpw/connection", view="detail", title="References")
        main_div.add(ref_head)
        main_div.add(ref_div)


        task_head, task_div = self.get_sobject_wdg(sobject, "sthpw/task", view="summary")
        main_div.add(task_head)
        main_div.add(task_div)


        # add dailies: need a special function for this
        #dailies_head, dailies_div = self.get_dailies_wdg(sobject)
        #main_div.add(dailies_head)
        #main_div.add(dailies_div)

        # add sobject history div
        hist_head, hist_div = self.get_sobject_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        # queue
        queue_head, queue_div = self.get_sobject_wdg(sobject, "sthpw/queue","summary")
        main_div.add(queue_head)
        main_div.add(queue_div)

        # renders
        #render_head, render_div = self.get_sobject_wdg(sobject, "prod/render")
        #main_div.add(render_head)
        #main_div.add(render_div)

        # add history div
        hist_head, hist_div = self.get_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)


        return main_div



    def get_sobject_wdg(self, sobject, search_type, view="table", title="", show_count=True):

        key = search_type

        search_type_obj = SearchType.get(search_type)
        if not title:
            title = search_type_obj.get_title()

        content_id ='sub_sobj_%s_%s' % (key, sobject.get_id())
        title_id = '%s_head_%s' % (key, sobject.get_id())

        div = DivWdg(id=content_id)
        div.add_style('display','none')
        #div.add_style('width','100%')

        head = DivWdg()
        head.add_style('height','1.8em')
        title_span = self._get_title_span(title) 

        dyn_load = AjaxLoader(display_id=content_id)

        args_dict = {'sobj_search_type': sobject.get_search_type()}
        args_dict['search_id'] = sobject.get_id()
        args_dict['search_type'] = search_type
        args_dict['view'] = view
        
        
        dyn_load.set_load_method('_get_sobject_wdg')
        dyn_load.set_load_class(Common.get_full_class_name(self), load_args=args_dict)
        on_script = dyn_load.get_on_script(load_once=True)

        swap_wdg = self._get_swap_wdg(title_id)
        swap_wdg.add_action_script(on_script, "toggle_display('%s')" %content_id)

        head.add(swap_wdg)
        head.add(title_span)
        self.add_title_style(title_span, title_id, swap_wdg)

        if show_count:
            search = self._get_sobject_search(sobject, search_type)
            title_span.add(" ( %s )" % search.get_count() )
        

        return head, div


    def _get_sobject_wdg(self):
        ''' this method is called thru ajax '''
        args = WebContainer.get_web().get_form_args()
        
        # get the args in the URL
        search_type = args['search_type']
        sobj_search_type = args['sobj_search_type']
        search_id = args['search_id']
        view = args['view']
        sobject = Search.get_by_id(sobj_search_type, search_id)

        content = Widget()
        table = TableWdg(search_type, view, css='table')
        table.set_show_property(False)
        content.add(table)
        content.add(HtmlElement.br(2))

        search = self._get_sobject_search(sobject, search_type)
           
        sobjects = search.get_sobjects()
        if search_type.startswith("sthpw/note"):
            # this assumes that a project has submission!
            from pyasm.prod.biz import Submission
            from pyasm.search import SqlException
            try:
                notes = Submission.get_all_notes(sobject)
                sobjects.extend( notes )
            except SqlException:
                pass

            def compare(x,y):
                return cmp( y.get_value("timestamp"), x.get_value("timestamp") )

            sobjects.sort(cmp=compare)

        table.set_search(search)
        table.set_sobjects(sobjects)
        return content

    def _get_sobject_search(self, sobject, search_type):
        ''' get the search for this sobject and search_type '''
        if search_type.startswith("sthpw/connection"):
            search = Search(search_type)
            search.add_sobject_filter(sobject,"src_")
            if sobject.get_base_search_type() == 'prod/shot':
                search.add_filter('context', 'reference')
        elif search_type.startswith("sthpw/"):
            search = Search(search_type)
            search.add_sobject_filter(sobject)
        elif search_type.startswith("prod/render"):
            search = Search(search_type)
            search.add_sobject_filter(sobject)
        elif search_type.startswith("internal/support_email"):
            search = Search(search_type)
            search.add_filter("ticket_code", sobject.get_id() )
        else:
            search = Search(search_type)
            search.add_filter( sobject.get_foreign_key(), sobject.get_code() )
        return search

    def add_title_style(self, title, title_id, swap_wdg):
        '''add style and toggle effect to different sections of the summary'''
        title.add_class('hand')
        title.set_id(title_id)

        script = ["if ($(%s).getStyle('display')=='none') {%s} else {%s}" \
                %(swap_wdg.swap2_id, swap_wdg.get_on_script(), swap_wdg.get_off_script())]
        #script.append(swap_wdg.get_swap_script())
        
        title.add_behavior({'type': 'click_up',
                            'cbjs_action': ';'.join(script)})
        title.add_style("margin: 5 0 5 0")
              
        # FIXME: commenting out for now: hard coded colors
        # and it doesn't seem to work for onmouseout
        """
        title.add_event('onmouseover', "Effects.bg_color('%s',"\
              "'active_label')" %title_id ) 
        title.add_event('onmouseout', "Effects.bg_color('%s',"\
              "'inactive_label')" %title_id ) 
        """

 
    def _get_swap_wdg(self, event_id=''):
        swap_wdg = SwapDisplayWdg(on_event_name='on_%s'%event_id, off_event_name='off_%s'%event_id)
        icon1 = IconWdg('open', IconWdg.INFO_CLOSED_SMALL)
        icon2 = IconWdg('close', IconWdg.INFO_OPEN_SMALL)
        swap_wdg.set_display_widgets(icon1, icon2)
        
        return swap_wdg

    def _get_title_span(self, content=None):
        span = SpanWdg(content, css='small')
        span.add_style('-moz-border-radius: 4px')
        return span




    def get_sobject_history_wdg(self, sobject):
        
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        content_id ='summary_sobject_history_%s' %sobject.get_id()
        title_id = 'sobject_history_head_%s' %sobject.get_id()

        head = DivWdg()
        head.add_style('height','1.8em')
        title = self._get_title_span()

        dyn_load = AjaxLoader(display_id=content_id)

        
        args_dict = {'search_type': sobject.get_search_type()}
        args_dict['search_id'] = sobject.get_id()
        dyn_load.set_load_method('_get_sobject_history_wdg')
        dyn_load.set_load_class('pyasm.prod.web.AssetDetailWdg', load_args=args_dict)
        on_script = dyn_load.get_on_script(load_once=True)

        swap_wdg = self._get_swap_wdg(title_id)
        swap_wdg.add_action_script(on_script, "toggle_display('%s')" %content_id)

        head.add(swap_wdg)
        head.add(title)
        title.add("Transaction History")
        search = Search("sthpw/sobject_log")
        search.add_filter("search_type", search_type)
        search.add_filter("search_id", search_id)
        count = search.get_count()
        title.add( " ( %s )" % count )

        self.add_title_style(title, title_id, swap_wdg)

        div = DivWdg(id=content_id)
        div.add_style("width: 100%")
        div.add_style("margin-left: auto")
        div.add_style('display','none')
        

        return head, div


    def _get_sobject_history_wdg(self):
        ''' this method is called thru ajax '''
        args = WebContainer.get_web().get_form_args()
        
        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']
        #sobject = Search.get_by_id(search_type, search_id)

        div = Widget()

        search = Search("sthpw/sobject_log")
        search.add_filter("search_type", search_type)
        search.add_filter("search_id", search_id)
        sobjects = search.get_sobjects()

        search = Search("sthpw/transaction_log")
        search.add_filters("id", [x.get_value("transaction_log_id") for x in sobjects] )
        sobjects = search.get_sobjects()


        table = TableWdg("sthpw/transaction_log", "table", css='table')
        table.set_show_property(False)
        table.set_sobjects(sobjects)
        div.add(table)
        div.add(HtmlElement.br(2))

        return div

     
        div.add(assigned_shot_wdg)
        div.add(HtmlElement.br(2))
        return div




    def get_dailies_wdg(self, sobject):
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        dailies_head = DivWdg()
        dailies_head.add_style('height','1.8em')
        dailies_title = self._get_title_span()
        content_id ='summary_dailies_%s' %sobject.get_id()
        title_id = 'dailies_head_%s' %sobject.get_id()

        args_dict = {'search_type': sobject.get_search_type()}
        args_dict['search_id'] = sobject.get_id()

        dyn_load = AjaxLoader(display_id=content_id)
        dyn_load.set_load_method('_get_dailies_wdg')
        dyn_load.set_load_class('pyasm.prod.web.AssetDetailWdg', load_args=args_dict)
        on_script = dyn_load.get_on_script(load_once=True)

        swap_wdg = self._get_swap_wdg(title_id)
        swap_wdg.add_action_script(on_script, "toggle_display('%s')" %content_id)
        
        dailies_head.add(swap_wdg)
        dailies_head.add(dailies_title)

        dailies_title.add("Dailies")
        search = Search("prod/submission")
        search.add_filter("search_type", search_type)
        search.add_filter("search_id", search_id)
        count = search.get_count()
        dailies_title.add( " ( %s )" % count )
        


        self.add_title_style(dailies_title, title_id, swap_wdg)

        dailies_div = DivWdg(id=content_id)
        dailies_div.add_style("width: 98%")
        dailies_div.add_style("margin-left: auto")
        dailies_div.add_style('display','none')
        
        return dailies_head, dailies_div


    def _get_dailies_wdg(self):
        ''' this method is called thru ajax '''
        from pyasm.prod.web import SubmissionTableWdg
        widget = SubmissionTableWdg()
        return widget




    def get_history_wdg(self, sobject):

        # special for snapshots as well
        content_id ='summary_hist_%s' %sobject.get_id()
        title_id = 'hist_head_%s' %sobject.get_id()
        hist_head = DivWdg()
        hist_head.add_style('height','1.8em')
        hist_title = self._get_title_span("Checkin History")
        
        swap_wdg = self._get_swap_wdg(title_id)

        """
        dyn_load = AjaxLoader(display_id=content_id)

        dyn_load.add_element_name('parent_key')
        args_dict = {'search_type': sobject.get_search_type()}
        args_dict['search_id'] = sobject.get_id()
        dyn_load.set_load_class('pyasm.flash.widget.FlashAssetHistoryWdg', load_args=args_dict)
        on_script = dyn_load.get_on_script(load_once=True)

        """
        # Load once feature is not implemented yet
        parent_key = SearchKey.get_by_sobject(sobject)
        dynamic_class = 'pyasm.flash.widget.FlashAssetHistoryWdg'
        on_script = '''
                spt.panel.is_refreshing = true;
                var el_id = '%s';
                spt.panel.show_progress(el_id);
                var kwargs = {'parent_key': '%s'};
                setTimeout( function() {
                    spt.panel.load(el_id, '%s', kwargs, {}, false);
                    spt.panel.is_refreshing = false;
                }, 100 );
                ''' % (content_id, parent_key, dynamic_class)

        on_script = "%s;spt.show_block('%s')"  %(on_script, content_id)
        toggle_script = "spt.toggle_show_hide('%s')" %content_id

        swap_wdg.add_action_script(on_script, toggle_script)

        hist_head.add(swap_wdg)
        hist_head.add(hist_title)

        self.add_title_style(hist_title, title_id, swap_wdg)
        
        hist_div = DivWdg(id=content_id)
        hist_div.add_style('display','none')
        
 
        return hist_head, hist_div



class AssetDetailWdg(SObjectDetailWdg):


    def get_display(self):
        
        main_div = DivWdg()
        main_div.add_style("width: 98%")
        main_div.add_style("float: right")
        #self.add(main_div)

        sobject = self.parent
        planned_head, planned_div = self.get_planned_wdg(sobject)
        main_div.add(planned_head)
        main_div.add(planned_div)

        # add notes
        notes_head, notes_div = self.get_sobject_wdg(sobject, "sthpw/note", view="summary", show_count=False)
        main_div.add(notes_head)
        main_div.add(notes_div)



        # add references
        ref_head, ref_div = self.get_sobject_wdg(sobject, "sthpw/connection", view="detail", title="References")
        main_div.add(ref_head)
        main_div.add(ref_div)

        
        task_head, task_div = self.get_sobject_wdg(sobject, "sthpw/task", view="summary")
        main_div.add(task_head)
        main_div.add(task_div)

        
        # add dailies: need a special function for this
        dailies_head, dailies_div = self.get_dailies_wdg(sobject)
        main_div.add(dailies_head)
        main_div.add(dailies_div)
        # add sobject history div
        hist_head, hist_div = self.get_sobject_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        # queue
        queue_head, queue_div = self.get_sobject_wdg(sobject, "sthpw/queue","summary")
        main_div.add(queue_head)
        main_div.add(queue_div)

        # renders
        render_head, render_div = self.get_sobject_wdg(sobject, "prod/render")
        main_div.add(render_head)
        main_div.add(render_div)

        # add history div
        hist_head, hist_div = self.get_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)


        return main_div


     

    def get_planned_wdg(self, sobject):
        
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        content_id ='summary_planned_%s' %sobject.get_id()
        title_id = 'planned_head_%s' %sobject.get_id()

        head = DivWdg()
        head.add_style('height','1.8em')
        title = self._get_title_span()

        dyn_load = AjaxLoader(display_id=content_id)

        args_dict = {'search_type': sobject.get_search_type()}
        args_dict['search_id'] = sobject.get_id()
        dyn_load.set_load_method('_get_planned_wdg')
        dyn_load.set_load_class('pyasm.prod.web.AssetDetailWdg', load_args=args_dict)
        on_script = dyn_load.get_on_script(load_once=True)

        swap_wdg = self._get_swap_wdg(title_id)
        swap_wdg.add_action_script(on_script, "toggle_display('%s')" %content_id)


        head.add(swap_wdg)
        head.add(title)
        title.add("Assigned Shots")
        self.add_title_style(title, title_id, swap_wdg)
        
        div = DivWdg(id=content_id)
        div.add_style("width: 98%")
        div.add_style("margin-left: auto")
        div.add_style('display','none')

        return head, div

    def _get_planned_wdg(self):
        ''' this method is called thru ajax '''
        args = WebContainer.get_web().get_form_args()
        
        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']
        sobject = Search.get_by_id(search_type, search_id)

        assigned_shot_wdg = AssignedShotWdg()
        assigned_shot_wdg.set_sobject(sobject)

        div = Widget()
      
        div.add(assigned_shot_wdg)
        div.add(HtmlElement.br(2))
        return div


    def get_planned_shots(self, sobject):
        pass



class ShotDetailWdg(AssetDetailWdg):

    def get_display(self):
      

        sobject = self.parent

        main_div = DivWdg()
        main_div.add_style("width: 99%")
        main_div.add_style("float: right")
        self.add(main_div)

        # get planned assets
        planned_head, planned_div = self.get_planned_wdg(sobject)
        main_div.add(planned_head)
        main_div.add(planned_div)

        # add layers
        layers_head, layers_div = self.get_sobject_wdg(sobject, "prod/layer", "table", show_count=True)
        main_div.add(layers_head)
        main_div.add(layers_div)
 
        # add notes
        notes_head, notes_div = self.get_sobject_wdg(sobject, "sthpw/note", "summary", show_count=False)
        main_div.add(notes_head)
        main_div.add(notes_div)
    
        from pyasm.prod.biz import Submission
        notes = Submission.get_all_notes(sobject)


        # add storyboards
        story_head, story_div = self.get_sobject_wdg(sobject, "prod/storyboard", "summary")
        main_div.add(story_head)
        main_div.add(story_div)

        # add camera
        camera_head, camera_div = self.get_sobject_wdg(sobject, "prod/camera",)
        main_div.add(camera_head)
        main_div.add(camera_div)
       
        # add plates
        plate_head, plate_div = self.get_sobject_wdg(sobject, "effects/plate",)
        main_div.add(plate_head)
        main_div.add(plate_div)


        # add references
       
        ref_head, ref_div = self.get_sobject_wdg(sobject, "sthpw/connection","detail", title="References")
        main_div.add(ref_head)
        main_div.add(ref_div)



        
        task_head, task_div = self.get_sobject_wdg(sobject, "sthpw/task", "summary")
        main_div.add(task_head)
        main_div.add(task_div)



        # add dailies: need a special function for this
        dailies_head, dailies_div = self.get_dailies_wdg(sobject)
        main_div.add(dailies_head)
        main_div.add(dailies_div)

        # add sobject history div
        hist_head, hist_div = self.get_sobject_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)



        # add history div
        hist_head, hist_div = self.get_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        # queue
        queue_head, queue_div = self.get_sobject_wdg(sobject, "sthpw/queue","summary")
        main_div.add(queue_head)
        main_div.add(queue_div)



        # renders
        render_head, render_div = self.get_sobject_wdg(sobject, "prod/render")
        main_div.add(render_head)
        main_div.add(render_div)

        # add composites
        layers_head, layers_div = self.get_sobject_wdg(sobject, "prod/composite", "table", show_count=True)
        main_div.add(layers_head)
        main_div.add(layers_div)
 


        return main_div


        # handle migration assets -- they are connected are connected to the
        # original
        # FIXME: disabling for now: we are running into ajax depth limitations
        """
        search = Search("sthpw/connection")
        search.add_filter("context", "migration")
        search.add_sobject_filter(sobject, prefix="src_")
        connections = search.get_sobjects()
        for connection in connections:
            conn_search_type = connection.get_value("dst_search_type")
            search = Search(conn_search_type)
            search.add_id_filter( connection.get_value("dst_search_id") )

            aref_head, aref_div = self.get_sobject_wdg(sobject,search_type,"table", title="Shot Migration", search=search)
            main_div.add(aref_head)
            main_div.add(aref_div)
        """

        return main_div





    def get_planned_wdg(self, sobject):
        
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        content_id ='summary_planned_%s' %sobject.get_id()
        title_id = 'planned_head_%s' %sobject.get_id()

        head = DivWdg()
        head.add_style('height','1.8em')
        title = self._get_title_span()

        dyn_load = AjaxLoader(display_id=content_id)

        args_dict = {'search_type': sobject.get_search_type()}
        args_dict['search_id'] = sobject.get_id()
        dyn_load.set_load_method('_get_planned_wdg')
        dyn_load.set_load_class('pyasm.prod.web.ShotDetailWdg', load_args=args_dict)
        on_script = dyn_load.get_on_script(load_once=True)

        swap_wdg = self._get_swap_wdg(title_id)
        swap_wdg.add_action_script(on_script, "toggle_display('%s')" %content_id)


        head.add(swap_wdg)
        head.add(title)
        title.add("Assigned Asset Instances")
        self.add_title_style(title, title_id, swap_wdg)
        
        div = DivWdg(id=content_id)
        div.add_style("width: 98%")
        div.add_style("margin-left: auto")
        div.add_style('display','none')

        return head, div

    def _get_planned_wdg(self):
        ''' this method is called thru ajax '''
        args = WebContainer.get_web().get_form_args()
        
        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']
        sobject = Search.get_by_id(search_type, search_id)

        assets_int_shot_wdg = AssetsInShotWdg()
        assets_int_shot_wdg.set_sobject(sobject)

        div = Widget()
      
        div.add(assets_int_shot_wdg)
        div.add(HtmlElement.br(2))
        return div




class LayerDetailWdg(AssetDetailWdg):

    def get_display(self):
	'''
        # get the args in the URL
        args = WebContainer.get_web().get_form_args()
        search_type = args['search_type']
        search_id = args['search_id']

	'''
        sobject = self.parent
        main_div = DivWdg()
        main_div.add_style("width: 98%")
        main_div.add_style("float: right")
        self.add(main_div)

        # get planned assets
        #planned_head, planned_div = self.get_planned_wdg(sobject)
        #main_div.add(planned_head)
        #main_div.add(planned_div)

        # add notes
        notes_head, notes_div = self.get_sobject_wdg(sobject, "sthpw/note", "summary", show_count=False)
        main_div.add(notes_head)
        main_div.add(notes_div)
    
        from pyasm.prod.biz import Submission
        notes = Submission.get_all_notes(sobject)

        # add references
        #ref_head, ref_div = self.get_sobject_wdg(sobject, "sthpw/connection","detail", title="References")
        #main_div.add(ref_head)
        #main_div.add(ref_div)

        
        #task_head, task_div = self.get_sobject_wdg(sobject, "sthpw/task", "summary")
        #main_div.add(task_head)
        #main_div.add(task_div)


        # add dailies: need a special function for this
        dailies_head, dailies_div = self.get_dailies_wdg(sobject)
        main_div.add(dailies_head)
        main_div.add(dailies_div)


        # add sobject history div
        hist_head, hist_div = self.get_sobject_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)



        # add checkin history div
        hist_head, hist_div = self.get_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        # queue
        queue_head, queue_div = self.get_sobject_wdg(sobject, "sthpw/queue","summary")
        main_div.add(queue_head)
        main_div.add(queue_div)



        # renders
        render_head, render_div = self.get_sobject_wdg(sobject, "prod/render")
        main_div.add(render_head)
        main_div.add(render_div)



        return main_div



class TaskDetailWdg(AssetDetailWdg):

    '''Details for Tasks in My Tactic tab'''
    def get_display(self):
 
        sobject = self.parent
        main_div = DivWdg()
        main_div.add_style("width: 98%")
        main_div.add_style("float: right")
       
        # add notes
        notes_head, notes_div = self.get_sobject_wdg(sobject, "sthpw/note", view="summary", show_count=False)
        main_div.add(notes_head)
        main_div.add(notes_div)

        return main_div

    def _get_sobject_search(self, sobject, search_type):
        ''' get the search for this sobject and search_type '''
        if search_type.startswith("sthpw/note"):
            search = Search(search_type)
            search.add_filter('search_type', sobject.get_value('search_type'))
            search.add_filter('search_id', sobject.get_value('search_id'))
            search.add_filter('context', sobject.get_process())
        
        return search

class SimpleDetailWdg(AssetDetailWdg):
    '''Used for Simple type project'''

    def get_display(self):
        sobject = self.parent

        main_div = DivWdg()
        main_div.add_style("width: 98%")
        main_div.add_style("float: right")

       
        # add notes
        notes_head, notes_div = self.get_sobject_wdg(sobject, "sthpw/note", view="summary", show_count=False)
        main_div.add(notes_head)
        main_div.add(notes_div)

         # add references
        ref_head, ref_div = self.get_sobject_wdg(sobject, "sthpw/connection", view="detail", title="References")
        main_div.add(ref_head)
        main_div.add(ref_div)


        task_head, task_div = self.get_sobject_wdg(sobject, "sthpw/task", view="summary")
        main_div.add(task_head)
        main_div.add(task_div)


        # add sobject history div
        hist_head, hist_div = self.get_sobject_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        # add checkin history div
        hist_head, hist_div = self.get_history_wdg(sobject)
        main_div.add(hist_head)
        main_div.add(hist_div)

        return main_div
