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


__all__ = ["NamingElementWdg", 'NamingInputWdg', 'NamingAction', 'NamingInputWdg2']

import re

from pyasm.common import Common, Xml
from pyasm.biz import Project, Naming, NamingUtil
from pyasm.search import Search, SearchType
from pyasm.command import DatabaseAction
from pyasm.web import Widget, DivWdg, Table, WebContainer, AjaxLoader, HtmlElement, SpanWdg
from pyasm.widget import BaseTableElementWdg, TextWdg, XmlWdg, SelectWdg, HiddenWdg, CheckboxWdg, BaseInputWdg, ButtonWdg, IconButtonWdg, IconWdg
from pyasm.widget import ProdIconButtonWdg




class NamingInputWdg(BaseInputWdg):

    def get_ajax_inputs(my):
        # how to determine 
        return ["search_type", "search_id", "naming", "widget_name"]

    def get_ajax_elements(my):
        return ['new_sample_name', 'edit|search_type']

    def setup_ajax_inputs(my):
        web = WebContainer.get_web()
        ajax_inputs = my.get_ajax_inputs()
        for input in ajax_inputs:
            if not my.__dict__.get(input):
                my.__dict__[input] = web.get_form_value(input)
        ajax_elements = my.get_ajax_elements()
        for element in ajax_elements:
            name = element.replace("|", "_")
            if not my.__dict__.get(name):
                my.__dict__[name] = web.get_form_value(element)




    def setup_ajax(my, display_id):
        # set up ajax
        ajax = AjaxLoader()
        ajax.set_load_class(Common.get_full_class_name(my))
        ajax.set_display_id(display_id)
        ajax_inputs = my.get_ajax_inputs()
        for input in ajax_inputs:
            ajax.set_option(input, my.__dict__.get(input))

        ajax_elements = my.get_ajax_elements()
        for element in ajax_elements:
            ajax.add_element_name(element)
        return ajax.get_on_script()

    def init(my):
        my.setup_ajax_inputs()


    def get_display(my):

        web = WebContainer.get_web()
        naming_util = NamingUtil()

        if not my.widget_name:
            my.widget_name = my.get_name()

        

        # get the sobject required by this input
        sobject = my.get_current_sobject()
        if not sobject:
            sobject = Search.get_by_id(my.search_type, my.search_id)


        if my.new_sample_name:
            my.new_sample_name.replace("//", "/")
        else:
            my.new_sample_name = sobject.get_value(my.widget_name)


        widget = DivWdg()
        widget.set_id("naming")
        widget.add_style("display: block")



        # set the sample text
        div = DivWdg()
        div.add("Sample name: <i>%s</i>" % my.new_sample_name)
        div.add( HtmlElement.br(2) )

        new_sample_wdg = ProdIconButtonWdg("Set New Sample")
        new_sample_wdg.add_event("onclick", "toggle_display('generate')")
        div.add(new_sample_wdg)
   
        generate = DivWdg()
        generate.add(HtmlElement.br())
        generate.set_id("generate")
        generate.add_style("display: none")
        sample_text = TextWdg("new_sample_name")
        sample_text.set_option("size", "30")
        #sample_text.set_persist_on_submit()
        #if my.new_sample_name:
        #    sample_text.set_value(my.new_sample_name)
        generate.add(sample_text)


        button = IconButtonWdg("Generate", IconWdg.REFRESH, long=True)
        on_script = my.setup_ajax("naming")
        button.add_event("onclick", on_script)
        generate.add(button)
        generate.add( HtmlElement.br(2) )

        div.add(generate)
        widget.add(div)

        hidden = TextWdg(my.widget_name)
        value = my.naming
        hidden.set_value( my.new_sample_name )
        widget.add(my.widget_name)
        widget.add(hidden) 

        # get all of the parts

        # TODO: not sure if this should be dictated by the sample name
        # break up the name into parts
        import re
        if my.new_sample_name:
            tmp = my.new_sample_name.strip("/")
            parts = re.split( '[\\/._]', tmp)
            print "parts: ", parts
        else:
            return widget

        # if there is a naming, then populate that
        if my.edit_search_type:
            options = naming_util.get_options(my.edit_search_type)
        else:
            options = naming_util.get_options(sobject.get_value("search_type"))



        table = Table()
        type_values = []
        padding_values = []
        for idx, part in enumerate(parts):
            table.add_row()
            table.add_cell(part)

            type_select = SelectWdg("type_%s" % idx)
            type_select.add_empty_option("-- Explicit --")
            type_select.set_persist_on_submit()
            type_select.set_option("values", "|".join(options) )
            type_values.append(type_select.get_value())
            td = table.add_cell(type_select)

        widget.add(table)

        return widget


