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

__all__ = ['ExpressionParser']


import os, re, types, math
import dateutil
from dateutil import parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
import calendar
import datetime

from pyasm.common import TacticException, Environment, Container, FormatValue
from pyasm.search import Search, SObject, SearchKey, SearchType

from project import Project

class ParserException(TacticException):
    pass





class ExpressionParser(object):
        
    EXPRESSION_KEY = "Expression:keys"
    def __init__(my):
        my.init()


    def init(my):
        my.env_sobjects = {}
        my.expression = None
        my.index = -1
        my.sobjects = []
        my.result = None
        my.vars = {}
        my.show_retired = False
        my.state = {}
        my.return_mode = 'array'
        my.is_single = False


    def eval(my, expression, sobjects=None, mode=None, single=False, list=False, dictionary=False, vars={}, env_sobjects={}, show_retired=False, state={}, extra_filters={} ):

        if not expression:
            return ''

        my.init()


        if dictionary == True:
            return_mode = 'dict'
        elif single == True:
            return_mode = 'single'
        else:
            return_mode = 'array'
        Container.put("Expression::return_mode", return_mode)

        if sobjects == None:
            #my.is_single = False
            sobjects = []
     
        elif type(sobjects) != types.ListType:
            #my.is_single = True
            sobjects = [sobjects]
      

        my.show_retired = show_retired


        my.expression = expression
        my.sobjects = sobjects
        my.env_sobjects = env_sobjects
        my.state = state

        my.vars = {}
        my.vars.update( my.get_date_vars() )

        # add the environment
        login = Environment.get_login()
        if login:
            my.vars['LOGIN'] = login.get_value("login")
            my.vars['LOGIN_ID'] = login.get_id()

            # add users in login group
            from pyasm.security import LoginGroup
            login_codes = LoginGroup.get_login_codes_in_group()
            login_codes = "|".join(login_codes)
            my.vars['LOGINS_IN_GROUP'] = login_codes


        project = Project.get_project_code()
        my.vars['PROJECT'] = project

        if vars:
            my.vars.update(vars)
 
        # replace all of the variables: Note that this replaces even in the
        # string area ... not sure if this is what we want
        keys = my.vars.keys()
        keys.sort()
        keys.reverse()
        #for name, value in my.vars.items():
        for name in keys:
            value = my.vars.get(name)
            new_value = "'%s'" % str(value)
            # HACK: replace with the single quotes first.  Not elegant, but
            # it works for now until we have real variables
            my.expression = my.expression.replace("'$%s'" % name, new_value)
            my.expression = my.expression.replace("$%s" % name, new_value)



        if not mode:
            # start in string mode
            string_idx = my.expression.find("{")
            expr_idx = my.expression.find("@")

            if string_idx == -1:
                new_parser = ExpressionMode()
            elif expr_idx == -1:
                new_parser = StringMode()
            elif expr_idx < string_idx:
                new_parser = ExpressionMode()
            else:
                new_parser = StringMode()
                my.is_single = False
    
        elif mode == 'expression':
            # start in string mode
            new_parser = ExpressionMode()
            my.is_single = True
        elif mode == 'string':
            new_parser = StringMode()
            my.is_single = True

            # if the are no {}, then just exit ... no use parsing
            string_idx = my.expression.find("{")
            if string_idx == -1:
                return my.expression


        if single:
            my.is_single = True
        if list:
            my.is_single = False

        
        Container.put("Expression::extra_filters", extra_filters)

        my.dive(new_parser)
        Container.put("Expression::extra_filters", None)
        if my.is_single and type(my.result) == types.ListType: 
            if my.result:
                return my.result[0]
            else:
                # for single, should return None
                return None
        elif list and type(my.result) != types.ListType:
            return [my.result]
        else:
            return my.result



    def get_date_vars(my):
        date_vars = Container.get("Expression:date_vars")
        if date_vars != None:
            return date_vars

        date_vars = {}
        Container.put("Expression:date_vars", date_vars)

        today = datetime.datetime.today()
        today = datetime.datetime(today.year, today.month, today.day)
        now = datetime.datetime.now()
        year = datetime.datetime(today.year, 1, 1)
        month = datetime.datetime(today.year, today.month, 1)

        hour = datetime.datetime(now.year, now.month, now.day, now.hour)
        min = datetime.datetime(now.year, now.month, now.day, hour=now.hour, minute=now.minute)

        date_vars['TODAY'] = today
        date_vars['NEXT_DAY'] = today + relativedelta(days=1)
        date_vars['PREV_DAY'] = today + relativedelta(days=-1)


        date_vars['NOW'] = now

        date_vars['NEXT_HOUR'] = hour + relativedelta(hours=1)
        date_vars['THIS_HOUR'] = hour
        date_vars['PREV_HOUR'] = hour + relativedelta(hours=-1)

        date_vars['NEXT_MINUTE'] = now + relativedelta(minutes=1)
        date_vars['THIS_MINUTE'] = now
        date_vars['PREV_MINUTE'] = now + relativedelta(minutes=-1)


        date_vars['NEXT_MONDAY'] = today + relativedelta(weekday=MO)
        date_vars['PREV_MONDAY'] = today + relativedelta(weeks=-1,weekday=MO)
        date_vars['THIS_MONDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=1)

        date_vars['NEXT_TUESDAY'] = today + relativedelta(weekday=TU)
        date_vars['PREV_TUESDAY'] = today + relativedelta(weeks=-1,weekday=TU)
        date_vars['THIS_TUESDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=2)

        date_vars['NEXT_WEDNESDAY'] = today + relativedelta(weekday=WE)
        date_vars['PREV_WEDNESDAY'] = today + relativedelta(weeks=-1,weekday=WE)
        date_vars['THIS_WEDNESDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=3)

        date_vars['NEXT_THURSDAY'] = today + relativedelta(weekday=TH)
        date_vars['PREV_THURSDAY'] = today + relativedelta(weeks=-1,weekday=TH)
        date_vars['THIS_THURSDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=4)

        date_vars['NEXT_FRIDAY'] = today + relativedelta(weekday=FR)
        date_vars['PREV_FRIDAY'] = today + relativedelta(weeks=-1,weekday=FR)
        date_vars['THIS_FRIDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=5)

        date_vars['NEXT_SATURDAY'] = today + relativedelta(weekday=SA)
        date_vars['PREV_SATURDAY'] = today + relativedelta(weeks=-1,weekday=SA)
        date_vars['THIS_SATURDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=6)

        date_vars['NEXT_SUNDAY'] = today + relativedelta(weekday=SU)
        date_vars['PREV_SUNDAY'] = today + relativedelta(weeks=-1,weekday=SU)
        date_vars['THIS_SUNDAY'] = today + relativedelta(weeks=-1,weekday=SU) + relativedelta(days=7)

        date_vars['2_SUNDAYS_AHEAD'] = date_vars['NEXT_SUNDAY']+relativedelta(days=7)
        date_vars['2_SUNDAYS_AGO'] = date_vars['PREV_SUNDAY']+relativedelta(days=-7)


        date_vars['NEXT_MONTH'] = month + relativedelta(months=1)
        date_vars['THIS_MONTH'] = month
        date_vars['PREV_MONTH'] = month + relativedelta(months=-1)

        date_vars['NEXT_YEAR'] = year + relativedelta(years=1)
        date_vars['THIS_YEAR'] = year
        date_vars['PREV_YEAR'] = year + relativedelta(years=-1)

        for i in range(1, 12):
            date_vars['%d_DAY_AGO'%i] = today + relativedelta(days=-i)
            date_vars['%d_DAY_AHEAD'%i] = today + relativedelta(days=+i)
            date_vars['%d_DAYS_AGO'%i] = today + relativedelta(days=-i)
            date_vars['%d_DAYS_AHEAD'%i] = today + relativedelta(days=+i)

            date_vars['%d_WEEK_AGO'%i] = today + relativedelta(weeks=-i)
            date_vars['%d_WEEK_AHEAD'%i] = today + relativedelta(weeks=+i)
            date_vars['%d_WEEKS_AGO'%i] = today + relativedelta(weeks=-i)
            date_vars['%d_WEEKS_AHEAD'%i] = today + relativedelta(weeks=+i)

            date_vars['%d_MONTH_AGO'%i] = today + relativedelta(months=-i)
            date_vars['%d_MONTH_AHEAD'%i] = today + relativedelta(months=+i)
            date_vars['%d_MONTHS_AGO'%i] = today + relativedelta(months=-i)
            date_vars['%d_MONTHS_AHEAD'%i] = today + relativedelta(months=+i)
            date_vars['%d_YEAR_AGO'] = today + relativedelta(years=-i)
            date_vars['%d_YEAR_AHEAD'] = today + relativedelta(years=+i)
            date_vars['%d_YEARS_AGO'] = today + relativedelta(years=-i)
            date_vars['%d_YEARS_AHEAD'] = today + relativedelta(years=+i)
        return date_vars




    def get_result(my):
        return my.result

    def get_env_sobject(my, key):
        return my.env_sobjects.get(key)


    def get_cache_sobjects(my):
        '''method to store all the sobjects as they being searched through
        the hierarchy'''
        cache = Container.get_full_dict('Expression:%s' % my.expression)
        return cache


    def cache_sobjects(my, sobject, related_sobjects):
        '''method to store all the sobjects as they being searched through
        the hierarchy'''
        if not related_sobjects:
            related_sobjects = []

        cache = Container.get_full_dict('Expression:%s' % my.expression)
        cache[sobject] = related_sobjects


        if isinstance(sobject, basestring):
            search_key = sobject
        else:
            search_key = SearchKey.get_by_sobject(sobject)

        cache[search_key] = related_sobjects


    def get_flat_cache(my, filter_leaf=False):
        cache_sobjects = my.get_cache_sobjects()
        flat_cache_sobjects = {}
        level = 0
        for sobject in my.sobjects:
            leaf_sobjects = []
            search_key = sobject.get_search_key()
            my._flatten_cache(sobject, level, cache_sobjects, leaf_sobjects)

            # FIXME
            # _flatten_cache return a bizarre case where the leaf = [sobject]
            # to determine
            # This is run in the gantt widget
            if filter_leaf and leaf_sobjects    \
                    and leaf_sobjects[0].get_search_key() == search_key:
                continue

            flat_cache_sobjects[search_key] = leaf_sobjects

       
        return flat_cache_sobjects



    def _flatten_cache(my, top_sobject, level, cache_sobjects, leaf_sobjects):
        search_key = top_sobject.get_search_key()
        #print " "*level*2, "- ", search_key
        # flatten the cache_sobjects
        sobjects = cache_sobjects.get(search_key)
        if not sobjects:
            # if [] is returned, then there are no children.  if None
            # is returned, then this is a leaf
            if sobjects == None:
                leaf_sobjects.append(top_sobject)
            return

        # sobjects could be a single value
        if not isinstance(sobjects, list):
            leaf_sobjects.append(top_sobject)
            return

        level += 1

        for sobject in sobjects:
            # it coould be a value
            if not isinstance(sobject, SObject) or not sobject:
                continue
          
            my._flatten_cache(sobject, level, cache_sobjects, leaf_sobjects)

    #
    # These methods allow for querying the leaf values for each sobject on
    # an expression that started with multiple sobjects.
    #
    def get_result_by_sobject(my, sobject):
        results = my.get_results_by_sobject(sobject)
        if results:
            return results[0]
        else:
            return None

    def get_results_by_sobject(my, sobject):
        key = sobject.get_search_key()
        relationships = my.get_cache_sobjects()

        # only go one level right now
        results = []
        while 1:
            nodes = relationships.get(key)
            if nodes:
                for key in nodes:
                    result = relationships.get(key)
                    results.append(result)
            #results = nodes
            break
        return results

    def get_results_by_sobject_dict(my):
        results = {}
        for sobject in my.sobjects:
            key = sobject.get_search_key()
            sobj_results = my.get_results_by_sobject(sobject)
            results[key] = sobj_results
        return results

    def get_result_by_sobject_dict(my):
        '''get a single result for each sobject organized by a dictionary'''
        results = {}
        for sobject in my.sobjects:
            key = sobject.get_search_key()
            sobj_results = my.get_result_by_sobject(sobject)
            results[key] = sobj_results
        return results





    def _find_sqr_brackets(my, filter):
        '''get the [ ] in the string and pass it to SqrBracketMode''' 
        # use greedy search
        p = re.compile("(\[.*\])")
        m = p.findall(filter)
        if m:
            filter = m[0]
            mode = SqrBracketMode()
            rtn = my.dive(mode, expression=filter)
        else:
            rtn = []

        return rtn


    def _split_arg(my, arg):
        parts = []
        

        #p = re.compile("(\[.*?\])")
        #filters = p.findall(arg)
        filters = my._find_sqr_brackets(arg)
        if not filters:
            return arg.split(".")

        tmp_arg = arg
        for i, filter in enumerate(filters):
            tmp_arg = tmp_arg.replace(filter, "$__FILTER%0.2d__" % i)

        parts = tmp_arg.split(".")
        for j, part in enumerate(parts):
            for i, filter in enumerate(filters):
                part = part.replace("$__FILTER%0.2d__" % i, filters[i])
            parts[j] = part

        return parts
        
    def get_plain_related_types(my, expression):
        '''get plain related_types without the filters in an expression. This is similar to _split_arg()'''
        # this should work in a nested expression as well with @UNIQUE 
        m = re.match(r'.*@SOBJECT\((.*?)\)*$',expression)
        if not m:
            return []
        arg = m.groups()[0]
        parser = ExpressionParser()

        parts = []

        filters = my._find_sqr_brackets(arg)
        if not filters:
            return arg.split(".")

        tmp_arg = arg
        for i, filter in enumerate(filters):
            tmp_arg = tmp_arg.replace(filter, '')

        parts = tmp_arg.split(".")
        for j, part in enumerate(parts):
            parts[j] = part

        return parts

    def do_parse(my):
        
        while(1):
            char = my.expression[my.index]
            value = my.parse(char)
            if value == 'continue':
                my.result = None
                my.stack = []

            if value == 'exit':
                return

            my.index += 1

            if my.index >= len(my.expression):
                break



    def dive(my, new_parser, reuse_token=False, expression=None):

        # handle the case where expression is empty ... no reason to go further
        if expression == '':
            return ''

        if expression:
            new_parser.expression = expression
            new_parser.index = 0
        else:
            new_parser.expression = my.expression
            if reuse_token:
                new_parser.index = my.index
            else:
                new_parser.index = my.index + 1



        new_parser.sobjects = my.sobjects
        new_parser.env_sobjects = my.env_sobjects
        new_parser.state = my.state
        new_parser.vars = my.vars
        new_parser.show_retired = my.show_retired

        new_parser.do_parse()

        # get the result from the parse
        my.result = new_parser.get_result()

        if not expression:
            my.index = new_parser.index

        return my.result


    def get_mode(my, expression):
        # start in string mode
        string_idx = expression.find("{")
        expr_idx = expression.find("@")

        if string_idx == -1:
            new_parser = ExpressionMode()
        elif expr_idx == -1:
            new_parser = StringMode()
        elif expr_idx < string_idx:
            new_parser = ExpressionMode()
        else:
            new_parser = StringMode()

        return new_parser


    def clear_cache():
        Container.clear_dict(ExpressionParser.EXPRESSION_KEY)
    clear_cache = staticmethod(clear_cache)


class StringMode(ExpressionParser):

    def __init__(my):
        my.stack = []

        my.arg = []
        
        super(StringMode, my).__init__()

    def get_result(my):
        try:
            result =  "".join( my.stack )
        except UnicodeDecodeError:
            my.stack = [ x.decode('utf-8') if type(x)==types.StringType else x for x in my.stack]
            result =  "".join( my.stack )
        return result


    def parse(my, token):
        # go in to expression mode
        if token == '{':
            mode = ExpressionMode()
            result = my.dive(mode)

            # FIXME: for now, take the first element
            if type(result) == types.ListType:
                if not result:
                    result = ''
                else:
                    result = result[0]
                    if isinstance(result, SObject):
                        result = result.get_display_value()



            if my.expression[my.index] != '}':

                mode = StringFormatMode()
                format = my.dive(mode)
                format = format.strip()
                if isinstance(result, datetime.datetime):
                    try:
                        result = result.strftime(str(format))
                    except Exception, e:
                        raise SyntaxError("Error when using format [%s] on datetime result [%s] in expression [%s]: [%s]" % (format, result, my.expression, str(e)))

                # FIXME: does this make sense??
                # if it is a timedelta, convert to seconds for
                # formatting
                elif isinstance(result, datetime.timedelta):
                    result = result.seconds

                elif format.startswith("%"):
                    if result == None:
                        result = ''
                    else:
                        try:
                            result = format % result
                        except Exception, e:
                            # handle the case where an integer is expected
                            # in the string formatting
                            if str(e) == "an integer is required":
                                result = ''
                            elif str(e) == "a float is required":
                                result = ''
                            else:
                                #raise SyntaxError("Error when using format [%s] on result [%s] in expression [%s]: [%s]" % (format, result, my.expression, str(e)))
                                result = ''
                elif format.startswith("format="):

                    # {@GET(.cost),-$1,234.00}
                    format_value = FormatValue()
                    parts = format.split("=")
                    format = parts[1]
                    format = format.strip("'")
                    result = format_value.get_format_value(result, format)


                else: # regex formatting
                    if not result:
                        result = ''
                    else:
                        p = re.compile(format)
                        m = p.search(result)
                        if m:
                            groups = m.groups()
                            if groups:
                                result = ''.join(groups)
                                # just take the first one right now
                                #result = m.groups()[0]

            if not isinstance(result, basestring):
                result = str(result)
            my.stack.append(result)

        elif token == '}':
            return 'exit'

        else:
            my.stack.append(token)



       

 

class StringFormatMode(ExpressionParser):

    def __init__(my):
        my.format = []

        my.start_char = False
        my.brackets = 0
        super(StringFormatMode, my).__init__()

    def get_result(my):
        return "".join(my.format)

    def parse(my, token):

        if not my.start_char and token == '}':
            return "exit"

        elif token == my.start_char: 
            # using matching parentheses to ensure | is not part of an expression
            if my.brackets == 0:
                # skip pass the } after |
                char = my.expression[my.index]
                while char != '}':
                    my.index += 1
                    char = my.expression[my.index]
                return "exit"
            else:
                my.format.append(token)
             

        #elif token == ' ':
        #    pass

        elif token == '|':
            my.start_char = token

        else:
            if token == '(':
                my.brackets += 1
            elif token == ')':
                my.brackets -= 1
            my.format.append(token)



class ExpressionMode(ExpressionParser):

    def __init__(my):
        my.stack = []
        my.literal = []
        my.literal_mode = False

        super(ExpressionMode, my).__init__()


    def get_result(my):
        my.handle_literal()

        if len(my.stack) == 1:
            # FIXME: not sure why this is double array?
            return my.stack[0]

        # go through the stack and calculate
        value = my.evaluate_stack(my.stack)
        my.result = value

        return my.result



    EMPTY_LITERAL = '!!!_^^^_!!!'

    def parse(my, token):
        # make special provision for literal (string) mode
        if my.literal_mode:
            if token == "'":
                my.literal_mode = False
                if not my.literal:
                    # NEED A SPECIAL STRING TO GET BY LITERAL CHECKS
                    my.literal = [my.EMPTY_LITERAL]
            else:
                my.literal.append(token)
            return

        # if the next character is }, then exit
        if token == '}':
            return 'exit'
       
        elif token == '@':
            mode = MethodMode()
            my.result = my.dive(mode)
            my.stack.append(my.result)


        elif token == ',':
            return 'exit'

        elif token == '(':
            mode = ExpressionMode()
            value = my.dive(mode)
            my.stack.append(value)


        elif token == ')':
            return 'exit'


        elif token == '-':
            try:
                # handle negative number
                int(my.expression[my.index+1])
                my.literal.append(token)
            except ValueError:
                my.handle_literal()
                my.stack.append(token)

        elif token in ['+', '-', '/', '*', '~']:

            my.handle_literal()

            my.stack.append(token)

        #elif op in ['>','>=','==','=','<','<=']:
        elif token in ['>','=','<','!']:
            my.handle_literal()

            if my.expression[my.index+1] in ['=','!']:
                token += '='
                my.index += 1
            elif my.expression[my.index+1] in ['~']:
                token += '~'
                my.index += 1

            my.stack.append(token)

        elif token in ["'"]:
            my.literal_mode = True
            return

        elif token in [' ', '\t', '\n']:
            my.handle_literal()

        elif token in [';']:
            return "continue"

        else:
            # append to the literal if this is any other token
            my.literal.append(token)

            #raise SyntaxError("Unrecognized token [%s] in expression mode in line [%s]" % (token, my.expression))


    def handle_literal(my):
        if not my.literal:
            return

        literal = "".join(my.literal)

        # parse the shorthand
        literal = my.handle_shorthand(literal)
        if literal == '':
            return 0
        try:
            literal = float(literal)
        except ValueError:
            #raise SyntaxError("Expression contains non-number element [%s] in [%s]" % (literal, my.expression))
            pass

        if literal == my.EMPTY_LITERAL:
            literal = ''
        
        my.stack.append(literal)
        my.literal = []



    def handle_shorthand(my, expr):

        my.literal_sobjects = {
            'login': Environment.get_login(),
            #'sobjects': my.sobject,
            #'snapshot': my.snapshot,
            #'file': my.file_object,
        }

        my.literal_vars = {
            'login': Environment.get_user_name(),
            #'version': '003'
        }



        # find sobject.column
        if expr.find(".") != -1:
            type, attr = expr.split(".", 1)

            literal_value = my.literal_sobjects.get(type)
            if literal_value:
                return literal_value.get_value(attr)

        # find single values
        literal_value = my.literal_vars.get(expr)
        if literal_value:
            return literal_value

        return expr
 




    def evaluate_stack(my, stack):
        # build the expression for each element
        num_elements = 0
        for item in stack:
            if type(item) == types.ListType:
                num_elements = len(item)
        if num_elements == 0:
            num_elements = 1

        # figure out the default
        default = ''
        for i, item in enumerate(stack):
            if i % 2 == 1:
                continue

            if type(item) == types.ListType:
                if len(item) == 0:
                    continue
                else:
                    item = item[0]

            if item in [None, '']:
                continue

            if type(item) == types.FloatType:
                default = 0.0
                break
            elif type(item) == types.IntType:
                default = 0
                break
            elif isinstance(item, datetime.datetime):
                default = "parser.parse('1900-01-01')"
                break

        # special cases
        # we have a regular exprssion
        if len(stack) >= 3 and stack[1] in ['~', '=~', '!~']:
            left = stack[0]
            op = stack[1]
            is_single = False
            if isinstance(left, basestring):
                left = [left]
                is_single = True
            regex = stack[2]
            results = []
            for item in left:
                p = re.compile(regex)
                m = p.search(item)
                if (op in ['=~','~'] and m != None) or (op == '!~' and m == None):
                    results.append(True)
                else:
                    results.append(False)
            if is_single:
                return results[0]
            else:
                return results
        
        # format
        results = []
        for i in range(0, num_elements):
            elements = []
            for item in stack:

                if type(item) == types.ListType:
                    if len(item) == 0:
                        value = default
                    else:
                        value = item[i]
                        if value in ['', None]:
                            value = default

                elif item == '=':
                    value = '=='

                else:
                    value = item

                # process the time value
                # FIXME: this is a bit hacky!
                if isinstance(value, datetime.datetime):
                    value = "parser.parse('%s')" % value
                #else:
                #    value = str(value)

                elements.append(value)

            # either its all strings or all numbers??
            # assume <1> op <2> op <3>
            has_string = False
            for i, element in enumerate(elements):
                if i % 2 == 1:
                    continue
                if type(element) in types.StringTypes:
                    has_string = True
                    break
 
            if has_string:
                offset = 0
                for i, element in enumerate(elements):
                    # special case with a negative sign
                    if element in ['-']:
                        offset += 1
                        continue

                    # skip operators - adjust for modifiers ie: '-'
                    if (i-offset) % 2 == 1:
                        continue

                    if element == 0:
                        continue

                    # some hacky process to make different types work.
                    if type(element) == types.BooleanType:
                        if element == True:
                            element = 'True'
                        elif element == False:
                            element = 'False'
                    # HACK: skip parser.parse
                    if not isinstance(element, basestring):
                        continue

                    if element.startswith("parser.parse(") or element.startswith("relativedelta("):
                        continue

                    elements[i] = '"""%s"""' % element

            #expression = ' '.join([str(x) for x in elements])
            parts = []
            for element in elements:
                if not isinstance(element, basestring):
                    element = str(element)
                parts.append(element)
            expression = ' '.join(parts)
           
            if expression == '':
                return ''

            try:
                result = eval(expression)

                # convert result to  seconds if it is a timedelta
                if isinstance(result, datetime.timedelta):
                    result = result.seconds

            except ZeroDivisionError:
                result = None
            except TypeError:
                result = None

            except Exception, e:
                raise SyntaxError("Could not evaluate [%s] in expression [%s] due to error [%s]" % ( expression, my.expression, str(e) ) )

            # NOTE: not sure if this is correct.  If there is only one
            # element, return it as a single value
            if num_elements == 1:
                #results = [result]
                results = result
            else:
                results.append(result)


        return results


    # not used!!!
    def evaluate_stack2(my, stack):
        op = stack[1]
        left = stack[0]
        right = stack[2]

        if type(left) != types.ListType:
            value = left
            left = []
            for i in range(0, len(right)):
                left.append(value)

        if type(right) != types.ListType:
            value = right
            right = []
            for i in range(0, len(left)):
                right.append(value)



        if op == '+':
            result = [l+r for l,r in zip(left, right)]
        elif op == '-':
            result = [l-r for l,r in zip(left, right)]
        elif op == '*':
            result = [l*r for l,r in zip(left, right)]
        elif op == '/':
            result = [float(l)/float(r) for l,r in zip(left, right)]
        elif op in ['>','>=','==','=','<','<=','!=']:
            if op == '=':
                op = '=='
            result = [eval("l %s r" % op) for l, r in zip(left, right)]
        else:
            raise ParserException("Syntax Error: Operator [%s] not recognized" % op)
            #result = "".join(my.stack)

        return result





class MethodMode(ExpressionParser):

    def __init__(my):
        my.method_name = []
        my.result = None
        my.brackets = 0

    def parse(my, token):

        if token == '}':
            return

        elif token == '(':
            method_name = ''.join(my.method_name)

            my.brackets += 1
            mode = ArgListMode()
            my.dive( mode )

            # get the args
            args = mode.get_result()

            # call the method
            try:
                my.result = my.execute_method(method_name, args)
            except SyntaxError, e:
                raise
            except Exception, e:
                raise
                #raise SyntaxError( "Error when calculating method [%s(%s)]: %s" % (method_name, args, str(e)))

            return "exit"

        elif token == ')':
            my.brackets -= 1
            if my.brackets == 0:
                return "exit"
            else:
                my.method_name.append(token)


        elif token == ' ':
            raise SyntaxError('Syntax Error: found extra space in [%s]' % my.expression)


        else:
            my.method_name.append(token)


 

   
        



    def execute_method(my, method, args):
        results = []
        method = method.upper()

        if method in ['GET', 'GETALL']:
            format = None
            if len(args) == 1:
                parts = my._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
            elif len(args) == 2:
                parts = my._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
                format = args[1]
            else:
                raise SyntaxError("Method @GET can only have one or two arguments, found [%s] in expression [%s]" % (len(args), my.expression))

            if not search_types and column:
                raise SyntaxError("Method [%s] requires a column in search_type [%s] in expression [%s]" % (method, args[0], my.expression))

            if not search_types:
                raise SyntaxError("Improper arguments in method [%s] definition in expression [%s]" % (method, my.expression))

            unique = method == 'GET'
            sobjects = my.get_sobjects(search_types, unique=unique)


            return_mode = Container.get("Expression::return_mode")
            if return_mode == 'dict':
                sobjects = my.get_flat_cache()
            
            results = my.get(sobjects, column)
            if format and results:
                results = my.format_results(results, format)
                
        elif method == 'SOBJECT':
            if not len(args):
                results = my.sobjects
            else:
                first_arg = args[0]
                search_types = my._split_arg(first_arg)
                results = my.get_sobjects(search_types)

            return_mode = Container.get("Expression::return_mode")
            if return_mode == 'dict':
                results = my.get_flat_cache()

        elif method == 'SEARCH':
            if not len(args):
                # may raise an error
                pass
            else:
                first_arg = args[0]
                search_types = my._split_arg(first_arg)
                results = my.get_search(search_types)

        elif method == 'COUNT':
            if len(args) == 0:
                results = my.count(my.sobjects)
            elif len(args) == 1 or len(args) == 2:
                # matching @GET(....
                p = re.compile("^@\w+\((\w+\/\w+)?")
                #p = re.compile("^(\w+\/\w+\[?.*?\]?)(\.[\/\w+]*)?")
                m = p.match(args[0])
                if m:
                    mode = my.get_mode(args[0])
                    sobjects = my.dive(mode, expression= args[0])
                  
                else:
                    parts = my._split_arg(args[0])
                    search_types = parts
                    sobjects = my.get_sobjects(search_types, is_count=True)

                return_mode = Container.get("Expression::return_mode")
                if return_mode == 'dict':
                    sobjects = my.get_flat_cache()

                # it is possible that get_sobjects just returns a number
                if type(sobjects) == types.IntType:
                    results = sobjects
                else:
                    results = my.count(sobjects)

            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))

        elif method == 'PYTHON':
            if len(args) :
                from tactic.command import PythonCmd
                first_arg = args[0]
                if my.sobjects:
                    sobject = my.sobjects[0]
                    cmd = PythonCmd(script_path=first_arg, sobject=sobject)
                    results = cmd.execute()


        elif method == 'SUM':
            if len(args) == 1 or len(args) == 2:
                arg = args[0]

                # prod/asset.sthpw/task.completion
                p = re.compile("^(\w+\/\w+\[?.*?\]?)?(\.[\/\w+]*)?\.(\w+)")
                m = p.match(arg)

                if not m:
                    # evaluate expression
                    mode = ExpressionMode()
                    arg_results = my.dive(mode, expression=arg)
                    if type(arg_results) == types.ListType:
                        results = 0
                        for arg_result in arg_results:
                            if arg_result:
                                results += arg_result

                    #elif type(arg_results) == types.DictType:
                    #    sobjects = my.get_flat_cache()
                    #    results = my.sum(sobjects, column)

                    elif not arg_results:
                        results = 0
                    else:
                        results = arg_results


                else:
                    parts = my._split_arg(args[0])
                    search_types = parts[:-1]
                    column = parts[-1]

                    sobjects = my.get_sobjects(search_types)

                    return_mode = Container.get("Expression::return_mode")
                    if return_mode == 'dict':
                        sobjects = my.get_flat_cache()

                    results = my.sum(sobjects, column)
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))

        elif method == 'VAR':
            name = args[0]
            value = args[1]
            new_value = value


        elif method == 'AVG':
            if len(args) == 1:
                arg = args[0]

                # prod/asset.sthpw/task.completion
                p = re.compile("^(\w+\/\w+)?(\.[\/\w+]*)?\.(\w+)")
                m = p.match(arg)
                if not m:
                    parts = my._split_arg(args[0])
                    search_types = parts[:-1]
                    sobjects = my.get_sobjects(search_types)
                    results = my.avg(sobjects, parts[-1])
                    """
                    # evaluate expression
                    mode = ExpressionMode()
                    arg_results = my.dive(mode, expression=arg)
                    if type(arg_results) == types.ListType:
                        results = 0
                        for arg_result in arg_results:
                            results += arg_result
                    else:
                        results = arg_results
                    """
                else:

                    parts = my._split_arg(args[0])
                    search_types = parts[:-1]
                    column = parts[-1]
                    sobjects = my.get_sobjects(search_types)
                    results = my.avg(sobjects, column)

            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))

            # FIXME: search_types is not declared if m is None. It's fixed above in if not m:
            #sobjects = my.get_sobjects(search_types)
            #results = my.avg(sobjects, column)


        elif method == 'MIN':
            if len(args) == 1:
                parts = my._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))

            sobjects = my.get_sobjects(search_types)
            results = my.fcmp(sobjects, column, op='<')

        elif method == 'MAX':
            if len(args) == 1:
                parts = my._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))

            sobjects = my.get_sobjects(search_types)
            results = my.fcmp(sobjects, column, op='>')

        elif method == 'FLOOR':
            if len(args) == 1:
                arg = args[0]
                mode = my.get_mode(arg)
                arg_results = my.dive(mode, expression=arg)

                # FIXME: should this not always return an array
                results = []
                if type(arg_results) == types.ListType:
                    for arg_result in arg_results:
                        result = math.floor(arg_result)
                        results.append(result)
                else:
                    results = math.floor(arg_results)

            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))


        elif method == 'UNIQUE':
            if len(args) == 1:
                arg = args[0]
                mode = my.get_mode(arg)
                result = my.dive(mode, expression=arg)
                if len(result) == 0:
                    return []
                elif isinstance(result[0], SObject):
                    results = []
                    ids = set()
                    for sobject in result:
                        sobject_id = sobject.get_id()
                        if sobject_id in ids:
                            continue
                        results.append(sobject)
                        ids.add(sobject_id)
                else:
                    results = list(set(result))
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), my.expression))


        elif method == 'UNION':
            results = set()
            for arg in args:
                mode = my.get_mode(arg)
                result = my.dive(mode, expression=arg)
                results = results.union(result)
            results = list(results)

        elif method == 'INTERSECT':
            results = set()
            is_first = True
            final_sks = []
            for arg in args:
                mode = my.get_mode(arg)
                result = my.dive(mode, expression=arg)
                if is_first:
                    results = results.union(result)
                    is_first = False
                else:
                    # intersection with sobjects depends on search keys
                    if '@SOBJECT' in arg:
                        final_sks = [ SearchKey.get_by_sobject(x) for x in results] 
                        results = [ x for x in result if SearchKey.get_by_sobject(x) in final_sks]
                    else:
                        results = results.intersection(result)
            results = list(results)


        elif method == 'IF':
            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), my.expression))

            expression = args[0]
            mode = my.get_mode(expression)
            result = my.dive(mode, expression=expression)
            if type(result) == types.ListType and result:
                result = result[0]
            if result:
                expression = args[1]
                mode = my.get_mode(expression)
                results = my.dive(mode, expression=expression)
            else:
                if len(args) == 3:
                    expression = args[2]
                    mode = my.get_mode(expression)
                    results = my.dive(mode, expression=expression)
                else:
                    results = None

        elif method == 'CASE':
            for i in xrange(0, len(args), 2):
                expression = args[i]
                value_expr = args[i+1]
                mode = my.get_mode(expression)
                result = my.dive(mode, expression=expression)

                # NOTE: single assumption
                # if the returned value is a list, then take the first one
                if type(result) == types.ListType:
                    result = result[0]

                if result:
                    mode = my.get_mode(value_expr)
                    results = my.dive(mode, expression=value_expr)
                    break


        elif method == 'STRING':
            if len(args) >= 2:
                raise SyntaxError("Method @%s must have only 1 argument" % (method))
            result = args[0]
            if not isinstance(result, basestring):
                result = str(result)
            #else:
            #    mode = my.get_mode(result)
            #    result = my.dive(mode, expression=result)
            #    result = str(result)
            results = result


        elif method == 'FOREACH':
            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), my.expression))

            expression = args[0]
            mode = my.get_mode(expression)
            results = my.dive(mode, expression=expression)

            # iterate through each
            format = args[1]
            results = [format % x for x in results]

            # do a join if a 3rd parameter is specified
            if len(args) == 3:
                delimiter = args[2]
                results = delimiter.join(results)
                
                


        elif method == 'JOIN':
            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), my.expression))

            expression = args[0]
            mode = my.get_mode(expression)
            results = my.dive(mode, expression=expression)

            delimiter = args[1]
            results = delimiter.join(results)


        elif method == 'UPDATE':
            # the first argument is sobjects
            expression = args[0]
            if expression == "sobject":
                sobjects = my.sobjects
            else:
                mode = my.get_mode(expression)
                sobjects = my.dive(mode, expression=expression)

            if sobjects:
                column = args[1]
                value = args[2]
                
                # prevent saving '' into the db
                if value == "''":
                    value = ''
                for sobject in sobjects:
                    sobject.set_value(column, value)
                    sobject.commit()

            return sobjects


        elif method in ['LATEST','CURRENT']:
            # get the file paths
            first_arg = args[0]
            expression = "@SOBJECT(%s)" % first_arg
            mode = my.get_mode(expression)
            sobjects = my.dive(mode, expression=expression)

            results = []
            if sobjects:
                context = args[1]
                #file_type = args[2]

                base_dir = Environment.get_asset_dir()
                mode = my.get_mode(expression)

                if method == 'LATEST':
                    expression = '''@SOBJECT(sthpw/snapshot['context','%s']['is_latest','true'].sthpw/file)''' % context
                else:
                    expression = '''@SOBJECT(sthpw/snapshot['context','%s']['is_current','true'].sthpw/file)''' % context
                parser = ExpressionParser()
                files = parser.eval(expression, sobjects)

                for file in files:
                    rel_dir = file.get_value("relative_dir")
                    file_name = file.get_value("file_name")
                    path = "%s/%s/%s" % (base_dir, rel_dir, file_name)
                    results.append(path)

        elif method == 'RELTIME':
            kwargs = {}
            for arg in args:
                name, value = arg.split("=")
                try:
                    kwargs[name] = float(value)
                except:
                    kwargs[name] = value
                    
            results = relativedelta(**kwargs)

        elif method == 'EVAL' or method == '':
            expression = args[0]
            mode = my.get_mode(expression)
            results = my.dive(mode, expression=expression)


        elif method == 'FORMAT':
            expression = args[0]
            mode = my.get_mode(expression)
            result = my.dive(mode, expression=expression)

            args_len = len(args)
            if args_len != 0:
                format_option = None
                if args_len >= 2:
                    format_type = 'format'
                    format = args[1]
                    # support optional arg for timecode for example
                    if args_len > 2:
                        format_option = args[2]
                """
                else: # this part does not seem to be used
                    format_type = args[1]
                    format = args[2]
                """
               
                if format_type == 'format':
                    f = FormatValue()
                    # sometimes result could be a list from @GET
                    if isinstance(result, list):
                        f_result = [f.get_format_value(x, format, format_option) for x in result]
                    else:
                        f_result = [f.get_format_value(result, format, format_option)]
                    results = f_result

                else:
                    raise SyntaxError("Format type [%s] not supported" % format_type)


        elif method == 'COLOR':
            from pyasm.web import Palette
            palette = Palette.get()
            attr = args[0]
            if len(args) > 1:
                offset = args[1]
                offset = int(offset)
            else:
                offset = None

            color = palette.color(attr, offset, default='color')
            results = [color]


        elif method == 'GRADIENT':
            from pyasm.web import Palette
            palette = Palette.get()
            attr = args[0]
            if len(args) > 1:
                offset = args[1]
                offset = eval(offset)
            else:
                offset = None

            if len(args) > 2:
                grd_range = args[2]
                grd_range = eval(grd_range)
            else:
                grd_range = None

            color = palette.gradient(attr, offset, grd_range)
            results = [color]


        elif method == 'PALETTE':
            from pyasm.web import Palette
            if len(args) == 0:
                palette = Palette.get()
            else:
                palette = Palette(palette=args[0])
            colors = palette.get_colors()
            results = colors

        else:
            raise SyntaxError("Method [%s] not support found in expression[%s]" % (method, my.expression))


        return results


    def format_results(my, results, format):

        if isinstance(results, dict):
            new_results = {}
            for key, values in results.items():
                if values:
                    new_results[key] = my.format_results(values, format)
                else:
                    new_results[key] = values

            return new_results



        format = str(format)
        formated_results = []

        # assume they are of the same type
        result = results[0]

        result_type = None
        if isinstance(result, datetime.datetime):
            result_type = 'datetime'

        if not result_type:
            return results

        # format the results
        for result in results:
            if result_type == 'datetime':
                result = result.strftime(format)
                result = dateutil.parser.parse(result)

            formated_results.append(result)

        return formated_results
            



    def process_search_type(my, search_type):

        filters = []

        # find the first [
        index = search_type.find("[")
        if index == -1:
            return search_type, filters


        base_search_type = search_type[:index]
        filter = search_type[index:]

        # process filters
        cur_filter = None

        #tokens = tokenize(filter, '''[]'",''')

        string_mode = False
        number_mode = False
        method_mode = False
        string = []
        string_delimiter = None
        method_delimiter = None
        brackets = 0

        for i, token in enumerate(filter):
            if number_mode == True :
                if token not in '.0123456789':
                    string_str = ''.join(string)
                    #FIXME: limited to just integer number
                    number = int(string_str)
                    cur_filter.append(number)
                    number_mode = False
                else:
                    string.append(token)
                    continue

           
            # the order in the if statement matters here 
            if token == string_delimiter:
                string_str = "".join(string)
               
                # TODO: parsing not strong enough for this right now
                #if string_str.startswith("@"):
                #    mode = ExpressionMode()
                #    string_str = my.dive(mode, expression=string_str)
           
                string = []
                cur_filter.append(string_str)
                string_mode = False
                string_delimiter = None
                
            elif token == method_delimiter:
                string.append(token)
                string_str = "".join(string)
                
                mode = my.get_mode(string_str)
                string_str = my.dive(mode, expression=string_str)
                
                # just pass the only item in the list of a @GET, which is the most common case
                if isinstance(string_str, list) and len(string_str) == 1:
                    string_str = string_str[0]

                string = []
                cur_filter.append(string_str)
                method_mode = False
                method_delimiter = None
            
           
            elif string_mode:
                string.append(token)
            elif method_mode:
                string.append(token)
            elif token in ["'", '"']:
                if not string_mode:
                    string_delimiter = token
                    string_mode = True
            elif token == '[':
                cur_filter = []
            elif token == ']':
                filters.append(cur_filter)
            elif token in [' ',',']:
                pass
            elif token in '.0123456789':
                if not number_mode:
                    string = [token]
                    number_mode = True
        
            elif token == "@":
                if not method_mode:
                    string = [token]
                    method_delimiter = ")"
                    method_mode = True

            else:
                
                raise SyntaxError("Could not process token [%s] search type [%s] in expression [%s]" % (token, search_type, my.expression))


        return base_search_type, filters

        

    def get_search(my, related_types, is_count=False):
        search =  my.get_sobjects(related_types, is_count=is_count, is_search=True)
        if not isinstance(search, Search):
            raise ParserException('Make sure the @SEARCH expression ends with a valid sType') 
        return search

    def group_filters(my, filters):
        context_filters = []
        reg_filters = []
        for item in filters:
            if '@CONTEXT' in item:
               item[0] = item[0].replace('@CONTEXT','context')
               context_filters.append(item)
            else:
               reg_filters.append(item)

        return reg_filters, context_filters

    def get_sobjects(my, related_types, is_count=False, is_search=False, unique=True):
        # FIXME: not sure why id() does not work. It seems to return the same
        # results all the time.  It is desireable to use id because the
        # keys would be much smaller
        #key = "%s|%s" % (related_types, id(my.sobjects))
        key = "%s|%s" % (related_types, str(my.sobjects))
        if len(key) > 10240:
            print "WARNING: huge key in get_sobjects in expression"
        results = Container.get_dict(my.EXPRESSION_KEY, key)
        if results != None:
            return results


        related_types_filters = {}
        related_types_paths = {}

        # process the search type
        p = re.compile('^(\w+):')
        for i, related_type in enumerate(related_types):
            m = p.search(related_type)
            if m:
                path = m.groups()[0]
                related_type = related_type[(len(path)+1):]
                #print "path: ", path
                #print "related_type: ", related_type
            else:
                path = None

            related_type, filters = my.process_search_type(related_type)

            related_types[i] = related_type
            related_types_filters[related_type] = filters
            related_types_paths[related_type] = path

        # handle some absolute sobjects
        if len(related_types) == 1:
            # support some shorthand here?
            if related_type == 'login':
                related_sobjects = [Environment.get_login()]
                return related_sobjects
            elif related_type == 'state':
                sobject = SearchType.create("sthpw/virtual")
                for name, value in my.state.items():
                    if value != None:
                        sobject.set_value(name, value)
                return [sobject]

            elif related_type == 'parent':
                related_sobjects = []
                for sobject in my.sobjects:
                    parent = sobject.get_parent()
                    related_sobjects.append(parent)
                    my.cache_sobjects(sobject.get_search_key(), [parent])
                return related_sobjects

            elif related_type == 'connect':
                related_sobjects = []
                from pyasm.biz import SObjectConnection
                filters = related_types_filters.get(related_type)
                reg_filters, context_filters = my.group_filters(filters)

                connections = SObjectConnection.get_connections(my.sobjects, context_filters=context_filters)
                related_sobjects = SObjectConnection.get_sobjects(connections, filters=reg_filters)
                return related_sobjects


            elif related_type == 'date':
                sobject = SearchType.create("sthpw/virtual")
                today = datetime.datetime.today()
                sobject.set_value("today", today)
                now = datetime.datetime.now()
                sobject.set_value("now", now)
                related_sobjects = [sobject]
                return related_sobjects

            elif related_type == 'palette':
                from pyasm.web import Palette
                palette = Palette.get()
                sobject = SearchType.create("sthpw/virtual")
                keys = palette.get_keys()
                for key in keys:
                    sobject.set_value(key, palette.color(key))
                related_sobjects = [sobject]
                return related_sobjects
 
            elif related_type == 'search_type':
                related_sobjects = []
                for sobject in my.sobjects:
                    search_type = sobject.get_search_type_obj()
                    related_sobjects.append(search_type)
                    return related_sobjects

 
            elif related_type == 'project':
                related_sobjects = []
                project = Project.get()
                related_sobjects.append(project)
                return related_sobjects




        # if no sobjects have been specified to start with, then use
        # the first search type as a starting point
        if not my.sobjects:
            related_type = related_types[0]

            # support some shorthand here?
            if related_type == 'login':
                related_sobjects = [Environment.get_login()]
            elif related_type == 'date':
                sobject = SearchType.create("sthpw/virtual")
                today = datetime.datetime.today()
                sobject.set_value("today", today)
                now = datetime.datetime.now()
                sobject.set_value("now", now)
                related_sobjects = [sobject]
            elif related_type == 'project':
                project = Project.get()
                related_sobjects = [project]

            elif related_type.find("/") == -1:
                sobject = my.get_env_sobject(related_type)
                if sobject:
                    related_sobjects = [sobject]
                else:
                    related_sobjects = []


            elif not related_type:
                related_sobjects = []
            else:
                related_sobjects = []
                # do the full search
                search = Search(related_type)

                if my.show_retired:
                    search.set_show_retired(True)

                filters = related_types_filters.get(related_type)
                search.add_op_filters(filters)

                # add any extra filters
                extra_filters = Container.get("Expression::extra_filters")
                if extra_filters:
                    extra_filter = extra_filters.get(related_type)
                    if extra_filter:
                        search.add_op_filters(extra_filter)

                # on the very specific time when there are no relative sobjects
                # to start off with we only have one level of related types,
                # then just use the count method
                if is_count and len(related_types) == 1:
                    return search.get_count()

                if is_search:
                    if len(related_types) == 1:
                        return search
                    else:
                        related_search = search
                else:
                    related_sobjects = search.get_sobjects()

            if not related_sobjects and not is_search:
                return []

            # remove the one just found
            related_types = related_types[1:]
        else:
            # start of with the current sobject list
            related_sobjects = my.sobjects


        # go through each of the related types
        cur_search_type = ''
        if related_sobjects:
            sample_sobject = related_sobjects[0]
            # this is a fix if the list is [None] for some reason
            # this condition needs to be considered again for is_search=True
            if not sample_sobject:
                return []
            cur_search_type = sample_sobject.get_base_search_type()
        elif is_search:
            cur_search_type = related_search.get_base_search_type()
        list = []
        for i, related_type in enumerate(related_types):
            if related_type == '':
                break

            #mode = 'original'
            mode = 'fast'

            # support some shorthand here?
            if related_type == 'login':
                related_sobjects = [Environment.get_login()]

            elif related_type == 'parent':
                list = []
                for related_sobject in related_sobjects:
                    parent = related_sobject.get_parent()
                    list.append(parent)
                    my.cache_sobjects(related_sobject.get_search_key(), [parent])


            elif related_type == 'connect':
                list = []
                from pyasm.biz import SObjectConnection

                filters = related_types_filters.get(related_type)
                reg_filters, context_filters = my.group_filters(filters)

                connections = SObjectConnection.get_connections(related_sobjects, context_filters=context_filters)
                list = SObjectConnection.get_sobjects(connections, filters=reg_filters)
                # TODO: caching is not implemented on connect
                #my.cache_sobjects(related_sobject.get_search_key(), sobjects)

            elif related_type.find("/") == -1:
                list = []
                sobject = my.get_env_sobject(related_type)
                if sobject:
                    list.append(sobject)

            elif i == 0 and related_type == cur_search_type:
                # no need to search for itself again
                if is_search:
                    related_search = Search(related_type)
                    if my.show_retired:
                        related_search.set_show_retired(True) 
                    if related_sobjects:
                        related_search.add_relationship_filters(related_sobjects)
                break

            #elif mode == 'fast':
            else:
                filters = related_types_filters.get(related_type)
                path = related_types_paths.get(related_type)
                
                if is_search:
                    # do the full search
                    sub_search = Search(related_type)

                    if my.show_retired:
                        sub_search.set_show_retired(True)

                    #FIXME: filters for the very last related_type is not found
                    filters = related_types_filters.get(related_type)
                    sub_search.add_op_filters(filters)

                    if related_sobjects:
                        sub_search.add_relationship_filters(related_sobjects)
                    else:
                        # or from an sobject-less/plain search
                        sub_search.add_relationship_search_filter(related_search)
                        
                    related_search = sub_search
                    
                else:
                    tmp_dict = Search.get_related_by_sobjects(related_sobjects, related_type, filters=filters, path=path, show_retired=my.show_retired)

                    # collapse the list and make it unique
                    tmp_list = []
                    for key, items in tmp_dict.items():
                        tmp_list.extend(items)
                        my.cache_sobjects(key, items)


                    list = []
                    ids = set()
                    for sobject in tmp_list:
                        sobject_id = sobject.get_id()
                        if unique and sobject_id in ids:
                            continue
                        list.append(sobject)
                        ids.add(sobject_id)

            """
            else:
                list = []
                for related_sobject in related_sobjects:
                    
                    if not related_sobject:
                        continue
                    # maybe an env obj
                    if related_type.find("/") == -1:
                        tmp_sobj = my.get_env_sobject(related_type)
                        if tmp_sobj:
                            tmp = [tmp_sobj]
                        else:
                            tmp = []
                    else:
                        filters = related_types_filters.get(related_type)
                    	path = related_types_paths.get(related_type)
                        tmp = related_sobject.get_related_sobjects(related_type, filters, path=path, show_retired=my.show_retired)
                    my.cache_sobjects(related_sobject, tmp)
                    if not tmp:
                        continue

                    list.extend(tmp)
            """

            related_sobjects = list
            if not related_sobjects:
                related_sobjects = []
                if not is_search:
                    break



        if is_search:
            return related_search
        #Container.put(key, related_sobjects)
        Container.put_dict(my.EXPRESSION_KEY, key, related_sobjects)

        return related_sobjects





    def get(my, sobjects, column):

        if isinstance(sobjects, dict):
            results = {}
            for key, values in sobjects.items():
                results[key] = my.get(values, column)
            return results

        if not sobjects:
            return []

        values = []
        for sobject in sobjects:
            # sobject could have been deleted
            if not sobject:
                continue

            if column == '__search_key__':
                value = sobject.get_search_key()
            elif column == '__search_type__':
                value = sobject.get_search_type()
            elif column == '__base_search_type__':
                value = sobject.get_base_search_type()
            elif column == '__project__':
                value = sobject.get_project_code()
            else:
                value = sobject.get_value(column)

            col_type = SearchType.get_column_type(sobject.get_search_type(), column)
            #col_type = sobject.get_search_type_obj().get_column_type(column)
            if value and col_type in ['timestamp','datetime2']:
                from dateutil import parser
                if not isinstance(value, datetime.datetime):
                    value = parser.parse(value)
           
            values.append(value)

            my.cache_sobjects(sobject, value)

        return values


    def sum(my, sobjects, column):
        if isinstance(sobjects, dict):
            results = {}
            for key, values in sobjects.items():
                results[key] = my.sum(values, column)
            return results

        total = 0
        for sobject in sobjects:
            
            value = sobject.get_value(column, no_exception=True)
            if not value:
                continue
            if type(value) in types.StringTypes:
                value = float(value)
            total += value

        return total

    def avg(my, sobjects, column):
        value = my.sum(sobjects, column)
        count = len(sobjects)
        if not count:
            return 0
        avg = float(value) / count
        return avg


    def count(my, sobjects):
        if isinstance(sobjects, dict):
            results = {}
            for key, values in sobjects.items():
                results[key] = my.count(values)
            return results

        if not sobjects:
            return 0
        return len(sobjects)


    def is_zero(my, sobjects, column):
        value = my.sum(sobjects, column)
        return value == 0



    def fcmp(cls, sobjects, column, op='>'):
        if not sobjects:
            return None
        #return max( [x.get_value(column) for x in sobjects] )

        search_type = sobjects[0].get_base_search_type()
        info = SearchType.get_column_info(search_type)
        column_info = info.get(column)
        if not column_info:
            data_type = {'data_type': 'string'}
        else:
            data_type = column_info.get('data_type')

        if data_type == 'timestamp':
            best = None
        else:
            best = None

        for sobject in sobjects:
            value = sobject.get_value(column)
            if data_type == 'timestamp':
                if not value:
                    continue
                value = dateutil.parser.parse(value)
                if not best:
                    best = value
                else:
                    if eval("str(value) %s str(best)" %op):
                        best = value

            else:
                if best == None:
                    best = value
                elif value != '' and eval("value %s best" %op):
                    best = value
        return best
    fcmp = classmethod(fcmp)






