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

__all__ = ['AppEnvironment', 'AppException']

import os, urllib

# for whatever reason, Maya 2008 does not ship with md5
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

gl = globals()
lc = locals()



from upload_multipart import UploadMultipart
from base_app_info import TacticException


class AppException(Exception):
    pass

class AppEnvironment(object):
    '''The applicaton environment.  All information about the
    environment can be extracted from here.  If necessary, it will delegate
    to the "info" object to extract the real source of the information'''

    def __init__(self):
        self.app = None
        self.tmpdir = None
        self.ticket = None
        self.upload_server = None
        self.xmlrpc_server = None
        self.user = None
        self.project_code = None
        self.server = None
        self.info = None

    def set_info(self, info):
        self.info = info

        # extract information from info object
        self.tmpdir = info.get_tmpdir()
        self.sandbox_dir = info.get_sandbox_dir()
        self.ticket = info.get_ticket()
        self.upload_server = info.get_upload_server()
        self.xmlrpc_server = info.get_xmlrpc_server()
        self.user = info.get_user()
        self.project_code = info.get_project_code() 
        self.server = info.get_server()
        self.save_dir = None

    def get_info(self):
        return self.info

    def set_app(self, app):
        '''set the maya object'''
        self.app = app

    def get_app(self):
        return self.app


    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

        # make sure tmpdir exists
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)

    def get_tmpdir(self):
        return self.tmpdir

    def set_save_dir(self, save_dir):
        self.save_dir = save_dir

    def get_save_dir(self):
        # by default it is the tmpdir
        return self.tmpdir

    def set_ticket(self, ticket):
        self.ticket = ticket

    def get_ticket(self):
        return self.ticket

 
    def set_sandbox_dir(self, sandbox_dir):
        self.sandbox_dir = sandbox_dir

        # make sure sandbox_dir exists
        if not os.path.exists(self.sandbox_dir):
            try:
                os.makedirs(self.sandbox_dir)
            except Exception, e:
                raise Exception("Cannot create directory '%s'" % self.sandbox_dir)


    def get_sandbox_dir(self):
        return self.sandbox_dir


    def get_upload_server(self):
        return self.upload_server

    def get_xmlrpc_server(self):
        return self.xmlrpc_server


    def get_user(self):
        return self.user

    def get_project_code(self):
        return self.project_code

    def get_server(self):
        return self.server


    def upload(self, from_path):

        print "uploading: ", from_path

        ticket = self.get_ticket()
        upload_server = self.get_upload_server()

        upload = UploadMultipart()
        upload.set_ticket(ticket)
        upload.set_upload_server(upload_server)
        upload.execute(from_path)

        return



    def download(self, url, to_dir="", md5_checksum=""):

        filename = os.path.basename(url)

        # download to temp_dir
        if not to_dir:
            to_dir = self.get_tmpdir()

        # make sure the directory exists
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        to_path = "%s/%s" % (to_dir, filename)


        # check if this file is already downloaded.  if so, skip
        if os.path.exists(to_path):
            # if it exists, check the MD5 checksum
            if HAS_MD5:
                if md5_checksum:
                    if self._md5_check(to_path, md5_checksum):
                        print "skipping '%s', already exists" % to_path
                        return to_path
                else:
                    # always download if no md5_checksum available
                    pass

            else:
                # if no md5 library is available, then existence is enough
                print "skipping '%s', already exists" % to_path
                return to_path

        f = urllib.urlopen(url)
        file = open(to_path, "wb")
        file.write( f.read() )
        file.close()
        f.close()

        # check for downloaded file
        # COMMENTED OUT for now since it does not work well with icons
        #if md5_checksum and not self._md5_check(to_path, md5_checksum):
        #    raise TacticException('Downloaded file [%s] in local repo failed md5 check. This file may be missing on the server or corrupted.'%to_path)

        """
        print "starting download"
        try:
            import urllib2
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


    def create_from_class_path(class_path, args=[]):
        '''dynamically creats an object from a string class path.'''
        assert class_path 
        parts = class_path.split(".")
        module_name = ".".join(parts[0:len(parts)-1])
        class_name = parts[len(parts)-1]
        exec( "from %s import %s" % (module_name,class_name), gl, lc )
        if args:
            object = eval("%s(%s)" % (class_name, args) )
        else:
            object = eval("%s()" % (class_name) )
        return object
    create_from_class_path = staticmethod(create_from_class_path)
 

    def _md5_check(self, to_path, md5_checksum):
        if not HAS_MD5:
            return True

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
            return True
    
    app_env = None
    def get(cls):
        # Don't need container, because Maya will never be launched from
        # a multithreaded application server.  A process will always be
        # forked
        if AppEnvironment.app_env == None:
            AppEnvironment.app_env = cls()
        return AppEnvironment.app_env

    get = classmethod(get)


