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
__all__ = ['SObjectActionException','SObjectActionWdg','SObjectFilePublishWdg','SObjectUploadWdg',
'SObjectUploadCmd','SObjectDownloadWdg','SingleFilePerSObjectUploadCmd']

from pyasm.common import Container, Config, Marshaller, Environment
from pyasm.command import *
from pyasm.checkin import FileCheckin
from pyasm.search import SearchType, Search
from pyasm.biz import *
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import *
import os, re, shutil


'''Classes to support the uploading and downloading of sobjects'''


class SObjectActionException(Exception):
    pass


class SObjectActionWdg(SpanWdg):

    def __init__(self, search=None, child=None, css=None):
        super(SObjectActionWdg,self).__init__(child, css)
        self.search = search
        self.upload_options = {}

    def get_download_types(self):
        return ["fla", "png", "jpg"]


    def set_upload_option(self, name, value):
        self.upload_options[name] = value



    def get_display(self):
        
        assert self.search is not None
        
        search_type_obj = self.search.get_search_type_obj()
        search_type = search_type_obj.get_full_key()

        title = search_type_obj.get_title()

        upload_url = WebContainer.get_web().get_widget_url()
        upload_url.set_option("widget", "pyasm.prod.web.SObjectUploadWdg")
        upload_url.set_option("search_type", search_type)
        for name, value in self.upload_options.items():
            upload_url.set_option(name,value)

        search_ids = [ x.get_id() for x in self.sobjects ]
        download_url = WebContainer.get_web().get_widget_url()
        download_url.set_option("widget", "pyasm.prod.web.SObjectDownloadWdg")
        download_url.set_option("search_type", search_type)
        download_url.set_option("search_ids", search_ids)
        download_url.set_option("download_types", self.get_download_types())

        # get the main iframe
        iframe = Container.get("iframe")
        iframe.set_width(65)
        upload_action = iframe.get_on_script(upload_url.get_url())
        download_action = iframe.get_on_script(download_url.get_url())


        # upload button
        upload_button = IconButtonWdg("Publish %s" % title, IconWdg.UPLOAD, True)
        upload_button.add_event("onclick", upload_action )

        # download button
        download_button = IconButtonWdg("Download %s" % title, IconWdg.DOWNLOAD, True)
        download_button.add_event("onclick", download_action)
        
        self.add(download_button, "download_button")
        self.add(upload_button, "upload_button")
        self.add_style("height", "2.0em")
        
        return super(SObjectActionWdg,self).get_display()
        
class SObjectFilePublishWdg(SpanWdg):

    def __init__(self, sobject=None, child=None, css=None):
        super(SObjectFilePublishWdg,self).__init__(child, css)
        self.sobject = sobject
        self.upload_options = {}

   

    def set_upload_option(self, name, value):
        self.upload_options[name] = value



    def get_display(self):
        
        #assert self.search is not None
        
        #search_type_obj = self.search.get_search_type_obj()
        search_key = self.sobject.get_search_key()

        title = self.sobject.get_code()

        upload_url = WebContainer.get_web().get_widget_url()
        upload_url.set_option("widget", "pyasm.prod.web.SObjectUploadWdg")
        upload_url.set_option("search_key", search_key)
        #upload_url.set_option("mode", "copy")
        upload_url.set_option("naming", "no")
        for name, value in self.upload_options.items():
            upload_url.set_option(name,value)

       
        # get the main iframe
        iframe = Container.get("iframe")
        iframe.set_width(65)
        upload_action = iframe.get_on_script(upload_url.get_url())

        # upload button
        upload_button = IconButtonWdg("file publish %s" % title, IconWdg.UPLOAD)
        upload_button.add_event("onclick", upload_action )
    
        self.add(upload_button, "upload_button")
        
        return super(SObjectFilePublishWdg,self).get_display()    

