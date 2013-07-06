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


__all__ = ['PipelineEditWdg', 'PipelineEditCbk', 'PipelineCreateCbk']

from pyasm.biz import Pipeline, Project
from pyasm.command import Command
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, Table
from pyasm.widget import TextWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import SingleButtonWdg, ActionButtonWdg, IconButtonWdg


class PipelineEditWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_pipelines_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        search_type = my.kwargs.get("search_type")
        pipeline_code = my.kwargs.get("pipeline_code")

        if search_type:
            search = Search("sthpw/pipeline")
            search.add_filter("search_type", search_type)
            pipelines = search.get_sobjects()
        else:
            pipeline = Pipeline.get_by_code(pipeline_code)
            if pipeline:
                pipelines = [pipeline]
            else:
                pipelines = []


        if not pipelines:
            div = DivWdg()
            inner.add(div)
            inner.add_style("padding: 50px")
            div.add_border()
            div.add_color("color", "color3")
            div.add_color("background", "background3")
            div.add_style("width: 350px")
            div.add_style("height: 100px")
            div.add_style("padding: 30px")
           
            icon = IconWdg("WARNING", IconWdg.WARNING)
            div.add(icon)
            div.add("<b>This Searchable Type has not pipelines defined</b>")
            div.add("<br/>"*2)

            div.add("<b style='padding-left: 30px'>If you want to add a pipeline click create...</b>")
            div.add("<br/>"*2)
 
            button_div = DivWdg()
            div.add(button_div)

            button = ActionButtonWdg(title="Create", tip="Create pipeline")
            button_div.add(button)
            button.add_style("margin: auto")
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'cbjs_action': '''
                var server = TacticServerStub.get();

                var cmd = 'tactic.ui.startup.PipelineCreateCbk';
                var kwargs = {
                    search_type: bvr.search_type
                }
                server.execute_cmd(cmd, kwargs)

                var top = bvr.src_el.getParent(".spt_pipelines_top");
                spt.panel.refresh(top);
                '''
            } )

            return top



        # get the defalt task statuses
        task_pipeline = Pipeline.get_by_code("task")
        if task_pipeline:
            statuses = task_pipeline.get_process_names()
        else:
            statuses = ['Pending', 'In Progress', 'Complete']
        statuses_str = ",".join(statuses)



        pipelines_div = DivWdg()
        inner.add( pipelines_div )
        pipelines_div.add_style("font-size: 12px")
        pipelines_div.add_style("padding: 10px")

        buttons_div = DivWdg()
        pipelines_div.add(buttons_div)

        button = SingleButtonWdg( title="Save Pipelines", icon=IconWdg.SAVE )
        buttons_div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'default_statuses': statuses_str,
        'cbjs_action': '''
        spt.app_busy.show("Saving Pipeline...")

        setTimeout(function() {
            try {
                var top = bvr.src_el.getParent(".spt_pipelines_top");
                // get all the pipeline divs
                var pipeline_els = top.getElements(".spt_pipeline_top");
                var data = {};
                for ( var i = 0; i < pipeline_els.length; i++) {
                    var pipeline_code = pipeline_els[i].getAttribute("spt_pipeline_code");
                    var values = spt.api.Utility.get_input_values(pipeline_els[i]);
                    data[pipeline_code] = values;
                }


                var class_name = 'tactic.ui.startup.PipelineEditCbk';
                var kwargs = {
                    data: data
                }
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }
            spt.app_busy.hide();
        }
        , 100);

        '''
        } )


        buttons_div.add("<br clear='all'/>")
        buttons_div.add_style("margin-bottom: 5px")




        for pipeline in pipelines:
            pipeline_div = DivWdg()
            pipelines_div.add(pipeline_div)
            pipeline_div.add_class("spt_pipeline_top")


            code = pipeline.get_code()
            pipeline_div.add_attr("spt_pipeline_code", code)

            title = DivWdg()
            pipeline_div.add(title)
            title.add("Pipeline: ")
            title.add(code)
            title.add_style("padding: 5px")
            title.add_gradient("background", "background", -10)
            title.add_style("font-weight: bold")
            title.add_style("margin: -10 -10 5 -10")


            header_wdg = DivWdg()
            pipeline_div.add(header_wdg)
            header_wdg.add_color("background", "background", -5)

            headers = ['Process', 'Description', 'Task Status']
            widths = ['90px', '170px', '200px']
            for header, width in zip(headers,widths):
                th = DivWdg()
                header_wdg.add(th)
                th.add("<b>%s</b>" % header)
                th.add_style("float: left")
                th.add_style("width: %s" % width)
                th.add_style("padding: 3px")
            header_wdg.add("<br clear='all'/>")



            # get all of the process sobjects from this pipeline
            pipeline_code = pipeline.get_code()
            search = Search("config/process")
            search.add_filter("pipeline_code", pipeline.get_code() )
            process_sobjs = search.get_sobjects()

            process_sobj_dict = {}
            for process_sobj in process_sobjs:
                process = process_sobj.get_value("process")
                process_sobj_dict[process] = process_sobj


            from tactic.ui.container import DynamicListWdg
            dyn_list = DynamicListWdg()
            pipeline_div.add(dyn_list)
            pipeline_div.add_style("width: 725px")

            processes = pipeline.get_process_names()
            if not processes:
                processes.append("")
                processes.append("")
                processes.append("")

            processes.insert(0, "")

            for i, process in enumerate(processes):

                if process == '':
                    process_name = ''
                    description = ''
                else:
                    process_sobj = process_sobj_dict.get(process)
                    if process_sobj:
                        process_name = process_sobj.get_value("process")
                        description = process_sobj.get_value("description")
                    else:
                        if isinstance(process,basestring):
                            process_name = process
                        else:
                            process_name = process.get_name()
                        deccription = ''

                # get the task pipeline for this process
                if process_name:
                    process = pipeline.get_process(process_name)
                    task_pipeline_code = process.get_task_pipeline()
                    if task_pipeline_code != "task":
                        task_pipeline = Search.get_by_code("sthpw/pipeline", task_pipeline_code)
                    else:
                        task_pipeline = None
                else:
                    task_pipeline_code = "task"
                    task_pipeline = None


                process_div = DivWdg()
                process_div.add_style("float: left")
                process_div.add_class("spt_process_top")


                if i == 0:
                    dyn_list.add_template(process_div)
                else:
                    dyn_list.add_item(process_div)

                #process_div.add_style("padding-left: 10px")
                #process_div.add_style("margin: 5px")

                table = Table()
                process_div.add(table)
                table.add_row()

                text = NewTextWdg("process")
                table.add_cell(text)
                text.add_style("width: 95px")
                text.set_value(process_name)
                text.add_class("spt_process")

                # the template has a border
                if i == 0:
                    text.add_style("border: solid 1px #AAA")



                text = NewTextWdg("description")
                table.add_cell(text)
                text.add_style("width: 175px")
                text.set_value(description)
                # the template has a border
                if i == 0:
                    text.add_style("border: solid 1px #AAA")


                text = NewTextWdg("task_status")
                table.add_cell(text)
                text.add_style("width: 325px")

                #text.set_value(statuses_str)
                if task_pipeline:
                    statuses = task_pipeline.get_process_names()
                    text.set_value(",".join(statuses))
                else:
                    text.set_value("(default)")
                    #text.add_style("opacity: 0.5")
                

                text.add_style("border-style: none")

                text.add_behavior( {
                'type': 'click_up',
                'statuses': statuses_str,
                'cbjs_action': '''
                if (bvr.src_el.value == '(default)') {
                    bvr.src_el.value = bvr.statuses;
                }
                '''
                } )

                table.add_cell("&nbsp;"*2)

                button = IconButtonWdg(tip="Trigger", icon=IconWdg.ARROW_OUT)
                table.add_cell(button)
                button.add_behavior( {
                    'type': 'click_up',
                    'search_type': search_type,
                    'pipeline_code': pipeline_code,
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_process_top");
                    var process_el = top.getElement(".spt_process");

                    var process = process_el.value;
                    if (process == "") {
                        alert("Process value is empty");
                        return;
                    }

                    var class_name = 'tactic.ui.tools.TriggerToolWdg';
                    var kwargs = {
                        mode: "pipeline",
                        process: process,
                        pipeline_code: bvr.pipeline_code
                    };
                    spt.panel.load_popup("Trigger", class_name, kwargs);
     
                    '''
                } )

                """
                button = IconButtonWdg(tip="Edit", icon=IconWdg.EDIT)
                table.add_cell(button)
                button.add_behavior( {
                    'type': 'click_up',
                    'search_type': search_type,
                    'pipeline_code': pipeline_code,
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_process_top");
                    var process_el = top.getElement(".spt_process");

                    var process = process_el.value;
                    if (process == "") {
                        alert("Process value is empty");
                        return;
                    }

                    var class_name = 'tactic.ui.panel.EditWdg';
                    var kwargs = {
                        expression: "@SOBJECT(config/process['process','"+process+"'])"
                    }
                    spt.panel.load_popup("Trigger", class_name, kwargs);
     
                    '''
                } )
                """

                table.add_cell("&nbsp;"*3)
               


            pipeline_div.add("<br clear='all'/>")
            pipeline_div.add("<br clear='all'/>")



        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return top




class PipelineCreateCbk(Command):

    def execute(my):

        search_type = my.kwargs.get("search_type")

        code = my.kwargs.get("code")

        project_code = Project.get_project_code()
        parts = search_type.split("/")
        code = "%s/%s" % (project_code, parts[1])

        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_value("search_type", search_type)
        pipeline.set_value("code", code)

        pipeline.commit()





class PipelineEditCbk(Command):

    def execute(my):

        data = my.kwargs.get("data")

        for pipeline_code, pipeline_data in data.items():

            pipeline = Pipeline.get_by_code(pipeline_code)
            if not pipeline:
                pipeline = SearchType.create("sthpw/pipeline")
                pipeline.set_value("code", pipeline_code)

            # get the task_pipeline for this process
            prev_pipeline_xml = pipeline.get_value("pipeline")


            # get the input data
            processes = pipeline_data.get("process")
            statuses = pipeline_data.get("task_status")
            descriptions = pipeline_data.get("description")

            # go through each process and build up the xml
            pipeline_xml = my.create_pipeline_xml(processes)
            pipeline.set_value("pipeline", pipeline_xml)
            pipeline.set_pipeline(pipeline_xml)
            pipeline.on_insert()


            pipeline_xml = pipeline.get_xml_value("pipeline")

            # need to commit to get the pipeline code
            pipeline.commit()
            pipeline_code = pipeline.get_value("code")


            # this one doesn't call pipeline.update_process_table() since it adds additional description
            for i, process in enumerate(processes):
                if not process:
                    continue

                description = descriptions[i]

                # create the process as well
                search = Search("config/process")
                search.add_filter("pipeline_code", pipeline_code)
                search.add_filter("process", process)
                process_obj = search.get_sobject()
                if process_obj:
                    if description != process_obj.get_value("description"):
                        process_obj.set_value("description", description)
                        process_obj.commit()

                

            # handle the statuses for each process
            for process, status in zip(processes, statuses):
                if process == '':
                    continue

                if status == '(default)':
                    node = pipeline_xml.get_node("/pipeline/process[@name='%s']" % process)
                    pipeline_xml.del_attribute(node, "task_pipeline")
                    continue

                status_list = status.split(",")
                status_xml = my.create_pipeline_xml(status_list)

                project_code = Project.get_project_code()

                status_code = "%s/%s" % (project_code, process)
                status_pipeline = Search.get_by_code("sthpw/pipeline", status_code)
                if not status_pipeline:
                    status_pipeline = SearchType.create("sthpw/pipeline")
                    status_pipeline.set_value("description", 'Status pipeline for process [%s]'%process)
                    status_pipeline.set_value("code", status_code)
                    status_pipeline.set_value("search_type", "sthpw/task")
                    # update_process_table relies on this 
                    status_pipeline.set_pipeline(status_xml)
                else:
                    status_pipeline.set_pipeline(status_xml)
                    status_pipeline.on_insert()

                status_pipeline.set_value("pipeline", status_xml)
                status_pipeline.commit()


                status_pipeline_code = status_pipeline.get_code()
                # get the process node
                node = pipeline_xml.get_node("/pipeline/process[@name='%s']" % process)
                pipeline_xml.set_attribute(node, "task_pipeline", status_pipeline_code)

            # commit the changes again to get the task pipelines
            pipeline.set_value("pipeline", pipeline_xml.to_string())
            pipeline.commit()


    def create_pipeline_xml(my, statuses):
        if not statuses:
            statuses = []

        xml = []

        xml.append('''<pipeline>''')

        for status in statuses:
            if status == '':
                continue
            xml.append('''  <process name="%s"/>''' % status)

        

        last_status = None
        for i, status in enumerate(statuses):
            if status == '':
                continue

            if i == 0 or last_status == None:
                last_status = status
                continue


            xml.append('''  <connect from="%s" to="%s"/>''' % (last_status,status))
            last_status = status

        xml.append('''</pipeline>''')
        return "\n".join(xml)




class NewTextWdg(TextWdg):
    def init(my):

        #color = my.get_color("border", -20)
        color2 = my.get_color("border")
        color = my.get_color("border", -20)

        my.add_event("onfocus", "this.focused=true")
        my.add_event("onblur", "this.focused=false;$(this).setStyle('border-color','%s')" % color2)

        my.add_behavior( {
        'type': 'mouseover',
        'color': color,
        'cbjs_action': '''
        bvr.src_el.setStyle("border-color", bvr.color);
        '''
        } )
        my.add_behavior( {
        'type': 'mouseout',
        'color': color2,
        'cbjs_action': '''
        if (!bvr.src_el.focused) {
            bvr.src_el.setStyle("border-color", bvr.color);
        }
        '''
        } )

        super(NewTextWdg,my).init()



