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

__all__ = ['TimeCode']

import types



class TimeCode(object):

    def __init__(self, **kwargs):
        self.frames = kwargs.get("frames")
        self.frames = float(self.frames)

        self.fps = kwargs.get("fps")
        if not self.fps:
            from pyasm.prod.biz import ProdSetting
            self.fps = ProdSetting.get_value_by_key("fps")
            self.fps = int(self.fps)
        if not self.fps:
            self.fps = 24

        if not self.frames:
            timecode = kwargs.get("timecode")
            self.frames = self.calculate_frames(timecode, self.fps)

        # handle cases where frames has a decimal: ie: 400.4
        self.frames = int(float(self.frames))


    def get_frames(self):
        return self.frames


    def get_timecode(self, format='MM:SS:FF', fps=None):
        frames = self.frames
        if not fps:
            fps = self.fps

        hours = frames // (60*60*fps)
        minutes = (frames // (60*fps)) % 60
        seconds = ((frames // fps) % 60 ) % 60
        frames = frames % fps % 60 % 60

        if format == 'MM:SS:FF':
            timecode = "%0.2d:%0.2d:%0.2d" %(minutes, seconds, frames)
        elif format == 'MM:SS.FF':
            timecode = "%0.2d:%0.2d.%0.2d" %(minutes, seconds, frames)
        elif format == 'MM:SS':
            timecode = "%0.2d:%0.2d" %(minutes, seconds)
        elif format == 'HH:MM:SS:FF':
            timecode = "%0.2d:%0.2d:%0.2d:%0.2d" %(hours, minutes, seconds, frames)
        elif format == 'HH:MM:SS.FF':
            timecode = "%0.2d:%0.2d:%0.2d.%0.2d" %(hours, minutes, seconds, frames)
        elif format == 'HH:MM:SS':
            timecode = "%0.2d:%0.2d:%0.2d" %(hours, minutes, seconds)

        return timecode


    def calculate_frames(self, timecode, fps):
        if not timecode:
            return 0

        parts = timecode.split(":")
        if parts[-1].find(".") != -1:
            a, b = parts[-1].split(".")
            parts[-1] = a
            parts.append(b)

        # SS:FF
        if len(parts) == 2:
            seconds = int(parts[0])
            frames = int(parts[1])

            frames = frames + fps*seconds


        # MM:SS:FF
        elif len(parts) == 3:
            minutes = int(parts[0])
            seconds = int(parts[1])
            frames = int(parts[2])

            frames = frames + fps*( seconds + 60*(minutes) )

        # HH:MM:SS:FF
        elif len(parts) == 4:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            frames = int(parts[3])

            frames = frames + fps*( seconds + 60*(minutes + 60*hours) )

        return frames


    def __add__(self, timecode):

        if isinstance(timecode, TimeCode):
            t = timecode
        else:
            t = TimeCode(timecode=timecode, fps=self.fps)
        frames = t.get_frames() + self.get_frames()

        t2 = TimeCode(frames=frames, fps=self.fps)
        return t2



    def __add__(self, timecode):

        if type(timecode) == types.IntType:
            frames = timecode
        else:
            if isinstance(timecode, TimeCode):
                t = timecode
            else:
                t = TimeCode(timecode=timecode, fps=self.fps)
            frames = t.get_frames()
            
        frames = frames + self.get_frames()

        t2 = TimeCode(frames=frames, fps=self.fps)
        return t2



    def __sub__(self, timecode):

        if type(timecode) == types.IntType:
            frames = timecode
        else:
            if isinstance(timecode, TimeCode):
                t = timecode
            else:
                t = TimeCode(timecode=timecode, fps=self.fps)
            frames = t.get_frames()

        frames = self.get_frames() - frames

        t2 = TimeCode(frames=frames, fps=self.fps)
        return t2

# FIXME: this should be a separate file: produces a dependency error
"""
import unittest
class TimeCodeTest(unittest.TestCase):
    def test_all(self):

        timecode = "00:01:12"
        fps = 24
        t1 = TimeCode(timecode=timecode, fps=fps)
        frames = t1.get_frames()
        self.assertEquals(36, frames)

        timecode2 = t1.get_timecode()
        self.assertEquals(timecode, timecode2)

        timecode = "00:02:00"
        fps = 24
        t2 = TimeCode(timecode=timecode, fps=fps)
        frames = t2.get_frames()
        self.assertEquals(48, frames)


        # try changing fps
        timecode = t2.get_timecode(fps=12)
        self.assertEquals("00:04:00", timecode)

        timecode = t2.get_timecode(fps=60)
        self.assertEquals("00:00:48", timecode)



        # try adding
        t3 = t1 + t2
        self.assertEquals(84, t3.get_frames())
        timecode = t3.get_timecode()
        self.assertEquals("00:03:12", timecode)

        t3 = t3 + "00:02:20"
        timecode = t3.get_timecode()
        self.assertEquals("00:06:08", timecode)

        t3 = t1 + 24
        timecode = t3.get_timecode()
        self.assertEquals("00:02:12", timecode)


        # try subtracting
        t3 = t2 - t1
        timecode = t3.get_timecode()
        self.assertEquals("00:00:12", timecode)



        timecode2 = TimeCode(timecode="01:15:12")
        timecode1 = TimeCode(timecode="01:12:15")
        timecode = timecode1 + timecode2
        self.assertEquals("02:28:03", timecode.get_timecode() )
        timecode = timecode2 - timecode1
        self.assertEquals("00:02:21", timecode.get_timecode() )





if __name__ == '__main__':
    unittest.main()
"""
