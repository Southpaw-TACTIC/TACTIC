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

__all__ = ["RenderSubmit", "QubeRenderSubmit", 'QubeState', 'RenderSubmitException']

import re, os

from pyasm.common import Base, Environment, TacticException, Config, System
from pyasm.command import Command, DatabaseAction
from pyasm.biz import Snapshot
from pyasm.prod.biz import FrameRange
from pyasm.prod.queue import Queue

from render_cmd_builder import *
from render_package import RenderPackage


class RenderSubmitException(TacticException):
    pass


class RenderSubmit(Command):
    '''Generic class which takes a render package and submits it'''
    def __init__(my, render_package=None):
        my.render_package = render_package
        my.snapshot = my.render_package.get_snapshot()
        my.sobject = my.render_package.get_sobject()
        my.queue = None

    def set_queue(my, queue):
        my.queue = queue

    def set_render_package(my, render_package):
        my.render_package = render_package

    def get_render_package(my):
        return my.render_package

    def get_option(my, name):
        return my.render_package.get_option(name)

    def set_option(my, name, value):
        return my.render_package.set_option(name, value)



    def get_render_dir(my):
        ticket = Environment.get_security().get_ticket_key()
        tmpdir = Environment.get_tmp_dir()
        render_dir = "%s/temp/%s" % (tmpdir, ticket)
        System().makedirs(render_dir)

        return render_dir


    def get_input_path(my):
        print my.snapshot.get_value("snapshot")
        for type in ['main', 'maya', 'xsi', 'houdini']:
            input_path = my.snapshot.get_client_lib_path_by_type(type)
            if input_path:
                #input_path = '////%s' %input_path
                return input_path

        raise RenderSubmitException("No input path found for snapshot [%s]" % my.snapshot.get_code() )

 
    def execute(my):
        assert my.snapshot
        assert my.sobject

        # add some additional options
        my.set_option("snapshot_code", my.snapshot.get_code() )
        my.set_option("render_dir", my.get_render_dir() )

        input_path = my.get_input_path()
        my.set_option("input_path", input_path)

        # handle the policy if it exists
        policy = my.render_package.get_policy()
        if policy:
            width = policy.get_value("width")
            height = policy.get_value("height")
            frame_by = policy.get_value("frame_by")
            extra_settings = policy.get_value("extra_settings")

            my.set_option("resolution", "%sx%s" % (width, height))

            my.set_option("width", width)
            my.set_option("height", height)
            my.set_option("frame_by", frame_by)
            my.set_option("extra_settings", extra_settings)
            





        # get some information from the render context
        search_type = my.sobject.get_search_type_obj()
        description = "Render %s: %s" % (search_type.get_title(),my.sobject.get_code())

        # create queue in tactic related to this submission
        if not my.queue:
            my.queue = Queue.create(my.sobject, "render", "9999", description)
        else:
            my.queue.set_sobject_value(my.sobject)
            my.queue.set_value('login', Environment.get_user_name())
            # have to make sure it is committed to get a queue_id
            if my.queue.get_id() == -1:
                my.queue.commit()


        # submit the job to the dispatcher
        dispatcher_id = my.submit()

        # store the dispatcher id in the queue object
        my.queue.set_value("dispatcher_id", dispatcher_id)
        my.queue.commit()


    def submit(my):
        # get the type of job ... the only one currently support it Qube
        # FIXME: this should not be called Queue
        queue = my.get_option("queue")

        # delegate it out to the appropriate submission handler
        if queue == "Qube":
            submit = QubeRenderSubmit(my.render_package)
        else:
            raise TacticException("Invlid queue type [%s]" % queue)

        submit.set_queue(my.queue)
        return submit.submit()





# create the qube jobs
try:
    import qb
except ImportError:
    #print("WARNING: Qube is not installed")
    pass


class QubeRenderSubmit(RenderSubmit):
    '''Class which specifically handles submitting a render to Qube'''
    def __init__(my, render_package):
        super(QubeRenderSubmit,my).__init__(render_package)

    def submit(my):

        job_type = my.get_option('job_type')
        if not job_type:
            job_type = "tactic"

        # build the appropriate package
        if job_type == "tactic":
            qube_job = QubeTacticJob(my.render_package, my.queue)
        #elif job_type == "xsi":
        #    qube_job = QubeXSIJob(my.render_package, my.queue)
        else:
            qube_job = QubeSimpleJob(my.render_package, my.queue)


        # build a qube job and submit command
        my.job_list = []

        # get the job from 
        my.job_list.append( qube_job.get_job() )

        print "job_list: ", my.job_list

        # append the checkin job as a callback
        #checkin_job = QubeCheckinJob(my.render_package, queue)
        #my.job_list.append( checkin_job.get_job() )

        # get the id for the submitted job
        submitted = qb.submit(my.job_list)
        dispatcher_id = submitted[0]['id']

        return dispatcher_id





