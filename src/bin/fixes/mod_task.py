import sys
import tacticenv


from pyasm.biz import Project
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.search import Search


class ModTaskCmd(Command):


    def get_title(self):
        ''' this is just for show for now'''
        return "Mod Task"

    def execute(self):
        self.add_description("Set task's context to match process if empty")
        search = Search('sthpw/task')
        search.add_filter('context', None)
        tasks = search.get_sobjects()
        if tasks and len(tasks) > 700:
	    print "More than 700 tasks are found. Exiting as a precaution."
	    sys.exit(0)
        if not tasks: 
            print "All tasks have context attribute filled in. Exiting."
            sys.exit(0)

        ctr = 0
        for task in tasks:
            context = task.get_value('context')
            process = task.get_value('process')
            search_type = task.get_value('search_type')
            # delete dangling task
            if not search_type:
                task.delete()
                continue
            if not context and process:
                task.set_value('context', process)
                task.commit(triggers=False)
                ctr += 1
        print "%s tasks have been processed. Their context are matched with their process." %ctr   




if __name__ == '__main__':
    
    my_login = 'admin'
    batch = Batch(login_code=my_login)
    Project.set_project('admin')

    command = ModTaskCmd()
    Command.execute_cmd(command)

