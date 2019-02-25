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

__all__ = ['ParserImportError', 'CheckinMetadataHandler', 'BaseMetadataParser', 'PILMetadataParser', 'ExifMetadataParser', 'ImageMagickMetadataParser', 'FFProbeMetadataParser', 'IPTCMetadataParser','XMPMetadataParser', 'XMPKeywordsParser']


import os, sys, re, subprocess

from pyasm.common import Common, Xml
from pyasm.biz import File

# OS-specific import checks
convert_exe = "convert"
ffprobe_exe = "ffprobe"

if os.name == "nt":
    convert_exe+= ".exe"
    ffprobe_exe+= ".exe"

try:
    from PIL import Image
    HAS_PIL = True
    # Test to see if imaging actually works
    import _imaging
except:
    HAS_PIL = False

if Common.which(convert_exe):
    HAS_IMAGEMAGICK = True
else:
    HAS_IMAGEMAGICK = False

if Common.which(ffprobe_exe):
    HAS_FFMPEG = True
else:
    HAS_FFMPEG = False


try:
    import exifread
    HAS_EXIF = True
except:
    HAS_EXIF = False

try:
    import iptcinfo
    HAS_IPTC = True
except:
    HAS_IPTC = False

try:
    import libxmp
    HAS_XMP = True
except:
    HAS_XMP = False


class ParserImportError(ImportError):
    def __init__(self,*args,**kwargs):
        ImportError.__init__(self,*args,**kwargs)

class CheckinMetadataHandler():
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self):

        # extra data from the file check-in

        commit = self.kwargs.get("commit")
        if commit in ['false', False]:
            commit = False
        else:
            commit = True

        # metadata can only be associated with a single file on the
        # snapshot.
        files = self.kwargs.get("files")
        file_objects = self.kwargs.get("file_objects")

        snapshot_metadata = None

        parser_type = self.kwargs.get("parser")

        for i, file in enumerate(files):
            path = file
            ext = File.get_extension(path)
            file_object = file_objects[i]

            if not os.path.exists(path):
                continue
            elif parser_type != "auto" and parser_type != "true":
                pass
            elif ext in File.VIDEO_EXT:
                parser_type = "FFMPEG"
            elif ext in File.NORMAL_EXT:
                continue
            else:
                if HAS_IMAGEMAGICK:                    
                    parser_type = "ImageMagick" 
                else:
                    parser_type = "PIL"
            metadata = {}

            if parser_type == "FFMPEG":
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
                searchable = self.get_searchable(metadata)
                file_object.set_value("metadata_search", searchable)

                file_object.commit()


                if i == 0:
                    snapshot = self.kwargs.get("snapshot")
                    snapshot.add_metadata(metadata, replace=True)
                    if commit:
                        snapshot.commit()



    def get_searchable(self, metadata):
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
            
            keys = [] 
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
    def __init__(self, **kwargs):
        self.kwargs = kwargs


    def get_title(self):
        return "Base"

    def get_media_type(self):
        return "image"

    def get_metadata(self):
        return {}

    def get_tactic_mapping(self):
        return {}

    def process_tactic_mapping(self, tactic_data, metadata):
        pass


    def get_initial_data(self):
        return {
        }

    def get_tactic_metadata(self):

        tactic_data = self.get_initial_data()

        metadata = self.get_metadata()

        mapping = self.get_tactic_mapping()
        for name, name2 in mapping.items():
            tactic_data[name] = metadata.get(name2)

        self.process_tactic_mapping(tactic_data, metadata)

        return tactic_data
    
    def sanitize_data(self, data):
        # sanitize output
        RE_ILLEGAL_XML = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                 u'|' + u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
        data = re.sub(RE_ILLEGAL_XML, "?", data)
        return data
    
   
    def get_parser_by_path(cls, path):
        ext = File.get_extension(path)

        parser_str = None

        if ext in File.VIDEO_EXT:
            if HAS_FFMPEG:
                parser_str = "FFMPEG"
            else:
                parser_str = "PIL"
        else:
            if HAS_IMAGEMAGICK:
                parser_str = "ImageMagick"
            elif HAS_PIL:
                parser_str = "PIL"
            elif HAS_EXIF:
                parser_str = "EXIF"
            elif HAS_FFMPEG:
                parser_str = "FFMPEG"
        return cls.get_parser(parser_str, path)
    get_parser_by_path = classmethod(get_parser_by_path)


    def get_parser(cls, parser_str, path):
        if parser_str == "EXIF":
            parser = ExifMetadataParser(path=path)
        elif parser_str == "IPTC":
            parser = IPTCMetadataParser(path=path)
        elif parser_str == "XMP":
            parser = XMPMetadataParser(path=path)
        elif parser_str == "ImageMagick":
            parser = ImageMagickMetadataParser(path=path)
        elif parser_str == "PIL":
            parser = PILMetadataParser(path=path)
        elif parser_str == "FFMPEG":
            parser = FFProbeMetadataParser(path=path)
        elif parser_str == "XMP Keywords":
            parser = XMPKeywordsParser(path=path)
        else:
            parser = None

        return parser
    get_parser = classmethod(get_parser)




