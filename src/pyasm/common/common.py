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


__all__ = ["Common", "Marshaller", "jsondumps", "jsonloads"]


import os, sys, time, string, re, random, types, new, pprint, traceback
import thread, threading, zipfile
import hashlib, StringIO, urllib
import datetime
import colorsys


from base import *

try:
    #from cjson import encode as jsondumps
    #from cjson import decode as jsonloads
    raise ImportError()
except ImportError:
    try:
        # Python 2.6 ships with json
        from json import dumps as xjsondumps
        from json import loads as jsonloads
        import json

    except ImportError:
        try:
            from simplejson import dumps as xjsondumps
            from simplejson import loads as jsonloads
            import simplejson as json
        except ImportError:
            print "ERROR: no json library found"
            print
            raise

    try:
        from bson import ObjectId
    except ImportError:
        ObjectId = None

    class SPTJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            elif ObjectId and isinstance(obj, ObjectId):
                return str(obj)
            else:
                return json.JSONEncoder.default(self, obj)

    def jsondumps(obj, ensure_ascii=True):
        return xjsondumps(obj, cls=SPTJSONEncoder, ensure_ascii=ensure_ascii)



class Common(Base):


    def get_full_class_name(object):
        name = "%s.%s" % (object.__module__, object.__class__.__name__)
        return name
    get_full_class_name = staticmethod(get_full_class_name)

    def breakup_class_path(class_path):
        '''breaks up a class path into a module and class_name'''
        parts = string.split(class_path,".")
        module_name = string.join(parts[0:len(parts)-1],".")
        class_name = parts[len(parts)-1]
        return (module_name, class_name)
    breakup_class_path = staticmethod(breakup_class_path)


    def create_from_class_path(class_path, args=[], kwargs={}):
        '''dynamically creats an object from a string class path.'''
        assert class_path
        
        marshaller = Marshaller()
        marshaller.set_class(class_path)
        for arg in args:
            marshaller.add_arg(arg)

        marshaller.set_kwargs(kwargs)

        # instantiate the object
        object = marshaller.get_object()

        return object
    create_from_class_path = staticmethod(create_from_class_path)

    def create_from_method(class_path, method, kwargs=None):
        '''dynamically creates an object from a string class path and its
        method.
        Note: this assumes an empty constructor'''

        assert class_path and class_path != ""
       
        # instantiate the object
        obj = Common.create_from_class_path(class_path)
        if kwargs:
            obj = eval('obj.%s(**kwargs)' %method)
        else:
            obj = eval('obj.%s()' %method)
        return obj
    
    create_from_method = staticmethod(create_from_method)

    def add_func_to_class(func, instance, cls, method_name=None):
        ''' add a function to a class, if an instance is given 
            it will be bound to it. '''
        # if the func is wrapped in a method, extract it
        if isinstance(func, types.MethodType):
            func = func.im_func
            
        method = new.instancemethod(func, instance, cls)
        if not method_name: 
            method_name=func.__name__
            
        if instance:
            # and the method to the instance dict to be readily callable
            instance.__dict__[method_name]=method

        return method
    
    add_func_to_class = staticmethod(add_func_to_class)

    def get_import_from_class_path(class_path):
        '''dynamically executes a an import statement
        Note: this assumes an empty constructor'''
        assert class_path != None
        assert class_path != ""
        
        (module_name, class_name) = Common.breakup_class_path(class_path)
        if not module_name:
            return ''

        return "import %s" % module_name
    get_import_from_class_path = staticmethod(get_import_from_class_path)




    def relative_dir(dir_a, dir_b):
        '''get the relative directory between two directories'''

        if dir_a == dir_b:
            return "."

        # strip out any ending /'s
        if dir_a.endswith("/"):
            dir_a = dir_a.rstrip("/")
        if dir_b.endswith("/"):
            dir_b = dir_b.rstrip("/")

        parts_a = dir_a.split("/")
        parts_b = dir_b.split("/")

        len_a = len(parts_a)
        len_b = len(parts_b)
        if len_a < len_b:
            length = len_a
        else:
            length = len_b

        # remove parts that are similar
        for i in range(0, length):
            if parts_a[0] != parts_b[0]:
                break

            parts_a = parts_a[1:]
            parts_b = parts_b[1:]


        # figure out the relative path
        len_a = len(parts_a)
        len_b = len(parts_b)

        relative = [".."] * len_a
        relative.extend(parts_b)
        relative = "/".join(relative)

        return relative

    relative_dir = staticmethod(relative_dir)


    def relative_path(cls, path_a, path_b):
        '''get the relative path between two paths.  These will include
        file names and should be handled differently'''
        dir_a = os.path.dirname(path_a)
        #file_a = os.path.dirname(file_a)
        dir_b = os.path.dirname(path_b)
        file_b = os.path.basename(path_b)
        rel_dir = cls.relative_dir(dir_a, dir_b)
        return "%s/%s" % (rel_dir, file_b)

    relative_path = classmethod(relative_path)


    def generate_random_key(digits=None):
        # generate a random key
        random.seed()
        random_key = ""
        for i in range(0,19):
            random_key += chr(random.randint(0,255))
        #random_key = md5.new(random_key).hexdigest()
        random_key = hashlib.md5(random_key).hexdigest()
        if digits:
            random_key = random_key[:digits]
        return random_key
    generate_random_key = staticmethod(generate_random_key)



    def generate_alphanum_key(num_digits=10, mode="alpha"):
        if mode == "alpha":
            low = 65
            high = 90
        else:
            log = 48
            high = 90
        # generate a random key
        key = ""
        for i in range(0, num_digits):
            idx = 58
            while idx >= 58 and idx <= 64:
                idx = random.randint(low, high)
            key += chr(idx)

        return key
    generate_alphanum_key = staticmethod(generate_alphanum_key)




    def extract_keywords(data, lower=True):

        if not isinstance(data, basestring):
            data = str(data)

        is_ascii = Common.is_ascii(data)

        data = re.sub(r'([_|,\n])+', ' ', data)
        if is_ascii:
            # other non ASCII languages don't need these
            data = re.sub(r'([^\s\w\'/\.])+', '', data)
        # lowercase is still needed for a mix of ASCII and non-ASCII like a french word
        if lower:
            data = data.lower()
        data = data.split(" ")
        data = [x for x in data if x]
        return data
    extract_keywords = staticmethod(extract_keywords)


    def is_ascii(value):
        '''check if a value is ASCII'''
        is_ascii = True   
        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            is_ascii = False
        except Exception, e:
            is_acii = False
        else:
            is_ascii = True

        return is_ascii

    is_ascii = staticmethod(is_ascii)


    def download(url, to_dir=".", filename='', md5_checksum=""):
        '''Download a file from a given url

        @param:
            url - the url source location of the file

        @keyparam:
            to_dir - the directory to download to
            filename - the filename to download to, defaults to original filename
            md5_checksum - an md5 checksum to match the file against

        @return:
            string - path of the file donwloaded
        '''

        # use url filename by default
        if not filename:
            filename = os.path.basename(url)


        # make sure the directory exists
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        to_path = "%s/%s" % (to_dir, filename)


        # check if this file is already downloaded.  if so, skip
        if os.path.exists(to_path):
            # if it exists, check the MD5 checksum
            if md5_checksum:
                if my._md5_check(to_path, md5_checksum):
                    print "skipping '%s', already exists" % to_path
                    return to_path
            else:
                # always download if no md5_checksum available
                pass


        f = urllib.urlopen(url)
        file = open(to_path, "wb")
        file.write( f.read() )
        file.close()
        f.close()

        return to_path

    download = staticmethod(download)




    def get_user_name():
        '''win32 code to get the user'''
        if os.name == "nt":
            # Taken from:
            # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66314
            import win32api
            #import win32net
            #import win32netcon
            #dc=win32net.NetServerEnum(None,100,win32netcon.SV_TYPE_DOMAIN_CTRL)
            user=win32api.GetUserName()
            """
            if dc[0]:
                dcname=dc[0][0]['name']
                info = win32net.NetUserGetInfo("\\\\"+dcname,user,1)
            else:
                info = win32net.NetUserGetInfo(None,user,1)
            return info['name']
            """
            return user
        else:
            return os.getlogin()
    get_user_name = staticmethod(get_user_name)

      
    def get_os():
        return os.name
    get_os = staticmethod(get_os)
    
    def escape_quote(function):
        p = re.compile("('|\")")
        
        return  p.sub(r"\'", function)
    escape_quote = staticmethod(escape_quote)

    def escape_tag(function):
        function = function.replace('<','&lt;')
        function = function.replace('>','&gt;')
        return  function
    escape_tag = staticmethod(escape_tag)

    def sort_dict(dct, reverse=False):
        ''' sort a dictionary based on its keys, 
            a list of sorted values is returned '''
        keys = dct.keys()
        keys.sort(reverse=reverse)
        return map(dct.get, keys)
    sort_dict = staticmethod(sort_dict)

    def get_dict_list(dct):
        '''get a tuple sorted list given a dictionary'''
        keys = dct.keys()
        keys.sort()
        # value is str() to remove the u' in front of unicode str
        return [(x, dct[x]) for x in keys]
    get_dict_list = staticmethod(get_dict_list)

    def subset_dict(dct, keys):
        return dict([ (i, dct.get(i) ) for i in keys])
    subset_dict = staticmethod(subset_dict)

    def get_unique_list(list):
        ''' get a unique list, order preserving'''
        seen = set()
        return [ x for x in list if x not in seen and not seen.add(x)]
    get_unique_list = staticmethod(get_unique_list)

    """
    def dump_trace(stacktrace):
        '''The argument 'tb' traceback is found by calling:
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)

        This, unfortunately, must be called in the except clause to get
        a proper traceback
        
        ''' 
        stacktrace_str = "".join(stacktrace)
        print "-"*50
        print stacktrace_str
        print "-"*50
    dump_trace = staticmethod(dump_trace)
    """



    def match_ip(a_ip, b_ip, mask):

        a_ip = a_ip.split(".")
        b_ip = b_ip.split(".")
        mask = mask.split(".")

        for count in range(0, 4):
            a_part = int(a_ip[count])
            b_part = int(b_ip[count])
            mask_part = int(mask[count])

            if (a_part & mask_part) != b_part:
                break

        else:
            return True

        return False

    match_ip = staticmethod(match_ip)



    def get_dir_info(dir, skip_dir_details=False):
        '''Finds the disk size of a path'''

        info = {}

        count = 0
        dir_size = 0


        if dir.find("#") != -1:
            dir_size = 0
            file_type = 'sequence'
        elif not os.path.exists(dir):
            dir_size = 0
            file_type = 'missing'
        elif os.path.islink(dir):
            count = 0
            dir_size = 0
            dir_size += os.path.getsize(dir)
            file_type = 'link'
        elif os.path.isdir(dir):
            # this part is too slow
            if not skip_dir_details:
                for (path, dirs, files) in os.walk(unicode(dir)):
                    for file in files:
                        filename = os.path.join(path, file)
                        if os.path.islink(filename):
                            # ignore links
                            pass                        
                        else:
                            try: 
                                dir_size += os.path.getsize(filename)
                            except:
                                continue

                                
                        count += 1
            file_type = 'directory'
        else:
            dir_size = os.path.getsize(dir)
            count = 1
            file_type = 'file'

        info['size'] = dir_size
        info['count'] = count
        info['file_type'] = file_type
            
        return info
    get_dir_info = staticmethod(get_dir_info)


    def unzip_file(file_path, dir=None):
        if not zipfile.is_zipfile(file_path):
            from environment import Environment
            Environment.add_warning('invalid zip file', file_path)
        if dir:
            os.mkdir(dir, 0777)
        else:
            dir, filename = os.path.split(file_path)
        zf_obj = zipfile.ZipFile(file_path)

        files = []
        for name in zf_obj.namelist():
            if name.endswith('/'):
                os.mkdir(os.path.join(dir, name))
            else:
                outfile_path = os.path.join(dir, name)
                outfile = open(outfile_path, 'wb')
                outfile.write(zf_obj.read(name))
                outfile.close()
                files.append(outfile_path)

        return files
    unzip_file = staticmethod(unzip_file)


    def get_filesystem_name(filename):
        # FIXME: for now, turn it off
        return filename
    get_filesystem_name = staticmethod(get_filesystem_name)


    def clean_filesystem_name(filename):
        '''take a name and converts it to a name that can be saved in
        the filesystem. This is different from File.get_filesystem_name()'''


        # handle python style
        p = re.compile("^__(\w+)__.py$")
        if p.match(filename):
            return filename
        

        processed = []
        # remove unwanted mixed delimiters.  Double delimiters of -- and __ are
        # ok, but not double ..
        last_char = None
        length = len(filename)
        for i, char in enumerate(filename):

            if char == ' ':
                char = '_'

            if i == length - 1:
                next_char = None
            else:
                next_char = filename[i+1]

            if char == '.' and last_char == '.':
                continue
            
            if char in ['_','-']:
                if last_char == '.'or next_char == '.':
                    continue
                elif char == '-' and (last_char == '_' or next_char == '_'):
                    continue
                elif char == '-' and last_char == '!':
                    continue
                elif char == '_' and last_char == '!':
                    continue
                else:
                    processed.append(char)

            elif char == '%' and next_char == '0':
                processed.append(char)
            elif char in ':' and i == 1:
                # handle windows C:
                processed.append(char)
            elif char in '''!@$%^&*()={}[]:"|;'\\<>?''':
                pass

            else:
                processed.append(char)

            last_char = char

        # remove trailing . if any
        if processed and processed[-1] == '.':
            processed.pop()

        filename = "".join(processed)

        filename = filename.replace("//", "/")


        return filename

    clean_filesystem_name = staticmethod(clean_filesystem_name)




    def get_keywords_from_path(cls, rel_path):
        # delimiters 
        P_delimiters = re.compile("[- _\.]")
        # special characters
        P_special_chars = re.compile("[\[\]{}\(\)\,]")
        # camel case
        P_camel_case = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


        parts = rel_path.split("/")
        keywords = set()

        for item in parts:
            item = P_camel_case.sub(r'_\1', item)
            parts2 = re.split(P_delimiters, item)
            for item2 in parts2:
                if not item2:
                    continue

                item2 = re.sub(P_special_chars, "", item2)

                # skip 1 letter keywords
                if len(item2) == 1:
                    continue

                try:
                    int(item2)
                    continue
                except:
                    pass


                #print "item: ", item2
                item2 = item2.lower()

                keywords.add(item2)

        keywords_list = list(keywords)
        keywords_list.sort()
        return keywords_list

    get_keywords_from_path = classmethod(get_keywords_from_path)



    #
    # String manipulation functions
    #

    def expand_env(base_dir):
        '''expand the environment variables in a string
           e.g. $(CLASSPATH)/admin/'''
        pat = re.compile('\$\(([^)]*)\)')
        # find one or more $()
        s = pat.finditer(base_dir)
        expanded = []
        iter_s = []
        for i in s:
            temp_str = base_dir[i.start()+2:i.end()-1]
            expanded_temp_str = os.getenv(temp_str)
            expanded.append(expanded_temp_str)
            iter_s.append(i.group())
        for idx, i in enumerate(iter_s):
            base_dir = base_dir.replace(i, expanded[idx])
        base_dir = base_dir.replace('\\', '/')
        return base_dir
    expand_env = staticmethod(expand_env)


    def get_display_title(title):
        title = title.strip()
        if title.find("_") == -1:
            # camelcase
            p = re.compile("([A-Z])")
            replace = " \\1"
            return p.sub(replace, title).strip().title()
            
        else:
            title = title.replace("_", " ")
            return title.title()
    get_display_title = staticmethod(get_display_title)



    def process_unicode_string( in_string ):
        if isinstance(in_string, unicode):
            return in_string.encode('utf-8')
        elif isinstance(in_string, basestring):
            return in_string

        else:
            # for integer and floats
            return str(in_string)
    process_unicode_string = staticmethod(process_unicode_string)


    def convert_to_strings(my, array):
        new = []
        for x in array:
            if not isinstance(array, basestring):
                x = str(array)
            new.append(x)
        return new



    def convert_to_json(data):
        regex = re.compile( r'\n\s*' )
        dict_str = jsondumps(data)
        dict_str = dict_str.replace('"', '&quot;')
        return dict_str
    convert_to_json = staticmethod(convert_to_json)
        


    def pretty_print(data):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
    pretty_print = staticmethod(pretty_print)


    def get_pretty_print(data):
        data_str = StringIO.StringIO()
        pprint.pprint(data, indent=4, stream=data_str)
        return data_str.getvalue()
    get_pretty_print = staticmethod(get_pretty_print)



    def modify_color(color, modifier):

        if not modifier:
            return color
            
        if not color:
            return None

        color = color.replace("#", '')

        if color in ['grey', 'blue', 'red']:
            return color

        if len(color) == 3:
            first = "%s%s" % (color[0], color[0])
            second = "%s%s" % (color[1], color[1])
            third = "%s%s" % (color[2], color[2])
        elif len(color) == 6:
            first = "%s" % color[0:2]
            second = "%s" % color[2:4]
            third = "%s" % color[4:6]
        else:
            return color



        first =  float(int(first, 16) ) / 256
        second = float(int(second, 16) ) / 256
        third =  float(int(third, 16) ) / 256

        if type(modifier) == types.ListType:
            rgb = []
            rgb.append( 0.01*modifier[0] + first )
            rgb.append( 0.01*modifier[1] + second )
            rgb.append( 0.01*modifier[2] + third )
        else:

            hsv = colorsys.rgb_to_hsv(first, second, third)
            value = 0.01*modifier + hsv[2]
            if value < 0:
                value = 0
            if value > 1:
                value = 1
            hsv = (hsv[0], hsv[1], value )
            rgb = colorsys.hsv_to_rgb(*hsv)


        first =  hex(int(rgb[0]*256))[2:]
        if len(first) == 1:
            first = "0%s" % first
        second = hex(int(rgb[1]*256))[2:]
        if len(second) == 1:
            second = "0%s" % second
        third =  hex(int(rgb[2]*256))[2:]
        if len(third) == 1:
            third = "0%s" % third

        if len(first) == 3:
            first = "FF"
        if len(second) == 3:
            second = "FF"
        if len(third) == 3:
            third = "FF"

        color = "#%s%s%s" % (first, second, third)
        return color

    modify_color = staticmethod(modify_color)







    def extract_dict(value, expression):
        '''Given a string and an expression, return a dictionary for the corresponding arg name:value'''
        re_expression = expression

        token = []
        args = {}
        args_keys = []
        index = 0
        for char in expression:

            if char == "{":
                token = "".join(token)
                token = []
            elif char == "}":
                token = "".join(token)
                args_keys.append(token)
                re_expression = re_expression.replace("{%s}"%token, "([\w/=\?&\.-]+)")
                token = []
            else:
                token.append(char)

        #print re_expression
        p = re.compile(re_expression)
        m = p.search(value)
        if m:
            matches = m.groups()
            for key, match in zip(args_keys, matches):
                args[key] = match

        return args

    extract_dict = staticmethod(extract_dict)



    def get_next_code(code, min_padding=3):
        '''function to get the next code with a minimum padding
        For example: chr001 -> chr002
        '''
        p = re.compile("(.*?)(\d+)$")
        m = p.findall(code)
        if m:
            match = m[0]
            base = match[0]
            number = match[1]
            padding = len(number)
            number = int(number)
        else:
            number = 0
            padding = 1
            base = code

        if padding < min_padding:
            padding = min_padding

        next = number + 1
        next_str = "%s%s" % (base, "%%0.%sd" % padding % next) 
        return next_str
    get_next_code = staticmethod(get_next_code)


    def total_size(o, handlers={}, verbose=False):
        # Taken from:
        #http://code.activestate.com/recipes/577504-compute-memory-footprint-of-an-object-and-its-cont/
        """ Returns the approximate memory footprint an object and all of its contents.

        Automatically finds the contents of the following builtin containers and
        their subclasses:  tuple, list, deque, dict, set and frozenset.
        To search other containers, add handlers to iterate over their contents:

            handlers = {SomeContainerClass: iter,
                        OtherContainerClass: OtherContainerClass.get_elements}

        """
        from sys import getsizeof
        from itertools import chain
        from collections import deque


        dict_handler = lambda d: chain.from_iterable(d.items())
        all_handlers = {tuple: iter,
                        list: iter,
                        deque: iter,
                        dict: dict_handler,
                        set: iter,
                        frozenset: iter,
                       }
        all_handlers.update(handlers)     # user handlers take precedence
        seen = set()                      # track which object id's have already been seen
        default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

        def sizeof(o):
            from sys import getsizeof, stderr
            try:
                from reprlib import repr
            except ImportError:
                pass

            if id(o) in seen:       # do not double count the same object
                return 0
            seen.add(id(o))
            s = getsizeof(o, default_size)

            if verbose:
                print(s, type(o), repr(o))

            for typ, handler in all_handlers.items():
                if isinstance(o, typ):
                    s += sum(map(sizeof, handler(o)))
                    break
            return s

        return sizeof(o)

    total_size = staticmethod(total_size)


    # take from: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    which = staticmethod(which)


    def kill(pid=None):
        '''Kills the current program.'''
        import sys
        if not pid:
            pid = os.getpid()
        pid = int(pid)

        if os.name =='nt':
            # for windows
            python = sys.executable
            python = python.replace('\\','/')
            import subprocess
            subprocess.Popen([python, sys.argv])
            kill = KillProcessThread(pid)
            kill.start()
        else:
            os.kill(pid, 1)
    kill = staticmethod(kill)



    def restart():
        '''Restarts the current program.'''
        import sys
        python = sys.executable
        # for windows
        print "Restarting the process. . ."
        print
        python = python.replace('\\','/')
        if os.name =='nt':
            import subprocess
            cmd_list = [python]
            cmd_list.extend(sys.argv)
            subprocess.Popen(cmd_list)
            pid = os.getpid()
            kill = KillProcessThread(pid)
            kill.start()
        else:
            os.execl(python, python, * sys.argv)
    restart = staticmethod(restart)


