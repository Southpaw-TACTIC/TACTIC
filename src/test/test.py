

import tacticenv

from pyasm.security import Batch
Batch(site="workflow", project_code="workflow")

from pyasm.search import Search
search = Search("sthpw/login")
sobjects = search.get_sobjects()
for sobject in sobjects:
    print( sobject.get("display_name") )
