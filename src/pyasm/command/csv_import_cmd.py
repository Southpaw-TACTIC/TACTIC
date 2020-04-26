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

    def get_title(self):
        return "CSV Import"

    def strip_punctuation(self, word):
        '''strip punctuation and Cf BOM characters for unicode string'''
        chars = []
        for char in word:
            cat = unicodedata.category(char)
            if cat == 'Cf' or cat.startswith('P'):
                continue
            chars.append(char)
        return "".join(chars)

    def check(self):
        # make this a callback for now
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        
        self.search_type = web.get_form_value("search_type_filter")
        self.file_path = web.get_form_value("file_path")
        self.web_url = web.get_form_value("web_url")
        self.test_run = web.get_form_value("test_run")=='true'
        
        self.start_index = web.get_form_value("start_index")
        if self.start_index:
            try:
                self.start_index = int(self.start_index)
            except:
                self.start_index = None

        self.triggers_mode = web.get_form_value("triggers_mode")
        if  self.triggers_mode in ['', 'True']:
            self.triggers_mode = True
        elif self.triggers_mode == 'False':
            self.triggers_mode = False 

        if self.web_url:
            import urllib2
            response = urllib2.urlopen(url)
            csv = response.read()
            self.file_path = "/tmp/test.csv"
            f = open(self.file_path, 'w')
            f.write(csv)
            f.close()



        # either unknown or utf-8
        self.encoder = web.get_form_value("encoder")
        self.id_col = web.get_form_value("id_col")
        if not self.id_col:
            self.id_col = 'id'
        num_columns = web.get_form_value("num_columns")
        if num_columns:
            num_columns = int(num_columns)
        else:
            num_columns = 0

        # indices of the enabled columns
        self.enabled_idx = []
        self.columns = []
        self.new_columns = []
        self.new_column_types = []
        self.note_processes = []


        for i in range(0, num_columns):
            enabled =  web.get_form_value("column_enabled_%s" % i)
            if enabled  in ['on','true']:
                self.enabled_idx.append(i)

            # Default column name or '' for new columns
            column =  web.get_form_value("column_%s" % i)
            self.columns.append(column)
 
            # New column name if column==''
            new_column = web.get_form_value("new_column_%s" % i)
            if isinstance(new_column, unicode):
                new_column = self.strip_punctuation(new_column)
            self.new_columns.append(new_column)
            
            # New column type if column==''
            new_column_type = web.get_form_value("column_type_%s" % i)
            self.new_column_types.append(new_column_type)

            # New note process if column==('note')
            new_note_process = web.get_form_value("note_process_%s" % i)
            self.note_processes.append(new_note_process)

        # check for required columns
        sobj = SObjectFactory.create(self.search_type)
        required_columns = sobj.get_required_columns()
        for required in required_columns:
            if required in self.columns:
                continue
            else:
                raise UserException('Missing required column [%s] in the input CSV' % required)

        self.has_title = web.get_form_value("has_title") == 'on'
        self.lowercase_title = web.get_form_value("lowercase_title") == 'on'
        return True

    def execute(self):

        assert self.search_type
        assert self.file_path
        assert self.columns

        csv_parser = CsvParser(self.file_path)
        if self.has_title:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)
        if self.lowercase_title:
            csv_parser.set_lowercase_title(True)

        if self.encoder:
            csv_parser.set_encoder(self.encoder)

        csv_parser.parse()

        # get the data and columns
        #csv_titles = csv_parser.get_titles()
        csv_data = csv_parser.get_data()
        # make sure all of the new columns are created
        csv_titles = []
        for i, column in enumerate(self.columns):
            if not column:
                new_column = self.new_columns[i]
                new_column_type = self.new_column_types[i]
                if new_column and new_column not in ['id', 'code'] and\
                    i in self.enabled_idx:
                    # create the new column
                    from pyasm.command import ColumnAddCmd
                    #col_type = "Name/Code"
                    cmd = ColumnAddCmd(self.search_type, new_column, new_column_type)
                    cmd.execute()

                    # create the sobject for now
                    """
                    sobject = SObjectFactory.create("prod/custom_property")
                    sobject.set_value("search_type", self.search_type)
                    sobject.set_value("name", new_column)
                    sobject.set_value("description", new_column)
                    sobject.commit()
                    """

                csv_titles.append( self.new_columns[i] )
            else:
                csv_titles.append( column )

        try:
            id_col = csv_titles.index(self.id_col)
            # id is special we want it to be identifiable at all times
            # but not importable
            if self.id_col != 'id' and id_col not in self.enabled_idx:
                id_col = -1
        except ValueError:
            id_col = -1

        new_entries = []
        updated_entries = []
        error_entries = []
        error = False
        
        # create entries or update values
        for row_count, row in enumerate(csv_data):
            if self.start_index and row_count < self.start_index:
                continue

            sobject = None
            # if id_col doesn't exist
            is_new_entry = False
            
            if id_col == -1:
                sobject = SObjectFactory.create(self.search_type)
                is_new_entry = True
            else:
                id = row[id_col]
                if id:
                    # this essentially updates the current sobject in db
                    if self.id_col=='code':
                        sobject = Search.get_by_code(self.search_type, id.strip())
                    elif self.id_col=='id':
                        sobject = Search.get_by_id(self.search_type, id.strip())
                    else:
                        u_search = Search(self.search_type)
                        u_search.add_filter(self.id_col, id.strip())
                        sobject = u_search.get_sobject()
                    #assert sobject
                # in case a previously exported sobject with this code
                # or id has been deleted or it is a completely foreign code
                # or id, sobject will be None
                else: # skip if empty id or code
                    continue
                  
                if not sobject:
                    sobject = SObjectFactory.create(self.search_type)
                    is_new_entry = True

            new_columns = 0
            note = None
            for cell_count, cell in enumerate(row):
                '''
                column_override = self.columns[cell_count]

                if column_override:
                    title = column_override
                else:
                    title = csv_titles[cell_count]
                    if not title:
                        continue
                '''
                # skip if not enabled
                if cell_count not in self.enabled_idx:
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
                sobject.commit(triggers=self.triggers_mode)

                if note:
                    note_obj = SearchType.create("sthpw/note")
                    note_obj.set_value("note", note)
                    note_process = self.note_processes[i]
                    if not note_process:
                        note_process = "publish"
                    note_obj.set_value("process", note_process)
                    note_obj.set_value("context", note_process)
                    note_obj.set_user()
                    note_obj.set_parent(sobject)
                    note_obj.commit()

            except SqlException, e:
                msg = "%s [%s]: %s, %s" % (self.ENTRY_ERROR_MSG, row_count, str(row), e.__str__() )
                if self.test_run:
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
        self.description = "Total columns selected: %s\n\n  Imported %s new %s entries: %s " % (len(self.enabled_idx), len(new_entries), self.search_type, new_entries_display)
        if updated_entries:
            self.description = "%s.\n  Updated %s %s existing entries." %(self.description,  len(updated_entries), self.search_type)
        

