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

from pyasm.common import TacticException, Environment, Container, FormatValue, Config
from pyasm.search import Search, SObject, SearchKey, SearchType
from pyasm.security import Site

from project import Project



def get_expression_key():
    site = Site.get_site()
    if site:
        expression_key = "Expression:keys:%s" % site
    else:
        expression_key = "Expression:keys"
    return expression_key


class ParserException(TacticException):
    pass





class ExpressionParser(object):
        
    def __init__(self):
        self.init()


    def init(self):
        self.env_sobjects = {}
        self.expression = None
        # for building cache key
        self.related_types = []
        self.index = -1
        self.sobjects = []
        self.search = None
        self.result = None
        self.vars = {}
        self.show_retired = False
        self.state = {}
        self.return_mode = 'array'
        self.is_single = False
        self.use_cache = True



    def eval(self, expression, sobjects=None, mode=None, single=False, list=False, dictionary=False, vars={}, env_sobjects={}, show_retired=False, state={}, extra_filters={}, search=None, use_cache=None ):

        if not expression:
            return ''

        self.init()


        if use_cache is not None:
            self.use_cache = use_cache


        if dictionary == True:
            return_mode = 'dict'
        elif single == True:
            return_mode = 'single'
        else:
            return_mode = 'array'
        Container.put("Expression::return_mode", return_mode)

        if sobjects == None:
            #self.is_single = False
            sobjects = []
     
        elif type(sobjects) != types.ListType:
            #self.is_single = True
            sobjects = [sobjects]
      

        self.show_retired = show_retired


        self.expression = expression
        self.sobjects = sobjects
        if search:
            self.search = search.copy()
        self.env_sobjects = env_sobjects
        self.state = state

        self.vars = {}
        self.vars.update( self.get_date_vars() )

        # add the environment
        login = Environment.get_login()
        if login:
            self.vars['LOGIN'] = login.get_value("login")
            self.vars['LOGIN_ID'] = login.get_id()

            # add users in login group
            from pyasm.security import LoginGroup
            login_codes = LoginGroup.get_login_codes_in_group()
            login_codes = "|".join(login_codes)
            self.vars['LOGINS_IN_GROUP'] = login_codes


        project = Project.get_project_code()
        self.vars['PROJECT'] = project

        try:
            from pyasm.web import WebContainer
            web = WebContainer.get_web()
        except Exception, e:
            web = None
        if web:
            url = web.get_base_url()
            self.vars['BASE_URL'] = url.to_string()

            url = web.get_project_url()
            self.vars['PROJECT_URL'] = url.to_string()
        else:
            base_url = Config.get_value("services", "mail_base_url")
            if base_url:
                self.vars['BASE_URL'] = base_url
                self.vars['PROJECT_URL'] = "%s/tactic/%s" % (base_url, project)


        if vars:
            self.vars.update(vars)
 
        # replace all of the variables: Note that this replaces even in the
        # string area ... not sure if this is what we want
        keys = self.vars.keys()
        keys.sort()
        keys.reverse()
        #for name, value in self.vars.items():
        for name in keys:

            value = self.vars.get(name)
            new_value = "'%s'" % unicode(value).encode('utf-8', 'ignore')
            # HACK: replace with the single quotes first.  Not elegant, but
            # it works for now until we have real variables
            self.expression = re.sub("'\$%s'"%name, new_value, self.expression)
            self.expression = re.sub("\$%s"%name, new_value, self.expression)


        if not mode:
            # start in string mode
            string_idx = self.expression.find("{")
            expr_idx = self.expression.find("@")

            if string_idx == -1:
                new_parser = ExpressionMode()
            elif expr_idx == -1:
                new_parser = StringMode()
            elif expr_idx < string_idx:
                new_parser = ExpressionMode()
            else:
                new_parser = StringMode()
                self.is_single = False
    
        elif mode == 'expression':
            # start in string mode
            new_parser = ExpressionMode()
            self.is_single = True
        elif mode == 'string':
            new_parser = StringMode()
            self.is_single = True

            # if the are no {}, then just exit ... no use parsing
            string_idx = self.expression.find("{")
            if string_idx == -1:
                return self.expression


        if single:
            self.is_single = True
        if list:
            self.is_single = False

        
        Container.put("Expression::extra_filters", extra_filters)

        self.dive(new_parser)
        Container.put("Expression::extra_filters", None)
        if self.is_single and type(self.result) == types.ListType: 
            if self.result:
                return self.result[0]
            else:
                # for single, should return None
                return None
        elif list and type(self.result) != types.ListType:
            return [self.result]
        else:
            return self.result



    def get_date_vars(self):
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




    def get_result(self):
        return self.result

    def get_env_sobject(self, key):
        return self.env_sobjects.get(key)


    def get_cache_sobjects(self):
        '''method to store all the sobjects as they being searched through
        the hierarchy'''
        key = "%s|%s|%s" % (self.expression, self.related_types, str(self.sobjects))
        cache = Container.get_full_dict('Expression:%s' % key)
        return cache


    def cache_sobjects(self, sobject, related_sobjects):
        '''method to store all the sobjects as they being searched through
        the hierarchy'''
        if not related_sobjects:
            related_sobjects = []

        key = "%s|%s|%s" % (self.expression, self.related_types, str(self.sobjects))
        cache = Container.get_full_dict('Expression:%s' % key)
        cache[sobject] = related_sobjects


        if isinstance(sobject, basestring):
            search_key = sobject
        else:
            search_key = SearchKey.get_by_sobject(sobject)

        cache[search_key] = related_sobjects



    def get_flat_cache(self, filter_leaf=False):
        cache_sobjects = self.get_cache_sobjects()
        flat_cache_sobjects = {}
        level = 0

        for sobject in self.sobjects:
            leaf_sobjects = []
            search_key = sobject.get_search_key()
            self._flatten_cache(sobject, level, cache_sobjects, leaf_sobjects)
            # FIXME
            # _flatten_cache return a bizarre case where the leaf = [sobject]
            # to determine
            # This is run in the gantt widget
            if filter_leaf and leaf_sobjects    \
                    and leaf_sobjects[0].get_search_key() == search_key:
                continue

            flat_cache_sobjects[search_key] = leaf_sobjects

        return flat_cache_sobjects



    def _flatten_cache(self, top_sobject, level, cache_sobjects, leaf_sobjects):
        search_key = top_sobject.get_search_key()
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
          
            self._flatten_cache(sobject, level, cache_sobjects, leaf_sobjects)

    #
    # These methods allow for querying the leaf values for each sobject on
    # an expression that started with multiple sobjects.
    #
    def get_result_by_sobject(self, sobject):
        results = self.get_results_by_sobject(sobject)
        if results:
            return results[0]
        else:
            return None

    def get_results_by_sobject(self, sobject):
        key = sobject.get_search_key()
        relationships = self.get_cache_sobjects()

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

    def get_results_by_sobject_dict(self):
        results = {}
        for sobject in self.sobjects:
            key = sobject.get_search_key()
            sobj_results = self.get_results_by_sobject(sobject)
            results[key] = sobj_results
        return results

    def get_result_by_sobject_dict(self):
        '''get a single result for each sobject organized by a dictionary'''
        results = {}
        for sobject in self.sobjects:
            key = sobject.get_search_key()
            sobj_results = self.get_result_by_sobject(sobject)
            results[key] = sobj_results
        return results





    def _find_sqr_brackets(self, filter):
        '''get the [ ] in the string and pass it to SqrBracketMode''' 
        # use greedy search
        p = re.compile("(\[.*\])")
        m = p.findall(filter)
        if m:
            filter = m[0]
            mode = SqrBracketMode()
            rtn = self.dive(mode, expression=filter)
        else:
            rtn = []

        return rtn


    def _split_arg(self, arg):
        parts = []
        

        #p = re.compile("(\[.*?\])")
        #filters = p.findall(arg)
        filters = self._find_sqr_brackets(arg)
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
        
    def get_plain_related_types(self, expression):
        '''get plain related_types without the filters in an expression. This is similar to _split_arg()'''
        # this should work in a nested expression as well with @UNIQUE 
        m = re.match(r'.*@SOBJECT\((.*?)\)*$',expression)
        if not m:
            return []
        arg = m.groups()[0]
        parser = ExpressionParser()

        parts = []

        filters = self._find_sqr_brackets(arg)
        if not filters:
            return arg.split(".")

        tmp_arg = arg
        for i, filter in enumerate(filters):
            tmp_arg = tmp_arg.replace(filter, '')

        parts = tmp_arg.split(".")
        for j, part in enumerate(parts):
            parts[j] = part

        return parts

    def do_parse(self):
        
        while(1):
            char = self.expression[self.index]
            value = self.parse(char)
            if value == 'continue':
                self.result = None
                self.stack = []

            if value == 'exit':
                return

            self.index += 1

            if self.index >= len(self.expression):
                break



    def dive(self, new_parser, reuse_token=False, expression=None):

        # handle the case where expression is empty ... no reason to go further
        if expression == '':
            return ''

        if expression:
            new_parser.expression = expression
            new_parser.index = 0
        else:
            new_parser.expression = self.expression
            if reuse_token:
                new_parser.index = self.index
            else:
                new_parser.index = self.index + 1



        new_parser.sobjects = self.sobjects
        new_parser.search = self.search
        new_parser.env_sobjects = self.env_sobjects
        new_parser.state = self.state
        new_parser.vars = self.vars
        new_parser.show_retired = self.show_retired
        new_parser.use_cache = self.use_cache
        new_parser.related_types = self.related_types

        new_parser.do_parse()

        # get the result from the parse
        self.result = new_parser.get_result()

        # get the related_types going back up after a dive
        # This is for caching purposes
        self.related_types = new_parser.related_types

        if not expression:
            self.index = new_parser.index

        return self.result


    def get_mode(self, expression):
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
        Container.clear_dict(get_expression_key())
    clear_cache = staticmethod(clear_cache)