class SObjectUploadWdg(HtmlElement):
    
    COPY_MODE = "copy"
    COPY = "File Copy"
    UPLOAD = "File Upload"
    
    PUBLISH_BUTTON ="Publish"
    
    def __init__(self,name=None):
        super(SObjectUploadWdg,self).__init__("div")

        self.set_class("admin_main")

    def set_cmd_class(self, command_class):
        '''sets the command to be executed for this widget'''
        self.command_class = command_class

    def get_action_label(self, mode):
        if mode == self.COPY_MODE:
            return self.COPY
        else:
            return self.UPLOAD

    def init(self):

        self.command_class = ""
        title = None
        web = WebContainer.get_web()
        search_type = web.get_form_value("search_type")
        search_key = web.get_form_value("search_key")
        mode = web.get_form_value("mode")
        action_label = self.get_action_label(mode)

        if search_type: 
            search_type_obj = SearchType.get(search_type)
            search_type = search_type_obj.get_full_key()
            title = search_type_obj.get_title()
        elif search_key:
            title = Search.get_by_search_key(search_key).get_code()
            
        if web.get_form_value("is_form_submitted") == "yes" and \
                web.get_form_value(SObjectUploadCmd.FILE_NAMES):
            self.add( HtmlElement.script("parent.document.form.submit()") )
    
        header = HtmlElement.div("%s %s" % (title, action_label))
        header.set_class("admin_header")
        self.add(header)


        # add a transfer mode select
        span = SpanWdg("Transfer mode:", css='small')
        select = SelectWdg("mode")
        select.set_submit_onchange()

        # upload is the default with an empty value
        select.set_option("values", "copy|")
        select.set_option("labels", "copy|upload")
        select.get_value()
         
        self.add(span)
        self.add(select)
        
        # add the multi-upload widget
        upload = MultiUploadWdg()
        self.add(upload)

        # add a hidden search type element
        hidden = HiddenWdg("search_type", search_type)
        self.add(hidden)

        # add the description widget
        textarea = TextAreaWdg(SObjectUploadCmd.PUBLISH_COMMENT)
        textarea.set_attr("cols", "40")
        textarea.set_attr("rows", "2")

        desc_div = HtmlElement.div()
        desc_div.add_style("border-style: solid")
        desc_div.add_style("border-width: 1px")
        desc_div.add_style("padding: 8px")
        desc_div.add_style("background-color: white")
        desc_div.add_style("border-color: #8cacbb")
        desc_div.add("<b>Description</b>:")
        desc_div.add("<br/>")
        desc_div.add(textarea)
        self.add(desc_div)


        ticket = web.get_cookie("login_ticket")
        if mode == self.COPY_MODE:
            copy_url = "%s/%s" %(WebContainer.get_web().get_copy_base_url(), \
                ticket)
            self.add(HtmlElement.script("document.form.%s.set_server_url('%s')" \
                %(MultiUploadWdg.UPLOAD_ID, copy_url)))
        else:
            upload_url = WebContainer.get_web().get_upload_url()
            self.add(HtmlElement.script("document.form.%s.set_server_url('%s'); \
                document.form.%s.set_ticket('%s');" \
                %(MultiUploadWdg.UPLOAD_ID, upload_url, MultiUploadWdg.UPLOAD_ID, ticket)))
                
        # add the submit button
        submit = SubmitWdg(self.PUBLISH_BUTTON)
        event_caller = WebContainer.get_event("sthpw:submit").get_caller()
        submit.add_event("onclick", event_caller )
        self.add(submit)


    def get_display(self):

        web = WebContainer.get_web()
        
        if web.get_form_value("naming") == "no":
            self.command_class = "pyasm.prod.web.SingleFilePerSObjectUploadCmd"
        else:
            self.command_class = "pyasm.prod.web.SObjectUploadCmd"

        # add action delegator for this widget
        cmd_delegator = WebContainer.get_cmd_delegator()
        marshaller = Marshaller(self.command_class)

        if web.get_form_value("column") != "":
            marshaller.set_option("column", web.get_form_value("column") )

        cmd_delegator.register_cmd( marshaller )

        return super(SObjectUploadWdg,self).get_display()





