############################################################
#
#    Copyright (c) 2010, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


__all__ = ['NotificationTestCmd']

from pyasm.common import Container, Environment, TacticException
from pyasm.command import Command, Trigger
from pyasm.search import SearchKey, SearchType
from pyasm.biz import Project

class NotificationTestCmd(Command):
    '''Do a dry-run of a notification sending'''

    def get_base_search_type(self):
        return ''

    def get_prev_value(self):
        return ''

    def execute(self):

        notification = self.kwargs.get('sobject_dict')
        search_key = notification.get('__search_key__')
        event = notification.get('event')
        parts  = event.split('|')
        if len(parts) < 2:
            raise TacticException('event should be in the form of {action}|{search_type}, e.g. update|sthpw/task or update|sthpw/task|status')
        orig_search_type = parts[1]
        search_type_obj  = SearchType.get(orig_search_type)
        sobject = SearchType.create(orig_search_type)

       
            
        self.sobjects.append(sobject)

        search_type = SearchKey.extract_search_type(search_key)
        search_id = notification.get('id')
        columns = search_type_obj.get_columns(orig_search_type)
        for column in columns:
            type = search_type_obj.get_column_type(orig_search_type,column)
            if column == 'search_type':
                value = search_type
            elif column == 'search_id':
                value = search_id
            elif column == 'project_code':
                value = Project.get_project_code()
            elif column in ['assigned', 'login']:
                value = Environment.get_user_name()
            elif type in ['integer','float','number']:
                value = 100
            elif type == 'timestamp':
                value = '20110101'
            else:
                value = '%s_test'%column
            try:
                sobject.set_value(column, value)
            except:
                continue


        notification_stype = notification.get('search_type')
        if notification_stype:
            sobject.set_value("search_type",  notification_stype)

        # some dummy output
        output = {'id': sobject.get_id()}

        notification_process = notification.get('process')
        if notification_process:
            if 'process' in columns:
                sobject.set_value("process", notification_process)
        try:
            triggers = Trigger.call(sobject, event, output=output, forced_mode='same process,same transaction', process = notification_process, search_type = notification_stype)
            if triggers:
                for idx, trigger in enumerate(triggers):
                    self.add_description('%s. %s' %(idx+1, trigger.get_description()))
            else:
                raise TacticException('No notification trigger is fired. Possible mismatched project_code for this notification entry.')
        except Exception, e:
            raise
            raise Exception(e.__str__())
    

    
