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


__all__ = ['BaseAppInfo', 'TacticException', 'Common']

import cStringIO, os, sys, urllib, xmlrpclib, re
from xml.dom.minidom import parseString

from upload_multipart import UploadMultipart

HAS_MD5 = True
try:
    import hashlib
except ImportError:
    import md5
except ImportError:
    HAS_MD5 = False

def get_md5():
    try: 
        import hashlib
        md5_obj = hashlib.md5()
    except ImportError:
        import md5
        md5_obj = md5.new()
    except ImportError:
        md5_obj = None
    return md5_obj


class TacticException(Exception):
    pass


class BaseAppInfo(object):
    '''Holds data in the application session that is fed by the tactic server.
    This is merely used to extract information from the appropriate source.
    Use the "AppEnvironment" classes to access this information
    '''

    def __init__(my, app_name=None):
        my.xmlrpc_server = None
        my.app = None

        my.app_name = app_name
        
        my.sandbox_dir = None
        my.project_code = None
        my.server = None
        my.tmpdir = None
        my.save_dir = None
        my.ticket = None
        my.user = None
        # set this as the singleton
        BaseAppInfo.set(my)

    def get_app_name(my):
        return my.app_name


    def set_up_maya(my, init=False):
        # set up application environment
        from pyasm.application.maya import MayaEnvironment
        MayaEnvironment.set_up(my)


    def set_up_houdini(my, port=None):
        from pyasm.application.houdini import HoudiniEnvironment
        HoudiniEnvironment.set_up(my)


    def set_up_xsi(my, xsi, tool):
        # set up application environment
        from pyasm.application.xsi import XSIEnvironment
        XSIEnvironment.set_up(my, xsi, tool)


    def set_up_flash(my):
        # set up application environment
        from pyasm.application.flash import FlashEnvironment
        my.env = FlashEnvironment.set_up(my)







    def close_houdini(my):
        '''close the socket to houdini'''
        socket = my.app.get_socket()
        if socket:
            socket.close()


    def close_xsi(my):
        '''
        var prefs = Application.Preferences;
        var originalsetting = prefs.GetPreferenceValue( "scripting.cmdlog" );

        // Disable command logging
        if ( !originalsetting ) { 
           prefs.SetPreferenceValue( "scripting.cmdlog", false ); 
        }

        //
        // Do your stuff
        //

        // Restore logging setting to the way it was
        prefs.SetPreferenceValue( "scripting.cmdlog", originalsetting );
        '''
        pass
        


    def get_builder(my):
        if my.app_name == "houdini":
            from pyasm.application.houdini import HoudiniBuilder
            return HoudiniBuilder()
        elif my.app_name == "maya":
            from pyasm.application.maya import MayaBuilder
            return MayaBuilder()
        elif my.app_name == "xsi":
            from pyasm.application.xsi import XSIBuilder
            return XSIBuilder()
        elif my.app_name == "flash":
            from pyasm.application.flash import FlashBuilder
            return FlashBuilder()
        

    def get_app_implementation(my):
        if my.app_name == "houdini":
            from pyasm.application.houdini import HoudiniImpl
            return HoudiniImpl()
        elif my.app_name == "maya":
            from pyasm.application.maya import MayaImpl
            return MayaImpl()
        elif my.app_name == "xsi":
            from pyasm.application.xsi import XSIImpl
            return XSIImpl()
        


    def get_app(my):
        return my.app

    def get_ticket(my):
        return my.ticket

    def set_ticket(my, ticket):
        my.ticket = ticket


    def set_user(my, user):
        my.user = user

    def get_user(my):
        return my.user

    def get_project_code(my):
        return my.project_code

    def get_server(my):
        return my.server

    def set_tmpdir(my, tmpdir):
        from app_environment import AppEnvironment
        env = AppEnvironment.get()
        env.set_tmpdir(tmpdir)
        my.tmpdir = tmpdir

    def get_tmpdir(my):
        return my.tmpdir

    def get_save_dir(my):
        impl = my.get_app_implementation()

        return impl.get_save_dir()

    def get_sandbox_dir(my):
        return my.sandbox_dir

    def set_sandbox_dir(my, sandbox_dir):
        my.sandbox_dir = sandbox_dir


    def get_xmlrpc_server(my):
        raise Exception("Not implemented")


    def report_msg(my, label, msg):
        '''this is for debugging only'''
        path = "%s/msg.txt" % my.get_tmpdir()
        file = open(path, "a")
        
        msg = '%s: %s\n' %(label, msg)

        file.write(msg)
        file.close()

    def report_error(my, exception):
        print "Error: ", exception
        path = "%s/error.txt" % my.get_tmpdir()
        file = open(path, "w")
        
        msg = str(exception)

        file.write(msg)
        file.close()
        my.upload(path)
        
    def report_warning(my, label, warning, upload=False, type=''):
        print "warning: ", warning
        path = "%s/warning.txt" % my.get_tmpdir()
        if label and warning:
            file = open(path, "a")
            
            msg = '%s||%s||%s\n' %(label, warning, type)

            file.write(msg)
            file.close()
        
        if upload and os.path.exists(path):
            my.upload(path)


    def get_upload_server(my):
        return None


    def upload(my, from_path):

        print "DEPRECATED"
        print "uploading: ", from_path

        ticket = my.get_ticket()
        upload_server = my.get_upload_server()

        upload = UploadMultipart()
        upload.set_ticket(ticket)
        upload.set_upload_server(upload_server)
        upload.execute(from_path)

        return


        '''
        file = open(from_path, "rb")
        buffer_size = 1024*1024
        iteration = 0
        while 1:
            contents = file.read(buffer_size)
            if contents == "":
                break

            # create a buffer with the contents
            buffer = cStringIO.StringIO()
            buffer.write("file=%s\n" % from_path)
            if iteration == 0:
                buffer.write("action=create\n")
            else:
                buffer.write("action=append\n")

            ticket = my.get_ticket()
            buffer.write("ticket=%s\n" % ticket)
            buffer.write("EOF\n")
            buffer.write(contents)

            f = urllib.urlopen(upload_server, buffer.getvalue() )
            response = f.readlines()
            f.close()
            print response

            iteration += 1

        file.close()
        '''





    def download(my, url, to_dir="", md5_checksum=""):

        print "DEPRECATED"

        filename = os.path.basename(url)

        # download to the current project
        if not to_dir:
            to_dir = my.get_tmpdir()

        # make sure the directory exists
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        to_path = "%s/%s" % (to_dir, filename)


        # check if this file is already downloaded.  if so, skip
        if os.path.exists(to_path):
            # if it exists, check the MD5 checksum
            if md5_checksum:
                f = open(to_path, 'rb')
                CHUNK = 1024*1024
                m = get_md5()
                while 1:
                    chunk = f.read(CHUNK)
                    if not chunk:
                        break
                    m.update(chunk)
                f.close()
                md5_local = m.hexdigest()

                # only return if the md5 checksums are the same
                if md5_checksum == md5_local:
                    print "skipping '%s', already exists" % to_path
                    return to_path

        f = urllib.urlopen(url)
        file = open(to_path, "wb")
        file.write( f.read() )
        file.close()
        f.close()

        """
        print "starting download"
        try:
            file = open(to_path, "wb")
            req = urllib2.urlopen(url)
            try:
                while True:
                    buffer = req.read(1024*100)
                    print "read: ", len(buffer)
                    if not buffer:
                        break
                    file.write( buffer )
            finally:
                print "closing ...."
                req.close()
                file.close()
        except urllib2.URLError, e:
            raise Exception('%s - %s' % (e,url))

        print "... done download"
        """


        return to_path




    __object = None
    def get():
        return BaseAppInfo.__object
    get = staticmethod(get)


    def set(info):
        BaseAppInfo.__object = info
    set = staticmethod(set)