class SimpleCsvImportCmd(Command):
    '''This Import does not require web values'''

    def get_title(self):
        return "Simple CSV Import"

    def __init__(self, **kwargs):
        super(SimpleCsvImportCmd, self).__init__(**kwargs)
        
        self.initialized = True
        self.search_type = self.kwargs.get("search_type_filter")
        self.file_path = self.kwargs.get("file_path")
        self.test_run = self.kwargs.get("test_run")=='true'
        self.has_title =  self.kwargs.get('has_title')

        # either unknown or utf-8
        self.encoder = self.kwargs.get("encoder")
        self.id_col = self.kwargs.get("id_col")
        if not self.id_col:
            self.id_col = 'id'
    
        
        self.columns = self.kwargs.get('columns')
        self.new_columns = []
        self.enabled_idx = self.kwargs.get("enabled_idx")

    def check(self):
        # make this a callback for now
        self.init() 
       
        # check for required columns
        sobj = SObjectFactory.create(self.search_type)
        required_columns = sobj.get_required_columns()
        for required in required_columns:
            if required in self.columns:
                continue
            else:
                raise UserException('Missing required column [%s] in the input CSV' % required)

        return True

    def execute(self):
        if not self.initialized:
            self.init()

        assert self.search_type
        assert self.file_path
        assert self.columns

        csv_parser = CsvParser(self.file_path)
        if self.has_title:
            csv_parser.set_has_title_row(True)
        else:
            csv_parser.set_has_title_row(False)

        if self.encoder:
            csv_parser.set_encoder(self.encoder)

        csv_parser.parse()

        # get the data and columns
        #csv_titles = csv_parser.get_titles()
        csv_data = csv_parser.get_data()
        # make sure all of the new columns are created
        csv_titles = []
        for i, column in enumerate(self.columns):
            if not column:
                new_column = self.new_columns[i]
                new_column_type = self.new_column_types[i]
                if new_column and new_column not in ['id', 'code'] and\
                    i in self.enabled_idx:
                    # create the new column
                    from pyasm.command import ColumnAddCmd
                    #col_type = "Name/Code"
                    cmd = ColumnAddCmd(self.search_type, new_column, new_column_type)
                    cmd.execute()

                    # create the sobject for now
                    sobject = SObjectFactory.create("prod/custom_property")
                    sobject.set_value("search_type", self.search_type)
                    sobject.set_value("name", new_column)
                    sobject.set_value("description", new_column)
                    sobject.commit()

                csv_titles.append( self.new_columns[i] )
            else:
                csv_titles.append( column )

        try:
            id_col = csv_titles.index(self.id_col)
            # id is special we want it to be identifiable at all times
            # but not importable
            if self.id_col != 'id' and id_col not in self.enabled_idx:
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
                sobject = SObjectFactory.create(self.search_type)
                is_new_entry = True
            else:
                id = row[id_col]
                if id:
                    # this essentially updates the current sobject in db
                    if self.id_col=='code':
                        sobject = Search.get_by_code(self.search_type, id.strip())
                    elif self.id_col=='id':
                        sobject = Search.get_by_id(self.search_type, id.strip())
                    else:
                        u_search = Search(self.search_type)
                        u_search.add_filter(self.id_col, id.strip())
                        sobject = u_search.get_sobject()
                    #assert sobject
                # in case a previously exported sobject with this code
                # or id has been deleted or it is a completely foreign code
                # or id, sobject will be None
                else: # skip if empty id or code
                    continue
                  
                if not sobject:
                    sobject = SObjectFactory.create(self.search_type)
                    is_new_entry = True

            new_columns = 0
            note = None
            for cell_count, cell in enumerate(row):
                '''
                column_override = self.columns[cell_count]

                if column_override:
                    title = column_override
                else:
                    title = csv_titles[cell_count]
                    if not title:
                        continue
                '''
                # skip if not enabled
                if cell_count not in self.enabled_idx:
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
                if self.test_run:
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
        self.description = "Total columns selected: %s\n\n  Imported %s new %s entries: %s " % (len(self.enabled_idx), len(new_entries), self.search_type, new_entries_display)
        if updated_entries:
            self.description = "%s.\n  Updated %s %s existing entries." %(self.description,  len(updated_entries), self.search_type)
        
                



       