class StringMode(ExpressionParser):

    def __init__(self):
        self.stack = []

        self.arg = []
        
        super(StringMode, self).__init__()

    def get_result(self):
        try:
            result =  "".join( self.stack )
        except UnicodeDecodeError:
            self.stack = [ x.decode('utf-8') if type(x)==types.StringType else x for x in self.stack]
            result =  "".join( self.stack )
        return result


    def parse(self, token):
        # go in to expression mode
        if token == '{':
            mode = ExpressionMode()
            result = self.dive(mode)
            # FIXME: for now, take the first element
            if type(result) == types.ListType:
                if not result:
                    result = ''
                else:
                    result = result[0]
                    if isinstance(result, SObject):
                        result = result.get_display_value()



            if self.expression[self.index] != '}':

                mode = StringFormatMode()
                format = self.dive(mode)
                format = format.strip()
                if isinstance(result, datetime.datetime):
                    try:
                        result = result.strftime(str(format))
                    except Exception, e:
                        raise SyntaxError("Error when using format [%s] on datetime result [%s] in expression [%s]: [%s]" % (format, result, self.expression, str(e)))

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
                                #raise SyntaxError("Error when using format [%s] on result [%s] in expression [%s]: [%s]" % (format, result, self.expression, str(e)))
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
            self.stack.append(result)

        elif token == '}':
            return 'exit'

        else:
            self.stack.append(token)



       

 

