import sys
import tacticenv


from pyasm.biz import Project
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.search import Search


class ModCodeCmd(Command):

    def execute(self):

        search = Search('config/widget_config')
        sobjects = search.get_sobjects()

        padding = 5
        prefix = 'WIDGET_CONFIG'

        
        for sobject in sobjects:
            id = sobject.get_id()
            code_expr = "%%s%%0.%dd" % padding
            new_code = code_expr % (prefix, id)
            old_code = sobject.get_code()
            print "Updating widget_config  [%s] with new code [%s]"%(id ,new_code)
            sobject.set_value("code", new_code )
            sobject.commit(triggers=False)

        self.add_description('Batch-update widget config code')

if __name__ == '__main__':
    
    args = sys.argv[1:]
    if len(args) != 1:
        print "Please provide a valid project code!"
        sys.exit(2)

    my_login = 'admin'
    batch = Batch(login_code=my_login)
    Project.set_project(args[0])

    command = ModCodeCmd()
    Command.execute_cmd(command)
