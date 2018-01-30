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

__all__ = ["CommandException", "CommandExitException", "Command", "CommandLog", "CommandDescription"]


import sys,traceback

from pyasm.common import *
from pyasm.biz import Pipeline, Snapshot, Task
from pyasm.search import *
from pyasm.security import Batch



class CommandException(TacticException):
    pass

class CommandExitException(TacticException):
    '''harmless exception that indicates that the command did not execute,
    so it should not be logged'''
    pass


class Command(Base):
    '''Base class for all command'''

    TOP_CMD_KEY = "Command:top_cmd"

    def __init__(self, **kwargs):
        self.errors = []
        self.description = ""
        self.info = {}
        self.response = ''
        # The sobjects that were operated on by this command
        self.sobjects = []

        self.pipeline_code = None
        self.process_name = None
        self.event_name = None

        self.kwargs = kwargs

        self.transaction = None


    '''
    already defined as a cls method below
    def is_undoable(self):
        return True
    '''
    
    def get_errors(self):
        return self.errors

    def get_description(self):
        '''returns a readable description of what the command did'''
        return self.description

    def add_description(self, description):
        if self.description:
            self.description += "\n%s" % description
        else:
            self.description += "%s" % description

    def set_response(self, response):
        self.response = response

    def get_sobjects(self):
        return self.sobjects


    ###########
    # methods to override
    ###########
    def get_title(self):
        print("WARNING: Should override 'get_title' function for %s" % self)
        return Common.get_full_class_name(self)
        #raise CommandException("Must override 'get_title' function for %s" % self)


    def check(self):
        '''This function allows the command to check to see if the conditions
        are correct to run at all.  With the function, a command can quickly
        avoid starting a full transaction and undo recording'''
        #print("WARNING: Should override 'check' function for %s" % self)
        return True


    def preprocess(self):
        '''everything necessary to prepare for the execution of the command
        is done here.  This includes all information checks and gathering
        of local information is done here'''
        pass

    # DEPRECATED: has never been used
    def get_data(self):
        '''There is separate data gathering phase.  This is separated
        so that embedded commands can have this command superseded by
        a parent command who will do a batch assemble of data and
        feed it to the child commands'''
        pass


    def execute(self):
        '''Does the work of the command.  NEVER call this explicitly:
        call execute_cmd.  This is purely execution phase and occurs
        in a transaction.  It should be simple, fast and safe to fail.
        '''
        raise CommandException("Must override execute function")


    def postprocess(self):
        pass



    def check_security(self):
        '''give the command a callback that allows it to check security'''
        return True


    def get_info(self, key=None):
        '''function to return the info of the command.  The command will
        place specific keyed results which other classes (particular triggers)
        can make use of.'''
        if not key:
            return self.info
        else:
            return self.info.get(key)


    # transaction commands
    def start(self):
        pass

    def rollback(self):
        pass
        #print("Command [%s] does not have a rollback function" % self)

    def commit(self):
        #print("Command [%s] does not have a commit function" % self)
        pass

    def set_transaction(self, transaction):
        # get the transaction from the container.  This is overridden
        # by some commands
        self.transaction = transaction
        return self.transaction


    def get_transaction(self):
        # get the transaction from the container.  This is overridden
        # by some commands
        if not self.transaction:
            self.transaction = Transaction.get(create=True)
        return self.transaction


    def execute_transaction(self, call_trigger=True):
        Command.execute_cmd(self, call_trigger=call_trigger)


    def execute_cmd(cls, cmd, call_trigger=True):
        '''Top level execution of the command heirarchy.  This is what needs
        to be executed to ensure that all the commands are in transaction.

        Usage: Command.execute_cmd(cmd)
        '''

        if not cmd.check_security():
            raise SecurityException()

        environment = Environment.get_env_object()

        # if command determines it shouldn't run, then exit.  In batch mode,
        # this check is ignored
        if not isinstance(environment, Batch):
            try:
                if not cmd.check():
                    return
            except TacticException as e:
                if not isinstance(e, CommandExitException):
                    if isinstance(e.message, unicode):
                        error = e.message.encode('utf-8')
                    else:
                        error = unicode(e.message, errors='ignore').encode('utf-8')
                    cmd.errors.append(error)
                raise

        # Get the tranaction.  Let the command determine where the transaction
        # comes from.  This is used by the client api
        try:
            transaction = cmd.get_transaction()
        except Exception as e:
            # fail with controlled error
            print("Error: ", e)
            # print the stacktrace
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print("-"*50)
            print(stacktrace_str)
            print(str(e))
            print("-"*50)

            raise

        # register this command to the transaction
        transaction.register(cmd)

        # register this as the top command if none has be registered yet
        top_cmd_seq = Container.get_seq(cmd.TOP_CMD_KEY)
        top_cmd_seq.append(cmd)
        if not top_cmd_seq:
            # get the command key
            command_key = environment.get_command_key()
        else:
            command_key = ""


        full_class_name = Common.get_full_class_name(cmd)
        ret_val = None

        # execute the commmand
        try:
            transaction.set_command_class(full_class_name)

            # go through the command pipeline
            cmd.preprocess()
            cmd.get_data()
            ret_val = cmd.execute()
            cmd.postprocess()

        except CommandExitException as e:
            # fail gracefully
            if cmd != top_cmd_seq[0]:
                raise

            # roll back and clear commands
            transaction.rollback()
            Container.put(cmd.TOP_CMD_KEY, None)
            raise

        except KeyboardInterrupt, e:
            # this is specifically for batch processes.  A keyboard interrupt
            # will commit the database and allow undo
            print("Keyboard interrupt...")
            transaction.add_description("Keyboard interrupt")
            transaction.commit()
            Container.put(cmd.TOP_CMD_KEY, None)
            raise

        except Exception as e:
            # if this is not the top command keep going up
            if cmd != top_cmd_seq[0]:
                raise
       
            # fail with controlled error
            message = e.message
           
            # we are risking Unicode encoding error here rather than
            # NoneType exception with the encode() method below
            # in Python 3k, e.message is no longer valid
            if not message:
                message = e.__str__()
            if isinstance(message, Exception):
                message = message.message
            if isinstance(message, basestring): 
                if isinstance(message, unicode):
                    error_msg = message.encode('utf-8')
                else:
                    error_msg = unicode(message, errors='ignore').encode('utf-8')
           
            else:
                error_msg = message
            print("Error: ", error_msg)
            # print the stacktrace
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print("-"*50)
            print(stacktrace_str)
            print("Error: ", error_msg)
            print("-"*50)


            transaction.rollback()
            if top_cmd_seq:
                top_cmd_seq.pop()

            if isinstance(e, TacticException):
                if isinstance(message, unicode):
                    error_msg = message.encode('utf-8')
                else:
                    error_msg = unicode(message, errors='ignore').encode('utf-8')
                cmd.errors.append("%s: %s" %(e.get_title(), error_msg))
            else:
                cmd.errors.append(str(e))

            raise


        else:
            # remember whether this is the top command
            if cmd == top_cmd_seq[0]:
                is_top = True
            else:
                is_top = False

            # if this command is the current top command, then commit
            if cmd == top_cmd_seq[-1]:
                # make sure that everything is committed
                try:
                    

                    # get the description of what the command just did
                    description = cmd.get_description()
                    if description:
                        transaction.add_description(description)
                    transaction.commit()


                except Exception as e:
                    print("FAILED TO COMMIT TRANSACTION", cmd, cmd.__class__.__name__)
                    # print the stacktrace
                    tb = sys.exc_info()[2]
                    stacktrace = traceback.format_tb(tb)
                    stacktrace_str = "".join(stacktrace)
                    print("-"*50)
                    print(stacktrace_str)
                    print(str(e))
                    print("-"*50)
                    raise
                    
                top_cmd_seq.pop()

            # if this is the top most command, then handle the triggers
            if is_top:
                # after a command has successfully executed, look at the
                # pipeline execute any actions
                try:
                    cmd.notify_listeners()
                except Exception as e:
                    # print the stacktrace
                    tb = sys.exc_info()[2]
                    stacktrace = traceback.format_tb(tb)
                    stacktrace_str = "".join(stacktrace)
                    print("-"*50)
                    print(stacktrace_str)
                    print(str(e))
                    print("-"*50)
                    raise

                # call all registered triggers 
                from trigger import Trigger
                Trigger.call_all_triggers()


        return ret_val


    execute_cmd = classmethod(execute_cmd)


    def is_undoable(cls):
        return True
    is_undoable = classmethod(is_undoable)


