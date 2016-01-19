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

__all__ = ["CsvImportCmd","SimpleCsvImportCmd"]

import os, csv
import re
import unicodedata

from pyasm.search import SObjectFactory, SearchType, Search, SqlException
from pyasm.biz import CsvParser
from pyasm.common import UserException

from command import *

class CsvImportCmd(Command):

    ENTRY_ERROR_MSG = "Error creating new entry for row"

    def get_title(my):
        return "CSV Import"

    def strip_punctuation(my, word):
        '''strip punctuation and Cf BOM characters for unicode string'''
        chars = []
        for char in word:
            cat = unicodedata.category(char)
            if cat == 'Cf' or cat.startswith('P'):
                continue
            chars.append(char)
        return "".join(chars)

    def check(my):
        # make this a callback for now
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        
        my.search_type = web.get_form_value("search_type_filter")
        my.file_path = web.get_form_value("file_path")
        my.web_url = web.get_form_value("web_url")
        my.test_run = web.get_form_value("test_run")=='true'
        
        my.start_index = web.get_form_value("start_index")
        if my.start_index:
            try:
                my.start_index = int(my.start_index)
            except:
                my.start_index = None

        my.triggers_mode = web.get_form_value("triggers_mode")
        if  my.triggers_mode in ['', 'True']:
            my.triggers_mode = True
        elif my.triggers_mode == 'False':
            my.triggers_mode = False 

        if my.web_url:
            import urllib2
            response = urllib2.urlopen(url)
            csv = response.read()
            my.file_path = "/tmp/test.csv"
            f = open(my.file_path, 'w')
            f.write(csv)
            f.close()



        # either unknown or utf-8
        my.encoder = web.get_form_value("encoder")
        my.id_col = web.get_form_value("id_col")
        if not my.id_col:
            my.id_col = 'id'
        num_columns = web.get_form_value("num_columns")
        if num_columns:
            num_columns = int(num_columns)
        else:
            num_columns = 0

        # indices of the enabled columns
        my.enabled_idx = []
        my.columns = []
        my.new_columns = []
        my.new_column_types = []
        my.note_processes = []


        for i in range(0, num_columns):
            enabled =  web.get_form_value("column_enabled_%s" % i)
            if enabled  in ['on','true']:
                my.enabled_idx.append(i)

            # Default column name or '' for new columns
            column =  web.get_form_value("column_%s" % i)
            my.columns.append(column)
 
            # New column name if column==''
            new_column = web.get_form_value("new_column_%s" % i)
            if isinstance(new_column, unicode):
                new_column = my.strip_punctuation(new_column)
            my.new_columns.append(new_column)
            
            # New column type if column==''
            new_column_type = web.get_form_value("column_type_%s" % i)
            my.new_column_types.append(new_column_type)

            # New note process if column==('note')
            new_note_process = web.get_form_value("note_process_%s" % i)
            my.note_processes.append(new_note_process)

        # check for required columns
        sobj = SObjectFactory.create(my.search_type)
        required_columns = sobj.get_required_columns()
        for required in required_columns:
            if required in my.columns:
                continue
            else:
                raise UserException('Missing required column [%s] in the input CSV' % required)

        my.has_title = web.get_form_value("has_title") == 'on'
        my.lowercase_title = web.get_form_value("lowercase_title") == 'on'
        return True

    def execute(my):

        assert my.search_type
        assert my.file_path
        assert my.columns

        csv_parser = CsvParser(my.file_path)
        if my.has_title:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)
        if my.lowercase_title:
            csv_parser.set_lowercase_title(True)

        if my.encoder:
            csv_parser.set_encoder(my.encoder)

        csv_parser.parse()

        # get the data and columns
        #csv_titles = csv_parser.get_titles()
        csv_data = csv_parser.get_data()
        # make sure all of the new columns are created
        csv_titles = []
        for i, column in enumerate(my.columns):
            if not column:
                new_column = my.new_columns[i]
                new_column_type = my.new_column_types[i]
                if new_column and new_column not in ['id', 'code'] and\
                    i in my.enabled_idx:
                    # create the new column
                    from pyasm.command import ColumnAddCmd
                    #col_type = "Name/Code"
                    cmd = ColumnAddCmd(my.search_type, new_column, new_column_type)
                    cmd.execute()

                    # create the sobject for now
                    """
                    sobject = SObjectFactory.create("prod/custom_property")
                    sobject.set_value("search_type", my.search_type)
                    sobject.set_value("name", new_column)
                    sobject.set_value("description", new_column)
                    sobject.commit()
                    """

                csv_titles.append( my.new_columns[i] )
            else:
                csv_titles.append( column )

        try:
            id_col = csv_titles.index(my.id_col)
            # id is special we want it to be identifiable at all times
            # but not importable
            if my.id_col != 'id' and id_col not in my.enabled_idx:
                id_col = -1
        except ValueError:
            id_col = -1

        new_entries = []
        updated_entries = []
        error_entries = []
        error = False
        
        # create entries or update values
        for row_count, row in enumerate(csv_data):
            if my.start_index and row_count < my.start_index:
                continue

            sobject = None
            # if id_col doesn't exist
            is_new_entry = False
            
            if id_col == -1:
                sobject = SObjectFactory.create(my.search_type)
                is_new_entry = True
            else:
                id = row[id_col]
                if id:
                    # this essentially updates the current sobject in db
                    if my.id_col=='code':
                        sobject = Search.get_by_code(my.search_type, id.strip())
                    elif my.id_col=='id':
                        sobject = Search.get_by_id(my.search_type, id.strip())
                    else:
                        u_search = Search(my.search_type)
                        u_search.add_filter(my.id_col, id.strip())
                        sobject = u_search.get_sobject()
                    #assert sobject
                # in case a previously exported sobject with this code
                # or id has been deleted or it is a completely foreign code
                # or id, sobject will be None
                else: # skip if empty id or code
                    continue
                  
                if not sobject:
                    sobject = SObjectFactory.create(my.search_type)
                    is_new_entry = True

            new_columns = 0
            note = None
            for cell_count, cell in enumerate(row):
                '''
                column_override = my.columns[cell_count]

                if column_override:
                    title = column_override
                else:
                    title = csv_titles[cell_count]
                    if not title:
                        continue
                '''
                # skip if not enabled
                if cell_count not in my.enabled_idx:
                    continue

                title = csv_titles[cell_count]
                if not title:
                    continue

                # always skip id column
                if title == "id":
                    continue
                cell = cell.strip()
               
                # remove control, other characters in unicode
                #cell = re.sub(r'\p{Cc}','', cell)
                cell = re.sub(r"[\x01-\x08\x0b-\x1f\x7f-\x9f]",'', cell)
                if title == "(note)":
                    note = cell
                else:
                    sobject.set_value(title, cell)
                new_columns += 1

            if not new_columns:
                msg = "No column or only the id column is selected."
                raise CommandException(msg)

            
            try:
                sobject.commit(triggers=my.triggers_mode)

                if note:
                    note_obj = SearchType.create("sthpw/note")
                    note_obj.set_value("note", note)
                    note_process = my.note_processes[i]
                    if not note_process:
                        note_process = "publish"
                    note_obj.set_value("process", note_process)
                    note_obj.set_value("context", note_process)
                    note_obj.set_user()
                    note_obj.set_parent(sobject)
                    note_obj.commit()

            except SqlException, e:
                msg = "%s [%s]: %s, %s" % (my.ENTRY_ERROR_MSG, row_count, str(row), e.__str__() )
                if my.test_run:
                    error = True
                    error_entries.append(sobject.get_code())
                raise SqlException(msg)
            else:
                if is_new_entry:
                    new_entries.append(sobject.get_code())
                else:
                    updated_entries.append(sobject.get_code())
        #show 30 max
        new_entries_display = ''
        if new_entries:
            new_entries_display = '%s ...'%', '.join(new_entries[0:5])
        my.description = "Total columns selected: %s\n\n  Imported %s new %s entries: %s " % (len(my.enabled_idx), len(new_entries), my.search_type, new_entries_display)
        if updated_entries:
            my.description = "%s.\n  Updated %s %s existing entries." %(my.description,  len(updated_entries), my.search_type)
        

