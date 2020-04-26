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


__all__ = ['Shot', 'Layer', 'Composite', 'FrameRange', 'ShotAudio']

import re
from pyasm.common import TacticException
from pyasm.search import *
from pyasm.biz import Snapshot, Task, FileRange

from asset import *


class Shot(SObject):

    SEARCH_TYPE = "prod/shot"

    
    def get_icon_context(cls, context=None):
        if context:
            return context
        else:
            return "icon"
    get_icon_context = classmethod(get_icon_context)


    def get_required_columns():
        '''for csv import'''
        return []
    get_required_columns = staticmethod(get_required_columns)

    def validate(self):
        pat = re.compile('^\d')
        code = self.get_code()
        if not code:
            return
        if pat.search(code):
            raise TacticException('Shot code should not start with a number')

        if self.get_frame_start() > self.get_frame_end():
            raise TacticException('End Frame must be larger than Start Frame')

    # simple definition for frames
    def get_frame_start(self):
        frame_start = self.get_value("tc_frame_start")
        try:
            return int(frame_start)
        except Exception, e:
            return 1

    def get_frame_end(self):
        frame_end = self.get_value("tc_frame_end")
        try:
            return int(frame_end)
        except Exception, e:
            return 1


    def get_frame_range(self):
        frame_range = FrameRange( self.get_frame_start(), \
            self.get_frame_end(), 1 )
        return frame_range


    def get_frame_handles(self):
        frame_in = self.get_value("frame_in", no_exception=True)
        frame_out = self.get_value("frame_out", no_exception=True)
        if frame_in:
            frame_in = int(frame_in)
        else:
            frame_in = 0
        if frame_out:
            frame_out = int(frame_out)
        else:
            frame_out = 0
        return frame_in, frame_out

    def get_frame_notes(self):
        return self.get_value("frame_note", no_exception=True)


    def add_asset(self, asset, instance_name, description=None):
        '''adds an asset with an instance to this shot'''
        instance = Instance.create(self, asset, instance_name, description)
        return instance


    def get_snapshot(self, instance, process, version):
        pass


    def get_all_instances(self, include_parent=False, type='asset'):
        '''gets all non-retired instances in the shot'''
        if include_parent:
            parent_code = self.get_value("parent_code")
            return ShotInstance.get_all_by_shot(self,[parent_code], type )
        else:
            return ShotInstance.get_all_by_shot(self, type=type)


    def get_all_layers(self):
        '''gets all non-retired instances in the shot'''
        return Layer.get_all_by_shot(self)



    # static functions

    def create(code, description):
        shot = SObjectFactory.create( Shot.SEARCH_TYPE )
        shot.set_value("code",code)
        shot.set_value("description",description)
        shot.commit()
        return shot
    create = staticmethod(create)


    def get_search_columns():
        search_columns = ['code', 'description', 'sequence_code', 'status', 'scan_status']
        return search_columns
    get_search_columns = staticmethod(get_search_columns)



    # TODO: this is a carbon copy of the asset delete    
    def delete(self, log=True):

        '''This is for undo'''
        # TODO: the should probably be clearer!!!!
        if log == False:
            super(Shot,self).delete(log)
            return
            

        # An asset can only be deleted if only icon snapshots exist
        snapshots = Snapshot.get_by_sobject(self)

        only_icons = True
        for snapshot in snapshots:
            context = snapshot.get_value("context")
            if context != self.get_icon_context():
                only_icons = False

        if not only_icons:
            raise TacticException("Cannot delete because snapshots exist")

        # only delete if not tasks have been assigned
        tasks = Task.get_by_sobject(self)
        has_assigned = False
        for task in tasks:
            assigned = task.get_value("assigned")
            if assigned != "" and assigned != "None":
                has_assigned = True
        
        if has_assigned:
            raise TacticException("Cannot delete because tasks have been assigned")

        # delete tasks and icons
        for snapshot in snapshots:
            snapshot.delete()
        for task in tasks:
            task.delete()

        self.description = "Deleted '%s', search_type '%s'" % (self.get_code(), self.get_search_type)

        super(Shot,self).delete(log)






class Layer(SObject):
    SEARCH_TYPE = "prod/layer"

    def get_shot(self):
        return Shot.get_by_code( self.get_value("shot_code") )

    def get_foreign_key(self):
        return "layer_id"

    def get_frame_range(self):
        shot = self.get_shot()
        return shot.get_frame_range()


    def get_all_by_shot(shot):
        foreign_key = shot.get_foreign_key()
        search = Search( Layer.SEARCH_TYPE )
        search.add_filter(foreign_key, shot.get_code() )
        return search.get_sobjects()
    get_all_by_shot = staticmethod(get_all_by_shot)


   

    def get(shot_code, name):
        search = Search( Layer.SEARCH_TYPE )
        search.add_filter('shot_code', shot_code)
        search.add_filter('name', name)
        return search.get_sobject()
    get = staticmethod(get)




    def create(name, shot_code):
        sobject = Layer.create_new()
        sobject.set_value("name", name)
        sobject.set_value("shot_code", shot_code)
        sobject.commit()
        return sobject
    create = staticmethod(create)






class Composite(SObject):
    SEARCH_TYPE = "prod/composite"




class FrameRange(FileRange):
    pass

class ShotAudio(SObject):

    SEARCH_TYPE = "prod/shot_audio"

    def create(cls, shot_code, title=''):
        '''create with a shot code'''
        asset = SObjectFactory.create( cls.SEARCH_TYPE )
        asset.set_value("shot_code", shot_code)
        if title:
            asset.set_value("title", title)
        asset.commit()
        return asset
    create = classmethod(create)

    def get_by_shot_code(code):
        search = Search(ShotAudio)
        search.add_filter('shot_code', code)
        return search.get_sobject()
    get_by_shot_code = staticmethod(get_by_shot_code)
