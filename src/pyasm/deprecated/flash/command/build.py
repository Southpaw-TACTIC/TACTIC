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

__all__ = ['FlashBuild']

import tactic
from pyasm.security import Batch
Batch()

import os, re

from pyasm.common import Environment, System
from pyasm.biz import Project
from pyasm.search import Search
from pyasm.command import Command
from pyasm.prod.biz import Shot

from frame_util import *


class FlashBuild(Command):

    def get_local_dir(my):
        #local_dir = Environment.get_local_dir()
        local_dir = "C:/sthpw/test"
        print local_dir
        return local_dir


    def execute(my):
        local_dir = my.get_local_dir()
        return


        pattern = "C:/test/{episode}/{shot}/image####.jpg"

        frame_util = FrameUtil(pattern)

        search = Search(Shot)
        search.add_limit(10)
        shots = search.get_sobjects()

        # prerun flash as a separate nonblockin process
        conn = FlashConnection()
        conn.run_flash()
        
        conn.download_jsfl("common.jsfl")
        conn.download_jsfl("load2.jsfl")


        for shot in shots:

            shot_code = shot.get_code()
            episode_code = shot.get_value("episode_code")

            info = { 'episode': episode_code, 'shot': shot_code }

            frame_dir, frame_pattern = frame_util.find_pattern(info)
            start_frame, end_frame, by_frame = frame_util.get_frame_range(info)

            if start_frame == 0 and end_frame == 0:
                print "Skipping: no frames found for shot '%s'" % shot_code
                continue

            src_path = "%s/%s" % (frame_dir, frame_pattern)
            src_path = src_path.replace("(.*)", "####")
            print "src_path: ", src_path
            print "start_frame: ", start_frame
            print "end_frame: ", end_frame

            load_jsfl = "%s/JSFL/load2.jsfl" % local_dir
            a = conn.get_jsfl(load_jsfl, "include", "common.jsfl", "%s/JSFL" % local_dir)
            b = conn.get_jsfl(load_jsfl, "init_session")
            c = conn.get_jsfl(load_jsfl, "import_leica", src_path, "Leica", start_frame, end_frame)

            exec_path = "%s/temp/exec.jsfl" % local_dir
            f = open(exec_path, "wb")
            f.write(a + "\n")
            f.write(b + "\n")
            f.write(c + "\n")
            f.close()
            os.system(exec_path)


        # wait until the file actually gets created
        #while 1:
        #    if os.path.exists(out_path):
        #        break
        #    time.sleep(0.5)




from subprocess import *

class FlashConnection:

    def get_local_dir(my):
        return "C:/sthpw"

    def run_flash(my, exec_path=None):
        '''execute flash'''

        if not exec_path:
            local_dir = my.get_local_dir()
            exec_path = "%s/temp/run.jsfl" % local_dir
            file = open(exec_path, "wb")
            file.write("x=1")
            file.close()

        print exec_path

        # hard code this for now
        flash = "C:/Program Files/Macromedia/Flash 8/Flash.exe"
        pid = Popen([flash, exec_path])
        print pid
        #os.system(exec_path)

        # sleep for 1 second
        import time
        time.sleep(1)




    def get_jsfl(my, load_path, function, *args):
        jsfl = "fl.runScript('file:///%s', '%s'" % (load_path, function)
        args = ["'%s'" % x for x in args]
        if args:
            jsfl += ", "
            jsfl += ", ".join(args)
        jsfl += ")"
        return jsfl


    def download_jsfl(my, file_name):
        my.server_url = "http://saba:8081"
        jsfl_url = my.server_url + "/context/JSFL/" + file_name

        local_dir = my.get_local_dir()
        jsfl_to_path = local_dir + "/JSFL"

        my.download(jsfl_url, jsfl_to_path)



    def download(my, url, to_dir="", skip_if_exists=False):
        import urllib, urllib2
        filename = os.path.basename(url)

        # download to the current project
        if not to_dir:
            to_dir = my.app.get_workspace_dir()
            # for now, put everything in scenes
            to_dir = "%s/scenes" % to_dir

        # make sure the directory exists
        System().makedirs(to_dir)

        to_path = "%s/%s" % (to_dir, filename)


        # check if this file is already downloaded.  if so, skip
        if skip_if_exists and os.path.exists(to_path):
            print "skipping '%s', already exists" % to_path
            return to_path

        file = open(to_path, "wb")
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req)
            file.write( resp.read() )
            file.close()
        except urllib2.URLError, e:
            raise Exception('%s - %s' % (e,url))

        return to_path








if __name__ == '__main__':
    os.environ['TACTIC_APP_SERVER'] = 'batch'
    Project.set_project("flash")
    cmd = FlashBuild()
    Command.execute_cmd(cmd)
