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


from cStringIO import StringIO
from maya_app import Maya
from pyasm.application.common import TacticException
import string, re, os, shutil


class MayaParser(object):
    '''class to read a maya ascii file'''


    def __init__(my, file_path):
        my.file_path = file_path

        my.filters = []
        my.read_only_flag = True

        my.current_node = None
        my.current_node_type = None

        my.line_delimiter = ";"


    def set_line_delimiter(my, delimiter):
        my.line_delimiter = delimiter



    def add_filter(my, filter):
        my.filters.append(filter)
        filter.set_parser(my)



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
            if line.endswith(my.line_delimiter):
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
                values = my._extract_values(expr, line)
                if values:
                    my.current_node_type = values[0]
                    my.current_node = values[1]


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








class MayaParserFilter(object):

    def __init__(my):
        my.parser = None


    def set_parser(my, parser):
        my.parser = parser



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






class MayaParserReferenceFilter(MayaParserFilter):
    def __init__(my):
        my.parser = None

        my.reference_paths = []


    def get_references(my):
        return reference_paths


    def process(my, line):
        # extract references
        if line.startswith('file -r'):
            #expr = r'file -rdi 1 -ns ".*" -rfn "\w+" "(.*)";'
            expr = r'-rfn ".*" "(.*)";'
            path = my._extract_value(expr, line)
            if path:
                my.reference_paths.append(path)
            else:
                print "WARNING: could not extract texture path from:\n\t%s" % line





class MayaParserTextureFilter(MayaParserFilter):

    def __init__(my):
        my.parser = None

        my.global_dirs = ['C:']
        my.texture_nodes = []
        my.texture_paths = []
        my.texture_attrs = []

    def set_global_dirs(my, dir_list):
        my.global_dirs = dir_list


    def get_textures(my):
        return my.texture_nodes, my.texture_paths, my.texture_attrs


    def process(my, line):

        current_node = my.parser.current_node
        if not current_node:
            return
            
        current_node_type = my.parser.current_node_type
        if current_node_type not in ['file', 'imagePlane', 'MayaManCustomShader']:
            return

        # extract file texture 
        if re.match(r'^setAttr "\.(ftn|imn)" -type "string"|^setAttr [-\w\s]*"\..*texture" -type "string"', line):

            p = re.compile(r'setAttr.*"\.(.+?)".*-type "string" "(.+?)";')
            m = p.match(line)
            if m:
                results = m.groups()
                my._add_texture(current_node, results[1], results[0])



    def _add_texture(my, current_node, path, attr=""):

        # if the path in the field does not exist, prepend it with the 
        # file_rule_entry dir for textures or sourceImages
        if not os.path.exists(path):
            my.app = Maya.get()
            texture_dir1 = my.app.mel('workspace -q -fre "textures"')
            texture_dir2 = my.app.mel('workspace -q -fre "sourceImages"')
            exists = False
            if texture_dir1:
                path = '%s/%s' %(texture_dir1, path)
                exists = os.path.exists(path)
                if not exists:
                    print "WARNING: texture_path '%s' does not exist" % path
            if not exists and texture_dir2:
                path = '%s/%s' %(texture_dir2, path)
                exists = os.path.exists(path)
                if not exists:
                    print "WARNING: texture_path '%s' does not exist" % path
            if not exists:
                return

            # Note: Temporarily disabling until we get a change to really test
            # this.
            """
            for dir in my.global_dirs:
                filename = path
                mayaman_path = "%s/%s" %(dir, filename)
                if os.path.exists(mayaman_path):
                    path = mayaman_path
                    break
            else:
                print "WARNING: texture_path '%s' does not exist" % path
                return
            """
        if os.path.exists(path):
            my.texture_nodes.append( current_node )
            my.texture_paths.append( path )
            if not attr:
                attr = "ftn"
            my.texture_attrs.append( attr )
        else:
            print "WARNING: texture_path '%s' does not exist" % path



class MayaParserTextureEditFilter(MayaParserTextureFilter):

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

            if path:
                my.texture_nodes.append( current_node )
                my.texture_paths.append( path )
                my.texture_attrs.append( attr )




