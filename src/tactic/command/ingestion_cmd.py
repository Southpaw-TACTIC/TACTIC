###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['IngestionCmd', 'IngestException', 'CheckinRuleSaveCmd']

import tacticenv

import os, time

from pyasm.common import jsondumps, jsonloads
from pyasm.command import Command
from pyasm.search import Search, SearchType

class IngestException(Exception):
    pass


__all__.append("CheckinRuleCmd")
class CheckinRuleCmd(Command):
    '''Command to checkin a rule'''
    def execute(my):

        sandbox_dir = "/home/apache/inhance_asset_library"
        rule_code = "6SIMULATION"


        rule_code = my.kwargs.get("rule_code")
        rule = Search.get_by_code("config/ingest_rule", rule_code)


        cmd = IngestionCmd(rule=rule, session_base_dir=sandbox_dir)

        cmd.execute()



class CheckinRuleSaveCmd(Command):

    def execute(my):

        rule_code = my.kwargs.get("rule_code")

        if rule_code:
            search = Search("config/ingest_rule")
            search.add_filter("code", rule_code)
            rule = search.get_sobject()
        else:
            rule = SearchType.create("config/ingest_rule")

        # explicitly save the columns
        columns = ['base_dir', 'rule', 'title']
        for column in columns:
            rule.set_value(column, my.kwargs.get(column) )


        # not sure if we want to save the entire kwargs??
        kwargs_str = jsondumps(my.kwargs)
        rule.set_value("data", kwargs_str)

        rule.commit()
        return



