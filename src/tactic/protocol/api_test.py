

import requests
import json

#url = "http://192.168.205.180/workflow/workflow/rest?login_ticket=south123paw&cow=123"
url = "http://192.168.205.180/workflow/workflow/rest"
data = {
        'login_ticket': 'south123paw',
        'method': 'eval',
        'kwargs': json.dumps( {
            'expression': "@SOBJECT(workflow/asset['@LIMIT',3])",
            'single': True,
        } )
}
ret_val = requests.post(url, data)
sobjects = json.loads(ret_val.text)

import pprint
pprint.pprint(sobjects)

print "---"


data = {
    'login_ticket': 'south123paw',
    'method': 'get_by_search_key',
    'search_key': 'workflow/asset?project=workflow&code=ASSET00002'
}
ret_val = requests.post(url, data)
sobject = json.loads(ret_val.text)
print "sobject: ", sobject.get("code")


print "---"


data = {
    'login_ticket': 'south123paw',
    'method': 'execute_cmd',
    'kwargs': json.dumps( {
        'class_name': 'spt.modules.workflow.TestCmd',
        'args': {
            'whatever': 123,
        }
    } ),
        
}
ret_val = requests.post(url, data)
info = json.loads(ret_val.text)
print "sobject: ", info



data = {
    'login_ticket': 'south123paw',
    'method': 'foo()',
}
ret_val = requests.post(url, data)
info = json.loads(ret_val.text)
print "sobject: ", info











