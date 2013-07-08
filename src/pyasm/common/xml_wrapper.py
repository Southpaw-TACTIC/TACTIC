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
import random

from cStringIO import StringIO

from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.Domlette import implementation
from Ft.Xml.XPath import Evaluate
from xml.dom.ext import PrettyPrint, Print
#from Ft.Xml.Domlette import PrettyPrint, Print
from Ft.Xml.Domlette import PrettyPrint as FtPrettyPrint

from container import Container
from base import *
from common import *
from common_exception import TacticException




class XmlException(TacticException):
    pass


    
class Xml(Base):
    """simple class to extract information from an xml document"""

    # cache xml files in a globa data structure
    XML_FILE_CACHE = {}
    XML_FILE_MTIME = {}


    def get_xml_library():
        return "4suite"
    get_xml_library = staticmethod(get_xml_library)



    def __init__(my, string=None, file_path=None, strip_cdata=False):
        my.doc = None
        my.uri = "XmlWrapper"
        my.strip_cdata = strip_cdata
        if string:
            my.read_string(string)
        elif file_path:
            my.read_file(file_path)

        my.cache_xpath = {}

    def read_file(my, file_path, cache=True):
        #my.reader = PyExpat.Reader()
        #my.doc = my.reader.fromUri(file_path)
        # the xml library does not like windows style separators
        try:
            file_path = file_path.replace("\\", "/")

            if not cache:
                my.doc = NonvalidatingReader.parseUri("file://%s" % file_path, my.uri)
            else:
                cur_mtime = os.path.getmtime(file_path)
                cache_mtime = my.XML_FILE_MTIME.get(file_path)

                if cur_mtime == cache_mtime:
                    my.doc = my.XML_FILE_CACHE.get(file_path)
                else:

                    my.doc = NonvalidatingReader.parseUri("file://%s" % file_path, my.uri)
                    my.cache_xml(file_path, my.doc, cur_mtime)



        except Exception, e:
            #print "Error in xml file: ", file_path
            raise XmlException(e)


    def cache_xml(cls, file_path, doc, cur_mtime):
        lock = thread.allocate_lock()
        lock.acquire()
        cls.XML_FILE_CACHE[file_path] = doc

        cls.XML_FILE_MTIME[file_path] = cur_mtime

        lock.release()
    cache_xml = classmethod(cache_xml)

    xmls = set()
    count = 0
    def read_string(my, xml_string, print_error=True):
        """
        # skip snapshots
        if xml_string not in Xml.xmls:
            Xml.xmls.add(xml_string)
        else:
            print "already parsed!!!"
            #print xml_string[:150]
            #if xml_string.find("pipeline scale='49'") != -1:
            #    sdafd

            #dfafds

        Xml.count += 1
        print Xml.count
        """


        # For whatever reason, parseString cannot be unicode??!
        if type(xml_string) != types.StringType:
            #xml_string = str(xml_string)
            xml_string = xml_string.encode('utf-8')

        #my.reader = PyExpat.Reader()
        #print xml_string
        #my.doc = my.reader.fromString(xml_string)
        try:
            # convert to utf-8
            if type(xml_string) != types.StringType:
                xml_string = xml_string.encode("utf-8")
            my.doc = NonvalidatingReader.parseString(xml_string, my.uri)
        except Exception, e:
            if print_error:
                print "Error in xml: ", xml_string
                print str(e)
            raise XmlException(e)


    def create_doc(my, root_name="snapshot"):
        #from xml.dom.minidom import getDOMImplementation
        #impl = getDOMImplementation()
        #my.doc = impl.createDocument(None, root_name, None)

        my.doc = implementation.createRootNode(None)
        if root_name != None:
            root = my.doc.createElementNS(None,root_name)
            my.doc.appendChild(root)
        return my.doc


    def get_doc(my):
        '''returns the document object'''
        return my.doc

    def get_root_node(my):
        return my.doc.firstChild

    def import_node(my, element, deep=True):
        return my.doc.importNode(element, deep)

    def create_element(my, name):
        '''create a new element with this document'''
        #return my.doc.createElementNS('xml', name)
        return my.doc.createElementNS(None, name)


    def create_text_element(my, name, text, node=None):
        '''create an element with a text node embedded

        DO NOT USE "node" ARGUMENT

        FIXME: the "node" argument here is wrong.  It overides the element
        created and renders "name" useless".  This cannot be fixed here.  A
        new method has to replace this one to fix it because too much may
        depend on it.
        '''
        text_node = my.doc.createTextNode(text)
        if not node:
            node = my.create_element(name)
            node.appendChild(text_node)
        else:
            first = node.firstChild
            if first:
                node.replaceChild(text_node, first)
            else:
                node.appendChild(text_node)
        return node
 
    def create_data_element(my, name, text):
        '''create an element with a text node embedded'''
        text_node = my.doc.createCDATASection(text)
        elem = my.create_element(name)
        elem.appendChild(text_node)
        return elem

    def create_comment(my, text):
        '''create an element with a text node embedded'''
        text_node = my.doc.createComment(text)
        return text_node
   

    def clear_xpath_cache(my):
        my.cache_xpath = {}
        Container.put("XML:xpath_cache", {})

    def get_parent(cls, node):
        return node.parentNode
    get_parent = classmethod(get_parent)

    def get_children(cls, node):
        xx = node.childNodes
        children = []
        for x in xx:
            name = x.nodeName
            if name in ['#text', '#comment']:
                continue
            children.append(x)

        return children
    get_children = classmethod(get_children)


    def get_first_child(cls, node):
        return node.firstChild
    get_first_child = classmethod(get_first_child)


    def append_child(cls, node, child):
        node.appendChild(child)
    append_child = classmethod(append_child)

    def remove_child(cls, node, child):
        if child != None:
            node.removeChild(child)
    remove_child = classmethod(remove_child)


    def replace_child(cls, node, old_node, new_node ):
        node.replaceChild(new_node, old_node )
    replace_child = classmethod(replace_child)
        

    def _evaluate(my, xpath):
        cache = Container.get("XML:xpath_cache")
        if cache == None:
            cache = {}
            Container.put("XML:xpath_cache", cache)

        #key = "%s|%s" % (str(my.doc), xpath)
        num = random.randint(0, 500000)
        key = "%s_%s|%s" % (str(my.doc), num, xpath)
        result = cache.get(key)
        if result == None:
            result = Evaluate(xpath, my.doc)
            cache[key] = result
            #print xpath
        else:
            #print "reuse"
            pass

        return result

        '''
        result = my.cache_xpath.get(xpath)
        if result:
            return result
        if result == []:
            return result
        #print xpath
        result = Evaluate(xpath, my.doc)
        my.cache_xpath[xpath] = result
        return result
        '''


    def get_nodes(my, xpath):
        '''get all of the nodes within the given xpath string'''
        try:
            nodes = my._evaluate(xpath)
        except Exception, e:
            raise XmlException('XPath Error: %s'%e.__str__())
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
            value = node.nodeValue
            if value == None:
                if node.firstChild == None:
                    value = ""
                else:
                    value = node.firstChild.nodeValue

            values.append(value)

        return values


    def get_value(my, xpath):
        values = my.get_values(xpath)
        if len(values) == 0:
            return ""
        else:
            return values[0]

    def get_xml(my):
        '''returns a stringified version of the document'''
        xml = StringIO()
        PrettyPrint(my.doc,xml)
        return xml.getvalue()


    def to_string(my, node=None, pretty=True, tree=None, method=None):
        '''returns a stringified version of the document'''
        xml = StringIO()

        if pretty:
            func = PrettyPrint
        else:
            func = Print

        if node == None:
            func(my.doc,xml)
        else:
            func(node,xml)

        # ensure that this value is unicode
        value = unicode( xml.getvalue(), 'utf-8')
        return value



    def fto_string(my, node=None, pretty=True):
        '''TEST: using 4Suite's pretty print'''
        xml = StringIO()

        if node == None:
            FtPrettyPrint(my.doc,xml)
        else:
            FtPrettyPrint(node,xml)

        return xml.getvalue()




    def dump(my):
        '''print out the stringafied version'''
        print my.get_xml()



    #
    # static methods
    #
    def get_attributes( cls, node ):
        data =  node.attributes

        # 4suite has a weird data structure for this
        attrs = {}
        for attr in data.values():
            name = attr.name
            value = attr.value
            attrs[name] = value
        return attrs
    get_attributes = classmethod(get_attributes)


    def get_attribute( cls, node, attribute ):
        return node.getAttributeNS(None,attribute)
    get_attribute = classmethod(get_attribute)

    def set_attribute( cls, node, attribute, value ):
        if type(value) not in types.StringTypes:
            value = str(value)
        return node.setAttributeNS(None,attribute,value)
    set_attribute = classmethod(set_attribute)

    def del_attribute(cls, node, attribute):
        value = cls.get_attribute(node, attribute)
        node.removeAttributeNS(None,attribute)
        return value
    del_attribute = classmethod(del_attribute)
    
    def get_node_name( node ):
        return node.nodeName
    get_node_name = staticmethod(get_node_name)

    def insert_before(new_element, ref_element, parent=None):
        parent.insertBefore(new_element, ref_element)

    insert_before = staticmethod(insert_before)

    def insert_after(new_element, ref_element, parent=None):
        parent.insertBefore(new_element, ref_element.nextSibling)

    insert_after = staticmethod(insert_after)


    def set_node_value(my, node, text):
        '''sets the value of a node.  This value is the first child'''
        text_node = my.doc.createTextNode(text)

        first_child = node.firstChild
        if not first_child:
            node.appendChild(text_node)
        else:
            node.replaceChild(text_node, first_child)

        return text_node



    def get_node_value(node):
        '''Gets the value of a node.  This value is often the first child
        of the node'''
        value = node.nodeValue
        if value == None:
            if node.firstChild == None:
                value = ""
            else:
                value = node.firstChild.nodeValue

        return value
    get_node_value = staticmethod(get_node_value)

    def get_node_values_of_children(cls, node):
        '''Gets the all the node value of the children of a node'''
        values = {}

        if not node:
            return values

        children = node.childNodes
        for child in children:
            if child.nodeType == 3:     # if this is a text node
                continue

            # first check the attribute for a name
            name = Xml.get_attribute(child,"name")
            if not name:
                name = child.nodeName

            value = cls.get_node_value(child)
            values[name] = value

        return values
    get_node_values_of_children = classmethod(get_node_values_of_children)



    def get_recursive_node_values(cls, node):
        '''Gets the all the node value of the children of a node'''
        values = {}

        if not node:
            return values

        cls._get_recursive_node_values(node, values)

        name = Xml.get_attribute(node, "name")
        if not name:
            name = node.nodeName
        values = values.get(name)

        if isinstance(values, basestring):
            values = values.strip()

        if not values:
            return {}
        else:
            return values

    get_recursive_node_values = classmethod(get_recursive_node_values)


    def _get_recursive_node_values(cls, node, values):
        if node.nodeName == '#text' or node.nodeType in [3,8]:
            return
        '''
        # somehow CDATA node is gone
        if node.nodeName == "html":
            values['html'] = Xml.get_node_xml(node)
            return
        '''

        children = []
        xx = node.childNodes
        for child in xx:
            # if this is a text node
            if child.nodeName != '#text' and child.nodeType != 3:
                children.append(child)


        # get the name of the node
        name = Xml.get_attribute(node, "name")
        if not name:
            name = node.nodeName

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







    def get_node_xml(node):
        '''returns a stringified version of the node'''
        xml = StringIO()
        PrettyPrint(node,xml)
        return xml.getvalue()
    get_node_xml = staticmethod(get_node_xml)




    def xpath(node, xpath):
        '''Evaluate an xpath of an arbitrary node'''
        nodes = Evaluate(xpath, node)
        return nodes
    xpath = staticmethod(xpath)


    def to_html(value):
        if value == "":
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




        

    