class SObjectUploadCmd(Command):
    '''Uploads sets of files with strict naming conventions.  The file
    name completely determines which asset to put the upload file into'''

    FILE_NAMES = "upload_files"
    PUBLISH_COMMENT ="upload_description"

    def __init__(self, column="snapshot"):
        super(SObjectUploadCmd,self).__init__()
        self.column = column
        self.web = WebContainer.get_web()
        self.file_paths = []
        self.sobject = None
        self.repo_file_list = []

    def get_title(self):
        return "SObject Upload"


    def check(self):
        self.upload_values = self.web.get_form_value(self.FILE_NAMES).split("|")
        if self.upload_values and self.upload_values[0]:
            return True
        else:
            return False

    def set_column(self, column):
        self.column = column



    def execute(self):
        self.sobject_dict = {}
        self.sobjects = []
        # parse the form values categorize them
        self._parse_form()

        # Go through each sobject and check in the files
        # Each sobject is a self contained entity
        for sobject_key, filenames in self.sobject_dict.items():
            try:
                self.sobject = Search.get_by_search_key(sobject_key)
                self.sobjects.append(self.sobject)
                self._handle_sobject(self.sobject, filenames)

            except SObjectActionException, e:
                self.errors.append(e)
           
        self.set_response('\n'.join(self.repo_file_list)) 

    def _parse_form(self):
        
        # get the downloaded files and sort them
      
        search_type = self.web.get_form_value("search_type")
        self.search_type_obj = SearchType.get(search_type)

        # Need a more scalable way to designate naming classes
        base_search_key = self.search_type_obj.get_base_key()
        if base_search_key == "prod/texture":
            self.naming = TextureCodeNaming()
        elif base_search_key == "flash/asset":
            self.naming = FlashAssetNaming()
        elif base_search_key == "flash/shot":
            self.naming = FlashShotNaming()
        elif base_search_key == "flash/layer":
            self.naming = FlashLayerNaming()  
        elif base_search_key == "sthpw/template":
            self.naming = TemplateCodeNaming()
        else:
            raise CommandException("No naming defined for '%s'" % \
                base_search_key )

        self.upload_values.sort()

        #sobjects = []

        # go through each uploaded file and categorize to the sobject
        for upload_value in self.upload_values:

            # convert the slashes
            filename = upload_value.replace("\\", "/")
            filename = os.path.basename(filename)

            sobject = self.naming.get_sobject_by_filename(filename)
            if sobject == None:
                print "WARNING(upload): sobject is none: ", upload_value
                continue

            sobject_key = sobject.get_search_key()

            # add all of the files to the sobject code
            if not self.sobject_dict.has_key(sobject_key):
                self.sobject_dict[sobject_key] = []
            self.sobject_dict[sobject_key].append(filename)

    def _is_flash(self, search_type_obj):
        return search_type_obj.get_value('namespace') == 'flash'

    def _handle_sobject(self, sobject, filenames):

        # check that all of the files are there
        #self.naming.check_files(filenames)

        # checkin in the file
        file_types = []
        self.file_paths = []
        # HACK fix this so it is more distributed
        '''
        if isinstance(self.naming, FlashNaming):
            flash = True
        elif isinstance(self.naming, FlashLayerNaming):
            flash = True
        else:
            flash = False
        '''

        search_type_obj = sobject.get_search_type_obj()
        if self._is_flash(search_type_obj):
            flash = True
        elif search_type_obj.get_value('search_type') == 'sthpw/template':
            flash = self._is_flash(SearchType.get(sobject.get_value('search_type')))
        else:
            flash = False

        basedir = WebContainer.get_web().get_upload_dir()
        for filename in filenames:

            file_path = "%s/%s" % (basedir, filename)
            self.file_paths.append(file_path)
            # for now, use the extension as the type
            basename, ext = os.path.splitext(filename)
            if flash == True:
                file_types.append(ext)

                # should create an icon here
                if ext == ".png":
                    creator = IconCreator(file_path)
                    creator.create_icons()

                    icon_path = creator.get_icon_path()
                    self.file_paths.append(icon_path)
                    file_types.append("icon")

                    # remove the web file
                    try:
                        os.unlink(creator.get_web_path())
                    except OSError, e:    
                        print e

            else:
                file_types.append("main")


                # create icons and add to the list
                if ext == ".png" or ext == ".jpg":
                    creator = IconCreator(file_path)
                    creator.create_icons()

                    icon_path = creator.get_icon_path()
                    self.file_paths.append(icon_path)
                    file_types.append("icon")

                    web_path = creator.get_web_path()
                    self.file_paths.append(web_path)
                    file_types.append("web")


        # checkin all of the files into the sobjects
        if self._is_flash(search_type_obj):
            snapshot_type = "flash"
        else:
            snapshot_type = "file"

        checkin = FileCheckin( sobject, self.file_paths, file_types,
            column=self.column, snapshot_type=snapshot_type )
        # handle the description
        web = WebContainer.get_web()

        comment = web.get_form_value(self.PUBLISH_COMMENT)
        self.add_description('[%s] %s ' %(sobject.get_code(), comment))
        checkin.set_description(comment)
        
        
        checkin.execute()
        checkin_info = []
        for key, value in checkin.file_dict.items():
            if not self.get_response_list(): 
                checkin_info.append("'%s=%s'" %(key, value))
            else:
                for type in self.get_response_list():
                    if type in key:
                        checkin_info.append("'%s=%s'" %(key, value))
                        break
                    
        self.repo_file_list.append(','.join(checkin_info))
        

    def get_response_list(self):
        ''' define a list of file extensions that we want to display in 
            commmand's response. By default, it will allow any files'''
        return []
    
    def postprocess(self):
        '''remove the source files after checkin'''
        for path in self.file_paths:
            if os.path.exists(path):
                os.unlink(path)