class PILMetadataParser(BaseMetadataParser):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_title(self):
        return "PIL"

    def get_initial_data(self):
        return {
            'media_type': 'image',
            'parser': 'PIL'
        }

    def get_metadata(self):
        if not HAS_PIL:
            raise ParserImportError("Unable to import PIL parser.")

        path = self.kwargs.get("path")
        try:
            from PIL import Image
            im = Image.open(path)
            return self._get_data(im)
        except Exception, e:
            print "WARNING: ", e
            return {}

 
    def _get_data(self, im):
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


    def get_tactic_mapping(self):
        return {
            'width': 'width',
            'height': 'height',
            'format': 'format',
            'format_description': 'format_description'
        }




class ExifMetadataParser(BaseMetadataParser):

    def __init__(self, **kwargs):
        self.kwargs = kwargs


    def get_title(self):
        return "EXIF"



    def get_initial_data(self):
        return {
            'media_type': 'image',
            'parser': 'Exif'
        }



    def get_metadata(self):
        if not HAS_EXIF:
            raise ParserImportError("Unable to import EXIF parser.")

        path = self.kwargs.get("path")

        from pyasm.checkin import exifread
        #import exifread

        f = open(path)
        tags = exifread.process_file(f)
        f.close()

        return tags



class IPTCMetadataParser(BaseMetadataParser):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_title(self):
        return "IPTC"

    def get_initial_data(self):
        return {
            'media_type': 'image',
            'parser': 'IPTC'
        }



    def get_metadata(self):
        if not HAS_IPTC:
            raise ParserImportError("Unable to import IPTC parser.")

        path = self.kwargs.get("path")

        from pyasm.checkin.iptcinfo import IPTCInfo, c_datasets, c_datasets_r

        try:

            info = IPTCInfo(path)
            data = info.data 

            metadata = {}
            for key, value in data.items():
                real_key = c_datasets.get(key)
                if not real_key:
                    real_key = key
                metadata[real_key] = value


            return metadata
        except Exception, e:
            info = {
                    "Message": str(e)
            }
            return info



class XMPMetadataParser(BaseMetadataParser):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_title(self):
        return "XMP"

    def get_initial_data(self):
        return {
            'media_type': 'image',
            'parser': 'XMP'
        }



    def get_metadata(self):
        if not HAS_XMP:
            raise ParserImportError("Unable to import XMP parser.")

        path = self.kwargs.get("path")

        from libxmp.utils import file_to_dict
        from libxmp import consts

        try:

            metadata = {}

            xmp = file_to_dict(path)
            for space in xmp.keys():
                #dc = xmp[consts.XMP_NS_DC]
                dc = xmp[space]

                for key, value, options in dc:
                    metadata[key] = value


            return metadata
        except Exception, e:
            info = {
                    "Message": str(e)
            }
            return info






