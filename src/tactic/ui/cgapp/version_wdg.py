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

__all__ = ['UnknownVersionContextWdg', 'CurrentVersionContextWdg','VersionWdg','SubRefWdg']

from pyasm.common import Xml, Container
from pyasm.search import Search
from pyasm.biz import Snapshot
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import SessionContents
from tactic.ui.common import BaseTableElementWdg


class UnknownVersionContextWdg(BaseTableElementWdg):
    
    def init(my):
        my.has_data = False
        my.is_loaded = None

    def get_status(my):
        return VersionWdg.NOT_CURRENT

    def get_display(my):
       
        version = my.get_option('version')
        display = 'v%0.3d' %version
        
        status = my.get_status()
        widget = VersionWdg.get(status)
        widget.add(display)
        
        return widget


class CurrentVersionContextWdg(BaseTableElementWdg):
    
    def init(my):
        my.has_data = False
        my.is_loaded = None

    def get_data(my):
        my.is_loaded = True
        my.session_version = my.get_option('session_version')
        my.current_version =  my.get_option('current_version')
        my.session_context = my.get_option('session_context')
        my.current_context = my.get_option('current_context')
        my.session_revision = my.get_option('session_revision')
        my.current_revision =  my.get_option('current_revision')

        if not my.current_version:
            my.current_version = 0
        
        if my.session_version in ['', None]:
            my.session_version = 0
            my.is_loaded = False
                
        if not my.session_revision:
            my.session_revision = 0
        else:
            my.session_revision = int(my.session_revision)
        if not my.current_revision:
            my.current_revision = 0
        else:
            my.current_revision = int(my.current_revision)
        my.has_data = True
  
    def get_status(my):
        if not my.has_data:
            my.get_data()
        '''
        is_loaded = False
        if my.session_version:
            is_loaded = True
        '''
        is_loaded = my.is_loaded
        if is_loaded:    
            if my.session_context != my.current_context:
                return VersionWdg.MISMATCHED_CONTEXT
            elif my.session_version == my.current_version:
                if my.session_revision == my.current_revision:
                    return VersionWdg.UPDATED 
                elif my.session_revision < my.current_revision:
                    return VersionWdg.OUTDATED
                else:
                    return VersionWdg.NOT_CURRENT

            elif my.session_version < my.current_version:
                return VersionWdg.OUTDATED
            else: # session has a version not found in db
                return VersionWdg.NOT_CURRENT
        else:
             return VersionWdg.NOT_LOADED

    def get_display(my):
        
        my.get_data()
        display = "v%0.3d" % int(my.current_version)
        if my.current_revision:
            display = "%s r%0.3d" % (display, int(my.current_revision))
        
        status = my.get_status()
        widget = VersionWdg.get(status)
        widget.add(display)
        
        return widget

class VersionWdg(Widget):
    '''Widget that displays the status/currency of a loaded object in the UI'''
    MISMATCHED_CONTEXT, UPDATED, OUTDATED, NOT_CURRENT, NOT_LOADED = xrange(5)
    def get(cls, status):
        widget = Widget()
        if status == cls.MISMATCHED_CONTEXT:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))
            widget.add("*")
        elif status == cls.UPDATED:
            widget.add(IconWdg(icon=IconWdg.DOT_GREEN))
        elif status == cls.NOT_CURRENT:
            widget.add(IconWdg(name='not current', icon=IconWdg.DOT_YELLOW))
        elif status == cls.OUTDATED:
            widget.add(IconWdg(name='outdated', icon=IconWdg.DOT_RED))
        elif status == cls.NOT_LOADED:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))
        else:
            widget.add(IconWdg(icon=IconWdg.DOT_GREY))

        return widget

    get = classmethod(get)

