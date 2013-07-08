
import tacticenv

from pyasm.security import Batch
from pyasm.search import Search



import sys


def fix_search_code(search_types=None, verbose=False):

    if not search_types:
        search_types = ['sthpw/task', 'sthpw/snapshot', 'sthpw/file', 'sthpw/note', 'sthpw/work_hour', 'sthpw/sobject_list']


    for search_type in search_types:
        search = Search(search_type)
        sobjects = search.get_sobjects()
        if verbose:
            print "Searching %s" % search_type
            print "  ... found %s sobjects" % len(sobjects)

        for i, sobject in enumerate(sobjects):
            #if i > 100:
            #    break;

            try:
                code = sobject.get_value("code")
            except:
                if verbose:
                    print "WARNING: No code for [%s]" % sobject.get_search_key()

            try:
                parent_type = sobject.get_value("search_type")
                parent_id = sobject.get_value("search_id")

                parent = Search.get_by_id(parent_type, parent_id)
                if not parent:
                    if verbose:
                        print "WARNING: No parent found for search_type [%s] id: [%s]" % (search_type, sobject.get_id())
                    continue
                else:
                    parent_code = parent.get_value("code")
            except Exception, e:
                if verbose:
                    print "ERROR: ", e, " for sobject: ", sobject.get_search_type(), sobject.get_code()
                parent_code = None

            if not parent_code:
                parent_code = ""

            sobject.set_value("search_code", parent_code)
            sobject.commit(triggers=False);


if __name__ == '__main__':
    Batch()

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
            verbose = True
        if o in ("-v", "--verbose"):
            verbose = True
   
    fix_search_code(search_types=args, verbose=verbose)