class ImageMagickMetadataParser(BaseMetadataParser):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_title(self):
        return "ImageMagick"


    def get_initial_data(self):
        return {
            'media_type': 'image',
            'parser': 'ImageMagick'
        }

    def get_metadata(self):
        if not HAS_IMAGEMAGICK:
            raise ParserImportError("Unable to import IMAGEMAGICK parser.")

        path = self.kwargs.get("path")

        import subprocess, re

        ret = {}

        process = subprocess.Popen(['identify','-verbose', path], shell=False, stdout=subprocess.PIPE)
        ret_val, error = process.communicate()
        if error:
            return ret

        ret_val = self.sanitize_data(ret_val)
        p = re.compile(":\ +")

        level = 0
        names = set()
        curr_ret = ret
        for line in ret_val.split("\n"):
            line = line.strip()
            if not line:
                continue

            index = 0
            while 1:
                if index >= len(line):
                    break
                if line[index] != ' ':
                    break
                index += 1
            level = index / 2
            line = line.strip()

            if not line:
                continue

            if line.endswith(":"):
                name = line.rstrip(":")
                curr_ret = {}
                ret[name] = "None"
                continue

            parts = re.split(p, line)
            if len(parts) < 2:
                print "WARNING: Skipping an ImageMagick line [%s] due to inconsistent formatting." % line
                continue
            name = parts[0]
            value = parts[1]
            try:
                if isinstance(value, unicode):
                   value = value.encode('utf-8', 'ignore')
                else:
                   value = unicode(value, errors='ignore').encode('utf-8')

                ret[name] = value
                names.add(name)
            except Exception, e:
                print "WARNING: Cannot handle line [%s] with error: " % line, e


        if names:
            ret['__keys__'] = list(names)


        return ret



    def get_tactic_mapping(self):
        return {
            'format_description': 'Format',
            'colorspace': 'Colorspace',
            'depth': 'Depth',
        }


    def process_tactic_mapping(self, tactic_data, metadata):

        geometry = metadata.get("Geometry")

        if geometry:
            if not isinstance(geometry, basestring):
                geometry = str(geometry)
                
            p = re.compile("(\d+)x(\d+)\+(\d+)\+(\d+)")
            m = p.match(geometry)
            if m:
                groups = m.groups()
                tactic_data['width'] = float(groups[0])
                tactic_data['height'] = float(groups[1])
        



class FFProbeMetadataParser(BaseMetadataParser):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_initial_data(self):
        return {
            'media_type': 'video',
            'parser': 'FFProbe'
        }


    def get_title(self):
        return "FFProbe"

    def get_metadata(self):
        path = self.kwargs.get("path")
        
        try:
            out = self.probe_file(path)
        except:
            out = ''

        # sanitize output
        
        out = self.sanitize_data(out)

        metadata = self.parse_output(out)

        return metadata

        
        


    def probe_file(self, fpath):
        cmd = ['ffprobe', '-show_streams', '-pretty', '-loglevel', 'quiet', fpath]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out 


    def parse_output(self, out):

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


    def get_tactic_mapping(self):
        return {
            'width': 'video:width',
            'height': 'video:height',
            'frames': 'video:nb_frames',
            'fps': 'video:r_frame_rate',
            'codec': 'video:codec_name',
            'video_codec': 'video:codec_name',
            'video_bitrate': 'video:bit_rate',
            'audio_codec': 'audio:codec_name',
            'audio_bitrate': 'audio:bit_rate',
        }

class XMPKeywordsParser(BaseMetadataParser):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_title(self):
        return "XMP Keywords"


    def get_initial_data(self):
        return {
            'media_type': 'image',
            'parser': 'XMP Keywords'
        }

    def check_xmpmetadata(self):
        '''Checking if the file has x:xmpmeta tag.
        
        We are reading the first 1000 lines of the file and 512 bytes of each line.
        It will return True if there is x:xmpemeta tag in the file. False otherwise.
        '''
        path = self.kwargs.get("path")
        cnt = 0
        f = open(path, "rb")
        while True:
            line = f.readline(512)
            if not line:
                break
            cnt += 1
            if cnt > 1000:
                return False
            line = line.strip()
            if line.startswith( "<x:xmpmeta"):
                return True
        f.close()
        return False

    def get_metadata(self):
        '''Extract Adobe Lightroom XMP metadata.
        
        First, check if the xmpmeta tag is in the file.
        If not, return None.
        If there is, read the data, and extract the keywords.
        Return an array of keywords in lower case.
        '''

        path = self.kwargs.get("path")

        if not self.check_xmpmetadata():
            return {"keywords": ""}

        f = open(path, "rb")

        lines = []
        lines.append( '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>''')

        start = False

        while True:

            line = f.readline()

            # this is just in case
            if not line:
                break

            line = line.strip()

            if not start:
                if line.startswith( "<x:xmpmeta"):
                    start = True
                    lines.append(line)
                continue


            if line.startswith("</x:xmpmeta>"):
                lines.append(line)
                break

            lines.append(line)

        if len(lines) > 1:
            doc = " ".join(lines)
            doc = doc.replace("dc:", "")
            doc = doc.replace("rdf:", "")

            xml = Xml()
            xml.read_string(doc)

            nodes = xml.get_nodes("//subject//li")

            keywords = [x.text.lower() for x in nodes]

            return {"keywords": " ".join(keywords)}
        else:
            return {"keywords": ""}