class SObjectDownloadWdg(HtmlElement):
    def __init__(self,name=None):
        super(SObjectDownloadWdg,self).__init__("div")

    def init(self):

        web = WebContainer.get_web()
        search_type = web.get_form_value("search_type")
        search_ids = web.get_form_values("search_ids")

        download_types = web.get_form_values("download_types")
        
        search = Search(search_type)
        sobjects = []
        
        if search_ids:
            search.add_where("id in (%s)" % ", ".join(search_ids) )
            sobjects = search.do_search()
        
        
       
        if not sobjects:
            message = HtmlElement.p("No %s to download." % search.get_search_type_obj().get_title())
            message.set_class('warning')
            self.add(message) 
            return 
        
        download_wdg = DownloadWdg()
        self.add(download_wdg)
        
        
        outer_div = DivWdg(css="admin_main")
        table = Table()
        table.set_class("table")

        # add download buttons
        
        widget = HtmlElement.div()
        #button = SubmitWdg("Download All")
        #widget.add(button)
        button = SubmitWdg("Download Selected")
        widget.add(button)
        tr, th = table.add_row_header(widget)
        th.add_style("text-align: center")

        # add all of the
        #widget = HtmlElement.div()
        #widget.add("<b>Download options:</b>")
        #for type in download_types:
        #    widget.add( CheckboxWdg(type) )
        #    widget.add( type)
        #tr, th = table.add_row_header(widget)
        #th.add_style("text-align: center")

        # add all of the sobjects
        col = 0
        for sobject in sobjects:

            if col == 0 or col % 3 == 0:
                table.add_row()

            search_id = sobject.get_id()

            icon_wdg = ThumbWdg()
            icon_wdg.set_name("snapshot")
            icon_wdg.set_sobject(sobject)

            div = HtmlElement.div()
            div.set_style("background-color: #f0f0f0")
            div.set_style("height: 100%")

            checkbox = CheckboxWdg("download_files")
            checkbox.set_option("value", "%s|%s" % (search_type, search_id) )
            div.add( checkbox )
            if sobject.has_value("code"):
                div.add( "<b>%s</b>" % sobject.get_value("code") )
            div.add( "<br/>")


            div.add( icon_wdg )

            if sobject.has_value("code"):
                div.add( sobject.get_value("description") )

            td = table.add_cell(div)
            td.add_style("height: 120px")
            td.add_style("widget: 200px")

            col += 1

        outer_div.add(table)

        self.add(outer_div)






class SingleFilePerSObjectUploadCmd(Command):
    '''Uploads sets of files with no naming conventions.  This command
    assumes each asset contains a single main file.  This is useful
    for documents.  Icons and web versions will be autocreated if possible
    New sobject will be created if search_type is provided. Existing sobject
    will be used if search_key is provided.
    '''
    FILE_NAMES = "upload_files"
    def __init__(self, column="snapshot"):
        self.column = column
        self.file_paths = []
        self.upload_files = []
        
        super(SingleFilePerSObjectUploadCmd,self).__init__()


    def get_title(self):
        return "Single File Per SObject Upload"


    def check(self):
        web = WebContainer.get_web()

        self.upload_values = web.get_form_value(self.FILE_NAMES).split("|")
        if not (self.upload_values and  self.upload_values[0]):
            return False
            
        self.search_type = web.get_form_value("search_type")
        self.search_key = web.get_form_value("search_key")
        if not self.search_type:
             assert self.search_key 
        if self.search_type and self.search_key:
            print "Either search_type or search_key is needed!"
            return False
        return True


    def set_column(self, column):
        self.column = column


    def execute(self):

        # parse the form values categorize them
        self._parse_form()

        return 


    def _parse_form(self):
 
        # get the downloaded files and sort them
        web = WebContainer.get_web()
        
        self.upload_values.sort()

        filenames = []
        ticket = web.get_cookie("login_ticket")
        # create a new entry for every file
        for upload_value in self.upload_values:
            tmp_dir = Environment.get_tmp_dir()
            basename = os.path.basename(upload_value)
            file_path = "%s/upload/%s/%s" % (tmp_dir, ticket, basename)

            filenames.append(basename)

            creator = IconCreator(file_path)
            creator.create_icons()

            self.file_paths = [file_path]
            file_types = ["main"]

            web_path = creator.get_web_path()
            if web_path != None:
                self.file_paths.append(web_path)
                file_types.append("web")

            icon_path = creator.get_icon_path()
            if icon_path != None:
                self.file_paths.append(icon_path)
                file_types.append("icon")

            sobject = None
            if self.search_key:
                sobject = Search.get_by_search_key(self.search_key)
            else:    
                sobject = SObjectFactory.create(self.search_type)
                sobject.commit()

            checkin = FileCheckin( sobject, self.file_paths, file_types,\
                column=self.column )
             
            checkin.set_description(web.get_form_value(SObjectUploadCmd.PUBLISH_COMMENT))
            checkin.execute()
            self.repo_file_list.append(checkin.file_dict)
            

        
        self.description = "Added files: %s" % filenames
        


    def postprocess(self):
        '''remove the source files after checkin'''
        for path in self.file_paths:
            os.unlink(path)
