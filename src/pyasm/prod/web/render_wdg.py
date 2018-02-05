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

__all__ = [
'RenderException',
'SObjectRenderCbk',
'RenderTableElementWdg',
'RenderSubmitInfoWdg',
]


from pyasm.common import Container, TacticException, Config, Common
from pyasm.command import Command, CommandExitException
from pyasm.command.remote_command import XmlRpcExec, TacticDispatcher
from pyasm.checkin import SnapshotBuilder
from pyasm.search import SearchType, Search
from pyasm.web import Widget, WebContainer, DivWdg
from pyasm.widget import FunctionalTableElement, SelectWdg, IconWdg, IconSubmitWdg, CheckboxWdg, BaseInputWdg, HiddenWdg, TableWdg
from pyasm.biz import Snapshot
from pyasm.prod.biz import Layer, FrameRange, RenderPolicy
from pyasm.prod.render import *


class RenderException(Exception):
    pass


   

from pyasm.command import DatabaseAction
class SObjectRenderCbk(DatabaseAction):
    '''initiates a render with properties'''


    def get_title(self):
        return "Render Submission"

    def check(self):
        web = WebContainer.get_web()
        if web.get_form_value("Render") == "" and web.get_form_value("do_edit").startswith("Submit/") == "":
            return False
        else:
            return True

    def execute(self):

        web = WebContainer.get_web()

        search_keys = []

        # discovery phase to find the sobject to be rendered.  This can be
        # either a snapshots or sobjects.  If it is an sobject, then
        # the latest snapshot will be rendered
        search_type = web.get_form_value("parent_search_type")
        search_id = web.get_form_value("parent_search_id")
        if search_type:
            search_keys = ["%s|%s" % (search_type, search_id)]

        if not search_keys:
            if self.sobject:
                search_keys = [self.sobject.get_search_key()]
            else:
                search_keys = web.get_form_values("search_key")

        # get the policy
        policy = None
        if self.sobject:
            policy_code = self.sobject.get_value("policy_code")
            if policy_code:
                policy = RenderPolicy.get_by_code(policy_code)


        # render options
        options = {}
        keys = web.get_form_keys()
        for key in keys:
            if key.startswith("edit|"):
                value = web.get_form_value(key)
                new_key = key.replace("edit|", "")
                options[new_key] = value

        # add the xmlrpc server to the package:
        # WARNING: not that there is no / separating the 2 %s.
        client_api_url = web.get_client_api_url()
        options['client_api_url'] = client_api_url



        # go through each of the search keys found from the interface
        for search_key in search_keys:

            # find the sobject associates with this key
            if not search_key:
                continue
            sobject = Search.get_by_search_key(search_key)
            if not sobject:
                raise TacticException("Search Key [%s] does not exist" % search_key)

            # if the search_keys represented a snapshot, then use this as
            # the snapshot and find the parent
            if sobject.get_base_search_type() == "sthpw/snapshot":
                snapshot = sobject
                sobject = sobject.get_sobject()
            else:
                # else use the latest, assuming a context (really doesn't
                # make much sense????!!!???
                # FIXME: will deal with this later
                context = "publish"
                snapshot = Snapshot.get_latest_by_sobject(sobject, context)
                if not snapshot:
                    raise TacticException("No checkins of context '%s' exist for '%s'.  Please look at the chekin history" % (context, sobject.get_code()) )


            # We provide a render package with a bunch of necessary information
            render_package = RenderPackage()
            render_package.set_policy(policy)
            render_package.set_snapshot(snapshot)
            render_package.set_sobject(sobject)
            render_package.set_options(options)


            # submission class
            submit_class = self.get_option("submit")
            if not submit_class:
                submit_class = Config.get_value("services", "render_submit_class", no_exception=True)
            if not submit_class:
                submit_class = "pyasm.prod.render.RenderSubmit"

            # now we have an sobject and a snapshot, we initiate a job
            submit = Common.create_from_class_path(submit_class, [render_package])
            # if this is from the EditWdg for queues then use this queue
            # entry instead
            if self.sobject.get_base_search_type() == "sthpw/queue":
                submit.set_queue(self.sobject)
            submit.execute()



	self.description = "Submitted: %s" % ", ".join(search_keys)







class RenderTableElementWdg(FunctionalTableElement):
    '''presents a checkbox to select for each sobject and executes a render'''
    def get_title(self):
        WebContainer.register_cmd("pyasm.prod.web.SObjectRenderCbk")
        render_button = IconSubmitWdg("Render", IconWdg.RENDER, False)
        return render_button

    def get_display(self):
        sobject = self.get_current_sobject()
        search_key = sobject.get_search_key()

        div = DivWdg()
        checkbox = CheckboxWdg("search_key")
        checkbox.set_option("value", search_key)
        div.add(checkbox)

        return div



class RenderSubmitInfoWdg(BaseInputWdg):
    '''presents information about the render'''
    def get_display(self):
        web = WebContainer.get_web()

        widget = Widget()

        search_type = web.get_form_value("parent_search_type")
        search_id = web.get_form_value("parent_search_id")

        if not search_type:
            widget.add("RenderSubmitInfo: parent type not found")
            return widget

        hidden = HiddenWdg("parent_search_type", search_type)
        widget.add(hidden)
        hidden = HiddenWdg("parent_search_id", search_id)
        widget.add(hidden)

        sobject = Search.get_by_id(search_type, search_id)
        table = TableWdg(search_type, css="embed")
        table.set_show_property(False)
        table.set_sobject(sobject)
        table.remove_widget("render")
        table.remove_widget("description")
        widget.add(table)

        return widget




