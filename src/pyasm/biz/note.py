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

__all__ = ["Note"]

from pyasm.common import Environment
from pyasm.security import Security
from pyasm.search import SearchType, SObject, Search

from project import Project

class Note(SObject):

    SEARCH_TYPE = "sthpw/note"

    def get_search_columns():
        return ['context','note']
    get_search_columns = staticmethod(get_search_columns)

    def get_required_columns():
        '''for csv import'''
        return ['search_type', 'search_id', 'context', 'note', 'login','project_code', 'timestamp']
    get_required_columns = staticmethod(get_required_columns)

    def get_defaults(my):
        context = my.get_value("context")
        defaults = {
            "process": context,
            "project_code": Project.get_project_code()
        }
        return defaults

    def alter_search(search):
        # always restrict access from others
        security = Environment.get_security()
        if security.check_access("builtin", "view_private_notes", 'view', default='deny'):
            return
        
        user = Environment.get_user_name() 
        search.add_op('begin')
        search.add_op('begin')
        search.add_filter("access", "private", op='=')
        search.add_user_filter()
        search.add_op("and")
        search.add_op('begin')
        search.add_filter("access", "private", op='!=')
        search.add_filter("access", None)
        search.add_op("or")
        search.add_op("or")
        #print search.get_statement()
    alter_search = staticmethod(alter_search)

    def get_login(my):
        return my.get_value('login')

    def get_status(my):
        return my.get_value('status')

    def get_parent_id(my):
        return my.get_value('parent_id')

    def get_process(my):
        note_process = my.get_value('process')
        if not note_process:
            note_process = my.get_value('context')
        return note_process

    def get_child_notes(my):
        '''get all the child notes'''
        search = Search( Note.SEARCH_TYPE )
        search.add_filter('parent_id', my.get_id())
        return search.get_sobjects()

    def copy_note(my, new_sobj_parent, parent=None):
        '''copy this note to a new parent
            @new_sobj_parent: the sobject this note relates to
            @parent: the parent note if applicable'''
        value = my.get_value('note')
        context = my.get_value('context')
        process = my.get_value('process')
        time = ''
        
        parent_id = ''
        if parent:
            parent_id = parent.get_id()
            time = my.get_value('timestamp')
        note = Note.create( new_sobj_parent, value, context=context,\
                process=process,  parent_id=parent_id, time=time )
        return note

    def build_update_description(my, is_insert=True):
        '''This is asked for by the edit widget and possibly other commands'''
        if is_insert:
            action = "Inserted"
        else:
            action = "Updated"
        title = my.get_search_type_obj().get_title()

        # we are interested in the parent
        parent = my.get_parent()
        code = ''
        if parent:
            code = "%s-%s" %(parent.get_search_type_obj().get_title(), \
                parent.get_code())
        description = "%s %s: %s" % (action, title, code)

        return description

    def get_search_by_sobjects(cls, sobjects):
        '''adds a filter to the search to get the related'''
        if not sobjects:
            return None

        sobject = sobjects[0]

        search = Search( cls.SEARCH_TYPE )
        if len(sobjects) == 1:
            search_id = sobject.get_id()
            search.add_filter("search_id", search_id)
        else:
            search_ids = [x.get_id() for x in sobjects]
            search.add_filters("search_id", search_ids)


        search_type = sobject.get_search_type()
        search.add_filter("search_type", search_type)
        search.add_order_by("search_type")
        search.add_order_by("search_id")

        return search


    get_search_by_sobjects = classmethod(get_search_by_sobjects)


    def create(sobject, value, context=None, process=None, parent_id=0, time=''):

        note = Note.create_new()
        note.set_user()
        project = sobject.get_project_code()
        note.set_value("project_code", project)


        if context:
            note.set_value("context", context)
        if process:
            note.set_value("process", process)

        if not context and process:
            note.set_value("context", process)

        if not process and context:
            parts = context.split("/")
            note.set_value("process", parts[0])

        if not process and not context:
            note.set_value("process", "publish")
            note.set_value("context", "publish")


        if parent_id:
            note.set_value("parent_id", parent_id)
        if time:
            note.set_value("timestamp" , str(time))

        note.set_value("note", value)
        
        note.set_sobject_value(sobject)

        note.commit()

        return note

    create = staticmethod(create)    


