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

__all__ = ["CheckinMetadataHandler"]

import os, sys, re, subprocess

from pyasm.common import Common


try:
    from PIL import Image
    HAS_PIL = True
    # Test to see if imaging actually works
    import _imaging
except:
    HAS_PIL = False

if Common.which("convert"):
    HAS_IMAGEMAGICK = True
else:
    HAS_IMAGEMAGICK = False

if Common.which("ffprobe"):
    HAS_FFMPEG = True
else:
    HAS_FFMPEG = False





class CheckinMetadataHandler():
    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def execute(my):

        # extra data from the file check-in

        commit = my.kwargs.get("commit")
        if commit in ['false', False]:
            commit = False
        else:
            commit = True

        # metadata can only be associated with a single file on the
        # snapshot.
        files = my.kwargs.get("files")
        file_objects = my.kwargs.get("file_objects")

        snapshot_metadata = None

        for i, file in enumerate(files):
            # first use PIL
            path = file
            base, ext = os.path.splitext(path)
            file_object = file_objects[i]

            if HAS_FFMPEG:
                parser_type = "FFMPEG"
            elif HAS_IMAGEMAGICK:
                parser_type = "ImageMagick"
            else:
                parser_type = "PIL"

            metadata = {}
            if not os.path.exists(path):
                pass

            elif ext in ['.txt','.doc','.docx','.xls','.rtf','.odt']:
                pass

            elif parser_type == "FFMPEG":
                parser = FFProbeMetadataParser(path=path)
                metadata = parser.get_metadata()
            elif parser_type == "ImageMagick":
                parser = ImageMagickMetadataParser(path=path)
                metadata = parser.get_metadata()
            else:
                parser = PILMetadataParser(path=path)
                metadata = parser.get_metadata()


            metadata['__parser__'] = parser_type

            """

            if os.path.exists(path):
                try:
                    parser = ImageMagickMetadataParser(path=path)
                    metadata = parser.get_metadata()
                except:
                    try:
                        #parser = PILMetadataParser(path=path)
                        parser = FFProbeMetadataParser(path=path)
                        metadata = parser.get_metadata()
                    except:
                        metadata = {}
            else:
                metadata = {}
            """

            # add some default metadata
            basename = os.path.basename(path)
            path = file_object.get_lib_path()
            dirname = os.path.dirname(path)
            parts = basename.split(".")
            ext = parts[-1]
            try:
                # occasionally, people will put frame numbers as the last
                # part
                ext = int(ext)
                ext = parts[-2]
            except:
                pass

            metadata['Ext'] = ext
            metadata['Basename'] = basename
            metadata['Dirname'] = dirname


            if metadata and not file_object.get_value("metadata"):
                file_object.add_metadata(metadata, replace=True)
                searchable = my.get_searchable(metadata)
                file_object.set_value("metadata_search", searchable)

                file_object.commit()


                if i == 0:
                    snapshot = my.kwargs.get("snapshot")
                    snapshot.add_metadata(metadata, replace=True)
                    if commit:
                        snapshot.commit()



    def get_searchable(my, metadata):
        pairs = []
        pairs_set = set()
        for name, value in metadata.items():
            # get rid of the spaces
            if name == "__keys__":
                continue

            # ignore attributes that are numbers only
            try:
                name = int(name)
                continue
            except:
                pass

            # clean up the names for indexed searching
            name = name.lower()
            name = name.replace(" ", "_")
            name = name.replace(":", "_")
      
            # otherwise it could an int or float
            if isinstance(value, basestring):
                value = value.lower()
                value = value.replace("(", "")
                value = value.replace(")", "")
                value = value.replace(" ", "_")
                keys = value.split(" ")
            
            if len(keys) > 1:
                for key in keys:
                    pair = "%s=%s" % (name, key)
                    if pair in pairs_set:
                        continue
                    pairs.append(pair)
                    pairs_set.add(pair)

            
            pair = "%s=%s" % (name, value)
            pairs.append(pair)



        searchable = " ".join(pairs)

        return searchable