class KillProcessThread(threading.Thread):
    '''Kill a Windows process'''
    def __init__(my, pid):
        super(KillProcessThread, my).__init__()
        my.pid = pid

    def run(my):
        """kill function for Win32 prior to Python2.7"""
       
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, my.pid)
        kernel32.TerminateProcess(handle, -1)
        rtn = kernel32.CloseHandle(handle)
        return (0 != rtn)


gl = globals()
lc = locals()


import binascii, pickle
try:
    import zlib
    HAS_ZLIB = True
except ImportError:
    HAS_ZLIB = False

class Marshaller:
    '''Marshals object creation to send over the web for dynamic creation.
    The problem with pickling is that it is not really web friendly.  Nor
    is it encrypted (not that encryption is all that important or secure here).
    The detail of the communication protocol, is completely
    encapsulated in this class and should never be exposed externally

    NOTE: this could be replaced by AJAX which uses a standard XML interface
    to marshal function calls to the server
    '''

    def __init__(my, class_path=None):
        my.set_class(class_path)

        my.options = {}
        my.args = []
        my.kwargs = {}


    def set_class(my, class_path):
        if not class_path:
            my.class_path = None
        elif type(class_path) in types.StringTypes:
            my.class_path = class_path
        elif type(class_path) == types.TypeType:
            # do some wonky stuff
            p = re.compile(r"<class '(.*)'>")
            m = p.findall(str(class_path))
            if not m:
                raise Exception("Cannot find class name for: %s" % str(class_path))
            my.class_path = m[0]
            
        else:
            my.class_path = Common.get_full_class_name(class_path)


    def set_option(my, name, value):
        my.options[name] = value

    def add_arg(my, arg):
        my.args.append(arg)

    def add_kwarg(my, name, value):
        my.kwargs[name] = value
    
    def set_kwargs(my, kwargs):
        # ensure all keywords are strings
        my.kwargs = {}
        for name, value in kwargs.items():
            my.kwargs[str(name)] = value
        #my.kwargs = kwargs

    def get_object(my):
        # dynamic creation using a string argument like the command line
        (module_name, class_name) = Common.breakup_class_path(my.class_path)
        unique_class_name = "%s%s" % (module_name.replace(".",""), class_name)

        args = ",".join(["my.args[%s]" % i for i in range(0,len(my.args))] )
        try:
            if module_name.startswith("tactic.plugins."):
                import tactic.plugins
                parts = module_name.split(".")
                plugin = parts[2]
                parts.append(class_name)
                rest = ".".join( parts[3:] )
                module = tactic.plugins.import_plugin(plugin)
                unique_class_name = "module.%s" % rest

            if my.kwargs and args:
                object = eval("%s(%s, **my.kwargs)" % (unique_class_name, args))
            elif my.kwargs:
                object = eval("%s(**my.kwargs)" % (unique_class_name) )
            else:
                object = eval("%s(%s)" % (unique_class_name, args) )
        except NameError:
            if module_name != "":
                try:
                    #print( "from %s import %s as %s" % (module_name,class_name, unique_class_name))
                    exec( "from %s import %s as %s" % (module_name,class_name, unique_class_name), gl, lc )
                except:
                    print ImportError("Cannot import [%s] from module [%s]" % (class_name, module_name) )
                    raise
            else:
                # standard libraries to import for dynamic loading
                # TODO: This dynamic loading of all of these libraries imparts
                # significant overhead when ihooks are used.  It is probably
                # better to be explicit with all class names
                try:
                    exec("from pyasm.widget import %s" % class_name, gl, lc)
                except ImportError:
                    try:
                        exec("from pyasm.command import %s" % class_name, gl, lc)
                    except ImportError:
                        try:
                            exec("from pyasm.web import %s" % class_name, gl, lc)
                        except ImportError:
                            raise ImportError("Could not find '%s' for import" % my.class_path)


            # now with module loaded, instantiate again
            try:
                if my.kwargs and args:
                    object = eval("%s(%s, **my.kwargs)" % (unique_class_name, args) )
                elif my.kwargs:
                    object = eval("%s(**my.kwargs)" % (unique_class_name) )
                else:
                    object = eval("%s(%s)" % (unique_class_name, args) )

            except Exception, e:
                print("%s: %s" % (class_name, e.__str__()))
                raise
                #raise Exception("%s: %s" % (class_name, e.__str__()))
        except Exception, e:
            print("%s: %s" % (class_name, e.__str__()))
            raise

        # go through each option and set it explicitly
        for option,value in my.options.items():
            eval( "object.set_%s(value)" % option )

        return object




    
    def get_marshalled(my):
        '''use to get a marshalled version of this class'''
        coded = pickle.dumps(my)
        if HAS_ZLIB:
            coded = zlib.compress(coded)
        coded = binascii.hexlify(coded)
        return coded



    def get_from_marshalled(uncoded):
        '''use to decrypt a marshalled version of this class'''
        uncoded = binascii.unhexlify(uncoded)
        if HAS_ZLIB:
            uncoded = zlib.decompress(uncoded)
        marshaller = pickle.loads(uncoded)
        return marshaller
    get_from_marshalled = staticmethod(get_from_marshalled)