class SubRefWdg(AjaxWdg):
    '''Widget that draws the hierarchical references of the asset of interest'''
    CB_NAME = "load_snapshot"

    def init(my):
        my.version_wdgs = []

    def set_info(my, snapshot, session, namespace):
        my.session = session
        my.snapshot = snapshot
        my.namespace = namespace

        # handle ajax settings
        my.widget = DivWdg()
        my.set_ajax_top(my.widget)
        my.set_ajax_option("namespace", my.namespace)
        my.set_ajax_option("snapshot_code", my.snapshot.get_code())

    def init_cgi(my):
        web = WebContainer.get_web()
        snapshot_code = web.get_form_value("snapshot_code")
        namespace = web.get_form_value("namespace")

        snapshot = Snapshot.get_by_code(snapshot_code)
        session = SessionContents.get(asset_mode=True)

        my.set_info(snapshot, session, namespace)

    def get_version_wdgs(my):
        '''get a list of version wdgs'''
        if my.version_wdgs:
            return my.version_wdgs
        xml = my.snapshot.get_xml_value("snapshot")
        refs = xml.get_nodes("snapshot/file/ref")
        if not refs:
            return my.version_wdgs

       
        # handle subreferences
        for ref in refs:

            instance = Xml.get_attribute(ref, "instance")
            node_name = Xml.get_attribute(ref, "node_name")
            snapshot = Snapshot.get_ref_snapshot_by_node(ref, mode='current')
            if not snapshot:
                print "WARNING: reference in snapshot [%s] does not exist" % my.snapshot.get_code()
                wdg = UnknownVersionContextWdg()
                context = Xml.get_attribute(ref, "context")
                version = Xml.get_attribute(ref, "version")
                try:
                    version = int(version)
                except ValueError:
                    versionm = 0
                data = {'node_name': node_name, 'context': context, 
                        'version': version}
                wdg.set_options(data)

                my.version_wdgs.append(wdg)
                continue

            #checkin_snapshot = Snapshot.get_ref_snapshot_by_node(ref)

            parent = snapshot.get_parent()
                
            asset_code = parent.get_code()

            # namespace = "veryron_rig"
            # node_name = "stool_model:furn001"
            # instance =  "stool_model"
            
            # HACK: if node name was not specified, then try to guess it
            # (for backwards compatibility)
            if not node_name: 
                node_name = my.get_node_name(snapshot, asset_code, my.namespace)
                # HACK
                parts = node_name.split(":")
                parts.insert(1, instance)
                node_name = ":".join(parts)
                print "WARNING: node_name not given: using [%s]" % node_name


            # Add the current namespace to the node 
            # in session
            checked_node_name = node_name

            # FIXME: this is Maya-specific and meant for referencing a shot
            '''
            if app_name == 'Maya':
                
                if not node_name.startswith("%s:" % my.namespace):
                    node_name = "%s:%s" % (my.namespace, node_name)
            elif app_name == "XSI":
                pass
            ''' 
            # get the current information
            current_version = snapshot.get_value("version")
            current_context = snapshot.get_value("context")
            current_revision = snapshot.get_value("revision", no_exception=True)
            current_snapshot_type = snapshot.get_value("snapshot_type")


            # get the session information
            my.session.set_asset_mode(False)
            session_context = my.session.get_context(node_name, asset_code, current_snapshot_type)
            session_version = my.session.get_version(node_name, asset_code, current_snapshot_type)
            session_revision = my.session.get_revision(node_name, asset_code, current_snapshot_type)
            #print "session: ", session_version, session_context, session_revision
            # add to outdated ref list here, this is really current even though it's called current

            version_wdg = CurrentVersionContextWdg()
            data = {'session_version': session_version, \
                'session_context': session_context,  \
                'session_revision': session_revision,  \
                'current_context': current_context, \
                'current_version': current_version, \
                'current_revision': current_revision,\
                'asset_code': asset_code,\
                'node_name': checked_node_name ,\
                'sobject': parent,\
                'snapshot': snapshot}

            version_wdg.set_options(data)
            my.version_wdgs.append(version_wdg)

            # This only adds when it is being drawn with the corresponding process selected
            # so not that useful, commented out for now.
            #if version_wdg.get_status() not in [ VersionWdg.NOT_LOADED, VersionWdg.UPDATED]:
            #    SubRefWdg.add_outdated_ref(version_wdg)

        return my.version_wdgs

    def get_display(my):

        assert my.snapshot
        assert my.session
        assert my.namespace

        widget = my.widget
        

        if not my.is_ajax():
            return widget
 
        #widget.add_style("border-style: solid")
        #widget.add_style("padding: 10px")
        #widget.add_style("position: absolute")
        #widget.add_style("margin-left: 50px")
        widget.add_style("text-align: left")
        table = Table()
        
        version_wdgs = my.get_version_wdgs()

        for version_wdg in version_wdgs:
            # draw the info
            tr = table.add_row()
            #checkbox = CheckboxWdg(my.CB_NAME)
            #checkbox.set_option("value", "cow" )
            #table.add_cell( checkbox )

            td = table.add_cell(version_wdg)
            td.set_attr("nowrap", "1")
            current_context = version_wdg.get_option('current_context')
            if current_context:
                table.add_cell(HtmlElement.b("(%s)" % current_context))
            else:
                checkin_context = version_wdg.get_option('context')
                td = table.add_cell("(%s)" % checkin_context)
                tr.add_style('background-color: #7D0000')
                
            table.add_cell(version_wdg.get_option('asset_code'))
            node_name = version_wdg.get_option('node_name')
            if node_name:
                table.add_cell(node_name.split(":")[0])

        widget.add("<hr size='1'>")
        widget.add("References")
        widget.add(table)

        return widget


    def get_overall_status(my):
        version_wdgs = my.get_version_wdgs()
        all_updated = True
        is_loaded = False
        for wdg in version_wdgs:
            status = wdg.get_status()
            if status != VersionWdg.NOT_LOADED:
                is_loaded = True
            if wdg.get_status() != VersionWdg.UPDATED:
                all_updated = False
                # don't use break as we need the info of all the subrefs
                continue
                
        
        if not is_loaded:
            return VersionWdg.NOT_LOADED
        elif all_updated == False:
            return VersionWdg.OUTDATED
        else: 
            return VersionWdg.UPDATED

    def get_node_name(my, snapshot, asset_code, namespace):
        ''' if possible get the node name from snapshot which is more accurate'''
        node_name = snapshot.get_node_name()

        if not node_name:
            naming = MayaNodeNaming()
            app_name = WebContainer.get_web().get_selected_app() 
            if app_name == "Maya":
                naming = MayaNodeNaming()
            elif app_name == "XSI":
                naming = XSINodeNaming()
            elif app_name == "Houdini":
                naming = HoudiniNodeNaming()
            naming.set_asset_code(asset_code)
            naming.set_namespace(namespace)

            node_name = naming.build_node_name()
        return node_name

    def add_outdated_ref(version_wdg):
        Container.append_seq('SubRef_outdated', version_wdg)
    add_outdated_ref = staticmethod(add_outdated_ref)

    def get_outdated_ref():
        return Container.get('SubRef_outdated')
    get_outdated_ref = staticmethod(get_outdated_ref)

