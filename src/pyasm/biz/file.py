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

__all__ = ["FileException", "File", "FileAccess", "IconCreator", "FileGroup", "FileRange"]

from pyasm.common import Common, Xml, TacticException, Environment, System, Config
from pyasm.search import *
from project import Project
from subprocess import Popen, PIPE

import sys, os, string, re, stat, glob


try:
    #import Image
    from PIL import Image
    # Test to see if imaging actually works
    import _imaging
    HAS_PIL = True
except:
    HAS_PIL = False
    try:
        import Image
        # Test to see if imaging actually works
        import _imaging
        HAS_PIL = True
    except:
        HAS_PIL = False


# check if imagemagick is installed, and find exe if possible
convert_exe = ''
HAS_IMAGE_MAGICK = False
if os.name == "nt":
    # prefer direct exe to not confuse with other convert.exe present on nt systems
    convert_exe_list = glob.glob('C:\\Program Files\\ImageMagick*')
    for exe in convert_exe_list:
        try:
            convert_process = Popen(['%s\\convert.exe'%exe,'-version'], stdout=PIPE, stderr=PIPE)
            convert_return,convert_err = convert_process.communicate()
            if 'ImageMagick' in convert_return:
                convert_exe = '%s\\convert.exe'%exe
                HAS_IMAGE_MAGICK = True
        except:
            print "Running %s failed" %exe
    if not convert_exe_list:
        # IM might not be in Program Files but may still be in PATH
        try:
            convert_process = Popen(['convert','-version'], stdout=PIPE, stderr=PIPE)
            convert_return,convert_err = convert_process.communicate()
            if 'ImageMagick' in convert_return:
                convert_exe = 'convert'
                HAS_IMAGE_MAGICK = True
        except:
            pass
else:
    # in other systems (e.g. unix) 'convert' is expected to be in PATH
    try:    
        convert_process = Popen(['convert','-version'], stdout=PIPE, stderr=PIPE)
        convert_return,convert_err = convert_process.communicate()        
        if 'ImageMagick' in convert_return:
            convert_exe = 'convert'
            HAS_IMAGE_MAGICK = True
    except:
        pass

if Common.which("ffprobe"):
    HAS_FFMPEG = True
else:
    HAS_FFMPEG = False



import subprocess

class FileException(TacticException):
    pass


