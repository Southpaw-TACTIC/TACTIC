#!/usr/bin/python 
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

from pyasm.common import Container, jsonloads, Environment, Xml
from pyasm.security import Batch
from pyasm.search import Search, SearchType

from pyasm.unittest import UnittestEnvironment

import unittest


import urllib2

class RestTest(unittest.TestCase):

    def test_all(my):

        test_env = UnittestEnvironment()
        test_env.create()

        try:
            my._setup()
            print
            print
            print
            my._test_accept()
            my._test_method()
            my._test_custom_handler()
            print
            print
            print

        finally:
            test_env.delete()


    def send_request(my, url, headers, data={} ):

        ticket = Environment.get_ticket()

        method = headers.get("Method")
        if method == 'POST':
            data['login_ticket'] = ticket
            import urllib
            data = urllib.urlencode(data)
            request = urllib2.Request(url, data)
        else:
            url = "%s?login_ticket=%s" % (url, ticket)
            request = urllib2.Request(url)

        for key,value in headers.items():
            request.add_header(key,value)

        try:
            response = urllib2.urlopen(request)
        except Exception, e:
            # try again
            print "WARNING: ", e
            response = urllib2.urlopen(request)

        #print response.info().headers

        value = response.read()

        accept = headers.get("Accept")
        if accept == "application/json":
            value = jsonloads(value)

        return value



    def _setup(my):

        url = SearchType.create("config/url")
        url.set_value("url", "/rest/{code}")
        url.set_value('widget', '''
        <element>
          <display class='tactic.protocol.PythonRestHandler'>
            <script_path>rest/test</script_path>
          </display>
        </element>
        ''')
        url.commit()


        url = SearchType.create("config/url")
        url.set_value("url", "/rest2")
        url.set_value('widget', '''
        <element>
          <display class='tactic.protocol.TestCustomRestHandler'>
          </display>
        </element>
        ''')
        url.commit()



        url = SearchType.create("config/url")
        url.set_value("url", "/rest3/{method}/{data}")
        url.set_value('widget', '''
        <element>
          <display class='tactic.protocol.SObjectRestHandler'>
          </display>
        </element>
        ''')
        url.commit()





        script = SearchType.create("config/custom_script")
        script.set_value("folder", "rest")
        script.set_value("title", "test")
        script.set_value("script", """

from pyasm.common import Xml

accept = kwargs.get("Accept")
method = kwargs.get("Method")

print "kwargs: ", kwargs

code = kwargs.get("code")
if code == "CODE0123":
    return "OK"

if method == "POST":
    return "Method is POST"



if accept == "application/json":
    return [3,2,1]
    
else:
    return Xml('''
    <arr>
      <int>1</int>
      <int>2</int>
      <int>3</int>
    </arr>
    ''')
        """)
        script.commit()






    def _test_accept(my):

        # try json
        url = "http://localhost/tactic/unittest/rest"
        headers = {
            "Accept": "application/json"
        }
        ret_val = my.send_request(url, headers)
        my.assertEquals( [3,2,1], ret_val)


        # try xml
        url = "http://localhost/tactic/unittest/rest"
        headers = {
            "Accept": "application/xml"
        }
        ret_val = my.send_request(url, headers)
        xml = Xml(ret_val)
        values = xml.get_values("arr/int")
        my.assertEquals( ['1','2','3'], values)


        # try json
        url = "http://localhost/tactic/unittest/rest/CODE0123"
        headers = {
            "Accept": "application/json"
        }
        ret_val = my.send_request(url, headers)
        my.assertEquals( "OK", ret_val)




    def _test_method(my):

        # try json
        url = "http://localhost/tactic/unittest/rest"
        headers = {
            "Accept": "application/json",
            "Method": "POST"
        }
        ret_val = my.send_request(url, headers)
        my.assertEquals( "Method is POST", ret_val)



    def _test_custom_handler(my):

        # try json
        url = "http://localhost/tactic/unittest/rest2"
        headers = {
            "Accept": "application/json",
            "Method": "POST"
        }
        ret_val = my.send_request(url, headers)
        my.assertEquals( "Test Custom POST", ret_val)


        # try json
        url = "http://localhost/tactic/unittest/rest3/expression"
        headers = {
            "Accept": "application/json",
            "Method": "POST"
        }
        data = {
            'expression': '@SOBJECT(unittest/person)'
        }
        ret_val = my.send_request(url, headers, data)
        print ret_val



if __name__ == "__main__":
    Batch()
    unittest.main()

