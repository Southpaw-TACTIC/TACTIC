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

__all__ = ["XmlTest"]

import tacticenv

import unittest, pickle



Xml = None

class XmlTest(unittest.TestCase):

    def test_all(self):
        global Xml


        print "Testing: 4Suite"
        self.mode = "4Suite"
        from pyasm.common.xml_wrapper import Xml as classXml
        Xml = classXml
        self._test_all()

        print "Testing: lxml"
        self.mode = "lxml"
        from pyasm.common.lxml_wrapper import Xml as classXml
        Xml = classXml
        self._test_all()


    def _test_all(self):
        #self._test_read_string()
        self._test_attribute()
        self._test_create_doc()
        self._test_xpath()
        self._test_node_values()
        self._test_comment()
        #self._test_colon()
        self._test_to_string()

        self._test_color()


    def _test_read_string(self):
        xml = Xml()
        xml_string = '''
        <snapshot>
            <a>pig</a>
            <a>cow</a>
            <a>horse</a>
            <b>child</b>
            <c name="horse"/>
        </snapshot>'''
        xml.read_string(xml_string)


        expected = '''<?xml version='1.0' encoding='UTF-8'?>
<snapshot>
  <a>pig</a>
  <a>cow</a>
  <a>horse</a>
  <b>child</b>
  <c name='horse'/>
</snapshot>
'''

        print "[%s]" % xml.to_string()
        print "[%s]" % expected

        self.assertEquals(expected, xml.to_string())



    def _test_create_doc(self):
        xml = Xml()

        # create a new document
        doc = xml.create_doc("element")
        self.assertEquals(True, doc != None)

        # get the root element
        root = xml.get_root_node()
        self.assertEquals(True, doc != None)

        # create a new element with attributes
        display_node = xml.create_element("display")
        xml.set_attribute(display_node, "widget", "expression")
        xml.append_child(root, display_node)


        # get the node name
        name = xml.get_node_name(display_node)
        self.assertEquals("display", name)

        # test get attribute
        value = xml.get_attribute(display_node, "widget")
        self.assertEquals("expression", value)

        # test delete attribute
        xml.set_attribute(display_node, "garbage", "!!!!")
        value = xml.del_attribute(display_node, "garbage")
        self.assertEquals("!!!!", value)
        xml.del_attribute(display_node, "garbage2")


        # create a new element with text
        expr_node = xml.create_element("expression")
        xml.set_node_value(expr_node, "@GET(.completion)")
        xml.append_child(display_node, expr_node)

        value = xml.get_node_value(expr_node)
        self.assertEquals("@GET(.completion)", value)


        # create a new element with text
        expr_node = xml.create_text_element("mode", "check")
        xml.append_child(display_node, expr_node)

        # get all of the children values as a dict
        values = xml.get_node_values_of_children(display_node)
        expected = {'expression': '@GET(.completion)', 'mode': 'check'}
        self.assertEquals(expected, values)


        # FIXME: add CDATA element
        #cdata = xml.create_data_element("cbjs_action", '''a > b''')
        #display_node.append(cdata)

        #print xml.to_string()


    def _test_attribute(self):
        xml = Xml()
        xml.create_doc()
        element = xml.create_element("test")
        xml.set_attribute(element, "wow1", "1")
        xml.set_attribute(element, "wow2", "2")
        attrs = xml.get_attributes(element)

        keys = attrs.keys()
        keys.sort()

        self.assertEquals('wow1', keys[0])
        self.assertEquals('wow2', keys[1])




    def _test_xpath(self):
        xml_string = """
        <snapshot>
            <a>pig</a>
            <a>cow</a>
            <a>horse</a>
            <b>child</b>
            <c name="horse"/>
            <d name="cow"/>
            <d name="pig"/>
            <d name="dog" xx='1'/>
            <not_test/>
        </snapshot>
        """
        # build the xml object and find the values using xpath
        xml = Xml()
        xml.read_string(xml_string)


        # test get_node
        nodes = xml.get_nodes("snapshot/a")
        self.assertEquals(3, len(nodes) )
        node = xml.get_node("snapshot/b")
        self.assertEquals(1, node != None)

        # test not with no elements
        # WARNING: this is different in lxml
        xpath = "snapshot/not_test"
        node = xml.get_node(xpath)
        self.assertEquals(True, node != None)
        if node == None:
            self.fail()
        # Do not use!!!
        #if not node:
        #    ERROR



        xpath = "snapshot/a"
        values = xml.get_values(xpath)

        self.assertEqual("pig",values[0])
        self.assertEqual("cow",values[1])
        self.assertEqual("horse",values[2])

        # test single value
        value = xml.get_value("snapshot/b")
        self.assertEqual("child",value)

        # test getting an attribute
        value = xml.get_value("snapshot/c/@name")
        self.assertEqual("horse",value)

        # try "or" with nodes
        nodes = xml.get_nodes("snapshot/b | snapshot/c")
        self.assertEqual(len(nodes), 2)

        # try "or" with attributes
        nodes = xml.get_nodes("snapshot/d[@name='cow' or @name='pig']")
        self.assertEqual(len(nodes), 2)

        # try "and" with attributes
        nodes = xml.get_nodes("snapshot/d[@name='dog' and @xx='1']")
        self.assertEqual(len(nodes), 1)
        #xml.dump()

        # test none returned
        node = xml.get_node("snapshot/xxxxxx")
        self.assertEqual(None,node)





    def _test_node_values(self):

        xml_string = '''
        <element name='cow'>
          <display class='Whatever'>
            <a>1</a>
            <b>2</b>
            <c>3</c>
          </display>
        </element>'''

        xml = Xml()
        xml.read_string(xml_string)

        # get all of the children values as a dict
        display_node = xml.get_node("element/display")
        values = xml.get_node_values_of_children(display_node)
        expected = {
          'a': '1',
          'b': '2',
          'c': '3',
        }
        self.assertEquals(expected, values)



        xml_string = '''
        <element name='cow'>
          <display class='Whatever'>
            <a>1</a>
            <b>
              <x>123</x>
              <y>234</y>
              <z>345</z>
            </b>
            <c>3</c>
          </display>
        </element>'''

        xml = Xml()
        xml.read_string(xml_string)

        # get all of the children values as a dict
        display_node = xml.get_node("element/display")
        values = xml.get_recursive_node_values(display_node)
        expected = {
          'a': '1',
          'b': {
            'x': '123',
            'y': '234',
            'z': '345',
          },
          'c': '3',
        }
        self.assertEquals(expected, values)


        # get all of the children values as a dict
        node = xml.get_node("element")
        values = xml.get_recursive_node_values(node)
        expected = {
          'display': {
              'a': '1',
              'b': {
                'x': '123',
                'y': '234',
                'z': '345',
              },
              'c': '3',
            }
        }
        self.assertEquals(expected, values)




    def _test_comment(self):

        xml_string = '''
        <element>
          <!-- This is a comment -->
          <display class='SelectWdg'/>
        </element>
        '''

        xml = Xml()
        xml.read_string(xml_string)
        root = xml.get_root_node()
        children = xml.get_children(root)
        self.assertEquals( len(children), 1)



    def _test_colon(self):

        xml_string = '''<?xml version='1.0' encoding='UTF-8'?>
        <config>
        <search:whatever>
          <element class='whatever'/>
        </search:whatever>
        </config>
        '''
        xml = Xml()
        xml.read_string(xml_string)

        node = xml.get_node("config/search:whatever")



    def _test_to_string(self):
        xml_string = '''<?xml version='1.0' encoding='UTF-8'?>
        <config>
        <snapshot>
            <a>pig</a>
            <a>cow</a>
            <a>horse</a>
            <b>child</b>
            <c name="horse"/>
        </snapshot>
        </config>'''
        xml = Xml()
        xml.read_string(xml_string)

        node = xml.get_node("config/snapshot")

        node_string = xml.get_node_xml(node)
        if self.mode == '4Suite':
            expected = u'''<snapshot>
  <a>pig</a>
  <a>cow</a>
  <a>horse</a>
  <b>child</b>
  <c name='horse'/>
</snapshot>'''
        else:
            expected = u'''<snapshot>
  <a>pig</a>
  <a>cow</a>
  <a>horse</a>
  <b>child</b>
  <c name="horse"/>
</snapshot>'''

        self.assertEquals(expected, node_string.strip() )

        node = xml.get_node("config")
        nodes = xml.xpath(node, "snapshot")
        child = nodes[0]

        self.assertEquals( "snapshot", Xml.get_node_name(child) )


    def _test_color(self):
        xml_string = '''<?xml version='1.0' encoding='UTF-8'?>
<config>
  <color>
    <element name='test'>
      <colors>
        <value name='AAA'>#FF0000</value>
        <value name='BBB'>#FF8000</value>
        <value name='CCC'>#FFBD7A</value>
        <value name='DDD'>#FFFF00</value>
        <value name='EEE'>#FFFFFF</value>
        <value name='FFF'>#2EB800</value>
        <value name='GGG'>#0033FF</value>
      </colors>
      <text_colors>
        <value name='GGG'>#FFFFFF</value>
        <value name='FFF'>#FFFFFF</value>
        <value name='EEE'>#000000</value>
        <value name='DDD'>#000000</value>
        <value name='CCC'>#000000</value>
        <value name='BBB'>#FFFFFF</value>
        <value name='AAA'>#FFFFFF</value>
      </text_colors>
    </element>
  </color>
</config>
        '''

        xml = Xml()
        xml.read_string(xml_string)

        name = 'test'
        xpath = "config/color/element[@name='%s']/colors" % name
        text_xpath = "config/color/element[@name='%s']/text_colors" % name
        bg_color_node = xml.get_node(xpath)
        bg_color_map = xml.get_node_values_of_children(bg_color_node)

        self.assertEquals("#FF0000", bg_color_map.get("AAA"))
        self.assertEquals("#FF8000", bg_color_map.get("BBB"))


if __name__ == '__main__':
    unittest.main()



