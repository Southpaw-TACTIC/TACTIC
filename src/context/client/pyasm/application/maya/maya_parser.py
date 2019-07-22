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


__all__ = ['MayaParser', 'MayaParserFilter', 'MayaParserTextureFilter', 'MayaParserTextureEditFilter', 'MayaParserReferenceFilter']


from .maya_app import Maya
from pyasm.application.common import TacticException
import string, re, os, shutil


class MayaParser(object):
    '''class to read a maya ascii file'''


    def __init__(self, file_path):
        self.file_path = file_path

        self.filters = []
        self.read_only_flag = True

        self.current_node = None
        self.current_node_type = None

        self.line_delimiter = ";"


    def set_line_delimiter(self, delimiter):
        self.line_delimiter = delimiter



    def add_filter(self, filter):
        self.filters.append(filter)
        filter.set_parser(self)



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
            if line.endswith(self.line_delimiter):
                # remove \n
                line = " ".join(full_line)
                full_line = []
            else:
                # if no ; then continue
                continue

            # match lines starting with createNode ...

            if line.startswith("createNode"):
                # anything in the first set of double quotes
                expr = r'createNode (\w+) -n "([^"]*)"'
                values = self._extract_values(expr, line)
                if values:
                    self.current_node_type = values[0]
                    self.current_node = values[1]


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








class MayaParserFilter(object):

    def __init__(self):
        self.parser = None


    def set_parser(self, parser):
        self.parser = parser



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






class MayaParserReferenceFilter(MayaParserFilter):
    def __init__(self):
        self.parser = None

        self.reference_paths = []


    def get_references(self):
        return reference_paths


    def process(self, line):
        # extract references
        if line.startswith('file -r'):
            #expr = r'file -rdi 1 -ns ".*" -rfn "\w+" "(.*)";'
            expr = r'-rfn ".*" "(.*)";'
            path = self._extract_value(expr, line)
            if path:
                self.reference_paths.append(path)
            else:
                print("WARNING: could not extract texture path from:\n\t%s" % line)





class MayaParserTextureFilter(MayaParserFilter):

    def __init__(self):
        self.parser = None

        self.global_dirs = ['C:']
        self.texture_nodes = []
        self.texture_paths = []
        self.texture_attrs = []

    def set_global_dirs(self, dir_list):
        self.global_dirs = dir_list


    def get_textures(self):
        return self.texture_nodes, self.texture_paths, self.texture_attrs


    def process(self, line):

        current_node = self.parser.current_node
        if not current_node:
            return
            
        current_node_type = self.parser.current_node_type
        if current_node_type not in ['file', 'imagePlane', 'MayaManCustomShader']:
            return

        # extract file texture 
        if re.match(r'^setAttr "\.(ftn|imn)" -type "string"|^setAttr [-\w\s]*"\..*texture" -type "string"', line):

            p = re.compile(r'setAttr.*"\.(.+?)".*-type "string" "(.+?)";')
            m = p.match(line)
            if m:
                results = m.groups()
                self._add_texture(current_node, results[1], results[0])



    def _add_texture(self, current_node, path, attr=""):

        # if the path in the field does not exist, prepend it with the 
        # file_rule_entry dir for textures or sourceImages
        if not os.path.exists(path):
            self.app = Maya.get()
            texture_dir1 = self.app.mel('workspace -q -fre "textures"')
            texture_dir2 = self.app.mel('workspace -q -fre "sourceImages"')
            exists = False
            if texture_dir1:
                path = '%s/%s' %(texture_dir1, path)
                exists = os.path.exists(path)
                if not exists:
                    print("WARNING: texture_path '%s' does not exist" % path)
            if not exists and texture_dir2:
                path = '%s/%s' %(texture_dir2, path)
                exists = os.path.exists(path)
                if not exists:
                    print("WARNING: texture_path '%s' does not exist" % path)
            if not exists:
                return

            # Note: Temporarily disabling until we get a change to really test
            # this.
            """
            for dir in self.global_dirs:
                filename = path
                mayaman_path = "%s/%s" %(dir, filename)
                if os.path.exists(mayaman_path):
                    path = mayaman_path
                    break
            else:
                print("WARNING: texture_path '%s' does not exist" % path)
                return
            """
        if os.path.exists(path):
            self.texture_nodes.append( current_node )
            self.texture_paths.append( path )
            if not attr:
                attr = "ftn"
            self.texture_attrs.append( attr )
        else:
            print("WARNING: texture_path '%s' does not exist" % path)



class MayaParserTextureEditFilter(MayaParserTextureFilter):

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

            if path:
                self.texture_nodes.append( current_node )
                self.texture_paths.append( path )
                self.texture_attrs.append( attr )




