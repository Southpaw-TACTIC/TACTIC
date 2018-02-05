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
    def execute(self):

        sandbox_dir = "/home/apache/inhance_asset_library"
        rule_code = "6SIMULATION"


        rule_code = self.kwargs.get("rule_code")
        rule = Search.get_by_code("config/ingest_rule", rule_code)


        cmd = IngestionCmd(rule=rule, session_base_dir=sandbox_dir)

        cmd.execute()



class CheckinRuleSaveCmd(Command):

    def execute(self):

        rule_code = self.kwargs.get("rule_code")

        if rule_code:
            search = Search("config/ingest_rule")
            search.add_filter("code", rule_code)
            rule = search.get_sobject()
        else:
            rule = SearchType.create("config/ingest_rule")

        # explicitly save the columns
        columns = ['base_dir', 'rule', 'title']
        for column in columns:
            rule.set_value(column, self.kwargs.get(column) )


        # not sure if we want to save the entire kwargs??
        kwargs_str = jsondumps(self.kwargs)
        rule.set_value("data", kwargs_str)

        rule.commit()
        return



class IngestionCmd(Command):

    ARGS_KEYS = {
    }

    def init(self):
        self.sobject_tags = {}
        self.snapshot_tags = {}

        self.paths_not_matched = []
        self.paths_matched = []
        self.paths_irregular = []
        self.tags = {}
        self.data = {}


    def execute(self):
        """
        rule = self.kwargs.get("rule")
        if rule:
            # kwargs takes precedence over data
            data = rule.get_json_value("data")

            # do a quick convertion
            data["pattern"] = data.get("rule")

            data.update( self.kwargs )
            self.kwargs = data
        """

        print self.kwargs

        scan_type = self.kwargs.get('scan_type')
        action_type = self.kwargs.get('action_type')
        checkin_type = self.kwargs.get('action')
        checkin_mode = self.kwargs.get('mode')



        rule_code = self.kwargs.get("rule_code")
        mode = self.kwargs.get("mode")

        print "scan: ", scan_type
        print "mode: ", mode



        if scan_type == 'list':
            file_list = self.kwargs.get("file_list")
            file_list = file_list.split("\n")
            for path in file_list:
                print "found: ", path

                # use some simple rules to checkin the files
                return


        base_dir = self.kwargs.get("base_dir")
        pattern = self.kwargs.get("pattern")
        if not pattern:
            pattern = base_dir




        # if there is a session, then apply the base of the session
        session_base_dir = self.kwargs.get('session_base_dir')
        session_code = self.kwargs.get("session_code")
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



        ignore = self.kwargs.get("ignore")
        if not ignore:
            ignore = []
        else:
            ignore = ignore.split(",")

        filter = self.kwargs.get("filter")
        if not filter:
            filter = []
        else:
            filter = filter.split(",")




        # directory checkin
        """
        pattern = "/home/apache/{sobject.category}/{sobject.code}/"
        base_dir = "/home/apache/Structures"
        checkin_type = "directory"
        self.apply_pattern(base_dir, pattern, checkin_type)

        # directory checkin
        pattern = "/home/apache/{category}/{code}/"
        base_dir = "/home/apache/Vehicles"
        checkin_type = "directory"
        depth = 0
        """

        # other possible options
        if scan_type == 'rule':
            self.apply_pattern(base_dir, pattern, checkin_type, ignore=ignore, filter=filter)

        # TEST
        # using regular expressions to match (maybe more flexible?)
        #pattern = "/home/apache/(\w+)/(\w+)/"
        #pattern_tags = ["category", "code"]




    def apply_pattern(self, base_dir, pattern, checkin_type, depth=1, ignore=[], filter=[]):

        # remove the trailing /
        if base_dir.endswith("/"):
            base_dir = base_dir.rstrip("/")

        self.paths_not_matched = []
        self.paths_matched = []
        self.paths_irregular = []
        self.paths_invalid = []
        self.tags = {}
        self.data = {}

        # if checkin mode
        if checkin_type == "directory":
            self.sobject_tags = {}
            self.snapshot_tags = {}
            self.process_path(base_dir, pattern, checkin_type)




        # if paths are passed in, then process them
        files = self.kwargs.get("files")
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
                        self.paths_not_matched.append(path)
                        continue

                    self.sobject_tags = {}
                    self.snapshot_tags = {}
                    self.process_path(path, pattern, checkin_type)

                    self.tags[path] = {
                        'sobject': self.sobject_tags,
                        'snapshot': self.snapshot_tags
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
                            self.paths_not_matched.append(path)
                            continue

                        self.sobject_tags = {}
                        self.snapshot_tags = {}

                        self.process_path(path, pattern, checkin_type)

                        self.tags[path] = {
                            'sobject': self.sobject_tags,
                            'snapshot': self.snapshot_tags
                        }

                else:
                    for file in files:

                        count += 1
                        limit = 100000
                        if count > limit:
                            break


                        path = "%s/%s" % (root, file)
                        self.check_irregular(path)

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
                            self.paths_not_matched.append(path)
                            continue


                        #xx = "scan"
                        xx = "xx"
                        if xx == 'scan':
                            self.scan_path(path, pattern)
                        else:

                            self.sobject_tags = {}
                            self.snapshot_tags = {}
                            self.process_path(path, pattern, checkin_type)
                            self.tags[path] = {
                                'sobject': self.sobject_tags,
                                'snapshot': self.snapshot_tags,
                            }

        print "length: ", len(self.data.keys())

        self.info["paths_matched"] = self.paths_matched
        self.info["paths_not_matched"] = self.paths_not_matched
        self.info["paths_invalid"] = self.paths_invalid
        self.info["paths_irregular"] = self.paths_irregular
        self.info["tags"] = self.tags


        self.info["data"] = self.data

        import codecs
        scan_path = "/tmp/scan"
        if os.path.exists(scan_path):
            f = codecs.open(scan_path, 'r', 'utf-8')
            data = jsonloads( f.read() )
            f.close()
            data.update(self.data)
        else:
            data = self.data

        f = codecs.open(scan_path, 'w', 'utf-8')
        f.write( jsondumps( data ) )
        f.close()

        return


    def check_irregular(self, path):
        import re
        p = re.compile("[\!]")
        if p.search(path):
            self.paths_irregular.append(path)
            return True


        # see if there are any non-acii characters
        #print path
        

    def scan_path(self, path, pattern):
        '''simple scan of the file system'''
        is_matched = self.process_pattern(path, pattern)
        if not is_matched:
            return

        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)

        status = 'scan'

        self.data[path] = {
            'size': size,
            'ctime': ctime,
            'status': 'scan'
        }

    def process_path(self, path, pattern, checkin_type):
        is_matched = self.process_pattern(path, pattern)
        if not is_matched:
            return


        status = self.kwargs.get("mode")
        action_type = self.kwargs.get("action_type")
        if action_type == 'ignore':
            print "ignoring: ", path
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
            self.data[path] = {
                'size': size,
                'ctime': ctime,
                'status': status
            }
            return





        search_key = self.kwargs.get("search_key")
        search_type = self.kwargs.get("search_type")

        # create an sobject to store data
        if search_key:
            self.sobject = Search.get_by_search_key(search_key)
            self.parent = self.sobject.get_parent()

        elif search_type:
            code = self.sobject_tags.get("code")
            id = self.sobject_tags.get("id")
            if code:
                self.sobject = Search.get_by_code(search_type, code)
            elif id:
                self.sobject = Search.get_by_id(search_type, code)
            else:
                self.sobject = None

            if not self.sobject:
                # create a new sobject
                self.sobject = SearchType.create(search_type)
                self.parent = None

        # create a snapshot to store snapshot data
        snapshot = SearchType.create("sthpw/snapshot")


        # extras
        keywords = []

        search_type_sobj = SearchType.get(search_type)

        # create the new sobject
        for name, value in self.sobject_tags.items():
            if search_type_sobj.column_exists(name):
                self.sobject.set_value(name, value)
            keywords.append(value)

        extra_names = self.kwargs.get("extra_name")
        extra_values = self.kwargs.get("extra_value")
        for name, value in zip(extra_names, extra_values):
            if not name:
                continue

            if search_type_sobj.column_exists(name):
                self.sobject.set_value(name, value)
            keywords.append(value)


        extra_keywords = self.kwargs.get("keywords")
        if extra_keywords:
            extra_keywords = extra_keywords.split(",")
            for k in extra_keywords:
                keywords.append(k)



        #has_keyword = True
        #if has_keyword:
        if search_type_sobj.column_exists('keywords'):
            keywords = " ".join(keywords)
            self.sobject.set_value("keywords", keywords)


        self.validation_script = self.kwargs.get("validation_script")
        if self.validation_script:
            from tactic.command import PythonCmd
            input = {
                "path": path,
                "sobject": self.sobject,
                "parent": self.parent,
                "snapshot": snapshot
            }
            validation_cmd = PythonCmd(script_path=self.validation_script, input=input, IngestException=IngestException)
            try:
                result = validation_cmd.execute()
            except IngestException as e:
                print e.message
                result = None
            except Exception as e:
                print "ERROR: ", e.message
                result = None


            if not result:
                self.paths_invalid.append(path)
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
        self.sobject_tags['metadata'] = metadata


        mode = self.kwargs.get("mode")
        self.data[path] = {
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
        self.process_script = self.kwargs.get("process_script")
        if self.process_script:
            from tactic.command import PythonCmd
            input = {
                "path": path,
                "sobject": self.sobject,
                "parent": self.parent,
                "snapshot": snapshot
            }
            process_cmd = PythonCmd(script_path=self.process_script, input=input)
            result = process_cmd.execute()

            if not result:
                return






        #print "keywords: ", keywords

        #
        # action
        #

        # first commit the data that has changed to the sobject
        self.sobject.commit()




        # check in the files to the new sobject
        context = self.snapshot_tags.get("context")
        if not context:
            context = "publish"

        #checkin.execute()
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol='local')
        if checkin_type == "directory":
            print "dir checkin: ", self.sobject_tags.get("code"), context, path
            server.directory_checkin( self.sobject.get_search_key(), context, path, mode='copy')
 

        elif checkin_type == "file":

            # use the client api
            snapshot = server.simple_checkin( self.sobject.get_search_key(), context, path, mode='copy', metadata=metadata)

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
            checkin = FileCheckin(self.sobject, path, context=context)
            checkin.execute()
            """


    def process_pattern(self, path, pattern):
       
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

                self.handle_expr(expr, value)

                # if it at then of the pattern, then it is matched
                if pattern_index == len(pattern)-1:
                    self.paths_matched.append(path)
                    return True

                pattern_index += 1

                continue

            elif expr_mode:
                cur_expr.append(token)
                pattern_index += 1
                continue


            # if we are at the end of the pattern
            elif pattern_index >= len(pattern) - 1:
                self.paths_matched.append(path)
                return True


            # if we are at the end of the path
            elif path_index >= len(path) - 1:
                self.paths_not_matched.append(path)
                return False




            elif path[path_index] != pattern[pattern_index]:
                self.paths_not_matched.append(path)
                return False

            pattern_index += 1
            path_index += 1

            # if we are at the end of the pattern, then we have matched
            if pattern_index == len(pattern)-1:
                self.paths_matched.append(path)
                return True


    def handle_expr(self, expr, value):
        parts = expr.split(".")

        if len(parts) == 1:
            self.sobject_tags[expr] = value
            return

        key = parts[0]
        attr = parts[1]

        if key == 'sobject':
            self.sobject_tags[attr] = value

        elif key == 'snapshot':
            self.snapshot_tags[attr] = value
            
        elif key == 'parent':
            pass

        elif key == 'project':
            # ignore the project
            pass


# NOT IMPLEMENTED YET
class IngestCreateSObjectCmd(Command):
    def execute(self):
        # create the new sobject
        for name, value in self.sobject_tags.items():
            self.sobject.set_value(name, value)

        has_keyword = True
        if has_keyword:
            keywords = self.sobject_tags.values()
            keywords = " ".join(keywords)
            self.sobject.set_value("keywords", keywords)


        # check in the files to the new sobject
        context = self.snapshot_tags.get("context")
        if not context:
            context = "publish"

        #checkin = FileCheckin(self.sobject, ... )
        #checkin.execute()
        if checkin_type == "dir":
            print "dir checkin: ", self.sobject_tags.get("code"), context, path
        elif checkin_type == "file":
            print "checkin: ", self.sobject_tags.get("code"), context, path





