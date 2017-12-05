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


__all__ = ['XSIParser', 'XSIParserFilter']

from cStringIO import StringIO
from pyasm.application.common import TacticException
import string, re, os, shutil

from pyasm.application.maya import MayaParser


class XSIParser(MayaParser):
    '''class to read a .dotXSI file'''

    ENDLINE_DELIMITER = '}'


    def __init__(my, file_path):
        my.file_path = file_path

        my.filters = []
        my.read_only_flag = True

        my.current_node = None
        my.current_node_type = None

        my.app = None

    def set_app(my, app):
        my.app = app


    def get_file_path(my):
        return my.file_path


    
    def parse(my):
 
        # find all of the textures in the extracted file
        file = open(my.file_path, "r")

        if not my.read_only_flag:
            file2 = open(my.file_path+".tmp", "w")

        current_node = None
        full_line = []

        while 1:
            line = file.readline()
            if not line:
                break

            """
            # join multi lines
            line = line.rstrip()
            line = line.lstrip()
            if line.startswith("//"):
                if not my.read_only_flag:
                    file2.write(line)
                    file2.write("\n")
                continue

            # handle multi lines
            full_line.append(line)
            if line.endswith(my.ENDLINE_DELIMITER):
                # remove \n
                line = "\n".join(full_line)
                full_line = []
            else:
                # if no ; then continue
                continue
            """

            cmp_line = line.rstrip()
            cmp_line = cmp_line.lstrip()

            # match lines starting with createNode ...
            if cmp_line.startswith("SI_") or cmp_line.startswith("XSI_"):
                expr = r'(\w+)\ +([\w-]+)\ +{'
                values = my._extract_values(expr, line)
                if values:
                    my.current_node_type = values[0]
                    my.current_node = values[1]
                else:
                    expr = r'(\w+)\ +{'
                    values = my._extract_values(expr, line)
                    if values:
                        my.current_node_type = values[0]


            # go through the filters
            for filter in my.filters:
                new_line = filter.process(line)
                if new_line:
                    line = new_line

            if not my.read_only_flag:
                file2.write(line)
                file2.write("\n")

        file.close()
        if not my.read_only_flag:
            file2.close()
            shutil.move("%s.tmp" % my.file_path, my.file_path)





class XSIParserFilter(object):

    def __init__(my):
        my.parser = None
        my.app = None


    def set_parser(my, parser):
        my.parser = parser
        my.app = parser.app



    def _extract_values(my, expr, line):
        p = re.compile(expr, re.DOTALL)
        m = p.search(line)
        if not m:
            return None
        values = m.groups()
        if not values:
            raise TacticException('Error parsing [%s] with regex [%s]' %(line, expr))
        return values



    def _extract_value(my, expr, line):
        values = my._extract_values(expr, line)
        if values:
            return values[0]
        else:
            return ""







class XSIParserTextureFilter(XSIParserFilter):

    def __init__(my):
        my.parser = None

        my.global_dirs = ['C:']
        my.texture_nodes = []
        my.texture_paths = []
        my.texture_attrs = []


    def message(my, msg):
        if my.app:
            my.app.message(msg)
        else:
            print msg

    def set_global_dirs(my, dir_list):
        my.global_dirs = dir_list


    def get_textures(my):
        return my.texture_nodes, my.texture_paths, my.texture_attrs


    def process(my, line):

        current_node = my.parser.current_node
        if not current_node:
            return
            
        current_node_type = my.parser.current_node_type
        if current_node_type not in ['XSI_Image']:
            return


        # extract file texture 
        if re.search(r'"(.*)"', line):

            p = re.compile(r'"(.*)"')
            m = p.search(line)
            if m:
                results = m.groups()
                attr = ""
                my.message( "Texture: %s %s %s" % (current_node, results[0], attr) )
                my._add_texture(current_node, results[0], attr)



    def _add_texture(my, current_node, path, attr=""):

        # By default, dotXSI files will dump out the texture in the same path
        # as the .xsi file. 
        if not os.path.exists(path):
            xsi_path = my.parser.get_file_path()
            dir = os.path.dirname(xsi_path)
            path = "%s/%s" % (dir, path)

        if os.path.exists(path):
            my.texture_nodes.append( current_node )
            my.texture_paths.append( path )
            if not attr:
                attr = "ftn"
            my.texture_attrs.append( attr )
        else:
            my.message("WARNING: texture_path '%s' does not exist" % path)



class XSIParserTextureEditFilter(XSIParserTextureFilter):

    def process(my, line):
        key = 'setAttr ".ed" -type "dataReferenceEdits"'
        if not line.startswith(key):
            return

        p = re.compile(r'"([\w|\:]+)" "(fileTextureName|imageName)" " -type \\"string\\" \\"(.*?)\\""')
        matches = p.findall(line)
        if not matches:
            return

        for match in matches:
            current_node = match[0]
            attr = match[1]
            if attr == "fileTextureName":
                attr = "ftn"
            else:
                attr = "imn"

            path = match[2]

            my.texture_nodes.append( current_node )
            my.texture_paths.append( path )
            my.texture_attrs.append( attr )




