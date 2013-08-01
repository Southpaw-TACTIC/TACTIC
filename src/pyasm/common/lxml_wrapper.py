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

__all__ = ["XmlException", "Xml"]


import time, string, types, thread, os

from cStringIO import StringIO

from base import *
from common import *
from common_exception import TacticException

import lxml.etree as etree


class XmlException(TacticException):
    pass


    
class Xml(Base):
    '''simple class to extract information from an xml document'''

    # cache xml files in a globa data structure
    XML_FILE_CACHE = {}
    XML_FILE_MTIME = {}


    def get_xml_library():
        return "lxml"
    get_xml_library = staticmethod(get_xml_library)


    def __init__(my, string=None, file_path=None, doc=None, strip_cdata=True):
        my.doc = None
        my.uri = "XmlWrapper"
        my.strip_cdata = strip_cdata
        if string:
            my.read_string(string)
        elif file_path:
            my.read_file(file_path)
        elif doc:
            my.doc = doc


        my.cache_xpath = {}

    def read_file(my, file_path, cache=True):
        #my.reader = PyExpat.Reader()
        #my.doc = my.reader.fromUri(file_path)
        # the xml library does not like windows style separators
        try:
            file_path = file_path.replace("\\", "/")

            if not cache:
                ##!!
                parser = etree.XMLParser(remove_blank_text=True)
                my.doc = etree.parse(file_path, parser)
                # we assume doc is the root node instead of the ElementTree
                my.doc = my.doc.getroot()

            else:
                cur_mtime = os.path.getmtime(file_path)
                cache_mtime = my.XML_FILE_MTIME.get(file_path)

                if cur_mtime == cache_mtime:
                    my.doc = my.XML_FILE_CACHE.get(file_path)
                else:

                    parser = etree.XMLParser(remove_blank_text=True)
                    my.doc = etree.parse(file_path, parser)
                    my.doc = my.doc.getroot()

                    my.cache_xml(file_path, my.doc, cur_mtime)



        except Exception, e:
            #print "Error in xml file: ", file_path
            raise XmlException(e)


    def cache_xml(cls, file_path, doc, cur_mtime):
        lock = thread.allocate_lock()
        lock.acquire()
        cls.XML_FILE_CACHE[file_path] = doc

        cls.XML_FILE_MTIME[file_path] = cur_mtime

        lock.release
    cache_xml = classmethod(cache_xml)


    def clear_xpath_cache(my):
        my.cache_xpath = {}


    xmls = set()
    count = 0
    def read_string(my, xml_string, print_error=True, remove_blank_text=True):

        if type(xml_string) not in types.StringTypes:
            xml_string = str(xml_string)
        elif type(xml_string) == types.UnicodeType:
            xml_string = xml_string.replace('encoding="UTF-8"','')
            xml_string = xml_string.replace("encoding='UTF-8'",'')
            if xml_string.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
                #print "STRING ", xml_string
                #xml_string = xml_string.encode('UTF-8')
                pass

        try:
            
            parser = etree.XMLParser(remove_blank_text=remove_blank_text, strip_cdata=my.strip_cdata)
            if not xml_string:
                raise XmlException('The input XML is empty.')
            my.doc = etree.fromstring(xml_string, parser)
        except Exception, e:
            if print_error:
                print "Error in xml: ", xml_string
                print e
            raise XmlException(e)


    def create_doc(my, root_name="snapshot"):
        my.doc = etree.Element(root_name)
        # since we assume the use of Element in most places, avoid using ElementTree here
        #my.doc = etree.ElementTree(etree.Element(root_name))
        return my.doc
    
    def get_doc(my):
        '''returns the document object'''
        return my.doc


    def get_root_node(my):
        return my.doc

    def import_node(my, element, deep=True):
        #return my.doc.importNode(element, deep)
        return my.doc.insert(0, element)

    def create_element(my, name):
        '''create a new element with this document'''
        return etree.Element(name)

    def create_text_element(my, name, text, node=None):
        '''create an element with a text node embedded'''
        element = my.create_element(name)
        element.text = text

        if node is not None:
            node.append(element)

        return element


    # !!! FIXME
    def create_data_element(my, name, text):
        '''create an element with a text node embedded'''
        #elem = my.create_element(name)
        #elem.text = "<![CDATA[%s]]>" % text

        #parser = etree.XMLParser(strip_cdata=False)
        #elem = etree.XML('<%s><![CDATA[%s]]></%s>'%(name, text, name))
        elem = my.create_element(name)
        elem.text = etree.CDATA(text)
        return elem

    def create_comment(my, text):
        '''create an element with a text node embedded'''
        comment_node = etree.Comment(text)
        #comment_node.text = text
        return comment_node


    def rename_node(cls, node, name):
        node.tag = name
    rename_node = classmethod(rename_node)



    def get_parent(cls, node):
        return node.getparent()
    get_parent = classmethod(get_parent)

    def get_children(cls, node):
        xx = node.getchildren()
        children = []
        # filter out the comments
        for x in xx:
            if x.tag is etree.Comment:
                continue
            children.append(x)
        return children
    get_children = classmethod(get_children)

    def get_first_child(cls, node):
        children = cls.get_children(node)
        if not children:
            return None
        else:
            return children[0]
    get_first_child = classmethod(get_first_child)

    def append_child(cls, node, child):
        node.append(child)
    append_child = classmethod(append_child)


    def remove_child(cls, node, child):
        #children = my.get_children(node)
        node.remove(child)
    remove_child = classmethod(remove_child)
  
    def replace_child(cls, node, old_node, new_node):
        node.replace(old_node, new_node)
    replace_child = classmethod(replace_child)
  
 
    def _evaluate(my, xpath, node=None):
        if node != None:
            result = node.xpath(xpath)
            return result
            


        result = my.cache_xpath.get(xpath)
        if result:
            return result
        if result == []:
            return result

        # FIXME: not sure about this.  Prohibits relative paths!
        if not xpath.startswith('/'):
            xpath = "/%s" % xpath

        if xpath.find(" | ") != -1:
            parts = xpath.split(" | ")
            xpath = " | ".join( ["/%s" % x for x in parts] )

       
        # we have to put in some namespaces because of our use of such
        # tags as link:search
        namespaces = {
            'link_search': 'http://southpawtech.com'
        }

        if node == None:
            result = my.doc.xpath(xpath, namespaces=namespaces)
        else:
            result = node.xpath(xpath, namespaces=namespaces)
            print "xpath: ", xpath
        my.cache_xpath[xpath] = result

        return result


    def get_nodes(my, xpath):
        '''get all of the nodes within the given xpath string'''
        try:
            nodes = my._evaluate(xpath)
        except Exception, e:
            raise XmlException('XPath Error for [%s]: %s'% (xpath, e.message))
        return nodes
    
    def get_nodes_attr(my, xpath, attr):
        nodes = my.get_nodes(xpath)
        value_list = []
        for node in nodes:
            value_list.append(Xml.get_attribute(node, attr))
        return value_list

    def get_node(my, xpath):
        '''convenience function to get a single node'''
        nodes = my.get_nodes(xpath)
        if len(nodes) == 0:
            return None
        else:
            return nodes[0]



    def get_values(my, xpath):
        values = []
        for node in my._evaluate(xpath):
            if not isinstance(node,basestring):
                value = my.get_node_value(node)
                values.append(value)
            else:
                try:
                    if isinstance(node, etree._ElementStringResult):
                        values.append(str(node))
                    else:
                        values.append(node)
                except:
                    values.append(node)

        return values



    def get_value(my, xpath):
        values = my.get_values(xpath)
        if len(values) == 0:
            return ""
        else:
            return values[0]

    def get_xml(my):
        '''returns a stringified version of the document'''
        return etree.tostring(my.doc, pretty_print=True)


    def to_string(my, node=None, pretty=True, tree=False, method='xml'):
        '''returns a stringified version of the document
            method: xml, html, text'''
        if tree: # needed for adding comment before the root
            if node == None:
                output = etree.ElementTree(my.doc)
            else:
                output = etree.ElementTree(node)
        else:
            if node == None:
                output = my.doc 
            else:
                output = node
       

        value = etree.tostring(output, pretty_print=pretty, encoding='utf-8', method=method)
        value = unicode( value, 'utf-8')
        return value


    def dump(my):
        '''print out the stringafied version'''
        print my.to_string()



    #
    # static methods
    #
    def get_attributes( cls, node ):
        return dict(node.attrib)
    get_attributes = classmethod(get_attributes)


    def get_attribute( cls, node, attribute ):
        return node.get(attribute)
    get_attribute = classmethod(get_attribute)

    def set_attribute( cls, node, attribute, value ):
        if not isinstance(value,basestring):
            value = str(value)
        return node.set(attribute,value)
    set_attribute = classmethod(set_attribute)

    def del_attribute(cls, node, attribute):
        value = node.get(attribute)
        try:
            del(node.attrib[attribute])
        except KeyError:
            pass
        return value
    del_attribute = classmethod(del_attribute)
    
    def get_node_name( node ):
        return node.tag
    get_node_name = staticmethod(get_node_name)


    def insert_before(new_element, ref_element, parent=None):
        '''parent is None, but just to match the xml_wrapper impl'''
        ref_element.addprevious(new_element)
    insert_before = staticmethod(insert_before)

    def insert_after(new_element, ref_element, parent=None):
        ref_element.addnext(new_element)
    insert_after = staticmethod(insert_after)




    def set_node_value(cls, node, text):
        '''sets the value of a node.  This value is the first child'''
        node.text = text
        return text
    set_node_value = classmethod(set_node_value)



    def get_node_value(cls, node):
        '''Gets the value of a node.  This value is often the first child
        of the node'''
        value = node.text
        if value == None:
            return ''
        else:
            return value
    get_node_value = classmethod(get_node_value)

    def get_node_values_of_children(cls, node):
        '''Gets the all the node value of the children of a node'''
        values = {}

        if node == None:
            return values

        for child in node.iterchildren():
            name = Xml.get_attribute(child,"name")
            if not name:
                name = child.tag

            # Comments come in as functions?!
            if not isinstance(name, basestring):
                continue
            text = child.text
            if text == None:
                text = ''
            values[name] = text

            #for child_node in child_nodes:
            #    child_values = my._process_node(child_node, child_values)
            #name = node.nodeName
            #if child_values:
            #    value_dict[name] = child_values
 
        return values
    get_node_values_of_children = classmethod(get_node_values_of_children)



    def get_recursive_node_values(cls, node):
        '''Gets the all the node value of the children of a node'''
        values = {}

        if node == None:
            return values

        cls._get_recursive_node_values(node, values)

        name = Xml.get_node_name(node)
        values = values.get(name)

        if isinstance(values, basestring):
            values = values.strip()

        if not values:
            return {}
        else:
            return values
    get_recursive_node_values = classmethod(get_recursive_node_values)


    def _get_recursive_node_values(cls, node, values):
        children = cls.get_children(node)

        # get the name of the node
        name = Xml.get_node_name(node)

        # first check the attribute for a name
        if not children:
            value = cls.get_node_value(node)
            values[name] = value

        else:
            child_values = {}
            values[name] = child_values
            for child in children:
                cls._get_recursive_node_values(child, child_values)
            
    _get_recursive_node_values = classmethod(_get_recursive_node_values)





    # FIXME
    def get_node_xml(node):
        '''returns a stringified version of the node'''
        #xml = StringIO()
        #PrettyPrint(node,xml)
        #return xml.getvalue()
        xml = Xml()
        return xml.to_string(node)
    get_node_xml = staticmethod(get_node_xml)

    def xpath(node, xpath):
        '''Evaluate an xpath of an arbitrary node'''
        xml = Xml()
        xml.create_doc()
        nodes = xml._evaluate(xpath, node=node)
        #nodes = Evaluate(xpath, node)
        return nodes
    xpath = staticmethod(xpath)



    def to_html(value, allow_empty=False):
        if value == "":
            if allow_empty:
                return value
            else:
                value = "&nbsp;"

        else:
            #value = value.replace("<", "&lt;")
            #value = value.replace(">", "&gt;")

            # we need to encode this specially because this inline xml is
            # not part of the dom structure.
            value = value.replace("<", "&spt_lt;")
            value = value.replace(">", "&spt_gt;")
        return value
    to_html = staticmethod(to_html)




    import StringIO
    def parse_html(html):
        parser = etree.HTMLParser(remove_blank_text=False)
        tree = etree.parse(StringIO(html), parser)
        return tree
    parse_html = staticmethod(parse_html)