class File(SObject):

    NORMAL_EXT = ['max','ma','xls' ,'xlsx', 'doc', 'docx','txt', 'rtf', 'odt','fla','psd', 'xsi', 'scn', 'hip', 'xml','eani','pdf', 'fbx',
            'gz', 'zip', 'rar',
            'ini', 'db', 'py', 'pyd', 'spt'
    ]

    VIDEO_EXT = ['mov','wmv','mpg','mpeg','m1v','m2v','mp2','mp4','mpa','mpe','mp4','wma','asf','asx','avi','wax', 
                'wm','wvx','ogg','webm','mkv','m4v','mxf','f4v','rmvb']

    IMAGE_EXT = ['jpg','png','tif','tiff','gif','dds','dcm']
                



    SEARCH_TYPE = "sthpw/file"
    BASE_TYPE_SEQ = "sequence"
    BASE_TYPE_DIR = "directory"
    BASE_TYPE_FILE = "file"



    def get_code(my):
        return my.get_value("code")

    def get_file_name(my):
        return my.get_value("file_name")

    def get_file_range(my):
        return my.get_value("file_range")

    def get_type(my):
        return my.get_value("type")


    def get_media_type_by_path(cls, path):
        tmp, ext = os.path.splitext(path)
        ext = ext.lstrip(".")
        ext = ext.lower()
        if ext in File.VIDEO_EXT:
            return "video"
        elif ext in File.NORMAL_EXT:
            return "document"
        else:
            return "image"
    get_media_type_by_path = classmethod(get_media_type_by_path)


    def get_sobject(my):
        '''get the sobject associated with this file'''
        search = Search(my.get_value("search_type"))
        search.add_id_filter(my.get_value("search_id"))
        sobject = search.get_sobject()
        return sobject

    def get_full_file_name(my):
        '''Gets the full file name.  This is the same as get_file_name'''
        return my.get_file_name()


    def get_lib_dir(my,snapshot=None):
        '''go through the stored snapshot_code to get the actual path'''
        code = my.get_value("snapshot_code")
        from snapshot import Snapshot
        snapshot = Snapshot.get_by_code(code)
        return snapshot.get_lib_dir()

    def get_env_dir(my,snapshot=None):
        '''go through the stored snapshot_code to get the actual path'''
        code = my.get_value("snapshot_code")
        from snapshot import Snapshot
        snapshot = Snapshot.get_by_code(code)
        return snapshot.get_env_dir()

    def get_web_dir(my,snapshot=None):
        '''go through the stored snapshot_code to get the actual path'''
        code = my.get_value("snapshot_code")
        from snapshot import Snapshot
        snapshot = Snapshot.get_by_code(code)
        return snapshot.get_web_dir()



    def get_lib_path(my):
        filename = my.get_full_file_name()
        return "%s/%s" % (my.get_lib_dir(), filename)

    def get_env_path(my):
        '''path beginning with $TACTIC_ASSET_DIR'''
        filename = my.get_full_file_name()
        return "%s/%s" % (my.get_env_dir(), filename)

    def get_web_path(my):
        filename = my.get_full_file_name()
        return "%s/%s" % (my.get_web_dir(), filename)




    ##################
    # Static Methods
    ##################
    """
    # DEPRERECATED
    PADDING = 10

    # DEPRERECATED
    def add_file_code(file_path, file_code):
        ext = ".".join( File.get_extensions(file_path) )
        padded_id = str(file_code).zfill(File.PADDING)
        file_path = file_path.replace(".%s" % ext, "_%s.%s" % (padded_id, ext) )
        return file_path
    add_file_code = staticmethod(add_file_code)


    # DEPRERECATED
    def remove_file_code(file_path):
        new_path = re.compile(r'_(\w{%s})\.' % File.PADDING).sub(".", file_path)
        return new_path
    remove_file_code = staticmethod(remove_file_code)


    # DEPRERECATED
    def extract_file_code(file_path):
        p = re.compile(r'_(\w{%s})\.' % File.PADDING)
        m = p.search(file_path)
        if not m:
            return 0
        groups = m.groups()
        if not groups:
            return 0
        else:
            file_code = groups[0]

            # make sure there are only alpha/numberic characters
            if file_code.find("_") != -1:
                return 0

            # make sure the first 3 are numeric
            if not re.match('^\d{3}\w+$', file_code):
                return 0


            # strip out the leading zeros
            return file_code.lstrip("0")

    extract_file_code = staticmethod(extract_file_code)


    # DEPRERECATED
    def extract_file_path(file_path):
        '''return file path without the unique id'''
        p = re.compile(r'_(\w{%s})\.' % File.PADDING)
        m = p.search(file_path)
        if not m:
            return file_path

        groups = m.groups()
        if not groups:
            return file_path
        else:
            new_path = file_path.replace("_%s" % groups[0], "")
            return new_path
    extract_file_path = staticmethod(extract_file_path)



    # DEPRERECATED
    def has_file_code(file_path):
        file_code = File.extract_file_code(file_path)
        if file_code == 0:
            return False
        else:
            return True
    has_file_code = staticmethod(has_file_code)
    """


    def get_extension(file_path):
        '''get only the final extension'''
        parts = os.path.basename(file_path).split(".")
        ext = parts[len(parts)-1]
        return ext
    get_extension = staticmethod(get_extension)


    def get_extensions(file_path):
        '''get all of the extensions after the first .'''
        parts = os.path.basename(file_path).split(".")
        ext = parts[1:len(parts)]
        return ext
    get_extensions = staticmethod(get_extensions)


    def get_by_snapshot(cls, snapshot, file_type=None):
        xml = snapshot.get_xml_value("snapshot")
        file_codes = xml.get_values("snapshot/file/@file_code")
        search = Search( cls.SEARCH_TYPE)
        search.add_filters("code", file_codes)
        if file_type:
            search.add_filter("type", file_type)
        return search.get_sobjects()
    get_by_snapshot = classmethod(get_by_snapshot)



    def get_by_filename(cls, filename, skip_id=None, padding=0):
        search = Search(cls.SEARCH_TYPE)

        # if this is a file range then convert file name to padding
        # FIXME: need some way to know what and where the padding is
        if padding:
            filename = re.sub("(.*\.)(\d+)", r"\1####", filename)

        search.add_filter("file_name", filename)
        project_code = Project.get_project_code()
        search.add_filter("project_code", project_code)
        if skip_id:
            search.add_where('id != %s'%skip_id)
        return search.get_sobject()
    get_by_filename = classmethod(get_by_filename)



    def get_by_snapshots(cls, snapshots, file_type=None):
        all_file_codes = []
        for snapshot in snapshots:
            xml = snapshot.get_xml_value("snapshot")
            file_codes = xml.get_values("snapshot/file/@file_code")
            all_file_codes.extend(file_codes)

        search = Search( cls.SEARCH_TYPE)
        search.add_filters("code", all_file_codes)
        if file_type:
            search.add_filter("type", file_type)
        files = search.get_sobjects()

        # cache these
        for file in files:
            key = "%s|%s" % (file.get_search_type(),file.get_code())
            SObject.cache_sobject(key, file)

        return files
    get_by_snapshots = classmethod(get_by_snapshots)


    # DEPRECATED
    """
    def get_by_path(path):
        file_code = File.extract_file_code(path)
        if file_code == 0:
            return None

        search = Search(File.SEARCH_TYPE)
        search.add_id_filter(file_code)
        file = search.get_sobject()
        return file
    get_by_path = staticmethod(get_by_path)
    """


    def get_by_path(path):
        asset_dir = Environment.get_asset_dir()
        path = path.replace("%s/" % asset_dir, "")
        relative_dir = os.path.dirname(path)
        file_name = os.path.basename(path)

        # NOTE: this does not work with base_dir_alias

        search = Search("sthpw/file")
        search.add_filter("relative_dir", relative_dir)
        search.add_filter("file_name", file_name)
        sobject = search.get_sobject()
        return sobject

    get_by_path = staticmethod(get_by_path)



    def create( file_path, search_type, search_id, file_type=None, requires_file=True, st_size=None, repo_type=None, search_code = None):

        exists = os.path.exists(file_path)
        isdir = os.path.isdir(file_path)

        if requires_file and not os.path.exists(file_path):
            raise FileException("File '%s' does not exist" % file_path)

        file_name = os.path.basename(file_path)

        file = File(File.SEARCH_TYPE)
        file.set_value("file_name", file_name)
        file.set_value("search_type", search_type)
        if search_code:
            file.set_value("search_code", search_code)
        
        # MongoDb
        if search_id and isinstance(search_id, int):
            file.set_value("search_id", search_id)


        if file_type:
            file.set_value("type", file_type)

        if isdir:
            file.set_value("base_type", File.BASE_TYPE_DIR)
        else:
            file.set_value("base_type", File.BASE_TYPE_FILE)

        project = Project.get()
        
        file.set_value("project_code", project.get_code())
    
        if exists:
            if isdir:
                dir_info = Common.get_dir_info(file_path)
                size = dir_info.get("size")
                file.set_value("st_size", size)
            else:
                from stat import ST_SIZE
                size =  os.stat(file_path)[ST_SIZE]
                file.set_value("st_size", size)
        elif st_size != None:
            file.set_value("st_size", st_size)


        if repo_type:
            file.set_value("repo_type", repo_type)


        file.commit()
        return file
    create = staticmethod(create)



    def makedirs(dir, mode=None):
        '''wrapper to mkdirs in case it ever needs to be overridden'''
        print "DEPRECATED: use System().makedirs()"
        return System().makedirs(dir,mode)
    makedirs = staticmethod(makedirs)


    def get_filesystem_name(name, strict=True):
        '''takes a name and converts it to a name that can be saved in
        the filesystem.'''
        filename = name

        filename = filename.replace("/", "__")
        filename = filename.replace("|", "__")
        filename = filename.replace(":", "__")
        filename = filename.replace("?", "__")
        filename = filename.replace("=", "__")

        if strict:
            filename = filename.replace(" ", "_")

            filename_base, ext = os.path.splitext(filename)
            ext = string.lower(ext)
            filename = "%s%s" % (filename_base, ext)

        return filename
    get_filesystem_name = staticmethod(get_filesystem_name)


    def process_file_path(file_path):
        '''makes a file path completely kosher with the file system. Only do it on basename or it would remove the : from C:/'''

        return Common.get_filesystem_name(file_path)

    process_file_path = staticmethod(process_file_path)

    
    def get_md5(path):
        '''get md5 checksum'''
        py_exec = Config.get_value("services", "python")
        if not py_exec:
            py_exec = "python"

        if isinstance(path, unicode):
            path = path.encode('utf-8')
        popen =  subprocess.Popen([py_exec, '%s/src/bin/get_md5.py'%Environment.get_install_dir(), path], shell=False, stdout=subprocess.PIPE)
        popen.wait()
        output = ''
        value = popen.communicate()
        if value:
            output = value[0].strip()
            if not output:
                err = value[1]
                print err
            
        return output
       
    get_md5 = staticmethod(get_md5)

    def is_file_group(file_path):
        '''returns True if it is a file group'''
        return not (file_path.find('#') == -1 and file_path.find('%') == -1)
    is_file_group = staticmethod(is_file_group)