# interesting, but can't get it to work ... commenting out for now.  Works
# outside of TACTIC, but not in TACTIC.
"""
import __builtin__
class RollbackImporter:
    '''
    Taken from pyunit and modified to conform to TACTIC style guide
    http://pyunit.sourceforge.net/notes/reloading.html
    Usage:
    def execute(self):
        rollbackImporter = RollbackImporter()
        import <module>
        rollbackImporter.uninstall()

    This will ensure that any module loaded between insantiation and the
    uninstall function will be unloaded

    '''
    def __init__(my):
        "Creates an instance and installs as the global importer"
        my.previousModules = sys.modules.copy()
        print "starting ... "
        my.realImport = __builtin__.__import__
        __builtin__.__import__ = my._import
        print "import: ", __builtin__.__import__
        my.newModules = {}

    def _import(my, name, globals=None, locals=None, fromlist=[]):
        result = apply(my.realImport, (name, globals, locals, fromlist))
        my.newModules[name] = (globals, locals)
        print "loading: ", name
        return result
        
    def uninstall(my):
        print "uninstall ...."
        __builtin__.__import__ = my.realImport
        for modname, modinfo in my.newModules.items():
            if not my.previousModules.has_key(modname):
                # Force reload when modname next imported
                print "modname: ", modname
                if not sys.modules.get(modname):
                    print "WARNING: module [%s] not imported" % modname
                    continue

                #globals = modinfo[0]
                #locals = modinfo[1]

                print "deleting %s" % modname

                print "prehas? ", sys.modules.get(modname)
                del(sys.modules[modname])
                print "has? ", sys.modules.get(modname)
"""