class Common(object):

    def get_filesystem_name(name):
        new_name = re.sub(r'/|\||:|\?|=|\s', '_', name)
        filename_base, ext = os.path.splitext(new_name)
        ext = ext.lower()
        new_name = "%s%s" % (filename_base, ext)
        return new_name
    get_filesystem_name = staticmethod(get_filesystem_name)

    def set_sys_env(name, value):
        '''seting windows system environment variable, without broadcasting'''
        if os.name == 'nt':
            try:
                import _winreg
                x= _winreg.ConnectRegistry(None,_winreg.HKEY_LOCAL_MACHINE)
                y=_winreg.OpenKey(x,\
                 r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",\
                 0,_winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(y, name ,0,_winreg.REG_EXPAND_SZ, value)
                _winreg.CloseKey(y)
                _winreg.CloseKey(x)
            except OSError, e:
                print "Registry Key not found."
                return 
            except WindowsError, e:
                print str(e)
                return
        
            # This part is too error-prone, like fail to import win32gui
            '''
            # broadcast
            HWND_BROADCAST      = 0xFFFF
            WM_SETTINGCHANGE    = 0x001A
            SMTO_ABORTIFHUNG    = 0x0002
            sParam              = "Environment"

            import win32gui
            res1, res2 = win32gui.SendMessageTimeout(HWND_BROADCAST,\
                    WM_SETTINGCHANGE, 0, sParam, SMTO_ABORTIFHUNG, 100)
            if  not res1:
                print ("result %s, %s from SendMessageTimeout" % (bool(res1), res2))
            '''
    set_sys_env = staticmethod(set_sys_env)

    def get_option_dict(options_str):
        '''get an option dict'''
        options = {}
        exprs = options_str.split("|")
        for expr in exprs:
            name, value = expr.split("=")
            options[name] = value
        return options
    get_option_dict = staticmethod(get_option_dict)

    def get_option_str(option_dict):
        '''get the option str given a dict'''
        option_list = []
        for key, value in option_dict.items():
            option_list.append('%s=%s' %(key, value))
        return '|'.join(option_list)
    get_option_str = staticmethod(get_option_str)

    def get_file_range(file_range):
        ''' build a file range tuple from a string'''
        frame_by = 1
        if file_range.find("/") != -1:
            file_range, frame_by = file_range.split("/")
            
        frame_start, frame_end = file_range.split("-")
        frame_start = int(frame_start)
        frame_end = int(frame_end)
        frame_by = int(frame_by)

        return frame_start, frame_end, frame_by
    get_file_range = staticmethod(get_file_range)

    def is_file_group(path):
        pat = re.compile('\.(#+)\.')
        if pat.search(path):
            return True
        return False
    is_file_group = staticmethod(is_file_group)

    def expand_paths( file_path, file_range ):
        '''expands the file paths, replacing # as specified in the file_range'''
        #TODO: expand paths somehow if file_range is empty
        file_paths = []
        
        # frame_by is not really used here yet
        frame_by = 1
        if file_range.find("/") != -1:
            file_range, frame_by = file_range.split("/")
        frame_start, frame_end = file_range.split("-")
        frame_start = int(frame_start)
        frame_end = int(frame_end)
        frame_by = int(frame_by)

        # find out the number of #'s in the path
        padding = len( file_path[file_path.index('#'):file_path.rindex('#')] )+1

        for i in range(frame_start, frame_end+1, frame_by):
            expanded = file_path.replace( '#'*padding, str(i).zfill(padding) )
            file_paths.append(expanded)

        return file_paths
    expand_paths = staticmethod(expand_paths)

    def get_md5(path):
        '''get md5 checksum'''
        try:
            f = open(path, 'rb')
            CHUNK = 1024*1024
            m = get_md5()
            while 1:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                m.update(chunk)
            md5_checksum = m.hexdigest()
            f.close()
            return md5_checksum
        except IOError, e:
            print "WARNING: error getting md5 on [%s]: " % path, e
            return None
    get_md5 = staticmethod(get_md5)  

    def get_unique_list(list):
        ''' get a unique list, order preserving'''
        seen = set()
        return [ x for x in list if x not in seen and not seen.add(x)]
    get_unique_list = staticmethod(get_unique_list)
    