class FileAccess(SObject):

    SEARCH_TYPE = "sthpw/file_access"

    def create(file):

        file_code = file.get_code()
        file_access = FileAccess(FileAccess.SEARCH_TYPE)
        file_access.set_value("file_code", file_code)

        security = WebContainer.get_security()
        user = security.get_user_name()
        file_access.set_value("login", user)

        file_access.commit()

        return file_access

    create = staticmethod(create)
       



class IconCreator(object):
    '''Utility class that creates icons of an image or document in the
    same directory as the image'''

    def __init__(my, file_path):
        my.file_path = file_path

        # check if it exists
        if not os.path.exists( file_path ):
            raise FileException( \
                "Error: file [%s] does not exist" % my.file_path )

        my.tmp_dir = os.path.dirname(file_path)

        my.icon_path = None
        my.web_path = None

        my.texture_mode = False
        my.icon_mode = False



    def set_texture_mode(my):
        '''texture mode down res is 1/4 size'''
        my.texture_mode = True

    def set_icon_mode(my):
        '''icon mode down res is 1/4 size'''
        my.icon_mode = True
    
    def get_icon_path(my):
        return my.icon_path

    def get_web_path(my):
        return my.web_path


    
    def create_icons(my):
        my.execute()

    def execute(my):

        # check file name
        file_name = os.path.basename(my.file_path)

        ext = File.get_extension(file_name)
        type = string.lower(ext)


        if type == "pdf":
            my._process_pdf( file_name )
        elif type in File.NORMAL_EXT:
            # skip icon generation for normal or video files
            pass
        elif type in File.VIDEO_EXT:
            try:
                my._process_video( file_name )
            except IOError, e:
                '''This is an unknown file type.  Do nothing and except as a
                file'''
                print "WARNING: ", e.__str__()
                Environment.add_warning("Unknown file type", e.__str__())
        else:
            # assume it is an image
            try:
                my._process_image( file_name )
            except IOError, e:
                '''This is an unknown file type.  Do nothing and except as a
                file'''
                print "WARNING: ", e.__str__()
                Environment.add_warning("Unknown file type", e.__str__())





    def _process_pdf(my, file_name):

        base, ext = os.path.splitext(file_name)

        icon_file_name = base + "_icon.png"
        tmp_icon_path = "%s/%s" % (my.tmp_dir, icon_file_name)

        if sys.platform == 'darwin':
            return
        else:
            if not Common.which("convert"):
                return
            try:
                my.file_path = my.file_path.encode('utf-8')
                import shlex, subprocess
                subprocess.call(['convert', '-geometry','80','-raise','2x2','%s[0]'%my.file_path,\
                        "%s"%tmp_icon_path]) 
            except Exception, e:
                print "Error extracting from pdf [%s]" % e
                return


        # check that it actually got created
        if os.path.exists(tmp_icon_path):
            my.icon_path = tmp_icon_path
        else:
            print "Warning: [%s] did not get created from pdf" % tmp_icon_path


    def get_web_file_size(my):
        from pyasm.prod.biz import ProdSetting
        web_file_size = ProdSetting.get_value_by_key('web_file_size')
        thumb_size = (640, 480)
        if web_file_size:
            parts = re.split('[\Wx]+', web_file_size)
            
            thumb_size = (640, 480)
            if len(parts) == 2:
                try:
                    thumb_size = (int(parts[0]), int(parts[1]))
                except ValueError:
                    thumb_size = (640, 480)

        return thumb_size

    def _process_video(my, file_name):
        ffmpeg = Common.which("ffmpeg")
        if not ffmpeg:
            return

        thumb_web_size = my.get_web_file_size()
        thumb_icon_size = (120, 100)

        exts = File.get_extensions(file_name)

        base, ext = os.path.splitext(file_name)
        icon_file_name = "%s_icon.png" % base
        web_file_name = "%s_web.jpg" % base

        tmp_icon_path = "%s/%s" % (my.tmp_dir, icon_file_name)
        tmp_web_path = "%s/%s" % (my.tmp_dir, web_file_name)

        #cmd = '''"%s" -i "%s" -r 1 -ss 00:00:01 -t 1 -s %sx%s -vframes 1 "%s"''' % (ffmpeg, my.file_path, thumb_web_size[0], thumb_web_size[1], tmp_web_path)
        #os.system(cmd)

        import subprocess
        try:
            subprocess.call([ffmpeg, '-i', my.file_path, "-y", "-ss", "00:00:01","-t","1",\
                    "-s","%sx%s"%(thumb_web_size[0], thumb_web_size[1]),"-vframes","1","-f","image2", tmp_web_path])
            
            if os.path.exists(tmp_web_path):
                my.web_path = tmp_web_path
            else:
                my.web_path = None

        except Exception, e:
            Environment.add_warning("Could not process file", \
                    "%s - %s" % (my.file_path, e.__str__()))
            pass
           
        try:
            subprocess.call([ffmpeg, '-i', my.file_path, "-y", "-ss", "00:00:01","-t","1",\
                    "-s","%sx%s"%(thumb_icon_size[0], thumb_icon_size[1]),"-vframes","1","-f","image2", tmp_icon_path])
            
            if os.path.exists(tmp_icon_path):
                my.icon_path = tmp_icon_path
            else:
                my.icon_path = None

        except Exception, e:
            Environment.add_warning("Could not process file", \
                    "%s - %s" % (my.file_path, e.__str__()))
            pass

    def _process_image(my, file_name):

        base, ext = os.path.splitext(file_name)

        # get all of the extensions
        exts = File.get_extensions(file_name)
        frame = 0
        if len(exts) == 2:
            try:
                frame = int(exts[0])
                base = base.replace(".%s" % exts[0], '' )
            except ValueError:
                frame = 0

        if frame:
            icon_file_name = "%s_icon.%s.png" % (base, exts[0])
            web_file_name = "%s_web.%s.jpg" % (base, exts[0])
        else:
            icon_file_name = "%s_icon.png" % base
            web_file_name = "%s_web.jpg" % base

        tmp_icon_path = "%s/%s" % (my.tmp_dir, icon_file_name)
        tmp_web_path = "%s/%s" % (my.tmp_dir, web_file_name)

        # create the web image
        try:
            if my.texture_mode:
                my._resize_texture(my.file_path, tmp_web_path, 0.5)
                my.web_path = tmp_web_path

                # create the icon
                thumb_size = (120,100)
                try:
                    my._resize_image(tmp_web_path, tmp_icon_path, thumb_size)
                except TacticException:
                    my.icon_path = None
                else:
                    my.icon_path = tmp_icon_path
            elif my.icon_mode: # just icon, no web
                # create the icon only
                thumb_size = (120,100)
                try:
                    my._resize_image(my.file_path, tmp_icon_path, thumb_size)
                except TacticException:
                    my.icon_path = None
                else:
                    my.icon_path = tmp_icon_path


            else:
                
                thumb_size = my.get_web_file_size()
                
                try:
                    my._resize_image(my.file_path, tmp_web_path, thumb_size)
                except TacticException:
                    my.web_path = None
                else:
                    my.web_path = tmp_web_path

                # create the icon
                thumb_size = (120,100)
                try:
                    my._resize_image(tmp_web_path, tmp_icon_path, thumb_size)
                except TacticException:
                    my.icon_path = None
                else:
                    my.icon_path = tmp_icon_path

            # check icon file size, reset to none if it is empty
            # TODO: use finally in Python 2.5
            if my.web_path:
                web_path_size = os.stat(my.web_path)[stat.ST_SIZE]
                if not web_path_size:
                    my.web_path = None
            if my.icon_path:
                icon_path_size = os.stat(my.icon_path)[stat.ST_SIZE]
                if not icon_path_size:
                    my.icon_path = None
        except IOError, e:
            Environment.add_warning("Could not process file", \
                "%s - %s" % (my.file_path, e.__str__()))
            my.web_path = None
            my.icon_path = None
        
            

    def _extract_frame(my, large_path, small_path, thumb_size):
        pass


    def _resize_image(my, large_path, small_path, thumb_size):
        try:
            large_path = large_path.encode('utf-8')
            small_path = small_path.encode('utf-8')
            
            if HAS_IMAGE_MAGICK:
                # generate imagemagick command
                convert_cmd = []
                convert_cmd.append(convert_exe)
                # png's and psd's can have multiple layers which need to be flattened to make an accurate thumbnail
                if large_path.lower().endswith('png'):
                    convert_cmd.append('-flatten')
                if large_path.lower().endswith('psd'):
                    large_path += "[0]"
                convert_cmd.extend(['-resize','%sx%s'%(thumb_size[0], thumb_size[1])])

                # FIXME: needs PIL for this ... should use ImageMagick to find image size
                if HAS_PIL:
                    try:
                        im = Image.open(large_path)
                        x,y = im.size
                    except Exception, e:
                        print "WARNING: ", e
                        x = 0
                        y = 0
                    if x < y:
                        # icons become awkward if height is bigger than width
                        # add white background for more reasonable icons
                        convert_cmd.extend(['-background','white'])
                        convert_cmd.extend(['-gravity','center'])
                        convert_cmd.extend(['-extent','%sx%s'%(thumb_size[0], thumb_size[1])])
                convert_cmd.append('%s'%(large_path))
                convert_cmd.append('%s'%(small_path))

                subprocess.call(convert_cmd)

            # if we don't have ImageMagick, use PIL, if installed (in non-mac os systems)
            elif HAS_PIL:
                # use PIL
                # create the thumbnail
                im = Image.open(large_path)

                try:
                    im.seek(1)
                except EOFError:
                    is_animated = False
                else:
                    is_animated = True
                    im.seek(0)
                    im = im.convert('RGB')

                x,y = im.size
                to_ext = "PNG"
                if small_path.lower().endswith('jpg') or small_path.lower().endswith('jpeg'):
                    to_ext = "JPEG"
                if x >= y:
                    im.thumbnail( (thumb_size[0],10000), Image.ANTIALIAS )
                    im.save(small_path, to_ext)
                else:
                    
                    #im.thumbnail( (10000,thumb_size[1]), Image.ANTIALIAS )
                    x,y = im.size

                    # first resize to match this thumb_size
                    base_height = thumb_size[1]
                    h_percent = (base_height/float(y))
                    base_width = int((float(x) * float(h_percent)))
                    im = im.resize((base_width, base_height), Image.ANTIALIAS )

                    # then paste to white image
                    im2 = Image.new( "RGB", thumb_size, (255,255,255) )
                    offset = (thumb_size[0]/2) - (im.size[0]/2)
                    im2.paste(im, (offset,0) )
                    im2.save(small_path, to_ext)

            # if neither IM nor PIL is installed, check if this is a mac system and use sips if so
            elif sys.platform == 'darwin':
                convert_cmd = ['sips', '--resampleWidth', '%s'%thumb_size[0], '--out', small_path, large_path]
                subprocess.call(convert_cmd)
            else:
                raise TacticException('No image manipulation tool installed')
            
        except Exception, e:
            print "Error: ", e

        # after these operations, confirm that the icon has been generated
        if not os.path.exists(small_path):
            raise TacticException('Icon generation failed')


    def _resize_texture(my, large_path, small_path, scale):

        # create the thumbnail
        try:
            im = Image.open(large_path)

            x,y = im.size
            resize = int( float(x) * scale )

            im.thumbnail( (resize,10000), Image.ANTIALIAS )
            im.save(small_path, "PNG")
        except:
            if sys.platform == 'darwin':
                cmd = "sips --resampleWidth 25%% --out %s %s" \
                    % (large_path, small_path)
            else:
                cmd = "convert -resize 25%% %s %s" \
                    % (large_path, small_path)
            os.system(cmd)
            if not os.path.exists(small_path):
                raise



    def add_icons(file_paths):
        new_file_paths=[]
        new_file_types=[]
        
        for file_path in file_paths:

            # create icons and add to the list
            creator = IconCreator(file_path)
            creator.create_icons()

            icon_path = creator.get_icon_path()
            new_file_paths.append(icon_path)
            new_file_types.append("icon")

            web_path = creator.get_web_path()
            new_file_paths.append(web_path)
            new_file_types.append("web")

        return new_file_paths, new_file_types 
    add_icons = staticmethod(add_icons)

    


