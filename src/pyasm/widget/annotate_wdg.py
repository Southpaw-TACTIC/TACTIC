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

__all__ = ['AnnotateLink', 'AnnotatePage', 'AnnotateWdg', 'AnnotateCbk']

from pyasm.web import *
from pyasm.command import Command
from pyasm.search import Search, SObject
from pyasm.biz import Snapshot, File
from pyasm.widget import BaseTableElementWdg, IconButtonWdg

from input_wdg import *
from dynamic_loader_page import *
from layout_wdg import TableWdg
from icon_wdg import *



class AnnotateLink(BaseTableElementWdg):

    def get_annotate_wdg_class(self):
        return "AnnotateWdg"

    def get_display(self):
        sobject = self.get_current_sobject()

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", self.get_annotate_wdg_class() )
        url.set_option("search_type", sobject.get_search_type() )
        url.set_option("search_id", sobject.get_id() )

        button = IconButtonWdg("Annotate", IconWdg.DETAILS, False)
        button.add_event("onclick", \
            "document.location='%s'" % url.to_string() )

        widget = Widget()
        widget.add(button)

        return widget




class AnnotatePage(Widget):

    def init(self):

        WebContainer.register_cmd("pyasm.widget.AnnotateCbk")

        sobject = self.get_current_sobject()

        if not sobject:
            if not self.__dict__.has_key("search_type"):
                web = WebContainer.get_web()
                self.search_type = web.get_form_value("search_type")
                self.search_id = web.get_form_value("search_id")

            if not self.search_type:
                self.add("No search type")
                return

            search = Search(self.search_type)
            search.add_id_filter(self.search_id)
            sobject = search.get_sobject()

        self.add("<h3>Design Review: Annotation</h3>")
        table = TableWdg(self.search_type)
        table.set_sobject(sobject)
        self.add(table)

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "AnnotateWdg")
        url.set_option("search_type", self.search_type)
        url.set_option("search_id", self.search_id)
        src = url.to_string()

        self.add("<h3>Click on image to add an annotation</h3>")
        self.add("The annotation will be located where you clicked on the image")
        
        self.add( """
        <iframe id="annotate_frame" scrolling="no" src="%s" style='width: 800; height: 450; margin-left: 30px; border: none;">
        WARNING: iframes are not supported
        </iframe>
        """ % src )




