

import tacticenv

from pyasm.search import Search
from pyasm.security import Batch

Batch(site="workflow", project_code="workflow")

search = Search("config/authenticate")
sobjects = search.get_sobjects()
for sobject in sobjects:
    base_dir = sobject.get_base_dir()

    url = sobject.get_url()

    print(sobject.get_code(), sobject.get("name") )

