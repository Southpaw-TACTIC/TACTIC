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
import tacticenv

__all__ = ['SPTDate']


from datetime import datetime, timedelta
from dateutil import parser
from dateutil.tz import *
from dateutil.rrule import DAILY, rrule, MO, TU, WE, TH, FR

TZLOCAL = tzlocal()
TZUTC = tzutc()
TZGMT = gettz('GMT')

import six
basestring = six.string_types


class SPTDate(object):

    def now(cls):
        # utcnow is already converted to GMT
        date = datetime.utcnow()
        date = date.replace(tzinfo=TZGMT)
        date = cls.convert(date)
        return date
    now = classmethod(now)

    def today(cls):
        date = datetime.today()
        return cls.convert(date)
    today = classmethod(today)


    def start_of_today(cls):
        today = datetime.today()
        today = cls.convert(today)
        today = datetime(today.year, today.month, today.day)
        return today
    start_of_today = classmethod(start_of_today)


    def strip_time(cls, date):
        if isinstance(date, basestring):
            date = parser.parse(date)

        date = datetime(date.year, date.month, date.day)
        return date
    strip_time = classmethod(strip_time)


    def strip_timezone(cls, date):
        if isinstance(date, basestring):
            date = parser.parse(date)

        date = date.replace(tzinfo=None)
        return date
    strip_timezone = classmethod(strip_timezone)


    def set_noon(cls, date):
        date = datetime(date.year, date.month, date.day, hour=12, minute=0, second=0)
        return date
    set_noon = classmethod(set_noon)



    def timedelta(cls, **kwargs):
        delta = timedelta(**kwargs)
        return delta
    timedelta = classmethod(timedelta)

    def parse(cls, expression):
        date = parser.parse(expression)
        date = cls.convert(date)
        return date
    parse = classmethod(parse)



    def is_weekday(cls, date):
        if date.weekday() in (5,6):
            return False
        else:
            return True

    is_weekday = classmethod(is_weekday)



    def add_business_days(cls, from_date, add_days, holidays=[]):
        business_days_to_add = add_days
        current_date = from_date
        
        while business_days_to_add >= 0:
            if business_days_to_add > 1:
                current_date += timedelta(days=1)
                weekday = current_date.weekday()
                if weekday >= 5: # sunday = 6
                    continue
                if current_date in holidays:
                    continue
                business_days_to_add -= 1
                if business_days_to_add == 0:
                    break
            else:
                current_date +=timedelta(days=business_days_to_add)
                weekday = current_date.weekday()
                if weekday >= 5 or current_date in holidays:
                    current_date += timedelta(days=1)
                else:
                    break
                business_days_to_add = 0

        return current_date
    add_business_days = classmethod(add_business_days)


    def subtract_business_days(cls, from_date, sub_days, holidays=[]): 
        business_days_to_sub = sub_days
        current_date = from_date

        while business_days_to_sub >= 0:
            if business_days_to_sub > 1:
                current_date -= timedelta(days=1)
                weekday = current_date.weekday()
                if weekday >= 5: # sunday = 6
                    continue
                if current_date in holidays:
                    continue
                business_days_to_sub -= 1
                if business_days_to_sub == 0:
                    break
            else:
                current_date -=timedelta(days=business_days_to_sub)
                weekday = current_date.weekday()
                if weekday >= 5 or current_date in holidays:
                    current_date -= timedelta(days=1)
                else:
                    break
                business_days_to_sub = 0

        return current_date
    subtract_business_days = classmethod(subtract_business_days)


    def get_business_days_duration(cls, start_date, end_date):
        if isinstance(start_date, basestring):
            start_date = parser.parse(start_date)
        if isinstance(end_date, basestring):
            end_date = parser.parse(end_date)


        # intraday
        if (end_date - start_date).days == 0:
            return (end_date - start_date).total_seconds() / (60 * 60 * 24) 


        # first and last days are handled separately
        s = start_date + timedelta(days=1)
        s = s.date()
        e = end_date - timedelta(days=1)
        e = e.date()
        days = rrule(DAILY, dtstart=s, until=e, byweekday=(MO,TU,WE,TH,FR))


        first_day_minute = float(start_date.minute) / 60
        end_day_minute = float(end_date.minute) / 60

        if start_date.weekday() not in (5,6):
            first_day = (24 - (float(start_date.hour) + first_day_minute)) / 24.0
        else:
            first_day = 0


        if end_date.weekday() not in (5,6):
            last_day = (float((end_date.hour) + end_day_minute) / 24.0)
        else:
            last_day = 0

        result = days.count() + first_day + last_day
        return result


    get_business_days_duration = classmethod(get_business_days_duration)


    def convert_to_local(cls, date):
        '''convert a time to local time with timezone'''
        if not date:
            return None

        if isinstance(date, basestring):
            try:
                date = parser.parse(date)
            except:
                # This could be "now()", for example
                return date

        if date.tzinfo == None:
            # assume GMT
            date = date.replace(tzinfo=TZGMT)

        #NOTE: it errors out on time before epoch
        try:    
            local = date.astimezone(TZLOCAL)
        except Exception as e:
            local = date.replace(tzinfo=None)

        return local
    convert_to_local = classmethod(convert_to_local)



    def convert_to_timezone(cls, date, timezone):
        '''convert a time to local time with timezone'''
        if not date:
            return None

        if isinstance(date, basestring):
            try:
                date = parser.parse(date)
            except:
                # This could be "now()", for example
                return date

        if date.tzinfo == None:
            # assume GMT
            date = date.replace(tzinfo=TZGMT)

        TZ = gettz(timezone)
        
        date = date.astimezone(TZ)
        return date
    convert_to_timezone = classmethod(convert_to_timezone)




    # convert to UTC, no timezone.  If no timezone is given in the date, use local
    def convert(cls, date, is_gmt=False):
        if date == "CURRENT_TIMESTAMP":
            date = datetime.utcnow()

        elif isinstance(date, basestring):
            # parse and convert 
            date = parser.parse(date)

        # set the timezone to UTC
        if not is_gmt and date.tzinfo == None:
            # assume local timezone if none is given
            date = date.replace(tzinfo=TZLOCAL)
        else:
            offset = date.utcoffset()
            if offset:
                date = date - date.utcoffset()
            date = date.replace(tzinfo=TZGMT)
        
        #FIXME: it errors out on time before epoch
        try:
            utc = date.astimezone(TZUTC)
        except Exception as e:
            naive = date.replace(tzinfo=None)
        else:
            naive = utc.replace(tzinfo=None)
        return naive

    convert = classmethod(convert)


    def add_gmt_timezone(cls, date):
        if isinstance(date, basestring):
            try:
                # do not use cls.parse ... it does a convert.
                date = parser.parse(date)
            except:
                # This could be "now()", for example
                return date

        date = date.replace(tzinfo=TZGMT)
        return date
    add_gmt_timezone = classmethod(add_gmt_timezone)


    def add_local_timezone(cls, date):
        if isinstance(date, basestring):
            try:
                # do not use cls.parse ... it does a convert.
                date = parser.parse(date)
            except:
                # This could be "now()", for example
                return date

        date = date.replace(tzinfo=TZLOCAL)
        return date
    add_local_timezone = classmethod(add_local_timezone)

    def add_timezone(cls, date, timezone):
        '''add an arbitrary timezone without affecting the value'''
        if isinstance(date, basestring):
            try:
                # do not use cls.parse ... it does a convert.
                date = parser.parse(date)
            except:
                # This could be "now()", for example
                return date
        new_tz = gettz(timezone)

        date = date.replace(tzinfo=new_tz)
        return date
    add_timezone = classmethod(add_timezone)


    def has_timezone(cls, date):
        err = False
        
        if isinstance(date, basestring):
            try:
                # do not use cls.parse ... it does a convert.
                date = parser.parse(date)
            except:
                # This could be "now()", for example
                err = True
                pass
        if err:
            return False
        else:
            return date.tzinfo != None
    has_timezone = classmethod(has_timezone)
 

    def get_display_date(cls, date, date_format=None, timezone=None, include_time=False):
        '''Given a datetime value, convert to timezone, and convert to date format.'''
        from pyasm.biz import PrefSetting, ProjectSetting

        if not timezone:
            timezone = PrefSetting.get_value_by_key('timezone')
            if not timezone:
                timezone = ProjectSetting.get_value_by_key("timezone")

        if timezone in [None, "local", '']:
            value = SPTDate.convert_to_local(date)
        else:
            value = SPTDate.convert_to_timezone(date, timezone)
        
        setting = "date_format"
        if include_time:
            setting = "datetime_format"
        
        
        if not date_format:
            date_format = PrefSetting.get_value_by_key(setting)
            if not date_format:
                date_format = ProjectSetting.get_value_by_key(setting)

        if not date_format:
            date_format = "%Y %m %d"
            if include_time:
                date_format = "%Y %m %d %H:%M"

        try:
            encoding = locale.getlocale()[1]		
            value = value.strftime(date_format).decode(encoding)
        except:
            value = value.strftime(date_format)
           
        return value
   
    get_display_date = classmethod(get_display_date)



    def get_time_ago(cls, date, convert=False, start=None, show_date=True):

        if isinstance(date, basestring):
            date = parser.parse(date)

        if convert:
            date = cls.convert(date)
        else:
            date = cls.strip_timezone(date)

        if start:
            now = start
        else:
            now = cls.now()

        diff = now - date
        if diff.days < 0:
            diff = date - now
            txt = "from now"
        else:
            txt = "ago"



        if diff.days >= 7:
            if show_date in ['false', False]:
                value = "%s days %s" % (diff.days, txt)
            else:
                value = date.strftime("%b %d at %I:%M %p")

        elif diff.days == 1:
            value = "1 day %s" % txt

        elif diff.days > 1:
            value = "%s days %s" % (diff.days, txt)

        # less than a minute
        elif diff.seconds < 60:
            value = "%s seconds %s" % (diff.seconds, txt)

        # less than an hour
        elif diff.seconds < 60 * 60:
            minutes = diff.seconds / 60
            if minutes == 1:
                value = "1 minute %s" % txt
            else:
                value = "%s minutes %s" % (minutes, txt)

        # less than a day
        elif diff.seconds < 60 * 60 * 24:
            hours = float(diff.seconds) / 60.0 / 60.0
            if hours < 12:
                value = "%0.1f hours %s" % (hours, txt)
            else:
                value = "%s hours %s" % (int(hours), txt)


        else:
            value = date.strftime("%b %d at %I:%m %p")

        return value

    get_time_ago = classmethod(get_time_ago)


    def get_time_diff(cls, start=None, end=None, convert=False, txt=""):

        if isinstance(start, basestring):
            start = parser.parse(start)
        if isinstance(end, basestring):
            end = parser.parse(end)

        if convert:
            start = cls.convert(start)
            end = cls.convert(end)
        else:
            start = cls.strip_timezone(start)
            end = cls.strip_timezone(end)

        diff = end - start

        days = diff.days + float(int(10 * diff.seconds / (24*60*60))) / 10

        if diff.days == 0 and diff.seconds == 0:
            value = "-"

        elif abs(diff.days) > 1:
            value = "%s days %s" % (days, txt)

        # less than a minute
        elif diff.seconds < 60:
            value = "%s seconds %s" % (diff.seconds, txt)

        # less than an hour
        elif diff.seconds < 60 * 60:
            minutes = diff.seconds / 60
            if minutes == 1:
                value = "1 minute %s" % txt
            else:
                value = "%s minutes %s" % (minutes, txt)

        # less than a day
        elif diff.seconds < 60 * 60 * 24:
            hours = float(diff.seconds) / 60.0 / 60.0
            if hours < 12:
                value = "%0.1f hours %s" % (hours, txt)
            else:
                value = "%s hours %s" % (int(hours), txt)


        else:
            value = date.strftime("%b %d at %I:%m %p")

        return value

    get_time_diff = classmethod(get_time_diff)




if __name__ == '__main__':


    date1 = SPTDate.now()
    date2 = SPTDate.now()

    #print("Date 1 :" , date1 , " Date 2: ", date2)

    #print(SPTDate.get_business_days_duration(date1, date2))





