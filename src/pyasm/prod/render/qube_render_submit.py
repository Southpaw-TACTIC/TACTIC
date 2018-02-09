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
    def __init__(self, render_package=None):
        self.render_package = render_package
        self.snapshot = self.render_package.get_snapshot()
        self.sobject = self.render_package.get_sobject()
        self.queue = None

    def set_queue(self, queue):
        self.queue = queue

    def set_render_package(self, render_package):
        self.render_package = render_package

    def get_render_package(self):
        return self.render_package

    def get_option(self, name):
        return self.render_package.get_option(name)

    def set_option(self, name, value):
        return self.render_package.set_option(name, value)



    def get_render_dir(self):
        ticket = Environment.get_security().get_ticket_key()
        tmpdir = Environment.get_tmp_dir()
        render_dir = "%s/temp/%s" % (tmpdir, ticket)
        System().makedirs(render_dir)

        return render_dir


    def get_input_path(self):
        print self.snapshot.get_value("snapshot")
        for type in ['main', 'maya', 'xsi', 'houdini']:
            input_path = self.snapshot.get_client_lib_path_by_type(type)
            if input_path:
                #input_path = '////%s' %input_path
                return input_path

        raise RenderSubmitException("No input path found for snapshot [%s]" % self.snapshot.get_code() )

 
    def execute(self):
        assert self.snapshot
        assert self.sobject

        # add some additional options
        self.set_option("snapshot_code", self.snapshot.get_code() )
        self.set_option("render_dir", self.get_render_dir() )

        input_path = self.get_input_path()
        self.set_option("input_path", input_path)

        # handle the policy if it exists
        policy = self.render_package.get_policy()
        if policy:
            width = policy.get_value("width")
            height = policy.get_value("height")
            frame_by = policy.get_value("frame_by")
            extra_settings = policy.get_value("extra_settings")

            self.set_option("resolution", "%sx%s" % (width, height))

            self.set_option("width", width)
            self.set_option("height", height)
            self.set_option("frame_by", frame_by)
            self.set_option("extra_settings", extra_settings)
            





        # get some information from the render context
        search_type = self.sobject.get_search_type_obj()
        description = "Render %s: %s" % (search_type.get_title(),self.sobject.get_code())

        # create queue in tactic related to this submission
        if not self.queue:
            self.queue = Queue.create(self.sobject, "render", "9999", description)
        else:
            self.queue.set_sobject_value(self.sobject)
            self.queue.set_value('login', Environment.get_user_name())
            # have to make sure it is committed to get a queue_id
            if self.queue.get_id() == -1:
                self.queue.commit()


        # submit the job to the dispatcher
        dispatcher_id = self.submit()

        # store the dispatcher id in the queue object
        self.queue.set_value("dispatcher_id", dispatcher_id)
        self.queue.commit()


    def submit(self):
        # get the type of job ... the only one currently support it Qube
        # FIXME: this should not be called Queue
        queue = self.get_option("queue")

        # delegate it out to the appropriate submission handler
        if queue == "Qube":
            submit = QubeRenderSubmit(self.render_package)
        else:
            raise TacticException("Invlid queue type [%s]" % queue)

        submit.set_queue(self.queue)
        return submit.submit()





# create the qube jobs
try:
    import qb
except ImportError:
    #print("WARNING: Qube is not installed")
    pass


class QubeRenderSubmit(RenderSubmit):
    '''Class which specifically handles submitting a render to Qube'''
    def __init__(self, render_package):
        super(QubeRenderSubmit,self).__init__(render_package)

    def submit(self):

        job_type = self.get_option('job_type')
        if not job_type:
            job_type = "tactic"

        # build the appropriate package
        if job_type == "tactic":
            qube_job = QubeTacticJob(self.render_package, self.queue)
        #elif job_type == "xsi":
        #    qube_job = QubeXSIJob(self.render_package, self.queue)
        else:
            qube_job = QubeSimpleJob(self.render_package, self.queue)


        # build a qube job and submit command
        self.job_list = []

        # get the job from 
        self.job_list.append( qube_job.get_job() )

        print "job_list: ", self.job_list

        # append the checkin job as a callback
        #checkin_job = QubeCheckinJob(self.render_package, queue)
        #self.job_list.append( checkin_job.get_job() )

        # get the id for the submitted job
        submitted = qb.submit(self.job_list)
        dispatcher_id = submitted[0]['id']

        return dispatcher_id