# Is now part of command ... may change later
#class ProcessCommand(Command):
    '''These commands must be run under a process in a pipeline.  In effect,
    this pipeline owns the command that was executed.
    '''
    def set_process(self, process_name):
        self.process_name = process_name

    def get_process(self):
        return self.process_name

    def set_pipeline_code(self, pipeline_code):
        self.pipeline_code = pipeline_code

    def get_pipeline_code(self):
        return self.pipeline_code

    def set_event_name(self, event_name):
        self.event_name = event_name

    def get_event_name(self):
        return self.event_name

    def set_as_approved(self):
        '''convinience function that sets task for this process as approved'''
        self.set_event_name("task/approved")

        # get the task associated with this process
        tasks = Task.get_by_sobjects(self.sobjects, self.process_name)

        for task in tasks:
            task.set_value("status", "Approved")
            task.commit()


        



    def notify_listeners(self):
        '''The command must have operated on an sobject with a pipeline and
        the operation must have been done on a process in that pipeline'''

        # find the sobject that this command operated on
        sobjects = self.get_sobjects()
        if not sobjects:
            return

        sobject = sobjects[0]
        if not sobject.has_value("pipeline_code"):
            return


        # we have sufficient information
        current_pipeline_code = self.get_pipeline_code()
        if not current_pipeline_code:
            current_pipeline_code = sobject.get_value("pipeline_code")


        current_process = self.get_process()
        event = self.get_event_name()
        if not current_pipeline_code or not current_process:
            return
        # get the pipelne (for in pipeline process)
        pipeline = Pipeline.get_by_code(current_pipeline_code)
        self.handle_pipeline(pipeline, current_process, event)



    def handle_pipeline(self, pipeline, current_process, event):

        # find the output processes
        output_processes = pipeline.get_output_processes(current_process)
        for process in output_processes:
            action_node = process.get_action_node(event, scope="dependent")
            if action_node is None:
                continue

            # get the action class.
            handler_cls = Xml.get_attribute(action_node, "class")
            if not handler_cls:
                continue



            # execute handler
            handler = Common.create_from_class_path(handler_cls)

            # DEPRECATED
            handler.set_prev_command(self)

            # set the options
            options = process.get_action_options(event, scope="dependent")
            handler.set_options(options)

            # send some info to the executed handler
            handler.set_process_name(process.get_name() )

            # create a package
            #package = { 'foo': 'whatever'}
            #handler.set_package(package)

            # transfer outputs to inputs.  This allows a command to deliver
            # from one process to another
            input = self.get_info()
            handler.set_input(input)
            # By default, inputs travel through
            handler.set_output(input)


            # execute the handler command wrapper
            handler_cmd = HandlerCmd(handler)
            handler_cmd.set_event_name(event)
            handler_cmd.set_process(process.get_name() )
            handler_cmd.set_pipeline_code(pipeline.get_code() )
            Command.execute_cmd(handler_cmd)