# DEPRECATED: use python one
class IPTCMetadataParserX(BaseMetadataParser):
    '''Grab IPTC data from files. This requires use of exif metadata extractor.
    Basically read xmp metadata of a file and consider IPTC data points'''

    
    def get_iptc_keywords(self, path, parser_path = ""):
        '''Extracts IPTC metadata given a path to an image.
        Returns IPTC metadata as a dictionary'''

        ret = {} # dictionary with metadata to be returned

        # determine file format of image path
        type_start = path.rfind(".")
        image_type = path[type_start:]

        # check if exiftool exists first:
        from distutils.spawn import find_executable
        if os.name == "nt":
            exiftool_exists = find_executable("exiftool", path=parser_path)
        else:
            exiftool_exists = find_executable("exiftool")
        
        if not exiftool_exists:
            print "WARNING: exiftool does not exist at path %s" %(parser_path)
            return "WARNING: exiftool does not exist at path %s" %(parser_path)

        # get IPTC data from exiftool

        # For windows, use parser_path for exiftool.exe
        if os.name == "nt" and parser_path:
            exif_process = subprocess.Popen([parser_path,'-ext', 'dng', '-xmp', '-b', path], shell=False, stdout=subprocess.PIPE)
            exif_process = subprocess.Popen([parser_path,'-ext', image_type, '-xmp', '-b', path], shell=False, stdout=subprocess.PIPE)
 
        # For linux, use command-line exiftool
        else:
            exif_process = subprocess.Popen(['exiftool','-ext', 'dng', '-xmp', '-b', path], shell=False, stdout=subprocess.PIPE)
            exif_process = subprocess.Popen(['exiftool','-ext', image_type, '-xmp', '-b', path], shell=False, stdout=subprocess.PIPE)

        ret_val, error = exif_process.communicate()

        if error:
            return ret

        # parse and clean the metadata
        keyword_values = self.get_keywords_metadata_from_xmp(ret_val)
        description_values = self.get_description_metadata_from_xmp(ret_val)

        # add keywords metadata to the dictionary to be returned: "ret"
        ret["Keywords"] = keyword_values
        ret["Description"] = description_values

        return ret


    
    def get_keywords_metadata_from_xmp(self, xmp_data):
        '''Given XMP data as a string, parse it for Keywords of IPTC metadata, and
       return it as a string, with values separated by spaces.'''

        keywords_list = []
        
        # find the chunk of data in xmp_data where the keywords reside
        starting_index = xmp_data.find("<dc:subject>")
        end_index = xmp_data.find("</dc:subject>")

        # section of xmp data containing keywords metadata
        dc_subject_str = xmp_data[starting_index:end_index]

        # find all words between tags in the xmp data using regular expression.
        # ie, search for words between <tag>words</tag>
        # Allows newline (\n\r), vertical tab (\f) and form feed (\v) between tags
        keywords_list = re.findall('>[^<\n\r\f\v]*<', dc_subject_str)

        # get rid of the > and < around words in keywords_list
        keywords_list = [ x[1:-1] for x in keywords_list]
 
        # remove empty keywords from list
        keywords_list = [x for x in keywords_list if x and x != ' ']

        return keywords_list


    def get_description_metadata_from_xmp(self, xmp_data):
        '''Given XMP data as a string, retrieve the description.'''

        description_list = []
        
        # find the chunk of data in xmp_data where the description resides
        starting_index = xmp_data.find("<dc:description>")
        end_index = xmp_data.find("</dc:description>")

        # section of xmp data containing description metadata
        dc_subject_str = xmp_data[starting_index:end_index]

        # find all words between tags in the xmp data using regular expression.
        # ie, search for words between <tag>words</tag>
        # Allows newline (\n\r), vertical tab (\f) and form feed (\v) between tags
        description_list = re.findall('>[^<\n\r\f\v]*<', dc_subject_str)

        # get rid of the > and < around words in description_list
        description_list = [ x[1:-1] for x in description_list]
 
        # take the list, and turn it into a string, separated by spaces
        description_list = [x for x in description_list if x and x != ' ']

        return description_list


    def get_metadata(self):
        path = self.kwargs.get("path")

        import subprocess, re

        iptc_data = {} # dictionary to hold iptc data

        # make it an option to extract IPTC data from a file
        if self.kwargs.get("extract_iptc_keywords_only") in ["true", "True", True]:
            # Option to specify where exiftool is.
            parser_path = self.kwargs.get('parser_path')
            if parser_path:
                iptc_data = self.get_iptc_keywords(path, parser_path=parser_path)
            else:
                iptc_data = self.get_iptc_keywords(path)
            return iptc_data




if __name__ == '__main__':
    import sys
    import tacticenv
    parser = FFProbeMetadataParser(path=sys.argv[1])
    metadata = parser.get_metadata()
    from pyasm.common import Common
    Common.pretty_print(metadata)

