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

__all__ = ['BaseRepoHandler', 'SampleRepoHandler']

from pyasm.common import Common


class BaseRepoHandler(object):

    TACTIC_REPO = "pyasm.checkin.TacticRepo"
    PERFORCE_REPO = "pyasm.checkin.PerforceRepo"
    SUBVERSION_REPO = "pyasm.checkin.SubversionRepo" # not implemented

    def __init__(my):
        my.sobject = None
        my.snapshot = None

    def get_repo_class(my):
        '''You can define which repo class is used based on certain conditions
        This gives the ability to use different styles and or 3rd party
        repositories such as Perforce or Subversion'''
        return my.TACTIC_REPO


    def set_sobject(my, sobject):
        my.sobject = sobject

    def set_snapshot(my, snapshot):
        my.snapshot = snapshot


    def get_repo(my):
        repo_handler = my.get_repo_class()
        repo = Common.create_from_class_path(repo_handler)
        return repo



    def is_tactic_repo(my):
        '''returns whether the current state is a tactic repo'''

        repo_handler = my.get_repo_class()
        if repo_handler == my.TACTIC_REPO:
            return True
        else:
            return False




class SampleRepoHandler(BaseRepoHandler):

    def get_repo_class(my):
        context = my.snapshot.get_value("context")

        search_type = my.sobject.get_base_search_type()

        # all contexts of game are sent to perforce
        if context == "Game Ready":
            return my.PERFORCE_REPO

        #elif search_type == "prod/texture":
        #    asset_context = my.sobject.get_value("asset_context")
        #    if asset_context == "model":
        #        return my.PERFORCE_REPO
        #    else:
        #        return my.TACTIC_REPO

        else:
            return my.TACTIC_REPO




