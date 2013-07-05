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

import os, sys, re



class CheckinMetadataHandler():
    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def execute(my):

        # extra data from the file check-in

        # metadata can only be associated with a single file on the
        # snapshot.
        files = my.kwargs.get("files")
        file_objects = my.kwargs.get("file_objects")

        snapshot_metadata = None

        for i, file in enumerate(files):
            # first use PIL
            path = file
            base, ext = os.path.splitext(path)
            if ext in ['.txt','.doc','.docx','.xls','.rtf','.odt']:
                continue

            if os.path.exists(path):
                try:
                    #parser = PILMetadataParser(path=path)
                    parser = ImageMagickMetadataParser(path=path)
                    metadata = parser.get_metadata()
                except:
                    metadata = {}
            else:
                metadata = {}

            # add some default metadata
            basename = os.path.basename(path)
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


            file_object = file_objects[i]
            if metadata and not file_object.get_value("metadata"):
                file_object.add_metadata(metadata, replace=True)

                searchable = my.get_searchable(metadata)
                file_object.set_value("metadata_search", searchable)

                file_object.commit()


                if i == 0:
                    snapshot = my.kwargs.get("snapshot")
                    snapshot.add_metadata(metadata, replace=True)
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
            value = value.lower()
            value = value.replace("(", "")
            value = value.replace(")", "")



            keys = value.split(" ")
            if len(keys) > 1:
                for key in keys:
                    pair = "%s=%s" % (name, key)
                    if pair in pairs_set:
                        continue
                    pairs.append(pair)
                    pairs_set.add(pair)

            value = value.replace(" ", "_")
            pair = "%s=%s" % (name, value)
            pairs.append(pair)



        searchable = " ".join(pairs)

        return searchable



#
# Common file types
#
#from PIL import Image
#from PIL.ExifTags import TAGS
import Image

class PILMetadataParser:

    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def get_metadata(my):
        path = my.kwargs.get("path")

        try:
            im = Image.open(path)
        except:
            pass

        return my.get_data(im)

 
    def get_data(my, im):
        #info = im._getexif()
        ret = {}
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


class ImageMagickMetadataParser:

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




