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

__all__ = ["Naming", "NamingUtil", "NamingException"]

import os, re

from pyasm.common import Xml, TacticException, Container, Environment, Common, Config
from pyasm.search import *

from project import Project
from file import File
from expression import ExpressionParser

class NamingException(TacticException):
    pass


class Naming(SObject):

    SEARCH_TYPE = "config/naming"

    # Commenting this out.  File names can be anything.  We cannot and should
    # not enforce what people think are correct file names for whatever
    # purpose they happen to need it for.

    def validate(my):

        sandbox_dir_name = my.get_value('sandbox_dir_naming')
        dir_naming = my.get_value('dir_naming')

        if sandbox_dir_name.rstrip('/') != sandbox_dir_name:
            raise TacticException('sandbox_dir_naming should not end with /')

        if dir_naming.rstrip('/') != dir_naming:
            raise TacticException('dir_naming should not end with /')
            
        #file_name = my.get_value('file_naming')
        #p = re.compile('.*\.({ext}|\w+)$')
        #if not p.match(file_name):
        #    raise TacticException('file_naming has to end with .{ext} or .xxx')

    def get_by_search_type(search_type):

        # if the project is in admin, then skip this step because there is
        # no database
        # FIXME: this should be handle more gracefully elsewhere
        if Project.get_project_name() == "admin":
            return ""

        naming_dict = Container.get("Naming:cache")
        if naming_dict == None:

            naming_dict = {}
            Container.put("Naming:cache", naming_dict)

            search = Search(Naming)
            namings = search.get_sobjects()

            for naming in namings:
                #value = naming.get_value("file_naming")
                naming_dict[naming.get_value("search_type")] = naming

        return naming_dict.get(search_type)

    get_by_search_type = staticmethod(get_by_search_type)


    def has_versionless(cls, sobject, snapshot, versionless=''):
        '''check to see if a naming is defined''' 
        return cls.get(sobject, snapshot, versionless, mode='check') != None
    has_versionless = classmethod(has_versionless)



    def get(sobject, snapshot, versionless='', file_path='' ,mode='find'):
        '''
        The special check mode is used in versionless to check whether a
        naming convention is defined.  It should only be called by
        has_versionless()

        mode: find - find the naming
              check - check that a naming is defined
        '''

        if not versionless and snapshot:
            version = snapshot.get_value("version")
            if version == -1:
                versionless = 'latest'
            elif version == 0:
                versionless = 'current'
            else:
                versionless = ''

        # get the project of the sobject
        project_code = sobject.get_project_code()

        if versionless:
            cache_key = "Naming:cache:%s:%s" % (project_code, versionless)
        else:
            cache_key = "Naming:cache:%s" % project_code

        naming_dict = Container.get(cache_key)
        if naming_dict == None:

            naming_dict = {}
            Container.put(cache_key, naming_dict)
            namings = Container.get("Naming:namings")
            if namings == None:
                try:
                    search = Search(Naming)
                    namings = search.get_sobjects()
                except SearchException, e:
                    # it is possible that there is no naming table
                    # in this project.  This is possible if the datbase
                    # is just a resource
                    if str(e).find("does not exist for database"):
                        namings = {}
                    else:
                        raise
                Container.put("Naming:namings", namings)

            for naming in namings:
                # depending on whether the snapshot is latest or current
                # switch which column we are looking at
                n_versionless = ''
                latest = naming.get_value("latest_versionless",no_exception=True)
                current = naming.get_value("current_versionless",no_exception=True)

                if versionless == 'latest':
                    if latest == True:
                        n_versionless = 'latest'
                elif versionless == 'current':
                    if current == True:
                        n_versionless = 'current'
                else:
                    if latest == True or current == True:
                        n_versionless = "XXX"
                
                n_search_type = naming.get_value("search_type")
                n_snapshot_type = naming.get_value("snapshot_type")
                n_context = naming.get_value("context")
                key = "|".join( [n_search_type.strip(), n_snapshot_type.strip(), n_context.strip(), str(n_versionless)])
                #key = "|".join( [n_search_type.strip(), n_snapshot_type.strip(), n_context.strip()])
                naming_list = naming_dict.get(key)
                if naming_list == None:
                    naming_list = []
                    naming_dict[key] = naming_list

                naming_list.append(naming)

                #naming_dict[key] = naming
        
        # build the key
        search_type = sobject.get_base_search_type()
        snapshot_type = 'file'
        context = ''

        # supports */<subcontext> and <context>/* 
        context_list = []
        snapshot_version = None

        if snapshot:
            snapshot_type = snapshot.get_value("snapshot_type")
            snapshot_version = snapshot.get_value("version")
            context = snapshot.get_value("context")
            if context:
                context_list.append(context)
                if context.find('/') == -1:
                    context_list.append('%s/*' %context)
                else:
                    parts =  context.split('/')
                    cont = parts[0]
                    subcontext = "/".join(parts[1:])
                    context_list.append('*/%s' %subcontext)
                    context_list.append('%s/*' %cont)

        else:   
            context_list.append('')


        # get the keys to look for
        keys = []
        if mode == 'check' or snapshot_version in [-1, 0]:
            for context in context_list:
                keys.append("%s|%s|%s|%s" % (search_type, snapshot_type, context, versionless ) )
                keys.append("%s||%s|%s" % (search_type,  context, versionless ) )
            keys.append("%s|%s||%s" % (search_type, snapshot_type,  versionless ) )
            keys.append("%s|||%s" % (search_type, versionless ) )

        else:

            for context in context_list:
                keys.append("%s|%s|%s|%s" % (search_type, snapshot_type, context, versionless ) )
                keys.append("%s||%s|%s" % (search_type,  context, versionless ) )
                keys.append("%s|%s|%s|" % (search_type, snapshot_type, context) )
                keys.append("%s||%s|" % (search_type, context) )


            keys.append("%s|%s||%s" % (search_type, snapshot_type,  versionless ) )
            keys.append("%s|%s||" % (search_type, snapshot_type) )
            keys.append("%s|||%s" % (search_type, versionless ) )
            keys.append("%s|||" % (search_type) )


            # these 2 are questionable, we should always include search_type
            for context in context_list:
                keys.append("||%s|" % (context) )
            keys.append("|%s||" % (snapshot_type) )

            keys.append("")

        naming = None
        
        from pyasm.biz import ExpressionParser
        xp = ExpressionParser()
                    
        base_name = os.path.basename(file_path)
        base, ext = os.path.splitext(base_name)
        if not ext:
            value = None
        else:
            # external ext starts with a .
            ext = ext.lstrip(".")
            value = ext
        vars = {'EXT': value, 'BASEFILE': base}

        for key in keys:
            if naming:
                break
            naming_list = naming_dict.get(key)
            if naming_list:
                # now that we have the namings, evaluate the expression
                default_naming = None
                for tmp_naming in naming_list:
                    expr = tmp_naming.get_value("condition", no_exception=True)

                    # if there is no expression, then this is the default
                    # for this match
                    if not expr:
                        default_naming = tmp_naming
                   
                    elif xp.eval(expr, sobject, vars=vars):
                        naming = tmp_naming
                        break

                else:
                    # this extra check of not naming is for precaution 
                    if not naming and default_naming:
                        naming = default_naming
                        break

        return naming

    get = staticmethod(get)






