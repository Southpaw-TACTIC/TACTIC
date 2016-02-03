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


from pyasm.common import Common, TacticException, Config

import os, subprocess, time, re, os



class RSyncConnectionException(Exception):
    pass



class RSync(object):

    def __init__(my, **kwargs):
        my.kwargs = kwargs
        my.paths = []
        my.data = {}

    def get_paths(my):
        return my.paths

    def get_data(my):
        return my.data


    def execute(my):
        base_dir = my.kwargs.get("base_dir")

        relative_dir = my.kwargs.get("relative_dir")

        # if not file_name is given, then the default is to recurse through
        # relative_dir
        file_name = my.kwargs.get("file_name")
        if not file_name:
            file_name = ""

        from_paths = []

        relative_paths = my.kwargs.get("relative_paths")
        from_path = my.kwargs.get("from_path")


        # support multiple relative paths
        if relative_paths:
            for relative_path in relative_paths:
                from_path = "%s/./%s" % (base_dir, relative_path)
                from_paths.append(from_path)

        elif from_path:
            from_paths.append(from_path)


        else:
            from_path = "%s/./%s/%s" % (base_dir, relative_dir, file_name)
            from_paths.append(from_path)



        # base to dir (should be to_dir, not to_path)
        to_path = my.kwargs.get("to_path")
        if not to_path:
            to_path = my.kwargs.get("to_dir")




        tries = 1
        success = False
        value = ""
        start = time.time()

        message_key = my.kwargs.get("message_key")

        while 1:
            try:
                value = my.sync_paths(from_paths, to_path)
                success = True
                break
            except RSyncConnectionException, e:
                time.sleep(60)

                from tactic_client_lib import TacticServerStub
                server = TacticServerStub.get()
                server.log_message(message_key, {"message": str(e)}, "error_retry")
                continue

            except Exception, e:
                print "Failed on try [%s]..." % tries
                raise

                # ping the server to see

                if message_key:
                    from tactic_client_lib import TacticServerStub
                    server = TacticServerStub.get()
                    server.log_message(message_key, {"message": str(e)}, "error_retry")

                time.sleep(tries)
                if tries == 3:
                    break

                tries += 1




        #print "success: ", success
        #print time.time() - start, " seconds"
        #print value



    def get_current_data(my):
        return my.current_data


    def get_data(my):
        return my.data


    def sync_paths(my, from_paths, to_path):

        server = my.kwargs.get("server")
        login = my.kwargs.get("login")
        paths = my.kwargs.get("paths")
        base_dir = my.kwargs.get("base_dir")

        paths_sizes = []
        if paths:
            for path in paths:
                full_path = "%s/%s" % (base_dir, path)
                print "full_path: ", full_path
                size = os.path.getsize(full_path)
                paths_sizes.append(size)


        if server:
            to_path = "%s@%s:%s" % (login, server, to_path)

        if os.name == "nt":
            # This assumes we are using the cygwin implementation of RSync
            if to_path[1] == ":":
                # then this is a drive letter
                drive_letter = to_path[0]
                to_path = "/cygdrive/%s/%s" % (drive_letter, to_path[3:])

            for i, from_path in enumerate(from_paths):
                if from_path[1] == ":":
                    # then this is a drive letter
                    drive_letter = from_path[0]
                    from_path = "/cygdrive/%s/%s" % (drive_letter, from_path[3:])
                from_paths[i] = from_path

            to_path = to_path.replace("\\", '/')
            from_path = from_path.replace("\\", '/')


        rsync = Config.get_value("services", "rsync")
        if not rsync:
            rsync = Common.which("rsync")

        if not rsync:
            raise Exception("RSync executable could not be found")


        cmd_list = []
        cmd_list.append(rsync)
        flags = "-az"
        cmd_list.append(flags)
        if server:
            cmd_list.append("-e ssh")
        cmd_list.append("-v")
        cmd_list.append("--progress")

        delete = False
        if delete:
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


        for from_path in from_paths:
            cmd_list.append('%s' % from_path)

        cmd_list.append('%s' % to_path)

        print "exec: ", " ".join(cmd_list)

        program = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        #program.wait()

        message_key = my.kwargs.get("message_key")

        progress = RSyncProgress(
                message_key=message_key,
                paths=paths,
                paths_sizes=paths_sizes
        )

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
        #while program.poll() is None:
        buffer = []
        line = ""
        while 1:
            char = program.stdout.read(1)
            if not char:
                break

            if char == "\n":
                line = "".join(buffer)

            else:
                buffer.append(char)
            

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
                    #print my.current_data
                    #print "status: ", line

                    if on_update:
                        on_update(path, my.current_data)

                elif line.startswith("rsync "):
                    error.append(line)
                elif line.startswith("rsync: "):
                    error.append(line)
                elif line.startswith("deleting "):
                    my.handle_data_line(line)
                elif line.startswith("sent "):
                    my.handle_data_line(line)
                elif line.startswith("total "):
                    my.handle_data_line(line)
                elif line.startswith("sending incremental "):
                    my.handle_data_line(line)
                elif line.startswith("created directory "):
                    my.handle_data_line(line)
                else:
                    line = line.strip()
                    path = line
                    if not line.endswith("/"):
                        if line.find(" -> ") != -1:
                            parts = line.split(" -> ")
                            line = parts[0]

                        my.paths.append(line)
    
                # reset the line
                line = None
                buffer = []



        if error:
            error = "\n".join(error)
            if error.startswith("rsync: connection unexpectedly closed"):
                raise RSyncConnectionException(error) 

            if on_error:
                on_error(path, {"message": error})
            raise Exception("Sync Error\n%s" % error)


        if on_complete:
            on_complete(path, {"message": "All files synchronized"})


        return "success"



    def handle_data_line(my, line):

        if line.startswith("sent "):
            # sent 520 bytes  received 22 bytes  361.33 bytes/sec
            pass

        elif line.startswith("total "):
            #total size is 431666  speedup is 796.43 (DRY RUN)
            parts = line.split()
            total_size = parts[3]
            total_size = int(total_size)
            my.data['total_size'] = total_size




class RSyncProgress(object):
    def __init__(my, **kwargs):
        from tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()
        my.message_key = kwargs.get("message_key")
        my.paths = kwargs.get("paths")
        my.paths_sizes = kwargs.get("paths_sizes")
        if not my.paths:
            my.paths = []

    def on_update(my, path, data):
        data['path'] = path

        bytes = data.get("bytes")

        try:
            index = my.paths.index(path)
        except:
            index = 0
        data["path_index"] = index+1
        data["paths_count"] = len(my.paths)
        data["paths_sizes"] = my.paths_sizes

        total_size = 0
        current_size = 0
        for i in range(0, len(my.paths)):
            if i < index:
                current_size += my.paths_sizes[i]
            elif i == index:
                current_size += bytes

            total_size += my.paths_sizes[i]

        #print "current_size: ", current_size
        #print "total_size: ", total_size
        #print "percent: ", (current_size*1000)/(total_size*10)
        if total_size:
            total_percent = (current_size*1000)/(total_size*10)
        else:
            total_percent = 0
        data['total_percent'] = total_percent


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