class SimpleCsvImportCmd(Command):
    '''This Import does not require web values'''

    def get_title(my):
        return "Simple CSV Import"

    def __init__(my, **kwargs):
        super(SimpleCsvImportCmd, my).__init__(**kwargs)
        
        my.initialized = True
        my.search_type = my.kwargs.get("search_type_filter")
        my.file_path = my.kwargs.get("file_path")
        my.test_run = my.kwargs.get("test_run")=='true'
        my.has_title =  my.kwargs.get('has_title')

        # either unknown or utf-8
        my.encoder = my.kwargs.get("encoder")
        my.id_col = my.kwargs.get("id_col")
        if not my.id_col:
            my.id_col = 'id'
    
        
        my.columns = my.kwargs.get('columns')
        my.new_columns = []
        my.enabled_idx = my.kwargs.get("enabled_idx")

    def check(my):
        # make this a callback for now
        my.init() 
       
        # check for required columns
        sobj = SObjectFactory.create(my.search_type)
        required_columns = sobj.get_required_columns()
        for required in required_columns:
            if required in my.columns:
                continue
            else:
                raise UserException('Missing required column [%s] in the input CSV' % required)

        return True

    def execute(my):
        if not my.initialized:
            my.init()

        assert my.search_type
        assert my.file_path
        assert my.columns

        csv_parser = CsvParser(my.file_path)
        if my.has_title:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)

        if my.encoder:
            csv_parser.set_encoder(my.encoder)

        csv_parser.parse()

        # get the data and columns
        #csv_titles = csv_parser.get_titles()
        csv_data = csv_parser.get_data()
        # make sure all of the new columns are created
        csv_titles = []
        for i, column in enumerate(my.columns):
            if not column:
                new_column = my.new_columns[i]
                new_column_type = my.new_column_types[i]
                if new_column and new_column not in ['id', 'code'] and\
                    i in my.enabled_idx:
                    # create the new column
                    from pyasm.command import ColumnAddCmd
                    #col_type = "Name/Code"
                    cmd = ColumnAddCmd(my.search_type, new_column, new_column_type)
                    cmd.execute()

                    # create the sobject for now
                    sobject = SObjectFactory.create("prod/custom_property")
                    sobject.set_value("search_type", my.search_type)
                    sobject.set_value("name", new_column)
                    sobject.set_value("description", new_column)
                    sobject.commit()

                csv_titles.append( my.new_columns[i] )
            else:
                csv_titles.append( column )

        try:
            id_col = csv_titles.index(my.id_col)
            # id is special we want it to be identifiable at all times
            # but not importable
            if my.id_col != 'id' and id_col not in my.enabled_idx:
                id_col = -1
        except ValueError:
            id_col = -1

        new_entries = []
        updated_entries = []
        error_entries = []
        error = False
 
        # create entries or update values
        for row_count, row in enumerate(csv_data):
            sobject = None
            # if id_col doesn't exist
            is_new_entry = False
            
            if id_col == -1:
                sobject = SObjectFactory.create(my.search_type)
                is_new_entry = True
            else:
                id = row[id_col]
                if id:
                    # this essentially updates the current sobject in db
                    if my.id_col=='code':
                        sobject = Search.get_by_code(my.search_type, id.strip())
                    elif my.id_col=='id':
                        sobject = Search.get_by_id(my.search_type, id.strip())
                    else:
                        u_search = Search(my.search_type)
                        u_search.add_filter(my.id_col, id.strip())
                        sobject = u_search.get_sobject()
                    #assert sobject
                # in case a previously exported sobject with this code
                # or id has been deleted or it is a completely foreign code
                # or id, sobject will be None
                else: # skip if empty id or code
                    continue
                  
                if not sobject:
                    sobject = SObjectFactory.create(my.search_type)
                    is_new_entry = True

            new_columns = 0
            note = None
            for cell_count, cell in enumerate(row):
                '''
                column_override = my.columns[cell_count]

                if column_override:
                    title = column_override
                else:
                    title = csv_titles[cell_count]
                    if not title:
                        continue
                '''
                # skip if not enabled
                if cell_count not in my.enabled_idx:
                    continue

                title = csv_titles[cell_count]
                if not title:
                    continue

                # always skip id column
                if title == "id":
                    continue
                cell = cell.strip()
               
                # remove control, other characters in unicode
                #cell = re.sub(r'\p{Cc}','', cell)
                cell = re.sub(r"[\x01-\x08\x0b-\x1f\x7f-\x9f]",'', cell)
                if title == "(note)":
                    note = cell
                else:
                    sobject.set_value(title, cell)
                new_columns += 1

            if not new_columns:
                msg = "No column or only the id column is selected."
                raise CommandException(msg)

            
            try:
                #sobject.commit(triggers=False)
                sobject.commit(triggers=True)

                if note:
                    note_obj = SearchType.create("sthpw/note")
                    note_obj.set_value("note", note)
                    note_obj.set_value("process", "publish")
                    note_obj.set_value("context", "publish")
                    note_obj.set_user()
                    note_obj.set_parent(sobject)
                    note_obj.commit()

            except SqlException, e:
                msg = "Error creating new entry for row [%s]: %s, %s" % (row_count, str(row), e.__str__() )
                if my.test_run:
                    error = True
                    error_entries.append(sobject.get_code())
                raise SqlException(msg)
            else:
                if is_new_entry:
                    new_entries.append(sobject.get_code())
                else:
                    updated_entries.append(sobject.get_code())
        #show 30 max
        new_entries_display = ''
        if new_entries:
            new_entries_display = '%s ...'%', '.join(new_entries[0:5])
        my.description = "Total columns selected: %s\n\n  Imported %s new %s entries: %s " % (len(my.enabled_idx), len(new_entries), my.search_type, new_entries_display)
        if updated_entries:
            my.description = "%s.\n  Updated %s %s existing entries." %(my.description,  len(updated_entries), my.search_type)
        
                



       