class StringFormatMode(ExpressionParser):

    def __init__(self):
        self.format = []

        self.start_char = False
        self.brackets = 0
        super(StringFormatMode, self).__init__()

    def get_result(self):
        return "".join(self.format)

    def parse(self, token):

        if not self.start_char and token == '}':
            return "exit"

        elif token == self.start_char: 
            # using matching parentheses to ensure | is not part of an expression
            if self.brackets == 0:
                # skip pass the } after |
                char = self.expression[self.index]
                while char != '}':
                    self.index += 1
                    char = self.expression[self.index]
                return "exit"
            else:
                self.format.append(token)
             

        #elif token == ' ':
        #    pass

        elif token == '|':
            self.start_char = token

        else:
            if token == '(':
                self.brackets += 1
            elif token == ')':
                self.brackets -= 1
            self.format.append(token)



class ExpressionMode(ExpressionParser):

    def __init__(self):
        self.stack = []
        self.literal = []
        self.literal_mode = False

        super(ExpressionMode, self).__init__()


    def get_result(self):
        self.handle_literal()

        if len(self.stack) == 1:
            # FIXME: not sure why this is double array?
            return self.stack[0]

        # go through the stack and calculate
        value = self.evaluate_stack(self.stack)
        self.result = value

        return self.result



    EMPTY_LITERAL = '!!!_^^^_!!!'

    def parse(self, token):
        # make special provision for literal (string) mode
        if self.literal_mode:
            if token == "'":
                self.literal_mode = False
                if not self.literal:
                    # NEED A SPECIAL STRING TO GET BY LITERAL CHECKS
                    self.literal = [self.EMPTY_LITERAL]
            else:
                self.literal.append(token)
            return

        # if the next character is }, then exit
        if token == '}':
            return 'exit'
       
        elif token == '@':
            mode = MethodMode()
            self.result = self.dive(mode)
            self.stack.append(self.result)


        elif token == ',':
            return 'exit'

        elif token == '(':
            mode = ExpressionMode()
            value = self.dive(mode)
            self.stack.append(value)


        elif token == ')':
            return 'exit'


        elif token == '-':
            try:
                # handle negative number
                int(self.expression[self.index+1])
                self.literal.append(token)
            except ValueError:
                self.handle_literal()
                self.stack.append(token)

        elif token in ['+', '-', '/', '*', '~']:

            self.handle_literal()

            self.stack.append(token)

        #elif op in ['>','>=','==','=','<','<=']:
        elif token in ['>','=','<','!']:
            self.handle_literal()

            if self.expression[self.index+1] in ['=','!']:
                token += '='
                self.index += 1
            elif self.expression[self.index+1] in ['~']:
                token += '~'
                self.index += 1

            self.stack.append(token)

        elif token in ["'"]:
            self.literal_mode = True
            return

        elif token in [' ', '\t', '\n']:
            self.handle_literal()

        elif token in [';']:
            return "continue"

        else:
            # append to the literal if this is any other token
            self.literal.append(token)

            #raise SyntaxError("Unrecognized token [%s] in expression mode in line [%s]" % (token, self.expression))


    def handle_literal(self):
        if not self.literal:
            return

        literal = "".join(self.literal)

        # parse the shorthand
        literal = self.handle_shorthand(literal)
        if literal == '':
            return 0
        try:
            literal = float(literal)
        except ValueError:
            #raise SyntaxError("Expression contains non-number element [%s] in [%s]" % (literal, self.expression))
            pass

        if literal == self.EMPTY_LITERAL:
            literal = ''
        
        self.stack.append(literal)
        self.literal = []



    def handle_shorthand(self, expr):

        self.literal_sobjects = {
            'login': Environment.get_login(),
            #'sobjects': self.sobject,
            #'snapshot': self.snapshot,
            #'file': self.file_object,
        }

        self.literal_vars = {
            'login': Environment.get_user_name(),
            #'version': '003'
        }



        # find sobject.column
        if expr.find(".") != -1:
            type, attr = expr.split(".", 1)

            literal_value = self.literal_sobjects.get(type)
            if literal_value:
                return literal_value.get_value(attr)

        # find single values
        literal_value = self.literal_vars.get(expr)
        if literal_value:
            return literal_value

        return expr
 




    def evaluate_stack(self, stack):
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
                raise SyntaxError("Could not evaluate [%s] in expression [%s] due to error [%s]" % ( expression, self.expression, str(e) ) )

            # NOTE: not sure if this is correct.  If there is only one
            # element, return it as a single value
            if num_elements == 1:
                #results = [result]
                results = result
            else:
                results.append(result)


        return results


    # not used!!!
    def evaluate_stack2(self, stack):
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
            #result = "".join(self.stack)

        return result