class AnnotateWdg(Widget):


    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_search_id(self, search_id):
        self.search_id = search_id


    def init(self):

        WebContainer.register_cmd("pyasm.widget.AnnotateCbk")

        sobject = self.get_current_sobject()

        if not sobject:
            if not self.__dict__.has_key("search_type"):
                web = WebContainer.get_web()
                self.search_type = web.get_form_value("search_type")
                self.search_id = web.get_form_value("search_id")

            if not self.search_type:
                self.add("No search type")
                return


            search = Search(self.search_type)
            search.add_id_filter(self.search_id)
            sobject = search.get_sobject()


        snapshot = Snapshot.get_latest_by_sobject(sobject)

        # TODO:
        # this is a bit klunky
        snapshot_xml = snapshot.get_xml_value("snapshot")
        file_code = snapshot_xml.get_value("snapshot/file[@type='web']/@file_code")
        file = File.get_by_code(file_code)
        web_dir = snapshot.get_web_dir()
        path = "%s/%s" % (web_dir, file.get_full_file_name() )


        # add the annotate js object
        script = HtmlElement.script("annotate = new Annotate()")
        self.add(script)


        # add the image

        self.add("<h3>Image Annotations</h3>")

        width = 600
        img = HtmlElement.img(path)
        img.add_style("position: absolute")
        img.set_id("annotate_image")
        img.add_style("left: 0px")
        img.add_style("top: 0px")
        img.add_style("opacity: 1.0")
        img.add_style("z-index: 1")
        img.add_style("width", width)
        img.add_event("onmouseup", "annotate.add_new(event)")
        self.add(img)



        # test 
        version = snapshot.get_value("version")
        if version != 1:
            last_version = version - 1
            snapshot = Snapshot.get_by_version( \
                self.search_type, self.search_id, version=last_version )

            snapshot_xml = snapshot.get_xml_value("snapshot")
            file_code = snapshot_xml.get_value("snapshot/file[@type='web']/@file_code")
            file = File.get_by_code(file_code)
            web_dir = snapshot.get_web_dir()
            path = "%s/%s" % (web_dir, file.get_full_file_name() )

            img = HtmlElement.img(path)
            img.set_id("annotate_image_alt")
            img.add_style("position: absolute")
            img.add_style("left: 0px")
            img.add_style("top: 0px")
            img.add_style("opacity: 1.0")
            img.add_style("z-index: 0")
            img.add_style("width", width)
            img.add_event("onmouseup", "annotate.add_new(event)")
            self.add(img)


            #script = HtmlElement.script("align_element('%s','%s')" % \
            #    ("annotate_image", "annotate_image_alt") )
            #self.add(script)

            div = DivWdg()
            div.add_style("position: absolute")
            div.add_style("left: 620")
            div.add_style("top: 300")
            self.add(div)

            button = IconButtonWdg("Switch", IconWdg.REFRESH, True)
            button.add_event("onclick", "annotate.switch_alt()")
            div.add(button)

            button = IconButtonWdg("Opacity", IconWdg.LOAD, True)
            button.add_event("onclick", "annotate.set_opacity()")
            div.add(button)







        # add the new annotation div
        new_annotation_div = DivWdg()
        new_annotation_div.set_id("annotate_msg")
        new_annotation_div.set_class("annotate_new")
        new_annotation_div.add_style("top: 0")
        new_annotation_div.add_style("left: 0")

        title = DivWdg("Enter Annotation:")
        title.add_style("background-color: #000000")
        title.add_style("color: #ffffff")
        new_annotation_div.add(title)

        text = TextAreaWdg("annotate_msg")
        text.set_attr("cols", "30")
        text.set_attr("rows", "3")
        new_annotation_div.add(text)
        new_annotation_div.add("<br/>")
        cancel = ButtonWdg("Cancel")
        cancel.add_style("float: right")
        cancel.add_event("onclick", "toggle_display('annotate_msg')")
        new_annotation_div.add( cancel )
        submit = SubmitWdg("Add Annotation")
        submit.add_style("float: right")

        new_annotation_div.add( submit )

        new_annotation_div.add_style("display: none")
        new_annotation_div.add_style("position: absolute")
        self.add(new_annotation_div)

        # get all of the stored annotations for this image
        search = Search("sthpw/annotation")
        search.add_order_by("login")
        search.add_filter("file_code", file_code)
        annotations = search.get_sobjects()


        # sort by user
        sorted_annotations = {}
        for annotation in annotations:
            user = annotation.get_value("login")

            if not sorted_annotations.has_key(user):
                sorted_annotations[user] = []

            sorted_annotations[user].append(annotation)


        buttons = []
        for user, annotations in sorted_annotations.items():

            button = IconButtonWdg(user, IconWdg.INSERT, True)
            button.add_event("onclick", "annotate.show_marks('%s','%s')" % (user, len(annotations)-1) )
            buttons.append(button)

            count = 0
            for annotation in annotations:
                self.add( self.get_annotate_wdg(annotation,count) )
                count += 1



        # add the user buttons
        table = Table()
        table.set_class("table")
        table.add_style("width: 0px")
        table.add_style("position: absolute")
        table.add_style("left: 620")
        table.add_style("top: 0")
        table.add_row()

        table.add_header("Annotations")
        for button in buttons:
            table.add_row()
            legend_wdg = DivWdg()
            legend_wdg.set_class("annotate_mark")
            legend_wdg.add_style("position: relative")
            legend_wdg.add("&nbsp;")

            table.add_cell(legend_wdg)

            table.add_cell(button)

        self.add(table)


        # add form elements
        hidden = HiddenWdg("mouse_xpos")
        self.add(hidden)
        hidden = HiddenWdg("mouse_ypos")
        self.add(hidden)
        hidden = HiddenWdg("file_code", file_code)
        self.add(hidden)

        # move the rest below
        self.add("<div style='height:300'>&nbsp</div>")



    def get_annotate_wdg(self, annotation, count):

        # get information from annotation
        x_pos = annotation.get_value("xpos")
        y_pos = annotation.get_value("ypos")
        user = annotation.get_value("login")
        message = annotation.get_value("message")

        widget = DivWdg()
        widget.add_style("display: none")
        widget.set_id( "annotate_div_%s_%s" % (user,count) )

        # add the box
        annotate_wdg = DivWdg()
        annotate_wdg.set_class("annotate_mark")
        annotate_wdg.set_id( "annotate_mark_%s_%s" % (user,count) )
        annotate_wdg.add_style("display", "block")
        annotate_wdg.add_style("left: %s" % x_pos )
        annotate_wdg.add_style("top: %s" % y_pos )

        # message 
        back_wdg = DivWdg()
        back_wdg.set_class("annotate_back")
        back_wdg.set_id("annotate_back_%s_%s" % (user,count) )
        back_wdg.add_style("display", "block")
        back_wdg.add_style("left: %s" % str(int(x_pos)+10) )
        back_wdg.add_style("top: %s" % y_pos )
        back_wdg.add(message)
 

        msg_wdg = DivWdg()
        msg_wdg.set_class("annotate_msg")
        msg_wdg.set_id("annotate_msg_%s_%s" % (user,count) )
        msg_wdg.add_style("display", "block")
        msg_wdg.add_style("left: %s" % str(int(x_pos)+10) )
        msg_wdg.add_style("top: %s" % y_pos )
        msg_wdg.add(message)

        widget.add(back_wdg)
        widget.add(annotate_wdg)
        widget.add(msg_wdg)


        return widget




class AnnotateCbk(Command):

    def get_title(self):
        return "Annotate Image"

    def execute(self):
        web = WebContainer.get_web()
        if web.get_form_value("Add Annotation") == "":
            return

        annotate_msg = web.get_form_value("annotate_msg")
        if annotate_msg == "":
            return


        xpos = web.get_form_value("mouse_xpos")
        ypos = web.get_form_value("mouse_ypos")
        file_code = web.get_form_value("file_code")

        user = web.get_user_name()

        annotate = SObject("sthpw/annotation")
        annotate.set_value("message", annotate_msg)
        annotate.set_value("xpos", xpos)
        annotate.set_value("ypos", ypos)
        annotate.set_value("login", user)
        annotate.set_value("file_code", file_code)
        annotate.commit()

        self.description = "Added annotation '%s'" % annotate_msg








