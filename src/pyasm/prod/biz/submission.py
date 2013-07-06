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

__all__ = ['Submission', 'Bin', 'SubmissionInBin']

from pyasm.search import *
from pyasm.biz import Note

class Submission(SObject):
    SEARCH_TYPE = "prod/submission"

    def get_search_columns():
        return ['artist', 'description', 'status', 'search_type']
    get_search_columns = staticmethod(get_search_columns)

    def build_update_description(my, is_insert):
        if is_insert:
            action = "Inserted"
        else:
            action = "Updated"
        title = my.get_search_type_obj().get_title()

        parent = my.get_parent()
        code = ''
        name = ''
        parent_title = ''
        # Manual insert has no parent
        if parent:
            code = parent.get_code()
            name = parent.get_name()
            parent_title = parent.get_search_type_obj().get_title()

        if not code:
            description = "%s %s" %(action, title)
        elif code == name:
            description = "%s %s to %s: %s" % (action, title, parent_title, code)
        else:
            description = "%s %s to %s: %s %s" % (action, title, parent_title, code, name)


        return description


    def get_bins(my):
        '''get all of the bins for this submission'''
        id = my.get_id()
        search = Search(Bin, project_code=my.get_project_code() )
        search.set_show_retired(True)
        search.add_where("\"id\" in (select \"bin_id\" from \"submission_in_bin\" where \"submission_id\" = '%s')" % id )

        bins = Bin.get_by_search(search, id, is_multi=True)
        #bins = search.get_sobjects()
        if bins==None:
            bins = []
        return bins



    # Static methods
    def get_all_notes(sobject, context=None):
        '''gets all of the submission notes for a particular sobject'''
        search = Search(Submission)
        search.add_column("id")
        search.add_sobject_filter(sobject)
        submissions = search.get_sobjects()

        if submissions:
            search = Search(Note)
            search.add_filters("search_id", [x.get_id() for x in submissions] )
            search.add_filter("search_type", submissions[0].get_search_type() )
            if context and context[0]:
                search.add_filters("context", context)
            notes = search.get_sobjects()
            return notes
        else:
            return []

    get_all_notes = staticmethod(get_all_notes)



    
class Bin(SObject):
    SEARCH_TYPE = "prod/bin"

    def get_search_columns():
        return ['code', 'type', 'label']
    get_search_columns = staticmethod(get_search_columns)

    def get_label(my):
        type = my.get_value('type')
        if my.get_value('label'):
            return "%s (%s) - %s" %(my.get_value('code'), \
                my.get_value('label'), type)
        else:
            return "%s - %s" %(my.get_value('code'), type)

    def get_type(my):
        return my.get_value('type')




class SubmissionInBin(SObject):
    SEARCH_TYPE = "prod/submission_in_bin"

