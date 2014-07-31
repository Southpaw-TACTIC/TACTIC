###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["DeleteToolWdg", "DeleteDelegateCmd", "DeleteCmd", "DeleteSearchTypeToolWdg", 'DeleteSearchTypeCmd', "DeleteProjectToolWdg", "DeleteProjectCmd"]

from pyasm.common import Common, TacticException, Container, Environment
from pyasm.biz import Schema, Project
from pyasm.command import Command
from pyasm.search import Search, SearchKey, SearchType, TableDropUndo, FileUndo, SqlException, SearchException
from pyasm.web import DivWdg, Table, SpanWdg, HtmlElement, Widget
from pyasm.widget import ThumbWdg, IconWdg, WidgetConfig, TextWdg, TextAreaWdg, SelectWdg, HiddenWdg, WidgetConfig, CheckboxWdg, RadioWdg, SwapDisplayWdg

from tactic.ui.widget import SingleButtonWdg, ActionButtonWdg, ButtonRowWdg, ButtonNewWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg


import random





class DeleteToolWdg(BaseRefreshWdg):
    
   
    def init(my):
        my.search_keys_dict = {}
        my.warning_msg = None
        my.level_dict = {}

    def get_level(my, search_type, level):
        ''' Get the level of this search_type in the hierarchy. 
            e.g.If vfx/sequce is 0, vfx/shot is 1 and vfx/layout is 2''' 
        cur_level = my.level_dict.get(search_type)
        if cur_level == None:
            if not level:
                cur_level = 0
            else:
                cur_level = level
            my.level_dict[search_type] = cur_level

        return level

    def populate_checklist(my, content, sobjects, level=0):
        
        search_type = sobjects[0].get_base_search_type()

        if sobjects:
            search_keys = [x.get_search_key() for x in sobjects]
            if my.search_keys_dict.get(search_type):
                my.warning_msg = "When looking through dependecies, [%s] has been detected more than once in the search."%search_type
            my.search_keys_dict[search_type] = search_keys


        # find all the relationships
        related_types = SearchType.get_related_types(search_type, direction='children') 
        
     
        if not related_types:
            return 0
    
        related_div = DivWdg()

        
        checkbox = CheckboxWdg('related_to')
        checkbox.add_behavior({'type': 'click_up',
            'current_stype': search_type,
            'cbjs_action': ''' var top = bvr.src_el.getParent('.spt_delete_top');
            var stype = bvr.current_stype.replace('/', '_');
            var cbs = top.getElements('.spt_' + stype);
            for (var k=0; k<cbs.length; k++)
                cbs[k].checked = bvr.src_el.checked;
            '''})

        related_div.add(checkbox) 
        content.add(related_div)

        swap = SwapDisplayWdg.get_triangle_wdg()
        related_div.add(swap)
        
        items_div = DivWdg()
        SwapDisplayWdg.create_swap_title('', swap, items_div, is_open=False)
        content.add( items_div )
        
        items_div.add_style("padding: 10px")
        valid_related_ctr = 0
        sub_total = 0
        
        level = my.get_level(search_type, level)
        level +=1
        for related_type in related_types:
            
            if related_type == "*":
                print "WARNING: related_type is *"
                continue
            if related_type == search_type:
                continue
            if related_type in ['sthpw/search_object','sthpw/search_type']:
                continue
            try:
                SearchType.get(related_type)
                check_stype = True
            except:
                check_stype = False

            if not check_stype:
                continue   
            item_div = my.get_item_div(sobjects, related_type, level)
            if item_div:
                items_div.add(item_div)
                valid_related_ctr += 1
            expr = "@SOBJECT(%s)"%(related_type)
            sub_sobjects = Search.eval(expr, sobjects=sobjects)
            
          
            if sub_sobjects: 
                sub_total += len(sub_sobjects)
                # If related_tupe is a central sType, ends the search
                if not sub_sobjects[0].get_base_search_type().startswith('sthpw/'):

                    my.populate_checklist(content, sub_sobjects, level=level)
        
        label ="related to %s: (%s) "%(search_type, sub_total) 
        checkbox.label = label
        if sub_total > 0:
            checkbox.set_checked()
        return valid_related_ctr

    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_delete_top")
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_border()
        top.add_style("width: 400px")
        top.add_border()


        search_key = my.kwargs.get("search_key")

        
        search_keys = my.kwargs.get("search_keys")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            sobjects = [sobject]
            search_keys = [search_key]
        elif search_keys:
            sobjects = Search.get_by_search_keys(search_keys)
            sobject = sobjects[0]

        if not sobjects:
            msg =  "%s not found" %search_key
            return msg
        search_type = sobject.get_base_search_type()
        

        if search_type in ['sthpw/project', 'sthpw/search_object']:
            msg = 'You cannot delete these items with this tool'
            return msg


        my.search_keys = search_keys


        title = DivWdg()
        top.add(title)
        title.add_color("background", "background", -10)
        
        if len(my.search_keys) > 1:
            entry_label = 'entries'
            title.add("Delete %s %s %s" % (len(my.search_keys), sobject.get_search_type_title(), entry_label))
        else:
            entry_label = 'entry'
            title.add("Delete %s %s [%s]" % ( sobject.get_search_type_title(), entry_label, sobject.get_code()))
        title.add_style("font-size: 14px")
        # no bold
        title.add_style("padding: 10px")

        content = DivWdg()
       
        top.add(content)
        content.add_style("padding: 10px")


        content.add("The %s to be deleted has a number of dependencies:<br/>" %entry_label, 'heading')

       
        related_div = DivWdg()
        related_div.add_style('padding: 10px')
        related_div.set_round_corners()
        related_div.add_color('background','background', -6)
        
        content.add("<br/>")
        content.add(related_div)

        valid_related_ctr = my.populate_checklist(related_div, sobjects)
       


        content.add(HtmlElement.br())

        if valid_related_ctr > 0:
            icon = IconWdg("WARNING", IconWdg.WARNING)
            icon.add_style("float: left")
            table = Table()
            content.add( table )
            
            table.add_row()
            td =  table.add_cell(icon)
            td.add_style('vertical-align','top')
            msg_wdg = Widget()
            msg_wdg.add("<div><b>WARNING: By selecting the related items above, you will delete them together with this sObject.</b></div>")
            msg_wdg.add("<br/>"*2)
            if my.warning_msg:
                msg_wdg.add(my.warning_msg)
            table.add_cell(msg_wdg)
        else:
            # changed the heading to say no dependencies
            content.add("The item to be deleted has no dependencies.<br/>", 'heading')
            related_div.add_style('display: none')


    

        
        button_div = DivWdg()
        content.add("Continue to delete?")
        content.add("<br/>"*2)

        button_div.add_styles('width: 200px; height: 25px; margin-left: auto; margin-right: auto;')
        button = ActionButtonWdg(title="Delete")
        button_div.add(button)
        content.add(button_div)
        button.add_style("float: left")

        button.add_behavior( {
        'type': 'click_up',
        'search_keys_dict': my.search_keys_dict,
        'cbjs_action': '''
        spt.app_busy.show("Deleting");

        var top = bvr.src_el.getParent(".spt_delete_top");
        var values = spt.api.Utility.get_input_values(top);

        var class_name = "tactic.ui.tools.DeleteDelegateCmd";
        var kwargs = {
            'search_keys_dict': bvr.search_keys_dict,
            'values': values
        };
        var server = TacticServerStub.get();
        try {
            server.start({'title': 'Delete sObject', 'description': 'Delete sObject [' + bvr.search_keys + ']'});
            server.execute_cmd(class_name, kwargs);
            server.finish();

            // run the post delete and destroy the popup
            var popup = bvr.src_el.getParent(".spt_popup");
            if (popup.spt_on_post_delete) {
                popup.spt_on_post_delete();
            }

            spt.popup.destroy(popup);


        }
        catch(e) {
            spt.alert(spt.exception.handler(e));
        }

        spt.app_busy.hide();
       
        '''
        } )



        button = ActionButtonWdg(title="Cancel")
        button.add_style("float: left")
        button.add_style("margin-left: 20px")
        button_div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_popup");
        top.destroy();
        '''
        } )


        content.add("<br clear='all'/>")


        return top



    def get_item_div(my, sobjects, related_type, level):
        item_div = DivWdg()

        sobject = sobjects[0]
        
        current_type = sobject.get_base_search_type()
        

        checkbox = CheckboxWdg('related_types')
        tmp_stype = current_type.replace('/','_')
        checkbox.add_class('spt_%s'%tmp_stype)

        item_div.add(checkbox)
      
        # prefix with current sType current_type
        checkbox.set_attr("value", "%s|%s|%s" %(current_type, related_type, level))
        checkbox.set_checked() 
        item_div.add(related_type)
        item_div.add(": ")

        
        related_total = 0
        if related_type.startswith("@SOBJECT"):
            related_sobjects = Search.eval(related_type, [sobject], list=True)
            related_total =len(related_sobjects)
            
        else:
            try:
                related_sobjects = []
                for sobject in sobjects:
                    
                    count = Search.eval("@COUNT(%s)"%related_type, sobjects=[sobject])
                   
                    related_total += count
                    
                    

            except Exception, e:
                print "WARNING: ", e
                related_total = 0
                #raise

        
        item_div.add("(%s)" % (related_total))    

        if related_total == 0:
            item_div.add_style("opacity: 0.5")
            return None
        else:
            # leave them unchecked for now to account for user's careless delete behavior
            pass

            # skip checking login by default to avoid accidental delete
            #if related_type != 'sthpw/login':
            #    checkbox.set_checked()

        return item_div



class DeleteDelegateCmd(Command):
    ''' Delegate the search keys of a particular sType and its checked related types to its own DeleteCmd.'''
  

    def execute(my):

        related_types_dict = {}
        stype_level_dict = {}

        search_keys_dict = my.kwargs.get("search_keys_dict")

        values = my.kwargs.get("values")
        if values:
            related_types = values.get("related_types")
        else:
            related_types = None
       
        
        # filter out the empty ones
        if related_types:
            related_types = [x for x in related_types if x]
        
        # this is no dependency case
        if not related_types:
            search_keys = search_keys_dict.values()[0]
            cmd = DeleteCmd(search_keys=search_keys, values = {'related_types': related_types})
            cmd.execute()
            return
        
       

        for related_type in related_types:
            if not related_type:
                continue
            prefix, actual_type, level = related_type.split('|')
            stype_level_dict[prefix] = level
            related_types_list = related_types_dict.get(prefix)
            if related_types_list == None:
                related_types_list = []
                related_types_dict[prefix] = related_types_list
            related_types_list.append(actual_type)

        sort_keys = stype_level_dict.values()
        # order the delete from bottom up (children to the current sobject)
        stype_list = sorted(stype_level_dict, key=stype_level_dict.get, reverse=True)

        
        for stype in stype_list:
            search_keys = search_keys_dict.get(stype)
            related_types = related_types_dict.get(stype)
            cmd = DeleteCmd(search_keys=search_keys, values = {'related_types': related_types})
            cmd.execute()




class DeleteCmd(Command):

    def is_undoable(cls):
        return True
    is_undoable = classmethod(is_undoable)

    def execute(my):

        # if a single sobject is passed in
        sobject = my.kwargs.get("sobject")
        if not sobject:
            search_key = my.kwargs.get("search_key")
            sobject = Search.get_by_search_key(search_key)

        if sobject:
            sobjects = [sobject]
        else:
            search_keys = my.kwargs.get("search_keys")
            sobjects = Search.get_by_search_keys(search_keys)

        if not sobjects:
            return


        # find all the relationships
        my.schema = Schema.get()
        for sobject in sobjects:
            my.delete_sobject(sobject)

            
    
        
    def delete_sobject(my, sobject):

        search_type = sobject.get_base_search_type()

        # this is used by API method delete_sobject
        auto_discover = my.kwargs.get("auto_discover")
        
        values = my.kwargs.get("values")
        if values:
            related_types = values.get("related_types")
        elif auto_discover:
            related_types = SearchType.get_related_types(search_type, direction="children")
        else:
            related_types = None


        # always delete notes and task and snapshot
        #if not related_types:
        #    related_types = ['sthpw/note', 'sthpw/task', 'sthpw/snapshot']
        #related_types = my.schema.get_related_search_types(search_type)
        if related_types:
            for related_type in related_types:
                if not related_type or related_type == search_type:
                    continue

                # snapshots take care of sthpw/file in the proper manner, so
                # skip them here
                if related_type == 'sthpw/file':
                    continue

                related_sobjects = sobject.get_related_sobjects(related_type)
                for related_sobject in related_sobjects:
                    if related_type == 'sthpw/snapshot':
                        my.delete_snapshot(related_sobject)

                    else:
                        related_sobject.delete()


        # implicitly remove "directory" files associated with the sobject
        search = Search("sthpw/file")
        search.add_op("begin")
        search.add_filter("file_name", "")
        search.add_null_filter("file_name")
        search.add_op("or")
        search.add_parent_filter(sobject)
        file_objects = search.get_sobjects()
        for file_object in file_objects:
            base_dir = Environment.get_asset_dir()
            relative_dir = file_object.get("relative_dir")
            lib_dir = "%s/%s" % (base_dir, relative_dir)
            print "removing: ", lib_dir
            FileUndo.rmdir(lib_dir)
            file_object.delete()


        # finally delete the sobject
        print "deleting: ", sobject.get_search_key()
        if search_type == 'sthpw/snapshot':
            my.delete_snapshot(sobject)
        else:
            sobject.delete()


    
    def delete_snapshot(my, snapshot):

        # get all of the file paths
        file_paths = snapshot.get_all_lib_paths()

        files = snapshot.get_related_sobjects("sthpw/file")
        for file in files:
            print "deleting file: ", file.get_search_key()
            file.delete()

        # remove the files from the repo
        for file_path in file_paths:
            "removing path: ", file_path
            FileUndo.remove(file_path)

        print "deleting snapshot: ", snapshot.get_search_key()
        snapshot.delete()







class DeleteSearchTypeToolWdg(DeleteToolWdg):

    def init(my):
        # this doesn't work
        SearchType.clear_cache()


    def get_display(my):
        top = my.top
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("width", "400px")
        top.add_class('spt_delete_stype_top')
        top.add_border()

        project_code = Project.get_project_code()
        # Note search types should only really be deleted if they were just
        # created

        search_type = my.kwargs.get("search_type")
        if not search_type:
            node_name = my.kwargs.get("node_name")
            if node_name:
                #project_code = Project.get_project_code()
                search_type = "%s/%s" % (project_code, node_name)

        assert search_type
        built_in_stypes = ['task','note','work_hour','login','login_group','schema','project','login_in_group','snapshot','file','trigger','spt_trigger','widget_config','custom_script','notification','notification_log','file_access','cache','exception_log','milestone','pipeline','pref_list','pref_setting','project_type','repo','remote_repo','search_sobject','sobject_list','ticket','db_resource','wdg_settings','status_log','debug_log','transaction_log', 'sobject_log']

        for tbl in built_in_stypes:
            if search_type == 'sthpw/%s'%tbl:
                top.add("sType [%s] is internal and cannot be deleted!" % search_type)
                top.add_style("font-size: 14px")
                top.add_style('padding: 20px')
                return top

        search_type_obj = SearchType.get(search_type)
        if not search_type:
            top.add("sType [%s] does not exist!" % search_type)
            top.add_style("font-size: 14px")
            top.add_style('padding: 20px')
            return top
        table = search_type_obj.get_table()

        db_val = search_type_obj.get_value('database')
        if db_val == '{project}':
            label = ''
        elif db_val == 'sthpw':
            label = 'built-in'
        else:
            label = 'project-specific'

        
        # warn if more than 1 sType point to the same table in the same project
        expr = "@GET(sthpw/search_type['table_name', '%s']['database', 'in',  '{project}|%s']['namespace','%s'].search_type)" %(table, project_code, project_code)
        rtn = Search.eval(expr)
        
        warning_msg = ''
        if len(rtn) > 1:
            warning_msg = 'Warning: There is more than 1 sType [%s] pointing to the same table [%s]. Deleting will affect both sTypes.' %(', '.join(rtn), table)
           
        title_wdg = DivWdg()

        top.add(title_wdg)
        title_wdg.add(IconWdg(icon=IconWdg.WARNING))
        title_wdg.add("Delete %s sType: %s" % (label,search_type))
        title_wdg.add_gradient("background", "background", -10, -10)
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("font-size: 14px")


        content = DivWdg()
        top.add(content)
        content.add_style("padding: 10px")

        if warning_msg:
            content.add(DivWdg(warning_msg, css='warning'))
            content.add("<br/>")
        content.add("This sType uses the table \"%s\" to store items.<br/>" % table)


        content.add("<br/>")

        search = Search(search_type)
        count = search.get_count()
        content.add("Number of items in the table: %s<br/>" % count)

        content.add("<br/>")

        search.add_column("id")
        sobjects = search.get_sobjects()

        if sobjects:
            items_search_type = sobjects[0].get_search_type()

            search_ids = [x.get_id() for x in sobjects]

            notes_search = Search("sthpw/note")
            notes_search.add_filters("search_id", search_ids)
            notes_search.add_filter("search_type", items_search_type)
            note_count = notes_search.get_count()
            cb = CheckboxWdg('related_types')
            cb.set_attr('value', 'sthpw/note')
            content.add(cb)
            content.add(SpanWdg("Number of related notes: %s"% note_count, css='small') )
            content.add(HtmlElement.br())

            tasks_search = Search("sthpw/task")
            tasks_search.add_filters("search_id", search_ids)
            tasks_search.add_filter("search_type", items_search_type)
            task_count = tasks_search.get_count()
            cb = CheckboxWdg('related_types')
            cb.set_attr('value', 'sthpw/task')
            content.add(cb)
            content.add(SpanWdg("Number of related tasks: %s"% task_count, css='small') )
            content.add(HtmlElement.br())


            snapshots_search = Search("sthpw/snapshot")
            snapshots_search.add_filters("search_id", search_ids)
            snapshots_search.add_filter("search_type", items_search_type)
            snapshot_count = snapshots_search.get_count()
            cb = CheckboxWdg('related_types')
            cb.set_attr('value', 'sthpw/snapshot')
            content.add(cb)
            content.add(SpanWdg("Number of related snapshots: %s"% snapshot_count, css='small') )
            content.add(HtmlElement.br())

        pipelines_search = Search("sthpw/pipeline")
        pipelines_search.add_filter("search_type", search_type)
        pipeline_count = pipelines_search.get_count()
        cb = CheckboxWdg('related_types')
        cb.set_attr('value','sthpw/pipeline')
        content.add(cb)
        content.add(SpanWdg("Number of related pipelines: %s"% pipeline_count, css='small') )
        content.add(HtmlElement.br(2))




        content.add("<b>WARNING: Deleting the sType will delete all of these items.</b> ")
        content.add("<br/>"*2)
        content.add("Do you wish to continue deleting?")
        content.add("<br/>"*2)

        button_div = DivWdg()
        button_div.add_styles('width: 300px; height: 50px')
        button = ActionButtonWdg(title="Delete")
        button_div.add(button)
        content.add(button_div)
        button.add_style("float: left")

        button.add_behavior( {
        'type': 'click_up',
        'search_type': search_type,
        'cbjs_action': '''
        spt.app_busy.show("Deleting sType");
        var class_name = "tactic.ui.tools.DeleteSearchTypeCmd";
        var ui_top = bvr.src_el.getParent(".spt_delete_stype_top");
        var values = spt.api.Utility.get_input_values(ui_top);
        var kwargs = {
            'search_type': bvr.search_type,
             'values': values
        };
        var server = TacticServerStub.get();
        try {
            server.start({'title': 'Delete sType', 'description': 'Delete sType [' + bvr.search_type + ']'});
            server.execute_cmd(class_name, kwargs);
            var top = bvr.src_el.getParent(".spt_popup");
            spt.pipeline.remove_node(top.stype_node);

            // force a schema save
            spt.named_events.fire_event('schema|save', bvr)
            top.destroy();
            
            server.finish();
        
        }
        catch(e) {
            spt.alert(spt.exception.handler(e));
        }

        spt.app_busy.hide();

        spt.notify.show_message("Successfully deleted sType ["+bvr.search_type+"]");
       
        '''
        } )



        button = ActionButtonWdg(title="Cancel")
        button.add_style("float: left")
        button.add_style("margin-left: 20px")
        button_div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_popup");
        top.destroy();
        '''
        } )


        return top



