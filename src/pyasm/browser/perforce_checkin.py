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


__all__ = ['PerforceAssetCheckinCbk', 'TacticAssetCheckinCbk', 'TacticCompCheckinCbk', 'MaxAssetCheckinCbk']

import os, shutil

from pyasm.common import TacticException, UserException, Common
from pyasm.command import Command
from pyasm.search import Search
from pyasm.checkin import SnapshotCheckin, FileCheckin
from repo_action_wdg import *
from pyasm.web import *
from pyasm.biz import File, IconCreator, Project

class PerforceAssetCheckinCbk(SnapshotCheckin):
    '''this is run in conjunction with a Perforce changelist commit'''
    def preprocess(my):
        web = WebContainer.get_web()
        my.description = web.get_form_value(PerforceWdg.PUBLISH_DESC)

    def check(my):
        return True



class TacticAssetCheckinCbk(Command):
    '''checkin the uploaded files'''

    def __init__(my, search_key, project_code):
        my.search_key = search_key
        my.project_code = project_code
        my.upload_files = []
        my.file_type_dict = {}
        super(TacticAssetCheckinCbk, my).__init__()

    def check(my):
        web = WebContainer.get_web()
        
        upload_files = web.get_form_value("upload_files").split('|')
        if not upload_files or upload_files[0] == "":
            raise TacticException("No files selected for publish.")
        else:
            my.upload_files = upload_files
      

        upload_dir = web.get_upload_dir()
        checked_files = []
        # make them filesystem friendly, no space and symbols
        for file in my.upload_files:
            dir, base = os.path.split(file)
            base  = File.get_filesystem_name(base)
            file_path = "%s/%s" % (upload_dir, base)
            if not os.path.exists(file_path):
                raise TacticException("File [%s] does not exist" %file_path)
            if os.path.getsize(file_path) == 0:
                raise TacticException("Uploaded file [%s] is empty" %file_path)
            checked_files.append(file_path)
        my.upload_files = checked_files
        context = web.get_form_value(PerforceWdg.PUBLISH_CONTEXT)
        if not context:
            raise TacticException("No valid context for publish.")
        # can be overridden
        my.set_filetype_by_filename()

        # set the project 
        if my.project_code:
            Project.set_project(my.project_code)
        else:
            raise TacticException('No project information')
        return True
    
    def set_filetype_by_filename(my):
        if len(my.upload_files) > 2:
            raise UserException("Maximum of 2 files (1 psd and 1 image)\
                     or just 1 arbitrary file can be published.")
        
        for file in my.upload_files:
            ext = File.get_extension(file).lower()
            if ext == 'psd':
                # this can be anything like 'source' or 'concept'
                my.file_type_dict[file] = 'psd'
            elif ext in ['png','tif','jpg','gif']:
                # 'main' and 'file' are used for display in Repo
                my.file_type_dict[file] = 'main'
            else:
                my.file_type_dict[file] = 'main'

        file_types = my.file_type_dict.values()
        if file_types.count('main') > 1:
            raise UserException("Maximum of 2 files (1 psd and 1 image)\
                     or just 1 arbitrary file can be published.")
                
    def execute(my):
       

        sobject = Search.get_by_search_key(my.search_key)
        web = WebContainer.get_web()
       
        desc = web.get_form_value(PerforceWdg.PUBLISH_DESC)
        context = web.get_form_value(PerforceWdg.PUBLISH_CONTEXT)
        sub_context = web.get_form_value(PerforceWdg.PUBLISH_SUBCONTEXT)
        currency = web.get_form_value(TacticWdg.CURRENCY)
        if sub_context:
            context = '%s/%s' %(context, sub_context)
        
        file_paths = []
        file_types = []
        
        for upload_file in my.upload_files:
            file_paths.append(upload_file)
            file_types.append(my.file_type_dict.get(upload_file))
   
        # add icons
        icon_paths, icon_types = IconCreator.add_icons(file_paths)
        for i in range(0, len(icon_paths)):
            icon_path = icon_paths[i]
            if not icon_path:
                continue

            icon_type = icon_types[i]
            file_paths.append(icon_path)
            file_types.append(icon_type)
        
        if not currency:
            currency = False
        else:
            currency = True
        
        checkin_cls = my.get_checkin_cls() 
        checkin = Common.create_from_class_path(checkin_cls, args=[sobject, file_paths, file_types, context], kwargs={'is_current': currency})
        checkin.description = desc
        for file_path in file_paths:
            basename = os.path.basename(file_path)
            my.add_description("Published %s" %basename)
        checkin.execute()

        my.file_paths = file_paths

    def get_checkin_cls(my):
        return "pyasm.checkin.FileCheckin"

    def postprocess(my):
        # clean up
        for file_path in my.file_paths:
            pass
            #os.unlink(file_path)

class TacticCompCheckinCbk(TacticAssetCheckinCbk):
    '''checkin the uploaded files'''

    def get_checkin_cls(my):
        return "pyasm.prod.checkin.CompCheckin"

# example implementation
class ConceptCheckinCbk(TacticAssetCheckinCbk):

    def set_filetype_by_filename(my):
        if len(my.upload_files) > 2:
            raise UserException("Maximum of 2 files (1 psd and 1 image)\
                    can be published together.")
        
        for file in my.upload_files:
            ext = File.get_extension(file).lower()
            if ext == 'psd':
                # this can be anything like 'source' or 'concept'
                my.file_type_dict[file] = 'source'
            elif ext == 'png' or ext == 'tif' or ext == 'jpg':
                # 'main' and 'file' are used for display in Repo
                my.file_type_dict[file] = 'texture'

        file_types = my.file_type_dict.values()
        if file_types.count('file') > 1:
            raise UserException("Maximum of 2 files (1 psd and 1 image)\
                    can be published together.")
 
 
# example implementation
class MaxAssetCheckinCbk(TacticAssetCheckinCbk):

    def set_filetype_by_filename(my):
        if len(my.upload_files) == 0:
            raise UserException("Must select at least one file")
        
        for file in my.upload_files:
            ext = File.get_extension(file).lower()
            if ext == 'max':
                # this can be anything like 'source' or 'concept'
                my.file_type_dict[file] = 'max'
            elif ext == 'png' or ext == 'tif' or ext == 'jpg':
                # 'main' and 'file' are used for display in Repo
                my.file_type_dict[file] = 'texture'

 
 