class HandlerCmd(Command):
    '''Small wrapper class which executes a handler within a command'''
    def __init__(self, handler):
        self.handler = handler
        super(HandlerCmd, self).__init__()

    # DEPRECATED: use get_input()
    def get_info(self):
        # get the info from the handler
        return self.handler.get_input()

    def get_input(self):
        # get the info from the handler
        return self.handler.get_input()

    def execute(self):
        self.handler.execute()




__all__.append('SampleHandler')
__all__.append('SampleHandler2')

# Derive from the client api handler
class SampleHandler(Command):
    def set_prev_command(self, prev_command):
        self.prev_command = prev_command

    def execute(self):
        print("EXECUTING sample command")

        # create the render
        render = SearchType.create("prod/render")
        render.set_parent(self.prev_command.sobject)
        render.set_value("pipeline_code", "turntable")
        render.commit()
        Task.add_initial_tasks(render)

        prev_sobject = self.prev_command.sobject
        prev_process = "model"
        this_sobject = self.prev_command.sobject
        this_process = "turntable"

        # get the deliverable
        snapshot = Snapshot.get_latest_by_sobject(prev_sobject, prev_process)
        if not snapshot:
            return

        # once we have this snapshot, open the file and process
        lib_dir = snapshot.get_lib_dir()
        file_name = snapshot.get_name_by_type("maya")

        file_path = "%s/%s" % (lib_dir, file_name)

        f = open( file_path, 'r')
        lines = f.readlines()
        f.close()

        tmp_dir = Environment.get_tmp_dir()
        new_file_name = "whatever.new"
        new_file_path = "%s/%s" % (tmp_dir, new_file_name)

        f2 = open( new_file_path, 'wb')
        for i, line in enumerate(lines):
            line = "%s - %s" % ( i,line)
            f2.write(line)
        f2.close()

        file_paths = [new_file_path]
        file_types = ['maya']

        from pyasm.checkin import FileCheckin
        checkin = FileCheckin.get(this_sobject, file_paths, file_types, context=this_process)
        checkin.execute()

        self.set_event_name("task/approved")
        self.set_process("preprocess")
        self.set_pipeline_code("turntable")
        self.sobjects = [render]

        # ???
        self.sobject = render


        self.set_as_approved()


class SampleHandler2(Command):
    def set_prev_command(self, prev_command):
        self.prev_command = prev_command

    def execute(self):
        self.set_event_name("task/approved")
        self.set_process("render")
        self.set_pipeline_code("turntable")
        self.sobjects = [self.prev_command.sobject]

        print("SampleHandler2")
        self.set_as_approved()











class CommandLog(SObject):
    '''Central logger for all commands'''


    def create(command):
        class_name = command.__class__.__name__

        login = Environment.get_security().get_login().get_login()
        log = SObjectFactory.create("sthpw/command_log")
        log.set_value("class_name", class_name )
        log.set_value("login", login )
        log.set_value("parameters", command.get_undo() )
        log.commit()
        return log
    create = staticmethod(create)


class CommandDescription(Base):
    '''Class which builds up a description of a command'''

    def __init__(self):
        self.description = []

    def add(self, description):
        self.description.append(description)


    def get(self):
        return "\n".join(self.description)






