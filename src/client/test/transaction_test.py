import tacticenv
from tactic_client_lib import TacticServerStub

server = TacticServerStub(protocol="xmlrpc")
#server.set_project("sample3d")
server.set_ticket("60128265ebea63620de1f5b0ffc502eb")
search_type = "prod/shot"

server.start(title='cow')
sobject = server.insert(search_type, { 'description': 'wow'} )
server.update(search_key, { 'description': 'another update'} )
server.finish()

sobject = server.insert(search_type, { 'description': 'wow2'} )
sobject = server.insert(search_type, { 'description': 'wow3'} )