class XXNamingAction(DatabaseAction):
    def execute(my):
        sobject = my.sobject

        name = my.get_name()

        web = WebContainer.get_web()

        naming = web.get_form_value(name)

        if not naming:
            return

        xml = Xml(string=naming)
        sample_name = xml.get_value("naming/@sample")

        parts = re.split( '[\\/._]', sample_name)


        # make some adjustments based on selections
        nodes = xml.get_nodes("naming/part")
        for idx, node in enumerate(nodes):

            type_value = web.get_form_value("type_%s" % idx)
            part = parts[idx]

            if not type_value:
                continue

            if type_value == "placeholder":
                Xml.set_attribute(nodes[idx], "type", "placeholder")
                Xml.set_attribute(nodes[idx], "value", part)
            else:
                a, b = type_value.split("/")
                Xml.set_attribute(nodes[idx], "type", a)
                Xml.set_attribute(nodes[idx], "name", b)

        naming = xml.to_string() 


        sobject.set_value(name, naming)



class NamingAction(DatabaseAction):
    def execute(my):
        sobject = my.sobject

        name = my.get_name()

        web = WebContainer.get_web()

        naming = web.get_form_value(name)

        if not naming:
            return

        naming_util = NamingUtil()
        template = naming_util.build_naming2(naming)

        naming = naming.strip("/")
        parts = re.split( '[\\/._]', naming)

        # make some adjustments based on selections
        for idx, part in enumerate(parts):

            type_value = web.get_form_value("type_%s" % idx)

            if type_value:
                template = template.replace("{%d}" % idx, "{%s}" % type_value)
            else:
                template = template.replace("{%d}" % idx, part)


        sobject.set_value(name, template)





class NamingElementWdg(BaseTableElementWdg):

    def get_display(my):
        sobject = my.get_current_sobject()

        name = my.get_name()

        naming = sobject.get_value(name)
        if naming:
            try:
                xml = Xml(string=naming)
                sample_name = xml.get_value("naming/@sample")
            except Exception:
                sample_name = naming
        else:
            sample_name = '<i>-- none --</i>'


        return sample_name




class NamingInputWdg2(BaseInputWdg):
    def get_display(my):
        name = my.get_name()

        # get the sobject required by this input
        sobject = my.get_current_sobject()

        widget = DivWdg()

        # add an advanced widget
        text = TextWdg("%s" % name)
        text.set_attr("size", 90)
        value = sobject.get_value(name)
        text.set_value(value)
        div = DivWdg()
        #div.add("Advanced: ")
        div.add(text)
        widget.add(div)

        return widget


"""
@DEPRECATED
class NamingAction2(DatabaseAction):

    def execute(my):
        sobject = my.sobject

        name = my.get_input_name()

        web = WebContainer.get_web()

        naming = web.get_form_value(name)
        
        # we need to allow setting it back to empty
        #if not naming:
        #    return

        parts = re.split( '[\\/._]', naming)

        for idx, part in enumerate(parts):
            type_value = web.get_form_value("type_%s" % idx)
            naming = naming.replace("{%d}" % idx, type_value)

        print "naming: ", name, naming
        sobject.set_value(my.get_name(), naming)
"""





'''define a special language to extract a file path

some examples

1) take values directly from the sobject.  Anything in {} is a variable
{asset_library}/{code}/Maya
= chr/chr001/Maya

2) variables can be scoped based on 4 main objects:
    file, snapshot, sobject and parent
{parent.code}/{sobject.code}/{snapshot.context}
= vehicles/vehicle001/model

3) sometimes a value is composed of multiple parts and needs to be
broken up.  You can select the parts using [].  Note that
the parts will be split on non alpha_numeric characters
{sobject.code}/{snapshot.context[0]}/maya/{snapshot.context[1]}
= chr001/mode/maya/hi

4) without scoping, certain paramenters have special meaning
{code} = sobject.code
{short_code} = sobject.short_code
{context} = snapshot.context
{version} = snapshot.version ( "%0.3d" )
{revision} = snapshot.revision ( "%0.3d" )
{snapshot_type} = snapshot.snapshot_type
{project} = project.code
{search_type} = snapshot.search_type (without the project)
{parent_code} = parent.code
{ext} = file.ext

So a typical base dir name would be

/home/apache/assets/{project}/{search_type[1]}

A typical relpath would be

{parent.code}/{sobject.code}/{snapshot.context}
or
{parent_code}/{code}/{context}  (for short)

A typical file name would be
{code}_{context}_{version}.{ext}
'''






