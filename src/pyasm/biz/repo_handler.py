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

    def __init__(self):
        self.sobject = None
        self.snapshot = None

    def get_repo_class(self):
        '''You can define which repo class is used based on certain conditions
        This gives the ability to use different styles and or 3rd party
        repositories such as Perforce or Subversion'''
        return self.TACTIC_REPO


    def set_sobject(self, sobject):
        self.sobject = sobject

    def set_snapshot(self, snapshot):
        self.snapshot = snapshot


    def get_repo(self):
        repo_handler = self.get_repo_class()
        repo = Common.create_from_class_path(repo_handler)
        return repo



    def is_tactic_repo(self):
        '''returns whether the current state is a tactic repo'''

        repo_handler = self.get_repo_class()
        if repo_handler == self.TACTIC_REPO:
            return True
        else:
            return False




class SampleRepoHandler(BaseRepoHandler):

    def get_repo_class(self):
        context = self.snapshot.get_value("context")

        search_type = self.sobject.get_base_search_type()

        # all contexts of game are sent to perforce
        if context == "Game Ready":
            return self.PERFORCE_REPO

        #elif search_type == "prod/texture":
        #    asset_context = self.sobject.get_value("asset_context")
        #    if asset_context == "model":
        #        return self.PERFORCE_REPO
        #    else:
        #        return self.TACTIC_REPO

        else:
            return self.TACTIC_REPO