class NamingUtil(object):
    '''Interface to simply specifying naming convention'''


    #
    # try a new naming language which makes use of simple expression language
    #
    def naming_to_file(my, template, sobject, snapshot, file=None, ext=None, file_type=None):
        '''
        # chr001_model_v004_00001.ext
        '''


        version_padding = Config.get_value("checkin", "version_padding")
        if version_padding:
            version_padding = int(version_padding)
        else:
            version_padding = 3
        version_expr = "%%0.%dd" % version_padding


        # the main sobject
        project = sobject.get_project()

        # parse the pattern string
        expression = re.compile(r'{([\w|\.|\#]+\[?\d?\]?)}')
        temp_list = expression.findall(template)

        # if nothing is found, then just return parse through an expression
        if not temp_list:
            #return template
            # put in the ability to add expressions
            from pyasm.biz import ExpressionParser
            xp = ExpressionParser()
            env_sobjects = {
                'snapshot': snapshot,
                'file': file
            }
            file_name = file.get_value("file_name")
            base_type = file.get_value("base_type")
            if base_type =='directory':
                base = file_name
                ext = None
            else:
                base, ext = os.path.splitext(file_name)
            if not ext:
                value = None
            else:
                # external ext starts with a .
                ext = ext.lstrip(".")
                value = ext
            vars = {'EXT': value, 'BASEFILE': base}
            
            result = xp.eval(template, sobject, mode='string', env_sobjects=env_sobjects, vars=vars)
            test = template
            test = test.replace("{", "")
            test = test.replace("}", "")
            # don't allow / in filename
            test = test.replace("/", "_")
            if test != result:
                return result

        result = template
        for part in temp_list:
            index = -1
            if part.find(".") != -1:
                # explict declarations
                object, attr = part.split(".")
                
                if attr.endswith(']'):
                    # ugly, but it works
                    attr, index = attr.split("[")
                    index = int(index.rstrip("]"))

                if object == "sobject":
                    value = sobject.get_value(attr)
                elif object == "snapshot":
                    if not snapshot:
                        continue
                    value = snapshot.get_value(attr)
                    if attr in ['version', 'revision']:
                        if value:
                            value = version_expr % int(value)
                        else:
                            value = "0"*version_padding
                    #value = snapshot.get_value(attr)
                elif object == "file":
                    if attr == 'file_type':
                        if file_type:
                            value = file_type
                        else:
                            value = 'main'
                    else:
                        value = file.get_value(attr)

                elif object == "parent":
                    parent = sobject.get_parent()
                    if not parent:
                        value = "NO_PARENT"
                    else:
                        value = parent.get_value(attr)
                elif object in ["login","user"]:
                    login = Environment.get_login()
                    value = login.get_value(attr)
                elif object == "project":
                    project = Project.get()
                    value = project.get_value(attr)
                else:
                    raise NamingException("Can't parse part [%s] in template" % part)

            else:
                # use implicit declarations
                attr = part

                
                if attr.endswith(']'):
                    # ugly, but it works
                    attr, index = attr.split("[")
                    index = int(index.rstrip("]"))    

                if attr == "context":
                    value = snapshot.get_value(attr)
                elif attr == "snapshot_type":
                    value = snapshot.get_value(attr)
                elif attr == "version":
                    value = snapshot.get_value(attr)
                    if value:
                        value = version_expr % int(value)
                    else:
                        value = "0"*version_padding
                elif attr == "revision":
                    value = snapshot.get_value(attr)
                    if value:
                        value = version_expr % int(value)
                    else:
                        value = "0"*version_padding

                elif attr.startswith("#"):
                    if not snapshot:
                        continue
                    value = snapshot.get_value("version")

                    expr = "%%0.%sd" % len(attr)
                    if value:
                        value = expr % int(value)
                    else:
                        value = "0" * len(attr)

                elif attr == "basefile":
                    file_name = file.get_value("file_name")
                    base_type = file.get_value("base_type")
                    if base_type =='directory':
                        value = file_name
                    else:
                        base, ext = os.path.splitext(file_name)
                        value = base
                elif attr == "ext":
                    if not ext:
                        file_name = file.get_value("file_name")
                        base_type = file.get_value("base_type")
                        if base_type =='directory':
                            value = ''
                        else:
                            base, ext = os.path.splitext(file_name)
                            value = ext.lstrip(".")
                    else:
                        # external ext starts with a .
                        ext = ext.lstrip(".")
                        value = ext
                elif attr in ["login","user"]:
                    login = Environment.get_login()
                    value = login.get_value("login")

                elif attr == "file_type":
                    if file_type:
                        value = file_type
                    else:
                        value = 'main'

                elif attr.startswith('date'):
                    # {date,%Y-%m-%d_%H-%M-%S]}
                    import time
                    parts = attr.split(",", 1)
                    if len(parts) == 2:
                        format = parts[1]
                    else:
                        format = "%Y%m%d"
                    value = time.strftime(format, time.localtime())


                else:
                    value = sobject.get_value(attr)

            # tbis applies to context for now
            if index != -1:
                value = re.split("[/]", value)
                if len(value) <= index:
                    value = '!'
                else:
                    value = value[index]


            #if not value:
            #    raise NamingException("Value for part [%s] is empty" % part)
            if isinstance(value, int):
                value = str(value)
            
            result = result.replace("{%s}" % part, value)

        # don't allow / in filename, 
        # FIXME: it's not put in get_filesystem_name since it
        # is used for directory name also, need to modify that
        result = result.replace("/", "_")
        # post process result so that it looks good
        result = Common.get_filesystem_name(result)
                

        return result
             
    def _get_timestamp(my, sobject):
        '''get the portion yyyy-mm-dd'''
        return sobject.get_value('timestamp')[0:10]

    def naming_to_dir(my, template, sobject, snapshot, file=None, file_type=None):
        '''
        # shot/SEQ001/shot_001
        '''

        # the main sobject
        project = sobject.get_project()

        # parse the pattern string
        expression = re.compile(r'{([\w|\.|\#]+\[?\d?\]?)}')
        temp_list = expression.findall(template)

        # if nothing is found, then just return parse through an expression
        if not temp_list:
            #return template

            # put in the ability to add expressions
            from pyasm.biz import ExpressionParser
            xp = ExpressionParser()
            env_sobjects = {
                'snapshot': snapshot,
                'file': file
            }
            result = xp.eval(template, sobject, mode='string', env_sobjects=env_sobjects)
            test = template
            test = test.replace("{", "")
            test = test.replace("}", "")
            if test != result:
                return result


        # version padding defaults
        version_padding = Config.get_value("checkin", "version_padding")
        if version_padding:
            version_padding = int(version_padding)
        else:
            version_padding = 3
        version_expr = "%%0.%dd" % version_padding



        # use simplified expressions
        result = template
        for part in temp_list:
             
            index = -1
            if part.find(".") != -1:
                # explict declarasions
                object, attr = part.split(".")
                
                if attr.endswith(']'):
                    # ugly, but it works
                    attr, index = attr.split("[")
                    index = int(index.rstrip("]"))
                if object == "sobject":
                    if attr == "timestamp":
                        value = my._get_timestamp(sobject)
                    else:
                        value = sobject.get_value(attr)
                elif object == "snapshot":
                    if not snapshot:
                        continue
                    if attr == "timestamp":
                        value = my._get_timestamp(snapshot)
                    else:
                        value = snapshot.get_value(attr)
                    if attr in ['version', 'revision']:
                        if value:
                            value = version_expr % int(value)
                        else:
                            value = "0"*version_padding
                elif object == "search_type":
                    search_type_obj = sobject.get_search_type_obj()
                    value = search_type_obj.get_value(attr)
                elif object == "parent":
                    parent = sobject.get_parent()
                    if not parent:
                        value = "NO_PARENT"
                    else:
                        if attr == 'timestamp':
                            value = my._get_timestamp(parent)
                        else:
                            value = parent.get_value(attr)
                elif object == "project":
                    project = Project.get()
                    value = project.get_value(attr)
                elif object in ["login","user"]:
                    login = Environment.get_login()
                    value = login.get_value(attr)
                elif object == "file":
                    if attr == 'file_type':
                        if file_type:
                            value = file_type
                        else:
                            value = 'main'
                    else:
                        value = file.get_value(attr)

                else:
                    raise NamingException("Can't parse part [%s] in template" % part)

            else:
                # use implicit declarations
                attr = part
                if attr.endswith(']'):
                    # ugly, but it works
                    attr, index = attr.split("[")
                    index = int(index.rstrip("]"))
                
                if attr in ['context','snapshot_type','version','revision'] \
                    and not snapshot:
                    continue
                if attr == "context":
                    value = snapshot.get_value(attr)
                elif attr == "snapshot_type":
                    value = snapshot.get_value(attr)
                elif attr == "version":
                    value = snapshot.get_value(attr)
                    if value:
                        value = version_expr % int(value)
                    else:
                        value = "0"*version_padding
                elif attr == "revision":
                    value = snapshot.get_value(attr)
                    if value:
                        value = version_expr % int(value)
                    else:
                        value = "0"*version_padding

                elif attr.startswith("#"):
                    if not snapshot:
                        continue
                    value = snapshot.get_value("version")
                    expr = "%%0.%sd" % len(attr)
                    if value:
                        value = expr % int(value)
                    else:
                        value = "0" * len(attr)

                elif attr.startswith("id"):
                    value = "%0.5d" % sobject.get_id()

                elif attr in ["login","user"]:
                    login = Environment.get_login()
                    value = login.get_value("login")

                elif attr == "file_type":
                    if file_type:
                        value = file_type
                    else:
                        value = 'main'
                else:
                    if attr == "timestamp":
                        value = my._get_timestamp(sobject)
                    else:
                        value = sobject.get_value(attr)

            if index != -1:
                value = re.split("[/]", value)
                if len(value) <= index:
                    value = '!'
                else:
                    try:
                        value = value[index]
                    except IndexError, e:
                        value = ""



            if not sobject.is_insert() and not value:
                raise NamingException("Naming convention error: Value for part [%s] is empty" % part)
          
            if isinstance(value, int):
                value = str(value)
            result = result.replace("{%s}" % part, value)

        # post process result so that it looks good
        result = Common.get_filesystem_name(result)

        return result
 
    def build_naming(my, sample_name):
        separators = ['/','\\','.', '_', '-']

        # build a naming convention ui
        # sample_name = "chr001_model_v004.0001.ext"
        #                |....| |...| |..| |..| |.|
        #                p     sp    sp   sp   sp

        naming = ""
        count = 0
        for pos, char in enumerate(sample_name):
            if char in separators:
                if pos:
                    naming += char

                naming += "{%d}" % count
                count += 1
            elif not pos:
                naming += "{%d}" % count
                count += 1


        return naming




    def eval_template(template, sobject=None, parent=None, snapshot=None):
        ''' generic method to values an sobject template expression'''
        # parse the pattern string
        expression = re.compile(r'{([\w|\.|\#]+\[?\d?\]?)}')
        temp_list = expression.findall(template)

        # if nothing is found, then just return parse through an expression
        if not temp_list:
            #return template
            # put in the ability to add expressions
            env_sobjects = {
                'snapshot': snapshot
            }
            xp = ExpressionParser()
            result = xp.eval(template, sobject, mode='string', env_sobjects=env_sobjects)
          
            test = template
            test = test.replace("{", "")
            test = test.replace("}", "")
            if test != result:
                return result

             

        # if nothing is found, temp_list is empty
        if not temp_list:
            temp_list = []

        # the main sobject
        if sobject:
            project = sobject.get_project()
        else:
            project = Project.get()


        result = template
        for part in temp_list:

            if part.find(".") != -1:
                # explict declarasions
                object, attr = part.split(".")

                index = -1
                if attr.endswith(']'):
                    # ugly, but it works
                    attr, index = attr.split("[")
                    index = int(index.rstrip("]"))
                    


                if object == "sobject":
                    value = sobject.get_value(attr)

                elif object == "parent":
                    if not parent:
                        parent = sobject.get_parent()
                    if parent:
                        value = parent.get_value(attr)
                    else:
                        value = ''

                elif object in ["login", "user"]:
                    login = Environment.get_security().get_login()
                    value = login.get_value(attr)

                else:
                    raise NamingException("Can't parse part [%s] in template" % part)

                if index != -1:
                    value = re.split("[/._]", value)
                    value = value[index]

            else:
                value = part

            result = result.replace("{%s}" % part, str(value))

        return result

    eval_template = staticmethod(eval_template)