class ArgListMode(ExpressionParser):

    def __init__(my):
        my.cur_arg = []
        my.args = []

    def get_result(my):
        return my.args

    def parse(my, token):
        if token in [' ','\n','\t']:
            return

        elif token == ')':
            return "exit"

        else:
            mode = ArgMode()
            arg = my.dive(mode, reuse_token=True)
            my.args.append(arg)

        if my.index == len(my.expression):
            raise SyntaxError('No closing bracket around arguments for [%s]' % my.expression)
        # if the next character is ), then exit
        try:
            if my.expression[my.index] == ')':
                return 'exit'
        except IndexError:
            raise SyntaxError('Incorrect syntax found for %s' %my.expression)



class ArgMode(ExpressionParser):

    def __init__(my):
        my.result = []

        #my.in_filter = False
        my.brackets = 0

        my.literal_mode = False
        my.literal = []

        my.is_only_literal = True


    def parse(my, token):
        # handle literals
        if token == "'":
            if my.literal_mode:
                my.literal_mode = False
                if not my.literal:
                    my.result.append("''")
                else:
                    if my.is_only_literal:
                        literal = "".join(my.literal)
                    else:
                        literal = "'%s'" % "".join(my.literal)
                    my.result.append(literal)
                my.literal = []
            else:
                my.literal_mode = True

        elif my.literal_mode:
            my.literal.append(token)

        # ignore spaces
        elif token == ' ':
            return

        elif token in [',', ')']:
            if token == ')':
                my.brackets -= 1

                if my.brackets < 0:
                    my.result = "".join(my.result)
                    my.result = my.result.strip()
                    return "exit"
                else:
                    my.result.append(token)
                    
            else: # , found. Ensure it is a arg separator using bracket counts
                if my.brackets < 1:
                    my.result = "".join(my.result)
                    my.result = my.result.strip()
                    return "exit"
                else:
                    my.result.append(token)

        # start a filter
        elif token == '[':
            mode = FilterMode()
            tmp = my.result     # div makes use of my.result
            filter = my.dive(mode, reuse_token=True)
            my.result = tmp
            my.result.append(filter)

        elif token == '(':
            my.brackets += 1
            my.result.append(token)


        #elif token == ' ':
        #    #raise SyntaxError("Space found in argument in expression [%s]" % my.expression)

        else:
            my.result.append(token)
            my.is_only_literal = False


