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

__all__ = ["Date", "Calendar"]

from base import *
from common import *
from environment import Environment
from calendar import *
from time import *
import _strptime
from datetime import date


# DEPRECATED: datetime and dateutil are far better
class Date(Base):
    '''Date class that can convert to different dates use in various placess'''

    def __init__(my, db=None, ctime=None, db_date=None, show_warning=True):

        # internally stored time
        my.struct_time = None
        my.show_warning = show_warning

        # format = YYYY-MM-DD HH:MM:SS.SSSS
        if db in ["now", '{now}']:
            my.struct_time = localtime()
        elif db != None:
            # make sure db is a string
            db = str(db)


            # get rid of the decimal (high precision)
            if db.find(".") != -1:
                db, tmp = db.split(".")

            try: 
                my.struct_time = strptime(db, r'%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    my.struct_time = strptime(db, r'%Y-%m-%d')
                except ValueError:
                    try:
                        # try without seconds
                        my.struct_time = strptime(db, r'%Y-%m-%d %H:%M')
                    except ValueError:
                        # try another format
                        try:
                            my.struct_time = strptime(db, r'%b %d, %Y - %H:%M')
                        except ValueError:
                            # try another format
                            my.struct_time = strptime(db, r'%H:%M:%S')

 

        elif ctime != None:
            my.struct_time = strptime(ctime)
        elif db_date != None:
            db_date = str(db_date)
            if db_date.find(" ") != -1:
                db_date, tm = db_date.split(" ", 1)
            try:
                my.struct_time = strptime(db_date, r'%Y-%m-%d')
            except ValueError, e:
                my.struct_time = localtime()
                if my.show_warning:
                    Environment.add_warning('invalid time format', "bad time format [%s]" %db_date)
        else:
            my.struct_time = localtime()


    def copy(my):
        time = my.get_db_time()
        date = Date(db=time)
        return date



    def get_struct_time(my):
        return my.struct_time

    def get_display(my, pattern):
        return strftime(pattern,my.struct_time)


    def get_display_datetime(my):
        return strftime("%b %d, %Y - %H:%M",my.struct_time)

    def get_display_time(my):
        return strftime("%H:%M",my.struct_time)

    def get_display_date(my):
        return strftime("%b %d, %Y",my.struct_time)


    def get_db_time(my):
        return strftime("%Y-%m-%d %H:%M:%S",my.struct_time)

    def get_db_date(my):
        return strftime("%Y-%m-%d",my.struct_time)


    def get_year(my):
        return strftime("%Y",my.struct_time)

    def get_month(my, is_digit=True):
        if is_digit:
            return strftime("%m",my.struct_time)
        else:
            # this is abbreviated month
            return strftime("%b",my.struct_time)

    def get_day(my):
        return strftime("%d",my.struct_time)

    def get_week(my):
        '''Monday is the first day of the week. ISO Standard is used'''
        #return strftime("%W",my.struct_time)
        # we want to get the iso week which ranges from [1, 52]
        my_date = date(int(my.get_year()), int(my.get_month(is_digit=True)),\
            int(my.get_day()))
        week = my_date.isocalendar()[1]
        return week

    def get_weekday(my, is_digit=False):
        if is_digit:
            # fix the assumption that Sunday is the first day of the week
            weekday = int(strftime("%w",my.struct_time))
            weekday -= 1
            if weekday < 0:
                weekday = 6
            return weekday
        else:
            return strftime("%a",my.struct_time)
    
    def get_monthday(my):
        return strftime("%d",my.struct_time)

    def get_time(my):
        return strftime("%H:%M:%S",my.struct_time)
    
    def get_utc(my):
        return mktime(my.struct_time)

    def add_minutes(my, mins):
        utc = mktime(my.struct_time)
        utc = utc + (60 * mins)
        my.struct_time = localtime(utc)

    def add_hours(my, hours):
        utc = mktime(my.struct_time)
        utc = utc + (60 * 60) * hours
        my.struct_time = localtime(utc)



    def add_days(my, days):
        utc = mktime(my.struct_time)
        utc = utc + (24 *  60 * 60) * days
        my.struct_time = localtime(utc)

    def subtract_days(my, days):
        utc = mktime(my.struct_time)
        utc = utc - (24 *  60 * 60) * days
        my.struct_time = localtime(utc)

    def add_years(my, years):
        utc = mktime(my.struct_time)
        utc = utc + (365 * 24 *  60 * 60) * years
        my.struct_time = localtime(utc)


    def get_diff_days(my, date):
        '''calculates the difference in days between 2 dates'''
        my_utc = my.get_utc()
        utc = date.get_utc()

        diff = utc - my_utc
        # don't int this as it rounds up too much
        diff = diff/(24*60*60)
        return diff

    def get_diff_hours(my, date):
        '''calculates the difference in days between 2 dates'''
        my_utc = my.get_utc()
        utc = date.get_utc()

        diff = utc - my_utc
        diff = int(diff/(60*60))
        return diff

        
        

class Calendar(Base):
    ''' a calendar class that provides calendar-related static functions'''

    WEEK_CALENDAR = ["mon","tue","wed","thu","fri","sat","sun"]

    def get_num_days(year, month):
        weekday, num = monthrange(year, month)
        return num
    get_num_days = staticmethod(get_num_days)

    def get_weekday(year, month, day):
        return weekday(year, month, day)
    get_weekday = staticmethod(get_weekday)

    def get_month_calendar(year, month):
        return monthcalemdar(year, month)
    get_month_calendar = staticmethod(get_month_calendar)

    def get_monthday_time(year, week, month_digit=False):
        '''given year # and week #, a list of (month, monthday, time) 
           for the week is returned'''
        #FIXME should ditch this method. as it doesn't account for some years have 53 weeks
        week = int(week)
        year = int(year)

        today = Date()
        current_week = int(today.get_week())
        current_year = int(today.get_year())
        if week:
            # get the week diffrernce of this week and the chosen week
            weeks_diff = (week - current_week) + (int(year) - current_year) * 52
            today.add_days( weeks_diff * 7 )
        week_day = int(today.get_weekday(is_digit=True))
        
        weekday_list = []

        # this is the chosen date
        selected_date = today.get_db_date()
        for day in xrange(0, len(Calendar.WEEK_CALENDAR)):
            
            target_date = Date(db_date=selected_date)
            diff = day - week_day
            target_date.add_days(diff)
            target_month = target_date.get_month(is_digit=month_digit)
             
            weekday_list.append((target_month, target_date.get_monthday(), target_date.get_struct_time()))
        return weekday_list
    get_monthday_time = staticmethod(get_monthday_time)
