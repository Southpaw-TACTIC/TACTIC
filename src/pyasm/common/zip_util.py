###########################################################
#
# Copyright (c) 2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import zipfile, os, codecs, datetime

class ZipUtil(object):

    def zip_dir(cls, dir, zip_path=None):

        if not zip_path:
            zip_path = "./%s.zip" % os.path.basename(dir)

        f = codecs.open(zip_path, 'wb')
        zip = zipfile.ZipFile(f, 'w', compression=zipfile.ZIP_DEFLATED)
        # Probably not, this may work better in windows without compression
        #zip = zipfile.ZipFile(f, 'w', compression=zipfile.ZIP_STORED)

    
        try:
            for root, dirs, files in os.walk(dir):
                for file in files:
                    path = "%s/%s" % (root, file)
                    relpath = "%s/%s" % (os.path.basename(root), file)
                    zip.write(path, relpath)
        finally:
            zip.close()

    zip_dir = classmethod(zip_dir)



    def extract(cls, zip_path, base_dir=None):
        # first check if this is a zip file
        if not os.path.exists(zip_path):
            raise Exception("Path [%s] does not exist" % zip_path)

        is_zip = zipfile.is_zipfile(zip_path)
        if not is_zip:
            raise Exception("Path [%s] is not a zip file" % zip_path)

        # TODO: make sure all paths are relative

        if not base_dir:
            base_dir = os.path.dirname(zip_path)



        paths = []


        f = codecs.open(zip_path, 'rb')
        zf = zipfile.ZipFile(f, 'r')

        if hasattr(zf, 'extractall'):
            try:
                zf.extractall(path=base_dir)
            except Exception, e:
                print "WARNING extracting zip: ", e
            return

        name_list = zf.namelist()

        for file_path in name_list:

            try:
                data = zf.read(file_path)
            except KeyError:
                print 'ERROR: Did not find %s in zip file' % filename
            else:
                new_path = "%s/%s" % (base_dir, file_path)
                new_dir = os.path.dirname(new_path)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)

                nf = codecs.open(new_path, 'wb')
                nf.write(data)
                nf.close()

                paths.append(new_path)

        return paths

    extract = classmethod(extract)


    def get_file_paths(cls, path):
        paths = []
        zf = zipfile.ZipFile(path)
        for info in zf.infolist():
            paths.append( info.filename )

        return paths
    get_file_paths = classmethod(get_file_paths)


    def print_info(cls, path):
        zf = zipfile.ZipFile(path)
        for info in zf.infolist():
            print info.filename
        print '\tComment:\t', info.comment
        print '\tModified:\t', datetime.datetime(*info.date_time)
        print '\tSystem:\t\t', info.create_system, '(0 = Windows, 3 = Unix)'
        print '\tZIP version:\t', info.create_version
        print '\tCompressed:\t', info.compress_size, 'bytes'
        print '\tUncompressed:\t', info.file_size, 'bytes'
        print
    print_info = classmethod(print_info)



if __name__ == '__main__':
    zip = ZipUtil()
    zip.zip_dir("C:/test/mp3", "C:/test/mp3.zip")
    zip.extract("C:/test/mp3.zip", base_dir = "C:/test/output")
    """
    zip.zip_dir("zip_this", "/home/apache/test/cow.zip")
    zip.print_info("/home/apache/test/cow.zip")

    zip.extract("/home/apache/test/cow.zip", "/home/apache/test2")
    """
