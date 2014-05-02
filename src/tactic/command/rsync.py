############################################################
#
#    Copyright (c) 2013, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

import tacticenv


from pyasm.common import Common, TacticException

import os, subprocess, time



class RSync(object):

    def __init__(my, **kwargs):
        my.kwargs = kwargs


    def execute(my):
        from_path = my.kwargs.get("from_path")
        to_path = my.kwargs.get("to_path")

        tries = 1
        success = False
        value = ""
        start = time.time()

        while 1:
            try:
                value = my.sync_paths(from_path, to_path)
                success = True
                break

            except Exception, e:
                print "Failed on try [%s]..." % tries
                print e
                time.sleep(tries)
                if tries == 3:
                    break

                tries += 1



        print "success: ", success
        print time.time() - start, " seconds"
        print value




    def sync_paths(my, from_path, to_path):

        host = my.kwargs.get("host")
        login = my.kwargs.get("login")


        to_path = "%s@%s:%s" % (login, host, to_path)

        rsync = Common.which("rsync")

        flags = "-avz"


        cmd_list = []
        cmd_list.append(rsync)
        cmd_list.append(flags)
        cmd_list.append("-e ssh")

        partial = True
        if partial:
            cmd_list.append("--partial")


        cmd_list.append('%s' % from_path)
        cmd_list.append('%s' % to_path)

        program = subprocess.Popen(cmd_list, shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        program.wait()
        value = program.communicate()
        err = None
        if value:
            err = value[1]
       
        if err:
            raise TacticException(err)

        return value


if __name__ == '__main__':

    import time

    from_path = "/home/tactic/svg"


    start = time.time()

    kwargs = {
            "login": "root",
            "host": "sync1.southpawtech.com",
            "from_path": from_path,
            "to_path": "/spt/test/svg"
    }
    cmd = RSync(**kwargs)

    cmd.execute()