class FileGroup(File):
    '''Handles groups of files.
    The file paths have the following syntax
    <file>.####
    Where the number signs indicate padding to be replaced by the file_range

    The file_range parameter has the following syntax:
        1-12    Means from files 1-12
    '''

    def check_paths(file_path, file_range):
        ''' check existence of files. this expects a FileRange object'''
        expanded = FileGroup.expand_paths(file_path, file_range)
        for expand in expanded:
            if not System().exists(expand):
                raise FileException("File '%s' does not exist!" % expand)
        return expanded
    check_paths = staticmethod(check_paths)



    def create( file_path, file_range, search_type, search_id, file_type=None ):

        expanded = FileGroup.check_paths(file_path, file_range)

        file_name = os.path.basename(file_path)

        file = File(File.SEARCH_TYPE)
        file.set_value("file_name", file_name)
        file.set_value("search_type", search_type)
        file.set_value("search_id", search_id)

        from stat import ST_SIZE
        total = 0
        for expanded in expanded:
            size =  os.stat(expanded)[ST_SIZE]
            total += size

        project = Project.get()
        file.set_value("project_code", project.get_code())   

        file.set_value("st_size", total)
        file.set_value("file_range", file_range.get_key())
        if file_type:
            file.set_value("type", file_type)
        file.set_value("base_type", File.BASE_TYPE_SEQ)
        file.commit()
       
        return file
    create = staticmethod(create)




    def expand_paths( file_path, file_range ):
        '''expands the file paths, replacing # as specified in the file_range object'''
        file_paths = []
        # frame_by is not really used here yet
        frame_start, frame_end, frame_by  = file_range.get_values()

        # support %0.4d notation
        if file_path.find('#') == -1:
            for i in range(frame_start, frame_end+1, frame_by):
                expanded = file_path % i
                file_paths.append( expanded )
        else: 
            # find out the number of #'s in the path
            padding = len( file_path[file_path.index('#'):file_path.rindex('#')] )+1

            for i in range(frame_start, frame_end+1, frame_by):
                expanded = file_path.replace( '#'*padding, str(i).zfill(padding) )
                file_paths.append(expanded)

        return file_paths

    expand_paths = staticmethod(expand_paths)




    def extract_template_and_range(cls, paths):
        frame = None

        # do we extract a range?
        padding = 0
        for i in range(12,0,-1):
            p = re.compile("(\d{%d,})" % i)
            path = paths[0].replace("\\", "/")
            basename = os.path.basename(path)
            dirname = os.path.dirname(path)
            m = p.search(basename)
            if m:
                frame = m.groups()[0]
                padding = len(frame)
                break

        if not frame:
            padding = 4
            frame = 'x'*padding

        template = basename.replace(frame, '#'*padding)


        frange = []
        last_frame = None

        p = re.compile("(\d{%s})" % padding)
        for path in paths:
            path = path.replace("\\", "/")
            basename = os.path.basename(path)
            m = p.search(basename)
            if m:
                frame = int(m.groups()[0])
            else:
                frame = 0

            # the first one is always added
            if last_frame == None:
                frange.append(frame)
                frange.append('-')
                frange.append(frame)
                last_frame = frame
                continue

            # the next ones are not
            diff = frame - last_frame
            if diff == 1:
                frange[-1] = frame
            else:
                frange.append(frame)
                frange.append('-')
                frange.append(frame)

            last_frame = frame

        template = "%s/%s" % (dirname,template)

        frange = "".join([str(x) for x in frange])

        return template, frange

    extract_template_and_range = classmethod(extract_template_and_range)






