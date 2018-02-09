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

    def __init__(self, db=None, ctime=None, db_date=None, show_warning=True):

        # internally stored time
        self.struct_time = None
        self.show_warning = show_warning

        # format = YYYY-MM-DD HH:MM:SS.SSSS
        if db in ["now", '{now}']:
            self.struct_time = localtime()
        elif db != None:
            # make sure db is a string
            db = str(db)


            # get rid of the decimal (high precision)
            if db.find(".") != -1:
                db, tmp = db.split(".")

            try: 
                self.struct_time = strptime(db, r'%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    self.struct_time = strptime(db, r'%Y-%m-%d')
                except ValueError:
                    try:
                        # try without seconds
                        self.struct_time = strptime(db, r'%Y-%m-%d %H:%M')
                    except ValueError:
                        # try another format
                        try:
                            self.struct_time = strptime(db, r'%b %d, %Y - %H:%M')
                        except ValueError:
                            # try another format
                            self.struct_time = strptime(db, r'%H:%M:%S')

 

        elif ctime != None:
            self.struct_time = strptime(ctime)
        elif db_date != None:
            db_date = str(db_date)
            if db_date.find(" ") != -1:
                db_date, tm = db_date.split(" ", 1)
            try:
                self.struct_time = strptime(db_date, r'%Y-%m-%d')
            except ValueError, e:
                self.struct_time = localtime()
                if self.show_warning:
                    Environment.add_warning('invalid time format', "bad time format [%s]" %db_date)
        else:
            self.struct_time = localtime()


    def copy(self):
        time = self.get_db_time()
        date = Date(db=time)
        return date



    def get_struct_time(self):
        return self.struct_time

    def get_display(self, pattern):
        return strftime(pattern,self.struct_time)


    def get_display_datetime(self):
        return strftime("%b %d, %Y - %H:%M",self.struct_time)

    def get_display_time(self):
        return strftime("%H:%M",self.struct_time)

    def get_display_date(self):
        return strftime("%b %d, %Y",self.struct_time)


    def get_db_time(self):
        return strftime("%Y-%m-%d %H:%M:%S",self.struct_time)

    def get_db_date(self):
        return strftime("%Y-%m-%d",self.struct_time)


    def get_year(self):
        return strftime("%Y",self.struct_time)

    def get_month(self, is_digit=True):
        if is_digit:
            return strftime("%m",self.struct_time)
        else:
            # this is abbreviated month
            return strftime("%b",self.struct_time)

    def get_day(self):
        return strftime("%d",self.struct_time)

    def get_week(self):
        '''Monday is the first day of the week. ISO Standard is used'''
        #return strftime("%W",self.struct_time)
        # we want to get the iso week which ranges from [1, 52]
        my_date = date(int(self.get_year()), int(self.get_month(is_digit=True)),\
            int(self.get_day()))
        week = my_date.isocalendar()[1]
        return week

    def get_weekday(self, is_digit=False):
        if is_digit:
            # fix the assumption that Sunday is the first day of the week
            weekday = int(strftime("%w",self.struct_time))
            weekday -= 1
            if weekday < 0:
                weekday = 6
            return weekday
        else:
            return strftime("%a",self.struct_time)
    
    def get_monthday(self):
        return strftime("%d",self.struct_time)

    def get_time(self):
        return strftime("%H:%M:%S",self.struct_time)
    
    def get_utc(self):
        return mktime(self.struct_time)

    def add_minutes(self, mins):
        utc = mktime(self.struct_time)
        utc = utc + (60 * mins)
        self.struct_time = localtime(utc)

    def add_hours(self, hours):
        utc = mktime(self.struct_time)
        utc = utc + (60 * 60) * hours
        self.struct_time = localtime(utc)



    def add_days(self, days):
        utc = mktime(self.struct_time)
        utc = utc + (24 *  60 * 60) * days
        self.struct_time = localtime(utc)

    def subtract_days(self, days):
        utc = mktime(self.struct_time)
        utc = utc - (24 *  60 * 60) * days
        self.struct_time = localtime(utc)

    def add_years(self, years):
        utc = mktime(self.struct_time)
        utc = utc + (365 * 24 *  60 * 60) * years
        self.struct_time = localtime(utc)


    def get_diff_days(self, date):
        '''calculates the difference in days between 2 dates'''
        my_utc = self.get_utc()
        utc = date.get_utc()

        diff = utc - my_utc
        # don't int this as it rounds up too much
        diff = diff/(24*60*60)
        return diff

    def get_diff_hours(self, date):
        '''calculates the difference in days between 2 dates'''
        my_utc = self.get_utc()
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