#
# Common file types
#
#from PIL import Image
#from PIL.ExifTags import TAGS

class BaseMetadataParser(object):
    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def get_media_type(my):
        return "image"

    def get_metadata(my):
        return {}

    def get_tactic_mapping(my):
        return {}


    def get_initial_data(my):
        return {
        }

    def get_tactic_metadata(my):

        tactic_data = my.get_initial_data()

        metadata = my.get_metadata()

        mapping = my.get_tactic_mapping()
        for name, name2 in mapping.items():
            tactic_data[name] = metadata.get(name2)

        return tactic_data
    
    def sanitize_data(my, data):
        # sanitize output
        RE_ILLEGAL_XML = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
        data = re.sub(RE_ILLEGAL_XML, "?", data)
        return data
    
    



class PILMetadataParser(BaseMetadataParser):

    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def get_metadata(my):
        path = my.kwargs.get("path")

        try:
            im = Image.open(path)

        except:
            im = None
            pass
        
        return my.get_data(im)

 
    def get_data(my, im):
        #info = im._getexif()
        ret = {}
        if not im:
            return ret
        #if info:
        #    for tag, value in info.items():
        #        decoded = TAGS.get(tag, tag)
        #        ret[decoded] = value

        size = im.size
        ret['width'] = size[0]
        ret['height'] = size[1]
        ret['format'] = im.format
        ret['format_description'] = im.format_description


        return ret


class ImageMagickMetadataParser(BaseMetadataParser):

    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def get_metadata(my):
        path = my.kwargs.get("path")

        import subprocess, re

        ret = {}

        process = subprocess.Popen(['identify','-verbose', path], shell=False, stdout=subprocess.PIPE)
        ret_val, error = process.communicate()
        if error:
            return ret

        ret_val = my.sanitize_data(ret_val)
        p = re.compile(":\ +")

        level = 0
        names = []
        curr_ret = ret
        for line in ret_val.split("\n"):
            if not line:
                continue

            index = 0
            while 1:
                if  line[index] != ' ':
                    break
                index += 1
            level = index / 2
            line = line.strip()

            if line.endswith(":"):
                name = line.rstrip(":")
                curr_ret = {}
                ret[name] = "None"
                continue

            parts = re.split(p, line)
            name = parts[0]
            value = parts[1]
            value = value.encode('utf8', 'ignore')
            ret[name] = value

            names.append(name)

        if names:
            ret['__keys__'] = names


        return ret



class FFProbeMetadataParser(BaseMetadataParser):

    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def get_metadata(my):
        path = my.kwargs.get("path")
        out = my.probe_file(path)
        # sanitize output
        out = my.sanitize_data(out)

        metadata = my.parse_output(out)

        return metadata

        
        


    def probe_file(my, fpath):
        cmd = ['ffprobe', '-show_streams', '-pretty', '-loglevel', 'quiet', fpath]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out 


    def parse_output(my, out):

        index = 0
        metadata_list = {}

        metadata = {}


        for line in out.split("\n"):
            if line.find("STREAM") != -1:
                continue
            if not line:
                continue

            line = line.strip()
            parts = line.split("=")
            name = parts[0]
            value = parts[1]

            if name == "index":
                index = value
                data = {}

            elif name == "codec_type":
                metadata[value] = data

            data[str(name)] = str(value)

        flat_metadata = {}
        for prefix, data in metadata.items():
            for name, value in data.items():
                key = "%s:%s" % (prefix, name)
                flat_metadata[key] = value

        return flat_metadata







if __name__ == '__main__':
    import sys
    import tacticenv
    parser = FFProbeMetadataParser(path=sys.argv[1])
    metadata = parser.get_metadata()
    from pyasm.common import Common
    Common.pretty_print(metadata)

