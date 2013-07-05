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

__all__ = ['FrameUtil']

import os, re


class FrameUtil(object):
    '''Utility class for manipulating frames
   
    usage:

    frame_util = FrameUtil()
    frame_util.set_frame_pattern(r"image(\d+).jpg", ["frame"])
    '''

    def __init__(my, frame_pattern=None):
        my.frame_pattern = frame_pattern


    def set_frame_pattern(my, pattern):
        my.frame_pattern = pattern



    def find_pattern(my, info):
        '''find the file pattern'''

        # this is given by the user
        #pattern = "C:/test/{episode}/{shot}/image{frame}.jpg"
        pattern = my.frame_pattern

        # user selects a bunch of shots
        # requires some sobject values
        for key, value in info.items():
            pattern = pattern.replace("{%s}" % key, value)

        # get as the final pattern
        #pattern = "C:/test/ST01/ST01-001/image{frame}.jpg"

        dir = os.path.dirname(pattern)
        file = os.path.basename(pattern)

        # find frame
        padding = 4
        file = file.replace("#"*padding, r"(.*)")


        return dir,file




    def get_frame_list(my, info):
        '''simple return of a list of files that match the pattern'''

        frame_dir, frame_pattern = my.find_pattern(info)

        # look through a directory for the files
        files = os.listdir(frame_dir)
        files.sort()

        matched_files = []
        for file in files:
            #p = re.compile(my.frame_pattern)
            p = re.compile(frame_pattern)
            m = p.match(file)
            if not m:
                print "skipping: ", file, frame_pattern
                continue

            matched_files.append("%s/%s" % (frame_dir, file) )

        return matched_files






    def get_frame_range(my, info):
        frame_dir, frame_pattern = my.find_pattern(info)

        if not os.path.exists(frame_dir):
            return 0,0,0

        files = my.get_frame_list(info)

        frame_pattern = "%s/%s" % (frame_dir, frame_pattern)

        start_frame = None
        end_frame = None
        by_frame = 1

        for file in files:

            p = re.compile(frame_pattern)
            m = p.match(file)
            if not m:
                raise Exception("file '%s' does not match pattern '%s'" % \
                    (file, frame_pattern) )

            cur_frame = m.groups()[0]


            if start_frame == None:
                start_frame = int(cur_frame)
            end_frame = int(cur_frame)

        return start_frame, end_frame, by_frame








    def get_frame_info(my, file, frame_pattern):

        info = {}

        file = os.path.basename(file)

        p = re.compile(frame_pattern)
        m = p.match(file)
        if not m:
            raise Exception("file '%s' does not match pattern '%s'" % \
                (file, frame_pattern) )

        groups = m.groups()

        if len(groups) != len(my.parts):
            raise Exception("Defined parts '%s' does not match '%s'" % \
                (my.parts, frame_pattern) )

        for i in range(0, len(my.parts)):
            part = my.parts[i]
            group = groups[i]

            info[part] = group
            

        return info


