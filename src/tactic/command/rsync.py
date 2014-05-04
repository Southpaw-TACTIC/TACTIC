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
        my.paths = []

    def get_paths(my):
        return my.paths


    def execute(my):
        base_dir = my.kwargs.get("base_dir")
        relative_dir = my.kwargs.get("relative_dir")
        file_name = my.kwargs.get("file_name")
        to_path = my.kwargs.get("to_path")

        from_path = "%s/./%s/%s" % (base_dir, relative_dir, file_name)

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
        cmd_list.append("--delete")

        dry_run = my.kwargs.get("dry_run")
        if dry_run in [True, 'true']:
            cmd_list.append("--dry-run")

        relative = True
        if relative:
            cmd_list.append("--relative")

        partial = True
        if partial:
            cmd_list.append("--partial")


        cmd_list.append('%s' % from_path)
        cmd_list.append('%s' % to_path)

        print " ".join(cmd_list)



        program = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        #program.wait()

        message_key = my.kwargs.get("message_key")

        progress = RSyncProgress(message_key=message_key)

        on_update = my.kwargs.get("on_update")
        if not on_update:
            on_update = progress.on_update
        assert(on_update)

        on_complete = my.kwargs.get("on_complete")
        if not on_complete:
            on_complete = progress.on_complete
        assert(on_complete)

        on_error = my.kwargs.get("on_error")
        if not on_error:
            on_error = progress.on_error
        assert(on_error)



        data = []
        lines = []
        path = None
        my.paths = []
        error = []
        while program.poll() is None:
            buffer = []
            while 1:
                char = program.stdout.read(1)
                #print "char: ", char
                if char == "\n":
                    line = "".join(buffer)
                    buffer = []
                    break

                buffer.append(char)
                if len(buffer) > 1024:
                    print "ERROR: overflow"
                    print buffer
                    break
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

                elif line.startswith("rsync "):
                    error.append(line)
                elif line.startswith("rsync: "):
                    error.append(line)
                elif line.startswith("sent "):
                    my.handle_data_line(line)
                elif line.startswith("total "):
                    my.handle_data_line(line)
                elif line.startswith("sending incremental "):
                    my.handle_data_line(line)
                else:
                    line = line.strip()
                    path = line
                    if not line.endswith("/"):
                        my.paths.append(line)


        if error:
            error = "\n".join(error)
            if on_error:
                on_error(path, {"error": error})
            raise Exception("Sync Error\n%s" % error)


        if on_complete:
            on_complete(path, {})


        return "success"



    def handle_data_line(my, line):
        data = {}


        if line.startswith("sent "):
            # sent 520 bytes  received 22 bytes  361.33 bytes/sec
            pass

        elif line.startswith("total "):
            #total size is 431666  speedup is 796.43 (DRY RUN)
            parts = line.split()
            total_size = parts[3]
            data['total_size'] = total_size

        print "data: ", data




class RSyncProgress(object):
    def __init__(my, **kwargs):
        my.total_sent = 0
        from tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        my.message_key = kwargs.get("message_key")

    def on_update(my, path, data):
        data['path'] = path

        bytes = data.get("bytes")
        my.total_sent += bytes

        print "path: ", path
        print "total: ", my.total_sent

        if my.message_key:
            my.server.log_message(my.message_key, data, status="in_progress")


    def on_error(my, path, data):
        if my.message_key:
            my.server.log_message(my.message_key, data, status="error")

    def on_complete(my, path, data):
        if my.message_key:
            my.server.log_message(my.message_key, data, status="complete")



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


