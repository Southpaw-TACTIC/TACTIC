import sys
import tacticenv


from pyasm.biz import Project
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.search import Search, SearchType, DbContainer

class PopulateSObjectListCmd(Command):

    def execute(self):

        # go through all of the projects
        search = Search("sthpw/project")
        projects = search.get_sobjects()

        #search = Search("sthpw/sobject_list")
        #sobject_list_items = search.get_sobjects()
        #self.sobject_list_dict = {}
        #for x in sobject_list_items:
        #    key = "%s|%s" % ( x.get_value("search_type"), x.get_id() )
        #    self.sobject_list_dict[key] = x


        for project in projects:
            project_code = project.get_code()
            if project_code in ['admin','unittest','sthpw']:
                continue

            search_types = project.get_search_types(include_multi_project=True)
            for search_type in search_types:
                search_type.set_value('code', search_type.get_value('search_type'))
                search_type.commit(triggers=False)
                full_search_type = "%s?project=%s" % (search_type.get_value('search_type'), project_code)
                self.populate_search_type(full_search_type)


    def populate_search_type(self, search_type):

        print search_type
        search = Search(search_type)
        sobjects = search.get_sobjects()
        print "#: ", len(sobjects)

        from tactic.command import GlobalSearchTrigger

        for sobject in sobjects:
            #if not SearchType.column_exists(sobject.get_search_type(), "code"):
            #    print "WARNING: no code in [%s]" % sobject.get_search_key()
            #    continue

            input = {
                "id": sobject.get_id(),
                "search_key": sobject.get_search_key()
            }
            cmd = GlobalSearchTrigger()
            cmd.set_caller(sobject)
            cmd.set_input(input)
            cmd.execute()







if __name__ == '__main__':
    
    batch = Batch()
    msg = "\nThis script will delete the existing entries in your sobject_list table used for storing keywords for searching purpose " \
            "and renew them with the updated entries for all projects" 
    answer = raw_input(" %s. Continue (y/n): " %msg)
    if answer == "y":
        sthpw_sql = DbContainer.get("sthpw")
        statement = 'DELETE from sobject_list;'
        sthpw_sql.do_update(statement)
        print
        print "Deleting of existing entries finished.\n"
    elif answer == 'n':
        sys.exit(0)
    else:
        print "Anwer y or n. Exit..."
        sys.exit(0)
    command = PopulateSObjectListCmd()
    Command.execute_cmd(command)
    print
    print "Finished updating sobject_list table."

