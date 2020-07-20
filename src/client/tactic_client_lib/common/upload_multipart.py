###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
#
#

__all__ = ['UploadMultipart', 'TacticUploadException']

import socket
import base64

try:
    import urlparse
except:
    from urllib import parse as urlparse

try:
    import httplib
except:
    from http import client as httplib


import os, sys

class TacticUploadException(Exception):
    pass

class UploadMultipart(object):
    '''Handles the multipart content type for uploading files.  Will break up
    a file into chunks and upload separately for huge files'''

    def __init__(self):
        self.tries = 0
        self.chunk_size = 10*1024*1024
        self.ticket = None
        self.subdir = None

        self.server_url = None

        self.offset = 0


    def set_offset(self, offset):
        self.offset = offset


    def set_upload_server(self, server_url):
        self.server_url = server_url


    def set_chunk_size(self, size):
        '''set the chunk size of each upload'''
        self.chunk_size = size

    def set_ticket(self, ticket):
        '''set the ticket for security'''
        self.ticket = ticket

    def set_subdir(self, subdir):
        self.subdir = subdir


    def execute(self, path):
        assert self.server_url
        #f = open(path, 'rb')
        import codecs
        f = codecs.open(path, 'rb')

        if self.offset:
            f.seek(self.offset * self.chunk_size)
        else:
            self.offset = 0

        while 1:
            buffer = f.read(self.chunk_size)
            if not buffer:
                break

            if self.offset == 0:
                action = "create"
            else:
                action = "append"

            fields = [
                ("ajax", "true"),
                ("action", action),
            ]
            if self.ticket:
                fields.append(("ticket", self.ticket))
                fields.append(("login_ticket", self.ticket))
                basename = os.path.basename(path)
                from json import dumps as jsondumps

                # Workaround for python inside Maya, maya.Output has no sys.stdout.encoding property
                try:
                    if getattr(sys.stdout, "encoding", None) is not None and sys.stdout.encoding:
                        basename = basename.decode(sys.stdout.encoding)
                    else:
                        import locale
                        basename = basename.decode(locale.getpreferredencoding())
                except AttributeError:
                    # Python3 has no decode method on strings objects
                    pass

                basename = jsondumps(basename)
                basename = basename.strip('"')
                # the first index begins at 0
                fields.append(("file_name0", basename))

            if self.subdir:
                fields.append(("subdir", self.subdir))

            files = [("file", path, buffer)]
            (status, reason, content) = self.upload(self.server_url, fields, files)

            if reason != "OK":
                raise TacticUploadException("Upload of '%s' failed: %s %s" % (path, status, reason))

            self.offset += 1

        f.close()



    def upload(self, url, fields, files):

        try:
            ret_value = self.posturl(url, fields, files)

            if ret_value[0] != 200:
                raise Exception(ret_value[1])

            return ret_value

        except Exception as e:
            print("Error: ", e)

            # retry about 5 times
            print("... trying again")
            self.tries += 1
            if self.tries < 5:
                self.upload(url, fields, files)

        finally:
            self.tries = 0



    # Repurposed from:
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306

    def posturl(self, url, fields, files):
        #print("URL ", url)
        urlparts = urlparse.urlsplit(url)
        protocol = urlparts[0]
 
        return self.post_multipart(urlparts[1], urlparts[2], fields,files, protocol)
                


    def post_multipart(self, host, selector, fields, files, protocol):
        '''
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.dirk.noteboom@sympatico.ca
        '''
        content_type, body = self.encode_multipart_formdata(fields, files)
        if protocol == 'https':
            h = httplib.HTTPSConnection(host)  
        else:
            h = httplib.HTTPConnection(host)  
        headers = {
            'User-Agent': 'Tactic Client',
            'Content-Type': content_type
            }

        # prevent upgrading the method + url in the httplib module to turn it 
        # into a unicode string before sending the request
        selector = str(selector)
        h.request('POST', selector, body, headers)
        res = h.getresponse()
        return res.status, res.reason, res.read()    


    def encode_multipart_formdata(self, fields, files):
        '''
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return (content_type, body) ready for httplib.HTTPConnection instance
        '''
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_---$---'
        CRLF = '\r\n'
        L = []

        mode = "base64"
        if mode != "base64":
            CRLF = CRLF.encode("UTF8")

        try:
            from cStringIO import StringIO as Buffer
        except:
            if mode == "base64":
                from io import StringIO as Buffer
            else:
                from io import BytesIO as Buffer


        import sys
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            #print("len of value: ", len(value))
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('')


            if mode == "base64":
                # put in a fake header to show that it is base64 to the server
                L.append("data:xyz/xyz;base64,")
                L.append(base64.b64encode(value))
            else:
                L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')

        M = []
        for l in L:
            try:
                if mode == "binary":
                    l = l.encode("UTF8")
                    #l = bytes(l)
                else:
                    l = l.decode()
            except UnicodeDecodeError as e:
                pass
            except AttributeError as e:
                pass
            M.append(l)
            M.append(CRLF)

        # This fails
        #body = "".join(M)

        buf = Buffer()
        buf.writelines(M)
        body = buf.getvalue()
        #print("len of body: ", len(body), type(body))

        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body 