class DeleteSearchTypeCmd(Command):

    def check(my):
        my.search_type = my.kwargs.get("search_type")
        my.values = my.kwargs.get("values")

        my.db_resource = SearchType.get_db_resource_by_search_type(my.search_type)
        my.database = my.db_resource.get_database()
        my.search_type_obj = SearchType.get(my.search_type)
        if my.database != Project.get_project_code() and my.database !='sthpw':
            raise TacticException('You are not allowed to delete the sType [%s] from another project [%s].' %(my.search_type, my.database))
            return False
        
        return True

    def execute(my):
        search_type = my.search_type

        search_type_obj = my.search_type_obj 

        database = my.database

        try:
            db_val = search_type_obj.get_value('database')
            search = Search(search_type)
            sobjects = search.get_sobjects()

            for sobject in sobjects:
                cmd = DeleteCmd(sobject=sobject, values=my.values)
                cmd.execute()
        except (SqlException, SearchException), e:
            print "WARNING: ", e

       
        try:
            table_name = search_type_obj.get_table()
            # must log first
            TableDropUndo.log(search_type, database, table_name)
        except (SqlException, SearchException), e:
            print "WARNING: ", e
       


        try:
            from pyasm.search import DropTable
            cmd = DropTable(search_type)
            cmd.commit()
        except (SqlException, SearchException), e:
            print "WARNING: ", e

        
       
        # dump the table to a file and store it in cache
        #from pyasm.search import TableDataDumper
        #dumper = TableDataDumper()
        #dumper.set_info(table)
        #dumper.execute()


        # NOTE: already dealt with in DeleteCmd. get all of the pipelines
        """
        pipelines = search_type_obj.get_related_sobjects("sthpw/pipeline")
        for pipeline in pipelines:
            print "deleting: ", pipeline.get_search_key()
            pipeline.delete()
        """
 
        # delete the actual search type entry if it's not multi-project
        if db_val != '{project}':
            search_type_obj.delete()