class QubeJob(object):
    '''Builds Qube Jobs'''
    def __init__(my, render_package, queue):
        my.render_package = render_package
        my.snapshot = render_package.get_snapshot()
        my.sobject = render_package.get_sobject()
        my.options = render_package.get_options()
        my.queue = queue



    def _get_base_job(my):

        cpus = 1

        job_type = my.render_package.get_option("job_type")

        # generic qube parameters
        job = {
            'name': job_type,
            'prototype': job_type,
            'cpus': cpus,
            'priority': my.queue.get_value("priority"),
        }


        # create an agenda based on the frames ...
        frame_range = my.render_package.get_frame_range()
        start, end, by = frame_range.get_values()
        frames = qb.genframes("%s-%s" % (start, end) )
        if frames:
            job['agenda'] = frames


        # create a default package
        package = {}
        job['package'] = package


        # store the ticket in the job
        # FIXME: the problem with this is that the ticket may expire before
        # the job actually gets executed
        ticket = Environment.get_security().get_ticket_key()
        package['ticket'] = ticket

        return job



    def get_render_cmd(my):

        scene_file = my.render_package.get_option("input_path")
        if scene_file.endswith(".ma"):
            renderer = "maya"
        elif scene_file.endswith(".scn") or scene_file.endswith(".mdl") \
                or scene_file.endswith(".xsi"):
            renderer = "xsi"
        else:
            renderer = "maya"


        # get the render command
        if renderer == "maya":
            render = MayaRenderCmdBuilder(my.render_package)
        elif renderer == "xsi":
            render = XsiRenderCmdBuilder(my.render_package)

        # qube jobs override the frame values
        render.set_frame_range("QB_FRAME_START", "QB_FRAME_END", "QB_FRAME_STEP")

        cmd = render.get_command()
        return cmd

    def get_job(my):
        pass





class QubeSimpleJob(QubeJob):
    '''Simple job which basically takes the render package and passes it
    directly to the qube job'''

    def get_job(my):
        my.job = my._get_base_job()
        package = my.job.get("package")

        package['tactic_queue_id'] = my.queue.get_id()

        # copy all of the elements in the render package to the qube job package
        for name, value in my.options.items():
            package[name] = value

        return my.job






class QubeCheckinJob(QubeJob):
    def get_job(my):
        my.job = my._get_base_job()
        package = my.job.get("package")

        package['tactic_queue_id'] = my.queue.get_id()
        package['xmlrpc_url'] = ''
        package['handoff_dir'] = 'D:/tactic_temp'

        render_dir = my.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        return my.job




class QubeMayaJob(QubeJob):
    def get_job(my):
        my.job = my._get_base_job()
        package = my.job.get("package")

        render_dir = my.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        scene_file = my.render_package.get_option("render_dir")
        package['scenefile'] = str(scene_file)

        defaultRenderGlobals = {}
        my.job['defaultRenderGlobals'] = package

        defaultRenderGlobals["extensionPadding"] = 4
        defaultRenderGlobals["imageFilePrefix"] = my.render_package.get_option("output_prefix")

        #env = os.environ
        #my.job['package']['env'] = env

        return my.job



class QubeXsiJob(QubeJob):
    def get_job(my):
        my.job = my._get_base_job()
        package = my.job.get("package")

        package = {}
        my.job['package'] = package

        render_dir = my.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        #scene_file = my.render_package.get_option("scene_file")
        #package['scenefile'] = str(scene_file)

        package['ImageFileName'] = "image"
        scene_file = my.render_package.get_option("input_path")
        package['scenefile'] = str(scene_file)
        #env = os.environ
        #my.job['package']['env'] = env

        return my.job





class QubeTacticJob(QubeJob):
    def get_job(my):
        my.job = my._get_base_job()

        #my.job['notes'] = "%s, submitted by %s" % (description, queue.get_value('login') )

        # conform to Qubes Maya job types
        package = my.job.get('package')

        render_dir = my.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        scene_file = my.render_package.get_option("input_path")
        package['scenefile'] = str(scene_file)

        cmd = my.get_render_cmd()
        package['cmdline'] = str(cmd)

        frame_range = my.render_package.get_frame_range()
        frame_range_key = frame_range.get_key()
        package['frame_range'] = frame_range_key
        package['tactic_queue_id'] = my.queue.get_id()


        # FIXME: should use naming convention for this ... possibly?
        output_prefix = my.render_package.get_option("output_prefix", no_exception=True)
        output_ext = my.render_package.get_option("output_ext", no_exception=True)
        if not output_prefix:
            output_prefix = "image"
        if not output_ext:
            output_ext = "iff"

        image_name = "%s.%s" % (output_prefix, output_ext )
        package['image_name'] = image_name

        layers = my.render_package.get_option("layers", no_exception=True)
        if layers:
            package['layers'] = layers

        return my.job

        
        


class LSFRenderSubmit(RenderSubmit):
    def __init__(my):
        super(QubeRenderSubmit,my).__init__()

    def execute(my):
        assert my.render_package

        cmd = "bsub"

        render_cmd = my.get_render_cmd()

        os.system(cmd)

        value = "Job <1234> is submitted to default queue <normal>"

        # extract job id
        id = re.compile("<(\d+)>")







class JobState(Base):
    pass

# not sure if we should put this at the UI level
from pyasm.widget import BaseTableElementWdg
class QubeState(BaseTableElementWdg):
    '''class which queries qube to find the state'''
    def get_display(my):
        sobject = my.get_current_sobject()

        try:
            import qb
        except ImportError:
            Environment.add_warning("Qube not installed", "Qube not installed")
            return "---"
            
        dispatcher_id = sobject.get_value("dispatcher_id")

        all_jobinfo = qb.jobinfo(filters={'id': dispatcher_id})
        if not all_jobinfo:
            return "---"

        job_info = all_jobinfo[0]

        status = job_info.get('status')

        timestart = job_info.get('timestart')
        timecomplete = job_info.get('timecomplete')
        timeelapsed = int(timecomplete) - int(timestart)
        return "%s (%ss)" % (status, timeelapsed)








