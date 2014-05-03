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

import os, subprocess, time, re



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



    def get_current_data(my):
        return my.current_data



    def sync_paths(my, from_path, to_path):

        server = my.kwargs.get("server")
        login = my.kwargs.get("login")


        to_path = "%s@%s:%s" % (login, server, to_path)

        rsync = Common.which("rsync")



        cmd_list = []
        cmd_list.append(rsync)
        flags = "-az"
        cmd_list.append(flags)
        cmd_list.append("-e ssh")
        cmd_list.append("-v")
        cmd_list.append("--progress")

        partial = True
        if partial:
            cmd_list.append("--partial")


        cmd_list.append('%s' % from_path)
        cmd_list.append('%s' % to_path)

        print " ".join(cmd_list)



        program = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        #program.wait()


        on_update = my.kwargs.get("on_update")
        if not on_update:
            progress = RSyncProgress()
            on_update = progress.on_update
        assert(on_update)

        data = []
        lines = []
        path = None
        while program.poll() is None:
            buffer = []
            while 1:
                char = program.stdout.read(1)
                if char == "\n":
                    line = "".join(buffer)
                    buffer = []
                    break

                buffer.append(char)
                if not buffer:
                    break
                
            #line = program.stdout.readline()

            if line == "\n":
                continue

            if line:
                lines.append(line)
                if line.startswith(" "):

                    line = line.strip()
                    parts = re.split( re.compile("\ +"), line )

                    my.current_data = {
                        "bytes": int(parts[0]),
                        "percent": parts[1],
                        "rate": parts[2],
                        "time_left": parts[3]
                    }
                    print my.current_data
                    #print "status: ", line

                    if on_update:
                        on_update(path, my.current_data)


                else:
                    line = line.strip()
                    path = line



        return "".join(line)


class RSyncProgress(object):
    def __init__(my):
        my.total_sent = 0

    def on_update(my, path, data):
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()
        data['path'] = path

        bytes = data.get("bytes")
        my.total_sent += bytes

        print "path: ", path
        print "total: ", my.total_sent

        server.log_message("wow", data)






if __name__ == '__main__':

    import time

    from_path = "/home/tactic/svg"


    start = time.time()

    dir_info = Common.get_dir_info(from_path)
    print "dir_info: ", dir_info
    total_size = dir_info.get("size")


    from pyasm.security import Batch
    Batch()


    class Progress(object):
        def __init__(my):
            my.total_sent = 0

        def on_update(my, path, data):
            from tactic_client_lib import TacticServerStub
            server = TacticServerStub.get()
            data['path'] = path

            bytes = data.get("bytes")
            my.total_sent += bytes

            print "path: ", path
            print "total: ", my.total_sent

            server.log_message("wow", data)
    progress = Progress()



    kwargs = {
            "login": "root",
            "server": "sync1.southpawtech.com",
            "from_path": from_path,
            "to_path": "/spt/test/svg",
            "on_update": progress.on_update
    }
    cmd = RSync(**kwargs)

    cmd.execute()