class QubeJob(object):
    '''Builds Qube Jobs'''
    def __init__(self, render_package, queue):
        self.render_package = render_package
        self.snapshot = render_package.get_snapshot()
        self.sobject = render_package.get_sobject()
        self.options = render_package.get_options()
        self.queue = queue



    def _get_base_job(self):

        cpus = 1

        job_type = self.render_package.get_option("job_type")

        # generic qube parameters
        job = {
            'name': job_type,
            'prototype': job_type,
            'cpus': cpus,
            'priority': self.queue.get_value("priority"),
        }


        # create an agenda based on the frames ...
        frame_range = self.render_package.get_frame_range()
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



    def get_render_cmd(self):

        scene_file = self.render_package.get_option("input_path")
        if scene_file.endswith(".ma"):
            renderer = "maya"
        elif scene_file.endswith(".scn") or scene_file.endswith(".mdl") \
                or scene_file.endswith(".xsi"):
            renderer = "xsi"
        else:
            renderer = "maya"


        # get the render command
        if renderer == "maya":
            render = MayaRenderCmdBuilder(self.render_package)
        elif renderer == "xsi":
            render = XsiRenderCmdBuilder(self.render_package)

        # qube jobs override the frame values
        render.set_frame_range("QB_FRAME_START", "QB_FRAME_END", "QB_FRAME_STEP")

        cmd = render.get_command()
        return cmd

    def get_job(self):
        pass





class QubeSimpleJob(QubeJob):
    '''Simple job which basically takes the render package and passes it
    directly to the qube job'''

    def get_job(self):
        self.job = self._get_base_job()
        package = self.job.get("package")

        package['tactic_queue_id'] = self.queue.get_id()

        # copy all of the elements in the render package to the qube job package
        for name, value in self.options.items():
            package[name] = value

        return self.job






class QubeCheckinJob(QubeJob):
    def get_job(self):
        self.job = self._get_base_job()
        package = self.job.get("package")

        package['tactic_queue_id'] = self.queue.get_id()
        package['xmlrpc_url'] = ''
        package['handoff_dir'] = 'D:/tactic_temp'

        render_dir = self.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        return self.job




class QubeMayaJob(QubeJob):
    def get_job(self):
        self.job = self._get_base_job()
        package = self.job.get("package")

        render_dir = self.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        scene_file = self.render_package.get_option("render_dir")
        package['scenefile'] = str(scene_file)

        defaultRenderGlobals = {}
        self.job['defaultRenderGlobals'] = package

        defaultRenderGlobals["extensionPadding"] = 4
        defaultRenderGlobals["imageFilePrefix"] = self.render_package.get_option("output_prefix")

        #env = os.environ
        #self.job['package']['env'] = env

        return self.job



class QubeXsiJob(QubeJob):
    def get_job(self):
        self.job = self._get_base_job()
        package = self.job.get("package")

        package = {}
        self.job['package'] = package

        render_dir = self.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        #scene_file = self.render_package.get_option("scene_file")
        #package['scenefile'] = str(scene_file)

        package['ImageFileName'] = "image"
        scene_file = self.render_package.get_option("input_path")
        package['scenefile'] = str(scene_file)
        #env = os.environ
        #self.job['package']['env'] = env

        return self.job





class QubeTacticJob(QubeJob):
    def get_job(self):
        self.job = self._get_base_job()

        #self.job['notes'] = "%s, submitted by %s" % (description, queue.get_value('login') )

        # conform to Qubes Maya job types
        package = self.job.get('package')

        render_dir = self.render_package.get_option("render_dir")
        package['renderDirectory'] = str(render_dir)

        scene_file = self.render_package.get_option("input_path")
        package['scenefile'] = str(scene_file)

        cmd = self.get_render_cmd()
        package['cmdline'] = str(cmd)

        frame_range = self.render_package.get_frame_range()
        frame_range_key = frame_range.get_key()
        package['frame_range'] = frame_range_key
        package['tactic_queue_id'] = self.queue.get_id()


        # FIXME: should use naming convention for this ... possibly?
        output_prefix = self.render_package.get_option("output_prefix", no_exception=True)
        output_ext = self.render_package.get_option("output_ext", no_exception=True)
        if not output_prefix:
            output_prefix = "image"
        if not output_ext:
            output_ext = "iff"

        image_name = "%s.%s" % (output_prefix, output_ext )
        package['image_name'] = image_name

        layers = self.render_package.get_option("layers", no_exception=True)
        if layers:
            package['layers'] = layers

        return self.job

        
        


class LSFRenderSubmit(RenderSubmit):
    def __init__(self):
        super(QubeRenderSubmit,self).__init__()

    def execute(self):
        assert self.render_package

        cmd = "bsub"

        render_cmd = self.get_render_cmd()

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
    def get_display(self):
        sobject = self.get_current_sobject()

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








