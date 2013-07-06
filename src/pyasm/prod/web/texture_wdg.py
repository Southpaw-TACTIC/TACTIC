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

__all__ = ['TextureSourceElementWdg', 'TextureAddSourceWdg',
'TextureAddTexturesWdg', 'TextureAddSourceElementWdg', 'TextureAddSourceCmd',
'TextureAddSourceEditElement', 'TextureAddSourceAction' ]


from pyasm.common import Container, Xml, Environment, Common
from pyasm.biz import *
from pyasm.prod.biz import Texture, TextureSource
from pyasm.command import Command, DatabaseAction, FileUpload, CommandExitException
from pyasm.search import Search
from pyasm.web import *
from pyasm.widget import *
from pyasm.checkin import SnapshotBuilder, FileCheckin
from pyasm.prod.web import TextureFilterWdg


class TextureSourceElementWdg(BaseTableElementWdg):
    '''display the source information about textures.
        This class is shared by both Texture and Texture Source Tab'''

    def is_source(my, sobject):
        if isinstance(sobject, TextureSource):
            return True
        else:
            return False



    def get_display(my):

        sobject = my.get_current_sobject()

        if my.is_source(sobject):
            widget = my.get_add_textures_wdg()
            return widget

        # get the latest snapshot
        snapshot = Snapshot.get_latest_by_sobject(sobject)
        if not snapshot:
            return "No snapshots"

        xml = snapshot.get_xml_value("snapshot")
        nodes = xml.get_nodes("snapshot/ref")
        if not nodes:
            widget = Widget()
            icon = my.get_add_source_wdg()
            widget.add(icon)
            widget.add("No Source")
            return widget

        # assume 1 reference source, WHY? changed to list all for now
        #node = nodes[0]
        widget = Widget()
        for node in nodes:
            widget.add(my.get_source_link(node))
            widget.add(HtmlElement.br())
            
        
        return widget

    def get_source_link(my, node):
        search_type = Xml.get_attribute(node, "search_type")
        search_id = Xml.get_attribute(node, "search_id")
        context = Xml.get_attribute(node, "context")
        version = Xml.get_attribute(node, "version")

        source_snapshot = Snapshot.get_by_version(search_type, search_id, \
            context, version )
        if not source_snapshot:
            Environment.add_warning("Snapshot not found",  "Reference snapshot for [%s|%s] does not exist" \
              % (search_type, search_id) )
            return ''
            #raise WidgetException( "Reference snapshot in '%s' does not exist" \
            #   % snapshot.get_id() )

        source = source_snapshot.get_sobject()

        # get the file link
        file_name = source_snapshot.get_name_by_type("main")
        path = "%s/%s" % (source_snapshot.get_web_dir(), file_name)

        
        return HtmlElement.href("Source: %s" %source.get_value("code"), \
            ref=path ) 
        


    def get_add_textures_wdg(my):
        sobject = my.get_current_sobject()

        widget = Widget()

        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.prod.web.TextureAddTexturesWdg")
        url.set_option("search_type", search_type)
        url.set_option("search_id", search_id)
        url.set_option("refresh_mode", "page")

        ref = url.get_url()

        iframe = Container.get("iframe")
        iframe.set_width(80)
        action = iframe.get_on_script(ref)

        div = DivWdg()
        div.add_style("float: left")
        button = IconButtonWdg("Add Texture", IconWdg.IMAGE_ADD)
        button.add_event("onclick", action )
        button.add_style("margin: 3px 5px")
        div.add(button)
        div.add("Add Textures")
        widget.add(div)


        # find all of the forward references
        snapshot = Snapshot.get_latest_by_sobject(sobject)
        if snapshot:

            div = DivWdg()

            xml = snapshot.get_xml_value("snapshot")

            frefs = xml.get_nodes("snapshot/fref")
            if frefs:
                widget.add("<br clear='all'/><hr size='1px'/>")

            for fref in frefs:
                search_id = Xml.get_attribute(fref, "search_id")
                search_type = Xml.get_attribute(fref, "search_type")

                sobject = Search.get_by_id(search_type, search_id)
                if not sobject:
                    sobject_code = "n/a"
                else:
                    sobject_code = sobject.get_code()
                thumb = ThumbWdg()
                thumb.set_icon_size(30)
                thumb.set_show_latest_icon(True)
                thumb.set_sobject(sobject)
                div.add(thumb)
                div.add(sobject_code)
                div.add("<br/>")

            widget.add(div)




        return widget



    def get_add_source_wdg(my):

        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.prod.web.TextureAddSourceWdg")
        url.set_option("search_type", search_type)
        url.set_option("search_id", search_id)
        url.set_option("refresh_mode", 'page')
        ref = url.get_url()

        iframe = WebContainer.get_iframe()
        iframe.set_width(60)
        action = iframe.get_on_script(ref)

        button = IconButtonWdg("Warning", IconWdg.ERROR)
        button.add_event("onclick", action )
        button.add_style("margin: 3px 5px")

        return button






