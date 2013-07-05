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

__all__ = ['CompCheckin', 'FusionFileFilter', 'ShakeFileFilter', 'NukeFileFilter']

import os, shutil, re

from pyasm.common import *
from pyasm.checkin import *
from pyasm.biz import *
from pyasm.prod.biz import *
from pyasm.command import CommandException, Command
from pyasm.search import SearchType, Search
from pyasm.application.maya import *


class CompCheckin(FileCheckin):

    def __init__(my, sobject, file_paths, file_types, context="publish", column=None, snapshot_type=None, is_current=True):
        BaseCheckin.__init__(my, sobject)
        context = context
        snapshot_type = "composite"

        super(CompCheckin,my).__init__(sobject, file_paths, file_types, context, snapshot_type=snapshot_type, is_current=is_current)



    def preprocess_files(my, paths):
        '''Process the maya file so that all of the files exist.
        This makes the files self-consistent and usable without the
        asset management system'''
        pass
            


    def add_dependencies(my, snapshot_xml):
        '''look into shake session/file and create the files'''

        if not my.file_paths:
            return

        path = my.file_paths[0]
        if path.endswith(".shk"):
            parser = MayaParser(path)
            shake_filter = ShakeFileFilter()
            parser.add_filter(shake_filter)
            parser.parse()

            my.file_outs = shake_filter.get_file_outs()
            my.file_ins = shake_filter.get_file_ins()

        elif path.endswith(".comp"):
            parser = MayaParser(path)
            parser.set_line_delimiter(",")
            fusion_filter = FusionFileFilter()
            parser.add_filter(fusion_filter)
            parser.parse()

            my.file_outs = fusion_filter.get_file_outs()
            my.file_ins = fusion_filter.get_file_ins()

        elif path.endswith(".nk"):
            parser = MayaParser(path)
            nuke_filter = NukeFileFilter()
            parser.set_line_delimiter("")
            parser.add_filter(nuke_filter)
            parser.parse()

            my.file_outs = nuke_filter.get_file_outs()
            my.file_ins = nuke_filter.get_file_ins()

        else:
            return


        xml = Xml()
        xml.read_string(snapshot_xml)
        builder = SnapshotBuilder(xml)
        for file_path in my.file_ins:
            #print file_path
            builder.add_ref_by_file_path(file_path, type="input_ref")


        # commit it to the snapshot
        my.snapshot.set_value("snapshot", builder.to_string())       
        my.snapshot.commit()


        





class ShakeFileFilter(MayaParserFilter):

    def __init__(my):
        my.file_ins = []
        my.file_outs = []
        super(ShakeFileFilter,my).__init__()

    def get_file_ins(my):
        return my.file_ins

    def get_file_outs(my):
        return my.file_outs

    def process(my, line):
        # replace any paths with the new paths of the checked in textures
        if line.find('= FileOut(') != -1:
            
            p = re.compile("\w+ = FileOut\((\w+), \"(.*?)\",")
            m = p.search(line)
            if m:
                groups = m.groups()
                node = groups[0]
                file_out = groups[1]
                file_out = file_out.replace("\\", "/")
                my.file_outs.append(file_out)
        elif line.find('= FileIn(') != -1:
            p = re.compile("\w+ = FileIn\((\w+), \"(.*?)\",")
            m = p.search(line)
            if m:
                groups = m.groups()
                node = groups[0]
                file_in = groups[1]
                file_in = file_in.replace("\\", "/")
                my.file_ins.append(file_in)


        return line




class FusionFileFilter(MayaParserFilter):

    def __init__(my):
        my.file_ins = []
        my.file_outs = []
        super(FusionFileFilter,my).__init__()

    def get_file_ins(my):
        return my.file_ins

    def get_file_outs(my):
        return my.file_outs

    def process(my, line):

        # replace any paths with the new paths of the checked in textures
        if line.startswith("Filename ="):
            p = re.compile(r'Filename = "(.*)",')
            m = p.search(line)
            if m:
                groups = m.groups()
                file_path = groups[0]
                my.file_ins.append(file_path)
 

class NukeFileFilter(MayaParserFilter):

    def __init__(my):
        my.file_ins = []
        my.file_outs = []
        super(NukeFileFilter,my).__init__()

    def get_file_ins(my):
        return my.file_ins

    def get_file_outs(my):
        return my.file_outs

    def process(my, line):

        # replace any paths with the new paths of the checked in textures
        if line.startswith("file"):
            p = re.compile(r'file (.*)')
            m = p.search(line)
            if m:
                groups = m.groups()
                file_path = groups[0]
                my.file_ins.append(file_path)




