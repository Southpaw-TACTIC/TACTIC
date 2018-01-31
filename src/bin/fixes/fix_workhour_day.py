
import tacticenv

from pyasm.security import Batch
from pyasm.search import Search
from pyasm.common import SPTDate
from pyasm.command import Command
from dateutil import parser
from dateutil.relativedelta import relativedelta

import sys


class FixDay(Command):
    '''Fix the work hours getting offset issue by bringing the time forward to the mid-night of the day entered'''
    
   
    def execute(self):
        self.count = 0
        self.verbose = self.kwargs.get('verbose')
        self.fix_day(self.verbose)
        self.add_description('Fixed [%s] work hours offset'%self.count)

    def fix_day(self, verbose=False):
        search = Search('sthpw/work_hour')
        sobjects = search.get_sobjects()
        if verbose:
            print "Searching %s" % search_type
            print "  ... found %s sobjects" % len(sobjects)

        for i, sobject in enumerate(sobjects):
            # change back to pst for day that has finite hours
            day = sobject.get_value("day")

            try:
                if not day.endswith('00:00:00'):
                    date, hrs = day.split(' ')
                    new_day = '%s 00:00:00'%date
                    print "code: %s [%s]" %(sobject.get_code(), day)
                    date = parser.parse(new_day)
                    date = date + relativedelta(days=1)
                    print "adjusted day ", date
                    sobject.set_value("day", str(date))
                    sobject.commit(triggers=False)
                    self.count += 1

            except Exception, e:
                if verbose:
                    print "ERROR: ", e, " for sobject: ", sobject.get_search_type(), sobject.get_code()

        print 'Fixed [%s] work hours offset'%self.count
            
if __name__ == '__main__':
    Batch(login_code='admin')

    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
    except getopt.error, msg:
        print msg
        sys.exit(2)

    verbose = False
    help = False

    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print "Fix the work hours from GMT back to PST where applicable"
            sys.exit(0)
        if o in ("-v", "--verbose"):
            verbose = True
   
    cmd = FixDay(verbose=verbose)
    Command.execute_cmd(cmd)

