import sys
import tacticenv


from pyasm.biz import Project
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.flash import FlashShot
from pyasm.prod.biz import Episode
from pyasm.search import Search


class AddFlashShotCmd(Command):

    def __init__(self, seq_code):
        self.seq_code = seq_code
        super(AddFlashShotCmd, self).__init__()

    def get_title(self):
        ''' this is just for show for now'''
        return "Add Shot"

    def execute(self):
        self.add_description('Add flash shots in bulk')
        # add from shot 00001 to 00050 if they do not exist already
        count = 0
        for x in xrange(1, 51):
            shot_code = '%0.5d'%x
            shot_code = "%s-%s" %(self.seq_code, shot_code)
            shot = FlashShot.get_by_code(shot_code)
            if not shot:
                print "[%s] to be created." %shot_code
                shot = FlashShot.create(shot_code, self.seq_code, 'Shot %s' %shot_code)
                # assuming this is one of the values in project settings
                # shot_status
                shot.set_value('status', 'online')
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
    Project.set_project('flash')

    project_code = Project.get_project_code()
    args = sys.argv[1:]

    try:
        if len(args) != 1:
            raise Usage("A single episode code is expected.")
        seq = Episode.get_by_code(args[0])
        if not seq:
            raise Usage("The episode code [%s] has not been registered for "\
                "project [%s] in TACTIC. Please Insert it in the Episodes tab first." %(args[0], project_code))
    except Usage, e:
        print e.msg
        sys.exit(2)

    command = AddFlashShotCmd(seq.get_code())
    Command.execute_cmd(command)

