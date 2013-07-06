// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2010, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


alert("date_util.js is deprecated");

spt.date_util = {};
spt.date_util.ymd = {};

spt.date_util.two_digit_month_map = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
};


spt.date_util.two_digit_short_month_map = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'May',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Aug',
    '09': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec'
};


spt.date_util.ymd.get_month_str = function( ymd_str )
{
    var bits = ymd_str.split("-");
    var two_digit_month = bits[1];
    return spt.date_util.two_digit_month_map[ two_digit_month ];
}


spt.date_util.ymd.get_short_month_str = function( ymd_str )
{
    var bits = ymd_str.split("-");
    var two_digit_month = bits[1];
    return spt.date_util.two_digit_short_month_map[ two_digit_month ];
}


spt.date_util.ymd.get_week = function( ymd_str )
{
    var bits = ymd_str.split("-");
    var year = parseInt(bits[0]);
    var month = parseInt(bits[1].replace(/^0+/,''))-1;
    var day = parseInt(bits[2].replace(/^0+/,''));
    var one_jan = new Date(year,0,1);
    var this_date = new Date(year,month,day);

    var days = (this_date - one_jan) / (60*60*24*1000);
    var first_sun = 6 - one_jan.getDay();
    var weeks = Math.ceil((days - first_sun) / 7) + 1;
    return weeks;
}





spt.date_util.ymd.convert_to_date_obj = function( ymd_str )
{
    // Assumes ymd_str is in format 'YYYY-MM-DD' (e.g. '2010-01-27') ... it will strip off
    // timestamp if in a format like this '2010-01-27 13:45:33:00'
    //
    if( ymd_str.match( /\s+/ ) ) {
        ymd_str = ymd_str.split( /\s+/ )[0];
    }

    if( ! ymd_str.match( /^(\d{4})\-(\d{2})\-(\d{2})$/ ) ) {
        return null;
    }

    var bits = ymd_str.split( '-' );
    var year = parseInt(bits[0],10);
    var month = parseInt(bits[1],10) - 1;
    var day = parseInt(bits[2],10);

    var date_obj = new Date();
    date_obj.setFullYear( year, month, day );

    return date_obj;
}


spt.date_util.ymd.today = function()
{
    var today_date = new Date();
    var today_str = "" + today_date.getFullYear() + "-" +
                    spt.zero_pad( today_date.getMonth()+1, 2 ) + "-" +
                    spt.zero_pad( today_date.getDate(), 2 );
    return today_str;
}


spt.date_util.ymd.get_day_str = function( ymd_str, format )
{
    var date_obj = spt.date_util.ymd.convert_to_date_obj( ymd_str );
    return spt.date_util.get_day_str( date_obj, format );
}


spt.date_util.get_day_str = function( date_obj, format )
{
    var weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
    var weekdays_short = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    if( format == 'short' ) {
        return weekdays_short[ date_obj.getDay() ];
    }
    return weekdays[ date_obj.getDay() ];
}

spt.date_util.get_today_day_str = function( format )
{
    return spt.date_util.get_day_str( new Date(), format );
}


