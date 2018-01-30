import sys
import tacticenv


from pyasm.biz import Project
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.prod.biz import Shot, Sequence
from pyasm.search import Search


class AddShotCmd(Command):

    def __init__(self, seq_code):
        self.seq_code = seq_code
        super(AddShotCmd, self).__init__()

    def get_title(self):
        ''' this is just for show for now'''
        return "Add Shot"

    def execute(self):
        self.add_description('Add shots in bulk')
        # add from shot 00001 to 00050 if they do not exist already
        count = 0
        for x in xrange(1, 51):
            shot_code = '%s_%0.3d'%(self.seq_code, x)
            shot = Shot.get_by_code(shot_code)
            if not shot:
                print "[%s] to be created." %shot_code
                shot = Shot.create(shot_code, 'Shot %s' %shot_code)
                shot.set_value('sequence_code', self.seq_code)
                # assuming this is one of the values in project settings
                # shot_status
                shot.set_value('status', 'online')
                # this is the default
                shot.set_value('pipeline_code','shot')
                shot.commit()
                count += 1
            else:
                print "[%s] already exists." %shot_code
        print "%d shot(s) created." %count
       
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg



if __name__ == '__main__':
    
    my_login = 'admin'
    batch = Batch(login_code=my_login)
    Project.set_project('bar')

    project_code = Project.get_project_code()
    args = sys.argv[1:]

    try:
        if len(args) != 1:
            raise Usage("A single sequence code is expected.")
        seq = Sequence.get_by_code(args[0])
        if not seq:
            raise Usage("The sequence code [%s] has not been registered for "\
                "project [%s] in TACTIC. Please Insert it in the Sequences tab first." %(args[0], project_code))
    except Usage, e:
        print e.msg
        sys.exit(2)

    command = AddShotCmd(seq.get_code())
    Command.execute_cmd(command)

