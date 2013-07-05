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

__all__= ['ProdTaskFilter']


# <prod>/<process>/<role>


class ProdTaskFilter(Widget):
    '''Filters tasks according to the user'''

    def init(my):
        # look for groups that are relevant
        groups = Environment.get_security().get_groups()
        login = Environment.get_security().get_login()

        # get the current project
        project = Project.get()

        for group in groups:
            # namespace of group must be in the current project
            namespace = group.get_value("namespace")
            if namespace != project:
                continue

            # group names <project>/<process>/<role>
            # iggy/roughDesign/artist
            namespace, my.process, my.role = group_name.split("/")



    def get_role(my):
        return my.role

    def get_process(my):
        return my.process
        

    def postprocess_search(my, sobjects):

        new_sobjects = []

        # filter out sobjects that do not have appropriate tasks
        if sobjects:
            search_type = sobjects[0].get_search_type()
            ids = [str(x.get_id()) for x in sobjects]

            search = Search("sthpw/task")
            search.add_filter("search_type", search_type)
            search.add_where("search_id in (%s)" % ",".join(ids) )

            if is_supervisor:
                search.add_filter("status", "Submit for Review")

            elif user != "":
                search.add_filter("assigned", user)
                #search.add_where("status in ('Pending','In Progress')")



            tasks = search.get_sobjects()

            task_search_ids = [x.get_value("search_id") for x in tasks]

            # once we have all of the tasks for this episode, we filter
            # out any assets that don't have these tasks
            for sobject in sobjects:
                search_id = tmp_sobject.get_id()

                if search_id in task_search_ids:
                    new_sobjects.append(sobject)

        return new_sobjects