class FilterMode(ExpressionParser):

    def __init__(my):
        my.result = []
        my.brackets = 0

    def get_result(my):
        return "".join( my.result)

    def parse(my, token):

        # handle literals
        if token == ']':
            my.result.append(token)
            if my.brackets == 0:
                return 'exit'

        else:
            if token == '(':
                my.brackets += 1
            elif token == ')':
                my.brackets -= 1
            my.result.append(token)

class SqrBracketMode(ExpressionParser):
    '''this replaces the old regex of lazy findall of [..], which can't handle recursion 
        p = re.compile("(\[.*?\])")
        filters = p.findall(arg)
        
        The input string is a greedy regex of [..]'''

    def __init__(my):
        my.result = []
        my.brackets = 0
        my.delimiter = None
        my.stack = []

    def get_result(my):
        if my.brackets > 0:
            raise SyntaxError('Incorrect syntax: square brackets for the filter [] are not balanced for "%s"'%my.expression)
        return my.result

    def parse(my, token):
        if token == '[':
            my.brackets += 1
            my.delimiter = ']'
            my.stack.append(token)

        elif token == my.delimiter:
            my.brackets -= 1
            my.stack.append(token)
            if my.brackets == 0:
                string_str = "".join(my.stack)
                my.result.append(string_str)
                my.stack = []
        else:
            if my.brackets > 0:
                my.stack.append(token)

def tokenize(expr, special_chars):

        is_args = False
        is_string = False

        token_list = []
        start = 0
        for i, char in enumerate(expr):
          
            if char not in special_chars:
                continue


            if i != start:
                token = expr[start:i]

                # if not in string mode, remove whitespace
                if not is_string:
                    token = token.strip()
                    # convert to a number
                    try:
                        if token.find(".") != -1:
                            token = float(token)
                        else:
                            token = int(token)
                    except ValueError:
                        pass

                if token != '':
                    token_list.append(token)

            # add the special character as a token
            token_list.append(char)
            start = i+1

        if start != i + 1:
            token = expr[start:i+1]
            # if not in string mode, remove whitespace
            if not is_string:
                token = token.strip()
                # convert to a number
                try:
                    if token.find(".") != -1:
                        token = float(token)
                    else:
                        token = int(token)
                except ValueError:
                    pass

            if token != '':
                token_list.append(token)

        return token_list




