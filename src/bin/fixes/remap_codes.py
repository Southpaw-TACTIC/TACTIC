
import tacticenv

from pyasm.security import Batch
Batch(project_code='admin')

from pyasm.common import Config
from pyasm.search import Search
from pyasm.command import Command


class RemapCodesCmd(Command):

    def execute(self):

        server = Config.get_value("install", "server")

        search_types = ['sthpw/note', 'sthpw/task']
        prefixes = ["NOTE", "TASK"]
        

        for j, search_type in enumerate(search_types):

            search = Search(search_type)
            search.add_column("id")
            search.add_column("code")
            sobjects = search.get_sobjects()
            num = len(sobjects)
            print "Found [%s] of %s" % (num, search_type)


            for i, sobject in enumerate(sobjects):
                code = sobject.get_code()
                if code.startswith(server):
                    continue

                if not code:
                    #sobject.delete()
                    continue

                if not code.startswith(prefixes[j]):
                    continue

                print "(%s of %s) %s" % (i, num, code)

                new_code = "%s%s" % (server,code)

                sobject.set_value("code", new_code)
                sobject.commit()



if __name__ == '__main__':
    cmd = RemapCodesCmd()
    Command.execute_cmd(cmd)