class TextureAddSourceWdg(Widget):
    '''The entire widget for adding a source to the texture'''

    def init(my):
        search = Search("prod/texture")
        search.add_filter("category", "source")
        table = TableWdg("prod/texture", "source")
        table.set_search(search)
        my.add(table)



class TextureAddTexturesWdg(Widget):
    '''The entire widget for adding a source to the texture'''

    def is_error_free(my, web):
        ''' if it is instructed to close and is error-free , return True'''
        if web.get_form_value('add'):
            return True

        return False

    def get_sobject(my):

        web = WebContainer.get_web()

        # first try the search key
        search_key = web.get_form_value("search_key")
        if search_key != "":
            sobject = Search.get_by_search_key(search_key)
            return object

        # next try te search_type/search_id pair
        search_type = web.get_form_value("search_type")
        if search_type != "":
            search_id = web.get_form_value("search_id")
            sobject = Search.get_by_id(search_type, search_id)
            return sobject

        return None


    def init(my):
        web = WebContainer.get_web()
        if my.is_error_free(web):
            event_container = WebContainer.get_event_container()
            refresh_script = "window.parent.%s" % event_container.get_refresh_caller()

            iframe = WebContainer.get_iframe()
            off_script = "window.parent.%s" % iframe.get_off_script()

            script = HtmlElement.script('''
            %s
            %s
            ''' % (off_script, refresh_script) )
            my.add(script)
            return

        widget = Widget()

        sobject = my.get_sobject()
        search_type = sobject.get_search_type()
        table = TableWdg(search_type, "source")
        table.remove_widget("select")
        table.set_sobject(sobject)
        table.set_show_property(False)
        widget.add(table)

        widget.add(HtmlElement.h3("Latest Textures"))

        search = Search("prod/texture")
        search.add_order_by("timestamp desc")

        texture_filter = TextureFilterWdg()
        texture_filter.alter_search(search)
        div = DivWdg(texture_filter, css='filter_box')
        table = TableWdg("prod/texture", "texture")
        table.set_search(search)
        widget.add(div)
        widget.add(table)
        my.add(widget)




class TextureAddSourceElementWdg(BaseTableElementWdg):
    '''The table element that adds a specific source'''

    def get_title(my):
        WebContainer.register_cmd("pyasm.prod.web.TextureAddSourceCmd")
        add_button = SubmitWdg(my.name)
        return add_button

    def get_display(my):

        sobject = my.get_current_sobject()
        search_key = sobject.get_search_key()

        checkbox = CheckboxWdg("selected")
        checkbox.set_option("value", search_key)
        return checkbox