class FileRange(object):

    def __init__(my, frame_start=1, frame_end=1, frame_by=1):
        my.frame_start = frame_start
        my.frame_end = frame_end
        my.frame_by = frame_by
        
        assert(isinstance(frame_start, (int)))
        assert(isinstance(frame_end, (int)))
        assert(isinstance(frame_by, (int)))

    def get_frame_by(my):
        return my.frame_by

    def get_frame_start(my):
        return my.frame_start

    def get_frame_end(my):
        return my.frame_end

    def set_frame_by(my, frame_by):
        assert(isinstance(frame_by, (int)))
        my.frame_by = frame_by

  
    def set_duration(my, duration):
        my.frame_start = 1
        my.frame_end = duration

    def get_num_frames(my):
        return (my.frame_end - my.frame_start + 1) / my.frame_by

    def get_key(my):
        return "%s-%s/%s" % (my.frame_start, my.frame_end, my.frame_by)

    def get_display(my):
        if my.frame_by == 1:
            return "%s-%s" % (my.frame_start, my.frame_end)
        else:
            return my.get_key()
        


    def get_values(my):
        return (my.frame_start, my.frame_end, my.frame_by)


    # static method
    def get(file_range):
        ''' build a FileRange obj from a string'''
        frame_by = 1
        if file_range.find("/") != -1:
            file_range, frame_by = file_range.split("/")
    
        tmps = file_range.split("-")
        if len(tmps) > 2:
            raise FileException("Unable to determine file_range [%s]" %file_range)
        frame_start, frame_end = tmps[0], tmps[1]
        frame_start = int(frame_start)
        frame_end = int(frame_end)
        frame_by = int(frame_by)

        return FileRange(frame_start, frame_end, frame_by)
    get = staticmethod(get)
        