class IngestionCmd(Command):

    ARGS_KEYS = {
    }

    def init(my):
        my.sobject_tags = {}
        my.snapshot_tags = {}

        my.paths_not_matched = []
        my.paths_matched = []
        my.paths_irregular = []
        my.tags = {}
        my.data = {}


    def execute(my):
        """
        rule = my.kwargs.get("rule")
        if rule:
            # kwargs takes precedence over data
            data = rule.get_json_value("data")

            # do a quick convertion
            data["pattern"] = data.get("rule")

            data.update( my.kwargs )
            my.kwargs = data
        """

        print my.kwargs

        scan_type = my.kwargs.get('scan_type')
        action_type = my.kwargs.get('action_type')
        checkin_type = my.kwargs.get('action')
        checkin_mode = my.kwargs.get('mode')



        rule_code = my.kwargs.get("rule_code")
        mode = my.kwargs.get("mode")

        print "scan: ", scan_type
        print "mode: ", mode



        if scan_type == 'list':
            file_list = my.kwargs.get("file_list")
            file_list = file_list.split("\n")
            for path in file_list:
                print "found: ", path

                # use some simple rules to checkin the files
                return


        base_dir = my.kwargs.get("base_dir")
        pattern = my.kwargs.get("pattern")
        if not pattern:
            pattern = base_dir




        # if there is a session, then apply the base of the session
        session_base_dir = my.kwargs.get('session_base_dir')
        session_code = my.kwargs.get("session_code")
        if session_code:
            base_dir = base_dir.lstrip("/")
            session = Search.get_by_code("config/ingest_session", session_code)
            session_base_dir = session.get_value("base_dir")
            session_base_dir = session_base_dir.rstrip("/")

            base_dir = "%s/%s" % (session_base_dir, base_dir)
            pattern = "%s/%s" % (session_base_dir, pattern)

        elif session_base_dir:
            base_dir = "%s/%s" % (session_base_dir, base_dir)
            pattern = "%s/%s" % (session_base_dir, pattern)

        else:
            raise Exception("No session found")

        print "base_dir: ", base_dir
        print "pattern: ", pattern



        ignore = my.kwargs.get("ignore")
        if not ignore:
            ignore = []
        else:
            ignore = ignore.split(",")

        filter = my.kwargs.get("filter")
        if not filter:
            filter = []
        else:
            filter = filter.split(",")




        # directory checkin
        """
        pattern = "/home/apache/{sobject.category}/{sobject.code}/"
        base_dir = "/home/apache/Structures"
        checkin_type = "directory"
        my.apply_pattern(base_dir, pattern, checkin_type)

        # directory checkin
        pattern = "/home/apache/{category}/{code}/"
        base_dir = "/home/apache/Vehicles"
        checkin_type = "directory"
        depth = 0
        """

        # other possible options
        if scan_type == 'rule':
            my.apply_pattern(base_dir, pattern, checkin_type, ignore=ignore, filter=filter)

        # TEST
        # using regular expressions to match (maybe more flexible?)
        #pattern = "/home/apache/(\w+)/(\w+)/"
        #pattern_tags = ["category", "code"]




    def apply_pattern(my, base_dir, pattern, checkin_type, depth=1, ignore=[], filter=[]):

        # remove the trailing /
        if base_dir.endswith("/"):
            base_dir = base_dir.rstrip("/")

        my.paths_not_matched = []
        my.paths_matched = []
        my.paths_irregular = []
        my.paths_invalid = []
        my.tags = {}
        my.data = {}

        # if checkin mode
        if checkin_type == "directory":
            my.sobject_tags = {}
            my.snapshot_tags = {}
            my.process_path(base_dir, pattern, checkin_type)




        # if paths are passed in, then process them
        files = my.kwargs.get("files")
        if files:
            root = base_dir

            if checkin_type == "file":
                start_depth = len(pattern.split("/"))

                for file in files:
                    #path = "%s/%s" % (root, file)
                    path = file

                    skip = False
                    for p in ignore:
                        if file.endswith(p):
                            skip = True
                            break

                    for p in filter:
                        if file.find(p) == -1:
                            skip = True
                            break

                    if skip:
                        my.paths_not_matched.append(path)
                        continue

                    my.sobject_tags = {}
                    my.snapshot_tags = {}
                    my.process_path(path, pattern, checkin_type)

                    my.tags[path] = {
                        'sobject': my.sobject_tags,
                        'snapshot': my.snapshot_tags
                    }


        # else look through the file system
        else:
            count = 0

            # find all of the paths in here
            for root, dirs, files in os.walk(unicode(base_dir)):

                if checkin_type == "directory":
                    start_depth = len(pattern.split("/"))

                    for dir in dirs:

                        path = "%s/%s/" % (root, dir)
                        parts_depth = len(path.split("/"))
                        #print path, parts_depth

                        if not parts_depth - start_depth == depth:
                            my.paths_not_matched.append(path)
                            continue

                        my.sobject_tags = {}
                        my.snapshot_tags = {}

                        my.process_path(path, pattern, checkin_type)

                        my.tags[path] = {
                            'sobject': my.sobject_tags,
                            'snapshot': my.snapshot_tags
                        }

                else:
                    for file in files:

                        count += 1
                        limit = 100000
                        if count > limit:
                            break


                        path = "%s/%s" % (root, file)
                        my.check_irregular(path)

                        skip = False
                        for p in ignore:
                            if file.endswith(p):
                                skip = True
                                break

                        for p in filter:
                            if p.startswith("/") and p.endswith("/"):
                                import re
                                p = p.strip("/")
                                p = re.compile(p)
                                if p.match(file):
                                    skip = False
                                    break

                            elif file.find(p) != -1:
                                skip = False
                                break
                        else:
                            if not filter:
                                skip = False
                            else:
                                skip = True

                        if skip:
                            my.paths_not_matched.append(path)
                            continue


                        #xx = "scan"
                        xx = "xx"
                        if xx == 'scan':
                            my.scan_path(path, pattern)
                        else:

                            my.sobject_tags = {}
                            my.snapshot_tags = {}
                            my.process_path(path, pattern, checkin_type)
                            my.tags[path] = {
                                'sobject': my.sobject_tags,
                                'snapshot': my.snapshot_tags,
                            }

        print "length: ", len(my.data.keys())

        my.info["paths_matched"] = my.paths_matched
        my.info["paths_not_matched"] = my.paths_not_matched
        my.info["paths_invalid"] = my.paths_invalid
        my.info["paths_irregular"] = my.paths_irregular
        my.info["tags"] = my.tags


        my.info["data"] = my.data

        import codecs
        scan_path = "/tmp/scan"
        if os.path.exists(scan_path):
            f = codecs.open(scan_path, 'r', 'utf-8')
            data = jsonloads( f.read() )
            f.close()
            data.update(my.data)
        else:
            data = my.data

        f = codecs.open(scan_path, 'w', 'utf-8')
        f.write( jsondumps( data ) )
        f.close()

        return


    def check_irregular(my, path):
        import re
        p = re.compile("[\!]")
        if p.search(path):
            my.paths_irregular.append(path)
            return True


        # see if there are any non-acii characters
        #print path
        

    def scan_path(my, path, pattern):
        '''simple scan of the file system'''
        is_matched = my.process_pattern(path, pattern)
        if not is_matched:
            return

        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)

        status = 'scan'

        my.data[path] = {
            'size': size,
            'ctime': ctime,
            'status': 'scan'
        }

    def process_path(my, path, pattern, checkin_type):
        is_matched = my.process_pattern(path, pattern)
        if not is_matched:
            return


        status = my.kwargs.get("mode")
        action_type = my.kwargs.get("action_type")
        if action_type == 'ignore':
            print "ignoring: ", path
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
            my.data[path] = {
                'size': size,
                'ctime': ctime,
                'status': status
            }
            return





        search_key = my.kwargs.get("search_key")
        search_type = my.kwargs.get("search_type")

        # create an sobject to store data
        if search_key:
            my.sobject = Search.get_by_search_key(search_key)
            my.parent = my.sobject.get_parent()

        elif search_type:
            code = my.sobject_tags.get("code")
            id = my.sobject_tags.get("id")
            if code:
                my.sobject = Search.get_by_code(search_type, code)
            elif id:
                my.sobject = Search.get_by_id(search_type, code)
            else:
                my.sobject = None

            if not my.sobject:
                # create a new sobject
                my.sobject = SearchType.create(search_type)
                my.parent = None

        # create a snapshot to store snapshot data
        snapshot = SearchType.create("sthpw/snapshot")


        # extras
        keywords = []

        search_type_sobj = SearchType.get(search_type)

        # create the new sobject
        for name, value in my.sobject_tags.items():
            if search_type_sobj.column_exists(name):
                my.sobject.set_value(name, value)
            keywords.append(value)

        extra_names = my.kwargs.get("extra_name")
        extra_values = my.kwargs.get("extra_value")
        for name, value in zip(extra_names, extra_values):
            if not name:
                continue

            if search_type_sobj.column_exists(name):
                my.sobject.set_value(name, value)
            keywords.append(value)


        extra_keywords = my.kwargs.get("keywords")
        if extra_keywords:
            extra_keywords = extra_keywords.split(",")
            for k in extra_keywords:
                keywords.append(k)



        #has_keyword = True
        #if has_keyword:
        if search_type_sobj.column_exists('keywords'):
            keywords = " ".join(keywords)
            my.sobject.set_value("keywords", keywords)


        my.validation_script = my.kwargs.get("validation_script")
        if my.validation_script:
            from tactic.command import PythonCmd
            input = {
                "path": path,
                "sobject": my.sobject,
                "parent": my.parent,
                "snapshot": snapshot
            }
            validation_cmd = PythonCmd(script_path=my.validation_script, input=input, IngestException=IngestException)
            try:
                result = validation_cmd.execute()
            except IngestException as e:
                print e.message
                result = None
            except Exception as e:
                print "ERROR: ", e.message
                result = None


            if not result:
                my.paths_invalid.append(path)
                return


        # handle metadata for the files
        # FIXME: this should go directly onto the snapshot
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
        metadata = snapshot.get_value("metadata")
        if not metadata:
            metadata = {}
        else:
            metadata = jsonloads(metadata)

        metadata['size'] = size
        metadata['ctime'] = ctime
        metadata['mtime'] = mtime

        # add metadata if there is any
        my.sobject_tags['metadata'] = metadata


        mode = my.kwargs.get("mode")
        my.data[path] = {
            'size': size,
            'ctime': ctime,
            'status': mode
        }



        # skip if no action takes place
        if mode == 'scan':
            return


        # TODO: not sure if we need to make the distinction between
        # a between a process script and a validation script.  They
        # basically do the same thing???
        my.process_script = my.kwargs.get("process_script")
        if my.process_script:
            from tactic.command import PythonCmd
            input = {
                "path": path,
                "sobject": my.sobject,
                "parent": my.parent,
                "snapshot": snapshot
            }
            process_cmd = PythonCmd(script_path=my.process_script, input=input)
            result = process_cmd.execute()

            if not result:
                return






        #print "keywords: ", keywords

        #
        # action
        #

        # first commit the data that has changed to the sobject
        my.sobject.commit()




        # check in the files to the new sobject
        context = my.snapshot_tags.get("context")
        if not context:
            context = "publish"

        #checkin.execute()
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol='local')
        if checkin_type == "directory":
            print "dir checkin: ", my.sobject_tags.get("code"), context, path
            server.directory_checkin( my.sobject.get_search_key(), context, path, mode='copy')
 

        elif checkin_type == "file":

            # use the client api
            snapshot = server.simple_checkin( my.sobject.get_search_key(), context, path, mode='copy', metadata=metadata)

            """
            from pyasm.biz import IconCreator
            icon_creator = IconCreator(path)
            icon_creator.execute()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()
            if web_path:
                file_paths = [upload_path, web_path, icon_path]
                file_types = [file_type, 'web', 'icon']

            from pyasm.checkin import FileCheckin
            checkin = FileCheckin(my.sobject, path, context=context)
            checkin.execute()
            """


    def process_pattern(my, path, pattern):
       
        path_index = 0
        pattern_index = 0

        cur_expr = []
        expr_mode = False

        while(1):
            token = pattern[pattern_index]

            if token == "{":
                expr_mode = True
                pattern_index += 1
                continue

            elif token == "}":
                expr = "".join(cur_expr)

                expr_mode = False
                cur_expr = []

                # get the next token
                if pattern_index+1 >= len(pattern):
                    next_token = None
                else:
                    next_token = pattern[pattern_index+1]

                # match the expression to the path
                value = []
                while 1:
                    if path_index >= len(path):
                        break

                    path_token = path[path_index]
                    value.append( path_token )

                    # if we reach the end of the path, then end the
                    # search through the path
                    if path_index+1 >= len(path):
                        break

                    path_token = path[path_index+1]

                    # Match until the next / delimiter
                    #if path_token in "/":
                    #    break

                    path_index += 1

                    if path_token == next_token:
                        break


                value = "".join(value)

                my.handle_expr(expr, value)

                # if it at then of the pattern, then it is matched
                if pattern_index == len(pattern)-1:
                    my.paths_matched.append(path)
                    return True

                pattern_index += 1

                continue

            elif expr_mode:
                cur_expr.append(token)
                pattern_index += 1
                continue


            # if we are at the end of the pattern
            elif pattern_index >= len(pattern) - 1:
                my.paths_matched.append(path)
                return True


            # if we are at the end of the path
            elif path_index >= len(path) - 1:
                my.paths_not_matched.append(path)
                return False




            elif path[path_index] != pattern[pattern_index]:
                my.paths_not_matched.append(path)
                return False

            pattern_index += 1
            path_index += 1

            # if we are at the end of the pattern, then we have matched
            if pattern_index == len(pattern)-1:
                my.paths_matched.append(path)
                return True


    def handle_expr(my, expr, value):
        parts = expr.split(".")

        if len(parts) == 1:
            my.sobject_tags[expr] = value
            return

        key = parts[0]
        attr = parts[1]

        if key == 'sobject':
            my.sobject_tags[attr] = value

        elif key == 'snapshot':
            my.snapshot_tags[attr] = value
            
        elif key == 'parent':
            pass

        elif key == 'project':
            # ignore the project
            pass


# NOT IMPLEMENTED YET
class IngestCreateSObjectCmd(Command):
    def execute(my):
        # create the new sobject
        for name, value in my.sobject_tags.items():
            my.sobject.set_value(name, value)

        has_keyword = True
        if has_keyword:
            keywords = my.sobject_tags.values()
            keywords = " ".join(keywords)
            my.sobject.set_value("keywords", keywords)


        # check in the files to the new sobject
        context = my.snapshot_tags.get("context")
        if not context:
            context = "publish"

        #checkin = FileCheckin(my.sobject, ... )
        #checkin.execute()
        if checkin_type == "dir":
            print "dir checkin: ", my.sobject_tags.get("code"), context, path
        elif checkin_type == "file":
            print "checkin: ", my.sobject_tags.get("code"), context, path