class DeleteProjectToolWdg(DeleteToolWdg):

    # For now, project creation is not undoable
    def is_undoable(cls):
        return True
    is_undoable = classmethod(is_undoable)


    def get_related_types(my, search_type):
        # find all the relationships
        schema = Schema.get()
        related_types = schema.get_related_search_types(search_type)
        parent_type = schema.get_parent_type(search_type)
        child_types = schema.get_child_types(search_type)


        # some special considerations
        # FIXME: this needs to be more automatic.  Should only be
        # deletable children (however, that will be defined)
        if search_type in ['sthpw/task','sthpw/note', 'sthpw/snapshot']:
            if "sthpw/project" in related_types:
                related_types.remove("sthpw/project")

            if "sthpw/login" in related_types:
                related_types.remove("sthpw/login")

            if "config/process" in related_types:
                related_types.remove("config/process")


        if parent_type in related_types:
            related_types.remove(parent_type)

        related_types.append('sthpw/note')
        related_types.append('sthpw/task')
        related_types.append('sthpw/snapshot')
        related_types.append('sthpw/work_hour')
        related_types.append('sthpw/pipeline')
        related_types.append('sthpw/sobject_list')

        return related_types


    def get_display(my):
        top = my.top
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_style("width", "400px")
        top.add_border()
        top.add_class("spt_delete_project_tool_top")

        project_code = my.kwargs.get("project_code")
        if project_code:
            project = Project.get_by_code(project_code)
        else:
            search_key = my.kwargs.get("search_key")
            project = Search.get_by_search_key(search_key)
            if project:
                project_code = project.get_code()

       
           
        title_wdg = DivWdg()

        if project:
            top.add(title_wdg)
            title_wdg.add(IconWdg(icon=IconWdg.WARNING))
            title_wdg.add("Deleting Project: %s" % project.get_value("title") ) 
            title_wdg.add_gradient("background", "background", -10, -10)
            title_wdg.add_style("padding: 5px")
            title_wdg.add_style("font-weight: bold")
            title_wdg.add_style("font-size: 14px")


        content = DivWdg()
        top.add(content)
        content.add_style("padding: 10px")

        if not search_key:
            warning_msg = "Projects must be deleted individually"
            content.add(DivWdg(warning_msg, css='warning'))
            content.add("<br/>")
            return top

        warning_msg = "Deleting a project will delete the database associated with this project.  All data will be lost.  Please consider carefully before proceeding."
        if warning_msg:
            content.add(DivWdg(warning_msg, css='warning'))
            content.add("<br/>")

        
        if not project_code:
            content.add("This project [%s] has been deleted."%search_key)
            return top
        elif not project:
            content.add("This project [%s] has been deleted."%project_code)
            return top


        assert project_code
        assert project

        content.add("<br/>")

        content.add("<b>WARNING: These items will be deleted, but the sTypes entries in search_objects table will be retained.</b> ")


      
        content.add("<br/>")
        content.add("<br/>")

        total_items_wdg = DivWdg()
        total_items = 0
        content.add(total_items_wdg)


        # find all of the sTypes
        details_wdg = DivWdg()
        content.add(details_wdg)
        details_wdg.add_style("max-height: 300px")
        details_wdg.add_style("overflow-y: auto")
        details_wdg.add_style("padding-left: 15px")
        details_wdg.add_border()

        search_types = project.get_search_types()

        related_types = []

        for search_type_obj in search_types:
            search_type_wdg = DivWdg()
            title = search_type_obj.get_title()
            search_type = search_type_obj.get_value("search_type")

            search_type_wdg.add_style("margin-top: 5px")
            search_type_wdg.add_style("margin-bottom: 5px")


            details_wdg.add(search_type_wdg)
            search_type_wdg.add(title)
            search_type_wdg.add(" (%s)" % search_type )

            search = Search( search_type, project_code=project_code )
            count = search.get_count()
            total_items += count
            search_type_wdg.add("&nbsp; - &nbsp; %s item(s)" % count)

            # TODO: this is similar to SearchType.get_related_types(). streamline at some point. 
            related_types = my.get_related_types(search_type)
            for related_type in related_types:

                search = Search(related_type)
                full_search_type = "%s?project=%s" % (search_type, project_code)
                if related_type.startswith("sthpw/"):
                    search.add_filter("search_type", full_search_type)
                count = search.get_count()
                if count == 0:
                    continue
                total_items += count


                related_wdg = DivWdg()
                related_wdg.add_style('padding-left: 25px')
                search_type_wdg.add(related_wdg)
                related_wdg.add(related_type)
                related_wdg.add("&nbsp; - &nbsp; %s item(s)" % count)


        if total_items:
            total_items_wdg.add("Total # of items to be deleted: ")
            total_items_wdg.add(total_items)
            total_items_wdg.add_style("font-size: 14px")
            total_items_wdg.add_style("font-weight: bold")
            total_items_wdg.add("<br/>")



        content.add("<br/>"*2)
        content.add("<b>Do you wish to continue deleting? </b>")
        radio = RadioWdg("mode")
        radio.add_class("spt_mode_radio")
        radio.set_value("delete")
        content.add(radio)
        content.add("<br/>"*2)

        #content.add("<b>Or do you just wish to retire the project? </b>")
        #radio = RadioWdg("mode")
        #radio.add_class("spt_mode_radio")
        #radio.set_value("retire")
        #content.add(radio)
        #content.add(radio)

        #content.add("<br/>"*2)


        #button = ActionButtonWdg(title="Retire")
        #content.add(button)
        #button.add_style("float: left")

        buttons = Table()
        content.add(buttons)
        buttons.add_row()
        buttons.add_style("margin-left: auto")
        buttons.add_style("margin-right: auto")
        buttons.add_style("width: 250px")


        button = ActionButtonWdg(title="Delete")
        buttons.add_cell(button)

        button.add_behavior( {
        'type': 'click_up',
        #'search_type': search_type,
        'project_code': project_code,
        'related_types': related_types,
        'cbjs_action': '''
            spt.app_busy.show("Deleting");
            var class_name = "tactic.ui.tools.DeleteProjectCmd";
            var kwargs = {
                'project_code': bvr.project_code,
                'related_types': bvr.related_types
            };

            var top = bvr.src_el.getParent(".spt_delete_project_tool_top");
            var radios = top.getElements(".spt_mode_radio");

            //if (!radios[0].checked && !radios[1].checked) {
            if (!radios[0].checked) {
                spt.alert("Please confirm the delete by checking the radio button.");
                spt.app_busy.hide();
                return;
            }

            var mode = 'retire';
            if (radios[0].checked == true) {
                mode = 'delete';
            }


            if (mode == 'retire') {
                return;
            }



            var success = false;
            var server = TacticServerStub.get();
            setTimeout(function() {
                spt.app_busy.show("Deleting Project ["+bvr.project_code+"]")
                var error_message = "Error deleting project ["+bvr.project_code+"]";
                try {
                    server.start({'title': 'Deleted Project ', 'description': 'Deleted Project [' + bvr.project_code + ']'});
                    server.execute_cmd(class_name, kwargs);
                    success = true;

                    var top = bvr.src_el.getParent(".spt_popup");
                    spt.popup.destroy(top);
                    server.finish();
                }
                catch(e) {
                    error_message = spt.exception.handler(e);
                }

                
                spt.app_busy.hide();

                if (success) {
                    spt.notify.show_message("Successfully deleted project ["+bvr.project_code+"]");

                    spt.tab.set_main_body_tab();
                    spt.tab.reload_selected();
                }
                else {
                    if (error_message.test(/does not exist/))
                        error_message += '. You are advised to sign out and log in again.';
                    spt.error(error_message);
                }
            }, 100);
       
        '''
        } )



        button = ActionButtonWdg(title="Cancel")
        buttons.add_cell(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_popup");
        spt.popup.destroy(top);
        '''
        } )


        return top



class DeleteProjectCmd(DeleteCmd):


    def execute(my):
        from pyasm.search import DbContainer

        project_code = my.kwargs.get("project_code")
        if project_code:
            project = Project.get_by_code(project_code)
        else:
            search_key = my.kwargs.get("search_key")
            project = Search.get_by_search_key(search_key)
            project_code = project.get_code()


        assert project_code
        assert project


        # dump the database


        # remove all dependencies the sthpw database
        related_types = my.kwargs.get("related_types")
        if related_types:
            for related_type in related_types:
                search = Search(related_type)
                if related_type == "sthpw/schema":
                    search.add_filter("code", project_code)
                else:
                    search.add_filter("project_code", project_code)
                count = search.get_count()
                sobjects = search.get_sobjects()
                for sobject in sobjects:
                    if related_type == 'sthpw/snapshot':
                        my.delete_snapshot(sobject)
                    else:
                        sobject.delete()


        sthpw_project = Project.get_by_code('sthpw')
        
        # delete the database
        sthpw_db_resource = sthpw_project.get_project_db_resource()
        db_resource = project.get_project_db_resource()
        impl = sthpw_db_resource.get_database_impl()
        deleted_impl = db_resource.get_database_impl()

        if not impl.database_exists(db_resource):
            # remove the project entry
            project.delete()
            return

        # close this connection to the project to be deleted
        sql = DbContainer.get(db_resource)
        sql.close()

        if sql.get_database_type() == 'Sqlite':
            DbContainer.release_thread_sql()
        result = impl.drop_database(db_resource)

        # this is just extra check
        if result and "failed" in result:
            raise TacticException(result)
        
       
        Container.put("Sql:database_exists:%s"%db_resource.get_key(), None) 

		
       

        sql = DbContainer.get(db_resource, connect=True)
        if sql:
            try:
                if sql.get_database_type() != 'Sqlite':
                    if sql.get_connection() and sql.connect():
                        raise TacticException("Database [%s] still exists. There could still be connections to it."%project_code)
            except SqlException, e:
                pass
        # remove the project entry
        project.delete(triggers=False)

      

        return