class TextureAddSourceCmd(Command):

    def check(my):
        return True
    
    def execute(my):

        web = WebContainer.get_web()

        if web.get_form_value("add") == "":
            raise CommandExitException()

        # get the source
        search_type = web.get_form_value("search_type")
        search_id = web.get_form_value("search_id")
        parent = Search.get_by_id(search_type,search_id)
        parent_snapshot = Snapshot.get_latest_by_sobject(parent)

        parent_xml = parent_snapshot.get_xml_value("snapshot")
        parent_builder = SnapshotBuilder(parent_xml)

        
        # get the selected textures
        selected = web.get_form_values("selected")
        my.add_description("Adding source to texture for [%s]" %','.join(selected))
        for select in selected:
            sobject = Search.get_by_search_key(select)

            # add a backward reference
            sobject_snapshot = Snapshot.get_latest_by_sobject(sobject)
            xml = sobject_snapshot.get_xml_value("snapshot")
            builder = SnapshotBuilder(xml)
            builder.add_ref_by_snapshot(parent_snapshot)
            sobject_snapshot.set_value("snapshot", builder.to_string() )
            sobject_snapshot.commit()


            # add a forward reference
            parent_builder.add_fref_by_snapshot(sobject_snapshot)

        parent_snapshot.set_value("snapshot", parent_builder.to_string() )
        parent_snapshot.commit()





# Edit element which appears on insert of a new texture


class TextureAddSourceEditElement(BaseInputWdg):
    '''This widget is used to add a source to a texture at upload time'''
    
    def get_display(my):

        widget = Widget()

        # get all of the sources, add reverse timestamp order
        search = Search("prod/texture_source")
        search.add_order_by("timestamp")
        search.set_limit(10)
        sources = search.get_sobjects()

        if sources:
            widget.add(HtmlElement.b("Predefined Sources:"))
            widget.add(HtmlElement.br())
            for source in sources:
                search_key = source.get_search_key()
                checkbox = CheckboxWdg("predefined_source")
                checkbox.set_option("value",search_key)
                widget.add(checkbox)
                widget.add(source.get_value("code"))
                widget.add(SpanWdg("&gt;&gt;", css='med'))
                widget.add(source.get_value("description"))
                widget.add("<br/>")



        # or add a new one
        widget.add(HtmlElement.b("New Source:"))
        upload_wdg = SimpleUploadWdg("add_source")
        widget.add(upload_wdg)

        return widget





class TextureAddSourceAction(DatabaseAction):

    def execute(my):
        pass

    def postprocess(my):
        sobject = my.sobject
        texture_snapshot = Snapshot.get_latest_by_sobject(sobject)
        web = WebContainer.get_web()

        source_search_key = web.get_form_value("predefined_source")
        if source_search_key and texture_snapshot:
            source = Search.get_by_search_key(source_search_key)
            source_snapshot = Snapshot.get_latest_by_sobject(source)
            
            xml = texture_snapshot.get_xml_value("snapshot")
            builder = SnapshotBuilder(xml)
            builder.add_ref_by_snapshot(source_snapshot)
            texture_snapshot.set_value("snapshot", builder.to_string() )
            texture_snapshot.commit()

            return




        # if no files have been uploaded, don't do anything
        field_storage = web.get_form_value("add_source")
        if field_storage == "":
            return

        # process and get the uploaded files
        upload = FileUpload()
        upload.set_field_storage(field_storage)
        upload.execute()
        files = upload.get_files()
        if not files:
            return

        file_types = upload.get_file_types()
        
        asset_code = sobject.get_value("asset_code")

        # checkin this as a new source
        import os
        source_code = os.path.basename(files[0])
        source_description = "Referred to %s" % my.sobject.get_code()
        source_category = "default"
        source = TextureSource.create(asset_code, source_code, \
            source_category, source_description)

        # add the file as a snapshot to this source
        checkin = FileCheckin(source, files, file_types )
        checkin.execute()

        source_snapshot = Snapshot.get_latest_by_sobject(source)
        xml = source_snapshot.get_xml_value("snapshot")
        builder = SnapshotBuilder(xml)
        builder.add_fref_by_snapshot(texture_snapshot)
        source_snapshot.set_value("snapshot", builder.to_string() )
        source_snapshot.commit()


        # Modify the snapshot in the original texture to reference this
        # source.  This assumes that the other uploaded snapshot has
        # already been dealt with.
        source_snapshot = checkin.get_snapshot()

        # FIXME: what if no texture was uploaded???
        xml = texture_snapshot.get_xml_value("snapshot")
        builder = SnapshotBuilder(xml)
        builder.add_ref_by_snapshot(source_snapshot)
        texture_snapshot.set_value("snapshot", builder.to_string() )
        texture_snapshot.commit()





