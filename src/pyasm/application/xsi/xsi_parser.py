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


    def __init__(self, file_path):
        self.file_path = file_path

        self.filters = []
        self.read_only_flag = True

        self.current_node = None
        self.current_node_type = None

        self.app = None

    def set_app(self, app):
        self.app = app


    def get_file_path(self):
        return self.file_path


    
    def parse(self):
 
        # find all of the textures in the extracted file
        file = open(self.file_path, "r")

        if not self.read_only_flag:
            file2 = open(self.file_path+".tmp", "w")

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
                if not self.read_only_flag:
                    file2.write(line)
                    file2.write("\n")
                continue

            # handle multi lines
            full_line.append(line)
            if line.endswith(self.ENDLINE_DELIMITER):
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
                values = self._extract_values(expr, line)
                if values:
                    self.current_node_type = values[0]
                    self.current_node = values[1]
                else:
                    expr = r'(\w+)\ +{'
                    values = self._extract_values(expr, line)
                    if values:
                        self.current_node_type = values[0]


            # go through the filters
            for filter in self.filters:
                new_line = filter.process(line)
                if new_line:
                    line = new_line

            if not self.read_only_flag:
                file2.write(line)
                file2.write("\n")

        file.close()
        if not self.read_only_flag:
            file2.close()
            shutil.move("%s.tmp" % self.file_path, self.file_path)





class XSIParserFilter(object):

    def __init__(self):
        self.parser = None
        self.app = None


    def set_parser(self, parser):
        self.parser = parser
        self.app = parser.app



    def _extract_values(self, expr, line):
        p = re.compile(expr, re.DOTALL)
        m = p.search(line)
        if not m:
            return None
        values = m.groups()
        if not values:
            raise TacticException('Error parsing [%s] with regex [%s]' %(line, expr))
        return values



    def _extract_value(self, expr, line):
        values = self._extract_values(expr, line)
        if values:
            return values[0]
        else:
            return ""







class XSIParserTextureFilter(XSIParserFilter):

    def __init__(self):
        self.parser = None

        self.global_dirs = ['C:']
        self.texture_nodes = []
        self.texture_paths = []
        self.texture_attrs = []


    def message(self, msg):
        if self.app:
            self.app.message(msg)
        else:
            print msg

    def set_global_dirs(self, dir_list):
        self.global_dirs = dir_list


    def get_textures(self):
        return self.texture_nodes, self.texture_paths, self.texture_attrs


    def process(self, line):

        current_node = self.parser.current_node
        if not current_node:
            return
            
        current_node_type = self.parser.current_node_type
        if current_node_type not in ['XSI_Image']:
            return


        # extract file texture 
        if re.search(r'"(.*)"', line):

            p = re.compile(r'"(.*)"')
            m = p.search(line)
            if m:
                results = m.groups()
                attr = ""
                self.message( "Texture: %s %s %s" % (current_node, results[0], attr) )
                self._add_texture(current_node, results[0], attr)



    def _add_texture(self, current_node, path, attr=""):

        # By default, dotXSI files will dump out the texture in the same path
        # as the .xsi file. 
        if not os.path.exists(path):
            xsi_path = self.parser.get_file_path()
            dir = os.path.dirname(xsi_path)
            path = "%s/%s" % (dir, path)

        if os.path.exists(path):
            self.texture_nodes.append( current_node )
            self.texture_paths.append( path )
            if not attr:
                attr = "ftn"
            self.texture_attrs.append( attr )
        else:
            self.message("WARNING: texture_path '%s' does not exist" % path)



class XSIParserTextureEditFilter(XSIParserTextureFilter):

    def process(self, line):
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

            self.texture_nodes.append( current_node )
            self.texture_paths.append( path )
            self.texture_attrs.append( attr )




