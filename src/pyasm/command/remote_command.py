###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


'''Abstract interface to allow command to seamlessly be executed on another
machine.  The exact implementation of remote calling is hidden from the
command.  The command only knows to execute it self'''

__all__ = ['RemoteExec', 'XmlRpcExec', 'TacticDispatcher']


from pyasm.common import *
from pyasm.command import Command
from pyasm.search import SObjectFactory



class RemoteExec(Command):

    def execute_slave(my):
        pass




# various implementations of remote execution

class XmlRpcExec(RemoteExec):

    def execute_slave(my, command):

        # start a new thread
        import thread
        ticket = Environment.get_security().get_ticket_key()
        thread.start_new_thread( XmlRpcExec._execute_slave, (ticket,command) )


    def _execute_slave(ticket, command):

        # rpc the command
        import socket, xmlrpclib, pickle, time
        pickled = pickle.dumps(command)

        try:
            print "slave command ...."
            server_url = "http://saba:8081/xmlrpc"
            server = xmlrpclib.ServerProxy(server_url)
            print server.do_login(ticket)

            print server.do_command(pickled)
            print "... done!!!!"

        except (socket.error), e:
            raise SetupException( 'Could not connect to slave server "%s":\n\nError given: %s' % (server_url, e.__str__() ))
        except (xmlrpclib.ProtocolError), e:
            raise SetupException( 'xmlprc protocol error returned from slave server "%s"' % (server_url))

    _execute_slave = staticmethod(_execute_slave)






class TacticDispatcher(RemoteExec):
    '''The tactic dispatcher works by storing a queue object'''

    def __init__(my):
        my.description = "No Description"

    def set_description(my, description):
        my.description = description

    def execute_slave(my, command):
        import socket, xmlrpclib, pickle, time
        pickled = pickle.dumps(command)

        queue = SObjectFactory.create("sthpw/queue")
        queue.set_value("queue", "render")
        queue.set_value("state", "pending")
        queue.set_value("command", command.__class__.__name__)
        queue.set_value("serialized", pickled)

        queue.set_value("priority", "AAA")
        queue.set_value("description", my.description)

        queue.set_user()
        queue.commit()

        



class Qube(RemoteExec):
    pass