class MethodMode(ExpressionParser):

    def __init__(self):
        self.method_name = []
        self.result = None
        self.brackets = 0

    def parse(self, token):

        if token == '}':
            return

        elif token == '(':
            method_name = ''.join(self.method_name)

            self.brackets += 1
            mode = ArgListMode()
            self.dive( mode )

            # get the args
            args = mode.get_result()

            # call the method
            try:
                self.result = self.execute_method(method_name, args)
            except SyntaxError, e:
                raise
            except Exception, e:
                raise
                #raise SyntaxError( "Error when calculating method [%s(%s)]: %s" % (method_name, args, str(e)))

            return "exit"

        elif token == ')':
            self.brackets -= 1
            if self.brackets == 0:
                return "exit"
            else:
                self.method_name.append(token)


        elif token == ' ':
            raise SyntaxError('Syntax Error: found extra space in [%s]' % self.expression)


        else:
            self.method_name.append(token)


 

   
        



    def execute_method(self, method, args):
        results = []
        method = method.upper()

        if method in ['GET', 'GETALL']:
            format = None
            if len(args) == 1:
                parts = self._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
            elif len(args) == 2:
                parts = self._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
                format = args[1]
            else:
                raise SyntaxError("Method @GET can only have one or two arguments, found [%s] in expression [%s]" % (len(args), self.expression))

            if not search_types and column:
                raise SyntaxError("Method [%s] requires a column in search_type [%s] in expression [%s]" % (method, args[0], self.expression))

            if not search_types:
                raise SyntaxError("Improper arguments in method [%s] definition in expression [%s]" % (method, self.expression))

            unique = method == 'GET'
            sobjects = self.get_sobjects(search_types, unique=unique)
            """
            #TOOO: make this work with @CASE or @IF statements
            sobjects_search = self.get_sobjects(search_types, unique=unique, is_search=True)
            if sobjects_search:
                sobjects = sobjects_search.get_sobjects()
            else:
                sobjects = []
            """

            return_mode = Container.get("Expression::return_mode")
            if return_mode == 'dict':
                sobjects = self.get_flat_cache()
            
            results = self.get(sobjects, column)
            if format and results:
                results = self.format_results(results, format)
                
        elif method == 'SOBJECT':
            if not len(args):
                if self.search:
                    results = self.search.get_sobjects()
                else:
                    results = self.sobjects
            else:
                first_arg = args[0]
                search_types = self._split_arg(first_arg)
                results = self.get_sobjects(search_types)

            return_mode = Container.get("Expression::return_mode")
            if return_mode == 'dict':
                results = self.get_flat_cache()

        elif method == 'SEARCH':
            if not len(args):
                # may raise an error
                pass
            else:
                first_arg = args[0]
                search_types = self._split_arg(first_arg)
                results = self.get_search(search_types)

        elif method == 'COUNT':
            if len(args) == 0:
                results = self.count(self.sobjects)
            elif len(args) == 1 or len(args) == 2:
                # matching @GET(....
                p = re.compile("^@\w+\((\w+\/\w+)?")
                #p = re.compile("^(\w+\/\w+\[?.*?\]?)(\.[\/\w+]*)?")
                m = p.match(args[0])
                if m:
                    mode = self.get_mode(args[0])
                    sobjects = self.dive(mode, expression= args[0])
                  
                else:
                    parts = self._split_arg(args[0])
                    search_types = parts
                    sobjects = self.get_sobjects(search_types, is_count=True)

                return_mode = Container.get("Expression::return_mode")
                if return_mode == 'dict':
                    sobjects = self.get_flat_cache()

                # it is possible that get_sobjects just returns a number
                if type(sobjects) == types.IntType:
                    results = sobjects
                else:
                    results = self.count(sobjects)

            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

        elif method == 'PYTHON':
            if len(args) :
                from tactic.command import PythonCmd
                first_arg = args[0]
                if self.sobjects:
                    sobject = self.sobjects[0]
                else:
                    sobject = None
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
                    arg_results = self.dive(mode, expression=arg)
                    if type(arg_results) == types.ListType:
                        results = 0
                        for arg_result in arg_results:
                            if arg_result:
                                results += arg_result

                    #elif type(arg_results) == types.DictType:
                    #    sobjects = self.get_flat_cache()
                    #    results = self.sum(sobjects, column)

                    elif not arg_results:
                        results = 0
                    else:
                        results = arg_results


                else:
                    parts = self._split_arg(args[0])
                    search_types = parts[:-1]
                    column = parts[-1]

                    sobjects = self.get_sobjects(search_types)

                    return_mode = Container.get("Expression::return_mode")
                    if return_mode == 'dict':
                        sobjects = self.get_flat_cache()

                    results = self.sum(sobjects, column)
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

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
                    parts = self._split_arg(args[0])
                    search_types = parts[:-1]
                    sobjects = self.get_sobjects(search_types)
                    results = self.avg(sobjects, parts[-1])
                    """
                    # evaluate expression
                    mode = ExpressionMode()
                    arg_results = self.dive(mode, expression=arg)
                    if type(arg_results) == types.ListType:
                        results = 0
                        for arg_result in arg_results:
                            results += arg_result
                    else:
                        results = arg_results
                    """
                else:

                    parts = self._split_arg(args[0])
                    search_types = parts[:-1]
                    column = parts[-1]
                    sobjects = self.get_sobjects(search_types)
                    results = self.avg(sobjects, column)

            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

            # FIXME: search_types is not declared if m is None. It's fixed above in if not m:
            #sobjects = self.get_sobjects(search_types)
            #results = self.avg(sobjects, column)


        elif method == 'MIN':
            if len(args) == 1:
                parts = self._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

            sobjects = self.get_sobjects(search_types)
            results = self.fcmp(sobjects, column, op='<')

        elif method == 'MAX':
            if len(args) == 1:
                parts = self._split_arg(args[0])
                search_types = parts[:-1]
                column = parts[-1]
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

            sobjects = self.get_sobjects(search_types)
            results = self.fcmp(sobjects, column, op='>')

        elif method == 'FLOOR':
            if len(args) == 1:
                arg = args[0]
                mode = self.get_mode(arg)
                arg_results = self.dive(mode, expression=arg)

                # FIXME: should this not always return an array
                results = []
                if type(arg_results) == types.ListType:
                    for arg_result in arg_results:
                        result = math.floor(arg_result)
                        results.append(result)
                else:
                    results = math.floor(arg_results)

            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))


        elif method == 'UNIQUE':
            if len(args) == 1:
                arg = args[0]
                mode = self.get_mode(arg)
                result = self.dive(mode, expression=arg)
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
                    # provide some predictability in the result
                    results.sort()
            else:
                raise SyntaxError("Method @%s can only have one argument, found [%s] in expression [%s]" % (method, len(args), self.expression))


        elif method == 'UNION':
            results = set()
            for arg in args:
                mode = self.get_mode(arg)
                result = self.dive(mode, expression=arg)
                results = results.union(result)
            results = list(results)

        elif method == 'INTERSECT':
            results = set()
            is_first = True
            final_sks = []
            for arg in args:
                mode = self.get_mode(arg)
                result = self.dive(mode, expression=arg)
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
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            mode = self.get_mode(expression)
            result = self.dive(mode, expression=expression)
            if type(result) == types.ListType and result:
                result = result[0]
            if result:
                expression = args[1]
                mode = self.get_mode(expression)
                results = self.dive(mode, expression=expression)
            else:
                if len(args) == 3:
                    expression = args[2]
                    mode = self.get_mode(expression)
                    results = self.dive(mode, expression=expression)
                else:
                    results = None

        elif method == 'CASE':
            for i in xrange(0, len(args), 2):
                expression = args[i]
                value_expr = args[i+1]
                mode = self.get_mode(expression)
                result = self.dive(mode, expression=expression)

                # NOTE: single assumption
                # if the returned value is a list, then take the first one
                if type(result) == types.ListType:
                    result = result[0]

                if result:
                    mode = self.get_mode(value_expr)
                    results = self.dive(mode, expression=value_expr)
                    break


        elif method == 'STRING':
            if len(args) >= 2:
                raise SyntaxError("Method @%s must have only 1 argument" % (method))
            result = args[0]
            if not isinstance(result, basestring):
                result = str(result)
            #else:
            #    mode = self.get_mode(result)
            #    result = self.dive(mode, expression=result)
            #    result = str(result)
            results = result


        elif method == 'FOREACH':
            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            mode = self.get_mode(expression)
            results = self.dive(mode, expression=expression)

            # iterate through each
            format = args[1]
            results = [format % x for x in results]

            # do a join if a 3rd parameter is specified
            if len(args) == 3:
                delimiter = args[2]
                results = delimiter.join(results)
                


        elif method == 'JOIN':
            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            mode = self.get_mode(expression)
            results = self.dive(mode, expression=expression)

            delimiter = args[1]
            results = delimiter.join(results)


        elif method == 'SUBSTITUTE':
            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            values_list = []
            for arg in args[1:]:
                expression = arg
                mode = self.get_mode(expression)
                values = self.dive(mode, expression=expression)
                values_list.append(values)

            # transpose the values
            if len(values_list) == 1:
                pass
            else:
                values_list = zip(*values_list)
            results = []
            for values in values_list:
                result = args[0] % values
                results.append(result)


        elif method == 'STARTSWITH':

            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            mode = self.get_mode(expression)
            results = self.dive(mode, expression=expression)
            if not results:
                return False

            result = results[0]
            return result.startswith(args[1])

        elif method == 'ENDSWITH':

            if len(args) <= 1:
                raise SyntaxError("Method @%s must have at least 2 argument, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            mode = self.get_mode(expression)
            results = self.dive(mode, expression=expression)
            if not results:
                return False

            result = results[0]
            return result.endswith(args[1])



        elif method == 'BASENAME':
            if len(args) < 1:
                raise SyntaxError("Method @%s must have at least 1 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            if not expression.startswith("@"):
                expression = "@GET(%s)" % expression
            mode = self.get_mode(expression)
            values = self.dive(mode, expression=expression)

            results = []
            for value in values:
                value2 = os.path.basename(value)
                results.append(value2)


        elif method == 'DIRNAME':
            if len(args) < 1:
                raise SyntaxError("Method @%s must have at least 1 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            if not expression.startswith("@"):
                expression = "@GET(%s)" % expression
            mode = self.get_mode(expression)
            values = self.dive(mode, expression=expression)

            results = []
            for value in values:
                if not value:
                    value2 = ""
                else:
                    value2 = os.path.dirname(value)
                results.append(value2)



        elif method == 'REPLACE':
            if len(args) != 3:
                raise SyntaxError("Method @%s must have 3 arguments, found [%s] in expression [%s]" % (method, len(args), self.expression))

            expression = args[0]
            mode = self.get_mode(expression)
            values = self.dive(mode, expression=expression)

            # FIXME: empty string is handled weirdly elsewhere and resturns "''"
            if args[2] == "''":
                args[2] = ''

            results = []
            for value in values:
                result = value.replace( args[1], args[2] )
                results.append(result)


        elif method == 'UPDATE':
            # the first argument is sobjects
            expression = args[0]
            if expression == "sobject":
                sobjects = self.sobjects
            else:
                mode = self.get_mode(expression)
                sobjects = self.dive(mode, expression=expression)

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
            if len(args):
                first_arg = args[0]
                expression = "@SOBJECT(%s)" % first_arg
                mode = self.get_mode(expression)
                sobjects = self.dive(mode, expression=expression)
            else:
                sobjects = self.sobjects
                expression = "@SOBJECT()"

            results = []
            if sobjects:
                if len(args) > 1:
                    context = args[1]
                    if not context:
                        context = "__ALL__"
                else:
                    context = "__ALL__"
                #file_type = args[2]

                if len(args) > 2:
                    print args[2]
                    if args[2] == "web":
                        #base_dir = Environment.get_base_url().to_string()
                        base_dir = Environment.get_web_dir()
                    else:
                        base_dir = Environment.get_asset_dir()
                else:
                    base_dir = Environment.get_asset_dir()

                mode = self.get_mode(expression)

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
            mode = self.get_mode(expression)
            results = self.dive(mode, expression=expression)


        elif method == 'FORMAT':
            expression = args[0]
            mode = self.get_mode(expression)

            result = self.dive(mode, expression=expression)
            if result is None:
                result = ""


            args_len = len(args)
            if args_len != 0:
                format_option = None
                if args_len >= 2:
                    format_type = 'format'
                    format = args[1]
                    # support optional arg for timecode for example
                    if args_len > 2:
                        format_option = args[2]
                else: # this part does not seem to be used
                    format_type = args[1]
                    format = args[2]

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
            raise SyntaxError("Method [%s] not support found in expression[%s]" % (method, self.expression))


        return results


    def format_results(self, results, format):

        if isinstance(results, dict):
            new_results = {}
            for key, values in results.items():
                if values:
                    new_results[key] = self.format_results(values, format)
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
            



    def process_search_type(self, search_type):

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
                #    string_str = self.dive(mode, expression=string_str)
           
                string = []
                cur_filter.append(string_str)
                string_mode = False
                string_delimiter = None
                
            elif token == method_delimiter:
                string.append(token)
                string_str = "".join(string)
                
                mode = self.get_mode(string_str)
                string_str = self.dive(mode, expression=string_str)
                
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
                
                raise SyntaxError("Could not process token [%s] search type [%s] in expression [%s]" % (token, search_type, self.expression))


        return base_search_type, filters

        

    def get_search(self, related_types, is_count=False):
        search =  self.get_sobjects(related_types, is_count=is_count, is_search=True)
        if not isinstance(search, Search):
            raise ParserException('Make sure the @SEARCH expression ends with a valid sType') 
        return search

    def group_filters(self, filters):
        context_filters = []
        reg_filters = []
        for item in filters:
            if '@CONTEXT' in item:
               item[0] = item[0].replace('@CONTEXT','context')
               context_filters.append(item)
            else:
               reg_filters.append(item)

        return reg_filters, context_filters

    def get_sobjects(self, related_types, is_count=False, is_search=False, unique=True):
        # FIXME: not sure why id() does not work. It seems to return the same
        # results all the time.  It is desireable to use id because the
        # keys would be much smaller
        #key = "%s|%s" % (related_types, id(self.sobjects))

        #key = "%s|%s|%s" % (unique, related_types, str(self.sobjects))
        self.related_types = related_types

        if self.search:
            key = "%s|%s|%s" % (self.expression, related_types, str(self.search))
        else:
            key = "%s|%s|%s" % (self.expression, related_types, str(self.sobjects))
        if len(key) > 10240:
            print "WARNING: huge key in get_sobjects in expression"

        if self.use_cache == True:
            results = Container.get_dict(get_expression_key(), key)
            if results != None:
                return results

        related_types_filters = {}
        related_types_paths = {}

        related_exprs = related_types[:]
        related_types = related_types[:]

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

            related_type, filters = self.process_search_type(related_type)

            related_expr = related_exprs[i]

            related_types[i] = related_type
            related_types_filters[related_expr] = filters
            related_types_paths[related_expr] = path


        # handle some absolute sobjects
        if len(related_types) == 1:
            related_type = related_types[0]
            related_expr = related_exprs[0]

            # support some shorthand here?
            if related_type == 'login':
                related_sobjects = [Environment.get_login()]
                return related_sobjects
            elif related_type == 'state':
                sobject = SearchType.create("sthpw/virtual")
                for name, value in self.state.items():
                    if value != None:
                        sobject.set_value(name, value)
                return [sobject]

            elif related_type == 'parent':
                related_sobjects = []
                for sobject in self.sobjects:
                    parent = sobject.get_parent()
                    related_sobjects.append(parent)
                    self.cache_sobjects(sobject.get_search_key(), [parent])
                return related_sobjects

            elif related_type == 'connect':
                related_sobjects = []
                from pyasm.biz import SObjectConnection
                filters = related_types_filters.get(related_expr)
                reg_filters, context_filters = self.group_filters(filters)
                
                if is_search:
                    connections = SObjectConnection.get_connections(self.sobjects, context_filters=context_filters)
                    related_search = SObjectConnection.get_search(connections, filters=reg_filters)
                    return related_search
                else:

                    connections = SObjectConnection.get_connections(self.sobjects, context_filters=context_filters)
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
                for tmp_key in keys:
                    sobject.set_value(tmp_key, palette.color(tmp_key))
                related_sobjects = [sobject]
                return related_sobjects
 
            elif related_type == 'search_type':
                related_sobjects = []
                for sobject in self.sobjects:
                    search_type = sobject.get_search_type_obj()
                    related_sobjects.append(search_type)
                    return related_sobjects
 
            elif related_type == 'project':
                related_sobjects = []
                project = Project.get()
                related_sobjects.append(project)
                return related_sobjects

            elif related_type == 'site':
                related_sobjects = []
                site = Site.get()
                related_sobjects.append(site)
                return related_sobjects


        # if no sobjects have been specified to start with, then use
        # the first search type as a starting point
        if not self.sobjects:
            related_type = related_types[0]
            related_expr = related_exprs[0]

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
            elif related_type == 'site':
                site = Site.get()
                related_sobjects = [site]

            elif related_type.find("/") == -1:
                sobject = self.get_env_sobject(related_type)
                if sobject:
                    related_sobjects = [sobject]
                else:
                    related_sobjects = []

                if is_search:
                    related_search = None


            elif not related_type:
                related_sobjects = []
                if is_search:
                    related_search = None
            else:
                related_sobjects = []
                # do the full search
                if not self.search:
                    search = Search(related_type)
                else:
                    # Base type have to be the same
                    if not related_type == self.search.get_base_search_type():
                        raise SyntaxError('Base Type and Related type must be the same: %s' % self.expression)
                    search = self.search

                if self.show_retired:
                    search.set_show_retired(True)

                filters = related_types_filters.get(related_expr)
                search.add_op_filters(filters)

                # add any extra filters
                extra_filters = Container.get("Expression::extra_filters")
                if extra_filters:
                    extra_filter = extra_filters.get(related_type)
                    if extra_filter:
                        search.add_op_filters(extra_filter)

                # on the very specific case when there are no relative sobjects
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
            related_exprs = related_exprs[1:]
        else:
            # start of with the current sobject list
            related_sobjects = self.sobjects

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

            related_expr = related_exprs[i]

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
                    self.cache_sobjects(related_sobject.get_search_key(), [parent])


            elif related_type == 'connect':
                list = []
                from pyasm.biz import SObjectConnection

                filters = related_types_filters.get(related_expr)
                reg_filters, context_filters = self.group_filters(filters)

                if is_search:
                    related_search.add_column('id')
                    # assume dst direction, pass in a src_search and empty sobject list to return a search
                    direction = 'dst'
                    connection_search = SObjectConnection.get_connections([], direction=direction,\
                        context_filters=context_filters, src_search=related_search)
                    if connection_search:
                        connection_search.add_column('%s_search_id'% direction)
                        related_search = connection_search
                else:
                    #connections, list = SObjectConnection.get_connected_sobjects(related_sobjects, filters=reg_filters)
                    connections = SObjectConnection.get_connections(related_sobjects, context_filters=context_filters)
                    list = SObjectConnection.get_sobjects(connections, filters=reg_filters)


                # TODO: caching is not implemented on connect
                #self.cache_sobjects(related_sobject.get_search_key(), sobjects)

            elif related_type.find("/") == -1:
                list = []
                sobject = self.get_env_sobject(related_type)
                if sobject:
                    list.append(sobject)

            elif i == 0 and related_type == cur_search_type:
                # no need to search for itself again
                if is_search:
                    related_search = Search(related_type)
                    if self.show_retired:
                        related_search.set_show_retired(True) 
                    if related_sobjects:
                        related_search.add_relationship_filters(related_sobjects)
                break

            #elif mode == 'fast':
            else:
                filters = related_types_filters.get(related_expr)
                path = related_types_paths.get(related_expr)
                
                if is_search:
                    # do the full search
                    sub_search = Search(related_type)

                    if self.show_retired:
                        sub_search.set_show_retired(True)

                    #FIXME: filters for the very last related_type is not found
                    filters = related_types_filters.get(related_expr)
                    sub_search.add_op_filters(filters)

                    if related_sobjects:
                        sub_search.add_relationship_filters(related_sobjects)
                    else:
                        # or from an sobject-less/plain search
                        sub_search.add_relationship_search_filter(related_search)
                        
                    related_search = sub_search


                else:

                    # on the very specific case when there is just one relative
                    # type, then just use the count method
                    if is_count and len(related_types) == 1:
                        search = Search(related_type)
                        search.add_relationship_filters(related_sobjects, path=path)
                        search.add_op_filters(filters)
                        count = search.get_count()
                        return count


                    tmp_dict = Search.get_related_by_sobjects(related_sobjects, related_type, filters=filters, path=path, show_retired=self.show_retired)

                    # collapse the list and make it unique
                    tmp_list = []
                    for tmp_key, items in tmp_dict.items():
                        tmp_list.extend(items)
                        self.cache_sobjects(tmp_key, items)


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
                        tmp_sobj = self.get_env_sobject(related_type)
                        if tmp_sobj:
                            tmp = [tmp_sobj]
                        else:
                            tmp = []
                    else:
                        filters = related_types_filters.get(related_type)
                    	path = related_types_paths.get(related_type)
                        tmp = related_sobject.get_related_sobjects(related_type, filters, path=path, show_retired=self.show_retired)
                    self.cache_sobjects(related_sobject, tmp)
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
        Container.put_dict(get_expression_key(), key, related_sobjects)

        return related_sobjects





    def get(self, sobjects, column):
        if isinstance(sobjects, dict):
            results = {}
            for key, values in sobjects.items():
                """
                # special case where leaf = [sobject].  This is used to
                # designate a leaf value.  Look at get_flat_cache() for
                # code and explanation
                if key and values and values[0].get_search_key() == key:
                    # The result is empty
                    results[key] = [None]
                else:
                    results[key] = self.get(values, column)
                """
                results[key] = self.get(values, column)
            return results

        if not sobjects:
            return []

        values = []
        for sobject in sobjects:
            # sobject could have been deleted
            if not sobject:
                continue

            if isinstance(sobject, dict):
                value = sobject.get(column)
                col_type = SearchType.get_column_type(sobject.get('search_type'), column)
                if value and col_type in ['timestamp','datetime2']:
                    if not isinstance(value, datetime.datetime):
                        value = parser.parse(value)
                values.append(value)
                continue

            elif column == '__search_key__':
                value = sobject.get_search_key()
            elif column == '__search_type__':
                value = sobject.get_search_type()
            elif column == '__base_search_type__':
                value = sobject.get_base_search_type()
            elif column == '__project__':
                value = sobject.get_project_code()
            elif column == '__all__':
                value = sobject.get_data()
            else:
                value = sobject.get_value(column)
            
            col_type = SearchType.get_column_type(sobject.get_search_type(), column)
            #col_type = sobject.get_search_type_obj().get_column_type(column)
            if value and col_type in ['timestamp','datetime2']:
                if not isinstance(value, datetime.datetime):
                    value = parser.parse(value)
           
            values.append(value)

            self.cache_sobjects(sobject, value)

        return values


    def sum(self, sobjects, column):
        if isinstance(sobjects, dict):
            results = {}
            for key, values in sobjects.items():
                results[key] = self.sum(values, column)
            return results

        total = 0
        for sobject in sobjects:
            
            value = sobject.get_value(column, no_exception=True)
            if not value:
                continue
            if type(value) in types.StringTypes:
                try:
                    value = float(value)
                except:
                    value = 0
            total += value

        return total

    def avg(self, sobjects, column):
        value = self.sum(sobjects, column)
        count = len(sobjects)
        if not count:
            return 0
        avg = float(value) / count
        return avg


    def count(self, sobjects):
        if isinstance(sobjects, dict):
            results = {}
            for key, values in sobjects.items():
                results[key] = self.count(values)
            return results

        if not sobjects:
            return 0
        return len(sobjects)


    def is_zero(self, sobjects, column):
        value = self.sum(sobjects, column)
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

    def __init__(self):
        self.cur_arg = []
        self.args = []

    def get_result(self):
        return self.args

    def parse(self, token):
        if token in [' ','\n','\t']:
            return

        elif token == ')':
            return "exit"

        else:
            mode = ArgMode()
            arg = self.dive(mode, reuse_token=True)
            self.args.append(arg)

        if self.index == len(self.expression):
            raise SyntaxError('No closing bracket around arguments for [%s]' % self.expression)
        # if the next character is ), then exit
        try:
            if self.expression[self.index] == ')':
                return 'exit'
        except IndexError:
            raise SyntaxError('Incorrect syntax found for %s' %self.expression)



class ArgMode(ExpressionParser):

    def __init__(self):
        self.result = []

        #self.in_filter = False
        self.brackets = 0

        self.literal_mode = False
        self.literal = []

        self.is_only_literal = True


    def parse(self, token):
        # handle literals
        if token == "'":
            if self.literal_mode:
                self.literal_mode = False
                if not self.literal:
                    self.result.append("''")
                else:
                    if self.is_only_literal:
                        literal = "".join(self.literal)
                    else:
                        literal = "'%s'" % "".join(self.literal)
                    self.result.append(literal)
                self.literal = []
            else:
                self.literal_mode = True

        elif self.literal_mode:
            self.literal.append(token)

        # ignore spaces
        elif token == ' ':
            return

        elif token in [',', ')']:
            if token == ')':
                self.brackets -= 1

                if self.brackets < 0:
                    self.result = "".join(self.result)
                    self.result = self.result.strip()
                    return "exit"
                else:
                    self.result.append(token)
                    
            else: # , found. Ensure it is a arg separator using bracket counts
                if self.brackets < 1:
                    self.result = "".join(self.result)
                    self.result = self.result.strip()
                    return "exit"
                else:
                    self.result.append(token)

        # start a filter
        elif token == '[':
            mode = FilterMode()
            tmp = self.result     # div makes use of self.result
            filter = self.dive(mode, reuse_token=True)
            self.result = tmp
            self.result.append(filter)

        elif token == '(':
            self.brackets += 1
            self.result.append(token)


        #elif token == ' ':
        #    #raise SyntaxError("Space found in argument in expression [%s]" % self.expression)

        else:
            self.result.append(token)
            self.is_only_literal = False


class FilterMode(ExpressionParser):

    def __init__(self):
        self.result = []
        self.brackets = 0

    def get_result(self):
        return "".join( self.result)

    def parse(self, token):

        # handle literals
        if token == ']':
            self.result.append(token)
            if self.brackets == 0:
                return 'exit'

        else:
            if token == '(':
                self.brackets += 1
            elif token == ')':
                self.brackets -= 1
            self.result.append(token)

class SqrBracketMode(ExpressionParser):
    '''this replaces the old regex of lazy findall of [..], which can't handle recursion 
        p = re.compile("(\[.*?\])")
        filters = p.findall(arg)
        
        The input string is a greedy regex of [..]'''

    def __init__(self):
        self.result = []
        self.brackets = 0
        self.delimiter = None
        self.stack = []

    def get_result(self):
        if self.brackets > 0:
            raise SyntaxError('Incorrect syntax: square brackets for the filter [] are not balanced for "%s"'%self.expression)
        return self.result

    def parse(self, token):
        if token == '[':
            self.brackets += 1
            self.delimiter = ']'
            self.stack.append(token)

        elif token == self.delimiter:
            self.brackets -= 1
            self.stack.append(token)
            if self.brackets == 0:
                string_str = "".join(self.stack)
                self.result.append(string_str)
                self.stack = []
        else:
            if self.brackets > 0:
                self.stack.append(token)

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




